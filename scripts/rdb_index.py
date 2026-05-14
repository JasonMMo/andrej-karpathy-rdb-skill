"""rdb_index: lint + index + compile for karpathy-rdb wiki."""
from __future__ import annotations

import sys
import argparse
import datetime as _dt
import pathlib
import re
from typing import Tuple, Dict, Any, List

import yaml


def _coerce_legacy_null_key(node: Any) -> Any:
    """YAML treats unquoted `null:` as the null literal (Python None).

    Legacy wikis used `null: false` for column NOT NULL. Rewrite any
    `{None: X}` key inside dicts/lists to `{'nullable': X}` so downstream
    code sees the intended boolean. New wikis should use `nullable:` directly.
    """
    if isinstance(node, dict):
        if None in node:
            node["nullable"] = node.pop(None)
        for v in node.values():
            _coerce_legacy_null_key(v)
    elif isinstance(node, list):
        for item in node:
            _coerce_legacy_null_key(item)
    return node


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from a markdown string.

    Returns (frontmatter_dict, body).
    Raises ValueError on missing or malformed frontmatter.
    """
    if not text.startswith("---"):
        raise ValueError("no frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("no frontmatter (missing closing ---)")
    fm_text, body = parts[1], parts[2]
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        raise ValueError(f"invalid yaml: {e}") from e
    if not isinstance(fm, dict):
        raise ValueError("invalid yaml: frontmatter must be a mapping")
    _coerce_legacy_null_key(fm)
    return fm, body.lstrip("\n")


def validate_v001_pk_exists(entity: Dict[str, Any]) -> List[dict]:
    """V001: every entity must have at least one column with pk: true."""
    name = entity.get("name", "<unknown>")
    columns = entity.get("columns") or []
    has_pk = any(col.get("pk") is True for col in columns)
    if has_pk:
        return []
    return [{
        "code": "V001",
        "level": "ERROR",
        "target": f"entity:{name}",
        "message": "PK 컬럼 없음 — `columns[].pk: true`인 컬럼 1개 이상 필요",
    }]


def validate_v002_fk_targets(relation: Dict[str, Any], entities: Dict[str, Dict]) -> List[dict]:
    """V002: relation FK must be sane.

    - `to` entity must exist
    - `to` entity must declare a PK (the relation references it)
    - if `fk_column` is provided, it must be a column on the `to` entity
      (has_many/belongs_to relations declared on the 1-side place the FK column
      on the N-side, i.e. on `to`)
    """
    to_name = relation.get("to")
    from_name = relation.get("from")
    fk_column = relation.get("fk_column")
    target = f"relation:{from_name}->{to_name}"
    if to_name not in entities:
        return [{
            "code": "V002",
            "level": "ERROR",
            "target": target,
            "message": f"참조 entity 미존재: {to_name}",
        }]
    cols = entities[to_name].get("columns") or []
    if not any(c.get("pk") is True for c in cols):
        return [{
            "code": "V002",
            "level": "ERROR",
            "target": target,
            "message": f"참조 entity {to_name}에 PK 없음",
        }]
    if fk_column:
        col_names = {c.get("name") for c in cols}
        if fk_column not in col_names:
            return [{
                "code": "V002",
                "level": "ERROR",
                "target": target,
                "message": f"fk_column '{fk_column}' 이(가) {to_name}에 존재하지 않음",
            }]
    return []


RESERVED_WORDS = frozenset([
    "user", "order", "group", "table", "schema", "type", "role", "name",
    "value", "key", "primary", "foreign", "references", "default", "check",
    "unique", "index", "constraint", "select", "insert", "update", "delete",
    "from", "where", "join", "having", "by", "on", "as", "in", "is", "not",
    "null", "true", "false",
])


def validate_v003_naming(entity: Dict[str, Any]) -> List[dict]:
    """V003: column names must be snake_case and avoid PostgreSQL reserved words."""
    warnings = []
    name = entity.get("name", "<unknown>")
    for col in entity.get("columns") or []:
        col_name = col.get("name", "")
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", col_name):
            warnings.append({
                "code": "V003",
                "level": "WARN",
                "target": f"entity:{name}:column:{col_name}",
                "message": f"snake_case 위반: {col_name}",
            })
        if col_name.lower() in RESERVED_WORDS:
            warnings.append({
                "code": "V003",
                "level": "WARN",
                "target": f"entity:{name}:column:{col_name}",
                "message": f"PostgreSQL 예약어: {col_name}",
            })
    return warnings


def _strip_wikilink(s: str) -> str:
    """Extract 'name' from '[[name]]'; return s unchanged if not wikilink."""
    if not s:
        return ""
    m = re.fullmatch(r"\s*\[\[(.+?)\]\]\s*", s)
    return m.group(1) if m else s


def load_wiki(wiki_dir: pathlib.Path) -> Dict[str, Any]:
    """Read all wiki markdown files and return grouped frontmatter."""
    out: Dict[str, Any] = {
        "schema": None,
        "domains": {},
        "entities": {},
        "concepts": {},
        "sources": [],
        "parse_errors": [],
    }
    schema_file = wiki_dir / "_schema.md"
    if schema_file.exists():
        try:
            fm, _ = parse_frontmatter(schema_file.read_text(encoding="utf-8"))
            out["schema"] = fm
        except ValueError as e:
            out["parse_errors"].append({
                "code": "PARSE", "level": "ERROR",
                "target": str(schema_file), "message": str(e),
            })
    for md in sorted(wiki_dir.glob("entities/*/profile.md")):
        try:
            fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        except ValueError as e:
            out["parse_errors"].append({
                "code": "PARSE", "level": "ERROR",
                "target": str(md), "message": str(e),
            })
            continue
        name = fm.get("name")
        if not name:
            out["parse_errors"].append({
                "code": "PARSE", "level": "ERROR",
                "target": str(md), "message": "entity missing 'name'",
            })
            continue
        out["entities"][name] = fm
    for md in sorted(wiki_dir.glob("domains/*/profile.md")):
        try:
            fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        except ValueError as e:
            out["parse_errors"].append({
                "code": "PARSE", "level": "ERROR",
                "target": str(md), "message": str(e),
            })
            continue
        name = fm.get("name")
        if name:
            out["domains"][name] = fm
    for md in sorted(wiki_dir.glob("concepts/*.md")):
        try:
            fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        except ValueError as e:
            out["parse_errors"].append({
                "code": "PARSE", "level": "ERROR",
                "target": str(md), "message": str(e),
            })
            continue
        cname = fm.get("name") or md.stem
        out["concepts"][cname] = fm
    sid = 1
    for md in sorted(wiki_dir.glob("sources/*.md")):
        try:
            fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        except ValueError:
            fm = {}
        out["sources"].append({
            "id": fm.get("id") or f"SRC-{sid:03d}",
            "file": str(md.relative_to(wiki_dir)).replace("\\", "/"),
            "title": fm.get("title") or md.stem,
        })
        sid += 1
    return out


def _collect_relations(entities: Dict[str, Dict], concepts: Dict[str, Dict]) -> Tuple[List[dict], List[dict]]:
    """Build (blueprint_relations, validation_relations) from entity frontmatter.

    Source frontmatter uses flat `fk: <col>` (per frontmatter-schema.md).
    Compiled blueprint emits nested `fk: {column, on_delete}` (per blueprint-spec.md);
    `on_delete` and `cardinality` are pulled from the linked concept when present.
    """
    blueprint_rels: List[dict] = []
    validation_rels: List[dict] = []
    for ename, fm in entities.items():
        for rel in fm.get("relations") or []:
            to = rel.get("to")
            fk_col = rel.get("fk")
            concept_link = rel.get("concept") or ""
            concept_name = _strip_wikilink(concept_link)
            concept = concepts.get(concept_name)
            kind = (rel.get("kind") or "").lower()
            cardinality = "1:N"
            on_delete = "restrict"
            if concept:
                cardinality = concept.get("cardinality") or cardinality
                on_delete = concept.get("on_delete") or on_delete
                fk_col = fk_col or concept.get("fk_column")
            if kind == "many_to_many":
                cardinality = "N:M"
            elif kind == "has_one":
                cardinality = concept.get("cardinality") if concept else "1:1"
            blueprint_rels.append({
                "from": ename,
                "to": to,
                "cardinality": cardinality,
                "fk": {"column": fk_col, "on_delete": on_delete},
                "concept_name": concept_name,
            })
            validation_rels.append({"from": ename, "to": to, "fk_column": fk_col})
    return blueprint_rels, validation_rels


def _run_validators(entities: Dict[str, Dict], validation_rels: List[dict]) -> List[dict]:
    results: List[dict] = []
    for _name, e in entities.items():
        results.extend(validate_v001_pk_exists(e))
        results.extend(validate_v003_naming(e))
    for rel in validation_rels:
        results.extend(validate_v002_fk_targets(rel, entities))
    return results


def build_blueprint(wiki_dir: pathlib.Path) -> Dict[str, Any]:
    """Scan wiki/ and assemble a `_blueprint.yaml`-shaped dict per blueprint-spec.md."""
    data = load_wiki(wiki_dir)
    entities_list = []
    for name, fm in data["entities"].items():
        entities_list.append({
            "name": name,
            "table": fm.get("table") or name,
            "schema": fm.get("schema") or "public",
            "columns": fm.get("columns") or [],
            "indexes": fm.get("indexes") or [],
            "constraints": fm.get("constraints") or [],
        })
    domains_list = []
    for name, fm in data["domains"].items():
        domains_list.append({
            "name": name,
            "description": fm.get("description") or "",
            "entities": fm.get("entities") or [],
        })
    if not domains_list:
        derived: Dict[str, List[str]] = {}
        for ename, fm in data["entities"].items():
            for d in fm.get("domain") or []:
                derived.setdefault(d, []).append(ename)
        for dname, ents in derived.items():
            domains_list.append({"name": dname, "description": "", "entities": ents})
    blueprint_rels, validation_rels = _collect_relations(data["entities"], data["concepts"])
    validation_results = data["parse_errors"] + _run_validators(data["entities"], validation_rels)
    errs = [v for v in validation_results if v["level"] == "ERROR"]
    warns = [v for v in validation_results if v["level"] == "WARN"]
    infos = [v for v in validation_results if v["level"] == "INFO"]
    project = (data["schema"] or {}).get("project") or wiki_dir.name
    return {
        "version": 1,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": project,
        "domains": domains_list,
        "entities": entities_list,
        "relations": blueprint_rels,
        "business_rules": [],
        "sources": data["sources"],
        "validation": {
            "passed": len(errs) == 0,
            "errors": [
                {"code": e["code"], "target": e["target"], "message": e["message"]}
                for e in errs
            ],
            "warnings": [
                {"code": w["code"], "target": w["target"], "message": w["message"]}
                for w in warns
            ],
            "infos": [
                {"code": i["code"], "target": i["target"], "message": i["message"]}
                for i in infos
            ],
        },
    }


def write_compile_report(wiki_dir: pathlib.Path, blueprint: Dict[str, Any]) -> pathlib.Path:
    v = blueprint["validation"]
    lines = [
        "# Compile Report",
        "",
        f"- generated_at: {blueprint['generated_at']}",
        f"- project: {blueprint['project']}",
        f"- entities: {len(blueprint['entities'])}",
        f"- relations: {len(blueprint['relations'])}",
        f"- passed: {v['passed']}",
        f"- ERROR: {len(v['errors'])}, WARN: {len(v['warnings'])}, INFO: {len(v['infos'])}",
    ]
    if v["errors"]:
        lines += ["", "## Errors"]
        lines += [f"- **{e['code']}** {e['target']} — {e['message']}" for e in v["errors"]]
    if v["warnings"]:
        lines += ["", "## Warnings"]
        lines += [f"- **{w['code']}** {w['target']} — {w['message']}" for w in v["warnings"]]
    out = wiki_dir / "compile-report.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def compile_wiki(wiki_dir: pathlib.Path) -> int:
    """Compile wiki → _blueprint.yaml + compile-report.md. Returns ERROR count."""
    bp = build_blueprint(wiki_dir)
    (wiki_dir / "_blueprint.yaml").write_text(
        yaml.safe_dump(bp, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    write_compile_report(wiki_dir, bp)
    err_count = len(bp["validation"]["errors"])
    warn_count = len(bp["validation"]["warnings"])
    print(f"entities: {len(bp['entities'])}, relations: {len(bp['relations'])}")
    print(f"ERROR: {err_count}, WARN: {warn_count}")
    for e in bp["validation"]["errors"]:
        print(f"  [ERROR] {e['code']} {e['target']}: {e['message']}")
    for w in bp["validation"]["warnings"]:
        print(f"  [WARN] {w['code']} {w['target']}: {w['message']}")
    return err_count


def lint_wiki(wiki_dir: pathlib.Path) -> int:
    """Run all validators on a wiki directory. Returns ERROR count.

    Read-only counterpart to compile_wiki — no files written.
    """
    bp = build_blueprint(wiki_dir)
    err_count = len(bp["validation"]["errors"])
    warn_count = len(bp["validation"]["warnings"])
    print(f"entities: {len(bp['entities'])}, relations: {len(bp['relations'])}")
    print(f"ERROR: {err_count}, WARN: {warn_count}")
    for e in bp["validation"]["errors"]:
        print(f"  [ERROR] {e['code']} {e['target']}: {e['message']}")
    for w in bp["validation"]["warnings"]:
        print(f"  [WARN] {w['code']} {w['target']}: {w['message']}")
    return err_count


def main() -> int:
    parser = argparse.ArgumentParser(prog="rdb_index")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_lint = sub.add_parser("lint")
    p_lint.add_argument("wiki_dir", type=pathlib.Path)
    p_compile = sub.add_parser("compile")
    p_compile.add_argument("wiki_dir", type=pathlib.Path)
    args = parser.parse_args()
    if args.cmd == "lint":
        return 1 if lint_wiki(args.wiki_dir) > 0 else 0
    if args.cmd == "compile":
        return 1 if compile_wiki(args.wiki_dir) > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
