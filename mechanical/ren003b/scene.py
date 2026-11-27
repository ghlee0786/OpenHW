"""REN-003b 2) 제품 렌더 장면 (Blender 5.2, bpy, 헤드리스) — 메시 폴더만 바꾸면 같은 장면을 다시 만든다.

  blender -b --factory-startup --python mechanical/ren003b/scene.py -- --mesh <메시 폴더> --out <출력 폴더>
      [--mode stills|turntable|both] [--engine eevee|cycles] [--res 960x540] [--samples 32] [--frames 48]
      [--z-carrier -9.6] [--z-front 9.6] [--cams hero,rear,window] [--save-blend <새 .blend>]

- 입력 = prep.py 가 만든 폴더: board_carrier.glb · board_front.glb · <외함 부품>.stl(mm) · index.json
- 재질 = mechanical/ren003/materials.py 를 읽기만 한다(MATS 전부를 Principled 재질로 만든다).
    외함 부품: 파일 이름 → NAME_RULES (부분 일치, 앞쪽이 먼저). 규칙에 없는 이름은 「재질 빠짐」으로 센다(기본 'plastic' 을 입혀 렌더는 계속).
    보드: GLB 재질 원값(색 · 금속 · 알파) + 메시 이름(모델) + 부모 이름(참조 번호) → body_key(). 'keep'(규칙이 못 가른 색)은 빠짐으로 센다.
- 카메라 3개: hero(앞 3/4) · rear(뒤 3/4, 방열판 · 커넥터) · window(정면 가까이, 창 너머)
- 조명: 스튜디오 3점(KEY · FILL · RIM, 면광) + 바닥 + 회색 월드. 조명 · 카메라는 고정이고 턴테이블은 제품만 돈다.
- 출력: <out>/stills/<카메라>.png · <out>/turntable/frame_0001.png … (있는 프레임은 건너뜀) · <out>/scene_report.json
- 좌표: 제품 +Y 위 · +Z 앞(광축). 서 있는 자세 = PRODUCT 를 X 90° (제품 +Y → 월드 +Z).
종료 코드: 0 = 렌더 끝(재질 빠짐 수는 scene_report.json 에 — run.py 가 판정). 스크립트 오류를 종료 코드로 받으려면 blender 에 --python-exit-code 1 을 준다(run.py 가 준다)."""
import json
import math
import os
import re
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d


HERE = os.path.dirname(os.path.abspath(__file__))
MESH = os.path.abspath(arg('--mesh'))
OUT = os.path.abspath(arg('--out'))
MODE = arg('--mode', 'both')
ENGINE = arg('--engine', 'eevee')
RES = [int(v) for v in arg('--res', '960x540').split('x')]
SAMPLES = int(arg('--samples', '32'))
FRAMES = int(arg('--frames', '48'))
CAMS = arg('--cams', 'hero,rear,window').split(',')
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

# ---------------- 재질 (materials.py 읽기만) ----------------
T = {}
exec(open(os.path.join(HERE, '..', 'ren003', 'materials.py'), encoding='utf-8').read(), T)


def mat(name, v):
    m = bpy.data.materials.new(name)
    if hasattr(m, 'use_nodes') and not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*v['rgb'], 1)
    p.inputs['Metallic'].default_value = v.get('metal', 0.0)
    p.inputs['Roughness'].default_value = v.get('rough', 0.5)
    p.inputs['Transmission Weight'].default_value = v.get('trans', 0.0)
    p.inputs['IOR'].default_value = v.get('ior', 1.45)
    p.inputs['Specular IOR Level'].default_value = v.get('spec', 0.5)
    p.inputs['Coat Weight'].default_value = v.get('coat', 0.0)
    if v.get('trans', 0.0) > 0 and hasattr(m, 'use_raytrace_refraction'):
        m.use_raytrace_refraction = True          # EEVEE 굴절
    if v.get('bump'):   # FDM 층 결: 물결 무늬(객체 Z, 주기 mm) → 범프
        w = nt.nodes.new('ShaderNodeTexWave')
        w.wave_type = 'BANDS'
        w.bands_direction = 'Z'
        w.inputs['Scale'].default_value = 2 * math.pi / (10.0 * v['bump'][0] * MM)   # 객체 좌표 = m (STL 을 m 로 들임)
        bn = nt.nodes.new('ShaderNodeBump')
        bn.inputs['Strength'].default_value = v['bump'][1]
        bn.inputs['Distance'].default_value = 0.00002
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Object'], w.inputs['Vector'])
        nt.links.new(w.outputs['Fac'], bn.inputs['Height'])
        nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    return m


M = {k: mat('m_' + k, v) for k, v in T['MATS'].items()}
WIRES = ['wire_k', 'wire_r', 'wire_y', 'wire_y', 'wire_r', 'wire_k']
REPORT = {'mats_defined': len(M), 'enclosure': [], 'boards': {}, 'missing': [], 'used': {}}


def use(k, n=1):
    REPORT['used'][k] = REPORT['used'].get(k, 0) + n


