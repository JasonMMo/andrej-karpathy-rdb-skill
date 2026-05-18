import pathlib
import shutil
import textwrap

from rdb_index import build_blueprint


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "golden_wiki"


def _copy(tmp_path):
    target = tmp_path / "wiki"
    shutil.copytree(FIXTURE, target)
    return target


def test_pattern_field_absent_when_not_in_frontmatter():
    bp = build_blueprint(FIXTURE)
    for e in bp["entities"]:
        assert "pattern" not in e, f"{e['name']} should not have pattern key"


def test_pattern_field_propagated_from_entity_frontmatter(tmp_path):
    target = _copy(tmp_path)
    customer = target / "entities" / "customer" / "profile.md"
    text = customer.read_text(encoding="utf-8")
    patched = text.replace("type: entity\n", "type: entity\npattern: F1\n", 1)
    assert patched != text, "fixture patch failed — frontmatter shape changed"
    customer.write_text(patched, encoding="utf-8")

    bp = build_blueprint(target)
    customer_entry = next(e for e in bp["entities"] if e["name"] == "customer")
    assert customer_entry.get("pattern") == "F1"

    address_entry = next(e for e in bp["entities"] if e["name"] == "address")
    assert "pattern" not in address_entry
