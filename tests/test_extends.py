"""Tests for blueprint entity `extends:` resolution against catalog presets."""
import pathlib
import textwrap

import pytest

from rdb_index import (
    _parse_seed_entities,
    _load_catalog_for_domain,
    _merge_named,
    resolve_extends,
)


SAMPLE_SEED = textwrap.dedent("""\
    ---
    preset: 테스트
    version: 1
    ---

    # 테스트

    ## entities (시드)

    ### customer
    ```yaml
    type: entity
    name: customer
    columns:
      - { name: id,    type: bigserial,    pk: true,  nullable: false }
      - { name: email, type: varchar(255), nullable: false, unique: true }
    indexes:
      - { name: ix_customer_email, columns: [email], unique: true }
    ```

    ### address
    ```yaml
    type: entity
    name: address
    columns:
      - { name: id, type: bigserial, pk: true }
    ```
""")


def test_parse_seed_entities_extracts_yaml_blocks():
    parsed = _parse_seed_entities(SAMPLE_SEED)
    assert set(parsed.keys()) == {"customer", "address"}
    assert any(c["name"] == "email" for c in parsed["customer"]["columns"])


def test_parse_seed_entities_skips_non_entity_blocks():
    text = textwrap.dedent("""\
        ```yaml
        type: concept
        name: some-concept
        ```

        ```yaml
        type: entity
        name: only_one
        columns: []
        ```
    """)
    parsed = _parse_seed_entities(text)
    assert set(parsed.keys()) == {"only_one"}


def test_load_catalog_global_wins_over_plugin_preset(tmp_path):
    plugin_dir = tmp_path / "presets"
    global_dir = tmp_path / "catalog"
    plugin_dir.mkdir()
    global_dir.mkdir()
    (plugin_dir / "테스트.seed.md").write_text(
        SAMPLE_SEED.replace("varchar(255)", "varchar(100)"), encoding="utf-8"
    )
    (global_dir / "테스트.seed.md").write_text(SAMPLE_SEED, encoding="utf-8")
    out = _load_catalog_for_domain("테스트", plugin_dir, global_dir)
    email_col = next(c for c in out["customer"]["columns"] if c["name"] == "email")
    assert email_col["type"] == "varchar(255)", "global catalog should win"


def test_load_catalog_falls_back_to_plugin_preset(tmp_path):
    plugin_dir = tmp_path / "presets"
    global_dir = tmp_path / "catalog"
    plugin_dir.mkdir()
    global_dir.mkdir()  # exists but no domain file
    (plugin_dir / "테스트.seed.md").write_text(SAMPLE_SEED, encoding="utf-8")
    out = _load_catalog_for_domain("테스트", plugin_dir, global_dir)
    assert "customer" in out


def test_load_catalog_returns_empty_when_neither_exists(tmp_path):
    out = _load_catalog_for_domain("없는도메인", tmp_path / "presets", tmp_path / "catalog")
    assert out == {}


def test_merge_named_override_wins():
    base = [{"name": "a", "type": "x"}, {"name": "b", "type": "x"}]
    override = [{"name": "a", "type": "y"}, {"name": "c", "type": "z"}]
    out = _merge_named(base, override)
    by_name = {item["name"]: item for item in out}
    assert by_name["a"]["type"] == "y"  # override wins
    assert by_name["b"]["type"] == "x"  # base preserved
    assert by_name["c"]["type"] == "z"  # override-only added


def test_resolve_extends_merges_base_columns(tmp_path):
    plugin_dir = tmp_path / "presets"
    global_dir = tmp_path / "catalog"
    plugin_dir.mkdir()
    (plugin_dir / "테스트.seed.md").write_text(SAMPLE_SEED, encoding="utf-8")
    entities = {
        "vip_customer": {
            "name": "vip_customer",
            "domain": ["테스트"],
            "extends": "customer",
            "columns": [
                {"name": "vip_level", "type": "smallint"},
            ],
        }
    }
    errors = resolve_extends(entities, plugin_dir, global_dir)
    assert errors == []
    cols = {c["name"]: c for c in entities["vip_customer"]["columns"]}
    assert "id" in cols and "email" in cols and "vip_level" in cols
    assert "extends" not in entities["vip_customer"]


def test_resolve_extends_override_takes_precedence(tmp_path):
    plugin_dir = tmp_path / "presets"
    plugin_dir.mkdir()
    (plugin_dir / "테스트.seed.md").write_text(SAMPLE_SEED, encoding="utf-8")
    entities = {
        "narrow_email": {
            "name": "narrow_email",
            "domain": ["테스트"],
            "extends": "customer",
            "columns": [
                {"name": "email", "type": "varchar(50)", "nullable": False},
            ],
        }
    }
    resolve_extends(entities, plugin_dir, tmp_path / "catalog")
    email = next(c for c in entities["narrow_email"]["columns"] if c["name"] == "email")
    assert email["type"] == "varchar(50)"


def test_resolve_extends_emits_v004_when_base_missing(tmp_path):
    entities = {
        "x": {
            "name": "x",
            "domain": ["테스트"],
            "extends": "no_such_entity",
            "columns": [],
        }
    }
    errors = resolve_extends(entities, tmp_path / "presets", tmp_path / "catalog")
    assert len(errors) == 1
    assert errors[0]["code"] == "V004"
    assert "no_such_entity" in errors[0]["message"]


def test_resolve_extends_no_op_when_no_extends_field(tmp_path):
    entities = {
        "plain": {
            "name": "plain",
            "domain": ["테스트"],
            "columns": [{"name": "id", "pk": True}],
        }
    }
    errors = resolve_extends(entities, tmp_path / "presets", tmp_path / "catalog")
    assert errors == []
    assert entities["plain"]["columns"] == [{"name": "id", "pk": True}]


def test_resolve_extends_searches_all_entity_domains(tmp_path):
    plugin_dir = tmp_path / "presets"
    plugin_dir.mkdir()
    (plugin_dir / "B.seed.md").write_text(SAMPLE_SEED, encoding="utf-8")
    entities = {
        "x": {
            "name": "x",
            "domain": ["A", "B"],  # A has nothing, must fall through to B
            "extends": "customer",
            "columns": [],
        }
    }
    errors = resolve_extends(entities, plugin_dir, tmp_path / "catalog")
    assert errors == []
    assert any(c["name"] == "email" for c in entities["x"]["columns"])
