"""REN-003b 1) 메시 준비 (시스템 파이썬, Fusion · Blender 없이) — 보드 GLB 와 외함 STL 을 한 폴더에 만든다.

  python -I -B mechanical/ren003b/prep.py [--pcb <커밋>] [--enclosure <STEP/STL 폴더>] [--extra <STL 폴더>] [--out <메시 폴더>]
        [--boards-from <GLB 폴더>] [--deflection 0.01]

- 보드: `git archive <커밋>` 사본 → REN-002 `apply_models.py`(사본에만 적용, 3D 모델 연결) → `kicad-cli pcb export glb`
  (--subst-models, --user-origin 100x100mm = 코어 중심, 트랙 · 패드 · 면 · 실크 · 마스크 포함) → board_carrier.glb · board_front.glb
  `--boards-from` 을 주면 내보내지 않고 그 폴더의 GLB 를 복사한다.
- 외함: `--enclosure` 폴더의 *.step 을 gmsh(OpenCASCADE 삼각화, 곡면 오차 ≤ --deflection mm)로 이진 STL(mm)로 바꾼다. *.stl 은 그대로 복사한다.
  같은 이름의 STEP 과 STL 이 있으면 STEP 을 쓴다. → M-010 최종 STEP/STL 이 나오면 이 인자만 바꿔 다시 돌린다.
- 출력: <out>/board_<보드>.glb · <이름>.stl · index.json (파일 · 원본 · sha256 · 삼각형 수 · bbox mm)
- 기본 출력: main 체크아웃 validation/runtime/vd001/render/blender-b/mesh (O-100)
- 도구 경로: KiCad = 환경 변수 KICAD_BIN(폴더) 또는 %LOCALAPPDATA%/Programs/KiCad/10.0/bin
종료 코드 = 실패한 단계 수."""
import argparse
import glob
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(
    ['git', '-C', HERE, 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))
