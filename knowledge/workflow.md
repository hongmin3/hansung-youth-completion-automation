# Workflow

## Safe validation
<!-- akela: id=safe-validation scope=develop,test tier=must -->
먼저 `.venv/bin/python -m py_compile main.py completion_automation.py config.example.py`로 문법을 확인한다. 외부 조회가 필요 없는 검증을 우선한다.

## Dry-run
<!-- akela: id=dry-run scope=test,operate tier=must -->
`main.py --limit 5`는 입력하지 않는 드라이런이지만 인증과 외부 시스템 조회가 발생할 수 있다. 외부 접근이 요청 범위에 있을 때만 수행한다.

## Execute gate
<!-- akela: id=execute-gate scope=operate tier=must -->
`--execute`는 디모데와 Sheet 데이터를 실제 변경한다. 명시적인 실행 요청과 대상 범위 확인 없이는 사용하지 않는다.
