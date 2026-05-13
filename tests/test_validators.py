import pytest
from rdb_index import validate_v001_pk_exists, validate_v002_fk_targets, validate_v003_naming


def test_v001_passes_when_entity_has_pk():
    entity = {
        "type": "entity",
        "name": "customer",
        "columns": [
            {"name": "id", "pk": True},
            {"name": "name"},
        ],
    }
    errors = validate_v001_pk_exists(entity)
    assert errors == []


def test_v001_fails_when_no_pk_column():
    entity = {
        "type": "entity",
        "name": "broken",
        "columns": [
            {"name": "id"},
            {"name": "name"},
        ],
    }
    errors = validate_v001_pk_exists(entity)
    assert len(errors) == 1
    assert errors[0]["code"] == "V001"
    assert "broken" in errors[0]["target"]


def test_v001_fails_when_columns_empty():
    entity = {"type": "entity", "name": "empty", "columns": []}
    errors = validate_v001_pk_exists(entity)
    assert len(errors) == 1
    assert errors[0]["code"] == "V001"


def test_v002_passes_when_fk_targets_pk():
    entities = {
        "customer": {"name": "customer", "columns": [{"name": "id", "pk": True}]},
        "address": {"name": "address", "columns": [{"name": "id", "pk": True}, {"name": "customer_id"}]},
    }
    relation = {"from": "customer", "to": "address", "fk_column": "customer_id"}
    errors = validate_v002_fk_targets(relation, entities)
    assert errors == []


def test_v002_fails_when_fk_target_missing():
    entities = {
        "customer": {"name": "customer", "columns": [{"name": "id", "pk": True}]},
    }
    relation = {"from": "customer", "to": "ghost", "fk_column": "customer_id"}
    errors = validate_v002_fk_targets(relation, entities)
    assert len(errors) == 1
    assert errors[0]["code"] == "V002"


def test_v003_passes_for_snake_case():
    entity = {"name": "customer", "columns": [{"name": "customer_id"}, {"name": "email_address"}]}
    assert validate_v003_naming(entity) == []


def test_v003_warns_on_camelcase():
    entity = {"name": "customer", "columns": [{"name": "customerId"}]}
    warnings = validate_v003_naming(entity)
    assert len(warnings) == 1
    assert warnings[0]["code"] == "V003"


def test_v003_warns_on_reserved_word():
    entity = {"name": "customer", "columns": [{"name": "user"}]}
    warnings = validate_v003_naming(entity)
    assert any(w["code"] == "V003" for w in warnings)
