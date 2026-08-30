# Troubleshooting

## Business invariants
<!-- akela: id=business-invariants scope=develop,test,operate tier=must -->
교육과정 허용·제외 목록, 동일인 판정, 중복 방지, 디모데 저장 성공 후 Sheet 체크 순서를 근거 없이 변경하지 않는다.

## UI selector changes
<!-- akela: id=selector-changes scope=develop,test,operate tier=should -->
디모데 UI selector는 실제 화면 변화나 재현 가능한 실패 증거를 확보한 뒤 최소 범위로 변경한다.

## Secret and outputs
<!-- akela: id=secrets scope=all tier=must -->
`config.py`, credentials/token JSON, cookie, 계정, `output/`, `user_data/`, debug HTML·image, 실행 log를 Knowledge·Evidence·응답·Git에 복사하지 않는다.
