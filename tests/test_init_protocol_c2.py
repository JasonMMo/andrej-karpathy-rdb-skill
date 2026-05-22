"""v0.6 C-2: protocols/01-init.md Phase 1 Q2 3단계 fallback 무결성.

C-2 매칭 정책 (로컬 INDEX → 글로벌 catalog → meta) 가 protocol 문서에
명시되어 있는지 검증. 문서 보강이 누락되면 LLM 이 글로벌 카탈로그/메타를
무시하고 로컬 INDEX 만 보게 되므로, 텍스트 키워드로 회귀를 방지.
"""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
INIT_PROTOCOL = REPO_ROOT / ".claude" / "skills" / "karpathy-rdb" / "protocols" / "01-init.md"


def _read_protocol() -> str:
    assert INIT_PROTOCOL.is_file(), f"missing {INIT_PROTOCOL}"
    return INIT_PROTOCOL.read_text(encoding="utf-8")


def test_q2_has_three_stage_fallback_headers():
    text = _read_protocol()
    # 세 단계 헤더가 모두 존재해야 함
    assert "**2-1." in text, "단계 2-1 (로컬 INDEX) 헤더 누락"
    assert "**2-2." in text, "단계 2-2 (글로벌 카탈로그) 헤더 누락"
    assert "**2-3." in text, "단계 2-3 (메타 컨텍스트) 헤더 누락"


def test_q2_mentions_global_catalog_path():
    text = _read_protocol()
    assert "~/.karpathy-rdb/catalog/" in text, "글로벌 카탈로그 경로 누락"


def test_q2_mentions_meta_file_path():
    text = _read_protocol()
    # C-1 출력 경로 — _meta.md 패턴
    assert "_meta.md" in text, "C-1 메타 파일 경로 (_meta.md) 누락"
    assert "catalog/meta/" in text, "메타 디렉터리 경로 누락"


def test_q2_documents_skip_pass_for_missing_global_or_meta():
    text = _read_protocol()
    # 글로벌/메타 부재 시 폴백이 명시되어야 함
    assert "SKIP=PASS" in text, "SKIP=PASS 폴백 키워드 누락 (글로벌/메타 부재 처리)"


def test_q2_references_alignment_review_section():
    text = _read_protocol()
    assert "§7.2" in text, "알리먼트 리뷰 §7.2 (C-2 spec) 참조 누락"


def test_q2_keeps_score_thresholds():
    text = _read_protocol()
    # v0.3.x 의 점수 분기 (≥5 / 2~4 / 매치 0) 가 유지되는지
    assert "점수 ≥ 5" in text, "정확 매치 임계 누락"
    assert "점수 2~4" in text, "유사 매치 임계 누락"
    assert "매치 0" in text, "매치 0 분기 누락"
