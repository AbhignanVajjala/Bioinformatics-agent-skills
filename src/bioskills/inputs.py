"""Shared exact-text and serialized-input boundaries; no identity inference."""

import csv
import io
import json

import pandas as pd

from bioskills.science import ScientificValidationError, require, validate_labels


def require_text(value, field):
    require(
        isinstance(value, str) and bool(value.strip()), field, "Nonblank scalar string required."
    )


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "json_duplicate", "Duplicate JSON object key.")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ScientificValidationError("json: Nonfinite JSON constant.")

    require(isinstance(raw, (str, bytes)), "json", "Serialized JSON text/bytes required.")
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, ScientificValidationError):
            raise
        raise ScientificValidationError("json: Malformed or unsupported JSON.") from error


def parse_table_text(text, delimiter, *, index_header=False):
    try:
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter, strict=True))
    except csv.Error as error:
        raise ScientificValidationError("table_structure: Malformed delimited records.") from error
    require(len(rows) >= 2 and len(rows[0]) >= 2, "table_structure", "Header and data required.")
    header = rows[0]
    require(len(set(header)) == len(header), "duplicate_ids", "Duplicate raw table header.")
    validate_labels(header if index_header else header[1:], "table_header")
    require(
        all(len(row) == len(header) for row in rows[1:]),
        "table_structure",
        "Every record must match the header field count.",
    )
    table = pd.DataFrame(
        [row[1:] for row in rows[1:]], columns=header[1:], index=[row[0] for row in rows[1:]]
    )
    validate_labels(table.index)
    require(table.index.is_unique, "duplicate_ids", "Duplicate row identities.")
    return table
