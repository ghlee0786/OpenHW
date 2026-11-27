"""REN-001 제품 렌더 장면 (Blender 5.2, bpy) — 재현용. 입력: validation/runtime/vd001/render/mesh/*.stl (Fusion, 월드 좌표)·board_*.glb (KiCad)
실행: blender -b --factory-startup --python scene.py -- --mode dry|stills|blend [--views front,back,...] [--samples 256] [--res 2560x1440]
  dry    : 가져와서 크기·위치·재질 이름만 출력
  stills : Cycles(OptiX)로 앞·뒤·3/4·분해·단면·창 근접 PNG → render/stills/
  blend  : 턴테이블(8 s, 200프레임 @25)을 넣은 .blend 를 render/turntable.blend 로 저장 (render_chunks.py 로 렌더)
좌표: 제품 +Y 위 · +Z 앞(광축) → Blender: 제품 +Y → +Z, +Z → −Y (PRODUCT 빈 객체에 X 90°)."""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(k, d=None):
    return argv[argv.index(k) + 1] if k in argv else d
MODE = arg('--mode', 'dry')
LANE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
R = os.path.join(LANE, 'validation', 'runtime', 'vd001', 'render')
MESH = os.path.join(R, 'mesh')
RES = [int(v) for v in arg('--res', '2560x1440').split('x')]
SAMPLES = int(arg('--samples', '256'))
VIEWS = arg('--views', 'front,back,threequarter,exploded,section,window').split(',')
Z_CARRIER, Z_FRONT = -0.0096, 0.0096      # 판 아랫면 (m) — params z_car_bot / z_fr_bot

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# ---------------- 재질 ----------------
def mat(name, base, metal=0.0, rough=0.5, trans=0.0, ior=1.45, emit=None, bump=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*base, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Transmission Weight'].default_value = trans
    p.inputs['IOR'].default_value = ior
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1); p.inputs['Emission Strength'].default_value = 2.0
    if bump:   # 출력 적층 결 (제품 Y 방향 0.2 mm 간격) — 물결 무늬 → 범프
        w = nt.nodes.new('ShaderNodeTexWave'); w.inputs['Scale'].default_value = bump[0]; w.wave_type = 'BANDS'; w.bands_direction = 'Z'
        bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = bump[1]
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Object'], w.inputs['Vector']); nt.links.new(w.outputs['Fac'], bn.inputs['Height'])
        nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    return m

M = {
    'petg': mat('PETG_black', (0.018, 0.018, 0.02), rough=0.55, bump=(2500.0, 0.08)),
    'anod': mat('Al_black_anodize', (0.02, 0.02, 0.022), metal=1.0, rough=0.38),
    'al': mat('Al_raw', (0.78, 0.79, 0.8), metal=1.0, rough=0.28),
    'pmma': mat('PMMA_clear', (0.97, 0.98, 1.0), rough=0.02, trans=1.0, ior=1.49),
    'foam': mat('Foam_black', (0.01, 0.01, 0.01), rough=0.95),
    'pad': mat('Tflex_P340_purple', (0.32, 0.09, 0.42), rough=0.65),
    'brass': mat('Brass', (0.78, 0.6, 0.25), metal=1.0, rough=0.3),
    'steel': mat('Steel', (0.62, 0.63, 0.65), metal=1.0, rough=0.35),
    'lens': mat('Lens_black_metal', (0.03, 0.03, 0.03), metal=0.9, rough=0.35),
    'glass': mat('Lens_glass', (0.9, 0.95, 1.0), rough=0.0, trans=1.0, ior=1.6),
    'plastic': mat('Plastic_black', (0.025, 0.025, 0.028), rough=0.5),
    'sensor': mat('Sensor_block', (0.08, 0.08, 0.09), metal=0.6, rough=0.4),
    'ivory': mat('Connector_ivory', (0.85, 0.82, 0.72), rough=0.5),
    'fpc': mat('FPC_polyimide', (0.75, 0.42, 0.08), rough=0.4),
    'led': mat('LED_white', (0.92, 0.92, 0.9), rough=0.3),
    'core': mat('Core_module_pcb', (0.02, 0.14, 0.06), rough=0.45),
    'wire_r': mat('Wire_red', (0.6, 0.03, 0.02), rough=0.45), 'wire_k': mat('Wire_black', (0.02, 0.02, 0.02), rough=0.45),
    'wire_y': mat('Wire_yellow', (0.75, 0.6, 0.03), rough=0.45),
    'mask': mat('PCB_mask_green', (0.02, 0.18, 0.05), rough=0.25), 'enig': mat('ENIG_gold', (0.95, 0.72, 0.35), metal=1.0, rough=0.25),
    'silk': mat('Silk_white', (0.92, 0.92, 0.92), rough=0.6), 'fr4': mat('FR4_edge', (0.55, 0.5, 0.3), rough=0.6),
}
RULES = [('HOUSING', 'petg'), ('FRONT_COVER', 'petg'), ('HS_EXTRUSION', 'anod'), ('HS_PEDESTAL', 'al'), ('SPREADER_M003', 'al'),
         ('PMMA', 'pmma'), ('FOAM', 'foam'), ('INS_PADS', 'pad'), ('GAP_PAD', 'pad'), ('HW_STANDOFFS', 'brass'),
         ('HW_M16', 'steel'), ('HW_M25', 'steel'), ('LENS_CIL093', 'lens'), ('CLA216', 'plastic'), ('SPACER', 'plastic'),
         ('SENSOR', 'sensor'), ('PEDESTAL', 'al'), ('DF30', 'ivory'), ('FPC', 'fpc'), ('LED_', 'led'), ('CORE_MODULE', 'core'),
         ('ICR_LEAD', 'wire_k'), ('ICR_PADS', 'enig')]

