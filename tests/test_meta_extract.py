"""Tests for scripts/meta_extract.py — v0.6 C-1."""
from __future__ import annotations

import io
import pathlib

import pytest

import meta_extract as me


def _mk_project(root: pathlib.Path, name: str, log_lines: list[str]) -> pathlib.Path:
    p = root / name
    (p / "wiki").mkdir(parents=True)
    body = "---\ntype: learn-log\n---\n\n# log\n\n" + "\n".join(log_lines) + "\n"
    (p / "wiki" / "learn-log.md").write_text(body, encoding="utf-8")
    return p


# ---------------------------------------------------------------- parse


def test_parse_learn_log_extracts_valid_rows():
    text = "\n".join(
        [
            "---", "type: learn-log", "---",
            "# header",
            "> blockquote",
            "- bullet",
            "2026-05-01 | new_entity | customer | 고객관리 | 첫 고객 엔티티",
            "2026-05-02 | new_concept | customer-address | 고객관리 | 1:N 관계",
            "2026-05-03 | contribute | 고객관리 | 고객관리 | v1->v2",
            "garbage line",
            "2026-05-04 | new_rule | unique-email | 고객관리 | 이메일 유니크",
            "2026-05-05 | false_belief | phone-required | 고객관리 | 필수 아님",
            "bad-date | new_entity | x | y | z",
        ]
    )
    rows = me.parse_learn_log(text, "projA")
    kinds = [r.kind for r in rows]
    # contribute and pattern-contribute filtered; bad-date filtered; garbage filtered
    assert kinds == ["new_entity", "new_concept", "new_rule", "false_belief"]
    assert all(r.project == "projA" for r in rows)
    assert rows[0].domain == "고객관리"


def test_parse_skips_unknown_kind_and_empty_fields():
    text = "2026-05-01 | totally_made_up | x | y | z\n2026-05-02 | new_entity |  | 고객관리 | empty name\n"
    assert me.parse_learn_log(text, "p") == []


# ---------------------------------------------------------------- aggregate


def test_aggregate_groups_by_domain_kind_name(tmp_path):
    pa = _mk_project(tmp_path, "projA", ["2026-05-01 | new_entity | customer | 고객관리 | a"])
    pb = _mk_project(tmp_path, "projB", ["2026-05-03 | new_entity | customer | 고객관리 | b"])
    pc = _mk_project(tmp_path, "projC", ["2026-05-05 | new_entity | order | 주문관리 | c"])

    entries = []
    for p in (pa, pb, pc):
        rows, err = me.load_project_entries(p)
        assert err is None
        entries.extend(rows)

    agg = me.aggregate(entries)
    assert set(agg.keys()) == {"고객관리", "주문관리"}
    customer = agg["고객관리"]["new_entity"]["customer"]
    assert customer["projects"] == {"projA", "projB"}
    assert customer["first"] == "2026-05-01"
    assert customer["last"] == "2026-05-03"


# ---------------------------------------------------------------- skip gates


def test_skip_when_fewer_than_min_projects(tmp_path, capsys):
    pa = _mk_project(tmp_path, "projA", ["2026-05-01 | new_entity | customer | 고객관리 | x"])
    rc = me.extract([pa], tmp_path / "out", min_projects=3)
    assert rc == 0
    out = capsys.readouterr().out
    assert "SKIP" in out and "got 1" in out
    assert not (tmp_path / "out").exists()


def test_skip_when_no_domain_reaches_threshold(tmp_path, capsys):
    # 3 projects total (passes outer gate), but each is a different domain
    pa = _mk_project(tmp_path, "projA", ["2026-05-01 | new_entity | customer | 고객관리 | x"])
    pb = _mk_project(tmp_path, "projB", ["2026-05-01 | new_entity | order | 주문관리 | x"])
    pc = _mk_project(tmp_path, "projC", ["2026-05-01 | new_entity | sku | 재고관리 | x"])
    rc = me.extract([pa, pb, pc], tmp_path / "out", min_projects=3)
    assert rc == 0
    out = capsys.readouterr().out
    assert "no domain reached" in out