# ---------------- 가져오기 ----------------
prod = bpy.data.objects.new('PRODUCT', None)
scn.collection.objects.link(prod)
index = json.load(open(os.path.join(MESH, 'index.json'), encoding='utf-8'))['items']
parts = {}
for it in index:
    if it['kind'] != 'enclosure':
        continue
    bpy.ops.wm.stl_import(filepath=os.path.join(MESH, it['file']), global_scale=MM)
    o = bpy.context.selected_objects[0]
    name = it['file'][:-4]
    o.name = name
    o.parent = prod
    k = next((mk for key, mk in T['NAME_RULES'] if key in name), None)
    if k is None and name.startswith('HARNESS_GH6P__'):     # 보충 규칙(REN-002 scene.py 와 같음): 하니스 6선 색 — NAME_RULES 에 없는 이름
        k = WIRES[int(name.split('__')[1]) % len(WIRES)]
    if k is None:
        REPORT['missing'].append({'where': 'enclosure', 'name': name, 'why': 'NAME_RULES 에 없음'})
        k = 'plastic'
    o.data.materials.clear()
    o.data.materials.append(M[k])
    for poly in o.data.polygons:
        poly.use_smooth = False
    parts[name] = o
    use(k)
    REPORT['enclosure'].append({'name': name, 'material': k, 'triangles': len(o.data.polygons)})

lens = [o for n, o in parts.items() if n.startswith('LENS_CIL093')]
if lens:    # 보충 규칙(REN-002 와 같음): 렌즈 조각 가운데 맨 앞(+Z) 것은 유리
    front = max(lens, key=lambda o: max(v.co.z for v in o.data.vertices))
    front.data.materials[0] = M['glass']
    use('glass')
    next(e for e in REPORT['enclosure'] if e['name'] == front.name)['material'] = 'glass'

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
            k = T['body_key'](src[0], src[1], src[2], model=model, ref=ref, board=b) if src else None
            if k in M:
                s.material = M[k]
                cnt[k] = cnt.get(k, 0) + 1
                use(k)
            else:
                REPORT['missing'].append({'where': b, 'name': o.name, 'model': model, 'ref': ref, 'why': 'GLB 재질 못 읽음' if not src else '규칙이 못 가른 색 ' + str([round(c, 3) for c in src[0]])})
    root.location = (0, 0, z * MM)
    root.parent = prod
    parts['BOARD_' + b.upper()] = root
    REPORT['boards'][b] = {'meshes': sum(1 for o in new if o.type == 'MESH'), 'slots': cnt, 'z_mm': z}

prod.rotation_euler = (math.radians(90), 0, 0)        # 서 있는 자세


# ---------------- 범위 ----------------
def bounds(objs, space=None):
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != 'MESH':
            continue
        mw = (space.inverted() @ o.matrix_world) if space else o.matrix_world
        for c in o.bound_box:
            w = mw @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def children(o):
    out = []
    for c in o.children:
        out.append(c)
        out += children(c)
    return out


bpy.context.view_layer.update()
PROD_OBJS = [o for o in children(prod) if o.type == 'MESH']
lo, hi = bounds(PROD_OBJS)
C = (lo + hi) / 2
RAD = (hi - lo).length / 2
for n, o in parts.items():      # 제품 좌표(mm) 범위 — 보드가 외함 안에 있는지 run.py 가 본다
    l2, h2 = bounds([o] + children(o), prod.matrix_world)
    REPORT.setdefault('bbox_mm', {})[n] = [round(v / MM, 2) for v in (*l2, *h2)]

# ---------------- 턴테이블 축 · 바닥 · 조명 · 월드 ----------------
tt = bpy.data.objects.new('TT', None)
scn.collection.objects.link(tt)
tt.location = (C.x, C.y, 0)
bpy.context.view_layer.update()
mw = prod.matrix_world.copy()
prod.parent = tt
prod.matrix_world = mw

world = bpy.data.worlds.new('W')
scn.world = world
if hasattr(world, 'use_nodes') and not world.node_tree:
    world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.20, 0.205, 0.215, 1)
bg.inputs['Strength'].default_value = 0.35
bpy.ops.mesh.primitive_plane_add(size=6)
fl = bpy.context.object
fl.name = 'FLOOR'
fl.location = (C.x, C.y, lo.z - 0.0003)
fl.data.materials.append(mat('Floor_neutral_grey', dict(rgb=(0.30, 0.30, 0.31), rough=0.65, spec=0.3)))


