#!/usr/bin/env node
// Runs `python -m unittest discover -s tests` with the first Python 3 that actually starts.
// botyard.json runs its verify command through the platform shell (sh on macOS, cmd.exe on
// Windows), so a literal `.venv/bin/python` never runs on Windows, and there `python3` can be
// the Microsoft Store alias, which on one PC hung for minutes instead of failing. Candidates, in
// order: the macOS/Linux venv, the Windows venv, then python3/python (python first on Windows).
// Each probe has a time limit so a hanging alias is skipped.
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';

const bare = process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python'];
const candidates = ['.venv/bin/python', '.venv/Scripts/python.exe', ...bare];
const works = (cmd) => {
  if (cmd.includes('/') && !existsSync(cmd)) return false;
  const r = spawnSync(cmd, ['-c', 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)'], { stdio: 'ignore', timeout: 20000 });
  return !r.error && r.status === 0;
};
const python = candidates.find(works);
if (!python) {
  console.error(`Python 3을 찾지 못했다 (확인한 순서: ${candidates.join(', ')})`);
  process.exit(2);
}
const r = spawnSync(python, ['-m', 'unittest', 'discover', '-s', 'tests'], { stdio: 'inherit' });
process.exit(r.error ? 2 : r.status ?? 1);