prod = bpy.data.objects.new('PRODUCT', None); scn.collection.objects.link(prod)
prod.rotation_euler = (math.radians(90), 0, 0)
objs = {}
idx = json.load(open(os.path.join(MESH, 'index.json')))
for fn in idx:
    bpy.ops.wm.stl_import(filepath=os.path.join(MESH, fn))
    o = bpy.context.selected_objects[0]
    o.name = fn[:-4]; objs[o.name] = o
# 단위: 외함 높이(Z 방향, 제품 좌표 mm)로 판정 → m
hz = objs['HOUSING'].dimensions.z
k = 0.0659 / hz if hz > 0 else 0.001      # HOUSING z −26.2 … 39.485 = 65.69 mm
for o in objs.values():
    o.scale = (k, k, k); o.location = (o.location.x * k, o.location.y * k, o.location.z * k)
    o.parent = prod
    nm = o.name
    mname = 'plastic'
    for key, mk in RULES:
        if key in nm:
            mname = mk; break
    if nm.startswith('HARNESS_GH6P__'):
        i = int(nm.split('__')[1]); mname = ['wire_k', 'wire_r', 'wire_y', 'wire_y', 'wire_r', 'wire_k'][i]
    o.data.materials.clear(); o.data.materials.append(M[mname])
    for p in o.data.polygons:
        p.use_smooth = False
# 렌즈 돔(가장 앞쪽 바디) → 유리
lens = [o for n, o in objs.items() if n.startswith('LENS_CIL093')]
if lens:
    front = max(lens, key=lambda o: max((o.matrix_world @ Vector(c)).z for c in o.bound_box) if False else max(v.co.z for v in o.data.vertices))
    front.data.materials[0] = M['glass']
# 보드 GLB (KiCad, glTF 는 Y-up → 가져올 때 Z-up 으로 바뀜, 단위 m)
mat_names = set()
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
                if s.material:
                    mat_names.add(s.material.name)
                    nl = s.material.name.lower()
                    if 'mask' in nl:
                        s.material = M['mask']
                    elif 'silk' in nl:
                        s.material = M['silk']
                    elif any(w in nl for w in ('copper', 'pad', 'track', 'via', 'zone')):
                        s.material = M['enig']
    root.location = (0, 0, z); root.parent = prod
    objs['BOARD_' + b.upper()] = root

bpy.context.view_layer.update()
def bounds(o_list):
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    for o in o_list:
        if o.type != 'MESH':
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    return lo, hi
allm = [o for o in bpy.data.objects if o.type == 'MESH']
lo, hi = bounds(allm)
print('SCALE k', k, 'BOUNDS m', [round(v, 4) for v in lo], [round(v, 4) for v in hi])
for b in ('BOARD_CARRIER', 'BOARD_FRONT'):
    l2, h2 = bounds([o for o in bpy.data.objects if o.type == 'MESH' and o.parent and (o.parent.name == b or (o.parent.parent and o.parent.parent.name == b))])
    print(b, [round(v * 1000, 2) for v in l2], [round(v * 1000, 2) for v in h2])
l3, h3 = bounds([objs['HOUSING']]); print('HOUSING mm', [round(v * 1000, 2) for v in l3], [round(v * 1000, 2) for v in h3])
print('GLB materials', sorted(mat_names)[:30])
if MODE == 'dry':
    sys.exit(0)

