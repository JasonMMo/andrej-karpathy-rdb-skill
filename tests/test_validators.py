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


def test_v002_belongs_to_checks_fk_on_from_side():
    """Gap 4: belongs_to places FK on FROM (declaring N-side)."""
    entities = {
        "customer": {
            "name": "customer",
            "columns": [{"name": "id", "pk": True}, {"name": "category_id"}],
        },
        "customer_category": {
            "name": "customer_category",
            "columns": [{"name": "id", "pk": True}, {"name": "code"}],
        },
    }
    relation = {"from": "customer", "to": "customer_category",
                "fk_column": "category_id", "kind": "belongs_to"}
    assert validate_v002_fk_targets(relation, entities) == []


def test_v002_belongs_to_fails_when_fk_missing_on_from():
    """Gap 4: belongs_to flags missing FK column on FROM entity."""
    entities = {
        "customer": {
            "name": "customer",
            "columns": [{"name": "id", "pk": True}],  # no category_id
        },
        "customer_category": {
            "name": "customer_category",
            "columns": [{"name": "id", "pk": True}],
        },
    }
    relation = {"from": "customer", "to": "customer_category",
                "fk_column": "category_id", "kind": "belongs_to"}
    errors = validate_v002_fk_targets(relation, entities)
    assert len(errors) == 1
    assert "customer" in errors[0]["message"]
    assert "category_id" in errors[0]["message"]


def test_v002_has_many_checks_fk_on_to_side():
    """Gap 4: has_many places FK on TO (child N-side)."""
    entities = {
        "customer": {"name": "customer", "columns": [{"name": "id", "pk": True}]},
        "address": {
            "name": "address",
            "columns": [{"name": "id", "pk": True}, {"name": "customer_id"}],
        },
    }
    relation = {"from": "customer", "to": "address",
                "fk_column": "customer_id", "kind": "has_many"}
    assert validate_v002_fk_targets(relation, entities) == []


def test_v002_many_to_many_skips_column_check():
    """Gap 4: many_to_many uses junction table — FK column check skipped."""
    entities = {
        "user": {"name": "user", "columns": [{"name": "id", "pk": True}]},
        "role": {"name": "role", "columns": [{"name": "id", "pk": True}]},
    }
    relation = {"from": "user", "to": "role",
                "fk_column": "user_id", "kind": "many_to_many"}
    assert validate_v002_fk_targets(relation, entities) == []


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
