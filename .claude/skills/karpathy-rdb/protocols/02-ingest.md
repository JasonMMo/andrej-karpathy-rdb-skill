---
type: protocol
protocol: ingest
version: 1
---

# Protocol 02 — Ingest

`/karpathy-rdb ingest [<프롬프트>|--file <path>]` 실행 시 AI가 따르는 절차.

## 입력 판별
1. 명령에 자유 프롬프트 텍스트 → **프롬프트 모드**
2. `wiki/raw/`에 미처리 파일(`_log.md`에 미등재) 존재 → **파일 모드**
3. 둘 다이면 파일 우선

## 프롬프트 모드 절차
1. **요약 압축**: 입력을 `sources/YYYY-MM-DD-prompt-<slug>.md`에 저장 (sources 템플릿 사용). 원본 프롬프트는 `raw/YYYY-MM-DD-prompt-<slug>.md`에 보존.
2. **엔티티 후보 추출**: 입력에서 명사구를 후보로 식별. 사용자에게 한 번 확인 후 신규 entity 생성.
3. **관계 후보 추출**: 동사·소유격에서 관계 후보 식별 (예: "고객은 주소를 가진다" → `customer-has-many-addresses` concept).
4. **갱신**: 각 entity의 frontmatter `columns`, `relations`, `sources` 필드 갱신.

## 파일 모드 절차
1. `raw/`의 신규 파일을 1개씩 처리
2. 파일 내용을 위와 동일하게 압축 → sources/ 페이지
3. 같은 추출 절차

## 충돌 처리
- 기존 entity와 새 정보 충돌 (예: 같은 컬럼 다른 타입) → `decisions/conflict-<YYYY-MM-DD>-<topic>.md` 생성 후 사용자에게 alert
- 절대 silent overwrite 금지

## 후처리
1. `_log.md`에 1줄 추가: `YYYY-MM-DD HH:MM | ingest | <요약 한 줄>`
2. **`learn-log.md`에 신규 지식 1줄씩 추가** (이번 ingest로 새로 알게 된 것만):
   - 신규 entity 생성 시: `YYYY-MM-DD | new_entity | <name> | <domain> | <컬럼 요약>`
   - 신규 concept 생성 시: `YYYY-MM-DD | new_concept | <name> | <domain> | <관계 요약>`
   - 신규 rule을 `rules.md`에 추가 시: `YYYY-MM-DD | new_rule | <id> | <domain> | <규칙 요약>`
   - 반증된 통념을 `false-beliefs.md`에 추가 시: `YYYY-MM-DD | false_belief | <id> | <domain> | <반증 요약>`
   - 변경(필드 추가/타입 변경 등)은 기록하지 않는다 — **신규 발견만**
3. 사용자에게 결과 보고: 생성/갱신된 페이지 목록, 미해결 질문, learn-log에 추가된 항목 수

## 멱등성
같은 source를 재ingest 시 sources/ 페이지는 갱신, entity/concept는 diff만 적용 (기존 정보 보존).
