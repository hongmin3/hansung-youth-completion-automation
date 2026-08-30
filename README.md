# 청년 양육 수료내역 디모데 자동입력

Google Sheet의 수료자 명단을 읽어 한성교회 디모데의 `청년관리 > 교인검색(청년)`에서 교인을 찾고, 검증된 사람에게만 수료내역을 등록하는 Python/Playwright 자동화입니다. 등록에 성공했거나 동일 과정이 이미 등록된 사람은 Google Sheet의 `입력여부` 체크박스를 체크합니다.

## 자동화 구성

- `main.py`: 실행 진입점
- `completion_automation.py`: 시트 읽기, 교인 검색·검증, 수료 등록, 체크박스 갱신 로직
- `config.example.py`: 설정 예시. 복사해서 `config.py`로 사용
- `requirements.txt`: Python 패키지 목록
- `output/dry_run_plan.csv`: 드라이런 결과
- `output/execution_result.csv`: 실제 실행 결과

`config.py`, `credentials.json`, `token.json`, 실행 로그와 결과 파일에는 민감정보가 포함될 수 있어 Git에 올라가지 않도록 `.gitignore`에 등록되어 있습니다.

## 실제 처리 흐름

1. Google Sheet에서 `구분 / 군 / 팀 / 이름 / 핸드폰 / 담당자 / 입력여부`를 읽습니다.
2. `입력여부`가 이미 체크된 행은 건너뜁니다.
3. 허용된 `청년-` 교육과정인지 확인합니다.
4. 디모데 검색창의 이름과 핸드폰 값을 매번 모두 지워 이전 사람의 검색값이 남지 않게 합니다.
5. 핸드폰이 있으면 전화번호로 먼저 검색합니다.
   - 검색 결과 중 `이름+전화번호`가 유일하게 일치하면 군·팀이 달라도 동일인으로 판단합니다.
6. 전화번호로 찾지 못하거나 번호가 없으면 이름으로 다시 검색합니다.
   - 이때는 `이름+군`이 같고 디모데의 교인 구분이 `교인 > 청년 (A)` 또는 `(B)`인 사람이 정확히 한 명일 때만 진행합니다.
   - `신군(아하)`는 `신군`, `조군(아너스)`는 `조군`처럼 괄호 속 세부 명칭을 제거해 비교합니다.
   - 이름·군으로 찾은 디모데 교인에게 전화번호가 있으면 시트의 `핸드폰`도 보완합니다.
7. 교인 상세 창에서 동일한 교육과정이 이미 있으면 중복 등록하지 않습니다.
8. 신규 등록 시 상태 `수료`, 수료일 `20260621`, 수료연도 `2026`, 강사명은 시트의 `담당자`로 저장합니다.
9. 신규 저장 성공 또는 기존 등록 확인 후에만 `입력여부`를 체크합니다.
10. 불일치, 복수 일치, 과정 미등록은 입력하지 않고 결과 CSV에 사유를 남깁니다.

## 허용 교육과정

| 시트 `구분` | 디모데에서 선택하는 과정 |
|---|---|
| LTC | 청년-LTC |
| 확신반 | 청년-확신반 |
| 성장반 | 청년-성장반 |
| 성경대학 | 청년-성경대학 |
| 교리대학 | 청년-교리대학 |

`기초반`, `예배학교`, `결혼예비학교`는 현재 명시적인 제외 대상입니다. `config.py`에 매핑을 추가해도 코드에서 차단하며, 추후 교육과정이 확정되고 사용자가 별도로 요청한 뒤에만 코드를 변경합니다.

## 준비 사항

- macOS 또는 Playwright Chromium을 실행할 수 있는 환경
- Python 3.10 이상 권장
- 디모데 로그인 계정
- 대상 Google Sheet 접근 권한
- 실제 실행 및 체크박스 자동 갱신에는 Google Sheets OAuth Desktop Client 파일 필요

