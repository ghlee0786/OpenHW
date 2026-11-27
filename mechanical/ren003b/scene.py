"""REN-003b 2) 제품 렌더 장면 (Blender 5.2, bpy, 헤드리스) — O-125 2단계 사실적 렌더. 메시 폴더만 바꾸면 같은 장면을 다시 만든다.

  blender -b --factory-startup --python-exit-code 1 --python mechanical/ren003b/scene.py -- --mesh <메시 폴더> --out <출력 폴더>
      [--cuts hero,front,rear,exploded,section,inuse] [--turntable N] [--engine cycles|eevee] [--res 3840x2160] [--tt-res 1920x1080]
      [--samples 256] [--hdri <.hdr>] [--hdri-strength 0.7] [--hdri-rot 110] [--exposure 0.0] [--fstop 8] [--bevel 0.3] [--label OpenHW]
      [--z-carrier -9.6] [--z-front 9.6] [--frame-radius mm] [--override 이름조각=재질,…] [--save-blend <새 .blend>]

- 입력 = prep.py 가 만든 폴더: board_carrier.glb · board_front.glb · <부품>.stl(mm) · index.json
- 재질 = mechanical/ren003/materials.py MATS 전부(읽기만) + materials_ext.py(새 재질 · 미세 질감).
    부품: 이름 → NAME_RULES → (없으면) EXT_NAME_RULES. 어느 쪽에도 없으면 「재질 빠짐」(기본 'plastic' 으로 렌더는 계속).
    보드: GLB 재질 원값 + 모델 이름 + 참조 번호 → body_key(). 'keep'(못 가른 색)은 빠짐.
- 메시: 겹친 꼭짓점 합침 → 30° 넘는 모서리만 날카롭게 → 베벨(--bevel mm, 3단) → Weighted Normal.
- 조명: HDRI(--hdri, CC0) 월드 + KEY · RIM 면광. 무한 배경(바닥이 곡면으로 벽이 됨) 위에 제품을 세운다.
    스모크 앞유리가 있으면 거울 반사 방향에 띠 조명(GLASS_STRIP, 반사에만 잡힘)과 유리 안쪽 보조광 2개를 더한다.
- 카메라: 85~100 mm, 피사계 심도(--fstop), 3분할 구도(hero · inuse 는 주제를 3분할선에). 색 관리 AgX, 노출 --exposure.
- 컷: hero(앞 3/4) · front(정면) · rear(뒤 3/4, 포트 · 방열) · exploded(분해) · section(단면) · inuse(벽 브래킷) + 턴테이블(제품만 돈다).
- 출력: <out>/stills/<컷>.png · <out>/turntable/frame_0001.png …(있는 프레임은 건너뜀) · <out>/scene_report.json
- 좌표: 제품 +Y 위 · +Z 앞(광축). 서 있는 자세 = PRODUCT 를 X 90° (제품 +Y → 월드 +Z, 제품 앞 +Z → 월드 −Y = 카메라 쪽).
종료 코드: 0 = 렌더 끝(판정은 run.py 가 scene_report.json 으로)."""
import hashlib
import json
import math
import os
import re
import sys

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import materials_ext as X  # noqa: E402

MESH = os.path.abspath(arg('--mesh'))
OUT = os.path.abspath(arg('--out'))
CUTS = [c for c in arg('--cuts', 'hero,front,rear,exploded,section,inuse').split(',') if c]
TT = int(arg('--turntable', '0'))
ENGINE = arg('--engine', 'cycles')
RES = [int(v) for v in arg('--res', '3840x2160').split('x')]
TT_RES = [int(v) for v in arg('--tt-res', '1920x1080').split('x')]
SAMPLES = int(arg('--samples', '256'))
HDRI = arg('--hdri')
HDRI_STRENGTH = float(arg('--hdri-strength', '0.7'))
EXPOSURE = float(arg('--exposure', '0.0'))
FSTOP = float(arg('--fstop', '8'))
BEVEL = float(arg('--bevel', '0.3'))
LABEL = arg('--label', 'OpenHW')
OVERRIDE = [kv.split('=') for kv in arg('--override', '').split(',') if '=' in kv]     # 이름 조각=재질 — 모든 규칙보다 먼저(비교용 색 바꾸기)
FRAME_R = float(arg('--frame-radius', '0'))      # mm — 0 이 아니면 카메라 거리 · 조명을 이 반지름에 맞춘다(시안끼리 같은 카메라 · 조명)
MM = 0.001


