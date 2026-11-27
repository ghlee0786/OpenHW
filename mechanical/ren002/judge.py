"""REN-002 렌더 판정 — python -I -B mechanical/ren002/judge.py   (종료 코드 = 불합격 수)
기계 판정: 3D 모델 빠짐 0 (렌더용 사본 감사) · 파일 수 · 해상도 2560×1440 · MP4 길이 7.5~8.5 s · 입력 해시.
보기(재질·조명·구도·글자·치수선)는 사람 확인(verifiable 아니오) → manifest.json 의 check 로 VD-001 HTML 에 넘긴다.
쓰는 것: validation/runtime/vd001/render/manifest.json (vd001-format §4), mechanical/ren002/hashes.md (커밋용 해시 목록)."""
import glob, hashlib, json, os, struct, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))   # main 체크아웃 — 산출물 validation/runtime (O-100)
V = os.path.join(MAIN, 'validation', 'runtime', 'vd001')
R = os.path.join(V, 'render')
FFPROBE = glob.glob(os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*\bin\ffprobe.exe'))
W, H = 2560, 1440
BKO = {'carrier': '캐리어', 'front': '전면'}
PCB_SRC = 'kicad-cli 10.0.8 pcb render --quality high (렌더용 사본 = pcb 보드 + mechanical/models 연결, ren002/scripts/02_pcb_render.py)'
BL_SRC = 'Blender 5.2.1 Cycles OptiX 256 spp (mechanical/ren002/scene.py)'
STILLS = [  # (보기, kind, 제목, 사람이 볼 것)
    ('front', 'assembly', '앞', '흑색 PETG 무광 · 창 PMMA 투명 · 렌즈'),
    ('back', 'assembly', '뒤 (뒷벽·삼각대 자리)', '뒷벽 구멍·카운터보어 · 그림자'),
    ('threequarter', 'enclosure', '3/4 외함 완성', 'PETG(무광, 층 결) ↔ 아노다이즈 방열판(반광) 구분'),
    ('exploded', 'exploded', '분해', '부품 순서·겹침'),
    ('section', 'section', '단면 x = 0', '적층·렌즈·보드·하니스'),
    ('window', 'assembly', '창 근접 — 렌즈 창 + LED A 창 너머 (내부 조명 약간)', '창 너머 LED A1·A2·홀더가 보이는지'),
    ('connectors', 'assembly', '커넥터 면 — RJ45·DC 잭(−Y) · USB-C(−X), 누운 자세', '개구와 커넥터 정렬'),
    ('microsd', 'assembly', 'microSD 홈 (+Y 아래 벽), 누운 자세', '카드 홈 위치'),
    ('inuse', 'assembly', '사용 장면 — 받침대 + RJ45·DC 케이블', '플러그·케이블 굽힘이 자연스러운지'),
    ('dims', 'enclosure', '외형 치수선 (폭·높이·깊이 mm)', '치수선 위치·값 (폭 71.8 · 높이 71.0 · 깊이 69.9)'),
]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def png_size(p):
    with open(p, 'rb') as f:
        h = f.read(24)
    return struct.unpack('>II', h[16:24]) if h[:8] == b'\x89PNG\r\n\x1a\n' else (0, 0)


def rel(p):
    return os.path.relpath(p, MAIN).replace('\\', '/')


def main():
    fails, man, rows = [], [], []
    # 1) 3D 모델 빠짐 0 (렌더용 사본)
    # M-010: 렌더용 사본 = mechanical/m007/run_all.py 가 보드마다 만든 pcbsrc/<보드> (그 커밋 + apply_models)
    for b in ('carrier', 'front'):
        aj = os.path.join(V, 'ren002', 'model_audit_render_%s.json' % b)
        subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'audit_models.py'), '--src', os.path.join(V, 'pcbsrc', b), '--out-json', aj, '--no-md'],
                       capture_output=True, encoding='utf-8', errors='replace')
        n = sum(1 for r in json.load(open(aj, encoding='utf-8'))['rows'] if r['board'] == b and r['missing'])
        if n:
            fails.append('렌더용 사본 %s 3D 모델 빠짐 %d' % (b, n))
    pcb = json.load(open(os.path.join(V, 'boards', 'models_missing.json'), encoding='utf-8'))['pcb']   # 렌더용 사본을 만든 pcb 커밋
    inp = {'pcb': pcb}
    for f in ('m007_assembly.step', 'pcbsrc/carrier/hardware/schematic/carrier/carrier.kicad_pcb', 'pcbsrc/front/hardware/schematic/front/front.kicad_pcb',
              'render/mesh/index.json', 'render/mesh/board_carrier.glb', 'render/mesh/board_front.glb'):
        p = os.path.join(V, f)
        inp[f] = sha(p) if os.path.exists(p) else None
        if inp[f] is None:
            fails.append('입력 없음 ' + f)

    def png(p, kind, board, title, source, ikey, check):
        ok = os.path.exists(p)
        wh = png_size(p) if ok else (0, 0)
        good = ok and tuple(wh) == (W, H)
        if not good:
            fails.append('%s %s' % (rel(p), '없음' if not ok else '%dx%d' % wh))
        man.append({'kind': kind, 'board': board, 'title': title, 'path': rel(p), 'sha256': sha(p) if ok else None, 'source': source,
                    'input_sha256': inp.get(ikey), 'verifiable': False, 'check': check})
        rows.append((rel(p), '%dx%d' % tuple(wh), sha(p) if ok else '-', '통과' if good else '**불합격**'))

    for b in ('carrier', 'front'):
        ik = 'pcbsrc/%s/hardware/schematic/%s/%s.kicad_pcb' % (b, b, b)
        png(os.path.join(R, 'pcb', '%s_top.png' % b), 'pcb-front', b, '%s 윗면 (정사영)' % BKO[b], PCB_SRC, ik, '부품 3D 모델 빠짐 없음 · 실크')
        png(os.path.join(R, 'pcb', '%s_bottom.png' % b), 'pcb-back', b, '%s 아랫면 (정사영)' % BKO[b], PCB_SRC, ik, '부품 3D 모델 빠짐 없음 · 실크')
        png(os.path.join(R, 'pcb', '%s_tilt.png' % b), 'pcb-front', b, '%s 기울임' % BKO[b], PCB_SRC, ik, '입체감 · 높은 부품')
        for side, kind, ko in (('top', 'pcb-front', '윗면'), ('bottom', 'pcb-back', '아랫면')):
            tiles = sorted(glob.glob(os.path.join(R, 'pcb', '%s_%s_zoom*.png' % (b, side))), key=lambda s: int(s.rsplit('zoom', 1)[1][:-4]))
            if not tiles:
                fails.append('확대 컷 없음 %s %s' % (b, side))
            for t in tiles:
                png(t, kind, b, '%s %s 확대 %s (부품 번호 주석 = Fab 위치, 실크 아님)' % (BKO[b], ko, t.rsplit('zoom', 1)[1][:-4]), PCB_SRC, ik,
                    '실크 선·부품 번호(노란 주석) 읽힘')
    for v, kind, title, check in STILLS:
        png(os.path.join(R, 'blender', 'stills', 'ren002_%s.png' % v), kind, '-', title, BL_SRC, 'm007_assembly.step', check)
    mp4 = os.path.join(R, 'blender', 'ren002_turntable.mp4')
    if os.path.exists(mp4) and FFPROBE:
        j = json.loads(subprocess.run([FFPROBE[0], '-v', 'error', '-show_entries', 'format=duration:stream=width,height,nb_frames,codec_name', '-of', 'json', mp4],
                                      capture_output=True, text=True).stdout)
        dur = float(j['format']['duration']); st = j['streams'][0]
        good = 7.5 <= dur <= 8.5
        rows.append((rel(mp4), '%sx%s %s 프레임 %s · %.2f s' % (st['width'], st['height'], st['codec_name'], st.get('nb_frames'), dur), sha(mp4), '통과' if good else '**불합격**'))
        if not good:
            fails.append('MP4 길이 %.2f' % dur)
        man.append({'kind': 'turntable', 'board': '-', 'title': '턴테이블 8 s (최종 모델, EEVEE 1920×1080 25 fps)', 'path': rel(mp4), 'sha256': sha(mp4),
                    'source': 'Blender 5.2.1 EEVEE + render_chunks.py + ffmpeg libx264', 'input_sha256': inp['m007_assembly.step'], 'verifiable': False,
                    'check': '한 바퀴 매끄러움 · 재질'})
    else:
        fails.append('MP4 없음 또는 ffprobe 없음')
    json.dump(man, open(os.path.join(R, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    L = ['# REN-002 렌더 판정·해시 (judge.py 출력 — 불합격 %d, 산출 %d)' % (len(fails), len(rows)), '',
         '- 3D 모델 감사 (렌더용 사본 pcbsrc/<보드>, pcb %s + mechanical/models 연결): 빠짐 %d' % (pcb, sum(1 for f in fails if f.startswith('렌더용 사본'))),
         '- 산출물: validation/runtime/vd001/render/ (gitignore) · manifest.json (vd001-format §4, 모두 사람 확인 verifiable 아니오 + check 열)', '',
         '## 입력', '', '| 파일 (validation/runtime/vd001/) | sha256 |', '|---|---|'] + ['| %s | %s |' % (k, v) for k, v in inp.items()]
    L += ['', '## 산출', '', '| 파일 | 크기 | sha256 | 판정 |', '|---|---|---|---|'] + ['| %s | %s | %s | %s |' % r for r in rows]
    if fails:
        L += ['', '## 불합격', ''] + ['- ' + f for f in fails]
    open(os.path.join(HERE, 'hashes.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('\n'.join(L[:4]))
    for f in fails:
        print('FAIL', f)
    return len(fails)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
