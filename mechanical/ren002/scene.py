"""REN-002 제품 렌더 장면 (Blender 5.2, bpy) — REN-001 scene.py 를 이어 고친 것. 입력: validation/runtime/vd001/render/mesh/*.stl (03_export_meshes.py)
· board_*.glb (렌더용 사본 = pcb 보드 + 대체 3D 모델 연결, 빠짐 0).
실행: blender -b --factory-startup --python mechanical/ren002/scene.py -- --mode stills|blend [--views a,b] [--samples 256] [--res 2560x1440]
  stills : Cycles OptiX → render/stills/ren002_<view>.png  (dims 는 _raw.png + dims.json, 04_dims_overlay.py 가 치수선을 그림)
  blend  : 턴테이블(8 s, 200프레임 @25) .blend → render/turntable.blend
좌표: 제품 +Y 위 · +Z 앞(광축). 서 있는 자세 = PRODUCT X 90° (제품 +Y → 월드 +Z), 누운 자세 = X 0° (뒷면이 바닥, 렌즈가 위, 커넥터 면 −Y 가 카메라 쪽)."""
import bpy, math, os, sys, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d
MODE = arg('--mode', 'stills')
LANE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
R = os.path.join(LANE, 'validation', 'runtime', 'vd001', 'render')
MESH = os.path.join(R, 'mesh')
RES = [int(v) for v in arg('--res', '2560x1440').split('x')]
SAMPLES = int(arg('--samples', '256'))
VIEWS = arg('--views', 'front,back,threequarter,exploded,section,window,connectors,microsd,inuse,dims').split(',')
Z_CARRIER, Z_FRONT = -0.0096, 0.0096      # 판 아랫면 (m) — params z_car_bot / z_fr_bot

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---------------- 재질 ----------------
def mat(name, base, metal=0.0, rough=0.5, trans=0.0, ior=1.45, spec=0.5, bump=None, coat=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*base, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Transmission Weight'].default_value = trans
    p.inputs['IOR'].default_value = ior
    p.inputs['Specular IOR Level'].default_value = spec
    p.inputs['Coat Weight'].default_value = coat
    if bump:   # FDM 층 결: 물결 무늬(Bands, 객체 Z = 출력 적층 방향, 주기 bump[0] mm) → 범프 (미세 노멀)
        w = nt.nodes.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = 'Z'
        w.inputs['Scale'].default_value = 2 * math.pi / (10.0 * bump[0])   # Blender 물결: 주기 = 2π / (10·scale) (객체 좌표 = mm)
        bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = bump[1]; bn.inputs['Distance'].default_value = 0.02
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Object'], w.inputs['Vector']); nt.links.new(w.outputs['Fac'], bn.inputs['Height'])
        nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    return m

M = {
    'petg': mat('PETG_black_matte', (0.013, 0.013, 0.014), rough=0.62, spec=0.4, bump=(0.2, 0.12)),          # 약간 거친 무광 + 층 결
    'anod': mat('Al_black_anodize_satin', (0.045, 0.046, 0.05), metal=1.0, rough=0.27),                       # 반광 금속 — PETG 와 반사 결이 다름
    'al': mat('Al_raw', (0.78, 0.79, 0.8), metal=1.0, rough=0.28),
    'pmma': mat('PMMA_clear', (0.97, 0.98, 1.0), rough=0.02, trans=1.0, ior=1.49),
    'foam': mat('Foam_black', (0.01, 0.01, 0.01), rough=0.95, spec=0.1),
    'pad': mat('Tflex_P340_purple', (0.32, 0.09, 0.42), rough=0.65),
    'brass': mat('Brass', (0.78, 0.6, 0.25), metal=1.0, rough=0.3),
    'steel': mat('Steel', (0.62, 0.63, 0.65), metal=1.0, rough=0.35),
    'lens': mat('Lens_black_metal', (0.03, 0.03, 0.03), metal=0.9, rough=0.35),
    'glass': mat('Lens_glass', (0.9, 0.95, 1.0), rough=0.0, trans=1.0, ior=1.6),
    'plastic': mat('Plastic_black', (0.025, 0.025, 0.028), rough=0.5),
    'sensor': mat('Sensor_block', (0.08, 0.08, 0.09), metal=0.6, rough=0.4),
    'fpc': mat('FPC_polyimide', (0.75, 0.42, 0.08), rough=0.4),
    'core': mat('Core_module_pcb', (0.02, 0.14, 0.06), rough=0.45),
    'wire_r': mat('Wire_red', (0.6, 0.03, 0.02), rough=0.45), 'wire_k': mat('Wire_black', (0.02, 0.02, 0.02), rough=0.45),
    'wire_y': mat('Wire_yellow', (0.75, 0.6, 0.03), rough=0.45),
    'mask': mat('PCB_mask_green', (0.02, 0.18, 0.05), rough=0.25), 'enig': mat('ENIG_gold', (0.95, 0.72, 0.35), metal=1.0, rough=0.25),
    'silk': mat('Silk_white', (0.92, 0.92, 0.92), rough=0.6),
    'cable_grey': mat('Cable_PVC_grey', (0.42, 0.44, 0.47), rough=0.55), 'cable_k': mat('Cable_PVC_black', (0.02, 0.02, 0.022), rough=0.5),
    'plug_clear': mat('RJ45_plug_PC', (0.9, 0.92, 0.95), rough=0.1, trans=0.85, ior=1.58),
    'mount': mat('Mount_Al_dark', (0.12, 0.12, 0.13), metal=1.0, rough=0.4),
}
RULES = [('HOUSING', 'petg'), ('FRONT_COVER', 'petg'), ('HS_EXTRUSION', 'anod'), ('HS_PEDESTAL', 'al'), ('SPREADER_M003', 'al'),
         ('PMMA', 'pmma'), ('FOAM', 'foam'), ('INS_PADS', 'pad'), ('GAP_PAD', 'pad'), ('HW_STANDOFFS', 'brass'),
         ('HW_M16', 'steel'), ('HW_M25', 'steel'), ('LENS_CIL093', 'lens'), ('SENSOR', 'sensor'), ('PEDESTAL', 'al'), ('FPC', 'fpc'),
         ('CORE_MODULE', 'core')]

prod = bpy.data.objects.new('PRODUCT', None); scn.collection.objects.link(prod)
prod.rotation_euler = (math.radians(90), 0, 0)
objs = {}
for fn in json.load(open(os.path.join(MESH, 'index.json'))):
    bpy.ops.wm.stl_import(filepath=os.path.join(MESH, fn))
    o = bpy.context.selected_objects[0]
    o.name = fn[:-4]; objs[o.name] = o
k = 0.001                                   # Fusion STL = mm (REN-001 dry: 외함 높이로 0.0010033 확인)
for o in objs.values():
    o.scale = (k, k, k); o.location = (o.location.x * k, o.location.y * k, o.location.z * k)
    o.parent = prod
    nm = o.name
    mname = next((mk for key, mk in RULES if key in nm), 'plastic')
    if nm.startswith('HARNESS_GH6P__'):
        mname = ['wire_k', 'wire_r', 'wire_y', 'wire_y', 'wire_r', 'wire_k'][int(nm.split('__')[1])]
    o.data.materials.clear(); o.data.materials.append(M[mname])
lens = [o for n, o in objs.items() if n.startswith('LENS_CIL093')]
max(lens, key=lambda o: max(v.co.z for v in o.data.vertices)).data.materials[0] = M['glass']
for b, z in (('carrier', Z_CARRIER), ('front', Z_FRONT)):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(MESH, 'board_%s.glb' % b))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new('BOARD_' + b.upper(), None); scn.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
        if o.type == 'MESH':
            for s in o.material_slots:
                nl = s.material.name.lower() if s.material else ''
                if 'mask' in nl:
                    s.material = M['mask']
                elif 'silk' in nl:
                    s.material = M['silk']
                elif any(w in nl for w in ('copper', 'pad', 'track', 'via', 'zone')):
                    s.material = M['enig']
    root.location = (0, 0, z); root.parent = prod
    objs['BOARD_' + b.upper()] = root

