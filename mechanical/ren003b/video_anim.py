"""영상 프레임 (O-129 · O-130) — scene.py 가 장면(메시 · 재질 · 조명 · 배경 · 카메라)을 만든 뒤 `--video <이름,...>` 이 있으면 부른다.

  concept-explode  완제품 히어로 → 순간 분해 → 부품 6개 차례로(앞으로 떠올라 제 축으로 돌고, 카메라는 둘레를 돌며 다가감) → 다시 조립 → 로고 컷
  section-open     외함이 평면에 잘려 나가며 안의 보드 3층 · 렌즈가 드러남
  hero-dolly       뒤(방열 핀) → 위(상태 LED) → 앞(렌즈)으로 천천히 돌며 다가감
  bracket          벽 브래킷에 달린 채 팬(좌우) · 틸트(위아래)로 움직임 — 브래킷 부품(ARM · PAN · TILT · PIN)이 있는 시안만

- 프레임: `--video-dir`(없으면 <out>/video)/<이름>/frames/frame_0001.png … (TT_RES, `--video-fps`). 있는 프레임은 건너뛴다.
  `--video-part k/n` = 프레임 번호를 n 으로 나눈 나머지가 k 인 것만(여러 프로세스가 나눠 렌더).
- 자막은 여기서 그리지 않는다. 시각 · 문구를 <이름>/meta.json 에 적고 video.py 가 프레임 위에 얹는다.
- 조명 · 바닥은 닫힌 제품 기준으로 고정한다(카메라가 다가가도 밝기가 변하지 않게). 카메라 렌즈 90 mm.
- 심도: 조리개 = 4900 / (k × 카메라 거리 mm) — k = 1 이면 히어로 컷(f/8 · 0.6 m)과 같은 흐림 비율, 클로즈업은 k 를 키워 얕게.
- 분해 거리 · 순서 · 들어 올림 · 회전각은 보기용 연출 값이다(조립 공정 문서가 아니다).
"""
import json
import math
import os

import bpy
from mathutils import Matrix, Vector

MM = 0.001
LENS = 90


def ease(t, a=0.0, b=1.0):
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def quad(a, b, c, u):
    """u = 0 · 0.5 · 1 에서 a · b · c 를 지나는 2차 곡선."""
    return a * ((1 - u) * (1 - 2 * u)) + b * (4 * u * (1 - u)) + c * (u * (2 * u - 1))


def track(keys, t):
    """keys = [(시각, 값 dict, 'move' | 'drift')] — 앞 키에서 이 키로 가는 방식(move = 가감속, drift = 등속)."""
    if t <= keys[0][0]:
        return dict(keys[0][1])
    for (t0, a, _), (t1, b, how) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            u = u * u * (3 - 2 * u) if how == 'move' else u
            return {k: lerp(a[k], b[k], u) for k in a}
    return dict(keys[-1][1])


def aim(S, q, lift=Vector((0, 0, 0)), light=None):
    """q = yaw · el · az(°) · p(목표, 제품 좌표 m) · w(들어 올림 0~1) · r(틀 반높이 m) · k(심도 배율) · fb(초점을 앞으로 당기는 비율)"""
    S.tt.rotation_euler = (0, 0, math.radians(-q['yaw']))
    bpy.context.view_layer.update()
    tgt = S.prod.matrix_world @ q['p'] + lift * q['w']
    _, _, d = S.stage(q['yaw'], q['el'], LENS, 1.0, az=q['az'], target=tgt, res=S.TT_RES, focus_bias=q['fb'], radius=q['r'], light=light or (S.C, S.RAD))
    S.cyc.location = (S.C.x, S.C.y, S.lo.z - 0.0002)
    S.cd.dof.aperture_fstop = max(2.8, 4900.0 / (q['k'] * d / MM))


# ---------------- concept-explode (O-130) ----------------
# 분해 이동량(제품 좌표 mm, 광축 = Z). 분해도 컷(scene.EXPLODE)보다 넓게 벌려 부품을 하나씩 꺼내 돌릴 자리를 둔다.
C_OFF = [('WIN_CLEAR', (0, 0, 178)), ('GLASS_MASK', (0, 0, 150)), ('GLASS_IR', (0, 0, 165)), ('INNER_MASK', (0, 0, 68)), ('INSERT_M25', (0, 0, 88)),
         ('INSERT_1_4', (0, 0, 100)), ('SHELL_PLASTIC', (0, 0, 100)), ('LENS_CIL093', (0, 0, 34)), ('BOARD_FRONT', (0, 0, 14)), ('SENSOR_BLOCK', (0, 0, 14)),
         ('PEDESTAL', (0, 0, 14)), ('FPC', (0, 0, 14)), ('CORE_MODULE', (0, 0, 0)), ('GASKET', (0, 0, -12)), ('BOARD_CARRIER', (0, 0, -30)),
         ('LIGHT_PIPE', (0, 16, -95)), ('COVER_USBC', (-16, 0, -95)), ('COVER_MICROSD', (0, 14, -95)), ('GROMMET', (0, 0, -95)), ('SHELL_ALU', (0, 0, -95))]
