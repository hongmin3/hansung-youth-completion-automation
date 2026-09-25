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

- TEST-HYGIENE-001: 자동 검사가 없다는 11절·13절의 오래된 설명을 고쳤다. 현재는 저장소 위생 자동 검사 하나가 있고, 다른 절차는 수동이다.
- SPEC 문장을 처음 보는 사람도 읽을 수 있게 다시 썼다. 긴 문단은 나누고, 차례는 번호 목록, 예외는 `> **예외**` 상자, 이유는 `이유:` 줄로 옮겼다. 1절에 용어 표(`이 문서에서 쓰는 말`)를 더했다. 사양 내용(규칙·숫자·날짜·코드 이름·요구사항 ID·추적성 표)은 바꾸지 않았다(공통 SPEC workflow v5·렌더러 v5).
- 문서: 공통 SPEC workflow v4(AGENTS.md) — SPEC·CHANGELOG 작성 규칙(제목 이름, 기능 그룹 표, CHANGELOG ID, 예시 블록 금지, flow 흐름도, 로컬 이미지, HTML 재생성)을 한 절로 모았다. `docs/SPEC.html` 렌더러 v4: 왼쪽 목차에 지금 읽는 절·요구사항 표시.
- 준비 검사: CHANGELOG 형식 예시 블록에 실제 항목이 들어가면 `CHANGELOG_EXAMPLE_MODIFIED`로 경고한다(키트 관리 사본 `.project-check/project-readiness.js`, 기준 `.project-check/changelog-template.md`).
- 문서: `SPEC.md`의 REQ·NFR 제목 줄 13개에 기능 이름을 붙이고 5절에 기능 그룹 표를 추가했다.
  사양 내용은 바꾸지 않았다. 사람이 읽는 `docs/SPEC.html`(기능 목록·요구사항 카드·요구사항별
  변경 이력)과 렌더러 `.project-check/render-spec-html.js`를 추가하고 공통 SPEC workflow를 v3로
  갱신했다 — `SPEC.md`나 `CHANGELOG.md`를 고치면 HTML을 다시 만든다.
- REQ-MATCH-001/002: 동일인 판정 기준을 코드에 맞춰 문서 정리 — `팀`은 비교하지 않고
  `이름 + 군 + 청년 A/B`만 본다(README 문제 해결 절, SPEC 13절).
- SPEC.md: Project Version 1.0.0, Owner 역할명 지정.
- 브랜치 통합: `agent/apps-script-hardening`을 `main`에 merge했다. main에만 있던 Akela 지식
  (`knowledge/course-policy.md`, `knowledge/matching-rules.md`, 트러블슈팅 5개 절)과
  `scripts/find-project-root.ps1`을 보존하고, AGENTS.md에 main의 규칙 4개 절(Project Root 탐색,
  기초반·예배학교·결혼예비학교 절대 준수, 소스 수정 금지, 민감정보)을 옮겼다. `CLAUDE.md`는
  `@AGENTS.md` import로 통일했다. `akela.json` activity는 양쪽을 합쳤다.
- Knowledge: 태그가 없어 어떤 slice에도 들어가지 못하던 14개 절에 activity 범위를 붙였다
  (tier=should, 본문은 그대로).
- 문서: `docs/SPEC.html`을 렌더러 v3로 다시 만들었다 — 이력이 없는 요구사항에 "기록된 변경 없음" 표시.
- 2026-09-25: 워크스페이스가 프로젝트를 `projects/` 아래로 모으면서 README의 `cd` 경로를 배치와 무관한 형태로 고쳤다, AGENTS.md의 키트 문서 상대경로(`../docs/…`)를 루트 기준 설명으로 바꿨다. 준비 검사와 자체 테스트 통과.
- 2026-09-25: 공통 키트 이름이 Botyard로 바뀌어 `.project-check/`의 SPEC HTML 렌더러와 `docs/SPEC.html`의 생성기 표시를 갱신했다(형식·내용 변경 없음). 준비 검사와 자체 테스트 통과.

### Fixed

### Removed

## [1.0.0] - 2026-09-19

### Added

- SPEC.md 도입 — 기존 동작을 Requirement로 문서화 (REQ-*/NFR-*)
