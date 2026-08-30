# 디모데 수료내역 자동입력 AI 인덱스

Follow `akela/PROTOCOL.md` for every task. 프로젝트 도메인 규칙은 compile된 slice를 기준으로 사용한다.

## 목적과 구조

Google Sheet의 교육 수료 명단을 읽고 Playwright로 디모데 교인을 검증해 수료내역을 입력하며 성공 행만 시트에 표시한다.

- CLI 진입점: `main.py`
- 핵심 로직: `completion_automation.py`
- 설정 예시: `config.example.py`
- 로컬 비밀 설정: `config.py`
- 의존성: `requirements.txt`
- 운영 설명과 검증 기록: `README.md`
- 별도 Apps Script 보존본: `apps-script/` (현재 운영 기준은 `../newacts-newcomer-automation/`)

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

설치, OAuth, 실행 옵션, 결과 상태, 문제 해결은 `README.md`에 있다. Apps Script 보존본의 구성은 `apps-script/README.md`를 필요할 때만 읽는다.