# ---------------- 조명·바닥·월드 ----------------
world = bpy.data.worlds.new('W'); scn.world = world
bg = world.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.06, 0.065, 0.075, 1); bg.inputs['Strength'].default_value = 0.6
cz = (lo.z + hi.z) / 2
floor_z = lo.z - 0.0005
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, floor_z)); fl = bpy.context.object; fl.name = 'FLOOR'
fl.data.materials.append(mat('Floor', (0.18, 0.185, 0.2), rough=0.6))
def area(name, loc, energy, size, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.size = size; l.color = color
    o = bpy.data.objects.new(name, l); scn.collection.objects.link(o); o.location = loc
    d = Vector((0, 0, cz)) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
area('KEY', (-0.25, -0.3, cz + 0.28), 9, 0.25, (1, 0.97, 0.92))
area('FILL', (0.3, -0.22, cz + 0.08), 3, 0.3, (0.9, 0.95, 1))
area('RIM', (0.05, 0.32, cz + 0.25), 7, 0.2)
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
cam_d.lens = 85; cam_d.clip_start = 0.005
tgt = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, cz))
def aim(loc, target=tgt, lens=85):
    cam.location = loc; cam_d.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

EXPLODE = {'FRONT_COVER': (0, 0, 40), 'PMMA': (0, 0, 62), 'FOAM': (0, 0, 22), 'HS_EXTRUSION': (40, 0, 0), 'HS_PEDESTAL': (24, 0, 0),
           'GAP_PAD': (14, 0, 0), 'HOUSING': (0, 0, -55), 'BOARD_CARRIER': (0, 0, -30), 'HW_STANDOFFS': (0, 0, 0)}   # 제품 좌표 mm

def explode(on):
    for n, o in objs.items():
        for key, v in EXPLODE.items():
            if key in n:
                base = o.get('base_loc')
                if base is None:
                    o['base_loc'] = list(o.location); base = o['base_loc']
                o.location = Vector(base) + (Vector(v) * 0.001 if on else Vector((0, 0, 0)))
                break

def section(on):
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name in ('FLOOR', 'CUTTER'):
            continue
        md = o.modifiers.get('CUT')
        if on and md is None:
            if 'CUTTER' not in bpy.data.objects:
                bpy.ops.mesh.primitive_cube_add(size=1, location=(0.25, 0, cz)); c = bpy.context.object; c.name = 'CUTTER'
                c.scale = (0.5, 0.5, 0.5); c.hide_render = True; c.display_type = 'WIRE'
            md = o.modifiers.new('CUT', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = bpy.data.objects['CUTTER']; md.solver = 'EXACT'
        elif md:
            md.show_render = on

OUTS = os.path.join(R, 'stills'); os.makedirs(OUTS, exist_ok=True)
D = 0.52
shots = {
    'front': lambda: aim((0.0, -D, cz + 0.05)),
    'back': lambda: aim((0.03, D, cz + 0.06)),
    'threequarter': lambda: aim((D * 0.62, -D * 0.75, cz + 0.16)),
    'exploded': lambda: (explode(True), aim((D * 0.85, -D * 1.05, cz + 0.22), lens=70)),
    'section': lambda: (section(True), aim((D, -0.02, cz + 0.04), lens=85)),
    # 창 근접: 렌즈 창 + A 창(LED A1·A2) — 제품 (0, +8, 40) 을 앞 위에서 (제품 +Y → 월드 +Z, 제품 +Z → 월드 −Y)
    'window': lambda: aim((0.035, -0.15, 0.05), target=(0, -0.038, 0.009), lens=70),
}
if MODE == 'stills':
    for v in VIEWS:
        explode(False); section(False)
        shots[v]()
        scn.render.filepath = os.path.join(OUTS, 'ren001_%s.png' % v)
        bpy.ops.render.render(write_still=True)
        print('STILL', v)
elif MODE == 'blend':
    explode(False); section(False)
    aim((D * 0.62, -D * 0.75, cz + 0.12))
    scn.render.engine = 'BLENDER_EEVEE'; scn.eevee.taa_render_samples = 64
    scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
    scn.frame_start, scn.frame_end = 1, 200; scn.render.fps = 25
    prod.rotation_mode = 'XYZ'
    prod.keyframe_insert('rotation_euler', frame=1)
    prod.rotation_euler = (math.radians(90), 0, math.radians(360) * 199 / 200)
    prod.keyframe_insert('rotation_euler', frame=200)
    from bpy_extras import anim_utils
    act = prod.animation_data.action
    cb = anim_utils.action_get_channelbag_for_slot(act, prod.animation_data.action_slot)
    for fc in cb.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    p = os.path.join(R, 'turntable.blend')
    bpy.ops.wm.save_as_mainfile(filepath=p, copy=True)
    print('BLEND', p)
