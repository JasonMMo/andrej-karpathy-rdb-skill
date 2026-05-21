"""Seed convention 회귀: column type 에 `(n,m)` 형 정밀도가 있으면 따옴표 필수.

배경(false_belief 발견):
  YAML flow-mapping `{ key: value, ... }` 안에서 콤마는 **엔트리 구분자**.
  따라서 `type: numeric(15,2)` 는 `{'type': 'numeric(15', '2)': None}`
  으로 파싱되어 DDL 렌더 시 `NUMERIC(15` 처럼 잘림.

이 회귀가 깨지면 Stage 2 DDL 이 깨진 NUMERIC 타입을 생성한다.
새 seed 작성자가 같은 함정을 다시 밟지 않도록 catalog 전체를 잠근다.
"""
import pathlib
import re

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PRESETS_DIR = REPO_ROOT / ".claude" / "skills" / "karpathy-rdb" / "presets"
SEED_FILES = sorted(PRESETS_DIR.glob("*.seed.md"))

_ENTITY_BLOCK_RE = re.compile(
    r"^###\s+(\S.+?)\s*\n+```yaml\s*\n(.*?)\n```",
    re.MULTILINE | re.DOTALL,
)
_TRUNCATED_PAREN_RE = re.compile(r"\([^)]*$")


def _iter_entity_blocks():
    for seed in SEED_FILES:
        text = seed.read_text(encoding="utf-8")
        for name, src in _ENTITY_BLOCK_RE.findall(text):
            try:
                doc = yaml.safe_load(src)
            except yaml.YAMLError as exc:
                pytest.fail(f"{seed.name} / {name}: YAML 파싱 실패 — {exc}")
            if not isinstance(doc, dict) or doc.get("type") != "entity":
                continue
            yield seed.name, name, doc


@pytest.mark.parametrize("seed_name,entity_name,doc", list(_iter_entity_blocks()))
def test_column_type_has_no_truncated_paren(seed_name, entity_name, doc):
    """모든 column.type 은 `(` 가 열렸으면 `)` 로 닫혀 있어야 함."""
    cols = doc.get("columns") or []
    for col in cols:
        if not isinstance(col, dict):
            continue
        ctype = col.get("type")
        if not isinstance(ctype, str):
            continue
        assert not _TRUNCATED_PAREN_RE.search(ctype), (
            f"{seed_name} / {entity_name}.{col.get('name')}: "
            f"type='{ctype}' — 잘린 괄호. "
            f"YAML flow `{{...}}` 안에서 `numeric(15,2)` 같은 콤마 포함 타입은 "
            f'반드시 따옴표로 감싸야 함: `type: "numeric(15,2)"`'
        )


def test_known_decimal_precision_types_are_quoted():
    """`(n,m)` 형 정밀도 패턴이 등장하는 모든 seed 파일에서 따옴표 누락 0건."""
    pattern = re.compile(
        r"type:\s*(?!['\"])(numeric|decimal)\(\d+,\d+\)",
        re.IGNORECASE,
    )
    offenders = []
    for seed in SEED_FILES:
        for ln_no, line in enumerate(
            seed.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if pattern.search(line):
                offenders.append(f"{seed.name}:{ln_no}: {line.strip()}")
    assert not offenders, (
        "다음 라인의 numeric/decimal 정밀도 타입에 따옴표가 없음:\n"
        + "\n".join(offenders)
    )
