"""REN-002 대체 3D 모델 연결 적용 — models_spec.LINK (풋프린트 → mechanical/models/<이름>.step)
  python -I -B mechanical/ren002/apply_models.py <파일 또는 폴더> ...
  - .kicad_pcb: 연결 표에 있는 풋프린트마다 — 모델 속성이 없으면 새로 넣고, 있으면 풀리지 않는 경로를 바꾼다(다른 모델 줄은 그대로).
  - .pretty 폴더 / .kicad_mod: 같은 규칙을 풋프린트 라이브러리에 (pcb 가 라이브러리에 넣고 보드를 갱신하는 경우).
  - 경로 = ${KIPRJMOD}/../../../mechanical/models/<이름>.step, offset 0 · scale 1 · rotate 0.
  출력: 바꾼 풋프린트 수. pcb 저장소 파일에 쓸지는 pcb 가 정한다 — 렌더용 사본에는 render 스크립트가 이것을 부른다."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
S = {}
exec(open(os.path.join(HERE, 'models_spec.py'), encoding='utf-8').read(), S)


def model_block(name, ind):
    p = '%s/%s.step' % (S['MODEL_DIR'], name)
    return ('%s(model "%s"\n%s\t(offset\n%s\t\t(xyz 0 0 0)\n%s\t)\n%s\t(scale\n%s\t\t(xyz 1 1 1)\n%s\t)\n%s\t(rotate\n%s\t\t(xyz 0 0 0)\n%s\t)\n%s)\n'
            % (ind, p, ind, ind, ind, ind, ind, ind, ind, ind, ind, ind))


def fix_block(blk, lib, ind):
    name = S['LINK'].get(lib)
    if not name:
        return blk, False
    want = '%s/%s.step' % (S['MODEL_DIR'], name)
    if want in blk:
        return blk, False
    models = list(re.finditer(r'\(model "([^"]+)"', blk))
    if models:          # 표에 있는 풋프린트의 첫 모델 경로를 바꿈 (표준 라이브러리에 파일이 없는 것)
        m = models[0]
        return blk[:m.start(1)] + want + blk[m.end(1):], True
    k = blk.rstrip().rfind(')')
    return blk[:k].rstrip('\t') + model_block(name, ind) + ind[:-1] + blk[k:], True


def walk_pcb(t):
    out, pos, n = [], 0, 0
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', t):
        s = m.start() + 1
        if s < pos:
            continue
        depth = 0
        for k in range(s, len(t)):
            if t[k] == '(':
                depth += 1
            elif t[k] == ')':
                depth -= 1
                if depth == 0:
                    break
        blk = t[s:k + 1]
        nb, ch = fix_block(blk, m.group(1), '\t\t')
        out.append(t[pos:s]); out.append(nb); pos = k + 1; n += ch
    out.append(t[pos:])
    return ''.join(out), n


def apply(path):
    t = open(path, encoding='utf-8').read()
    if path.endswith('.kicad_pcb'):
        t2, n = walk_pcb(t)
    else:
        lib = 'openhw:' + os.path.splitext(os.path.basename(path))[0]
        if lib not in S['LINK']:
            return 0
        t2, n = fix_block(t, lib, '\t')
        n = int(n)
    if n:
        open(path, 'w', encoding='utf-8', newline='\n').write(t2)
    return n


def main(args):
    total = 0
    for a in args:
        files = [os.path.join(a, f) for f in sorted(os.listdir(a)) if f.endswith('.kicad_mod')] if os.path.isdir(a) else [a]
        for f in files:
            n = apply(f)
            total += n
            if n:
                print('LINK %s %d' % (f, n))
    print('changed footprints', total)
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))
