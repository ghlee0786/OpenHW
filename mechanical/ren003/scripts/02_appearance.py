"""REN-003 02 (Fusion, M007_assembly 문서) — 재질 표(mechanical/ren003/materials.py)로 모든 바디에 Appearance 배정. [초안 · 미실행]
규칙 순서 (Blender scene.py 와 같은 body_key / name_key):
  · REN_CARRIER / REN_FRONT 안 바디: 모델 이름 = 바디를 가진 컴포넌트 이름(KiCad 모델 파일 이름, ' (n)' 떼고), 색 = STEP 이 준 외관 색(0..1)
      → LAYER_RULES(이름 '<보드>_pad' 등 — Fusion STEP 의 층 바디 이름은 첫 실행 때 확인) → COLOR_OVERRIDES → classify → PART_RULES
  · 그 밖(외함·기구): NAME_RULES (컴포넌트·바디 이름 부분 일치), 못 찾으면 그대로 둠
외관: design.appearances 'ren003_<키>' 가 없으면 MATS[키]['fusion'] 기본 외관(라이브러리 BA5EE55E-…)을 복사해 색(sRGB)·거칠기를 바꿔 만든다.
출력: 배정 표 → main validation/runtime/vd001/render/fusion/appearance.json (재질 키별 바디 수 · 못 가른 바디)
실행: python -I -B mechanical/fusion_run.py mechanical/ren003/scripts/02_appearance.py"""
import adsk.core, adsk.fusion, json, os, re

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 이 스크립트의 체크아웃 경로로 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
OUT = MAIN + r"\validation\runtime\vd001\render\fusion"
APP_LIB = 'BA5EE55E-9982-449B-9D66-9F036540E140'   # Fusion 외관 라이브러리 (이름은 한국어라 ID 로)


def color_of(app_):
    for i in range(app_.appearanceProperties.count):
        p = app_.appearanceProperties.item(i)
        if isinstance(p, adsk.core.ColorProperty) and p.value is not None:
            c = p.value
            return (c.red / 255.0, c.green / 255.0, c.blue / 255.0), c.opacity / 255.0
    return None, 1.0


def run(_c):
    T = {}
    exec(open(LANE + r"\mechanical\ren003\materials.py", encoding="utf-8").read(), T)
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    lib = app.materialLibraries.itemById(APP_LIB)
    made = {}

    def appearance(k):
        if k in made:
            return made[k]
        v = T['MATS'][k]
        a = design.appearances.itemByName('ren003_' + k)
        if a is None:
            a = design.appearances.addByCopy(lib.appearances.itemById(v['fusion']), 'ren003_' + k)
            r, g, b = T['srgb255'](v['rgb'])
            for i in range(a.appearanceProperties.count):
                p = a.appearanceProperties.item(i)
                if isinstance(p, adsk.core.ColorProperty) and p.value is not None:
                    p.value = adsk.core.Color.create(r, g, b, 255)
                elif isinstance(p, adsk.core.FloatProperty) and 'roughness' in p.id.lower():
                    p.value = v.get('rough', 0.5)       # [미확인] Prism 외관의 거칠기 속성 id — 첫 실행 때 이름 출력으로 확인
        made[k] = a
        return a

    count, unknown = {}, []
    for o in [None] + list(root.allOccurrences):
        comp = root if o is None else o.component
        top = o
        while top is not None and top.assemblyContext:
            top = top.assemblyContext
        tn = top.component.name if top is not None else ''
        for b in (comp.bRepBodies if o is None else o.bRepBodies):
            if tn in ('REN_CARRIER', 'REN_FRONT'):
                model = re.sub(r' \(\d+\)$', '', comp.name)
                rgb, alpha = color_of(b.appearance) if b.appearance else (None, 1.0)
                k = T['body_key'](rgb, None, alpha, model=model, board=tn[4:].lower()) if rgb else 'keep'
                if k == 'keep':
                    k = T['body_key'](rgb or (0, 0, 0), None, alpha, model=b.name, board=tn[4:].lower()) if rgb else 'keep'
            elif tn in ('REF_CARRIER', 'REF_FRONT') or not b.isLightBulbOn:
                continue
            else:
                k = T['name_key'](tn + '/' + comp.name + '/' + b.name, default='')
                if not k:
                    unknown.append(tn + '/' + b.name); continue
            if k == 'keep':
                unknown.append(tn + '/' + comp.name + '/' + b.name); continue
            b.appearance = appearance(k)
            count[k] = count.get(k, 0) + 1
    os.makedirs(OUT, exist_ok=True)
    json.dump({'count': count, 'unknown': unknown}, open(OUT + r"\appearance.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('APPEARANCE', count, 'unknown', len(unknown), unknown[:20])