현재 대상 시트는 다음과 같습니다.

```text
https://docs.google.com/spreadsheets/d/1ZDMY1uPsekhh9vqoSt89oBB6T-RPZkb501l-pvgZuoM/edit?gid=987654321
```

시트 탭 이름은 `통합 명단`이고 열 순서는 반드시 아래와 같아야 합니다.

```text
구분 / 군 / 팀 / 이름 / 핸드폰 / 담당자 / 입력여부
```

## 설치

```bash
cd ~/Desktop/자동화/'새가족 수료여부 자동입력'
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
cp config.example.py config.py
```

이미 `config.py`가 있다면 덮어쓰지 말고 누락된 설정만 추가합니다.

## Google Sheets OAuth 준비

쿠키 방식은 만료 시 `401 Unauthorized`가 발생하므로 실제 운영은 OAuth 방식을 사용합니다.

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트를 만듭니다.
2. Google Sheets API를 활성화합니다.
3. Google 인증 플랫폼에서 앱 이름과 지원 이메일 등 OAuth 동의 화면을 설정합니다.
4. 테스트 상태라면 자동화를 실행할 Google 계정을 테스트 사용자에 추가합니다.
5. `클라이언트 > 클라이언트 만들기`에서 애플리케이션 유형을 `데스크톱 앱`으로 선택합니다.
6. JSON을 다운로드하고 프로젝트 폴더에 `credentials.json`으로 저장합니다.
7. 최초 실행 시 열리는 Google 승인 창에서 시트 접근을 허용합니다.
8. 승인이 끝나면 `token.json`이 자동 생성되며 다음 실행부터 재사용됩니다.

두 JSON 파일은 절대 GitHub에 커밋하지 않습니다.

## `config.py` 설정

`config.example.py`를 참고해 다음 값을 입력합니다.

```python
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZDMY1uPsekhh9vqoSt89oBB6T-RPZkb501l-pvgZuoM/edit?gid=987654321"
SHEET_TAB_NAME = "통합 명단"

DIMODE_URL = "https://hansungv6.dimode.co.kr/WebYouth/Default.aspx"
USER_ID = "디모데 아이디"
USER_PW = "디모데 비밀번호"

GOOGLE_OAUTH_CLIENT_FILE = "credentials.json"
GOOGLE_OAUTH_TOKEN_FILE = "token.json"
```

`GOOGLE_COOKIES`는 OAuth 파일이 없는 드라이런의 임시 CSV 다운로드에만 사용합니다. 쿠키가 만료되면 OAuth를 설정해야 합니다.

## 권장 실행 순서

가상환경을 활성화합니다.

```bash
cd ~/Desktop/자동화/'새가족 수료여부 자동입력'
source .venv/bin/activate
```

먼저 5명만 드라이런합니다. 디모데와 시트는 변경되지 않습니다.

```bash
python main.py --limit 5
```

결과는 `output/dry_run_plan.csv`에서 확인합니다. 이상이 없으면 전체 드라이런을 합니다.

```bash
python main.py
```

첫 실제 입력은 한 명만 실행해 디모데 저장값과 시트 체크를 직접 확인합니다.

```bash
python main.py --execute --limit 1
```

확인이 끝나면 전체 실제 입력을 실행합니다.

```bash
python main.py --execute
```

전화번호 자동 보완 검색을 생략하려면 다음 옵션을 사용합니다.

```bash
python main.py --skip-phone-lookup
```

## 실행 옵션

| 옵션 | 의미 |
|---|---|
| 옵션 없음 | 전체 드라이런 |
| `--execute` | 디모데 실제 저장 및 시트 체크 |
| `--limit N` | 최대 N개 행만 처리 |
| `--skip-phone-lookup` | 번호가 빈 사람의 이름 기반 번호 보완 조회 생략 |
| `--sheet-csv PATH` | Google Sheet 대신 전체 내보내기 CSV를 입력으로 사용 |
| `--defer-sheet-checks` | OAuth가 없는 긴급 운영에서 체크를 외부 작업으로 미룸 |