def default_z(key, fallback):
    """판 아랫면 z (mm): mechanical/m003/params.csv 의 유도값(읽기만). 없으면 fallback."""
    p = os.path.join(HERE, '..', 'm003', 'params.csv')
    if os.path.exists(p):
        for ln in open(p, encoding='utf-8'):
            c = ln.strip().split(',')
            if c[0] == key:
                return float(c[2])
    return fallback


Z_CARRIER = float(arg('--z-carrier', default_z('z_car_bot', -9.6)))
Z_FRONT = float(arg('--z-front', default_z('z_fr_bot', 9.6)))

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---------------- 재질 ----------------
T = {}
exec(open(os.path.join(HERE, '..', 'ren003', 'materials.py'), encoding='utf-8').read(), T)


def mat(name, v):
    m = bpy.data.materials.new(name)
    if hasattr(m, 'use_nodes') and not m.node_tree:
        m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*v['rgb'], 1)
    p.inputs['Metallic'].default_value = v.get('metal', 0.0)
    p.inputs['Roughness'].default_value = v.get('rough', 0.5)
    p.inputs['Transmission Weight'].default_value = v.get('trans', 0.0)
    p.inputs['IOR'].default_value = v.get('ior', 1.45)
    p.inputs['Specular IOR Level'].default_value = v.get('spec', 0.5)
    p.inputs['Coat Weight'].default_value = v.get('coat', 0.0)
    if v.get('emit'):
        p.inputs['Emission Color'].default_value = (*v['emit'][0], 1)
        p.inputs['Emission Strength'].default_value = v['emit'][1]
    if v.get('trans', 0.0) > 0 and hasattr(m, 'use_raytrace_refraction'):
        m.use_raytrace_refraction = True
    return m


M = {k: mat('m_' + k, v) for k, v in T['MATS'].items()}
N_BASE = len(M)
M.update({k: mat('x_' + k, v) for k, v in X.EXT_MATS.items()})
LOOKS = {k: X.detail(bpy, M[k], kind, X.EXT_MATS.get(k)) for k, kind in X.LOOK.items() if k in M}
WIRES = ['wire_k', 'wire_r', 'wire_y', 'wire_y', 'wire_r', 'wire_k']
REPORT = {'mats_defined': N_BASE, 'mats_ext': len(X.EXT_MATS), 'looks': LOOKS, 'enclosure': [], 'boards': {}, 'missing': [], 'used': {}, 'cuts': {}}


def use(k, n=1):
    REPORT['used'][k] = REPORT['used'].get(k, 0) + n


