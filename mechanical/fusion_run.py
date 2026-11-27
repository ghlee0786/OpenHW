"""Fusion 스크립트 실행기 (M-010). Fusion 안에서는 __file__ 이 없어 스크립트가 자기 저장소 위치를 모른다 →
스크립트의 `LANE = r"..."` 줄을 그 스크립트가 든 체크아웃(레인 worktree 또는 main) 경로로 바꾼 사본을 fusion_cli 로 돌린다.
  python -I -B mechanical/fusion_run.py <스크립트.py> [--set 이름=값 ...] [--readonly]
- 스크립트 안의 기본값 LANE = main 체크아웃 (fusion_cli 로 직접 돌려도 main 기준으로 동작)
- 산출물(validation/runtime)은 스크립트의 MAIN(main 체크아웃) 아래 — O-100 (레인 worktree 안은 accept 때 지워짐)
- --set: `이름 = ...` 로 시작하는 줄을 `이름 = r"값"` 으로 바꿈 (예: --set OUT=C:\\...\\case)
종료 코드 = fusion_cli 종료 코드."""
import argparse, os, re, subprocess, sys, tempfile

FCLI = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'fusion360', 'scripts', 'fusion_cli.py')


def checkout_of(path):
    d = os.path.dirname(os.path.abspath(path))
    while not os.path.exists(os.path.join(d, '.git')):
        up = os.path.dirname(d)
        if up == d:
            raise SystemExit('저장소 밖: ' + path)
        d = up
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('--set', action='append', default=[])
    ap.add_argument('--readonly', action='store_true')
    a = ap.parse_args()
    src = open(a.script, encoding='utf-8').read()
    subs = [('LANE', checkout_of(a.script))] + [tuple(s.split('=', 1)) for s in a.set]
    for name, val in subs:
        src, n = re.subn(r'(?m)^%s = .*$' % re.escape(name), lambda m: '%s = r"%s"' % (name, val), src, count=1)
        if not n:
            raise SystemExit('%s: `%s = ` 줄 없음' % (a.script, name))
    tmp = os.path.join(tempfile.gettempdir(), 'openhw_fusion_' + os.path.basename(a.script))
    open(tmp, 'w', encoding='utf-8').write(src)
    cmd = [sys.executable, FCLI, 'run', tmp] + (['--readonly'] if a.readonly else [])
    return subprocess.run(cmd).returncode


if __name__ == '__main__':
    sys.exit(main())
