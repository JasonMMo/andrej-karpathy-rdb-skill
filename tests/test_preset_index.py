"""v0.3.x C-2: preset INDEX.md 일관성 검사.

contribute Phase 7가 신규 도메인 추가 시 INDEX.md 갱신을 누락하면
다음 프로젝트의 init 추천에서 새 지식이 보이지 않는다. 이 회귀를 막는다.
"""
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PRESETS_DIR = REPO_ROOT / ".claude" / "skills" / "karpathy-rdb" / "presets"
INDEX_PATH = PRESETS_DIR / "INDEX.md"


def _list_preset_names():
    return sorted(p.stem.replace(".seed", "") for p in PRESETS_DIR.glob("*.seed.md"))


def test_index_exists():
    assert INDEX_PATH.exists(), "presets/INDEX.md 가 사라졌다 — 추천 인프라 깨짐"


def test_index_lists_every_preset():
    """모든 *.seed.md 가 INDEX.md 의 H2 섹션에 등재되어야 한다."""
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    sections = set(re.findall(r"^##\s+(\S.+?)\s*$", index_text, re.MULTILINE))
    presets = set(_list_preset_names())
    missing = presets - sections
    assert not missing, (
        f"INDEX.md 누락 도메인: {sorted(missing)}. "
        f"contribute Phase 7 (또는 신규 preset 추가) 시 INDEX.md 갱신 필요."
    )


def test_index_sections_have_required_fields():
    """각 도메인 섹션은 aliases / keywords / entities / 한 줄 4개 필드를 가져야 한다."""
    text = INDEX_PATH.read_text(encoding="utf-8")
    blocks = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    # 마지막 블록은 매칭 알고리즘 — 제외
    domain_blocks = [b for b in blocks if not b.startswith("매칭 알고리즘")]
    for blk in domain_blocks:
        header = blk.splitlines()[0].strip()
        for field in ("aliases:", "keywords:", "entities:", "한 줄:"):
            assert field in blk, f"INDEX.md '{header}' 섹션에 '{field}' 누락"


def test_index_does_not_reference_nonexistent_preset():
    """INDEX.md 의 H2 섹션이 실제 *.seed.md 파일과 매칭되어야 한다."""
    text = INDEX_PATH.read_text(encoding="utf-8")
    sections = set(re.findall(r"^##\s+(\S.+?)\s*$", text, re.MULTILINE))
    sections.discard("매칭 알고리즘 (LLM이 따를 절차)")
    presets = set(_list_preset_names())
    orphan = sections - presets
    assert not orphan, (
        f"INDEX.md 가 존재하지 않는 preset 을 참조: {sorted(orphan)}. "
        f"파일 이름 오타 또는 삭제된 preset 항목."
    )
