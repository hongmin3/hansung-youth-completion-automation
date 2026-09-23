# 디모데 수료내역 자동입력 AI 인덱스

Invoke the `task-observer` skill before the first tool call.

Follow `akela/PROTOCOL.md` for every task. 프로젝트 도메인 규칙은 compile된 slice를 기준으로 사용한다.

## 목적과 구조

Google Sheet의 교육 수료 명단을 읽고 Playwright로 디모데 교인을 검증해 수료내역을 입력하며 성공 행만 시트에 표시한다.

- CLI 진입점: `main.py`
- 핵심 로직: `completion_automation.py`
- 설정 예시: `config.example.py`
- 로컬 비밀 설정: `config.py`
- 의존성: `requirements.txt`
- 운영 설명과 검증 기록: `README.md`

이 프로젝트는 Apps Script 코드를 갖지 않는다. Apps Script 운영 기준은 `../newacts-newcomer-automation/`이다.

## 작업 시작 순서

1. 이어지는 작업이면 `progress.md`를 확인한다.
2. CLI 옵션이면 `main.py`, 검색·검증·저장이면 `completion_automation.py`의 대상 함수만 확인한다.
3. 실제 실행 절차가 필요할 때만 README 해당 절을 읽는다.
4. 여러 단계 변경이면 시트와 디모데 각각의 영향 및 드라이런 방법을 먼저 정리한다.

## 안전한 확인 명령

```bash
.venv/bin/python -m py_compile main.py completion_automation.py config.example.py
.venv/bin/python main.py --limit 5
```

두 번째 명령은 드라이런이지만 외부 시스템을 조회할 수 있다. 인증과 외부 접근이 요청 범위에 있을 때만 실행한다. `--execute`는 실제 데이터를 변경하므로 사용자의 명시적 요청 없이는 사용하지 않는다.

## 변경 금지 및 주의

- 교육과정 허용·제외 목록, 동일인 판정, 중복 방지, 성공 후 체크 순서를 임의 변경하지 않는다.
- `config.py`, `credentials.json`, `token.json`, 쿠키, 계정 정보를 읽어 출력하거나 커밋하지 않는다.
- `output/`, `user_data/`, 디버그 HTML·이미지, 실행 로그는 진단에 꼭 필요할 때만 확인한다.
- 디모데 UI 선택자 변경은 실제 화면 변화의 증거 없이 추측하지 않는다.
- Apps Script 수정 요청은 `../newacts-newcomer-automation/AGENTS.md`를 우선한다.

## 컨텍스트 효율

- 제외: `.git/`, `.venv/`, `__pycache__/`, `user_data/`, `output/`, `config.py`, 인증 JSON, `result_log.txt`, `debug_*`.
- 대형 `completion_automation.py`는 함수명이나 오류 문자열을 먼저 검색하고 필요한 줄만 읽는다.
- README의 실제 실행 기록은 운영 이력 확인이 필요한 경우에만 읽는다.
- READ-ONCE를 적용하고 수정 후 diff와 문법 검사 또는 대상 드라이런만 확인한다.
- 성공 로그 전체 대신 처리 요약만, 실패 시 해당 대상과 오류 주변만 확인한다.

## 상세 정보

설치, OAuth, 실행 옵션, 결과 상태, 문제 해결은 `README.md`에 있다. Apps Script 코드 위치는 `../docs/APPS_SCRIPT.md`를 필요할 때만 읽는다.

## 읽기 범위

요청 대상 함수와 README의 필요한 절만 확인한다.

이 절은 이전에 `CLAUDE.md`에만 있어 Codex가 볼 수 없던 규칙이다. AI 지침의 원본은 이 파일 하나다. 같은 디렉터리의 `CLAUDE.md`는 이 파일을 `@` import 하는 두 줄짜리 파일이며 `scripts/sync-agent-docs.sh`가 관리한다. Claude 전용 지침도 여기에 적는다.

<!-- readme-guidance: start -->
## README 작성 기준

- 처음 보는 사람이 **무엇을 해주는 프로젝트인지, 왜 필요한지, 어떻게 시작하는지** 이해할 수 있게 쓴다.
- 첫 부분은 쉬운 한두 문장과 실제 사용 예로 설명한다. 전문 용어는 필요한 곳에서 풀어 쓴다.
- 준비 사항 → 설치 → 첫 실행 → 기대 결과 순서의 **빠른 시작**을 앞에 둔다. 확인한 명령만 적는다.
- 자세한 운영 규칙, 내부 구조, 검증 기록은 `docs/` 등 별도 문서에 두고 README에서 연결한다.
- README는 현재 기능과 사용법을 설명한다. 세션별 작업 경과나 수정 내역을 길게 나열하지 않는다.
- 구현과 README가 어긋나지 않게 함께 갱신한다. 미검증 기능·플랫폼·제한사항은 분명히 구분한다.
- 기존 프로젝트의 기능·설정·민감정보·고유 문서 체계를 보존한다. 문서 정리를 이유로 실행 동작을 바꾸지 않는다.
<!-- readme-guidance: end -->

<!-- project-readiness-command: start -->
## 프로젝트 완료 검사