# (같이 움직이는 부품 이름 조각 — 첫 조각이 중심 · 크기 기준, 카메라 쪽을 보는 면의 처음 · 끝 방위°(0 = 앞면, 90 = +X 면, 180 = 뒷면), 틀 크기 배율, 자막 한 · 영)
C_SHOTS = [(('GLASS_IR', 'GLASS_MASK', 'WIN_CLEAR'), -30, 150, 1.15, 'IR 투과 앞유리 · 마스크', 'IR-pass front glass · mask'),
           (('LENS_CIL093',), -88, 12, 1.2, '렌즈 CIL093', 'CIL093 lens'),
           (('BOARD_FRONT', 'SENSOR_BLOCK', 'PEDESTAL', 'FPC'), -15, 165, 1.2, '전면 보드 — 이미지 센서 · IR LED · 조도 센서', 'Front board — image sensor · IR LEDs · ambient light sensor'),
           (('CORE_MODULE',), -20, 130, 1.3, '코어 모듈 — SoC · eMMC', 'Core module — SoC · eMMC'),
           (('BOARD_CARRIER',), -20, 160, 1.15, '캐리어 보드 — 커넥터 · microSD · 전원', 'Carrier board — connectors · microSD · power'),
           (('SHELL_ALU', 'LIGHT_PIPE', 'COVER_USBC', 'COVER_MICROSD', 'GROMMET'), 15, 150, 1.05, '알루미늄 방열 쉘', 'Aluminium heat-sink shell')]
C_T_BURST, C_BURST, C_T0, C_SHOT = 1.5, 0.8, 2.7, 2.5       # 분해 시작 · 분해 길이 · 첫 부품 시작 · 부품 하나 길이 (s)
C_YAW = -60                                                 # 분해한 줄을 보는 방위(제품 yaw°)
C_LIFT = Vector((0, -0.075, 0.004))                         # 부품을 꺼내는 방향 · 거리(월드 m): 카메라 쪽으로, 살짝 위로


