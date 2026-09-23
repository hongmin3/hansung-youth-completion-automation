"""저장소 위생 회귀 검사.

Validates: NFR-SEC-001, NFR-DATA-001

이 두 요구사항의 '측정'은 사람이 눈으로 볼 필요가 없다 — 추적 파일 목록과 `.gitignore`,
그리고 시트 쓰기 대상 열은 전부 기계가 확인할 수 있다. 자격 증명도 network도 쓰지 않으므로
언제든 돌릴 수 있다.

이 검사가 막는 것은 "실수로 커밋"이다. 그 실수는 한 번 일어나면 git 이력에 남아 되돌리기
어렵고, 이 자동화가 다루는 값은 실명·연락처·소속이다.
"""

import ast
import pathlib
import re
import subprocess
import unittest

PROJECT = pathlib.Path(__file__).resolve().parents[1]


def tracked_files():
    """git이 추적 중인 파일. 추적되지 않는 로컬 파일은 이 요구사항의 대상이 아니다."""
    out = subprocess.run(["git", "-C", str(PROJECT), "ls-files", "-z"],
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p]


class GitignoreCoverage(unittest.TestCase):
    """NFR-SEC-001 / NFR-DATA-001: 자격 증명과 개인정보 산출물이 추적 대상이 아니어야 한다."""

    # SPEC의 '측정'이 이름을 대는 경로들. 문구를 바꾸면 이 목록도 함께 바꾼다.
    MUST_IGNORE = [
        "config.py",            # 디모데 계정·시트 URL
        "credentials.json",     # Sheets OAuth 클라이언트
        "token.json",           # Sheets OAuth 토큰
        "output/",              # 결과 CSV (실명·연락처)
        "user_data/",           # 브라우저 프로필 (로그인 세션)
        "result_log.txt",       # 실행 로그
        "debug_*.html",         # 디버그 산출물 (개인 화면 캡처)
        "debug_*.png",
    ]

    def setUp(self):
        self.patterns = [line.strip() for line in
                         (PROJECT / ".gitignore").read_text(encoding="utf-8").splitlines()
                         if line.strip() and not line.startswith("#")]

    def test_every_sensitive_path_is_ignored(self):
        for pattern in self.MUST_IGNORE:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, self.patterns,
                              f".gitignore에 {pattern}이 없다 — SPEC NFR-SEC-001의 측정 항목이다")

    def test_git_actually_ignores_them(self):
        """`.gitignore`에 적혀 있다와 git이 실제로 무시한다는 다른 진술이다.

        상위 규칙이나 negation(`!`)이 뒤에서 덮을 수 있으므로 git 자신에게 묻는다.
        """
        probes = ["config.py", "credentials.json", "token.json", "result_log.txt",
                  "output/dry_run_plan.csv", "user_data/Default/Cookies",
                  "debug_홍길동.html", "debug_홍길동.png"]
        # core.quotepath: git은 기본값으로 비ASCII 경로를 "debug_\355\231\215..." 처럼
        # 따옴표로 감싸 8진 이스케이프해 내보낸다. 한글 파일명이 바로 그 경우라, 그대로
        # 비교하면 무시되고 있는데도 아니라고 나온다. (-z 는 --stdin 과만 쓸 수 있어
        # 여기서는 쓸 수 없다: "fatal: -z only makes sense with --stdin".)
        result = subprocess.run(["git", "-C", str(PROJECT), "-c", "core.quotepath=false",
                                 "check-ignore", "--no-index", *probes],
                                capture_output=True, text=True)
        ignored = {line for line in result.stdout.splitlines() if line}
        missing = [p for p in probes if p not in ignored]
        self.assertEqual(missing, [], f"git이 무시하지 않는 민감 경로: {missing}")

    def test_no_sensitive_file_is_tracked(self):
        """지금 추적 중인 파일에 민감 산출물이 없어야 한다 (규칙보다 현재 상태가 우선)."""
        forbidden = re.compile(
            r"(^|/)(config\.py|credentials\.json|token\.json|result_log\.txt)$"
            r"|^(output|user_data)/"
            r"|(^|/)debug_[^/]*\.(html|png)$")
        offenders = [p for p in tracked_files() if forbidden.search(p)]
        self.assertEqual(offenders, [], f"민감 파일이 추적되고 있다: {offenders}")

    def test_example_config_holds_no_real_values(self):
        """NFR-SEC-001: `config.example.py`에는 자리표시자만 둔다."""
        text = (PROJECT / "config.example.py").read_text(encoding="utf-8")
        # 실제 시트 URL과 이메일 주소는 자리표시자가 아니다.
        self.assertNotRegex(text, r"docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]{20,}",
                            "config.example.py에 실제 스프레드시트 ID가 들어 있다")
        self.assertNotRegex(text, r"[A-Za-z0-9._%+-]+@(?!example\.)[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                            "config.example.py에 실제로 보이는 이메일 주소가 있다")


class SheetWriteScope(unittest.TestCase):
    """NFR-DATA-001: 시트 쓰기는 E열(핸드폰)과 G열(입력여부) 두 칸으로 제한한다."""

    def test_update_sheet_result_writes_only_columns_e_and_g(self):
        """소스를 파싱해 `update_sheet_result`가 만드는 range 리터럴을 모두 본다.

        실제 Sheets API를 부르지 않는다 — 자격 증명이 필요하고, 확인하려는 것은
        네트워크 동작이 아니라 이 함수가 어느 열을 대상으로 삼는가이다.
        """
        source = (PROJECT / "completion_automation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        func = next((n for n in ast.walk(tree)
                     if isinstance(n, ast.FunctionDef) and n.name == "update_sheet_result"), None)
        self.assertIsNotNone(func, "update_sheet_result를 찾지 못했다")

        columns = set()
        for node in ast.walk(func):
            if isinstance(node, ast.JoinedStr):          # f"...!E{sheet_row}"
                rendered = "".join(part.value for part in node.values
                                   if isinstance(part, ast.Constant) and isinstance(part.value, str))
                columns.update(re.findall(r"!\s*([A-Z]+)", rendered))
        self.assertEqual(columns, {"E", "G"},
                         f"시트 쓰기 대상 열이 E, G가 아니다: {sorted(columns)}")

    def test_no_other_function_writes_to_the_sheet(self):
        """batchUpdate 호출이 update_sheet_result 안에만 있어야 한다 — 다른 경로가 생기면
        위 검사가 열 범위를 다 보지 못한다(검사 범위가 조용히 줄어든다)."""
        source = (PROJECT / "completion_automation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        writers = set()
        for func in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)):
            for node in ast.walk(func):
                if isinstance(node, ast.Attribute) and node.attr in {"batchUpdate", "update", "append"}:
                    parent = getattr(node.value, "func", None)
                    if isinstance(parent, ast.Attribute) and parent.attr == "values":
                        writers.add(func.name)
        self.assertEqual(writers, {"update_sheet_result"},
                         f"시트에 쓰는 함수가 하나가 아니다: {sorted(writers)}")


if __name__ == "__main__":
    unittest.main()
