import pathlib
import shutil
import yaml

from rdb_index import build_blueprint, compile_wiki

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "golden_wiki"


def _copy_golden(tmp_path):
    target = tmp_path / "wiki"
    shutil.copytree(FIXTURE, target)
    return target


def test_build_blueprint_returns_schema_compliant_dict():
    bp = build_blueprint(FIXTURE)
    for key in ("version", "generated_at", "project", "domains",
                "entities", "relations", "business_rules", "sources",
                "validation"):
        assert key in bp, f"missing top-level key: {key}"
    assert bp["version"] == 1
    assert bp["project"] == "고객관리"
    assert bp["validation"]["passed"] is True
    assert bp["validation"]["errors"] == []


def test_build_blueprint_entities_have_required_fields():
    bp = build_blueprint(FIXTURE)
    names = {e["name"] for e in bp["entities"]}
    assert names == {"customer", "address"}
    customer = next(e for e in bp["entities"] if e["name"] == "customer")
    assert customer["table"] == "customer"
    assert customer["schema"] == "public"
    assert any(c.get("pk") is True for c in customer["columns"])


def test_build_blueprint_relations_use_nested_fk_form():
    bp = build_blueprint(FIXTURE)
    assert len(bp["relations"]) == 1
    rel = bp["relations"][0]
    assert rel["from"] == "customer"
    assert rel["to"] == "address"
    assert rel["cardinality"] == "1:N"
    assert rel["fk"] == {"column": "customer_id", "on_delete": "cascade"}
    assert rel["concept_name"] == "customer-has-many-addresses"


def test_build_blueprint_derives_domains_from_entities_when_no_profiles():
    bp = build_blueprint(FIXTURE)
    assert any(d["name"] == "고객관리" for d in bp["domains"])
    domain = next(d for d in bp["domains"] if d["name"] == "고객관리")
    assert set(domain["entities"]) == {"customer", "address"}


def test_compile_wiki_writes_blueprint_yaml_and_report(tmp_path):
    target = _copy_golden(tmp_path)
    rc = compile_wiki(target)
    assert rc == 0
    bp_path = target / "_blueprint.yaml"
    rep_path = target / "compile-report.md"
    assert bp_path.exists()
    assert rep_path.exists()
    loaded = yaml.safe_load(bp_path.read_text(encoding="utf-8"))
    assert loaded["version"] == 1
    assert loaded["project"] == "고객관리"
    assert loaded["validation"]["passed"] is True
    report = rep_path.read_text(encoding="utf-8")
    assert "Compile Report" in report
    assert "passed: True" in report
    assert "entities: 2" in report
    assert "relations: 1" in report


def test_compile_wiki_returns_nonzero_when_errors(tmp_path):
    target = _copy_golden(tmp_path)
    bad = target / "entities" / "customer" / "profile.md"
    bad.write_text(
        bad.read_text(encoding="utf-8").replace("pk: true,", "pk: false,"),
        encoding="utf-8",
    )
    rc = compile_wiki(target)
    assert rc >= 1
    loaded = yaml.safe_load((target / "_blueprint.yaml").read_text(encoding="utf-8"))
    assert loaded["validation"]["passed"] is False
    assert any(e["code"] == "V001" for e in loaded["validation"]["errors"])


def test_v002_fails_when_fk_column_not_on_to_entity():
    from rdb_index import validate_v002_fk_targets
    entities = {
        "customer": {"name": "customer", "columns": [{"name": "id", "pk": True}]},
        "address": {"name": "address", "columns": [{"name": "id", "pk": True}]},
    }
    relation = {"from": "customer", "to": "address", "fk_column": "customer_id"}
    errors = validate_v002_fk_targets(relation, entities)
    assert len(errors) == 1
    assert errors[0]["code"] == "V002"
    assert "customer_id" in errors[0]["message"]