# ---------------- 사용 장면 소품 (제품 좌표 mm → PRODUCT 자식, 기본 숨김) ----------------
ACC = []
def acc_obj(o, m):
    o.parent = prod; o.data.materials.append(M[m]); o.hide_render = True; ACC.append(o); return o
def p_box(name, x0, x1, y0, y1, z0, z1, m):
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = name
    o.scale = ((x1 - x0) * k, (y1 - y0) * k, (z1 - z0) * k); o.location = ((x0 + x1) / 2 * k, (y0 + y1) / 2 * k, (z0 + z1) / 2 * k)
    return acc_obj(o, m)
def p_cyl(name, a, b, r, m):
    a, b = Vector(a) * k, Vector(b) * k
    bpy.ops.mesh.primitive_cylinder_add(radius=r * k, depth=(b - a).length, vertices=48); o = bpy.context.object; o.name = name
    o.location = (a + b) / 2; o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return acc_obj(o, m)
def p_cable(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r * k; cu.bevel_resolution = 6; cu.resolution_u = 24
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p) * k; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); scn.collection.objects.link(o)
    return acc_obj(o, m)
YF = -126.5                                  # 사용 장면 바닥 = 제품 아랫면 y −36.5 아래 90 mm
RJC, RJZ, DCX, DCZ = -2.455, -17.1, 15.18, -16.1   # J5 플러그 중심 x·z (M-003 BLK_J5_PLUG), J2 DC 축 (15.18, −16.10)
p_box('ACC_RJ45_PLUG', RJC - 5.85, RJC + 5.85, -52.0, -33.5, RJZ - 4.5, RJZ + 4.5, 'plug_clear')
p_box('ACC_RJ45_BOOT', RJC - 6.5, RJC + 6.5, -62.0, -52.0, RJZ - 5.5, RJZ + 5.5, 'cable_grey')
p_cable('ACC_RJ45_CABLE', [(RJC, -62, RJZ), (RJC, -88, RJZ), (RJC, YF + 3.0, RJZ - 28), (RJC - 15, YF + 3.0, RJZ - 150)], 3.0, 'cable_grey')
p_cyl('ACC_DC_PLUG', (DCX, -36.0, DCZ), (DCX, -53.0, DCZ), 5.0, 'cable_k')
p_cable('ACC_DC_CABLE', [(DCX, -53, DCZ), (DCX, -80, DCZ), (DCX + 4, YF + 1.8, DCZ - 30), (DCX + 30, YF + 1.8, DCZ - 160)], 1.8, 'cable_k')
p_cyl('ACC_MOUNT_SCREW', (0, -4, -26.2), (0, -4, -34.0), 6.0, 'mount')                 # 1/4"-20 삼각대 자리 (0, −4) 뒷면
p_cyl('ACC_MOUNT_ARM', (0, -4, -34.0), (0, -4, -48.0), 7.5, 'mount')
p_cyl('ACC_MOUNT_POLE', (0, -4, -48.0 - 7.5), (0, YF + 4, -48.0 - 7.5), 7.5, 'mount')
p_cyl('ACC_MOUNT_BASE', (0, YF + 4, -55.5), (0, YF, -55.5), 45.0, 'mount')

