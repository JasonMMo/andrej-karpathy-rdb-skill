---
type: preset-index
version: 2
purpose: |
  `/karpathy-rdb init <도메인>` 시 LLM이 사용자 입력과 매칭하여 유사 도메인을
  추천하는 데 사용. 정확 매치가 없을 때 aliases/keywords/entities/한줄 정의를
  비교해 상위 3개를 후보로 제시한다.

  Karpathy 원칙 유지: 벡터 DB 없음, RAG 없음, 파일·frontmatter·LLM 컨텍스트 윈도우로 충분.

  새 preset 추가/contribute 시 이 파일에 항목 추가 필수.
---

# Preset Catalog Index

12개 시드 도메인의 매칭 메타데이터. 항목은 `한글명`(파일명과 동일) 기준 정렬.

## 결재
- aliases: 승인, 전자결재, 결재라인, 결재시스템, approval, workflow, approval-line
- keywords: 결재요청, 결재라인, 결재이력, 순차결재, 병렬결재, 위임, 회수, 반려
- entities: approval_template, approval_request, approval_line, approval_history
- 한 줄: 한국 SI 표준 — 순차/병렬/혼합 결재 라인 + RO 이력 + 위임/회수

## 게시판
- aliases: 게시글, 공지, 공지사항, 게시물, BBS, board, post, bulletin
- keywords: 게시판, 댓글, 첨부, 카테고리, 익명, 비밀글, 답글
- entities: board, post, comment, attachment
- 한 줄: 다중 카테고리 + 익명/회원 글 + 트리형 댓글 + 첨부 N개

## 고객관리
- aliases: CRM, 회원관리, 회원, 컨택트, customer, contact, member
- keywords: 고객, 연락처, 주소록, 고객분류, 컨택로그, 상담이력
- entities: customer, customer_category, address, contact_log
- 한 줄: B2C/B2B 고객 + 다중 주소 + 응대 이력 + 분류 트리

## 공통코드
- aliases: 코드, 코드관리, 시스템코드, 공통, code, common-code, lookup
- keywords: 그룹코드, 코드값, 코드명, 정렬, 활성여부, 다국어 라벨
- entities: code_group, code_value, code_label
- 한 줄: 모든 도메인이 참조하는 lookup 테이블 + 그룹/값 2단 + 다국어

## 권한관리
- aliases: 인증, 인가, 사용자, 역할, ACL, RBAC, auth, permission, role, user
- keywords: 사용자, 역할, 권한, 메뉴권한, 데이터권한, 정책
- entities: app_user, role, permission, user_role, role_permission
- 한 줄: RBAC 기본 — 사용자·역할·권한 N:M + 메뉴/데이터 권한 분리

## 배송관리
- aliases: 배송, 출고, 물류, 택배, 운송, delivery, shipping, logistics, courier
- keywords: 배송, 택배사, 추적, tracking, 출고, 배송상태, 분할배송, 반품
- entities: courier, delivery, delivery_item, delivery_tracking
- 한 줄: 주문 출고 이후 물류 — 택배사·추적이력(RO) + 상태머신(pending→picked→in_transit→delivered)

## 알림
- aliases: notification, message, push, 알람, 알람센터, 메시지
- keywords: 알림, 푸시, SMS, 이메일, 인앱, 알림설정, 수신거부
- entities: notification_template, notification, notification_log, notification_preference
- 한 줄: 다채널 발송(SMS/이메일/인앱/push) + 템플릿 + 수신선호 + 로그

## 인사관리
- aliases: HR, HRM, 직원, 직원관리, 근태, 휴가, 인사, human-resources
- keywords: 직원, 부서, 직급, 근태, 출퇴근, 휴가, 연차, 조직도
- entities: employee, department, position, attendance, leave_request
- 한 줄: 직원·부서·직급 + 일별 근태 + 휴가 신청·승인

## 재고관리
- aliases: 재고, 창고, 입출고, 자재, 물류, inventory, stock, warehouse
- keywords: 재고, 입고, 출고, 이동, 창고, 안전재고, 재고조정
- entities: product, warehouse, stock, stock_movement
- 한 줄: 다창고 재고 + 입출고/이동 이력(RO) + 안전재고

## 재무관리
- aliases: 회계, 재무, 거래, 분개, 원장, finance, accounting, ledger
- keywords: 분개, 거래, 차변, 대변, 원장, 계정과목, 재무제표
- entities: account, journal_entry, journal_line, fiscal_period
- 한 줄: 복식부기 분개·원장 + 계정과목 트리 + 회계기간

## 주문관리
- aliases: 주문, 주문서, 발주, 판매, 결제, order, sales, purchase, payment
- keywords: 주문, 주문상품, 결제, 배송, 주문상태, 주문이력
- entities: sales_order, order_item, payment, order_status_history
- 한 줄: 주문·라인·결제 + 상태머신(pending→confirmed→shipped→delivered) + 이력(RO)

## 파일관리
- aliases: 첨부, 파일, 업로드, 스토리지, 문서, file, attachment, document, storage
- keywords: 파일, 폴더, 업로드, 다운로드, 버전, 공유, 만료
- entities: file_entry, folder, file_version, file_share
- 한 줄: 폴더 트리 + 파일/버전 + 공유 권한 + 만료 정책

---

## 매칭 알고리즘 (LLM이 따를 절차)

1. 사용자 입력 토큰화 → 한글/영문 모두 추출
2. 각 preset의 (제목 + aliases + keywords + entities + 한 줄)을 후보 풀로 사용
3. 점수 산출:
   - 제목·aliases 완전 일치: +5
   - keywords 부분 일치: 토큰당 +2
   - entities 영문명 일치: +3
   - 한 줄 의미적 유사 (LLM 판단): +1~3
4. 점수 ≥ 5: 정확 매치 — 자동 선택, 사용자 confirm 후 사용
5. 점수 2~4: 유사 후보 — 상위 3개 제시 + "없음(빈 wiki)" 옵션
6. 모두 0: 매치 없음 — 빈 wiki로 시작 + ingest 안내

매칭 근거(어느 키워드가 잡혔는지)를 사용자에게 1줄로 함께 표시한다.
