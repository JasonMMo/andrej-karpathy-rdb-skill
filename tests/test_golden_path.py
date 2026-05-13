import pathlib
import shutil
from rdb_index import lint_wiki

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "golden_wiki"


def test_golden_wiki_lints_clean():
    err_count = lint_wiki(FIXTURE)
    assert err_count == 0


def test_golden_wiki_breaks_when_pk_removed(tmp_path):
    target = tmp_path / "wiki"
    shutil.copytree(FIXTURE, target)
    bad = target / "entities" / "customer" / "profile.md"
    text = bad.read_text(encoding="utf-8")
    bad.write_text(text.replace("pk: true,", "pk: false,"), encoding="utf-8")
    err_count = lint_wiki(target)
    assert err_count >= 1