def concept(S):
    prod, parts = S.prod, S.parts
    moved = {}
    for n, o in parts.items():
        v = next((v for key, v in C_OFF if key in n), None)
        if v is not None and o not in S.OWN_BRACKET:
            moved[o] = Vector(v) * MM
    base = {o: o.matrix_basis.copy() for o in moved}
    pinv = {o: o.matrix_parent_inverse.copy() for o in moved}
    rank = {l: i for i, l in enumerate(sorted({round(v.length, 6) for v in moved.values()}))}       # 다시 조립: 조금 움직인 것(안쪽)부터
    t_re = C_T0 + len(C_SHOTS) * C_SHOT
    t_hero = t_re + 1.6
    dur = t_hero + 2.0
    group, shots = {}, []
    for g, (frags, ya, yb, rs, ko, en) in enumerate(C_SHOTS):
        first = [o for n, o in parts.items() if frags[0] in n and o in moved]
        if not first:
            continue
        l, h = S.bounds([c for o in first for c in [o] + S.children(o)], prod.matrix_world)
        for n, o in parts.items():
            if o in moved and any(f in n for f in frags):
                group[o] = len(shots)
        s = C_T0 + len(shots) * C_SHOT
        shots.append({'t': s, 'piv': (l + h) / 2, 'off': moved[first[0]], 'r': (h - l).length / 2 * rs, 'ya': ya - C_YAW, 'yb': yb - C_YAW,
                      'ye': 360.0 * round((yb - C_YAW) / 360.0), 'ko': ko, 'en': en})

    def amount(o, t):       # 분해 정도: 0 = 제자리, 1 = 다 벌어짐(순간 분해는 살짝 넘쳤다 돌아온다)
        if t < t_re:
            u = min(1.0, max(0.0, (t - C_T_BURST) / C_BURST)) - 1
            return 1 + 2.2 * u ** 3 + 1.2 * u ** 2
        a = t_re + 0.9 * rank[round(moved[o].length, 6)] / max(1, len(rank))
        return 1 - ease(t, a, a + 0.7)

    def place(t):
        r3 = prod.matrix_world.to_3x3().inverted()
        for o, off in moved.items():
            m = Matrix.Translation(off * amount(o, t))
            g = group.get(o)
            if g is not None:
                sh = shots[g]
                tau = t - sh['t']
                up = ease(tau, 0, 0.6) * (1 - ease(tau, C_SHOT, C_SHOT + 0.6))
                phi = sh['ya'] * ease(tau, 0, 0.6) + (sh['yb'] - sh['ya']) * ease(tau, 0.5, C_SHOT - 0.1) + (sh['ye'] - sh['yb']) * ease(tau, C_SHOT, C_SHOT + 0.6)
                if up > 0 or phi % 360:
                    p = sh['piv'] + sh['off'] * amount(o, t)
                    m = Matrix.Translation(r3 @ (C_LIFT * up) + p) @ Matrix.Rotation(-math.radians(phi), 4, 'Y') @ Matrix.Translation(-p) @ m
            o.matrix_basis = pinv[o].inverted() @ m @ pinv[o] @ base[o]

    place(C_T0)
    bpy.context.view_layer.update()
    el_, eh_ = S.bounds([c for o in parts.values() if o not in S.OWN_BRACKET for c in [o] + S.children(o)], prod.matrix_world)
    pc = (S.PL + S.PH) / 2
    rad = (S.PH - S.PL).length / 2
    wide = {'yaw': C_YAW, 'el': 16, 'az': 0, 'p': (el_ + eh_) / 2, 'w': 0, 'r': (eh_.z - el_.z) / 2 * math.sin(math.radians(-C_YAW)) * 9 / 16 * 1.12, 'k': 1.0, 'fb': 0.0}
    keys = [(0.0, {'yaw': -18, 'el': 22, 'az': 0, 'p': pc, 'w': 0, 'r': rad * 1.05, 'k': 1.0, 'fb': 0.35}, ''),
            (C_T_BURST, {'yaw': -30, 'el': 22, 'az': 0, 'p': pc, 'w': 0, 'r': rad * 1.05, 'k': 1.0, 'fb': 0.35}, 'drift'),
            (C_T_BURST + C_BURST, wide, 'move'), (C_T0, wide, 'drift')]
    for i, sh in enumerate(shots):
        az = 22 if i % 2 else -22
        q = {'yaw': C_YAW, 'el': 14, 'az': az, 'p': sh['piv'] + sh['off'], 'w': 1, 'r': sh['r'] * 1.2, 'k': 1.6, 'fb': 0.25}
        keys += [(sh['t'] + 0.7, q, 'move'), (sh['t'] + C_SHOT, dict(q, az=-az, r=sh['r'] * 0.95), 'drift')]
    keys += [(t_hero, {'yaw': -26, 'el': 20, 'az': 0, 'p': pc, 'w': 0, 'r': rad * 1.05, 'k': 1.0, 'fb': 0.35}, 'move'),
             (dur, {'yaw': -14, 'el': 12, 'az': 0, 'p': pc, 'w': 0, 'r': rad * 0.92, 'k': 1.0, 'fb': 0.35}, 'drift')]

    def pose(t):
        place(t)
        aim(S, track(keys, t), C_LIFT)

    def done():
        for o in moved:
            o.matrix_basis = base[o]

    caps = [{'t0': sh['t'] + 0.5, 't1': sh['t'] + C_SHOT, 'ko': sh['ko'], 'en': sh['en']} for sh in shots]
    return {'dur': dur, 'pose': pose, 'done': done, 'animated': list(moved), 'blur': [(C_T_BURST, C_T0 - 0.1), (t_re, t_hero + 0.1)],
            'meta': {'captions': caps, 'title': {'t0': t_hero + 0.3, 't1': dur, 'text': 'OpenHW'}, 'yaw_line': C_YAW, 'lift_mm': [round(v / MM, 1) for v in C_LIFT],
                     'offsets_mm': {k: v for k, v in C_OFF}, 'shots': [{'t': sh['t'], 'spin_deg': [sh['ya'] + C_YAW, sh['yb'] + C_YAW]} for sh in shots]}}


