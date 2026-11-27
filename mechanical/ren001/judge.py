"""REN-001 렌더 판정 — python -I -B mechanical/ren001/judge.py   (종료 코드 = 불합격 수)
기계 판정: 파일 수 · 해상도 · MP4 길이 · 입력 해시. 보기(색·재질·구도)는 사람 확인 → VD-001 HTML (manifest.json, verifiable 아니오).
쓰는 것: validation/runtime/vd001/render/manifest.json (docs/review/vd001-format.md §4), mechanical/ren001/hashes.md (커밋용 해시 목록)."""
import hashlib, json, os, struct, subprocess, sys, glob

LANE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
V = os.path.join(LANE, 'validation', 'runtime', 'vd001')
R = os.path.join(V, 'render')
FFPROBE = glob.glob(os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*\bin\ffprobe.exe'))
W, H = 2560, 1440
PCB = [(b, v) for b in ('carrier', 'front') for v in ('top', 'bottom', 'tilt')]
KIND_PCB = {'top': 'pcb-front', 'bottom': 'pcb-back', 'tilt': 'pcb-front'}
STILLS = {'front': ('assembly', '앞'), 'back': ('assembly', '뒤 (방열판·커넥터 면)'), 'threequarter': ('enclosure', '3/4 외함 완성'),
          'exploded': ('exploded', '분해'), 'section': ('section', '단면 x = 0'), 'window': ('assembly', '창 근접 — 렌즈·LED 가 창 너머로 보이는 컷')}
BOARD_KO = {'carrier': '캐리어', 'front': '전면'}
VIEW_KO = {'top': '윗면', 'bottom': '아랫면', 'tilt': '기울임'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def png_size(p):
    with open(p, 'rb') as f:
        h = f.read(24)
    return struct.unpack('>II', h[16:24]) if h[:8] == b'\x89PNG\r\n\x1a\n' else (0, 0)


def rel(p):
    return os.path.relpath(p, LANE).replace('\\', '/')


def main():
    fails = []
    man = []
    inp = {}
    for f in ('m007_assembly.step', 'pcbsrc/hardware/schematic/carrier/carrier.kicad_pcb', 'pcbsrc/hardware/schematic/front/front.kicad_pcb',
              'render/mesh/index.json', 'render/mesh/board_carrier.glb', 'render/mesh/board_front.glb'):
        p = os.path.join(V, f)
        inp[f] = sha(p) if os.path.exists(p) else None
        if inp[f] is None:
            fails.append('입력 없음 ' + f)
    rows = []

    def check_png(p, kind, board, title, source, input_key):
        ok = os.path.exists(p)
        wh = png_size(p) if ok else (0, 0)
        good = ok and tuple(wh) == (W, H)
        if not good:
            fails.append('%s %s' % (rel(p), '없음' if not ok else '%dx%d' % wh))
        h = sha(p) if ok else None
        man.append({'kind': kind, 'board': board, 'title': title, 'path': rel(p), 'sha256': h, 'source': source, 'input_sha256': inp.get(input_key)})
        rows.append((rel(p), '%dx%d' % tuple(wh), h, '통과' if good else '**불합격**'))

    for b, v in PCB:
        check_png(os.path.join(R, 'pcb', '%s_%s.png' % (b, v)), KIND_PCB[v], b, '%s %s' % (BOARD_KO[b], VIEW_KO[v]),
                  'kicad-cli 10.0.8 pcb render --quality high --floor --perspective', 'pcbsrc/hardware/schematic/%s/%s.kicad_pcb' % (b, b))
    for v, (kind, title) in STILLS.items():
        check_png(os.path.join(R, 'stills', 'ren001_%s.png' % v), kind, '-', title,
                  'Blender 5.2.1 Cycles OptiX 256 spp (mechanical/ren001/scene.py)', 'm007_assembly.step')
    mp4 = os.path.join(R, 'ren001_turntable.mp4')
    dur = None
    if os.path.exists(mp4) and FFPROBE:
        o = subprocess.run([FFPROBE[0], '-v', 'error', '-show_entries', 'format=duration:stream=width,height,nb_frames,codec_name', '-of', 'json', mp4],
                           capture_output=True, text=True).stdout
        j = json.loads(o); dur = float(j['format']['duration']); st = j['streams'][0]
        good = 7.5 <= dur <= 8.5
        rows.append((rel(mp4), '%sx%s %s 프레임 %s · %.2f s' % (st['width'], st['height'], st['codec_name'], st.get('nb_frames'), dur), sha(mp4), '통과' if good else '**불합격**'))
        if not good:
            fails.append('MP4 길이 %.2f' % dur)
        man.append({'kind': 'turntable', 'board': '-', 'title': '턴테이블 8 s (EEVEE 1920×1080 25 fps)', 'path': rel(mp4), 'sha256': sha(mp4),
                    'source': 'Blender 5.2.1 EEVEE + render_chunks.py + ffmpeg libx264', 'input_sha256': inp['m007_assembly.step']})
    else:
        fails.append('MP4 없음 또는 ffprobe 없음')
    json.dump(man, open(os.path.join(R, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    L = ['# REN-001 렌더 해시 (judge.py 출력 — 불합격 %d)' % len(fails), '',
         '- 산출물: validation/runtime/vd001/render/ (gitignore) · manifest.json (vd001-format §4)',
         '- 보기 확인은 사람 눈(verifiable 아니오) — VD-001 HTML 에서 체크', '', '## 입력', '', '| 파일 (validation/runtime/vd001/) | sha256 |', '|---|---|']
    L += ['| %s | %s |' % (k, v) for k, v in inp.items()]
    L += ['', '## 산출', '', '| 파일 | 크기 | sha256 | 판정 |', '|---|---|---|---|'] + ['| %s | %s | %s | %s |' % r for r in rows]
    if fails:
        L += ['', '## 불합격', ''] + ['- ' + f for f in fails]
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hashes.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    return len(fails)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
