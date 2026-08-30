# Architecture

## Data flow
<!-- akela: id=data-flow scope=develop,test,operate tier=must -->
Google Sheet에서 교육 수료 명단을 읽고 Playwright로 디모데 교인을 검증한 뒤 수료내역을 입력하며, 성공한 행만 Sheet에 표시한다.

## Module boundaries
<!-- akela: id=module-boundaries scope=develop,test tier=should -->
CLI option과 실행 orchestration은 `main.py`, 검색·동일인 검증·중복 방지·저장은 `completion_automation.py`, 공개 설정 예시는 `config.example.py`가 담당한다.

## Apps Script boundary
<!-- akela: id=apps-script-boundary scope=develop,operate tier=must -->
`apps-script/`는 보존본이며 현재 Apps Script 운영 기준은 `../newacts-newcomer-automation/`이다. Apps Script 변경은 그 프로젝트로 라우팅한다.
