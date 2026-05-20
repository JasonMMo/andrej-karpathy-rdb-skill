"""Growth-25: seed 컨벤션(`references/seed-spec.md`) 강제.

본 테스트는 `presets/*.seed.md` 가 seed-spec 의 1~6장 컨벤션을 따르는지
검증한다. 신규 도메인을 추가하거나 contribute 가 글로벌 카탈로그를
갱신할 때, 본 컨벤션을 깨면 회귀로 잡힌다.
"""
import pathlib
import re

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PRESETS_DIR = REPO_ROOT / ".claude" / "skills" / "karpathy-rdb" / "presets"
SEED_GLOB = sorted(PRESETS_DIR.glob("*.seed.md"))

# H3 + ```yaml ... ``` 블록 (lazy, multiline).
_ENTITY_BLOCK_RE = re.compile(
    r"^###\s+(\S.+?)\s*\n+```yaml\s*\n(.*?)\n```",
    re.MULTILINE | re.DOTALL,
)


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """프론트매터(dict)와 본문(str)을 분리. 없으면 ({}, text)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_yaml = text[4:end]
    body = text[end + 5 :]
    return yaml.safe_load(fm_yaml) or {}, body


def _entities_section(body: str) -> str:
    """`## entities (시드)` 다음부터 다음 `## ` 직전까지를 잘라낸다."""
    m = re.search(r"^##\s+entities\s*\(시드\)\s*$", body, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+", body[start:], re.MULTILINE)
    return body[start : start + nxt.start()] if nxt else body[start:]


def test_presets_directory_has_seeds():
    assert SEED_GLOB, f"{PRESETS_DIR} 에 *.seed.md 가 하나도 없음"


@pytest.mark.parametrize("seed_path", SEED_GLOB, ids=lambda p: p.name)
def test_seed_frontmatter_valid(seed_path):
    fm, _ = _split_frontmatter(seed_path.read_text(encoding="utf-8"))
    assert fm, f"{seed_path.name}: YAML frontmatter 누락 (seed-spec §2)"
    assert "preset" in fm, f"{seed_path.name}: frontmatter `preset` 누락"
    assert "version" in fm, f"{seed_path.name}: frontmatter `version` 누락"

    # preset 값은 파일명 stem 과 일치
    expected_preset = seed_path.stem.replace(".seed", "")
    assert fm["preset"] == expected_preset, (
        f"{seed_path.name}: frontmatter preset={fm['preset']!r} != 파일명 "
        f"{expected_preset!r} (seed-spec §1)"
    )

    # version 은 양의 정수
    assert isinstance(fm["version"], int) and fm["version"] >= 1, (
        f"{seed_path.name}: version={fm['version']!r} 은 양의 정수여야 함"
    )


@pytest.mark.parametrize("seed_path", SEED_GLOB, ids=lambda p: p.name)
def test_seed_h1_matches_preset(seed_path):
    fm, body = _split_frontmatter(seed_path.read_text(encoding="utf-8"))
    m = re.search(r"^#\s+(\S.+?)\s*$", body, re.MULTILINE)
    assert m, f"{seed_path.name}: H1 누락 (seed-spec §3.1)"
    assert m.group(1) == fm["preset"], (
        f"{seed_path.name}: H1={m.group(1)!r} != preset={fm['preset']!r} "
        f"(seed-spec §3.1)"
    )


@pytest.mark.parametrize("seed_path", SEED_GLOB, ids=lambda p: p.name)
def test_seed_entities_section_present(seed_path):
    _, body = _split_frontmatter(seed_path.read_text(encoding="utf-8"))
    section = _entities_section(body)
    assert section.strip(), (
        f"{seed_path.name}: `## entities (시드)` 섹션 누락/비어있음 "
        f"(seed-spec §3.2)"
    )
    blocks = _ENTITY_BLOCK_RE.findall(section)
    assert blocks, (
        f"{seed_path.name}: entities 섹션에 `### <name> + ```yaml`` 블록이 "
        f"하나도 없음 (seed-spec §3.2)"
    )


@pytest.mark.parametrize("seed_path", SEED_GLOB, ids=lambda p: p.name)
def test_entity_yaml_name_matches_h3(seed_path):
    _, body = _split_frontmatter(seed_path.read_text(encoding="utf-8"))
    section = _entities_section(body)
    for h3, yaml_src in _ENTITY_BLOCK_RE.findall(section):
        data = yaml.safe_load(yaml_src)
        assert isinstance(data, dict), (
            f"{seed_path.name}: '{h3}' YAML 블록이 dict 가 아님"
        )
        assert data.get("type") == "entity", (
            f"{seed_path.name}: '{h3}' type != entity (seed-spec §3.2)"
        )
        assert data.get("name") == h3, (
            f"{seed_path.name}: H3='{h3}' != yaml.name={data.get('name')!r} "
            f"(seed-spec §3.2)"
        )
        # domain 필드는 배열이어야 함 (seed-spec §4)
        domain = data.get("domain")
        assert isinstance(domain, list) and domain, (
            f"{seed_path.name}: '{h3}' domain 필드는 비어있지 않은 배열이어야 함 "
            f"(seed-spec §4); got {domain!r}"
        )
