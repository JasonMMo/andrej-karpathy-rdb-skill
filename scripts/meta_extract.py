"""meta_extract: cross-project learn-log → domain meta knowledge.

v0.6 C-1 — 알리먼트 리뷰 §7.1 (장기 로드맵, 실 프로젝트 3개 이상 누적 후).
복수 프로젝트의 `wiki/learn-log.md` 를 횡단해 도메인별 반복 등장 패턴을
`~/.karpathy-rdb/catalog/meta/<도메인>_meta.md` 로 추출한다.

명시적 명령으로만 호출. 자동 머지 없음. LLM/벡터 검색 없음 (Karpathy 원칙).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import pathlib
import sys
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_MIN_PROJECTS = 3
DEFAULT_OUTPUT_ROOT = pathlib.Path.home() / ".karpathy-rdb" / "catalog" / "meta"

# learn-log line: `YYYY-MM-DD | <kind> | <name> | <domain> | <요약>`
_LEARN_KINDS = {"new_entity", "new_concept", "new_rule", "false_belief"}
_SKIP_KINDS = {"contribute", "pattern-contribute"}


class LearnEntry:
    """One parsed row from wiki/learn-log.md."""

    __slots__ = ("date", "kind", "name", "domain", "summary", "project")

    def __init__(self, date: str, kind: str, name: str, domain: str, summary: str, project: str):
        self.date = date
        self.kind = kind
        self.name = name
        self.domain = domain
        self.summary = summary
        self.project = project


def parse_learn_log(text: str, project_name: str) -> List[LearnEntry]:
    """Parse the table rows of a learn-log.md into structured entries.

    Lines outside the `YYYY-MM-DD | kind | name | domain | summary` shape are
    skipped silently (frontmatter, prose, headers). Caller may log counts.
    """
    entries: List[LearnEntry] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ">", "-", "|", "<!--")):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5:
            continue
        date, kind, name, domain, summary = parts[0], parts[1], parts[2], parts[3], parts[4]
        # date sanity: YYYY-MM-DD
        if len(date) != 10 or date[4] != "-" or date[7] != "-":
            continue
        if kind in _SKIP_KINDS:
            continue
        if kind not in _LEARN_KINDS:
            continue
        if not name or not domain:
            continue
        entries.append(LearnEntry(date, kind, name, domain, summary, project_name))
    return entries


def load_project_entries(project_path: pathlib.Path) -> Tuple[List[LearnEntry], Optional[str]]:
    """Read `<project>/wiki/learn-log.md`. Returns (entries, error-or-None)."""
    log_path = project_path / "wiki" / "learn-log.md"
    if not log_path.is_file():
        return [], f"no wiki/learn-log.md at {project_path}"
    try:
        text = log_path.read_text(encoding="utf-8")
    except OSError as e:
        return [], f"read failed: {e}"
    return parse_learn_log(text, project_path.name), None


def aggregate(entries: Iterable[LearnEntry]) -> Dict[str, Dict[str, Dict]]:
    """Group entries → {domain: {kind: {name: {projects, first, last, summaries}}}}."""
    out: Dict[str, Dict[str, Dict[str, Dict]]] = defaultdict(lambda: defaultdict(dict))
    for e in entries:
        bucket = out[e.domain][e.kind].setdefault(
            e.name, {"projects": set(), "first": e.date, "last": e.date, "summaries": []}
        )
        bucket["projects"].add(e.project)
        if e.date < bucket["first"]:
            bucket["first"] = e.date
        if e.date > bucket["last"]:
            bucket["last"] = e.date
        bucket["summaries"].append((e.date, e.project, e.summary))
    return out


def render_meta(domain: str, by_kind: Dict[str, Dict[str, Dict]], min_projects: int) -> str:
    """Render a single domain's meta markdown. Only rows ≥ min_projects shown."""
    today = _dt.date.today().isoformat()
    source_projects = sorted({p for kind in by_kind.values() for r in kind.values() for p in r["projects"]})

    lines: List[str] = []
    lines.append("---")
    lines.append("type: meta")
    lines.append(f"domain: {domain}")
    lines.append(f"generated_at: {today}")
    lines.append(f"source_projects: {len(source_projects)}")
    lines.append(f"min_threshold: {min_projects}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {domain} 도메인 메타 지식")
    lines.append("")
    lines.append("> 자동 생성 (`scripts/meta_extract.py`). 직접 편집 금지.")
    lines.append(f"> {len(source_projects)}개 프로젝트의 `wiki/learn-log.md` 횡단 결과 — 반복 등장 (≥{min_projects} projects) 만 표기.")
    lines.append("")
    lines.append("**소스 프로젝트:** " + ", ".join(f"`{p}`" for p in source_projects))
    lines.append("")

    section_titles = [
        ("new_entity", "반복 등장 entity"),
        ("new_concept", "반복 등장 concept"),
        ("new_rule", "반복 등장 rule"),
        ("false_belief", "false-belief 패턴"),
    ]
    any_section = False
    for kind, title in section_titles:
        rows = by_kind.get(kind, {})
        eligible = [(name, b) for name, b in rows.items() if len(b["projects"]) >= min_projects]
        if not eligible:
            continue
        any_section = True
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| 이름 | 프로젝트 수 | 최초 등장 | 최근 등장 |")
        lines.append("|---|---|---|---|")
        for name, b in sorted(eligible, key=lambda kv: (-len(kv[1]["projects"]), kv[0])):
            lines.append(f"| {name} | {len(b['projects'])} | {b['first']} | {b['last']} |")
        lines.append("")

    if not any_section:
        lines.append("_반복 등장 패턴 없음 (모든 항목이 단일 프로젝트에만 등장)._")
        lines.append("")

    return "\n".join(lines)


