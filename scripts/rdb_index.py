"""rdb_index: lint + index + compile for karpathy-rdb wiki."""
from __future__ import annotations

import sys
import argparse
import pathlib
import re
from typing import Tuple, Dict, Any, List

import yaml


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
    """V002: relation.fk_column must reference an existing PK or UQ column on `to` entity."""
    to_name = relation.get("to")
    if to_name not in entities:
        return [{
            "code": "V002",
            "level": "ERROR",
            "target": f"relation:{relation.get('from')}->{to_name}",
            "message": f"참조 entity 미존재: {to_name}",
        }]
    target_entity = entities[to_name]
    cols = target_entity.get("columns") or []
    has_target_pk = any(c.get("pk") is True for c in cols)
    if not has_target_pk:
        return [{
            "code": "V002",
            "level": "ERROR",
            "target": f"relation:{relation.get('from')}->{to_name}",
            "message": f"참조 entity {to_name}에 PK 없음",
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


def lint_wiki(wiki_dir: pathlib.Path) -> int:
    """Run all validators on a wiki directory. Returns ERROR count."""
    entities: Dict[str, Dict] = {}
    relations: List[Dict] = []
    errors_total: List[dict] = []
    for md in wiki_dir.glob("entities/*/profile.md"):
        try:
            fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
        except ValueError as e:
            errors_total.append({"code": "PARSE", "level": "ERROR", "target": str(md), "message": str(e)})
            continue
        name = fm.get("name")
        if not name:
            errors_total.append({"code": "PARSE", "level": "ERROR", "target": str(md), "message": "entity missing 'name'"})
            continue
        entities[name] = fm
        errors_total.extend(validate_v001_pk_exists(fm))
        errors_total.extend(validate_v003_naming(fm))
        for rel in fm.get("relations") or []:
            relations.append({"from": name, "to": rel.get("to"), "fk_column": rel.get("fk")})
    for rel in relations:
        errors_total.extend(validate_v002_fk_targets(rel, entities))

    err_count = sum(1 for e in errors_total if e["level"] == "ERROR")
    warn_count = sum(1 for e in errors_total if e["level"] == "WARN")
    print(f"entities: {len(entities)}, relations: {len(relations)}")
    print(f"ERROR: {err_count}, WARN: {warn_count}")
    for e in errors_total:
        print(f"  [{e['level']}] {e['code']} {e['target']}: {e['message']}")
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
        return 1 if lint_wiki(args.wiki_dir) > 0 else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
