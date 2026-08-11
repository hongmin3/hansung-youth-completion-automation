import argparse
import csv
import io
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

import config


PROJECT_DIR = Path(__file__).resolve().parent
PERSON_LIST_URL = "https://hansungv6.dimode.co.kr/WebYouth/Person/PersonList.aspx?mTag=MB2"
COMPLETE_DATE = "20260621"
COMPLETE_YEAR = "2026"
COMPLETE_STATUS = "수료"

# 실제 디모데 교육 목록에서 확인한 정확한 명칭만 기본 허용한다.
DEFAULT_COURSE_MAP = {
    "LTC": "청년-LTC",
    "확신반": "청년-확신반",
    "성장반": "청년-성장반",
    "성경대학": "청년-성경대학",
    "교리대학": "청년-교리대학",
}

# 사용자가 추후 별도로 요청하기 전까지 디모데에 입력하지 않는 과정입니다.
EXCLUDED_COURSES = {"기초반", "예배학교", "결혼예비학교"}


def log(message):
    print(message)
    log_file = Path(getattr(config, "LOG_FILE", PROJECT_DIR / "result_log.txt"))
    if not log_file.is_absolute():
        log_file = PROJECT_DIR / log_file
    with log_file.open("a", encoding="utf-8") as stream:
        stream.write(message + "\n")


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_group(value):
    return re.sub(r"\([^)]*\)", "", normalize_text(value)).strip()


def normalize_team(value):
    value = normalize_text(value).replace("❤", "").replace("❤️", "")
    return value[:-1] if value.endswith("팀") else value


def format_phone(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return ""


def is_checked(value):
    return normalize_text(value).upper() in {"TRUE", "Y", "YES", "완료", "입력완료", "✓", "✔"}


def spreadsheet_id_from_url(url):
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url or "")
    if not match:
        raise ValueError("SHEET_URL에서 스프레드시트 ID를 찾을 수 없습니다.")
    return match.group(1)


def gid_from_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "gid" in query:
        return query["gid"][0]
    fragment = parse_qs(parsed.fragment)
    return fragment.get("gid", ["0"])[0]


def rows_from_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        rows = []
        for sheet_row, row in enumerate(reader, start=2):
            row["_sheet_row"] = sheet_row
            rows.append(row)
        return rows


def load_sheet_rows(sheets_service=None, csv_path=None):
    if csv_path:
        return rows_from_csv(csv_path)
    if sheets_service is not None:
        spreadsheet_id = spreadsheet_id_from_url(config.SHEET_URL)
        tab_name = getattr(config, "SHEET_TAB_NAME", "통합 명단")
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{tab_name}'!A:G",
        ).execute()
        values = result.get("values", [])
        if not values:
            return []
        headers = values[0]
        rows = []
        for sheet_row, values_row in enumerate(values[1:], start=2):
            padded = values_row + [""] * (len(headers) - len(values_row))
            row = dict(zip(headers, padded))
            row["_sheet_row"] = sheet_row
            rows.append(row)
        return rows

    sheet_url = config.SHEET_URL
    base_url = sheet_url.split("/edit")[0]
    csv_url = f"{base_url}/export?format=csv&gid={gid_from_url(sheet_url)}"
    response = requests.get(
        csv_url,
        headers={
            "Cookie": config.GOOGLE_COOKIES,
            "User-Agent": "Mozilla/5.0 Chrome/120 Safari/537.36",
        },
        timeout=30,
    )
    if response.status_code == 401:
        raise RuntimeError(
            "Google 시트 쿠키가 만료되었습니다. credentials.json을 설정해 OAuth로 연결하세요."
        )
    response.raise_for_status()
    reader = csv.DictReader(io.StringIO(response.content.decode("utf-8-sig")))
    rows = []
    for sheet_row, row in enumerate(reader, start=2):
        row["_sheet_row"] = sheet_row
        rows.append(row)
    return rows


def parse_person_card(text):
    name_match = re.search(r"이름\s*([^\s(]+)\s*\(", text)
    phone_match = re.search(r"핸드폰\s*([0-9\- ]{10,15})", text)
    group_match = re.search(r"([^\s>(]+군)(?:\([^)]*\))?\s*>\s*([^>\n]+)", text)
    activity_match = re.search(r"교인\s*>\s*청년\s*\(([A-Z])\)", text)
    name = re.sub(r"[A-Z]$", "", name_match.group(1) if name_match else "")
    return {
        "name": name,
        "phone": format_phone(phone_match.group(1) if phone_match else ""),
        "army": normalize_text(group_match.group(1)) if group_match else "",
        "team": normalize_text(group_match.group(2)) if group_match else "",
        "activity": activity_match.group(1) if activity_match else "",
    }


def identity_matches(candidate, row):
    return (
        candidate["name"] == normalize_text(row.get("이름") or row.get("성명"))
        and normalize_group(candidate["army"]) == normalize_group(row.get("군"))
        and normalize_team(candidate["team"]) == normalize_team(row.get("팀"))
    )


def same_name_and_group(candidate, row):
    return (
        candidate["name"] == normalize_text(row.get("이름") or row.get("성명"))
        and normalize_group(candidate["army"]) == normalize_group(row.get("군"))
    )


