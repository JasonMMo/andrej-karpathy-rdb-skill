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
