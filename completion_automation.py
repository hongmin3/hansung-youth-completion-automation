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


def load_sheet_rows():
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
    group_match = re.search(r"부서보기[^\n]*\n\s*([^\n]+)", text)
    name = re.sub(r"[A-Z]$", "", name_match.group(1) if name_match else "")
    path = (group_match.group(1) if group_match else "").split(">")
    return {
        "name": name,
        "phone": format_phone(phone_match.group(1) if phone_match else ""),
        "army": normalize_text(path[0]) if path else "",
        "team": normalize_text(path[1]) if len(path) > 1 else "",
    }


def identity_matches(candidate, row):
    return (
        candidate["name"] == normalize_text(row.get("이름") or row.get("성명"))
        and normalize_group(candidate["army"]) == normalize_group(row.get("군"))
        and normalize_team(candidate["team"]) == normalize_team(row.get("팀"))
    )


def search_person_cards(right_frame, *, name="", phone=""):
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
        if identity_matches(candidate, row) and candidate["phone"]:
            matched.append(candidate["phone"])
    unique = sorted(set(matched))
    return unique[0] if len(unique) == 1 else ""


def find_exact_person_card(right_frame, row):
    phone = format_phone(row.get("핸드폰") or row.get("전화번호") or row.get("연락처"))
    if not phone:
        return None, "전화번호없음"
    cards = search_person_cards(right_frame, phone=phone)
    matched = []
    for index in range(cards.count()):
        card = cards.nth(index)
        if identity_matches(parse_person_card(card.inner_text()), row):
            matched.append(card)
    if len(matched) != 1:
        return None, "정확한교인없음" if not matched else "교인복수일치"
    return matched[0], "일치"


def course_map():
    mapping = dict(DEFAULT_COURSE_MAP)
    mapping.update(getattr(config, "EDU_COURSE_MAP", {}))
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


def mark_sheet_complete(service, sheet_row):
    spreadsheet_id = spreadsheet_id_from_url(config.SHEET_URL)
    tab_name = getattr(config, "SHEET_TAB_NAME", "통합 명단")
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{tab_name}'!G{sheet_row}",
        valueInputOption="RAW",
        body={"values": [[True]]},
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
            if not phone:
                status = "전화번호없음"
            else:
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
                        mark_sheet_complete(sheets_service, row["_sheet_row"])
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
    return parser.parse_args()


def main():
    args = parse_args()
    options = Options(args.execute, args.limit, args.skip_phone_lookup)
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        raise SystemExit("python3 -m pip install -r requirements.txt 를 먼저 실행하세요.")

    sheets_service = get_sheets_service(required=options.execute) if options.execute else None
    rows = load_sheet_rows()
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