`--sheet-csv`는 원본 시트의 전체 행 순서를 유지한 CSV에만 사용해야 `시트행` 번호가 맞습니다. `--defer-sheet-checks`는 디모데 입력 후 별도 방식으로 성공 행을 체크할 운영자가 있을 때만 사용하며 일반 실행에는 권장하지 않습니다.

## 결과 상태

| 상태 | 의미 |
|---|---|
| `드라이런확인` | 교인을 찾았지만 저장하지 않음 |
| `입력완료` | 신규 수료내역 저장 성공 |
| `이미입력됨` | 동일 과정이 있어 중복 저장하지 않음 |
| `정확한교인없음` | 전화번호 또는 이름·군·팀으로 확정하지 못함 |
| `교인복수일치` | 같은 조건의 사람이 복수라 안전하게 중단 |
| `교육과정매핑없음` | 허용되지 않았거나 제외된 과정 |

## 재실행과 중복 방지

- 체크된 행은 처음부터 건너뜁니다.
- 디모데 저장 후 시트 체크 전에 프로그램이 중단돼도 재실행 시 상세 화면의 동일 교육과정을 확인해 중복 입력하지 않습니다.
- 실패한 사람은 체크하지 않으므로 시트 정보를 수정한 뒤 다시 실행할 수 있습니다.
- 결과 CSV는 매 실행마다 같은 파일명으로 갱신되므로 보관이 필요하면 실행 후 복사합니다.

## 문제 해결

### 시트 요청이 `401 Unauthorized`

`GOOGLE_COOKIES`가 만료된 것입니다. `credentials.json`을 준비해 OAuth로 실행합니다.

### 검색 결과가 있는데 `정확한교인없음`

- 전화번호가 있으면 시트와 디모데의 이름·전화번호를 확인합니다.
- 번호가 없으면 이름과 정규화한 군이 같고, 교인 구분이 A/B이며, 그 조건의 결과가 한 명이어야 합니다.
- 팀 이름의 오탈자나 현재 디모데 소속 변경 여부를 확인한 뒤 다시 실행합니다.

### 동일 과정이 이미 있음

정상입니다. 추가 저장하지 않고 `이미입력됨`으로 처리하며 시트만 체크합니다.

### 디모데 화면 변경으로 선택자를 찾지 못함

실제 실행을 중단하고 드라이런부터 다시 확인합니다. `completion_automation.py`의 검색·상세 창 선택자를 새 화면 구조에 맞게 수정해야 합니다.

## 2026-08-11 실제 실행 검증
- 대상 206행
- 입력 또는 기존 등록 확인 후 체크: 174행
- 사용자 요청에 따라 제외하고 미입력: 31행
- 전화번호 및 이름·군·A/B 재검색 후에도 교인을 확정하지 못해 미입력: 1행
- 수료 상태: `수료`
- 수료일: `20260621`
- 수료연도: `2026`

미입력 1행은 `이현우(성경대학)`입니다. 시트의 `입력여부`를 체크하지 않았으므로 정보 보완 후 재실행 대상입니다. 윤진은 시트의 군을 `영군`에서 `임군`으로 정정한 뒤 입력을 완료했습니다.

## AI Agent Context

이 저장소는 작업별 AI 컨텍스트 관리를 위해 Akela를 사용합니다. Akela는 자동입력 Runtime Dependency가 아닙니다.

- Knowledge: `knowledge/`
- Agent Protocol: `akela/PROTOCOL.md`
- Configuration: `akela.json`

Codex와 Claude Code는 Task slice를 compile하고 드라이런·실행 규칙에 따라 작업한 뒤 Evidence와 outcome을 기록합니다. `akela stats`와 `akela/CURATE.md`는 사람이 Knowledge 승격·수정·폐기를 검토하는 데 사용합니다.
