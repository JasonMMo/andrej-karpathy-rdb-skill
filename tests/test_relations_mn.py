"""M:N junction · 복합 PK · 복합 FK 테스트."""
from rdb_index import _pk_columns


def test_pk_columns_single():
    e = {"name": "x", "columns": [{"name": "id", "pk": True}, {"name": "n"}]}
    assert _pk_columns(e) == ["id"]


def test_pk_columns_composite():
    e = {"name": "x", "columns": [
        {"name": "a_id", "pk": True}, {"name": "b_id", "pk": True}, {"name": "n"}
    ]}
    assert _pk_columns(e) == ["a_id", "b_id"]


def test_pk_columns_none():
    e = {"name": "x", "columns": [{"name": "n"}]}
    assert _pk_columns(e) == []


from rdb_index import validate_v002_fk_targets


def _entities(*decls):
    return {name: {"name": name, "columns": cols} for name, cols in decls}


def test_v002_composite_fk_all_columns_present():
    entities = _entities(
        ("address", [
            {"name": "user_id", "pk": True},
            {"name": "seq", "pk": True},
            {"name": "city"},
        ]),
    )
    rel = {"from": "user", "to": "address", "fk_column": ["user_id", "seq"]}
    assert validate_v002_fk_targets(rel, entities) == []


def test_v002_composite_fk_missing_column():
    entities = _entities(
        ("address", [
            {"name": "user_id", "pk": True},
            {"name": "city"},
        ]),
    )
    rel = {"from": "user", "to": "address", "fk_column": ["user_id", "missing"]}
    errs = validate_v002_fk_targets(rel, entities)
    assert len(errs) == 1
    assert errs[0]["code"] == "V002"
    assert "missing" in errs[0]["message"]


from rdb_index import is_junction_entity, validate_v005_junction


def test_is_junction_entity_pure():
    e = {"name": "user_role", "columns": [
        {"name": "user_id", "pk": True},
        {"name": "role_id", "pk": True},
    ]}
    fk_columns = {"user_id", "role_id"}
    assert is_junction_entity(e, fk_columns) is True


def test_is_junction_entity_with_meta_only():
    e = {"name": "user_role", "columns": [
        {"name": "user_id", "pk": True},
        {"name": "role_id", "pk": True},
        {"name": "created_at"}, {"name": "updated_at"},
    ]}
    fk_columns = {"user_id", "role_id"}
    assert is_junction_entity(e, fk_columns) is True


def test_is_junction_entity_with_extra_data_column():
    e = {"name": "user_role", "columns": [
        {"name": "user_id", "pk": True},
        {"name": "role_id", "pk": True},
        {"name": "granted_by"},
    ]}
    fk_columns = {"user_id", "role_id"}
    assert is_junction_entity(e, fk_columns) is False


def test_v005_emits_info_for_junction():
    entity = {"name": "user_role", "columns": [
        {"name": "user_id", "pk": True}, {"name": "role_id", "pk": True}
    ]}
    fk_columns = {"user_id", "role_id"}
    msgs = validate_v005_junction(entity, fk_columns)
    assert len(msgs) == 1
    assert msgs[0]["code"] == "V005"
    assert msgs[0]["level"] == "INFO"
    assert "N:M" in msgs[0]["message"]