def test_error_when_no_readable_projects(tmp_path, capsys):
    fake = [tmp_path / "missing1", tmp_path / "missing2", tmp_path / "missing3"]
    rc = me.extract(fake, tmp_path / "out", min_projects=3)
    assert rc == 2
    err = capsys.readouterr().err
    assert "no projects had a readable" in err


# ---------------------------------------------------------------- render


def test_extract_writes_meta_for_eligible_domain(tmp_path):
    common = "2026-05-{:02d} | new_entity | customer | 고객관리 | row"
    projs = [
        _mk_project(tmp_path, f"proj{i}", [common.format(i)])
        for i in range(1, 4)
    ]
    out_root = tmp_path / "out"
    rc = me.extract(projs, out_root, min_projects=3)
    assert rc == 0
    meta = out_root / "고객관리_meta.md"
    assert meta.is_file()
    text = meta.read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "domain: 고객관리" in text
    assert "source_projects: 3" in text
    assert "min_threshold: 3" in text
    assert "## 반복 등장 entity" in text
    assert "| customer | 3 | 2026-05-01 | 2026-05-03 |" in text


def test_render_omits_section_when_no_rows_meet_threshold(tmp_path):
    # 3 projects, entity 'a' in all 3 (kept), concept 'c' in only 1 (omitted)
    _mk_project(tmp_path, "p1", [
        "2026-05-01 | new_entity | a | dom | x",
        "2026-05-01 | new_concept | c | dom | only here",
    ])
    _mk_project(tmp_path, "p2", ["2026-05-01 | new_entity | a | dom | x"])
    _mk_project(tmp_path, "p3", ["2026-05-01 | new_entity | a | dom | x"])
    out_root = tmp_path / "out"
    rc = me.extract([tmp_path / "p1", tmp_path / "p2", tmp_path / "p3"], out_root, 3)
    assert rc == 0
    text = (out_root / "dom_meta.md").read_text(encoding="utf-8")
    assert "## 반복 등장 entity" in text
    assert "## 반복 등장 concept" not in text


def test_render_empty_meta_when_all_sections_filtered(tmp_path):
    # 3 projects (passes outer gate), all share domain (passes per-domain gate),
    # but each names a different entity → no row >= 3
    _mk_project(tmp_path, "p1", ["2026-05-01 | new_entity | a | dom | x"])
    _mk_project(tmp_path, "p2", ["2026-05-01 | new_entity | b | dom | x"])
    _mk_project(tmp_path, "p3", ["2026-05-01 | new_entity | c | dom | x"])
    out_root = tmp_path / "out"
    rc = me.extract([tmp_path / "p1", tmp_path / "p2", tmp_path / "p3"], out_root, 3)
    assert rc == 0
    text = (out_root / "dom_meta.md").read_text(encoding="utf-8")
    assert "반복 등장 패턴 없음" in text


# ---------------------------------------------------------------- CLI


def test_cli_extract_with_project_flags(tmp_path, capsys):
    pa = _mk_project(tmp_path, "p1", ["2026-05-01 | new_entity | x | d | s"])
    rc = me.main([
        "extract",
        "--project", str(pa),
        "--output-root", str(tmp_path / "out"),
        "--min-projects", "1",
    ])
    assert rc == 0
    assert (tmp_path / "out" / "d_meta.md").is_file()


def test_cli_extract_with_projects_file(tmp_path):
    p1 = _mk_project(tmp_path, "p1", ["2026-05-01 | new_entity | x | d | s"])
    p2 = _mk_project(tmp_path, "p2", ["2026-05-01 | new_entity | x | d | s"])
    listing = tmp_path / "projects.txt"
    listing.write_text(f"# comment\n{p1}\n\n{p2}\n", encoding="utf-8")
    rc = me.main([
        "extract",
        "--projects-file", str(listing),
        "--output-root", str(tmp_path / "out"),
        "--min-projects", "2",
    ])
    assert rc == 0
    assert (tmp_path / "out" / "d_meta.md").is_file()


def test_cli_errors_when_no_projects(capsys):
    rc = me.main(["extract", "--output-root", "/tmp/x"])
    assert rc == 1
    assert "no projects given" in capsys.readouterr().err