# ---------------- section-open (O-129 ③) ----------------
def section_open(S):
    dur = 6.0
    enc = [o for n, o in S.parts.items() if o.type == 'MESH' and not n.startswith('BOARD_') and not any(n.startswith(p) for p in S.X.DESIGN_INTERNALS) and o not in S.OWN_BRACKET]
    pc = (S.PL + S.PH) / 2
    rad = (S.PH - S.PL).length / 2
    x_hi = S.PH.x + 0.0005
    q0 = {'yaw': 32, 'el': 22, 'az': 0, 'p': pc, 'w': 0, 'r': rad * 1.05, 'k': 1.0, 'fb': 0.35}
    keys = [(0.0, q0, ''), (4.2, dict(q0, yaw=74, el=13, r=rad * 1.0), 'move'), (dur, dict(q0, yaw=82, el=12, r=rad * 0.92), 'drift')]
    info = {}

    def bevel(on):      # 잘린 메시에 베벨을 걸면 큰 쉘에서 꼭짓점이 터진다 — 자르는 부품은 영상 내내 끈다(잘리는 순간 모서리가 바뀌지 않게)
        for o in enc:
            if o.modifiers.get('BEVEL'):
                o.modifiers['BEVEL'].show_render = o.modifiers['BEVEL'].show_viewport = on

    def pose(t):
        S.section(False)
        bevel(False)
        x0 = lerp(x_hi, 0.0, ease(t, 0.5, 3.8))
        if x0 < x_hi:
            S.section(True, x0, enc)
            info['section_check'] = dict(S.REPORT['section_check'], x0_mm=round(x0 / MM, 2))
        aim(S, track(keys, t))

    def done():
        S.section(False)
        bevel(True)

    return {'dur': dur, 'pose': pose, 'done': done, 'animated': [], 'blur': [],
            'meta': {'cut_parts': [o.name for o in enc], 'plane': 'x = %.1f → 0 mm (0.5 ~ 3.8 s)' % (x_hi / MM), 'info': info}}


# ---------------- hero-dolly (O-129 ④) ----------------
def hero_dolly(S):
    dur = 6.0
    pc = (S.PL + S.PH) / 2
    top = Vector((pc.x, S.PH.y - 0.012, pc.z - 0.006))
    lp = [o for n, o in S.parts.items() if 'LIGHT_PIPE' in n]
    if lp:      # 상태 LED(광 파이프 윗면) 쪽으로 반쯤 당긴다
        l, h = S.bounds(lp, S.prod.matrix_world)
        top = top.lerp(Vector(((l.x + h.x) / 2, h.y, (l.z + h.z) / 2)), 0.5)
    front = Vector((0, 0, S.PH.z - 0.004))
    if S.LENS_OBJS:
        l, h = S.bounds(S.LENS_OBJS, S.prod.matrix_world)
        front = Vector(((l.x + h.x) / 2, (l.y + h.y) / 2, S.PH.z - 0.004))
    a = {'yaw': 148.0, 'el': 14.0, 'p': Vector((pc.x, pc.y, S.PL.z + 0.012)), 'r': 0.050}       # 뒤: 방열 핀
    b = {'yaw': 92.0, 'el': 32.0, 'p': top, 'r': 0.058}                                         # 위: 상태 LED
    c = {'yaw': 26.0, 'el': 8.0, 'p': front, 'r': 0.034}                                        # 앞: 렌즈

    def pose(t):
        u = t / dur
        u = 0.3 * u + 0.7 * u * u * (3 - 2 * u)
        aim(S, dict({k: quad(a[k], b[k], c[k], u) for k in a}, az=0, w=0, k=1.3, fb=0.2))

    return {'dur': dur, 'pose': pose, 'done': lambda: None, 'animated': [], 'blur': [],
            'meta': {'path': [{k: ([round(x / MM, 1) for x in v] if isinstance(v, Vector) else v) for k, v in q.items()} for q in (a, b, c)]}}


