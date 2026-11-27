"""REN-003 재질 배정 건식 점검 — 보드 GLB(kicad-cli export glb)를 파일로만 읽어 materials.py 규칙이 어떤 재질을 주는지 표로 (렌더·Blender·Fusion 없이).
  python -I -B mechanical/ren003/dryrun_glb.py [GLB 폴더]   (기본: main 체크아웃 validation/runtime/vd001/render/mesh)
출력: mechanical/ren003/assign_glb.md. 종료 코드 = 'keep'(규칙이 못 가른 색) 바디 종류 수."""
import json, os, struct, sys, collections, subprocess

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))   # main 체크아웃 — 산출물 validation/runtime (O-100)
g = {}
exec(open(os.path.join(HERE, 'materials.py'), encoding='utf-8').read(), g)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(MAIN, 'validation', 'runtime', 'vd001', 'render', 'mesh')
    rows = collections.Counter()
    keep = set()
    for b in ('carrier', 'front'):
        d = open(os.path.join(src, 'board_%s.glb' % b), 'rb').read()
        n = struct.unpack('<I', d[12:16])[0]
        j = json.loads(d[20:20 + n])
        parent = {c: i for i, nd in enumerate(j['nodes']) for c in nd.get('children', [])}
        for i, nd in enumerate(j['nodes']):
            if 'mesh' not in nd:
                continue
            ref = j['nodes'][parent[i]].get('name', '') if i in parent else ''
            mesh = j['meshes'][nd['mesh']]
            model = mesh.get('name', '')
            for pr in mesh['primitives']:
                m = j['materials'][pr['material']] if 'material' in pr else {}
                p = m.get('pbrMetallicRoughness', {})
                c = p.get('baseColorFactor', [1, 1, 1, 1])
                key = g['body_key'](c[:3], p.get('metallicFactor'), c[3], model=model, ref=ref, board=b)
                rows[(b, model or '(보드)', '%.3f %.3f %.3f a%.2f m%s' % (c[0], c[1], c[2], c[3], p.get('metallicFactor')), key)] += 1
                if key == 'keep':
                    keep.add((b, model, tuple(round(x, 3) for x in c)))
    L = ['# REN-003 재질 배정 건식 점검 (보드 GLB, `dryrun_glb.py` 출력 — 종료 코드 = 못 가른 색 %d)' % len(keep), '',
         '- 입력: `%s` (board_carrier.glb · board_front.glb)' % (os.path.relpath(src, MAIN).replace('\\', '/') + ' (main 체크아웃 기준)' if os.path.abspath(src).lower().startswith(MAIN.lower()) else '(저장소 밖 폴더)'),
         '- 규칙: `mechanical/ren003/materials.py` `classify()` → `body` 이면 `PART_RULES`(모델 이름 → 참조 번호)', '',
         '| 보드 | 모델 (GLB 메시 이름) | 파일 색 (선형) | 재질 | 바디 수 |', '|---|---|---|---|---|']
    L += ['| %s | %s | %s | %s %s | %d |' % (b, mo, col, k, g['MATS'][k]['label'] if k in g['MATS'] else '(원래 색 유지)', n) for (b, mo, col, k), n in sorted(rows.items())]
    open(os.path.join(HERE, 'assign_glb.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('rows', len(rows), 'keep', sorted(keep))
    return len(keep)


if __name__ == '__main__':
    sys.exit(main())