하위 폴더에서 작업을 시작했더라도 완료 전에는 이 프로젝트 루트로 이동하여 다음 명령을 실행한다.
```text
node .project-check/project-readiness.js .
```
검사 실패를 해결하거나 미완료로 보고한다. 이 검사는 문서와 경로 연결을 확인하며 프로젝트 자체 테스트와 실제 동작 검증을 대신하지 않는다.
<!-- project-readiness-command: end -->

<!-- project-spec-guidance: start -->
## 사양 기반 개발 (SPEC)

<!-- spec-workflow: v3 -->

`SPEC.md`가 이 프로젝트가 **어떻게 동작해야 하는가**의 기준이다. 코드의 현재 동작은 사양이
아니다. 아래는 상위 기준이고, 실제 절차(계획·테스트·검증)는 기존 Skill을 그대로 쓴다.

**작업 시작 전** — 기능 추가·변경·버그 수정이면 먼저 `SPEC.md`에서 ① 관련 Requirement,
② 그 Requirement의 구현, ③ 관련 테스트, ④ 변경 영향 범위를 확인한다. 해당 Requirement가
없는 신규 기능은 **구현 전에** SPEC에 추가한다. typo, 주석, 문서만 바꾸는 작업은 예외다.

**구현** — 사양에 없는 기능을 임의로 추가하지 않는다. 요구사항이 불충분하거나 모순되면
추측으로 확정하지 말고 SPEC의 "13. 미확정 사항"에 `(TBD)` 또는 `확인 필요`로 남기고
사용자에게 알린다.

**변경 요청 판별** — 요청을 받으면 먼저 현재 SPEC · 요청 · 기존 구현 · 변경 의도를 대조해
둘 중 무엇인지 정한다.

- **사양 변경**: `SPEC.md` 수정 → 테스트 수정·추가 → 구현 → 검증 → `CHANGELOG.md`
- **기존 사양 미충족(버그)**: SPEC 유지 → 재현 테스트 → 코드 수정 → regression 확인 → `CHANGELOG.md`

버그를 고치려고 올바른 기존 사양을 바꾸지 않는다.

**완료 전** — `Requirement → 구현 → 테스트 → 실제 실행 결과`를 모두 확인한다. 테스트 PASS는
실제 동작 검증을 대체하지 않는다. 실행 가능한 프로젝트는 대표 실행 경로를 실제로 돌리고
출력을 읽는다.

**완료 시** — 검증을 통과하면 관련 문서(`CHANGELOG.md`, `progress.md`, 필요하면 `README.md`와
`SPEC.md`)를 갱신하고 저장소를 커밋·푸시한다. 사용자 요청을 기다리지 않으며 하위 프로젝트
세션에도 동일하게 적용한다. 게이트·CI·라이브 세션 충돌 회피는 설치된 키트의 공통 `AGENTS.md`
push 규칙을 따른다.
`SPEC.md`나 `CHANGELOG.md`를 고쳤으면 `node .project-check/render-spec-html.js .`로 사람이 읽는
`docs/SPEC.html`을 다시 만들어 같은 커밋에 넣는다. 이 HTML은 두 문서의 사본(기능 목록·요구사항별
변경 이력 포함)이므로 직접 고치지 않으며, 준비 검사가 낡은 HTML을 실패로 잡는다.

**SPEC / CODE 불일치** — 조용히 맞추지 말고 다음 형식으로 보고한다.

```text
SPEC / CODE MISMATCH

Requirement:
Specification:
Current Implementation:
Difference:
Action: SPEC 수정 / CODE 수정 / 사용자 확인 필요
```

코드의 현재 상태를 정당화하려고 SPEC을 고치지 않는다.

**ID 규칙** — `REQ-<CATEGORY>-NNN`, `NFR-<CATEGORY>-NNN`, `TEST-<CATEGORY>-NNN`.
CATEGORY는 대문자·숫자, NNN은 세 자리. 제목 줄에는 ID 뒤에 기능 이름을 쓴다
(`### REQ-EXPORT-001 CSV 저장`). CHANGELOG 항목 앞에 ID를 붙이면 그 요구사항의 변경 이력으로 모인다. 한 번 부여한 ID는 재사용하거나 의미를 바꾸지 않고,
삭제한 ID를 다른 기능에 돌려쓰지 않는다. 추적은 테스트 쪽에 남긴다(예: 테스트 위에
`Validates: REQ-QUERY-001`). 검색용 주석을 모든 함수에 강제로 달지 않는다.

**문서 경계** — 같은 내용을 두 곳에 두지 않는다.

| 파일 | 담는 것 |
|---|---|
| `SPEC.md` | 현재 시스템이 어떻게 동작해야 하는가 |
| `CHANGELOG.md` | 무엇이 변경되었는가 |
| `progress.md` | 현재 작업이 어디까지 진행됐는가 |
| `knowledge/` | AI가 작업할 때 필요한 판단 규칙·맥락 |
| `README.md` | 사람이 설치하고 사용하는 방법 |
| `AGENTS.md` | AI가 따라야 하는 작업 규칙 |

SPEC 내용을 `knowledge/`에 복제하지 않는다. knowledge는 Requirement ID를 **참조**만 한다
(예: "REQ-EXPORT-001을 고칠 때 한글 파일명 encoding 회귀를 항상 확인한다").
<!-- project-spec-guidance: end -->
