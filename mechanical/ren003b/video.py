"""VID-001 영상 한 명령 (O-129 · O-130) — 메시 준비 → HDRI · 글꼴 확인 → Blender 프레임(video_anim.py) → 자막 → MP4 · GIF · 포스터 → 판정.

  python -I -B mechanical/ren003b/video.py [--names concept-explode,section-open,hero-dolly,bracket] [--final] [--case <상세 설계 메시 폴더>]
        [--glass-t 0.15] [--procs N] [--samples N] [--fps N] [--res WxH] [--no-docs]

- 메시: 기본은 main 체크아웃 validation/runtime/vd001/case/A (고른 시안의 상세 설계) + render/mesh 의 보드 GLB · 내부 부품. run.py --design 과 같은 방식.
- 기본 = 저해상도 시험(640×360 · 24 샘플 · 6 fps). --final = 1920×1080 · 128 샘플 · 30 fps + 대표본 복사.
- --procs N = Blender 프로세스 N개가 프레임을 나눠 렌더한다(같은 GPU). 다시 돌리면 끝난 프레임은 건너뛴다.
- 출력: main 체크아웃 validation/runtime/vd001/render/blender-b/video[_preview]/<이름>/ — frames/ · sub/(자막 얹은 것) · <이름>.mp4 · .gif · 포스터 · report.json
- 대표본(--final 이고 전부 통과, 이 체크아웃): docs/renders/final/video/<이름>.mp4 · .gif · 포스터(concept-explode.jpg, 나머지는 <이름>-poster.jpg)
- GIF: 무한 반복. 한도(concept-explode 5.0 MB, 나머지 2.0 MB)에 들 때까지 폭 · fps · 색 수 · 디더링을 차례로 낮춘다(GIF_STEPS).
  자막이 있는 영상은 GIF 크기로 줄인 프레임에 자막을 더 크게(GIF_CAPTION 배) 다시 얹는다 — 작은 화면에서도 읽히게.
- 자막 글꼴: Pretendard(SIL OFL 1.1) — assets.json 의 URL 에서 사용자 홈 격리 폴더(OPENHW_FONT_DIR 또는 ~/tools/fonts/pretendard)로 받고 sha256 을 맞춰 본다.
종료 코드 = 불합격 항목 수(기계 증거만: 종료 코드 · 프레임 수 · ffprobe · 파일 크기). 연출 · 자막 가독성 · 보기 품질은 판정하지 않는다."""
import argparse
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))      # -I 로 돌리면 스크립트 폴더가 경로에 없다
import materials_ext  # noqa: E402
import run as R  # noqa: E402

NAMES = ['concept-explode', 'section-open', 'hero-dolly', 'bracket']
GIF_LIMIT = {'concept-explode': 5.0e6}       # 바이트 — 나머지는 2.0e6 (README 이미지 합 예산, D-003 #69)
GIF_STEPS = [(640, 15, 160, 'bayer:bayer_scale=5'), (640, 12, 128, 'bayer:bayer_scale=5'), (560, 12, 128, 'bayer:bayer_scale=5'), (480, 12, 128, 'bayer:bayer_scale=5'),
             (480, 12, 128, 'none'), (480, 10, 128, 'none'), (400, 10, 128, 'none'), (400, 10, 96, 'none'), (360, 10, 96, 'none')]     # (폭 px, fps, 색 수, 디더링)
GIF_CAPTION = 1.7                           # GIF 자막 글자 크기 배율(화면 높이 대비, MP4 = 1)
GIF_SPEC = (480, 12, 128)                    # 지시 범위의 아래 끝 — 이보다 낮춰야 들면 판정에 적는다
POSTER_T = {'concept-explode': 2.6}          # 포스터로 쓸 시각(s) — 없으면 마지막 프레임
DUR = {'concept-explode': (15, 22)}          # MP4 길이 범위(s) — 나머지는 6~10


