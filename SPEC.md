# 교육 수료내역 자동입력 사양서

<!-- spec-template: v1 -->

| 항목 | 값 |
|---|---|
| Document Version | 0.1.0 |
| Last Updated | 2026-09-21 |
| Status | draft — 제한된 기존 계약 기준선 |

전체 사양 및 운영 검증 완료를 의미하지 않는다. 기존 약속과 코드가 다르면 SPEC / CODE MISMATCH로 기록하며 현재 코드를 정당화하려고 약속을 바꾸지 않는다.

## 1. 목적

수료자 명단을 교인 정보와 대조해 확인된 대상에게만 수료내역을 등록한다.

## 2. 프로젝트 범위

이번 사양화는 아래 확인된 계약에 한정한다. 제품 전체 기능은 기존 문서와 구현을 보존한다. 문서 작업 범위에서 운영 기능·인증·예약·배포·비밀값·실데이터를 변경하지 않는다.

## 5. 기능 요구사항

### REQ-CORE-001 제외 과정 유지

기초반·예배학교·결혼예비학교는 매핑 설정이 있어도 등록하지 않는다. 사용자의 별도 명시 변경 요청 없이는 이 제외 정책을 바꾸지 않는다.

근거 구현: `completion_automation.py`. 검증 근거: `README.md`.

### REQ-CORE-002 드라이런 우선

기본 실행과 --limit 5 실행은 디모데와 시트를 변경하지 않고 dry_run_plan.csv로 계획을 남긴다. --execute는 실제 입력을 수행하는 별도 단계다.

근거 구현: `completion_automation.py`. 검증 근거: `README.md`.

### REQ-CORE-003 재실행 중복 방지

이미 체크된 행은 건너뛰며 동일 과정이 이미 등록된 경우 새로 저장하지 않는다. 등록 후 시트 체크 전에 중단되어도 재실행에서 기존 등록을 확인한다.

근거 구현: `completion_automation.py`. 검증 근거: `README.md`.

## 9. 오류 처리 정책

실패나 미검증 범위를 성공으로 기록하지 않는다. 구체적인 계약별 거부/보류 결과는 5절에 따른다. 아직 근거가 부족한 오류 처리 동작은 13절의 미확정 범위이며 추측으로 확정하지 않는다.

## 11. 테스트 사양

기존 README의 수동 검증 절차를 사양에 연결했다. 자동 회귀 테스트는 미확인이다. 실제 인증·교인 데이터 접근이나 등록은 이번 작업에서 하지 않았다.

### TEST-CORE-001

대상: REQ-CORE-001. 절차: README 제외 과정 설명과 EXCLUDED_COURSES 상수를 검토한다. 실제 대상 등록 테스트는 승인된 격리 환경에서만 수행한다.

기대 결과: 해당 Requirement의 동작과 일치해야 하며 실패나 미실행은 통과로 기록하지 않는다. 실행 상태: 미실행.

### TEST-CORE-002

대상: REQ-CORE-002. 절차: README 권장 실행 순서의 python main.py --limit 5를 격리된 검증 대상에서 실행해 계획 CSV와 쓰기 없음 여부를 대조한다.

기대 결과: 해당 Requirement의 동작과 일치해야 하며 실패나 미실행은 통과로 기록하지 않는다. 실행 상태: 미실행.

### TEST-CORE-003

대상: REQ-CORE-003. 절차: README 재실행과 중복 방지 절의 입력 전/후 및 중단 후 재시도 시나리오를 승인된 테스트 대상에서 수동 확인한다.

기대 결과: 해당 Requirement의 동작과 일치해야 하며 실패나 미실행은 통과로 기록하지 않는다. 실행 상태: 미실행.

## 12. 요구사항 추적성

| Requirement | Implementation | Test | Status |
|---|---|---|---|
| REQ-CORE-001 | `completion_automation.py` | TEST-CORE-001; 근거 `README.md` | draft |
| REQ-CORE-002 | `completion_automation.py` | TEST-CORE-002; 근거 `README.md` | draft |
| REQ-CORE-003 | `completion_automation.py` | TEST-CORE-003; 근거 `README.md` | draft |

## 13. 미확정 사항

- 전체 매칭 규칙/시트 오류 복구의 사양과 안전한 합성 자동 테스트는 확인 필요다.
- 전체 readiness 및 실제 운영/CLI 검증 완료로 선언하지 않는다.
