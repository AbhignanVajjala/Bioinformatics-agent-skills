"""Artifact contracts reject malformed evidence without certifying its truth."""

import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
NAMES = [p.name.removesuffix(".schema.json") for p in (ROOT / "schemas").glob("*.schema.json")]


def load(name):
    schema = json.loads((ROOT / "schemas" / f"{name}.schema.json").read_text())
    instance = json.loads((ROOT / "templates" / f"{name}.json").read_text())
    return schema, instance


def validate(name, instance):
    schema, _ = load(name)
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
        instance
    )


@pytest.mark.parametrize("name", NAMES)
def test_templates_match_contract(name):
    schema, instance = load(name)
    jsonschema.Draft202012Validator.check_schema(schema)
    validate(name, instance)


@pytest.mark.parametrize("name", NAMES)
def test_missing_required_field_rejected(name):
    schema, instance = load(name)
    del instance[schema["required"][0]]
    with pytest.raises(jsonschema.ValidationError):
        validate(name, instance)


@pytest.mark.parametrize("bad", ["PASSED", "success", None, 1])
def test_invalid_check_status_rejected(bad):
    _, instance = load("validation_report")
    instance["checks"][0]["status"] = bad
    with pytest.raises(jsonschema.ValidationError):
        validate("validation_report", instance)


def test_duplicates_in_sample_ids_rejected():
    _, instance = load("dataset_manifest")
    instance["sample_ids"] = ["same", "same"]
    with pytest.raises(jsonschema.ValidationError):
        validate("dataset_manifest", instance)


def test_hash_must_be_full_sha256():
    _, instance = load("analysis_run")
    instance["inputs"] = [{"path": "counts.csv", "sha256": "looks-good"}]
    with pytest.raises(jsonschema.ValidationError):
        validate("analysis_run", instance)


def test_claim_cannot_invent_a_classification():
    _, instance = load("scientific_claim_ledger")
    instance["claims"][0]["claim_type"] = "proven_cure"
    with pytest.raises(jsonschema.ValidationError):
        validate("scientific_claim_ledger", instance)


def test_invalid_timestamp_rejected():
    _, instance = load("analysis_run")
    instance["started_at"] = "yesterday"
    with pytest.raises(jsonschema.ValidationError):
        validate("analysis_run", instance)
