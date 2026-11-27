"""REN-003b 재질 확장 (O-125 2단계 — 사실적 렌더). mechanical/ren003/materials.py 는 읽기만 하고, 덧붙이는 것은 모두 여기에 둔다.

- EXT_MATS      : materials.py 에 없는 새 재질 (같은 표기: 선형 rgb · metal · rough · trans · ior · coat)
- EXT_NAME_RULES: 외함 부품 이름 규칙 — materials.py NAME_RULES 에 없는 이름일 때만 본다(부분 일치). 시안(A/B/C) 부품 이름용.
- LOOK          : 재질 키 → 미세 질감(노드) 종류. scene.py 가 Principled 재질을 만든 뒤 detail() 로 덧입힌다.
- BEVEL_SKIP    : 베벨을 넣지 않는 부품 이름(얇은 패드 · 폼 등)
값은 보기용 가정이다(측정값 아님). 좌표 단위: 객체 좌표 = m."""

EXT_MATS = {
    'ir_glass':  dict(label='IR 투과 앞유리 (짙은 스모크, 가시광 투과 약 25 % — 면당 0.5, 렌즈 앞은 투명 원형 창)', rgb=(0.004, 0.0035, 0.005), rough=0.02, ior=1.49,
                      smoke=0.5, window_r=7.5),
    'petg_shell': dict(label='본체 무광 흑색 플라스틱 (차콜 — 두 톤 가운데 밝은 쪽)', rgb=(0.024, 0.024, 0.026), rough=0.55, spec=0.4),
    'lightpipe_on': dict(label='상태 LED 광 파이프 (켜짐, 청록)', rgb=(0.05, 0.6, 0.5), rough=0.3, emit=((0.05, 1.0, 0.75), 2.5)),
    'floor':     dict(label='무한 배경 (밝은 회색, 약한 반사)', rgb=(0.62, 0.62, 0.63), rough=0.55, spec=0.3, coat=0.25),
    'anod_grey': dict(label='알루미늄 스페이스 그레이 양극산화 (중간 회색, 헤어라인)', rgb=(0.20, 0.205, 0.215), metal=1.0, rough=0.34),
    'rubber':    dict(label='고무 가스킷 (흑색 실리콘)', rgb=(0.012, 0.012, 0.013), rough=0.85, spec=0.25),
    'backdrop':  dict(label='무한 배경 (밝은 회색 종이)', rgb=(0.62, 0.62, 0.63), rough=0.75, spec=0.2),
    'wall':      dict(label='사용 장면 벽 (무광 도장)', rgb=(0.72, 0.71, 0.68), rough=0.8, spec=0.2),
    'bracket':   dict(label='벽 브래킷 (흑색 분체 도장 강판)', rgb=(0.02, 0.02, 0.022), rough=0.42, metal=0.0, coat=0.1),
    'lightpipe': dict(label='상태 LED 광 파이프 (투명 PC)', rgb=(0.9, 0.95, 0.92), rough=0.12, trans=0.9, ior=1.58),
}

# (이름 조각, 재질) — 앞쪽이 먼저. NAME_RULES 가 못 가른 이름에만 쓴다(시안에서 쓸 법한 이름).
EXT_NAME_RULES = [('IR_GLASS', 'ir_glass'), ('FRONT_GLASS', 'ir_glass'), ('GLASS_FRONT', 'ir_glass'), ('GLASS_IR', 'ir_glass'),
                  ('SHELL_PLASTIC', 'petg_shell'), ('LENS_RING', 'al'), ('SHELL_ALU', 'anod_grey'), ('GASKET', 'rubber'), ('ORING', 'rubber'),
                  ('LIGHT_PIPE', 'lightpipe_on'), ('LIGHTPIPE', 'lightpipe_on'), ('BRACKET', 'bracket'), ('HEATSINK', 'anod'), ('HS_SHELL', 'anod'),
                  ('SHELL_AL', 'anod'), ('SCREW', 'steel'), ('SUNSHIELD', 'petg'), ('GLAND', 'plastic'), ('BODY', 'petg'),
                  ('COVER', 'petg')]

