"""REN-002 1) 3D 모델 전수 감사 — python -I -B mechanical/ren002/audit_models.py [--pcb <커밋>] [--src <hardware 가 든 폴더>]   (종료 코드 = 빠진 수)
두 보드의 모든 풋프린트에 대해 (model ...) 경로가 실제 파일로 풀리는지 본다. kicad-cli 는 모델 속성이 아예 없는 풋프린트는 경고하지 않으므로 직접 읽는다.
- ${KICAD10_3DMODEL_DIR} → KiCad 10 설치 share/kicad/3dmodels, ${KIPRJMOD} → 보드 폴더(저장소 루트 위 mechanical/models 는 이 레인 것으로)
- .wrl 경로는 같은 이름 .step 도 찾는다 (kicad-cli --subst-models 와 같음)
- 모델이 필요 없는 것: attr board_only 또는 exclude_from_bom(실장 부품 없음, 예: 전면 J2 리드 납땜 패드 — M-008 F5), 또는 라이브러리 MountingHole · TestPoint · Fiducial · NetTie · Symbol
출력: mechanical/ren002/model_audit.md (표), validation/runtime/vd001/ren002/model_audit.json"""
import argparse, io, json, os, re, subprocess, sys, tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
MAIN = r'C:\workspace_python\OpenHW'   # 산출물 validation/runtime 은 main 체크아웃 (O-100 — 레인 worktree 안은 accept 때 지워짐)
PCB_LANE = MAIN   # pcb 커밋은 같은 저장소(pcb 레인 브랜치) — 레인 worktree 가 없어져도 커밋으로 읽힘
OUT = os.path.join(MAIN, 'validation', 'runtime', 'vd001', 'ren002')
KDIR = os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\share\kicad\3dmodels')
NO_MODEL_LIBS = ('MountingHole', 'TestPoint', 'Fiducial', 'NetTie', 'Symbol')


def footprints(text):
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', text):
        s = m.start() + 1
        depth = 0
        for k in range(s, len(text)):
            c = text[k]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    yield m.group(1), text[s:k + 1]
                    break


def resolve(path, board_dir, src_root):
    p = path.replace('${KICAD10_3DMODEL_DIR}', KDIR).replace('${KICAD9_3DMODEL_DIR}', KDIR).replace('${KIPRJMOD}', board_dir)
    if '${' in p:
        return None, 'unset variable'
    p = os.path.normpath(p if os.path.isabs(p) else os.path.join(board_dir, p))
    rel = os.path.relpath(p, src_root)
    if not rel.startswith('..') and rel.replace('\\', '/').startswith('mechanical/'):
        p = os.path.join(LANE, rel)          # 저장소 루트 기준 mechanical/models → 이 레인
    cands = [p] + ([os.path.splitext(p)[0] + e for e in ('.step', '.stp')] if p.lower().endswith('.wrl') else [])
    for c in cands:
        if os.path.isfile(c):
            return c, 'ok'
    return None, 'file not found'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcb', default='HEAD')
    ap.add_argument('--src', default=None, help='hardware/ 가 든 폴더 (주면 --pcb 무시)')
    ap.add_argument('--out-json', default=os.path.join(OUT, 'model_audit.json'))
    ap.add_argument('--no-md', action='store_true', help='mechanical/ren002/model_audit.md (pcb 커밋 기준 표) 를 쓰지 않음')
    a = ap.parse_args()
    if a.src:
        src, commit = os.path.abspath(a.src), 'src:' + a.src
    else:
        commit = subprocess.run(['git', '-C', PCB_LANE, 'rev-parse', '--short', a.pcb], capture_output=True, text=True).stdout.strip()
        src = os.path.join(OUT, 'pcbsrc')
        data = subprocess.run(['git', '-C', PCB_LANE, 'archive', a.pcb, 'hardware'], capture_output=True).stdout
        os.makedirs(src, exist_ok=True)
        tarfile.open(fileobj=io.BytesIO(data)).extractall(src)
    rows = []
    for b in ('carrier', 'front'):
        bd = os.path.join(src, 'hardware', 'schematic', b)
        t = open(os.path.join(bd, b + '.kicad_pcb'), encoding='utf-8').read()
        for lib, blk in footprints(t):
            ref = re.search(r'\(property "Reference" "([^"]*)"', blk).group(1)
            val = (re.search(r'\(property "Value" "([^"]*)"', blk) or [None, ''])[1]
            attr = (re.search(r'\n\t\t\(attr ([^)]*)\)', blk) or [None, ''])[1]
            side = 'B' if re.search(r'\n\t\t\(layer "B\.Cu"\)', blk) else 'F'
            models = re.findall(r'\(model "([^"]+)"', blk)
            hidden = re.findall(r'\(model "[^"]+"\s*\(hide yes\)', blk)
            need = not ('board_only' in attr or 'exclude_from_bom' in attr or lib.split(':')[0] in NO_MODEL_LIBS)
            res = []
            for m in models:
                f, why = resolve(m, bd, src)
                res.append({'path': m, 'file': os.path.relpath(f, LANE).replace('\\', '/') if f and f.startswith(LANE) else f, 'status': why})
            ok = any(r['status'] == 'ok' for r in res) and not hidden
            state = 'ok' if ok else ('모델 불필요' if not need else ('경로 없음' if not models else ('숨김' if hidden else res[0]['status'])))
            rows.append({'board': b, 'ref': ref, 'value': val, 'footprint': lib, 'side': side, 'attr': attr, 'models': res, 'state': state,
                         'missing': need and not ok})
    miss = [r for r in rows if r['missing']]
    os.makedirs(OUT, exist_ok=True)
    json.dump({'pcb': commit, 'rows': rows}, open(a.out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    L = ['# REN-002 3D 모델 전수 감사 (audit_models.py — pcb %s, 빠짐 %d / 풋프린트 %d)' % (commit, len(miss), len(rows)), '',
         '- 풀림 규칙: `${KICAD10_3DMODEL_DIR}` = KiCad 10.0 설치 `share/kicad/3dmodels`, `${KIPRJMOD}` = 보드 폴더, .wrl → 같은 이름 .step.',
         '- 상태: ok · 경로 없음(풋프린트에 model 속성 없음) · file not found · unset variable · 숨김 · 모델 불필요(board_only, 구멍·테스트 점·기점)', '',
         '| 보드 | 참조 | 값 | 풋프린트 | 면 | 모델 경로 | 상태 |', '|---|---|---|---|---|---|---|']
    for r in sorted(rows, key=lambda r: (not r['missing'], r['board'], r['ref'])):
        mp = '<br>'.join('`%s`' % m['path'] for m in r['models']) or '—'
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (r['board'], r['ref'], r['value'].replace('|', '/'), r['footprint'], r['side'], mp,
                                                          ('**%s**' % r['state']) if r['missing'] else r['state']))
    if not a.no_md:
        open(os.path.join(HERE, 'model_audit.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    by = {}
    for r in miss:
        by.setdefault((r['footprint'], r['state']), []).append('%s:%s' % (r['board'][0].upper(), r['ref']))
    print('pcb', commit, 'footprints', len(rows), 'missing', len(miss))
    for (fp, st), refs in sorted(by.items()):
        print('MISS %-70s %-15s %s' % (fp, st, ' '.join(refs)))
    return len(miss)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