def refine(o, bevel_mm):
    """겹친 꼭짓점 합침 · 날카로운 모서리 표시 · 베벨 · Weighted Normal. 반환: 베벨 넣었는가."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    lim = math.radians(30)
    for e in bm.edges:
        e.smooth = not (len(e.link_faces) == 2 and e.calc_face_angle(0.0) > lim) and len(e.link_faces) == 2
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(o.data)
    bm.free()
    dims = sorted(o.dimensions)
    beveled = False
    if bevel_mm > 0 and dims[0] > 6 * bevel_mm * MM and not any(s in o.name for s in X.BEVEL_SKIP):
        bv = o.modifiers.new('BEVEL', 'BEVEL')
        bv.width = bevel_mm * MM
        bv.segments = 3
        bv.limit_method = 'ANGLE'
        bv.angle_limit = lim
        bv.harden_normals = True
        bv.miter_outer = 'MITER_ARC'
        beveled = True
    wn = o.modifiers.new('WN', 'WEIGHTED_NORMAL')
    wn.keep_sharp = True
    return beveled


# ---------------- 가져오기 ----------------
prod = bpy.data.objects.new('PRODUCT', None)
scn.collection.objects.link(prod)
index = json.load(open(os.path.join(MESH, 'index.json'), encoding='utf-8'))
parts = {}
OWN_BRACKET = []
for it in index['items']:
    if it['kind'] != 'enclosure':
        continue
    bpy.ops.wm.stl_import(filepath=os.path.join(MESH, it['file']), global_scale=MM)
    o = bpy.context.selected_objects[0]
    name = it['file'][:-4]
    o.name = name
    o.parent = prod
    mk = next((v for key, v in OVERRIDE if key in name), None) or next((v for key, v in T['NAME_RULES'] if key in name), None)
    if mk is None and name.startswith('HARNESS_GH6P__'):     # 보충 규칙(REN-002 scene.py 와 같음): 하니스 6선 색
        mk = WIRES[int(name.split('__')[1]) % len(WIRES)]
    if mk is None:
        mk = next((v for key, v in X.EXT_NAME_RULES if key in name), None)
    if mk is None:
        REPORT['missing'].append({'where': 'enclosure', 'name': name, 'why': 'NAME_RULES · EXT_NAME_RULES 에 없음'})
        mk = 'plastic'
    o.data.materials.clear()
    o.data.materials.append(M[mk])
    bev = refine(o, BEVEL)
    if 'BRACKET' in name:       # 시안의 브래킷 부품은 사용 장면에서만 보인다(시안끼리 히어로가 비교되게) — 내장 브래킷 소품은 그때 쓰지 않는다
        o.hide_render = True
        OWN_BRACKET.append(o)
    parts[name] = o
    REPORT['enclosure'].append({'name': name, 'material': mk, 'triangles': len(o.data.polygons), 'bevel': bev, 'deflection_mm': it.get('deflection_mm')})
lens = [o for n, o in parts.items() if n.startswith('LENS_CIL093')]
if lens:    # 보충 규칙(REN-002 와 같음): 렌즈 조각 가운데 맨 앞(+Z) 것은 유리
    fr = max(lens, key=lambda o: max(v.co.z for v in o.data.vertices))
    fr.data.materials[0] = M['glass']
    next(e for e in REPORT['enclosure'] if e['name'] == fr.name)['material'] = 'glass'
for e in REPORT['enclosure']:
    use(e['material'])

for b, z in (('carrier', Z_CARRIER), ('front', Z_FRONT)):
    f = os.path.join(MESH, 'board_%s.glb' % b)
    before = set(bpy.data.objects)
    GM = T['glb_materials'](f)
    bpy.ops.import_scene.gltf(filepath=f)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new('BOARD_' + b.upper(), None)
    scn.collection.objects.link(root)
    cnt = {}
    for o in new:
        if o.parent is None:
            o.parent = root
        if o.type != 'MESH':
            continue
        model = re.sub(r'\.\d+$', '', o.data.name)
        ref = re.sub(r'\.\d+$', '', o.parent.name) if o.parent else ''
        if not o.material_slots:
            REPORT['missing'].append({'where': b, 'name': o.name, 'why': '재질 칸 없음'})
        for s in o.material_slots:
            src = GM.get(re.sub(r'\.\d+$', '', s.material.name)) if s.material else None
            mk = T['body_key'](src[0], src[1], src[2], model=model, ref=ref, board=b) if src else None
            if mk in M:
                s.material = M[mk]
                cnt[mk] = cnt.get(mk, 0) + 1
                use(mk)
            else:
                REPORT['missing'].append({'where': b, 'name': o.name, 'model': model, 'ref': ref,
                                          'why': 'GLB 재질 못 읽음' if not src else '규칙이 못 가른 색 ' + str([round(c, 3) for c in src[0]])})
    root.location = (0, 0, z * MM)
    root.parent = prod
    parts['BOARD_' + b.upper()] = root
    REPORT['boards'][b] = {'meshes': sum(1 for o in new if o.type == 'MESH'), 'slots': cnt, 'z_mm': z}

prod.rotation_euler = (math.radians(90), 0, 0)        # 서 있는 자세


# ---------------- 범위 ----------------
def children(o):
    out = []
    for c in o.children:
        out.append(c)
        out += children(c)
    return out


def bounds(objs, space=None):
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH' or o.hide_render:
            continue
        mw = (space.inverted() @ o.matrix_world) if space else o.matrix_world
        for c in o.bound_box:
            w = mw @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


bpy.context.view_layer.update()
for n, o in parts.items():      # 제품 좌표(mm) 범위 — 보드가 외함 안에 있는지 run.py 가 본다
    l2, h2 = bounds([o] + children(o), prod.matrix_world)
    REPORT.setdefault('bbox_mm', {})[n] = [round(v / MM, 2) for v in (*l2, *h2)]
PL, PH = bounds(children(prod), prod.matrix_world)       # 제품 좌표 범위 (m)

# ---------------- 라벨 (실크 인쇄) ----------------
cover = parts.get('FRONT_COVER') or parts.get('HOUSING')
if LABEL and cover:
    cl, ch = bounds([cover], prod.matrix_world)
    cu = bpy.data.curves.new('LABEL', 'FONT')
    cu.body = LABEL
    cu.size = 2.0 * MM
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.extrude = 0.01 * MM
    lab = bpy.data.objects.new('LABEL', cu)
    scn.collection.objects.link(lab)
    lab.parent = prod
    lab.location = ((cl.x + ch.x) / 2, cl.y + 1.9 * MM, ch.z + 0.012 * MM)    # 앞면 아래 가장자리
    lab.data.materials.append(M['silk'])
    use('silk')
    REPORT['label'] = LABEL

# ---------------- 앞유리 안쪽 보조광 (렌더 전용) ----------------
# 스모크 앞유리(ir_glass)가 있으면 유리 바로 뒤 위 · 아래에 약한 점광 2개 — 렌즈 경통 · IR LED 가 은은히 비치게. 화면 · 반사에는 안 보인다.
GLASS = [o for n, o in parts.items() if o.type == 'MESH' and o.data.materials and o.data.materials[0] == M['ir_glass']]
if GLASS:
    gl, gh = bounds(GLASS, prod.matrix_world)
    for i, fy in enumerate((0.78, 0.22)):
        ld = bpy.data.lights.new('INSIDE_%d' % i, 'POINT')
        ld.energy = float(arg('--inside-w', '0.03'))
        ld.color = (1.0, 0.96, 0.9)
        ld.shadow_soft_size = 0.004
        lo_ = bpy.data.objects.new('INSIDE_%d' % i, ld)
        scn.collection.objects.link(lo_)
        lo_.parent = prod
        lo_.location = ((gl.x + gh.x) / 2, gl.y + (gh.y - gl.y) * fy, gl.z - 0.004)
        lo_.visible_camera = False
        lo_.visible_glossy = False
    REPORT['inside_lights'] = 2

# ---------------- 사용 장면 소품: 벽 브래킷 (제품 좌표 mm, PRODUCT 자식, 기본 숨김) ----------------
ACC = []


def p_box(name, x0, x1, y0, y1, z0, z1, mk):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = name
    o.scale = ((x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM)
    o.location = ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, (z0 + z1) / 2 * MM)
    return p_fin(o, mk)


def p_cyl(name, a, b, r, mk):
    a, b = Vector(a) * MM, Vector(b) * MM
    bpy.ops.mesh.primitive_cylinder_add(radius=r * MM, depth=(b - a).length, vertices=64)
    o = bpy.context.object
    o.name = name
    o.location = (a + b) / 2
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return p_fin(o, mk)


def p_fin(o, mk):
    o.parent = prod
    o.data.materials.append(M[mk])
    bv = o.modifiers.new('BEVEL', 'BEVEL')
    bv.width = 0.6 * MM
    bv.segments = 3
    bv.harden_normals = True
    for f in o.data.polygons:
        f.use_smooth = True
    o.modifiers.new('WN', 'WEIGHTED_NORMAL')
    o.hide_render = True
    ACC.append(o)
    return o


ZB = PL.z / MM                   # 제품 뒷면 z (mm)
WALL_GAP = 46.0                  # 뒷면에서 벽까지 (mm)
MX, MY = 0.0, -4.0               # 뒷면 장착 자리 (REN-002 와 같은 1/4" 자리)
p_cyl('ACC_BRACKET_BOSS', (MX, MY, ZB), (MX, MY, ZB - 6), 9.0, 'bracket')
p_cyl('ACC_BRACKET_BALL', (MX, MY, ZB - 6), (MX, MY, ZB - 16), 6.5, 'steel')
p_cyl('ACC_BRACKET_ARM', (MX, MY, ZB - 14), (MX, MY, ZB - WALL_GAP + 4), 5.0, 'bracket')
p_box('ACC_BRACKET_PLATE', MX - 22, MX + 22, MY - 30, MY + 30, ZB - WALL_GAP, ZB - WALL_GAP + 4, 'bracket')
for sx, sy in ((-15, -22), (15, -22), (-15, 22), (15, 22)):
    p_cyl('ACC_BRACKET_SCREW', (MX + sx, MY + sy, ZB - WALL_GAP + 4), (MX + sx, MY + sy, ZB - WALL_GAP + 5.2), 2.6, 'steel')

# ---------------- 턴테이블 축 · 월드 · 배경 · 조명 ----------------
bpy.context.view_layer.update()
PROD_OBJS = [o for o in children(prod) if o.type in ('MESH', 'FONT') and not o.name.startswith('ACC_')]
lo, hi = bounds([o for o in PROD_OBJS if o.type == 'MESH'])
C = (lo + hi) / 2
RAD = (hi - lo).length / 2
tt = bpy.data.objects.new('TT', None)
scn.collection.objects.link(tt)
tt.location = (C.x, C.y, 0)
bpy.context.view_layer.update()
mw0 = prod.matrix_world.copy()
prod.parent = tt
prod.matrix_world = mw0

world = bpy.data.worlds.new('W')
scn.world = world
if hasattr(world, 'use_nodes') and not world.node_tree:
    world.use_nodes = True
wn = world.node_tree
bg = wn.nodes['Background']
bg.inputs['Strength'].default_value = HDRI_STRENGTH
if HDRI and os.path.exists(HDRI):
    env = wn.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(HDRI)
    mp = wn.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(float(arg('--hdri-rot', '110'))))
    tcw = wn.nodes.new('ShaderNodeTexCoord')
    wn.links.new(tcw.outputs['Generated'], mp.inputs['Vector'])
    wn.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    wn.links.new(env.outputs['Color'], bg.inputs['Color'])
    REPORT['hdri'] = {'file': os.path.basename(HDRI), 'sha256': hashlib.sha256(open(HDRI, 'rb').read()).hexdigest(), 'strength': HDRI_STRENGTH}
else:
    bg.inputs['Color'].default_value = (0.20, 0.205, 0.215, 1)
    bg.inputs['Strength'].default_value = 0.35
    REPORT['hdri'] = None


def cyclorama(name, mk, depth_front, depth_back, radius, height, width):
    """무한 배경: 바닥(−Y 쪽) → 1/4 원 → 벽(+Y 쪽). 원점 = 제품 자리 바닥."""
    prof = [(-depth_front, 0.0), (depth_back, 0.0)]
    for i in range(1, 25):
        a = math.radians(90 * i / 24)
        prof.append((depth_back + radius * math.sin(a), radius * (1 - math.cos(a))))
    prof.append((depth_back + radius, radius + height))
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for (y, z) in prof] for x in (-width / 2, width / 2)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    scn.collection.objects.link(o)
    o.data.materials.append(M[mk])
    return o


S = (FRAME_R * MM if FRAME_R else RAD) / 0.06          # 장면 크기를 제품 크기에 맞춤 (기준: 반지름 60 mm)
cyc = cyclorama('CYC', 'floor', 1.6 * S, 0.45 * S, 0.5 * S, 1.2 * S, 5.0 * S)
wall = cyclorama('WALL', 'wall', 2.0 * S, 0.0, 0.004 * S, 2.5 * S, 6.0 * S)     # 사용 장면: 바닥 없이 벽만 보이게 쓴다
wall.hide_render = True
LIGHTS = {}


def area(name, energy, size, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA')
    l.energy = energy
    l.size = size
    l.color = color
    o = bpy.data.objects.new(name, l)
    scn.collection.objects.link(o)
    LIGHTS[name] = o
    return o


area('KEY', 14 * S * S, 0.35 * S, (1, 0.97, 0.93))
area('RIM', 10 * S * S, 0.22 * S)
# 유리 하이라이트용 띠 조명: 앞유리의 거울 반사 방향에 두는 긴 면광. 반사(glossy)에만 잡히고 확산 조명에는 기여하지 않는다 — 유리가 유리로 읽히게.
STRIP_D = 0.55 * S                                  # 유리에서 띠 조명까지 (m)
STRIP_W = 2 * STRIP_D * math.tan(math.radians(0.7))  # 유리에서 본 띠 폭 약 1.4° — 유리(지름 약 3~4°) 위에 띠로 걸친다
STRIP = area('GLASS_STRIP', float(arg('--strip-radiance', '45')) * math.pi * STRIP_W * (0.9 * S) * 4, 0.5 * S)
STRIP.data.shape = 'RECTANGLE'
STRIP.data.size = STRIP_W
STRIP.data.size_y = 0.9 * S
STRIP.visible_diffuse = False
STRIP.visible_camera = False
STRIP.hide_render = True
if GLASS:       # 유리에만 비친다(빛 연결) — 본체 플라스틱 · 알루미늄의 밝기는 그대로
    gcol = bpy.data.collections.new('GLASS_ONLY')
    for o_ in GLASS:
        gcol.objects.link(o_)
    STRIP.light_linking.receiver_collection = gcol
    STRIP.light_linking.blocker_collection = gcol      # 바닥 · 차양에 가리지 않는다(카메라가 내려다보면 거울 방향이 바닥 아래다) — 스튜디오 반사 카드 구실

# ---------------- 카메라 ----------------
cd = bpy.data.cameras.new('CAM')
cam = bpy.data.objects.new('CAM', cd)
scn.collection.objects.link(cam)
scn.camera = cam
cd.clip_start = 0.005
cd.dof.use_dof = True
cd.dof.aperture_fstop = FSTOP


def stage(yaw, el, lens, fit, thirds=0.0, az=0.0, target=None, res=None, focus_bias=0.35):
    """제품을 yaw° 돌리고(양수 = 제품 +X 면이 카메라 쪽) 카메라를 정면(−Y)에서 방위 az° · 고도 el° 로 둔다. 바닥 · 조명도 다시 맞춘다."""
    res = res or RES
    tt.rotation_euler = (0, 0, math.radians(-yaw))
    bpy.context.view_layer.update()
    objs = [o for o in children(prod) if o.type == 'MESH']
    l, h = bounds(objs)
    c = Vector(target) if target else (l + h) / 2
    r = FRAME_R * MM if FRAME_R else (h - l).length / 2
    cyc.location = (c.x, c.y, l.z - 0.0002)
    wall.location = (c.x, h.y, l.z - 1.2 * (r / 0.06))      # 사용 장면: 벽 = 브래킷 판 뒷면(+Y 끝), 바닥은 화면 밖 아래
    cd.lens = lens
    fov = 2 * math.atan(min(cd.sensor_width, cd.sensor_width * res[1] / res[0]) / 2 / lens)
    d = r / math.sin(fov / 2) * fit
    e, a_ = math.radians(el), math.radians(az)
    cam.location = c + Vector((d * math.sin(a_) * math.cos(e), -d * math.cos(a_) * math.cos(e), d * math.sin(e)))
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cd.shift_x = thirds / 6.0                 # 주제를 3분할선으로 (센서 폭의 1/6)
    cd.dof.focus_distance = d - r * focus_bias  # 초점은 제품 앞쪽에
    for name, off in (('KEY', (-0.42, -0.50, 0.55)), ('RIM', (0.38, 0.35, 0.50))):
        o = LIGHTS[name]
        o.location = c + Vector(off) * (r / 0.06)
        o.rotation_euler = (c - o.location).to_track_quat('-Z', 'Y').to_euler()
    STRIP.hide_render = not GLASS
    if GLASS:       # 유리 중심에서 카메라 쪽 방향을 유리 법선으로 거울 반사한 곳 + 옆으로 0.5° 비켜서(하이라이트 띠가 유리 한쪽에 걸리게)
        gl_, gh_ = bounds(GLASS)
        gc = (gl_ + gh_) / 2
        nrm = (prod.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
        v = (cam.location - gc).normalized()
        rfl = (2 * nrm.dot(v) * nrm - v).normalized()
        side = rfl.cross(Vector((0, 0, 1))).normalized()
        dirn = (rfl + side * math.tan(math.radians(0.5))).normalized()
        STRIP.location = gc + dirn * STRIP_D
        STRIP.rotation_euler = (gc - STRIP.location).to_track_quat('-Z', 'Y').to_euler()
    return c, r, d


EXPLODE = [('FRONT_COVER', (0, 0, 46)), ('PMMA', (0, 0, 70)), ('IR_GLASS', (0, 0, 70)), ('FOAM', (0, 0, 24)), ('LENS_CIL093', (0, 0, 18)),
           ('HS_EXTRUSION', (46, 0, 0)), ('HS_PEDESTAL', (26, 0, 0)), ('GAP_PAD', (15, 0, 0)), ('HW_M16', (0, 0, 84)),
           ('HOUSING', (0, 0, -62)), ('BOARD_CARRIER', (0, 0, -34)), ('BOARD_FRONT', (0, 0, 6)), ('HW_M25', (0, 0, -74))]   # 제품 좌표 mm


def explode(on):
    for n, o in parts.items():
        v = next((v for key, v in EXPLODE if key in n), None)
        if v is None:
            continue
        if o.get('base_loc') is None:
            o['base_loc'] = list(o.location)
        o.location = Vector(o['base_loc']) + (Vector(v) * MM if on else Vector((0, 0, 0)))
    if 'LABEL' in bpy.data.objects:
        bpy.data.objects['LABEL'].hide_render = on


def section(on):
    """제품 좌표 x > 0 쪽 절반을 잘라 낸다(불리언). 단면 재질은 그 부품 재질."""
    if on and 'CUTTER' not in bpy.data.objects:
        bpy.ops.mesh.primitive_cube_add(size=1)
        cu = bpy.context.object
        cu.name = 'CUTTER'
        cu.parent = prod
        cu.scale = (0.5, 0.5, 0.5)
        cu.location = (0.25, 0, 0)
        cu.hide_render = True
        cu.display_type = 'WIRE'
    n = 0
    for o in children(prod):
        if o.type != 'MESH' or o.name == 'CUTTER' or o.name.startswith('ACC_'):
            continue
        md = o.modifiers.get('CUT')
        if on and md is None:
            md = o.modifiers.new('CUT', 'BOOLEAN')
            md.operation = 'DIFFERENCE'
            md.object = bpy.data.objects['CUTTER']
            md.solver = 'EXACT'
            wnm = o.modifiers.get('WN')
            if wnm:     # 단면 뒤에 노멀 다시
                bpy.context.view_layer.objects.active = o
                bpy.ops.object.modifier_move_to_index(modifier='WN', index=len(o.modifiers) - 1)
        if md:
            md.show_render = on
            md.show_viewport = on
            n += on
    return n


def accessories(on):
    for o in (OWN_BRACKET or ACC):
        o.hide_render = not on
    cyc.hide_render = on
    wall.hide_render = not on


# ---------------- 렌더 설정 ----------------
if ENGINE == 'cycles':
    scn.render.engine = 'CYCLES'
    cp = bpy.context.preferences.addons['cycles'].preferences
    dev = 'CPU'
    for kind in ('OPTIX', 'CUDA'):
        try:
            cp.compute_device_type = kind
            cp.get_devices()
            if any(d.type == kind for d in cp.devices):
                for d in cp.devices:
                    d.use = d.type == kind
                dev = kind
                break
        except Exception:
            pass
    scn.cycles.device = 'GPU' if dev != 'CPU' else 'CPU'
    scn.cycles.samples = SAMPLES
    scn.cycles.use_adaptive_sampling = True
    scn.cycles.adaptive_threshold = 0.01
    scn.cycles.use_denoising = True
    try:
        scn.cycles.denoiser = 'OPTIX' if dev == 'OPTIX' else 'OPENIMAGEDENOISE'
    except Exception:
        pass
    scn.cycles.max_bounces = 12
    scn.cycles.transmission_bounces = 12
    scn.cycles.glossy_bounces = 8
    REPORT['device'] = dev
    REPORT['denoiser'] = scn.cycles.denoiser
else:
    scn.render.engine = 'BLENDER_EEVEE'
    scn.eevee.taa_render_samples = SAMPLES
    if hasattr(scn.eevee, 'use_raytracing'):
        scn.eevee.use_raytracing = True
    REPORT['device'] = 'EEVEE'
    REPORT['denoiser'] = None
scn.render.resolution_percentage = 100
scn.render.film_transparent = False
scn.render.image_settings.file_format = 'PNG'
scn.view_settings.view_transform = 'AgX'
scn.view_settings.look = 'AgX - Medium High Contrast'
scn.view_settings.exposure = EXPOSURE
REPORT.update(frame_radius_mm=FRAME_R or None, engine=scn.render.engine, res=RES, tt_res=TT_RES, samples=SAMPLES, fstop=FSTOP, exposure=EXPOSURE, bevel_mm=BEVEL,
              view_transform=scn.view_settings.view_transform, radius_mm=round(RAD / MM, 1), objects=len([o for o in PROD_OBJS if o.type == 'MESH']),
              beveled=sum(1 for e in REPORT['enclosure'] if e['bevel']), frames_requested=TT)

# (컷, 제품 yaw°, 고도°, 렌즈 mm, 여유, 3분할 이동, 카메라 방위°)
CUT_SPEC = {'hero': (34, 24, 90, 0.9 if not FRAME_R else 0.7, -0.18, 0), 'front': (0, 4, 100, 0.9, 0.0, 0), 'rear': (146, 18, 90, 0.92, -0.45, 0),
            'exploded': (-42, 20, 85, 0.82, 0.0, 0), 'section': (78, 12, 100, 0.9, 0.0, 0), 'inuse': (0, -12, 85, 1.0, 0.5, 36)}


def shot(path, res):
    scn.render.resolution_x, scn.render.resolution_y = res
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)


os.makedirs(os.path.join(OUT, 'stills'), exist_ok=True)
for name in CUTS:
    yaw, el, lens, fit, thirds, az = CUT_SPEC[name]
    explode(name == 'exploded')
    ncut = section(name == 'section')
    accessories(name == 'inuse')
    stage(yaw, el, lens, fit, thirds, az, res=RES)
    shot(os.path.join(OUT, 'stills', name + '.png'), RES)
    REPORT['cuts'][name] = {'res': RES, 'samples': SAMPLES, 'lens_mm': lens, 'fstop': FSTOP, 'yaw': yaw, 'elev': el, 'thirds': thirds,
                            'section_objects': ncut if name == 'section' else None}
explode(False)
section(False)
accessories(False)

if arg('--save-blend'):
    p = os.path.abspath(arg('--save-blend'))
    assert not os.path.exists(p), '이미 있는 .blend 는 덮어쓰지 않는다: ' + p
    stage(*CUT_SPEC['hero'], res=RES)
    bpy.ops.wm.save_as_mainfile(filepath=p, copy=True)

done = {'turntable_new': 0, 'turntable_skipped': 0}
if TT:
    os.makedirs(os.path.join(OUT, 'turntable'), exist_ok=True)
    yaw0, el, lens, fit = CUT_SPEC['hero'][:4]
    for i in range(TT):
        f = os.path.join(OUT, 'turntable', 'frame_%04d.png' % (i + 1))
        if os.path.exists(f) and os.path.getsize(f) > 0:      # 다시 돌리면 끝난 프레임은 건너뜀
            done['turntable_skipped'] += 1
            continue
        stage(yaw0 + 360.0 * i / TT, el, lens, 1.05, 0.0, res=TT_RES)
        # 턴테이블은 바닥 · 초점이 프레임마다 흔들리지 않게 제품 중심 기준으로 고정
        cyc.location = (C.x, C.y, lo.z - 0.0002)
        shot(f, TT_RES)
        done['turntable_new'] += 1
REPORT['done'] = done
REPORT['missing_count'] = len(REPORT['missing'])
json.dump(REPORT, open(os.path.join(OUT, 'scene_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('REN003B objects %d mats %d+%d used %d missing %d cuts %d frames_new %d frames_skip %d device %s' % (
    REPORT['objects'], N_BASE, len(X.EXT_MATS), len(REPORT['used']), len(REPORT['missing']), len(REPORT['cuts']),
    done['turntable_new'], done['turntable_skipped'], REPORT['device']))
