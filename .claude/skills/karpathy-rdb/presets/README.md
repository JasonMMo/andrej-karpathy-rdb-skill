# 도메인 프리셋

각 `.seed.md` 파일은 그 도메인의 시드 entity·concept·rule을 담은 단일 markdown.
`/karpathy-rdb init`이 `--preset <도메인>` 플래그를 받으면 본 파일의 내용을 사용자 wiki에 적용한다.

## 형식
```yaml
---
preset: <도메인 한국어명>
version: 1
---

# <도메인>

## entities (시드)
<entity 정의 (entity profile.md frontmatter 발췌)>

## concepts (시드 관계)
<concept 정의>

## rules (시드 비즈니스 규칙)
<RULE>
```

## 새 프리셋 추가
1. 본 디렉터리에 `<도메인명>.seed.md` 추가
2. 위 형식 준수
3. README의 카탈로그에 등재

## 카탈로그
- `고객관리.seed.md` — customer / address / contact_log
- `주문관리.seed.md` — sales_order / order_item / payment
- `재고관리.seed.md` — product / sku / warehouse / stock
- `인사관리.seed.md` — employee / department / position
- `재무관리.seed.md` — account / fiscal_period / ledger_entry