def same_active_name_and_group(candidate, row):
    return same_name_and_group(candidate, row) and candidate.get("activity") in {"A", "B"}


def reset_person_search(right_frame):
    """이전 사람의 검색 조건이 다음 검색에 남지 않도록 검색 폼을 초기화한다."""
    right_frame.locator(
        "#ctl00_cph1_PersonListYouth1_tabConSch_tabPnSch0_txtNameSch0"
    ).fill("")
    right_frame.locator(
        "#ctl00_cph1_PersonListYouth1_tabConSch_tabPnSch0_txtHandphoneSch0"
    ).fill("")


def search_person_cards(right_frame, *, name="", phone=""):
    reset_person_search(right_frame)
    if name:
        field = right_frame.locator("#ctl00_cph1_PersonListYouth1_tabConSch_tabPnSch0_txtNameSch0")
    else:
        field = right_frame.locator("#ctl00_cph1_PersonListYouth1_tabConSch_tabPnSch0_txtHandphoneSch0")
    field.fill(name or phone)
    right_frame.locator("#ctl00_cph1_PersonListYouth1_tabConSch_tabPnSch0_imgSearch0").click()
    time.sleep(getattr(config, "SEARCH_DELAY", 0.8))
    return right_frame.locator("table.tablelineno")


def enrich_phone(right_frame, row):
    cards = search_person_cards(right_frame, name=normalize_text(row.get("이름")))
    matched = []
    for index in range(cards.count()):
        card = cards.nth(index)
        candidate = parse_person_card(card.inner_text())
        if same_active_name_and_group(candidate, row) and candidate["phone"]:
            matched.append(candidate["phone"])
    unique = sorted(set(matched))
    return unique[0] if len(unique) == 1 else ""


def find_exact_person_card(right_frame, row):
    phone = format_phone(row.get("핸드폰") or row.get("전화번호") or row.get("연락처"))
    expected_name = normalize_text(row.get("이름") or row.get("성명"))
    if phone:
        cards = search_person_cards(right_frame, phone=phone)
        phone_matched = []
        for index in range(cards.count()):
            card = cards.nth(index)
            candidate = parse_person_card(card.inner_text())
            if candidate["name"] == expected_name and candidate["phone"] == phone:
                phone_matched.append(card)
        if len(phone_matched) == 1:
            return phone_matched[0], "전화번호일치"
        if len(phone_matched) > 1:
            return None, "교인복수일치"

    cards = search_person_cards(right_frame, name=expected_name)
    matched = []
    for index in range(cards.count()):
        card = cards.nth(index)
        candidate = parse_person_card(card.inner_text())
        if same_active_name_and_group(candidate, row):
            matched.append((card, candidate))
    if len(matched) == 1:
        card, candidate = matched[0]
        if candidate["phone"]:
            row["핸드폰"] = candidate["phone"]
        return card, "이름군일치"
    if len(matched) > 1:
        return None, "교인복수일치"
    return None, "정확한교인없음"


def course_map():
    mapping = dict(DEFAULT_COURSE_MAP)
    mapping.update(getattr(config, "EDU_COURSE_MAP", {}))
    for category in EXCLUDED_COURSES:
        mapping.pop(category, None)
    return mapping


def oauth_paths():
    client_file = Path(getattr(config, "GOOGLE_OAUTH_CLIENT_FILE", PROJECT_DIR / "credentials.json"))
    token_file = Path(getattr(config, "GOOGLE_OAUTH_TOKEN_FILE", PROJECT_DIR / "token.json"))
    if not client_file.is_absolute():
        client_file = PROJECT_DIR / client_file
    if not token_file.is_absolute():
        token_file = PROJECT_DIR / token_file
    return client_file, token_file


def get_sheets_service(required=False):
    client_file, token_file = oauth_paths()
    if not client_file.exists():
        if required:
            raise RuntimeError(f"Google OAuth 파일이 없습니다: {client_file}")
        return None
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ModuleNotFoundError as exc:
        raise RuntimeError("requirements.txt의 Google API 패키지를 설치하세요.") from exc

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = None
    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(str(token_file), scopes)
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_file), scopes)
        credentials = flow.run_local_server(port=0)
    token_file.write_text(credentials.to_json(), encoding="utf-8")
    return build("sheets", "v4", credentials=credentials)


def update_sheet_result(service, row):
    spreadsheet_id = spreadsheet_id_from_url(config.SHEET_URL)
    tab_name = getattr(config, "SHEET_TAB_NAME", "통합 명단")
    sheet_row = row["_sheet_row"]
    data = []
    phone = format_phone(row.get("핸드폰"))
    if phone:
        data.append({"range": f"'{tab_name}'!E{sheet_row}", "values": [[phone]]})
    data.append({"range": f"'{tab_name}'!G{sheet_row}", "values": [[True]]})
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"valueInputOption": "RAW", "data": data},
    ).execute()