# ---------------- bracket (O-129 ⑤) ----------------
def bracket(S):
    dur = 6.0
    prod = S.prod
    S.accessories(True)
    bpy.context.view_layer.update()

    def box(frag):
        objs = [o for o in S.OWN_BRACKET if frag in o.name]
        assert objs, '브래킷 부품이 없다: ' + frag
        l, h = S.bounds(objs, prod.matrix_world)
        return objs, (l + h) / 2

    arm, _ = box('ARM')
    pan, pp = box('PAN')            # 팬 축: PAN 기둥 중심을 지나는 제품 Y(세로) 축
    _, pt = box('PIN')              # 틸트 축: PIN 중심을 지나는 제품 X(가로) 축
    moving = [o for o in prod.children if o not in arm]
    base = {o: o.matrix_basis.copy() for o in moving}
    pinv = {o: o.matrix_parent_inverse.copy() for o in moving}
    l, h = S.bounds([o for o in S.children(prod) if o.type == 'MESH'])
    c0, r0 = (l + h) / 2, (h - l).length / 2
    l, h = S.bounds([o for o in S.children(prod) if o.type == 'MESH'], prod.matrix_world)
    q = {'yaw': 0, 'el': -10, 'az': 36, 'p': (l + h) / 2, 'w': 0, 'r': r0 * 0.84, 'k': 1.0, 'fb': 0.35}
    aim(S, q, light=(c0, r0))
    wall0 = S.wall.location.copy()
    amp = (28.0, 12.0)              # 팬 · 틸트 진폭(°) — 보기용 값(설계 가동 범위가 아니다)

    def pose(t):
        u = t / dur                 # 한 바퀴 돌아 처음 자세로 온다(GIF 가 이어지게)
        a, b = math.radians(amp[0] * math.sin(2 * math.pi * u)), math.radians(amp[1] * math.sin(4 * math.pi * u))
        rp = Matrix.Translation(pp) @ Matrix.Rotation(a, 4, 'Y') @ Matrix.Translation(-pp)
        rt = Matrix.Translation(pt) @ Matrix.Rotation(b, 4, 'X') @ Matrix.Translation(-pt)
        for o in moving:
            o.matrix_basis = pinv[o].inverted() @ (rp if o in pan else rp @ rt) @ pinv[o] @ base[o]
        aim(S, q, light=(c0, r0))
        S.wall.location = wall0     # 벽은 움직이지 않는다(stage 가 프레임마다 범위로 다시 잡는 것을 되돌림)

    def done():
        for o in moving:
            o.matrix_basis = base[o]
        S.accessories(False)

    return {'dur': dur, 'pose': pose, 'done': done, 'animated': [], 'blur': [],
            'meta': {'pan_axis_mm': [round(pp.x / MM, 2), round(pp.z / MM, 2)], 'tilt_axis_mm': [round(pt.y / MM, 2), round(pt.z / MM, 2)], 'amplitude_deg': amp}}


CLIPS = {'concept-explode': concept, 'section-open': section_open, 'hero-dolly': hero_dolly, 'bracket': bracket}


def run(S, names):
    scn = bpy.context.scene
    root = S.arg('--video-dir') or os.path.join(S.OUT, 'video')
    part, nparts = (int(v) for v in (S.arg('--video-part') or '0/1').split('/'))
    fps = S.VFPS
    scn.render.fps = fps
    scn.render.motion_blur_shutter = 0.5
    out = {}
    for name in names:
        clip = CLIPS[name](S)
        n = round(clip['dur'] * fps)
        d = os.path.join(root, name, 'frames')
        os.makedirs(d, exist_ok=True)
        if S.LENS_FILL:
            S.LENS_FILL.hide_render = name != 'hero-dolly'
        anim = clip['animated'] + [S.tt, S.cam] if clip['blur'] else []
        if anim:        # 모션 블러는 프레임 사이 움직임(키프레임)이 있어야 한다 — 프레임마다 자세를 키로 찍어 둔다
            prev = None
            for i in range(n):
                clip['pose'](i / fps)
                if prev:
                    S.cam.rotation_euler.make_compatible(prev)
                prev = S.cam.rotation_euler.copy()
                for o in anim:
                    o.keyframe_insert('location', frame=i + 1)
                    o.keyframe_insert('rotation_euler', frame=i + 1)
        new = skip = 0
        for i in range(n):
            f = os.path.join(d, 'frame_%04d.png' % (i + 1))
            if i % nparts != part:
                continue
            if os.path.exists(f) and os.path.getsize(f) > 0:
                skip += 1
                continue
            t = i / fps
            if anim:
                scn.frame_set(i + 1)
            clip['pose'](t)
            scn.render.use_motion_blur = any(a <= t <= b for a, b in clip['blur'])
            S.shot(f, S.TT_RES)
            new += 1
        scn.render.use_motion_blur = False
        for o in anim:
            o.animation_data_clear()
        clip['done']()
        meta = dict(clip['meta'], name=name, fps=fps, frames=n, duration_s=clip['dur'], res=S.TT_RES, samples=S.SAMPLES, lens_mm=LENS,
                    motion_blur_s=clip['blur'], shutter=0.5 if clip['blur'] else None)
        if part == 0:
            json.dump(meta, open(os.path.join(root, name, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        out[name] = {'frames': n, 'new': new, 'skipped': skip, 'part': '%d/%d' % (part, nparts)}
    return out