# ---------------- 조명·바닥·월드 ----------------
world = bpy.data.worlds.new('W'); scn.world = world
bg = world.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.20, 0.205, 0.215, 1); bg.inputs['Strength'].default_value = 0.35
bpy.ops.mesh.primitive_plane_add(size=6); fl = bpy.context.object; fl.name = 'FLOOR'
fl.data.materials.append(mat('Floor_neutral_grey', (0.30, 0.30, 0.31), rough=0.65, spec=0.3))
LIGHTS = {}
def area(name, energy, size, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.size = size; l.color = color
    o = bpy.data.objects.new(name, l); scn.collection.objects.link(o); LIGHTS[name] = o
area('KEY', 9, 0.25, (1, 0.97, 0.93)); area('FILL', 3, 0.3, (0.92, 0.95, 1)); area('RIM', 7, 0.2)
li = bpy.data.lights.new('INSIDE', 'POINT'); li.energy = 0.012; li.color = (1.0, 0.85, 0.7); li.shadow_soft_size = 0.004
inside = bpy.data.objects.new('INSIDE', li); scn.collection.objects.link(inside); inside.parent = prod
inside.location = (0, 0.014, 0.022); inside.hide_render = True; inside.visible_camera = False; inside.visible_transmission = False; inside.visible_glossy = False   # 광원 자체는 화면에 안 보이게 (PMMA 너머 = 투과 광선)      # 제품 (0, 14, 22) mm — 전면 보드 위, 창 안쪽

SKIP_B = ('FLOOR', 'CUTTER', 'CAM')
def bounds():
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE') or o.name in SKIP_B or o.hide_render:
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    return lo, hi
def stage():
    bpy.context.view_layer.update()
    lo, hi = bounds()
    c = (lo + hi) / 2
    fl.location = (c.x, c.y, lo.z - 0.0003)
    for name, off in (('KEY', (-0.25, -0.3, 0.28)), ('FILL', (0.3, -0.22, 0.08)), ('RIM', (0.05, 0.32, 0.25))):
        o = LIGHTS[name]; o.location = c + Vector(off)
        o.rotation_euler = (c - o.location).to_track_quat('-Z', 'Y').to_euler()
    return lo, hi, c
def pose(p):
    prod.rotation_euler = (math.radians(90 if p == 'upright' else 0), 0, 0)
    prod.location = (0, 0, 0)

# ---------------- 렌더 설정 ----------------
scn.render.engine = 'CYCLES'
cp = bpy.context.preferences.addons['cycles'].preferences
cp.compute_device_type = 'OPTIX'; cp.get_devices()
for d in cp.devices:
    d.use = d.type in ('OPTIX',)
scn.cycles.device = 'GPU'; scn.cycles.samples = SAMPLES; scn.cycles.use_denoising = True
scn.render.resolution_x, scn.render.resolution_y = RES; scn.render.film_transparent = False
scn.view_settings.view_transform = 'AgX'; scn.view_settings.look = 'AgX - Medium High Contrast'
cam_d = bpy.data.cameras.new('CAM'); cam = bpy.data.objects.new('CAM', cam_d); scn.collection.objects.link(cam); scn.camera = cam
cam_d.clip_start = 0.005
def aim(loc, target, lens=85):
    cam.location = loc; cam_d.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

EXPLODE = {'FRONT_COVER': (0, 0, 40), 'PMMA': (0, 0, 62), 'FOAM': (0, 0, 22), 'HS_EXTRUSION': (40, 0, 0), 'HS_PEDESTAL': (24, 0, 0),
           'GAP_PAD': (14, 0, 0), 'HOUSING': (0, 0, -55), 'BOARD_CARRIER': (0, 0, -30)}   # 제품 좌표 mm
def explode(on):
    for n, o in objs.items():
        for key, v in EXPLODE.items():
            if key in n:
                if o.get('base_loc') is None:
                    o['base_loc'] = list(o.location)
                o.location = Vector(o['base_loc']) + (Vector(v) * 0.001 if on else Vector((0, 0, 0)))
                break
def section(on, c):
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or o.name in ('FLOOR', 'CUTTER') or o.name.startswith('ACC_'):
            continue
        md = o.modifiers.get('CUT')
        if on and md is None:
            if 'CUTTER' not in bpy.data.objects:
                bpy.ops.mesh.primitive_cube_add(size=1, location=(0.25, 0, c.z)); cu = bpy.context.object; cu.name = 'CUTTER'
                cu.scale = (0.5, 0.5, 0.5); cu.hide_render = True; cu.display_type = 'WIRE'
            md = o.modifiers.new('CUT', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = bpy.data.objects['CUTTER']; md.solver = 'EXACT'
        elif md:
            md.show_render = on
def accessories(on):
    for o in ACC:
        o.hide_render = not on

OUTS = os.path.join(R, 'stills'); os.makedirs(OUTS, exist_ok=True)
D = 0.52
def shot(v):
    explode(False); accessories(False); inside.hide_render = True
    pose('lying' if v in ('connectors', 'microsd') else 'upright')
    if v == 'inuse':
        accessories(True)
    lo, hi, c = stage()
    section(v == 'section', c)
    if v == 'front':
        aim((0.0, -D, c.z + 0.05), c)
    elif v == 'back':
        aim((0.03, D, c.z + 0.06), c)
    elif v == 'threequarter':
        aim((D * 0.62, -D * 0.75, c.z + 0.16), c)
    elif v == 'exploded':
        explode(True); lo, hi, c = stage(); aim((c.x + D * 0.85, -D * 1.05, c.z + 0.22), c, lens=70)
    elif v == 'section':
        aim((D, -0.02, c.z + 0.04), c)
    elif v == 'window':      # 렌즈 창 + A 창 (LED A1·A2), 내부 조명 약간
        inside.hide_render = False
        aim((0.035, -0.15, 0.05), (0, -0.038, 0.009), lens=70)
    elif v == 'connectors':  # 누운 자세: 커넥터 면 −Y(RJ45·DC) + −X(USB-C) 가 보임
        aim((c.x - D * 0.55, c.y - D * 0.7, c.z + D * 0.45), c, lens=85)
    elif v == 'microsd':     # 누운 자세: +Y 아래 벽의 microSD 홈
        aim((c.x - D * 0.25, c.y + D * 0.8, c.z + D * 0.35), c, lens=85)
    elif v == 'inuse':       # 받침대 + RJ45·DC 케이블
        aim((c.x + D * 0.75, c.y - D * 1.0, c.z + D * 0.35), c, lens=80)
    elif v == 'dims':
        aim((D * 0.66, -D * 0.82, c.z + 0.2), c, lens=70)
    return c

if MODE == 'stills':
    for v in VIEWS:
        shot(v)
        out = os.path.join(OUTS, 'ren002_%s%s.png' % (v, '_raw' if v == 'dims' else ''))
        scn.render.filepath = out
        bpy.ops.render.render(write_still=True)
        if v == 'dims':     # 외형 상자 (외함·덮개·방열판, 제품 좌표 mm) 모서리를 화면 좌표로
            inv = prod.matrix_world.inverted()
            lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
            for n in ('HOUSING', 'FRONT_COVER', 'HS_EXTRUSION'):
                o = objs[n]
                for cc in o.bound_box:
                    p = (inv @ (o.matrix_world @ Vector(cc))) * 1000.0
                    lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
            def px(p):
                w = prod.matrix_world @ (Vector(p) * 0.001)
                q = world_to_camera_view(scn, cam, w)
                return [q.x * RES[0], (1 - q.y) * RES[1]]
            o6 = 8.0   # 치수선 띄움 mm
            dims = {
                'X': {'mm': hi.x - lo.x, 'a': px((lo.x, lo.y - o6, hi.z)), 'b': px((hi.x, lo.y - o6, hi.z)), 'ea': [px((lo.x, lo.y, hi.z)), px((hi.x, lo.y, hi.z))]},
                'Y': {'mm': hi.y - lo.y, 'a': px((lo.x - o6, lo.y, hi.z)), 'b': px((lo.x - o6, hi.y, hi.z)), 'ea': [px((lo.x, lo.y, hi.z)), px((lo.x, hi.y, hi.z))]},
                'Z': {'mm': hi.z - lo.z, 'a': px((hi.x, lo.y - o6, hi.z)), 'b': px((hi.x, lo.y - o6, lo.z)), 'ea': [px((hi.x, lo.y, hi.z)), px((hi.x, lo.y, lo.z))]},
                'lo': list(lo), 'hi': list(hi), 'res': RES}
            json.dump(dims, open(os.path.join(OUTS, 'ren002_dims.json'), 'w'), indent=1)
        print('STILL', v)
elif MODE == 'blend':
    pose('upright'); accessories(False); explode(False)
    lo, hi, c = stage()
    aim((D * 0.62, -D * 0.75, c.z + 0.12), c)
    scn.render.engine = 'BLENDER_EEVEE'; scn.eevee.taa_render_samples = 64
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    scn.frame_start, scn.frame_end = 1, 200; scn.render.fps = 25
    prod.rotation_mode = 'XYZ'
    prod.keyframe_insert('rotation_euler', frame=1)
    prod.rotation_euler = (math.radians(90), 0, math.radians(360) * 199 / 200)
    prod.keyframe_insert('rotation_euler', frame=200)
    from bpy_extras import anim_utils
    cb = anim_utils.action_get_channelbag_for_slot(prod.animation_data.action, prod.animation_data.action_slot)
    for fc in cb.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    p = os.path.join(R, 'turntable.blend')
    bpy.ops.wm.save_as_mainfile(filepath=p, copy=True)
    print('BLEND', p)