KICAD = os.path.join(os.environ.get('KICAD_BIN') or os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin'), 'kicad-cli.exe')
BOARDS = ('carrier', 'front')
DEFLECTION = 0.01   # mm — STEP 삼각화 곡면 오차 (--deflection)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def export_boards(commit, out, work):
    """커밋 사본에서 보드 GLB 를 만든다. 반환: (실패 수, 기록 목록)"""
    src = os.path.join(work, 'pcbsrc')
    shutil.rmtree(src, ignore_errors=True)
    os.makedirs(src)
    r = subprocess.run(['git', '-C', LANE, '-c', 'core.autocrlf=false', 'archive', commit, 'hardware', 'mechanical/models', 'mechanical/ren002'],
                       capture_output=True)
    if r.returncode:
        print('git archive 실패', r.stderr.decode('utf-8', 'replace')[-300:])
        return 1, []
    tarfile.open(fileobj=io.BytesIO(r.stdout)).extractall(src)
    bad, rec = 0, []
    for b in BOARDS:
        pcb = os.path.join(src, 'hardware', 'schematic', b, b + '.kicad_pcb')
        a = subprocess.run([sys.executable, '-I', '-B', os.path.join(src, 'mechanical', 'ren002', 'apply_models.py'), pcb],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        glb = os.path.join(out, 'board_%s.glb' % b)
        k = subprocess.run([KICAD, 'pcb', 'export', 'glb', '--user-origin', '100x100mm', '--subst-models', '--include-tracks', '--include-pads',
                            '--include-zones', '--include-silkscreen', '--include-soldermask', '-f', '-o', glb, pcb],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        ok = k.returncode == 0 and os.path.exists(glb)
        warn = [ln for ln in (k.stdout + k.stderr).splitlines() if 'model' in ln.lower() and ('not' in ln.lower() or '없' in ln)]
        print('보드 %s: apply_models rc %d (%s) · GLB rc %d · 모델 경고 %d' % (b, a.returncode, a.stdout.strip()[-60:], k.returncode, len(warn)))
        bad += not ok
        if ok:
            rec.append({'file': os.path.basename(glb), 'kind': 'board', 'board': b, 'source': 'git %s hardware/schematic/%s/%s.kicad_pcb' % (commit, b, b),
                        'source_sha256': sha(pcb), 'sha256': sha(glb), 'model_warnings': warn[:20]})
    return bad, rec


def step_to_stl(path, out):
    """STEP → 이진 STL (mm). 반환: (삼각형 수, bbox)"""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.model.occ.importShapes(path)
        gmsh.model.occ.synchronize()
        bb = [round(v, 3) for v in gmsh.model.getBoundingBox(-1, -1)]
        gmsh.option.setNumber('Mesh.Binary', 1)
        # CAD 곡면 삼각화(OpenCASCADE): 곡면 오차(선형 편차) DEFLECTION mm 이하, 각 편차 0.1 rad — O-125 「≤ 0.01 mm」
        gmsh.option.setNumber('Mesh.StlLinearDeflection', DEFLECTION)
        gmsh.option.setNumber('Mesh.StlLinearDeflectionRelative', 0)
        gmsh.option.setNumber('Mesh.StlAngularDeflection', 0.1)
        gmsh.model.mesh.importStl()
        n = sum(len(t) for t in gmsh.model.mesh.getElements(2)[1])
        if n == 0:      # 삼각화 표현이 없으면 격자 생성으로
            gmsh.option.setNumber('Mesh.MeshSizeMin', 0.05)
            gmsh.option.setNumber('Mesh.MeshSizeMax', 4.0)
            gmsh.option.setNumber('Mesh.MeshSizeFromCurvature', 96)
            gmsh.model.mesh.generate(2)
            n = sum(len(t) for t in gmsh.model.mesh.getElements(2)[1])
        gmsh.write(out)
        return n, bb
    finally:
        gmsh.finalize()


def stl_info(path):
    import struct
    d = open(path, 'rb').read()
    if d[:5] == b'solid' and b'facet' in d[:400]:
        return d.count(b'facet normal'), None
    return struct.unpack('<I', d[80:84])[0], None


def main():
    global DEFLECTION
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcb', default='995b872', help='보드 커밋 (캐리어 · 전면 같은 커밋)')
    ap.add_argument('--enclosure', default=os.path.join(LANE, 'mechanical', 'm003', 'out', 'step'), help='외함 STEP/STL 폴더')
    ap.add_argument('--out', default=os.path.join(MAIN, 'validation', 'runtime', 'vd001', 'render', 'blender-b', 'mesh'))
    ap.add_argument('--boards-from', default=None, help='이미 만든 board_*.glb 폴더 (내보내기 건너뜀)')
    ap.add_argument('--extra', default=None, help='덧붙일 STL 폴더 — --enclosure 에 없는 이름만 복사 (렌즈 · 나사 · 하니스 등)')
    ap.add_argument('--deflection', type=float, default=DEFLECTION, help='STEP 삼각화 곡면 오차 mm')
    ap.add_argument('--extra-only', default=None, help='--extra 에서 이 이름 앞부분(쉼표)으로 시작하는 STL 만')
    ap.add_argument('--stl-only', action='store_true', help='외함 폴더의 STEP 은 쓰지 않는다(부품별 STL 과 통짜 STEP 이 같이 있는 시안 폴더)')
    a = ap.parse_args()
    DEFLECTION = a.deflection
    os.makedirs(a.out, exist_ok=True)
    for f in glob.glob(os.path.join(a.out, '*.stl')) + glob.glob(os.path.join(a.out, '*.glb')):
        os.remove(f)
    bad, index = 0, []
    if a.boards_from:
        for b in BOARDS:
            s = os.path.join(a.boards_from, 'board_%s.glb' % b)
            if os.path.exists(s):
                shutil.copy2(s, a.out)
                index.append({'file': 'board_%s.glb' % b, 'kind': 'board', 'board': b, 'source': '(복사한 GLB)', 'sha256': sha(s)})
            else:
                print('GLB 없음', b)
                bad += 1
    else:
        nb, rec = export_boards(a.pcb, a.out, os.path.join(os.path.dirname(a.out), 'work'))
        bad += nb
        index += rec
    names = {}
    for p in sorted(glob.glob(os.path.join(a.enclosure, '*.stl')) + ([] if a.stl_only else glob.glob(os.path.join(a.enclosure, '*.step')) + glob.glob(os.path.join(a.enclosure, '*.stp')))):
        names[os.path.splitext(os.path.basename(p))[0]] = p     # 같은 이름이면 뒤에 오는 STEP 이 이긴다
    if not names:
        print('외함 메시 없음:', a.enclosure)
        bad += 1
    import re
    for n in [n for n in names if re.search(r' \(\d+\)$', n)]:      # 내려받기 중복 이름 「이름 (1)」 은 쓰지 않는다
        print('건너뜀(중복 이름):', n)
        del names[n]
    if a.extra:
        only = tuple(a.extra_only.split(',')) if a.extra_only else None
        for p in sorted(glob.glob(os.path.join(a.extra, '*.stl'))):
            n = os.path.splitext(os.path.basename(p))[0]
            if only is None or n.startswith(only):
                names.setdefault(n, p)
    for name, p in sorted(names.items()):
        o = os.path.join(a.out, name + '.stl')
        try:
            if p.lower().endswith('.stl'):
                shutil.copy2(p, o)
                n, bb = stl_info(o)
            else:
                n, bb = step_to_stl(p, o)
            index.append({'file': name + '.stl', 'kind': 'enclosure', 'source': os.path.basename(p), 'source_sha256': sha(p), 'sha256': sha(o),
                          'triangles': n, 'bbox_mm': bb, 'deflection_mm': None if p.lower().endswith('.stl') else DEFLECTION})
            print('외함 %s: 삼각형 %d' % (name, n))
        except Exception as e:      # 한 부품이 실패해도 나머지는 계속
            print('외함 %s 실패: %s' % (name, e))
            bad += 1
    json.dump({'pcb': None if a.boards_from else a.pcb, 'enclosure_dir': os.path.basename(os.path.normpath(a.enclosure)), 'items': index},
              open(os.path.join(a.out, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('PREP 보드 %d · 외함 %d · 실패 %d → %s' % (sum(1 for i in index if i['kind'] == 'board'), sum(1 for i in index if i['kind'] == 'enclosure'), bad,
                                               os.path.relpath(a.out, MAIN).replace('\\', '/') if os.path.abspath(a.out).lower().startswith(MAIN.lower()) else '(저장소 밖)'))
    return bad


if __name__ == '__main__':
    sys.exit(main())
