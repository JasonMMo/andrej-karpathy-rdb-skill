"""Growth-26: 재무관리 preset 살붙임 회귀.

v3 → v4 변경 사항을 잠근다:
  - journal_entry MD 헤더 entity 추가 (entry_no, fiscal_period_id,
    posted_at, total_debit, total_credit, status)
  - ledger_entry 에 journal_entry_id FK 컬럼 추가
  - ledger-belongs-to-journal concept (cardinality 1:N, on_delete cascade)
  - 'double-entry' 규칙 명문화

이 회귀가 깨지면 Growth-26 의 복식부기 표현력이 사라진 것.
"""
import pathlib
import re

import yaml

SEED = (
    pathlib.Path(__file__).resolve().parents[1]
    / ".claude" / "skills" / "karpathy-rdb" / "presets" / "재무관리.seed.md"
)

_ENTITY_RE = re.compile(
    r"^###\s+(\S.+?)\s*\n+```yaml\s*\n(.*?)\n```",
    re.MULTILINE | re.DOTALL,
)


def _split_frontmatter(text: str):
    assert text.startswith("---\n")
    end = text.find("\n---\n", 4)
    return yaml.safe_load(text[4:end]), text[end + 5 :]


def _entities(body: str) -> dict:
    m = re.search(r"^##\s+entities\s*\(시드\)\s*$", body, re.MULTILINE)
    assert m, "재무관리 seed 에 `## entities (시드)` 섹션 누락"
    start = m.end()
    nxt = re.search(r"^##\s+", body[start:], re.MULTILINE)
    section = body[start : start + nxt.start()] if nxt else body[start:]
    return {h3: yaml.safe_load(src) for h3, src in _ENTITY_RE.findall(section)}


def _concepts(body: str) -> dict:
    m = re.search(r"^##\s+concepts\s*\(시드 관계\)\s*$", body, re.MULTILINE)
    assert m, "재무관리 seed 에 `## concepts (시드 관계)` 섹션 누락"
    start = m.end()
    nxt = re.search(r"^##\s+", body[start:], re.MULTILINE)
    section = body[start : start + nxt.start()] if nxt else body[start:]
    return {h3: yaml.safe_load(src) for h3, src in _ENTITY_RE.findall(section)}


def _rules(body: str) -> list[str]:
    m = re.search(r"^##\s+rules\s*\(시드 비즈니스 규칙\)\s*$", body, re.MULTILINE)
    assert m, "재무관리 seed 에 `## rules (시드 비즈니스 규칙)` 섹션 누락"
    tail = body[m.end():]
    return [
        ln[2:].strip() for ln in tail.splitlines() if ln.startswith("- ")
    ]


def test_version_bumped_to_v4_or_higher():
    fm, _ = _split_frontmatter(SEED.read_text(encoding="utf-8"))
    assert fm["preset"] == "재무관리"
    assert fm["version"] >= 4, (
        f"Growth-26 살붙임 후 version 은 4 이상이어야 함 — got {fm['version']}"
    )


def test_journal_entry_md_header_present():
    _, body = _split_frontmatter(SEED.read_text(encoding="utf-8"))
    ents = _entities(body)
    assert "journal_entry" in ents, "Growth-26: journal_entry 헤더 entity 누락"
    je = ents["journal_entry"]
    assert je["type"] == "entity"
    assert je.get("pattern") == "MD", (
        "journal_entry 는 master-detail 헤더 — pattern: MD 권장"
    )
    cols = {c["name"]: c for c in je["columns"]}
    for required in (
        "id", "entry_no", "fiscal_period_id",
        "posted_at", "total_debit", "total_credit", "status",
    ):
        assert required in cols, (
            f"journal_entry.{required} 컬럼 누락 (Growth-26 헤더 계약)"
        )
    assert cols["entry_no"].get("unique") is True, (
        "entry_no 는 unique 여야 전표번호 중복 방지"
    )


def test_ledger_entry_carries_journal_fk():
    _, body = _split_frontmatter(SEED.read_text(encoding="utf-8"))
    ents = _entities(body)
    assert "ledger_entry" in ents
    cols = {c["name"]: c for c in ents["ledger_entry"]["columns"]}
    assert "journal_entry_id" in cols, (
        "Growth-26: ledger_entry 에 journal_entry_id FK 추가 누락"
    )
    assert cols["journal_entry_id"].get("nullable") is False, (
        "ledger_entry.journal_entry_id 는 NOT NULL (헤더 없는 분개라인 금지)"
    )


def test_ledger_belongs_to_journal_concept():
    _, body = _split_frontmatter(SEED.read_text(encoding="utf-8"))
    cons = _concepts(body)
    assert "ledger-belongs-to-journal" in cons, (
        "Growth-26: ledger-belongs-to-journal concept 누락 — "
        "Stage 1 V005 cross-domain FK 인식이 끊김"
    )
    c = cons["ledger-belongs-to-journal"]
    assert c["from"] == "journal_entry"
    assert c["to"] == "ledger_entry"
    assert c["fk_column"] == "journal_entry_id"
    assert c["cardinality"] == "1:N"
    assert c["on_delete"] == "cascade", (
        "헤더 삭제 시 라인도 함께 — on_delete: cascade 필수"
    )


def test_double_entry_rule_documented():
    _, body = _split_frontmatter(SEED.read_text(encoding="utf-8"))
    rules = _rules(body)
    blob = "\n".join(rules).lower()
    assert "double-entry" in blob or "복식부기" in blob or "차변 합" in blob, (
        "Growth-26: double-entry invariant 규칙이 rules 섹션에 명문화되어야 함"
    )
