"""REN-003 한 명령 [초안 · 미실행 — KiCad 작업 완료 알림 뒤 (D-003 #53)]: Fusion 재질·로컬 렌더.
전제: mechanical/m010/run_case.py 를 그 pcb 커밋으로 먼저 돌림 → pcbsrc/<보드>(3D 모델 연결 사본) · M007_assembly 문서가 Fusion 에 있음.
  python -I -B mechanical/ren003/run_ren003.py [--docs <폴더>]
순서: ① 렌더용 보드 STEP (층 포함) ② M007 문서 활성 ③ 01 보드 가져오기 ④ 02 재질 ⑤ 03 로컬 렌더 6장 ⑥ 확인·manifest·대표본
산출: main 체크아웃 validation/runtime/vd001/render/fusion/ (O-100). 종료 코드 = 막힌 단계 + 불합격 수."""
import argparse, hashlib, json, os, shutil, struct, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
MAIN = r'C:\workspace_python\OpenHW'
V = os.path.join(MAIN, 'validation', 'runtime', 'vd001')
F = os.path.join(V, 'render', 'fusion')
PY = [sys.executable, '-I', '-B']
FRUN = PY + [os.path.join(LANE, 'mechanical', 'fusion_run.py')]
KICAD = os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe')
VIEWS = ['front', 'back', 'threequarter', 'exploded', 'window', 'connectors']
CHECK = {'front': '재질: 외함 무광 흑 · 창 투명 · 렌즈', 'back': '방열판 아노다이즈 반광 · 외함과 구분', 'threequarter': '전체 재질 체계',
         'exploded': '보드 녹색 마스크 · ENIG 패드 · 실크 흰색 · IC 흑색 · 커넥터 금속/플라스틱', 'window': '창 너머 보드·LED 보임',
         'connectors': 'RJ45·DC·USB-C 금속/플라스틱'}


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('[%s] rc %d' % (os.path.basename(cmd[-1] if cmd[-1].endswith('.py') else cmd[0]), r.returncode), (r.stdout + r.stderr).strip()[-400:], flush=True)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--docs', default=os.path.join(LANE, 'docs', 'renders', 'fusion'))
    a = ap.parse_args()
    os.makedirs(os.path.join(F, 'boards'), exist_ok=True)
    bad = 0
    for b in ('carrier', 'front'):     # ① 층(트랙·패드·면·실크·마스크) 포함 — 판정용 boards/*.step 과 따로
        bad += sh([KICAD, 'pcb', 'export', 'step', '--subst-models', '--user-origin', '100x100mm', '--include-tracks', '--include-pads',
                   '--include-zones', '--include-silkscreen', '--include-soldermask', '-f', '-o', os.path.join(F, 'boards', '%s_render.step' % b),
                   os.path.join(V, 'pcbsrc', b, 'hardware', 'schematic', b, b + '.kicad_pcb')]) != 0
    if bad:
        return bad
    for s, extra in (('m010/scripts/00_activate.py', ['--set', 'DOC=M007_assembly']), ('ren003/scripts/01_render_boards.py', []),
                     ('ren003/scripts/02_appearance.py', []), ('ren003/scripts/03_render.py', [])):
        if sh(FRUN + [os.path.join(LANE, 'mechanical', *s.split('/'))] + extra):
            return 1
    # ⑥ 확인 (파일·해상도) · manifest (사람 확인 항목) · 대표본
    man_p = os.path.join(V, 'render', 'manifest.json')
    man = [m for m in (json.load(open(man_p, encoding='utf-8')) if os.path.exists(man_p) else []) if not m.get('path', '').startswith('validation/runtime/vd001/render/fusion/')]
    fails = []
    os.makedirs(a.docs, exist_ok=True)
    for v in VIEWS:
        p = os.path.join(F, 'ren003_%s.png' % v)
        ok = os.path.exists(p)
        wh = struct.unpack('>II', open(p, 'rb').read()[16:24]) if ok else (0, 0)
        if not ok or wh[0] < 2560 or wh[1] < 1440:
            fails.append('%s %s' % (v, wh)); continue
        sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        man.append({'kind': 'product-fusion', 'board': '-', 'title': 'Fusion 로컬 렌더 %s' % v, 'path': os.path.relpath(p, MAIN).replace('\\', '/'),
                    'sha256': sha, 'source': 'Fusion 로컬 렌더 (mechanical/ren003/scripts/03_render.py, 재질 materials.py)',
                    'input_sha256': None, 'verifiable': False, 'check': CHECK[v]})
        if os.path.getsize(p) < 20 * 1024 * 1024:
            shutil.copy2(p, os.path.join(a.docs, os.path.basename(p)))
        else:
            fails.append('%s 20MB 이상' % v)
    json.dump(man, open(man_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('FUSION RENDER', len(VIEWS) - len(fails), '/', len(VIEWS), 'fails', fails)
    return len(fails)


if __name__ == '__main__':
    sys.exit(main())