def area(name, energy, size, off, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA')
    l.energy = energy
    l.size = size
    l.color = color
    o = bpy.data.objects.new(name, l)
    scn.collection.objects.link(o)
    o.location = C + Vector(off)
    o.rotation_euler = (C - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o


S = RAD / 0.06          # 조명 거리 · 세기를 제품 크기에 맞춤 (기준: 반지름 60 mm)
area('KEY', 9 * S * S, 0.25 * S, (-0.25 * S, -0.30 * S, 0.28 * S), (1, 0.97, 0.93))
area('FILL', 3 * S * S, 0.30 * S, (0.30 * S, -0.22 * S, 0.08 * S), (0.92, 0.95, 1))
area('RIM', 7 * S * S, 0.20 * S, (0.05 * S, 0.32 * S, 0.25 * S))

# ---------------- 카메라 3개 ----------------
# (이름, 방위각 °: 0 = 앞(−Y 쪽에서 제품 +Z 면을 봄) · 양수 = 제품 +X 쪽, 고도 °, 렌즈 mm, 여유 배율)
CAM_SPEC = {'hero': (32, 22, 85, 0.82), 'rear': (212, 24, 85, 0.82), 'window': (4, 6, 100, 0.6)}
CAMOBJ = {}
for name, (az, el, lens, fit) in CAM_SPEC.items():
    cd = bpy.data.cameras.new('CAM_' + name)
    cd.lens = lens
    cd.clip_start = 0.005
    co = bpy.data.objects.new('CAM_' + name, cd)
    scn.collection.objects.link(co)
    fov = 2 * math.atan(min(cd.sensor_width, cd.sensor_width * RES[1] / RES[0]) / 2 / lens)
    d = RAD / math.sin(fov / 2) * fit
    a, e = math.radians(az), math.radians(el)
    co.location = C + Vector((d * math.sin(a) * math.cos(e), -d * math.cos(a) * math.cos(e), d * math.sin(e)))
    co.rotation_euler = (C - co.location).to_track_quat('-Z', 'Y').to_euler()
    CAMOBJ[name] = co
REPORT['cameras'] = sorted(CAMOBJ)

# ---------------- 렌더 설정 ----------------
if ENGINE == 'cycles':
    scn.render.engine = 'CYCLES'
    cp = bpy.context.preferences.addons['cycles'].preferences
    cp.compute_device_type = 'OPTIX'
    cp.get_devices()
    gpu = [d for d in cp.devices if d.type == 'OPTIX']
    for d in cp.devices:
        d.use = d.type == 'OPTIX'
    scn.cycles.device = 'GPU' if gpu else 'CPU'
    scn.cycles.samples = SAMPLES
    scn.cycles.use_denoising = True
else:
    scn.render.engine = 'BLENDER_EEVEE'
    scn.eevee.taa_render_samples = SAMPLES
    if hasattr(scn.eevee, 'use_raytracing'):
        scn.eevee.use_raytracing = True
scn.render.resolution_x, scn.render.resolution_y = RES
scn.render.resolution_percentage = 100
scn.render.film_transparent = False
scn.render.image_settings.file_format = 'PNG'
scn.view_settings.view_transform = 'AgX'
scn.view_settings.look = 'AgX - Medium High Contrast'
REPORT.update(engine=scn.render.engine, res=RES, samples=SAMPLES, frames_requested=FRAMES if MODE in ('turntable', 'both') else 0,
              radius_mm=round(RAD / MM, 1), objects=len(PROD_OBJS))

if arg('--save-blend'):
    p = os.path.abspath(arg('--save-blend'))
    assert not os.path.exists(p), '이미 있는 .blend 는 덮어쓰지 않는다: ' + p
    bpy.ops.wm.save_as_mainfile(filepath=p, copy=True)

# ---------------- 렌더 ----------------
os.makedirs(OUT, exist_ok=True)
done = {'stills': [], 'turntable_new': 0, 'turntable_skipped': 0}
if MODE in ('stills', 'both'):
    os.makedirs(os.path.join(OUT, 'stills'), exist_ok=True)
    for name in CAMS:
        scn.camera = CAMOBJ[name]
        scn.render.filepath = os.path.join(OUT, 'stills', name + '.png')
        bpy.ops.render.render(write_still=True)
        done['stills'].append(name)
if MODE in ('turntable', 'both'):
    os.makedirs(os.path.join(OUT, 'turntable'), exist_ok=True)
    scn.camera = CAMOBJ['hero']
    for i in range(FRAMES):
        f = os.path.join(OUT, 'turntable', 'frame_%04d.png' % (i + 1))
        if os.path.exists(f) and os.path.getsize(f) > 0:      # 다시 돌리면 끝난 프레임은 건너뜀
            done['turntable_skipped'] += 1
            continue
        tt.rotation_euler = (0, 0, 2 * math.pi * i / FRAMES)
        scn.render.filepath = f
        bpy.ops.render.render(write_still=True)
        done['turntable_new'] += 1
    tt.rotation_euler = (0, 0, 0)
REPORT['done'] = done
REPORT['missing_count'] = len(REPORT['missing'])
json.dump(REPORT, open(os.path.join(OUT, 'scene_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('REN003B objects %d mats %d used %d missing %d stills %d frames_new %d frames_skip %d' % (
    len(PROD_OBJS), len(M), len(REPORT['used']), len(REPORT['missing']), len(done['stills']), done['turntable_new'], done['turntable_skipped']))
