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
