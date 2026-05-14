import pytest
from rdb_index import parse_frontmatter


def test_parse_frontmatter_returns_dict_and_body():
    text = """---
type: entity
name: customer
columns:
  - { name: id, pk: true }
---

# customer body
"""
    fm, body = parse_frontmatter(text)
    assert fm["type"] == "entity"
    assert fm["name"] == "customer"
    assert fm["columns"][0]["pk"] is True
    assert "customer body" in body


def test_parse_frontmatter_missing_raises():
    with pytest.raises(ValueError, match="no frontmatter"):
        parse_frontmatter("no frontmatter here")


def test_parse_frontmatter_malformed_yaml_raises():
    text = """---
type: entity
name: : bad
---
"""
    with pytest.raises(ValueError, match="invalid yaml"):
        parse_frontmatter(text)


def test_parse_frontmatter_legacy_null_key_coerced_to_nullable():
    """YAML `null:` (unquoted) parses as Python None — must be coerced to 'nullable'."""
    text = """---
type: entity
name: customer
columns:
  - { name: id, pk: true, null: false }
  - { name: email, null: false }
---
"""
    fm, _ = parse_frontmatter(text)
    assert None not in fm["columns"][0]
    assert fm["columns"][0]["nullable"] is False
    assert fm["columns"][1]["nullable"] is False