# 재질 키 → 질감 종류
LOOK = {'lightpipe': 'clear_coat', 'plug_clear': 'clear_coat', 'petg': 'matte_plastic', 'petg_shell': 'matte_plastic', 'floor': 'studio_floor', 'plastic': 'matte_plastic', 'holder': 'matte_plastic', 'conn_black': 'matte_plastic', 'bracket': 'matte_plastic',
        'anod': 'hairline', 'anod_grey': 'hairline_cut', 'mount': 'hairline', 'al': 'hairline_cut',
        'steel': 'machined', 'brass': 'machined', 'shield': 'machined',
        'pmma': 'clear_coat', 'ir_glass': 'smoke_glass', 'glass': 'lens_coating', 'lens': 'machined',
        'foam': 'soft', 'rubber': 'soft', 'backdrop': 'paper', 'wall': 'paper'}

BEVEL_SKIP = ('PAD', 'FOAM', 'GASKET', 'HARNESS', 'FPC', 'PMMA', 'GLASS', 'LIGHT_PIPE', 'LENS_CIL093')
# 시안 렌더에 같이 넣는 내부 부품(같은 적층) — 앞유리 너머로 렌즈 경통 · 유리가 보이게. 이름 앞부분.
DESIGN_INTERNALS = ('LENS_CIL093', 'SENSOR_BLOCK', 'PEDESTAL', 'CORE_MODULE', 'FPC_M008')


