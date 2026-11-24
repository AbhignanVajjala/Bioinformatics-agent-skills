"""ORA scope and independent combinatorial/BH references."""

from copy import deepcopy
import math

import numpy as np
import pytest

from test_expanded import enrichment_fixture
from bioskills.expanded import ora
from bioskills.inputs import strict_json
from bioskills.science import ScientificValidationError
from bioskills.validators import check_enrichment_background


def run(data, sets, **kwargs):
    return ora(
        data,
        sets,
        organism=kwargs.get("organism", "synthetic"),
        reference=kwargs.get("reference", "v1"),
        database=kwargs.get("database", "db"),
        release=kwargs.get("release", "v1"),
    )


@pytest.mark.parametrize("field", ["organism", "reference", "database", "release"])
@pytest.mark.parametrize("value", [None, "", " \t", 1, [], True])
def test_declaration_types(field, value):
    with pytest.raises(ScientificValidationError):
        run(enrichment_fixture(), {"set": ["g0"]}, **{field: value})


@pytest.mark.parametrize("name", ["", " ", 1, None])
def test_pathway_ids(name):
    with pytest.raises(ScientificValidationError):
        run(enrichment_fixture(), {name: ["g0"]})


@pytest.mark.parametrize(
    "failure",
    [
        "missing-tested",
        "missing-selected",
        "missing-mappings",
        "numeric-target",
        "numeric-source",
        "record-type",
        "missing-record-field",
        "blank-target",
        "ambiguous",
    ],
)
def test_structural_mapping_errors(failure):
    data = enrichment_fixture()
    if failure.startswith("missing-") and failure != "missing-record-field":
        del data[failure[8:]]
    elif failure == "numeric-target":
        data["mappings"][0]["target"] = 0
    elif failure == "numeric-source":
        data["mappings"][0]["source"] = 0
    elif failure == "record-type":
        data["mappings"][0] = []
    elif failure == "missing-record-field":
        del data["mappings"][0]["source"]
    elif failure == "blank-target":
        data["mappings"][0]["target"] = " "
    else:
        data["mappings"][1]["target"] = "g0"
    with pytest.raises(ScientificValidationError):
        run(data, {"set": ["g0"]})


def test_prespecified_family_and_no_testable_status():
    data = enrichment_fixture()
    before = deepcopy(data)
    sets = {
        "hit": data["selected"],
        "null": data["tested"][10:],
        "empty": [],
        "outside": ["other"],
        "duplicate": ["g0", "g0"],
    }
    result = run(data, sets)
    assert result["supplied_family"] == 5 and result["testing_family"] == 3
    assert {x["eligibility"] for x in result["excluded_pathways"]} == {
        "EMPTY_GENE_SET",
        "NO_UNIVERSE_MEMBERS",
    }
    assert next(x for x in result["results"] if x["gene_set"] == "null")["pvalue"] == 1
    assert (
        next(x for x in result["results"] if x["gene_set"] == "duplicate")["duplicate_memberships"]
        == 1
    )
    none = run(data, {"empty": [], "outside": ["other"]})
    assert (
        none["analysis_status"] == "NOT_RUN"
        and none["status"] == "NO_TESTABLE_PATHWAYS"
        and none["testing_family"] == 0
    )
    assert data == before
    data["selected"] = []
    with pytest.raises(ScientificValidationError):
        run(data, {"set": ["g0"]})


def test_independent_exact_hypergeometric_and_bh():
    data = enrichment_fixture()
    baseline = run(data, {"hit": data["selected"], "null": data["tested"][10:]})
    assert baseline["results"][0]["pvalue"] == pytest.approx(1 / math.comb(20, 5), rel=0, abs=2e-16)
    assert baseline["results"][0]["padj"] == pytest.approx(2 / math.comb(20, 5), rel=0, abs=2e-16)
    rng = np.random.default_rng(845)
    sets = {
        f"set{i:02}": rng.choice(data["tested"], size=i + 1, replace=False).tolist()
        for i in range(20)
    }
    result = run(data, sets)
    expected = []
    for row in result["results"]:
        k = row["eligible_members"]
        overlap = row["overlap"]
        expected.append(
            sum(
                math.comb(k, x) * math.comb(20 - k, 5 - x)
                for x in range(overlap, min(5, k) + 1)
                if 0 <= 5 - x <= 20 - k
            )
            / math.comb(20, 5)
        )
    order = sorted(range(len(expected)), key=expected.__getitem__)
    adjusted = [0.0] * 20
    current = 1.0
    for rank in range(20, 0, -1):
        i = order[rank - 1]
        current = min(current, expected[i] * 20 / rank)
        adjusted[i] = current
    assert [x["pvalue"] for x in result["results"]] == pytest.approx(expected, rel=0, abs=2e-15)
    assert [x["padj"] for x in result["results"]] == pytest.approx(adjusted, rel=0, abs=2e-15)


def test_identifier_chain_and_duplicate_serialized_keys():
    data = {
        "selected": ["0001"],
        "tested": ["0001", "1", "g3"],
        "mappings": [
            {"source": g, "target": g, "organism": "synthetic", "reference": "v1"}
            for g in ["0001", "1", "g3"]
        ],
    }
    result = run(data, {"0001": ["0001"], "1": ["1"]})
    assert result["results"][0]["overlap"] == 1 and result["results"][1]["overlap"] == 0
    with pytest.raises(ScientificValidationError, match="json_duplicate"):
        strict_json('{"tested":[],"tes\\u0074ed":["1"]}')
    with pytest.raises(ScientificValidationError):
        check_enrichment_background({}, organism="s", reference="r", multiple_testing="BH")
