"""Bounded content triage, deliberately not full format certification."""

import gzip
import hashlib
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zlib

from bioskills.inputs import parse_table_text
from bioskills.science import ScientificValidationError, require, validate_matrix

DECOMPRESSED_LIMIT = 4 * 1024 * 1024
SOURCE_LIMIT = 8 * 1024 * 1024
ALPHABETS = {
    "dna": set("ACGTRYSWKMBDHVN"),
    "rna": set("ACGURYSWKMBDHVN"),
    "nucleotide": set("ACGTURYSWKMBDHVN"),
    "protein": set("ACDEFGHIKLMNPQRSTVWYBXZJUO*"),
}


def _sequence(sequence, alphabet, *, gaps=False):
    allowed = ALPHABETS[alphabet] | ({"-"} if gaps else set())
    require(
        bool(sequence) and set(sequence.upper()) <= allowed,
        "sequence_alphabet",
        "Sequence contains symbols outside the declared alphabet.",
    )


def _vcf_alt(allele):
    if re.fullmatch(r"[ACGTNacgtn]+|\*|\.|<[^<>,\s]+>", allele):
        return True
    if re.fullmatch(r"\.[ACGTNacgtn]+|[ACGTNacgtn]+\.", allele):
        return True  # single breakend
    return bool(
        re.fullmatch(
            r"(?:[ACGTNacgtn]+)?([\[\]])[^\s\[\]:]+:[1-9][0-9]*\1(?:[ACGTNacgtn]+)?", allele
        )
    )


