SHEET_URL = "https://docs.google.com/spreadsheets/d/여기에_시트_ID/edit?gid=시트_gid"
SHEET_TAB_NAME = "통합 명단"
GOOGLE_COOKIES = "구글 시트 CSV 다운로드에 사용하는 Cookie 값"

DIMODE_URL = "https://hansungv6.dimode.co.kr/WebYouth/Default.aspx"
USER_ID = "디모데 아이디"
USER_PW = "디모데 비밀번호"

# Google Cloud에서 만든 Desktop OAuth 클라이언트 JSON 파일.
GOOGLE_OAUTH_CLIENT_FILE = "credentials.json"
GOOGLE_OAUTH_TOKEN_FILE = "token.json"

# 디모데에서 실제 존재하는 '청년-' 과정만 추가한다.
# 기본 제공: LTC, 확신반, 성장반, 성경대학, 교리대학
EDU_COURSE_MAP = {
    # 기초반/예배학교/결혼예비학교는 사용자 요청 전까지 입력 대상에서 제외됩니다.
}

LOG_FILE = "result_log.txt"
SEARCH_DELAY = 0.8
SAVE_DELAY = 1.0