def save_plan(rows, filename="dry_run_plan.csv"):
    output_dir = PROJECT_DIR / "output"
    output_dir.mkdir(exist_ok=True)
    path = output_dir / filename
    fields = ["시트행", "구분", "군", "팀", "이름", "핸드폰", "담당자", "교육과정", "상태"]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


@dataclass
class Options:
    execute: bool
    limit: int | None
    skip_phone_lookup: bool
    defer_sheet_checks: bool = False


def process(page, right_frame, rows, options, sheets_service):
    mapping = course_map()
    plan = []
    processed = 0
    for row in rows:
        if options.limit is not None and processed >= options.limit:
            break
        if is_checked(row.get("입력여부")):
            continue
        course = normalize_text(row.get("구분"))
        education = mapping.get(course)
        status = "대기"
        if not education or not education.startswith("청년-"):
            status = "교육과정매핑없음"
        else:
            phone = format_phone(row.get("핸드폰") or row.get("전화번호") or row.get("연락처"))
            if not phone and not options.skip_phone_lookup:
                phone = enrich_phone(right_frame, row)
                if phone:
                    row["핸드폰"] = phone
            card, match_status = find_exact_person_card(right_frame, row)
            if card is None:
                status = match_status
            elif not options.execute:
                status = "드라이런확인"
            else:
                name = normalize_text(row.get("이름") or row.get("성명"))
                with page.expect_popup() as popup_info:
                    card.get_by_text(name, exact=False).first.click()
                popup = popup_info.value
                popup.wait_for_load_state("domcontentloaded")
                try:
                    if popup.get_by_role("cell", name=education, exact=True).count() > 0:
                        status = "이미입력됨"
                    else:
                        popup.locator('input[name="ctl00$cph1$PersonModifyYouth1$EduList1$imgAdd"]').click()
                        popup.locator('input[name="ctl00$cph1$PersonModifyYouth1$EduList1$txtEdu"]').click()
                        popup.get_by_role("menuitem", name=education, exact=True).click()
                        popup.locator('select[name="ctl00$cph1$PersonModifyYouth1$EduList1$ucOkNOk$ddlData"]').select_option(COMPLETE_STATUS)
                        popup.locator('input[name="ctl00$cph1$PersonModifyYouth1$EduList1$ucEdEday$txtDate"]').fill(COMPLETE_DATE)
                        popup.locator('select[name="ctl00$cph1$PersonModifyYouth1$EduList1$ucYearEdID$ddlYear"]').select_option(COMPLETE_YEAR)
                        popup.locator('input[name="ctl00$cph1$PersonModifyYouth1$EduList1$txtEdTeacher"]').fill(normalize_text(row.get("담당자")))
                        popup.get_by_role("button", name="저장", exact=True).click()
                        time.sleep(getattr(config, "SAVE_DELAY", 1.0))
                        status = "입력완료"
                    if sheets_service is not None:
                        update_sheet_result(sheets_service, row)
                finally:
                    popup.close()
        plan.append({
            "시트행": row["_sheet_row"], "구분": course, "군": row.get("군", ""),
            "팀": row.get("팀", ""), "이름": row.get("이름", ""),
            "핸드폰": row.get("핸드폰", ""), "담당자": row.get("담당자", ""),
            "교육과정": education or "", "상태": status,
        })
        log(f"[{row.get('이름')}] {education or course}: {status}")
        processed += 1
    return plan


def parse_args():
    parser = argparse.ArgumentParser(description="청년 양육 수료 내역 디모데 자동입력")
    parser.add_argument("--execute", action="store_true", help="검증된 내역을 실제 저장")
    parser.add_argument("--limit", type=int, help="처리할 최대 인원 수")
    parser.add_argument("--skip-phone-lookup", action="store_true", help="빈 전화번호 자동 조회 생략")
    parser.add_argument("--sheet-csv", help="Google Sheets 대신 읽을 CSV 파일 경로")
    parser.add_argument(
        "--defer-sheet-checks",
        action="store_true",
        help="OAuth가 없을 때 입력 성공 행 체크를 외부 작업으로 미룸",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    options = Options(args.execute, args.limit, args.skip_phone_lookup, args.defer_sheet_checks)
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        raise SystemExit("python3 -m pip install -r requirements.txt 를 먼저 실행하세요.")

    sheets_service = get_sheets_service(required=options.execute and not options.defer_sheet_checks)
    rows = load_sheet_rows(sheets_service, args.sheet_csv)
    log(f"모드: {'실제입력' if options.execute else '드라이런'}, 대상 행: {len(rows)}")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(config.DIMODE_URL)
        page.get_by_role("textbox", name="username").fill(config.USER_ID)
        page.get_by_role("textbox", name="password").fill(config.USER_PW)
        page.get_by_role("textbox", name="password").press("Enter")
        page.wait_for_load_state("networkidle")
        right_page = page.frame(name="right")
        right_page.goto(PERSON_LIST_URL)
        right_page.wait_for_load_state("domcontentloaded")
        right_frame = page.frame_locator('frame[name="right"]')
        plan = process(page, right_frame, rows, options, sheets_service)
        browser.close()
    output = save_plan(plan, "execution_result.csv" if options.execute else "dry_run_plan.csv")
    log(f"결과 저장: {output}")