def extract(
    projects: Sequence[pathlib.Path],
    output_root: pathlib.Path,
    min_projects: int = DEFAULT_MIN_PROJECTS,
    *,
    out_stream=None,
    err_stream=None,
) -> int:
    """Main entry. Returns exit code (0=ok or SKIP, 2=no readable projects)."""
    out_stream = out_stream if out_stream is not None else sys.stdout
    err_stream = err_stream if err_stream is not None else sys.stderr
    if len(projects) < min_projects:
        print(
            f"SKIP: need >= {min_projects} projects to extract meta, got {len(projects)}",
            file=out_stream,
        )
        return 0

    all_entries: List[LearnEntry] = []
    readable = 0
    for p in projects:
        entries, err = load_project_entries(p)
        if err:
            print(f"[warn] {err}", file=err_stream)
            continue
        readable += 1
        all_entries.extend(entries)

    if readable == 0:
        print("[error] no projects had a readable wiki/learn-log.md", file=err_stream)
        return 2

    by_domain = aggregate(all_entries)

    # Gate per-domain: domain needs entries from >= min_projects distinct projects
    eligible_domains: List[str] = []
    for domain, by_kind in by_domain.items():
        project_set = {p for kind in by_kind.values() for r in kind.values() for p in r["projects"]}
        if len(project_set) >= min_projects:
            eligible_domains.append(domain)
        else:
            print(
                f"SKIP domain '{domain}': appears in {len(project_set)} project(s), need {min_projects}",
                file=out_stream,
            )

    if not eligible_domains:
        print("SKIP: no domain reached project threshold", file=out_stream)
        return 0

    output_root.mkdir(parents=True, exist_ok=True)
    for domain in sorted(eligible_domains):
        md = render_meta(domain, by_domain[domain], min_projects)
        out_path = output_root / f"{_sanitize_filename(domain)}_meta.md"
        out_path.write_text(md, encoding="utf-8")
        print(f"wrote {out_path}", file=out_stream)
    return 0


def _sanitize_filename(name: str) -> str:
    """Strip path separators and surrounding whitespace. Allow unicode."""
    return name.strip().replace("/", "_").replace("\\", "_") or "unknown"


def _load_projects_file(path: pathlib.Path) -> List[pathlib.Path]:
    out: List[pathlib.Path] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(pathlib.Path(line).expanduser())
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="meta_extract", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("extract", help="extract domain meta from N projects")
    ex.add_argument("--project", action="append", default=[], help="project root path (repeatable)")
    ex.add_argument("--projects-file", type=pathlib.Path, help="file with one project path per line")
    ex.add_argument(
        "--output-root",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"output dir (default: {DEFAULT_OUTPUT_ROOT})",
    )
    ex.add_argument(
        "--min-projects",
        type=int,
        default=DEFAULT_MIN_PROJECTS,
        help=f"threshold (default: {DEFAULT_MIN_PROJECTS})",
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "extract":
        projects: List[pathlib.Path] = [pathlib.Path(p).expanduser() for p in args.project]
        if args.projects_file:
            projects.extend(_load_projects_file(args.projects_file))
        if not projects:
            print("[error] no projects given (--project or --projects-file)", file=sys.stderr)
            return 1
        return extract(projects, args.output_root, args.min_projects)
    return 1


if __name__ == "__main__":
    sys.exit(main())
