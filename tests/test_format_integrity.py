"""Scoped content checks, bounded decompression and exact table identities."""

import gzip

import pytest

from bioskills.expanded import inspect_format
from bioskills.science import ScientificValidationError


@pytest.mark.parametrize(
    "text",
    [
        "@\nACGT\n+\nIIII\n",
        "@r\nACGT\n+other\nIIII\n",
        "@r\n1234\n+\nIIII\n",
        "@r\nACGT\n+\nIII\n",
        "@r\nACGT\n+\nIIII\n@incomplete\n",
    ],
)
def test_invalid_fastq(tmp_path, text):
    file = tmp_path / "reads.dat"
    file.write_text(text)
    with pytest.raises(ScientificValidationError):
        inspect_format(file)


@pytest.mark.parametrize(
    "alphabet,sequence",
    [
        ("dna", "ACGTRYSWKMBDHVN"),
        ("rna", "ACGURYSWKMBDHVN"),
        ("nucleotide", "ACGTUN"),
        ("protein", "MKWVTFISLL"),
    ],
)
def test_explicit_alphabet_and_repeated_id(tmp_path, alphabet, sequence):
    file = tmp_path / "reads.dat"
    file.write_text(f"@r description\n{sequence}\n+r\n{'I' * len(sequence)}\n")
    assert inspect_format(file, sequence_alphabet=alphabet)["validation"] == "FOUR_LINE_FASTQ"


def vcf(ref="A", alt="C"):
    return (
        "##fileformat=VCFv4.3\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t1\t.\t"
        + ref
        + "\t"
        + alt
        + "\t.\tPASS\t.\n"
    )


@pytest.mark.parametrize("ref,alt", [("", "C"), ("A", ""), ("1", "C"), ("A", "12"), ("A", "< >")])
def test_vcf_required_alleles(tmp_path, ref, alt):
    file = tmp_path / "variants.dat"
    file.write_text(vcf(ref, alt))
    with pytest.raises(ScientificValidationError):
        inspect_format(file)


@pytest.mark.parametrize(
    "alt", ["<DEL>", "<*>", "*", ".", "A,C", "N]chr2:10]", "[chr2:10[N", ".A", "A."]
)
def test_supported_vcf_representations(tmp_path, alt):
    file = tmp_path / "variants.dat"
    file.write_text(vcf(alt=alt))
    assert inspect_format(file)["format"] == "VCF"


@pytest.mark.parametrize(
    "text,hint",
    [
        ("chr1\tx\tgene\t1\t10\t.\tbad\t.\tID=g\n", "gff"),
        ("chr1\tx\tgene\t-1\t10\t.\t+\t.\tID=g\n", "gtf"),
        ("chr1\t10\t2\n", "bed"),
        ("chr1\t-1\t2\n", "bed"),
        ("chr1\t0\t2\tp\t0\tbad\n", "bed"),
    ],
)
def test_coordinate_and_strand_failures(tmp_path, text, hint):
    file = tmp_path / "file.dat"
    file.write_text(text)
    with pytest.raises(ScientificValidationError):
        inspect_format(file, format_hint=hint)


def test_zero_length_and_unknown_gff_strand_scope(tmp_path):
    file = tmp_path / "file.dat"
    file.write_text("chr1\t0\t0\n")
    result = inspect_format(file)
    assert (
        result["format"] == "BED"
        and result["details"]["zero_length_intervals"] == 1
        and result["warnings"]
    )
    file.write_text("chr1\tx\tgene\t1\t10\t.\t?\t.\tID=g\n")
    assert inspect_format(file, format_hint="gff")["format"] == "GTF_OR_GFF"
    with pytest.raises(ScientificValidationError):
        inspect_format(file, format_hint="gtf")


@pytest.mark.parametrize(
    "text",
    [
        "gene,a,a\ng,1,2\n",
        "gene,,b\ng,1,2\n",
        "gene,a,b\ng,1,2,3\n",
        "gene,a,b\nextra,g,1,2\n",
        "gene,a,b\ng,,2\n",
    ],
)
def test_raw_table_structure(tmp_path, text):
    file = tmp_path / "matrix.dat"
    file.write_text(text)
    with pytest.raises(ScientificValidationError):
        inspect_format(file)


def test_decompressed_bytes_and_ids_not_filename(tmp_path):
    raw = b"gene,a,b\n0001,1,2\n1,3,4\n"
    results = []
    for name in ["matrix.csv.gz", "matrix.dat"]:
        file = tmp_path / name
        file.write_bytes(gzip.compress(raw))
        before = file.read_bytes()
        result = inspect_format(file)
        results.append(result)
        assert result["details"]["row_ids"] == ["0001", "1"] and result["compression"] == "gzip"
        assert file.read_bytes() == before
    assert results[0]["decompressed_sha256"] == results[1]["decompressed_sha256"]
    file = tmp_path / "nine.tsv"
    file.write_text(
        "gene\t"
        + "\t".join(f"v{i}" for i in range(8))
        + "\ng\t"
        + "\t".join("1" for _ in range(8))
        + "\n"
    )
    assert inspect_format(file)["format"] == "NUMERIC_TABLE"


@pytest.mark.parametrize(
    "raw", [b"<sbml>", gzip.compress(b"gene,a\ng,1\n")[:-5], b"\xff\xfeinvalid"]
)
def test_controlled_decode_errors(tmp_path, raw):
    file = tmp_path / "file.dat"
    file.write_bytes(raw)
    with pytest.raises(ScientificValidationError):
        inspect_format(file)


def test_bounded_and_partial_formats(tmp_path):
    file = tmp_path / "file.dat"
    file.write_bytes(gzip.compress(b"A" * (4 * 1024 * 1024 + 1)))
    with pytest.raises(ScientificValidationError, match="size"):
        inspect_format(file)
    file.write_bytes(b"BAM\x01")
    assert inspect_format(file)["validation"] == "OPTIONAL_PYSAM_REQUIRED"
    file.write_text('<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core"/>')
    assert inspect_format(file)["validation"] == "XML_STRUCTURE_ONLY"
    file.write_text(">same\nACGT\n>same other\nACGT\n")
    with pytest.raises(ScientificValidationError, match="fasta_duplicate"):
        inspect_format(file)