def fonts(chk):
    rec = json.load(open(os.path.join(R.HERE, 'assets.json'), encoding='utf-8')).get('font', [])
    d = os.environ.get('OPENHW_FONT_DIR') or os.path.join(os.path.expanduser('~'), 'tools', 'fonts', 'pretendard')
    os.makedirs(d, exist_ok=True)
    out, ok = {}, bool(rec)
    for f in rec:
        p = os.path.join(d, f['file'])
        try:
            if not os.path.exists(p):
                with urllib.request.urlopen(urllib.request.Request(f['url'], headers={'User-Agent': 'python-urllib'}), timeout=120) as r:
                    open(p, 'wb').write(r.read())
            ok = ok and hashlib.sha256(open(p, 'rb').read()).hexdigest() == f['sha256']
        except OSError:
            ok = False
        out[f['weight']] = p
    chk('자막 글꼴 받음 · sha256 이 assets.json 과 같음 (%s)' % (rec[0]['license'] if rec else '기록 없음'), [f['file'] for f in rec], ok)
    return out if ok else None


def overlay(src, dst, meta, font, W, H, k=1.0):
    """자막(화면 아래 가운데, 어두운 둥근 띠 위에 한글 · 영문 두 줄, 0.3 s 페이드) · 마지막 제목을 프레임 위에 얹는다.
    프레임은 W×H 로 줄여 쓰고 글자 · 띠는 k 배로 그린다(GIF 용)."""
    from PIL import Image, ImageDraw, ImageFont
    fk = ImageFont.truetype(font['SemiBold'], round(H * 0.040 * k))
    fe = ImageFont.truetype(font['Regular'], round(H * 0.026 * k))
    ft = ImageFont.truetype(font['SemiBold'], round(H * 0.090 * min(k, 1.3)))
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst, exist_ok=True)
    for i, f in enumerate(src):
        t = i / meta['fps']
        im = Image.open(f).convert('RGBA')
        if im.size != (W, H):
            im = im.resize((W, H), Image.LANCZOS)
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        for c in meta.get('captions', []):
            a = max(0.0, min(1.0, (t - c['t0']) / 0.3, (c['t1'] - t) / 0.3))
            if a > 0:
                wk, we = dr.textlength(c['ko'], font=fk), dr.textlength(c['en'], font=fe)
                w, pad = max(wk, we), H * 0.030 * k
                y0, y1 = H * (0.945 - 0.130 * k), H * 0.945
                dr.rounded_rectangle((W / 2 - w / 2 - pad, y0, W / 2 + w / 2 + pad, y1), radius=H * 0.014 * k, fill=(18, 20, 24, round(150 * a)))
                dr.text((W / 2, y0 + (y1 - y0) * 0.36), c['ko'], font=fk, fill=(255, 255, 255, round(255 * a)), anchor='mm')
                dr.text((W / 2, y0 + (y1 - y0) * 0.74), c['en'], font=fe, fill=(205, 210, 216, round(255 * a)), anchor='mm')
        tt = meta.get('title')
        if tt:
            a = max(0.0, min(1.0, (t - tt['t0']) / 0.5))
            if a > 0:
                dr.text((W * 0.81, H * 0.50), tt['text'], font=ft, fill=(24, 26, 30, round(255 * a)), anchor='mm')      # 제품 오른쪽 빈 배경에(아래는 제품 받침과 겹친다)
        Image.alpha_composite(im, lay).convert('RGB').save(os.path.join(dst, os.path.basename(f)), compress_level=1)
    return sorted(glob.glob(os.path.join(dst, 'frame_*.png')))


def probe(fp, path):
    r = subprocess.run([fp, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries', 'stream=nb_read_frames,width,height,codec_name,r_frame_rate',
                        '-of', 'json', path], capture_output=True, text=True)
    return json.loads(r.stdout)['streams'][0] if r.returncode == 0 and r.stdout.strip() else {}


