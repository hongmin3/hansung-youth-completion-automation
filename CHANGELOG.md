# Changelog

이 파일은 **무엇이 바뀌었는가**만 담는다. 현재 사양은 `SPEC.md`, 현재 작업 진행 상태는
`progress.md`에 있다. 같은 내용을 두 곳에 쓰지 않는다.

가능하면 각 항목 앞에 Requirement ID를 붙인다.

```text
### Changed
- REQ-EXPORT-002: HTML 파일명에 실행 시간을 포함하도록 변경

### Fixed
- REQ-QUERY-001: 인증 만료 시 잘못된 성공 상태를 반환하던 문제 수정
```

Semantic Versioning은 강제하지 않는다. 프로젝트에 Versioning 정책이 있으면 그것을 따른다.

## [Unreleased]

### Added

- NFR-SEC-001 / NFR-DATA-001: 저장소 위생 자동 검사(TEST-HYGIENE-001,
  `tests/test_repository_hygiene.py`). `.gitignore` 선언과 git의 실제 무시 동작을 따로
  확인하고, 추적 파일에 민감 산출물이 없는지, `config.example.py`에 실제 값이 없는지,
  시트 쓰기가 E·G 두 열로 제한되는지 본다. 이 프로젝트의 첫 자동 테스트다 — 두
  요구사항의 '측정'은 사람 눈이 필요 없고, 실수로 커밋한 개인정보는 되돌리기 어렵다.

### Changed

- REQ-MATCH-001/002: 동일인 판정 기준을 코드에 맞춰 문서 정리 — `팀`은 비교하지 않고
  `이름 + 군 + 청년 A/B`만 본다(README 문제 해결 절, SPEC 13절).
- SPEC.md: Project Version 1.0.0, Owner 역할명 지정.

### Fixed

### Removed

## [1.0.0] - 2026-09-19

### Added

- SPEC.md 도입 — 기존 동작을 Requirement로 문서화 (REQ-*/NFR-*)