def inspect_format(
    path,
    *,
    reference=None,
    expected_reference=None,
    format_hint=None,
    sequence_alphabet="nucleotide",
):
    require(isinstance(path, (str, Path)), "input", "A filesystem path is required.")
    path = Path(path)
    require(path.is_file(), "input", "Input file required.")
    require(
        path.stat().st_size <= SOURCE_LIMIT,
        "size",
        "Use a streaming parser above 8 MiB source size.",
    )
    require(
        isinstance(sequence_alphabet, str) and sequence_alphabet in ALPHABETS,
        "sequence_alphabet",
        "Declare dna/rna/nucleotide/protein.",
    )
    require(
        format_hint is None
        or (
            isinstance(format_hint, str)
            and format_hint
            in {"bed", "gtf", "gff", "numeric_table", "fasta", "fastq", "vcf", "sbml"}
        ),
        "format_hint",
        "Unsupported format hint.",
    )
    source = path.read_bytes()
    compressed = source.startswith(b"\x1f\x8b")
    try:
        if compressed:
            with gzip.open(path, "rb") as stream:
                raw = stream.read(DECOMPRESSED_LIMIT + 1)
        else:
            raw = source[: DECOMPRESSED_LIMIT + 1]
    except (OSError, EOFError, zlib.error) as error:
        raise ScientificValidationError(
            "compression: Corrupt or incomplete gzip content."
        ) from error
    require(
        len(raw) <= DECOMPRESSED_LIMIT,
        "size",
        "Use a streaming parser above 4 MiB decompressed size.",
    )
    warnings, details = [], {}
    format_, validation = "UNKNOWN", "NOT_RUN"
    for magic, label, status in [
        (b"BAM\x01", "BAM", "OPTIONAL_PYSAM_REQUIRED"),
        (b"CRAM", "CRAM", "OPTIONAL_PYSAM_AND_REFERENCE_REQUIRED"),
        (b"BCF", "BCF", "OPTIONAL_PYSAM_REQUIRED"),
        (b"\x89HDF\r\n\x1a\n", "HDF5_CONTAINER", "OPTIONAL_H5AD_PARSER_REQUIRED"),
    ]:
        if raw.startswith(magic):
            format_, validation = label, status
            break
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeError as error:
            raise ScientificValidationError(
                "encoding: UTF-8 text or a supported binary signature required."
            ) from error
        require("\x00" not in text, "encoding", "NUL bytes are unsupported in text records.")
        lines = text.splitlines()
        require(bool(lines), "empty_file", "Empty input.")
        suffixes = path.suffixes
        suffix = (
            suffixes[-2]
            if compressed and len(suffixes) >= 2 and suffixes[-1] == ".gz"
            else path.suffix
        )
        hint = format_hint or {
            ".bed": "bed",
            ".gtf": "gtf",
            ".gff": "gff",
            ".gff3": "gff",
            ".csv": "numeric_table",
            ".vcf": "vcf",
            ".fastq": "fastq",
            ".fq": "fastq",
            ".fasta": "fasta",
            ".fa": "fasta",
            ".sbml": "sbml",
        }.get(suffix.lower())
        records = [
            line.split("\t")
            for line in lines
            if line and not line.startswith(("#", "track ", "browser "))
        ]
        first = records[0] if records else []
        if hint == "vcf" or text.startswith("##fileformat=VCF"):
            headers = [line.split("\t") for line in lines if line.startswith("#CHROM")]
            require(
                len(headers) == 1
                and headers[0][:8]
                == ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"],
                "vcf_header",
                "VCF fixed column header required.",
            )
            header = headers[0]
            require(
                len(set(header)) == len(header) and all(header),
                "vcf_header",
                "Unique nonblank VCF columns required.",
            )
            require(
                len(header) == 8 or (len(header) >= 10 and header[8] == "FORMAT"),
                "vcf_header",
                "Unsupported genotype columns.",
            )
            for row in records:
                require(
                    len(row) == len(header) and all(row) and row[1].isdigit() and int(row[1]) >= 1,
                    "vcf_record",
                    "Malformed VCF width, empty field or supported one-based position.",
                )
                require(
                    bool(re.fullmatch(r"[ACGTNacgtn]+", row[3])),
                    "vcf_ref",
                    "Nonempty A/C/G/T/N reference allele required.",
                )
                alleles = row[4].split(",")
                require(
                    all(_vcf_alt(allele) for allele in alleles)
                    and ("." not in alleles or len(alleles) == 1),
                    "vcf_alt",
                    "Invalid ALT; symbolic and basic breakend forms are supported.",
                )
            format_, validation = "VCF", "BASIC_TEXT_RECORDS"
        elif hint == "fasta" or text.startswith(">"):
            identifiers = []
            require(text.startswith(">"), "fasta", "FASTA header required.")
            for record in text.split(">")[1:]:
                parts = record.splitlines()
                require(
                    len(parts) >= 2 and bool(parts[0].strip()),
                    "fasta",
                    "Nonblank FASTA identifier/sequence required.",
                )
                identifiers.append(parts[0].split()[0])
                _sequence("".join(parts[1:]), sequence_alphabet, gaps=True)
            require(
                len(identifiers) == len(set(identifiers)),
                "fasta_duplicate",
                "This triage policy requires unique FASTA identifiers.",
            )
            format_, validation = "FASTA", "BASIC_TEXT_RECORDS"
        elif hint == "fastq" or text.startswith("@"):
            require(
                len(lines) % 4 == 0, "fastq", "Only complete four-line FASTQ records supported."
            )
            for i in range(0, len(lines), 4):
                header, seq, plus, quality = lines[i : i + 4]
                require(
                    header.startswith("@") and bool(header[1:].strip()) and plus.startswith("+"),
                    "fastq",
                    "Nonblank FASTQ read identifier and plus separator required.",
                )
                if plus[1:].strip():
                    require(
                        plus[1:].split()[0] == header[1:].split()[0],
                        "fastq_identifier",
                        "Repeated plus identifier differs from read identifier.",
                    )
                _sequence(seq, sequence_alphabet)
                require(
                    len(seq) == len(quality) and all(33 <= ord(x) <= 126 for x in quality),
                    "fastq_quality",
                    "Sequence/quality lengths and printable quality scope must agree.",
                )
            format_, validation = "FASTQ", "FOUR_LINE_FASTQ"
        elif hint == "sbml" or "<sbml" in text or "sbml:" in text:
            require(
                "<!DOCTYPE" not in text.upper() and "<!ENTITY" not in text.upper(),
                "sbml",
                "DTD/entity declarations unsupported.",
            )
            try:
                document = ET.fromstring(text)
            except ET.ParseError as error:
                raise ScientificValidationError("sbml_xml: Malformed XML.") from error
            require(document.tag.split("}")[-1] == "sbml", "sbml", "SBML root required.")
            format_, validation = "SBML", "XML_STRUCTURE_ONLY"
        elif (
            hint in {"gtf", "gff"}
            or text.startswith("##gff-version")
            or (
                hint != "numeric_table"
                and len(first) == 9
                and not first[1].lstrip("-").isdigit()
                and (
                    first[0].startswith(("chr", "NC_"))
                    or (first[3].lstrip("-").isdigit() and first[4].lstrip("-").isdigit())
                )
            )
        ):
            require(
                bool(records) and not any(line.startswith("##FASTA") for line in lines),
                "features",
                "Use a full parser for mixed annotation/FASTA sections.",
            )
            strands = {"+", "-", "."} if hint == "gtf" else {"+", "-", ".", "?"}
            for row in records:
                require(
                    len(row) == 9 and all(row),
                    "features",
                    "Nine nonempty annotation fields required.",
                )
                require(
                    row[3].isdigit() and row[4].isdigit() and 1 <= int(row[3]) <= int(row[4]),
                    "coordinates",
                    "Invalid one-based annotation interval.",
                )
                require(
                    row[6] in strands and row[7] in {".", "0", "1", "2"},
                    "features",
                    "Invalid strand or phase.",
                )
            format_, validation = "GTF_OR_GFF", "BASIC_TEXT_RECORDS"
        elif hint == "bed" or (
            hint != "numeric_table"
            and 3 <= len(first) <= 12
            and (first[0].startswith(("chr", "scaffold", "contig", "NC_")) or first[0].isdigit())
        ):
            require(
                bool(records) and len({len(row) for row in records}) == 1,
                "bed",
                "Consistent BED records required.",
            )
            zero = 0
            for row in records:
                require(
                    3 <= len(row) <= 12
                    and bool(row[0])
                    and row[1].isdigit()
                    and row[2].isdigit()
                    and 0 <= int(row[1]) <= int(row[2]),
                    "coordinates",
                    "Invalid zero-based BED interval.",
                )
                start, end = int(row[1]), int(row[2])
                zero += start == end
                if len(row) >= 5:
                    require(
                        row[4] == "." or (row[4].isdigit() and 0 <= int(row[4]) <= 1000),
                        "bed",
                        "Invalid BED score.",
                    )
                if len(row) >= 6:
                    require(row[5] in {"+", "-", "."}, "bed", "Invalid BED strand.")
                if len(row) >= 8:
                    require(
                        row[6].isdigit()
                        and row[7].isdigit()
                        and start <= int(row[6]) <= int(row[7]) <= end,
                        "coordinates",
                        "Invalid BED thick interval.",
                    )
            if zero:
                warnings.append(
                    "Zero-length insertion-style BED intervals require downstream compatibility review."
                )
            details["zero_length_intervals"] = zero
            format_, validation = "BED", "BASIC_TEXT_RECORDS"
        else:
            delimiter = "\t" if "\t" in lines[0] else ","
            table = parse_table_text(text, delimiter, index_header=True)
            validate_matrix(table)
            details.update(
                rows=len(table),
                columns=len(table.columns),
                row_ids=list(table.index),
                column_ids=list(table.columns),
            )
            format_, validation = "NUMERIC_TABLE", "NUMERIC_STRUCTURE_ONLY"
    if expected_reference is not None:
        require(reference == expected_reference, "reference", "Declared reference build mismatch.")
    return {
        "format": format_,
        "validation": validation,
        "compression": "gzip" if compressed else "none",
        "encoding": "binary" if validation.startswith("OPTIONAL") else "utf-8",
        "reference": reference,
        "sequence_alphabet": sequence_alphabet,
        "details": details,
        "warnings": warnings,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "decompressed_sha256": hashlib.sha256(raw).hexdigest(),
        "limitations": [
            "Bounded content/signature triage is not complete conformance or biological validation",
            "Optional binary parsing, VCF genotype semantics, annotation attributes and full BED block semantics are NOT_RUN",
            "Ambiguous text requires an explicit format_hint; extensions are hints checked against content",
            "Sample/reference identity is not authenticated from filenames or declarations",
        ],
    }