def detail(bpy, m, kind, spec=None):
    spec = spec or {}
    """Principled 재질 m 에 미세 질감을 덧입힌다. 반환: 넣은 것 이름."""
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    N, L = nt.nodes.new, nt.links.new
    tc = N('ShaderNodeTexCoord')

    def noise(scale, detail_=2.0, rough=0.5, vec=None):
        n = N('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail_
        n.inputs['Roughness'].default_value = rough
        L(vec or tc.outputs['Object'], n.inputs['Vector'])
        return n

    def ramp(src, lo, hi):
        r = N('ShaderNodeMapRange')
        r.inputs['From Min'].default_value = 0.3
        r.inputs['From Max'].default_value = 0.7
        r.inputs['To Min'].default_value = lo
        r.inputs['To Max'].default_value = hi
        L(src, r.inputs['Value'])
        return r.outputs['Result']

    def bump(height, strength, dist):
        for lk in list(p.inputs['Normal'].links):       # materials.py 의 층 결 범프는 뗀다(사출 제품 표면으로 본다)
            nt.links.remove(lk)
        b = N('ShaderNodeBump')
        b.inputs['Strength'].default_value = strength
        b.inputs['Distance'].default_value = dist
        L(height, b.inputs['Height'])
        L(b.outputs['Normal'], p.inputs['Normal'])

    def shadow_pass(amount):
        """그림자 광선에는 투명(amount)으로 — Cycles 는 굴절 화선을 계산하지 않아 유리 뒤가 검게 죽는다."""
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        lp = N('ShaderNodeLightPath')
        tr = N('ShaderNodeBsdfTransparent')
        mx = N('ShaderNodeMixShader')
        ml = N('ShaderNodeMath')
        ml.operation = 'MULTIPLY'
        ml.inputs[1].default_value = amount
        L(lp.outputs['Is Shadow Ray'], ml.inputs[0])
        L(ml.outputs['Value'], mx.inputs['Fac'])
        L(p.outputs['BSDF'], mx.inputs[1])
        L(tr.outputs['BSDF'], mx.inputs[2])
        L(mx.outputs['Shader'], out.inputs['Surface'])

    base = p.inputs['Roughness'].default_value
    if kind == 'matte_plastic':     # 미세 요철(입자 약 0.12 mm) + 거칠기 0.45~0.55 얼룩
        bump(noise(1.0 / 0.00012, 3.0).outputs["Fac"], 0.05, 0.00001)
        L(ramp(noise(140.0, 4.0, 0.6).outputs['Fac'], 0.45, 0.55), p.inputs['Roughness'])
    elif kind in ('hairline', 'hairline_cut'):   # 양극산화 알루미늄 헤어라인: 한 방향으로 길게 늘인 잡음 + 이방성 반사
        mp = N('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (60.0, 9000.0, 9000.0)       # X 로 길게(결 방향 = 객체 X)
        L(tc.outputs['Object'], mp.inputs['Vector'])
        h = noise(1.0, 2.0, 0.5, mp.outputs['Vector'])
        bump(h.outputs['Fac'], 0.04, 0.000004)
        L(ramp(h.outputs['Fac'], max(0.05, base - 0.06), base + 0.08), p.inputs['Roughness'])
        p.inputs['Anisotropic'].default_value = 0.7
        p.inputs['Anisotropic Rotation'].default_value = 0.0
        tg = N('ShaderNodeTangent')
        tg.direction_type = 'RADIAL'
        tg.axis = 'Y'
        L(tg.outputs['Tangent'], p.inputs['Tangent'])
        if kind == 'hairline_cut':   # 모서리 다이아컷: 볼록한 모서리(베벨 면)만 밝고 매끈하게 — Cycles Pointiness
            geo = N('ShaderNodeNewGeometry')
            mr = N('ShaderNodeMapRange')
            mr.inputs['From Min'].default_value = 0.53
            mr.inputs['From Max'].default_value = 0.60
            L(geo.outputs['Pointiness'], mr.inputs['Value'])
            col = N('ShaderNodeMix')
            col.data_type = 'RGBA'
            col.inputs['A'].default_value = p.inputs['Base Color'].default_value
            col.inputs['B'].default_value = (0.88, 0.89, 0.90, 1)
            L(mr.outputs['Result'], col.inputs['Factor'])
            L(col.outputs['Result'], p.inputs['Base Color'])
            ro = N('ShaderNodeMix')
            ro.data_type = 'FLOAT'
            src = p.inputs['Roughness'].links[0].from_socket
            L(src, ro.inputs['A'])
            ro.inputs['B'].default_value = 0.07
            L(mr.outputs['Result'], ro.inputs['Factor'])
            L(ro.outputs['Result'], p.inputs['Roughness'])
    elif kind == 'machined':        # 나사 · 쉘: 가는 가공 결 + 거칠기 얼룩
        L(ramp(noise(2500.0, 3.0).outputs['Fac'], max(0.05, base - 0.08), base + 0.08), p.inputs['Roughness'])
        p.inputs['Anisotropic'].default_value = 0.35
    elif kind == 'clear_coat':      # 투명 창: 코팅. 그림자 광선은 통과시켜 창 안쪽(보드 · LED)에 빛이 들어가게 한다
        p.inputs['Coat Weight'].default_value = 0.6
        p.inputs['Coat Roughness'].default_value = 0.02
        shadow_pass(0.92)
    elif kind == 'coated_glass':    # IR 투과 앞유리: 프레넬 반사 + 얇은 코팅(박막 간섭 약하게)
        p.inputs['Coat Weight'].default_value = 0.3        # 얇은 코팅감 — 세게 주면 흰 스튜디오가 비쳐 검정이 회색으로 뜬다
        p.inputs['Coat Roughness'].default_value = 0.015
        if 'Thin Film Thickness' in p.inputs:
            p.inputs['Thin Film Thickness'].default_value = 110.0   # 반사를 줄이는 쪽(반사 방지 코팅 기미)
            p.inputs['Thin Film IOR'].default_value = 1.38
    elif kind == 'lens_coating':    # 렌즈 다층 코팅: 박막 간섭(보라 · 초록 기미)
        p.inputs['Coat Weight'].default_value = 1.0
        p.inputs['Coat Roughness'].default_value = 0.0
        if 'Thin Film Thickness' in p.inputs:
            p.inputs['Thin Film Thickness'].default_value = 420.0
            p.inputs['Thin Film IOR'].default_value = 1.38
        shadow_pass(0.9)
    elif kind == 'soft':            # 폼 · 고무: 번들거림 없는 미세 요철
        bump(noise(1.0 / 0.0002, 2.0).outputs['Fac'], 0.2, 0.00002)
        if 'Sheen Weight' in p.inputs:
            p.inputs['Sheen Weight'].default_value = 0.15
    elif kind == 'smoke_glass':     # 스모크 앞유리: 직진 투과(면당 smoke) + 프레넬 반사. 광축 둘레 window_r mm 원 안은 투명 + 코팅 반사색
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        t = spec.get('smoke', 0.45)
        r = spec.get('window_r', 7.5) * 0.001
        flat = N('ShaderNodeVectorMath')
        flat.operation = 'MULTIPLY'
        flat.inputs[1].default_value = (1, 1, 0)
        L(tc.outputs['Object'], flat.inputs[0])
        ln = N('ShaderNodeVectorMath')
        ln.operation = 'LENGTH'
        L(flat.outputs['Vector'], ln.inputs[0])
        mask = N('ShaderNodeMath')
        mask.operation = 'LESS_THAN'
        mask.inputs[1].default_value = r
        L(ln.outputs['Value'], mask.inputs[0])
        tcol = N('ShaderNodeMix')
        tcol.data_type = 'RGBA'
        tcol.inputs['A'].default_value = (t * 0.97, t * 0.98, t * 1.0, 1)
        tcol.inputs['B'].default_value = (0.97, 0.97, 0.97, 1)
        L(mask.outputs['Value'], tcol.inputs['Factor'])
        tr = N('ShaderNodeBsdfTransparent')
        L(tcol.outputs['Result'], tr.inputs['Color'])
        lw = N('ShaderNodeLayerWeight')
        lw.inputs['Blend'].default_value = 0.45
        cr = N('ShaderNodeValToRGB')            # 다층 코팅 반사색: 보라 → 초록
        cr.color_ramp.elements[0].color = (0.50, 0.22, 0.85, 1)
        cr.color_ramp.elements[1].color = (0.22, 0.85, 0.50, 1)
        L(lw.outputs['Facing'], cr.inputs['Fac'])
        gcol = N('ShaderNodeMix')
        gcol.data_type = 'RGBA'
        gcol.inputs['A'].default_value = (1, 1, 1, 1)
        L(cr.outputs['Color'], gcol.inputs['B'])
        L(mask.outputs['Value'], gcol.inputs['Factor'])
        gl = N('ShaderNodeBsdfGlossy')
        gl.inputs['Roughness'].default_value = spec.get('rough', 0.02)
        L(gcol.outputs['Result'], gl.inputs['Color'])
        fr = N('ShaderNodeFresnel')
        fr.inputs['IOR'].default_value = spec.get('ior', 1.49)
        geo = N('ShaderNodeNewGeometry')
        front = N('ShaderNodeMath')                 # 뒷면에서는 반사 0(직진 투과만) — 안쪽 전반사로 검게 죽지 않게
        front.operation = 'SUBTRACT'
        front.inputs[0].default_value = 1.0
        L(geo.outputs['Backfacing'], front.inputs[1])
        fac = N('ShaderNodeMath')
        fac.operation = 'MULTIPLY'
        L(fr.outputs['Fac'], fac.inputs[0])
        L(front.outputs['Value'], fac.inputs[1])
        mx = N('ShaderNodeMixShader')
        L(fac.outputs['Value'], mx.inputs['Fac'])
        L(tr.outputs['BSDF'], mx.inputs[1])
        L(gl.outputs['BSDF'], mx.inputs[2])
        L(mx.outputs['Shader'], out.inputs['Surface'])
    elif kind == 'studio_floor':    # 바닥: 약한 반사(코팅) + 넓은 얼룩
        p.inputs['Coat Roughness'].default_value = 0.12
        L(ramp(noise(8.0, 3.0).outputs['Fac'], base - 0.05, base + 0.05), p.inputs['Roughness'])
    elif kind == 'paper':           # 배경지 · 도장 벽: 넓은 얼룩만
        L(ramp(noise(8.0, 3.0).outputs['Fac'], base - 0.05, base + 0.05), p.inputs['Roughness'])
    return kind