def gif_loops_forever(path):
    d = open(path, 'rb').read(4096)
    k = d.find(b'NETSCAPE2.0')
    return k > 0 and d[k + 11:k + 13] == b'\x03\x01' and d[k + 13:k + 15] == b'\x00\x00'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--names', default=','.join(NAMES))
    ap.add_argument('--case', default=os.path.join(R.V, 'case', 'A'))
    ap.add_argument('--extra', default=os.path.join(R.V, 'render', 'mesh'))
    ap.add_argument('--boards-from', default=os.path.join(R.V, 'render', 'mesh'))
    ap.add_argument('--final', action='store_true')
    ap.add_argument('--core-step', default=os.environ.get('OPENHW_CORE_STEP') or next((p for p in [os.path.join(R.V, 'third_party', 'Recamera Core 2002.step')] if os.path.exists(p)), None),
                    help='Seeed 코어 STEP(저장소 밖) — 있으면 코어 덩어리 대신 실형상. 기본: OPENHW_CORE_STEP 또는 validation/runtime/vd001/third_party/. none 이면 덩어리')
    ap.add_argument('--glass-t', type=float, default=0.15)
    ap.add_argument('--procs', type=int, default=1)
    ap.add_argument('--samples', type=int)
    ap.add_argument('--fps', type=int)
    ap.add_argument('--res')
    ap.add_argument('--no-docs', action='store_true')
    a = ap.parse_args()
    names = [n for n in a.names.split(',') if n]
    res = a.res or ('1920x1080' if a.final else '640x360')
    W, H = (int(v) for v in res.split('x'))
    samples = a.samples or (128 if a.final else 24)
    fps = a.fps or (30 if a.final else 6)
    base = os.path.join(R.BASE, 'video' if a.final else 'video_preview')
    os.makedirs(base, exist_ok=True)
    ff, fp = R.ffbin('ffmpeg'), R.ffbin('ffprobe')
    fails = 0

    # ① 메시 · HDRI (영상마다 같다)
    mesh = os.path.join(base, 'mesh')
    rc_mesh = R.sh('메시 준비', R.PY + [os.path.join(R.HERE, 'prep.py'), '--enclosure', os.path.abspath(a.case), '--out', mesh, '--extra', os.path.abspath(a.extra),
                                   '--boards-from', os.path.abspath(a.boards_from), '--stl-only', '--extra-only', ','.join(materials_ext.DESIGN_INTERNALS)]
                   + (['--core-step', os.path.abspath(a.core_step)] if a.core_step and a.core_step != 'none' else []),
                   os.path.join(base, 'prep.log'))
    idx = json.load(open(os.path.join(mesh, 'index.json'), encoding='utf-8')) if rc_mesh == 0 else {}
    items, cs = idx.get('items', []), idx.get('core_step') or {}
    rc_hdri = R.sh('HDRI 확인 (Poly Haven CC0)', R.PY + [os.path.join(R.HERE, 'fetch_hdri.py')], os.path.join(base, 'hdri.log'))
    rec = json.load(open(os.path.join(R.HERE, 'assets.json'), encoding='utf-8'))['hdri'][0]
    hdri = os.path.join(os.environ.get('OPENHW_HDRI_DIR') or os.path.join(os.path.expanduser('~'), 'tools', 'hdri', 'polyhaven'), rec['file'])
    g = {}
    exec(open(os.path.join(R.HERE, '..', 'ren003', 'materials.py'), encoding='utf-8').read(), g)

    for name in names:
        checks = []

        def chk(what, value, ok, verifiable=True):
            checks.append({'check': what, 'value': value, 'pass': bool(ok), 'verifiable': verifiable})

        out = os.path.join(base, name)
        os.makedirs(out, exist_ok=True)
        chk('메시 준비 종료 코드 · 부품 수', '%d · 보드 %d · 부품 %d' % (rc_mesh, sum(i['kind'] == 'board' for i in items), sum(i['kind'] == 'enclosure' for i in items)),
            rc_mesh == 0 and sum(i['kind'] == 'board' for i in items) == 2)
        chk('HDRI 받음 · sha256 이 assets.json 과 같음', rec['file'], rc_hdri == 0 and os.path.exists(hdri))
        if a.core_step and a.core_step != 'none':
            chk('코어 실형상(STEP sha256 = assets.json) · 솔리드 수 · 뺀 무선 부품 수', '%s… · %s · %s' % (str(cs.get('sha256'))[:12], cs.get('solids_kept'), len(cs.get('hidden', []))),
                bool(cs) and cs.get('solids_kept', 0) > 0 and any('ANT-SPRING' in h for h in cs.get('hidden', [])) and any('AP6212' in h for h in cs.get('hidden', [])))

        # ② Blender 프레임
        sig = hashlib.sha256(json.dumps([items, res, samples, fps, a.glass_t, [hashlib.sha256(open(os.path.join(R.HERE, f), 'rb').read()).hexdigest()
                                                                              for f in ('scene.py', 'materials_ext.py', 'video_anim.py')]], sort_keys=True).encode()).hexdigest()
        sp = os.path.join(out, 'sig.txt')
        if not (os.path.exists(sp) and open(sp).read() == sig):       # 메시 · 설정 · 스크립트가 바뀌면 옛 프레임을 지운다
            for d in ('frames', 'sub'):
                shutil.rmtree(os.path.join(out, d), ignore_errors=True)
        open(sp, 'w').write(sig)
        ps = []
        for k in range(a.procs):
            po = os.path.join(out, 'p%d' % k)
            os.makedirs(po, exist_ok=True)
            cmd = [R.BLENDER, '-b', '--factory-startup', '--python-exit-code', '1', '--python', os.path.join(R.HERE, 'scene.py'), '--', '--mesh', mesh, '--out', po,
                   '--cuts', '', '--turntable', '0', '--tt-res', res, '--samples', str(samples), '--hdri', hdri, '--label', '', '--glass-t', str(a.glass_t),
                   '--video', name, '--video-fps', str(fps), '--video-dir', base, '--video-part', '%d/%d' % (k, a.procs)]
            ps.append((po, subprocess.Popen(cmd, stdout=open(os.path.join(po, 'blender.log'), 'w', encoding='utf-8'), stderr=subprocess.STDOUT) if items else None))
        rcs = [p.wait() if p else 1 for _, p in ps]
        reps = [json.load(open(os.path.join(po, 'scene_report.json'), encoding='utf-8')) if rc == 0 else {} for (po, _), rc in zip(ps, rcs)]
        rep = reps[0]
        print('[Blender %s] rc %s · 새 프레임 %d · 건너뜀 %d' % (name, rcs, sum((r.get('video') or {}).get(name, {}).get('new', 0) for r in reps),
                                                           sum((r.get('video') or {}).get(name, {}).get('skipped', 0) for r in reps)), flush=True)
        chk('Blender 종료 코드 (--python-exit-code 1, 프로세스 %d개)' % a.procs, rcs, all(rc == 0 for rc in rcs))
        chk('재질 정의 수 = materials.py MATS · 재질 빠짐', '%s / %d (+확장 %s) · 빠짐 %s' % (rep.get('mats_defined'), len(g['MATS']), rep.get('mats_ext'), rep.get('missing_count')),
            rep.get('mats_defined') == len(g['MATS']) and rep.get('missing_count') == 0)
        chk('엔진 · 장치 · 디노이저 · 샘플', '%s · %s · %s · %s' % (rep.get('engine'), rep.get('device'), rep.get('denoiser'), rep.get('samples')),
            rep.get('engine') == 'CYCLES' and bool(rep.get('denoiser')) and rep.get('samples') == samples)
        chk('HDRI 가 장면에 쓰임 (sha256 일치) · 색 관리', '%s · %s' % ((rep.get('hdri') or {}).get('file'), rep.get('view_transform')),
            (rep.get('hdri') or {}).get('sha256') == rec['sha256'] and rep.get('view_transform') == 'AgX')
        meta = json.load(open(os.path.join(out, 'meta.json'), encoding='utf-8')) if os.path.exists(os.path.join(out, 'meta.json')) else {'frames': -1, 'fps': fps}
        n = meta['frames']
        fr = sorted(glob.glob(os.path.join(out, 'frames', 'frame_*.png')))
        chk('프레임 수 (길이 %s s × %d fps)' % (meta.get('duration_s'), fps), '%d / %d' % (len(fr), n), len(fr) == n)
        chk('프레임 해상도 · 빈 파일 없음', sorted({R.png_size(p) for p in fr}), bool(fr) and all(R.png_size(p) == (W, H) and os.path.getsize(p) > 1000 for p in fr))
        nd = len({hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in fr})
        chk('서로 다른 프레임 수 (움직임 있음, 멈춘 구간은 같을 수 있다)', '%d / %d' % (nd, len(fr)), len(fr) > 1 and nd >= 0.8 * len(fr))
        if 'section_check' in meta.get('info', {}):
            sc = meta['info']['section_check']
            chk('단면: 마지막 프레임에서 자른 쪽에 남은 객체 수 (자른 부품 %s · 평면 x = %s mm)' % (sc.get('n_cut'), sc.get('x0_mm')), sc.get('n_uncut'), sc.get('n_uncut') == 0)

        # ③ 자막
        src = fr
        if (meta.get('captions') or meta.get('title')) and len(fr) == n:
            font = fonts(chk)
            if font:
                src = overlay(fr, os.path.join(out, 'sub'), meta, font, W, H)
                chk('자막 얹은 프레임 수 (자막 %d개 + 제목)' % len(meta.get('captions', [])), '%d / %d' % (len(src), n), len(src) == n)
        pat = os.path.join(os.path.dirname(src[0]) if src else out, 'frame_%04d.png')

        # ④ MP4 · GIF · 포스터 (격리 ffmpeg)
        mp4, gif = os.path.join(out, name + '.mp4'), os.path.join(out, name + '.gif')
        poster = os.path.join(out, name + ('.jpg' if name == 'concept-explode' else '-poster.jpg'))
        chk('격리 ffmpeg 찾음', bool(ff and fp), bool(ff and fp))
        lim = GIF_LIMIT.get(name, 2.0e6)
        if ff and fp and len(src) == n > 0:
            for f in (mp4, gif, poster):
                if os.path.exists(f):
                    os.remove(f)
            rc = R.sh('ffmpeg MP4 ' + name, [ff, '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(fps), '-i', pat, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                                             '-crf', '18', '-movflags', '+faststart', mp4], os.path.join(out, 'ffmpeg_mp4.log'))
            st = probe(fp, mp4) if rc == 0 else {}
            nf = int(st.get('nb_read_frames', 0))
            chk('MP4 ffprobe: 프레임 수 · 길이 · 해상도 · 코덱 · fps', '%d · %.2f s · %sx%s · %s · %s' % (nf, nf / fps, st.get('width'), st.get('height'), st.get('codec_name'), st.get('r_frame_rate')),
                rc == 0 and nf == n and (st.get('width'), st.get('height')) == (W, H) and st.get('codec_name') == 'h264' and st.get('r_frame_rate') == '%d/1' % fps)
            if a.final:
                lo, hi = DUR.get(name, (6, 10))
                chk('MP4 1080p · 30 fps · 길이 %d~%d s' % (lo, hi), '%dp · %d fps · %.2f s · %d 바이트' % (H, fps, nf / fps, os.path.getsize(mp4) if rc == 0 else 0),
                    H == 1080 and fps == 30 and lo <= nf / fps <= hi)
            used, capt = None, src is not fr
            for gw, gf, gc, gd in GIF_STEPS if a.final else [(min(W, 480), fps, 128, 'none')]:
                vf = 'fps=%d,scale=%d:-1:flags=lanczos' % (gf, gw)
                gpat = pat
                if capt:        # 자막은 GIF 크기에서 더 크게 다시 얹는다
                    overlay(fr, os.path.join(out, 'gif_frames'), meta, font, gw, round(gw * H / W / 2) * 2, GIF_CAPTION)
                    vf, gpat = 'fps=%d' % gf, os.path.join(out, 'gif_frames', 'frame_%04d.png')
                rc = R.sh('ffmpeg GIF %s %dpx %dfps %d색 %s' % (name, gw, gf, gc, gd.split(':')[0]),
                          [ff, '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(fps), '-i', gpat, '-vf',
                           vf + ',split[a][b];[a]palettegen=max_colors=%d:stats_mode=diff[p];[b][p]paletteuse=dither=%s:diff_mode=rectangle' % (gc, gd),
                           '-loop', '0', gif], os.path.join(out, 'ffmpeg_gif.log'))
                used = (gw, gf, gc, gd.split(':')[0])
                if rc != 0 or os.path.getsize(gif) <= lim:
                    break
            gs = probe(fp, gif) if rc == 0 else {}
            sz = os.path.getsize(gif) if rc == 0 else 0
            inspec = all(u >= s_ for u, s_ in zip(used[:3], GIF_SPEC))
            chk('GIF 크기 ≤ %.1f MB · 무한 반복 (설정: 한도에 드는 첫 단계%s)' % (lim / 1e6, '' if inspec or not a.final else ' — 지시 범위 %dpx · %dfps · %d색 아래로 내려감' % GIF_SPEC),
                '%d 바이트 · %spx · %d fps · %d색 · 디더링 %s · %s프레임 · 반복 %s' % (sz, gs.get('width'), used[1], used[2], used[3], gs.get('nb_read_frames'),
                                                                        '무한' if rc == 0 and gif_loops_forever(gif) else '?'),
                rc == 0 and 0 < sz <= lim and gif_loops_forever(gif))
            from PIL import Image
            k = min(n - 1, round(POSTER_T[name] * fps)) if name in POSTER_T else n - 1
            Image.open(src[k]).convert('RGB').save(poster, quality=90)
            chk('포스터 (프레임 %d)' % (k + 1), '%s · %d 바이트' % (Image.open(poster).size, os.path.getsize(poster)), Image.open(poster).size == (W, H))
        else:
            chk('MP4 · GIF 만들기', '건너뜀 (프레임 수 또는 ffmpeg)', False)

        # ⑤ 대표본 · 기록
        docs = []
        if a.final and not a.no_docs and all(c['pass'] for c in checks):
            d = os.path.join(R.LANE, 'docs', 'renders', 'final', 'video')
            os.makedirs(d, exist_ok=True)
            for f in (mp4, gif, poster):
                shutil.copy2(f, os.path.join(d, os.path.basename(f)))
                docs.append('docs/renders/final/video/' + os.path.basename(f))
        chk('연출 · 자막 가독성 · 보기 품질', '사람 확인 필요 — %s' % R.rel(mp4), True, verifiable=False)
        bad = [c for c in checks if c['verifiable'] and not c['pass']]
        json.dump({'name': name, 'mode': 'final' if a.final else 'preview', 'res': [W, H], 'samples': samples, 'fps': fps, 'case': R.rel(a.case), 'out': R.rel(out),
                   'meta': meta, 'representative': docs, 'checks': checks, 'fail': len(bad)}, open(os.path.join(out, 'report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        for c in checks:
            print('  %s %s: %s' % ('—  ' if not c['verifiable'] else 'OK ' if c['pass'] else 'NG ', c['check'], c['value']))
        print('VID-001 %s %s: 불합격 %d · 출력 %s' % (name, 'final' if a.final else 'preview', len(bad), R.rel(out)), flush=True)
        fails += len(bad)
    return fails


if __name__ == '__main__':
    sys.exit(main())
