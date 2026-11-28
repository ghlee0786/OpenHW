"""README 인포그래픽 SVG 4종을 만든다 (stack · block · pipeline · numbers).

python -I docs/readme/tools/make_svgs.py
- 애니메이션은 CSS @keyframes 만 쓴다(script 없음). prefers-reduced-motion 이면 모두 멈춘다.
- 글꼴은 system-ui, 외부 이미지·폰트·href 없음. prefers-color-scheme 로 밝은·어두운 테마.
- 수치는 아래 FACTS 에만 두고, 값마다 저장소 안 출처 경로를 SVG 주석으로 남긴다.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
BASE = "main 995b872"  # 수치를 읽은 커밋

# 값, 출처 (저장소 루트 기준 경로 — 이 파일들의 값을 그대로 옮긴다)
FACTS = {
    "erc": ("0", "hardware/schematic/carrier/carrier-erc.json · hardware/schematic/front/front-erc.json (violations 0, KiCad 10.0.8)"),
    "sim": ("25/25", "hardware/sim/results/SIM-*.json (25개 모두 verdict pass)"),
    "front_drc": ("0 · 0", "hardware/pcb/drc/front-drc.json (violations 0 · unconnected_items 0 · schematic_parity 0)"),
    "carrier_drc": ("0 · 0", "hardware/pcb/drc/carrier-drc.json (violations 0 · unconnected_items 0 · schematic_parity 0, 2026-11-27T15:40)"),
    "models": ("0", "mechanical/m007/judge.md (캐리어·전면 원본 3D 모델 빠짐 0, 03_judge 실패 0)"),
    "stackup": ("4층", "docs/decisions/D-003-working-defaults.md #21 (4층 1.6 mm) · #25 (캐리어 40×54, 전면 40×40)"),
}

STYLE = """<style>
:root{--bg:#ffffff;--card:#f6f8fa;--fg:#1f2328;--mut:#59636e;--ln:#d0d7de;--pcb:#1a7f37;--pcb2:#2da44e;--pcbs:#116329;
--core:#0969da;--cores:#0550ae;--pw:#bf8700;--dat:#0969da;--ctl:#8250df;--ir:#cf222e;--ok:#1a7f37;--wip:#bf8700;--todo:#8c959f;--metal:#57606a}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--card:#161b22;--fg:#e6edf3;--mut:#9198a1;--ln:#3d444d;--pcb:#2ea043;--pcb2:#3fb950;--pcbs:#1a7f37;
--core:#4493f8;--cores:#1f6feb;--pw:#d29922;--dat:#4493f8;--ctl:#ab7df8;--ir:#f85149;--ok:#3fb950;--wip:#d29922;--todo:#6e7681;--metal:#8b949e}}
text{font-family:system-ui,-apple-system,"Segoe UI","Noto Sans KR","Apple SD Gothic Neo",sans-serif;fill:var(--fg)}
.t{font-size:22px;font-weight:700}.s{font-size:13px;fill:var(--mut)}.l{font-size:14px;font-weight:600}.m{font-size:12px;fill:var(--mut)}
.bg{fill:var(--bg);stroke:var(--ln)}
%s
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style>"""


def svg(name, w, h, title, desc, css, body, sources):
    notes = "\n".join(f"<!-- 출처 {k}: {v} -->" for k, v in sources)
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-labelledby="t d">\n'
         f"<!-- 생성: docs/readme/tools/make_svgs.py · 수치 기준 {BASE} -->\n{notes}\n"
         f"<title id=\"t\">{title}</title><desc id=\"d\">{desc}</desc>\n{STYLE % css}\n"
         f'<rect class="bg" x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14"/>\n{body}\n</svg>\n')
    (OUT / name).write_text(s, encoding="utf-8", newline="\n")
    return len(s.encode("utf-8"))


def slab(x, y, w, d, t, top, side, front):
    """비스듬히 본 판(윗면·앞면·옆면). (x, y) = 앞 아래 왼쪽 모서리 기준 윗면 앞 모서리."""
    dx, dy = d * 0.55, d * 0.32
    return (f'<polygon points="{x},{y} {x + w},{y} {x + w + dx},{y - dy} {x + dx},{y - dy}" fill="{top}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{t}" fill="{front}"/>'
            f'<polygon points="{x + w},{y} {x + w + dx},{y - dy} {x + w + dx},{y - dy + t} {x + w},{y + t}" fill="{side}"/>')


def stack():
    css = """.ex1{animation:up 7s ease-in-out infinite}.ex3{animation:dn 7s ease-in-out infinite}
@keyframes up{0%,18%{transform:translateY(-58px)}42%,78%{transform:translateY(0)}100%{transform:translateY(-58px)}}
@keyframes dn{0%,18%{transform:translateY(58px)}42%,78%{transform:translateY(0)}100%{transform:translateY(58px)}}
.ax{stroke:var(--ir);stroke-width:2;stroke-dasharray:6 6;animation:flow 1.2s linear infinite}
@keyframes flow{to{stroke-dashoffset:-12}}
.ld{stroke:var(--mut);stroke-width:1;fill:none}.btb{fill:var(--metal)}.led{fill:var(--ir)}
.hz{stroke:var(--pw);stroke-width:2.5;fill:none;stroke-dasharray:4 3}"""
    x0, yf, yc, yb = 110, 230, 286, 342  # 윗면 앞 모서리 y: 전면 · 코어 · 캐리어 (조립 상태)
    # 그리는 순서: 아래(캐리어) → 코어 → 위(전면) — 위에서 비스듬히 보므로 위층이 아래층을 가린다
    car = slab(x0, yb, 200, 190, 10, "var(--pcb2)", "var(--pcbs)", "var(--pcb)")
    btb2 = f'<rect class="btb" x="{x0 + 100}" y="{yb - 62}" width="70" height="18" rx="2"/>'
    core = slab(x0 + 30, yc, 140, 140, 9, "var(--core)", "var(--cores)", "var(--cores)")
    btb1 = f'<rect class="btb" x="{x0 + 80}" y="{yc - 52}" width="70" height="18" rx="2"/>'
    front = slab(x0 + 20, yf, 160, 150, 10, "var(--pcb2)", "var(--pcbs)", "var(--pcb)")
    cx, cy = x0 + 20 + 80 + 41, yf - 24  # 렌즈 중심 (전면 윗면 가운데)
    lens = (f'<rect x="{cx - 22}" y="{cy - 30}" width="44" height="30" rx="4" fill="var(--metal)"/>'
            f'<ellipse cx="{cx}" cy="{cy - 30}" rx="22" ry="8" fill="var(--fg)" opacity=".75"/>'
            f'<ellipse cx="{cx}" cy="{cy - 30}" rx="12" ry="4" fill="var(--core)" opacity=".85"/>')
    leds = "".join(f'<rect class="led" x="{x}" y="{y}" width="12" height="7" rx="1.5"/>'
                   for x, y in [(x0 + 40, yf - 14), (x0 + 168, yf - 14), (x0 + 82, yf - 40), (x0 + 210, yf - 40)])
    harness = f'<path class="hz" d="M{x0 + 300},{yb - 40} C{x0 + 350},{yb - 70} {x0 + 340},{yf - 10} {x0 + 262},{yf - 30}"/>'
    axis = f'<line class="ax" x1="{cx}" y1="{cy - 40}" x2="{cx}" y2="88"/>'
    body = f"""<text class="t" x="28" y="40">3층 적층</text>
<text class="s" x="28" y="62">전면 보드 · 코어 모듈 · 캐리어 보드 (분해 ↔ 결합)</text>
{axis}<text class="m" x="{cx + 12}" y="100">광축 (+Z)</text>
<g class="ex3">{car}</g>
<g>{btb2}{core}</g>
<g class="ex1">{btb1}{front}{lens}{leds}</g>
{harness}
<path class="ld" d="M{x0 + 290},{yf - 50} H520"/><path class="ld" d="M{x0 + 250},{yc - 30} H520"/><path class="ld" d="M{x0 + 320},{yb - 30} H520"/>
<text class="l" x="528" y="{yf - 54}">전면 보드 · 40×40 mm · 4층</text>
<text class="m" x="528" y="{yf - 36}">센서 · M12 렌즈 · IR-cut · IR LED 850 nm · 조도센서</text>
<text class="l" x="528" y="{yc - 34}">코어 모듈 (구매품)</text>
<text class="m" x="528" y="{yc - 16}">reCamera Core 2002 · SG2002 SoC · NPU</text>
<text class="l" x="528" y="{yb - 34}">캐리어 보드 · 40×54 mm · 4층</text>
<text class="m" x="528" y="{yb - 16}">12 V 입력 · 보호 · 5 V 강압 · 이더넷 · USB-C · microSD</text>
<rect x="528" y="372" width="12" height="8" class="btb"/><text class="m" x="548" y="380">보드 간 BTB 0.5 mm 60핀 ×2 · 결합 높이 8.0 mm</text>
<path class="hz" d="M528,400 h12"/><text class="m" x="548" y="404">GH 6핀 하니스 35 mm (캐리어 ↔ 전면)</text>
<rect x="528" y="418" width="12" height="7" class="led"/><text class="m" x="548" y="426">IR LED</text>"""
    src = [("크기·층", FACTS["stackup"][1]), ("BTB 높이", "mechanical/m003/params.md btb_h 8.0 · docs/decisions/D-003-working-defaults.md #44"),
           ("하니스", "docs/decisions/D-003-working-defaults.md #25"), ("광학·IR", "docs/decisions/D-003-working-defaults.md #4 #6 #17")]
    return svg("stack.svg", 900, 450, "3층 적층 구조", "전면 보드, 코어 모듈, 캐리어 보드가 BTB 커넥터로 결합되는 분해·결합 애니메이션", css, body, src)


def block():
    css = """.b{fill:var(--card);stroke:var(--ln);stroke-width:1.2}.bc{fill:var(--card);stroke:var(--core);stroke-width:2}
.g{fill:none;stroke:var(--ln);stroke-width:1.2;stroke-dasharray:3 4}
.pw,.dt,.ct{fill:none;stroke-width:2.4;stroke-dasharray:7 6;animation:f 1.4s linear infinite}
.pw{stroke:var(--pw)}.dt{stroke:var(--dat)}.ct{stroke:var(--ctl);stroke-width:1.8;animation-duration:2.2s}
.rv{animation-direction:reverse}
@keyframes f{to{stroke-dashoffset:-26}}"""

    def box(x, y, w, h, a, b="", cls="b"):
        t = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/><text class="l" x="{x + 10}" y="{y + 21}">{a}</text>'
        return t + (f'<text class="m" x="{x + 10}" y="{y + 38}">{b}</text>' if b else "")

    body = f"""<text class="t" x="28" y="40">시스템 블록도</text>
<text class="s" x="28" y="62">전원 · 영상 · 제어 · 네트워크 흐름</text>
<rect class="g" x="20" y="80" width="300" height="420" rx="12"/><text class="m" x="32" y="98">캐리어 보드</text>
<rect class="g" x="345" y="80" width="210" height="420" rx="12"/><text class="m" x="357" y="98">코어 모듈</text>
<rect class="g" x="580" y="80" width="300" height="420" rx="12"/><text class="m" x="592" y="98">전면 보드</text>
{box(36, 110, 128, 46, "12 V DC 입력")}
{box(36, 176, 128, 46, "퓨즈 · 역접속 보호")}
{box(36, 242, 128, 46, "5 V 강압", "TPS54302 → 코어")}
{box(36, 308, 128, 46, "eFuse (IR 전원)", "TPS26600")}
{box(180, 110, 128, 46, "이더넷 RJ45", "10/100 · ESD")}
{box(180, 176, 128, 46, "USB-C", "USB 2.0 · ESD")}
{box(180, 242, 128, 46, "microSD", "SDIO")}
{box(180, 308, 128, 46, "디버그 UART")}
{box(36, 410, 272, 46, "GH 6핀 하니스 → 전면", "12 V IR 전원 · 제어선")}
{box(360, 150, 180, 220, "SG2002", "SoC · NPU", "bc")}
<text class="m" x="370" y="210">reCamera Core 2002</text><text class="m" x="370" y="228">Linux (커널 5.10)</text>
<text class="m" x="370" y="246">사람 감지 모델 (NPU)</text>
<text class="m" x="370" y="360">BTB J2 ← 캐리어 · J1 → 전면</text>
{box(596, 110, 268, 46, "이미지 센서 GC2053", "2 MP · MIPI CSI")}
{box(596, 176, 268, 46, "IR-cut 전환", "DRV8837 → 필터 코일")}
{box(596, 242, 268, 46, "조도센서 LTR-329", "I2C · 주야 판별")}
{box(596, 308, 268, 46, "IR LED 구동 ×2", "AL8860 · 850 nm LED 자리 4")}
{box(596, 410, 268, 46, "M12 렌즈 · 광축", "수평 화각 약 90°")}
<path class="pw" d="M100,156 V176"/><path class="pw" d="M100,222 V242"/><path class="pw" d="M164,258 H172 V232 H360"/>
<path class="pw" d="M36,199 H28 V331 H36"/><path class="pw" d="M100,354 V410"/><path class="pw" d="M308,433 H570 V331 H596"/>
<path class="dt rv" d="M308,133 H360"/><path class="dt" d="M308,199 H360"/><path class="dt" d="M308,265 H340 V300 H360"/>
<path class="dt rv" d="M596,133 H540"/><path class="ct" d="M540,199 H596"/><path class="ct rv" d="M540,265 H596"/><path class="ct" d="M540,320 H596"/>
<path class="ct" d="M308,331 H360"/>
<path class="pw" d="M40,524 h26"/><text class="m" x="72" y="528">전원</text>
<path class="dt" d="M120,524 h26"/><text class="m" x="152" y="528">영상·데이터</text>
<path class="ct" d="M240,524 h26"/><text class="m" x="272" y="528">제어 (GPIO · I2C · PWM)</text>"""
    src = [("전원", "docs/decisions/D-003-working-defaults.md #10 #22 · carrier.kicad_pcb 넷 /12V_IN → U1 · U2 → /12V_IR → J7"), ("네트워크", "D-003 #11"), ("센서", "D-003 #5 #17"),
           ("조도", "D-003 #7 #18"), ("부품", "hardware/schematic/carrier/carrier.kicad_pcb · hardware/schematic/front/front.kicad_pcb 값 필드"),
           ("모델", "D-003 #19"), ("커널", "D-003 #1")]
    return svg("block.svg", 900, 550, "시스템 블록도", "12V 입력에서 코어 모듈까지 전원, 센서와 네트워크 신호 흐름", css, body, src)


STAGES = [  # (이름, 상태, 한 줄) — 2026-11-28 기준
    ("요구사항", "ok", "제품 기획·기본값"),
    ("회로도", "ok", "ERC 0 (2장)"),
    ("시뮬레이션", "ok", "25/25 통과"),
    ("PCB 배선", "ok", "전면 · 캐리어 완료"),
    ("DRC", "ok", "두 보드 0 · 0"),
    ("3D 검증", "ok", "27항목 불합격 0 · 간섭 0"),
    ("케이스", "ok", "시안 A 상세 설계"),
    ("렌더", "ok", "6컷 + 영상 · 사용자 확인 완료"),
]


def pipeline():
    css = """.ln{stroke:var(--ln);stroke-width:4}.pr{stroke:var(--ok);stroke-width:4;stroke-dasharray:640;animation:p 3s ease-out both}
@keyframes p{from{stroke-dashoffset:640}to{stroke-dashoffset:0}}
.ok{fill:var(--ok)}.wip{fill:var(--wip)}.todo{fill:var(--todo)}
.ring{fill:none;stroke:var(--wip);stroke-width:2;transform-box:fill-box;transform-origin:center;animation:r 1.8s ease-out infinite}
@keyframes r{0%{transform:scale(1);opacity:.9}100%{transform:scale(1.9);opacity:0}}
.ck{stroke:#fff;stroke-width:3;fill:none;stroke-linecap:round;stroke-linejoin:round}"""
    n, x0, gap, cy = len(STAGES), 70, 110, 140
    last_ok = max(i for i, s in enumerate(STAGES) if s[1] == "ok")
    parts = [f'<line class="ln" x1="{x0}" y1="{cy}" x2="{x0 + gap * (n - 1)}" y2="{cy}"/>',
             f'<line class="pr" x1="{x0}" y1="{cy}" x2="{x0 + gap * (last_ok + 1)}" y2="{cy}"/>']
    for i, (name, st, note) in enumerate(STAGES):
        x = x0 + gap * i
        if st == "wip":
            parts.append(f'<circle class="ring" cx="{x}" cy="{cy}" r="16" style="animation-delay:{i * 0.25:.2f}s"/>')
        parts.append(f'<circle class="{st}" cx="{x}" cy="{cy}" r="16"/>')
        if st == "ok":
            parts.append(f'<path class="ck" d="M{x - 7},{cy} l5,5 l9,-10"/>')
        elif st == "wip":
            parts.append(f'<circle cx="{x}" cy="{cy}" r="5" fill="#fff"/>')
        parts.append(f'<text class="l" x="{x}" y="{cy - 30}" text-anchor="middle">{name}</text>')
        parts.append(f'<text class="m" x="{x}" y="{cy + 38}" text-anchor="middle">{note.split(" · ")[0]}</text>')
        if " · " in note:
            parts.append(f'<text class="m" x="{x}" y="{cy + 54}" text-anchor="middle">{note.split(" · ", 1)[1]}</text>')
    legend = ('<circle class="ok" cx="40" cy="236" r="7"/><text class="m" x="54" y="240">완료</text>'
              '<circle class="wip" cx="110" cy="236" r="7"/><text class="m" x="124" y="240">진행 중</text>'
              '<circle class="todo" cx="196" cy="236" r="7"/><text class="m" x="210" y="240">대기</text>'
              '<text class="m" x="880" y="240" text-anchor="end">2026-11-28 기준 · 가상 설계 단계 (실물 제작 전)</text>')
    body = ('<text class="t" x="28" y="40">설계 흐름</text><text class="s" x="28" y="62">요구 → 회로도 → 시뮬레이션 → PCB → DRC → 3D → 케이스 → 렌더</text>\n'
            + "\n".join(parts) + "\n" + legend)
    src = [("회로도", FACTS["erc"][1]), ("시뮬레이션", FACTS["sim"][1]), ("DRC", FACTS["front_drc"][1] + " · " + FACTS["carrier_drc"][1]),
           ("3D", "mechanical/m010/run_A.md (run_case.py 두 보드 995b872 · 케이스 A 종료 0, 조건 5 27항목 불합격 0)"),
           ("케이스", "mechanical/design/o126_a.md · docs/decisions/D-003-working-defaults.md #67 (O-126 시안 A)"),
           ("렌더", "docs/renders/final/blender-*.png · blender-turntable.mp4 (O-126, 사용자 확인 2026-11-28)")]
    return svg("pipeline.svg", 900, 260, "설계 흐름과 진행 상태", "요구사항부터 렌더까지 8단계의 완료·진행 중·대기 상태", css, body, src)


def numbers():
    css = """.c{fill:var(--card);stroke:var(--ln)}.cd{animation:in .7s ease-out both}
@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.big{font-size:40px;font-weight:800}.okc{fill:var(--ok)}.wipc{fill:var(--wip)}
.dot{fill:var(--wip)}.pul{fill:none;stroke:var(--wip);stroke-width:2;transform-box:fill-box;transform-origin:center;animation:r 1.8s ease-out infinite}
@keyframes r{0%{transform:scale(1);opacity:.9}100%{transform:scale(2.2);opacity:0}}"""
    cards = [
        ("erc", "okc", "회로도 ERC 위반", "캐리어 · 전면 (KiCad 10)"),
        ("sim", "okc", "회로 시뮬레이션 통과", "ngspice-47 · 결과 파일 25개"),
        ("front_drc", "okc", "전면 DRC 위반 · 미연결", "parity 0"),
        ("carrier_drc", "okc", "캐리어 DRC 위반 · 미연결", "parity 0"),
        ("models", "okc", "3D 모델 빠짐", "두 보드 · 조립 판정 실패 0"),
        ("stackup", "okc", "1.6 mm PCB", "전면 40×40 · 캐리어 40×54 mm"),
    ]
    parts = []
    for i, (k, cls, label, sub) in enumerate(cards):
        x, y = 28 + (i % 3) * 286, 84 + (i // 3) * 150
        bar = (f'<circle class="pul" cx="{x + 244}" cy="{y + 30}" r="6"/>'
               f'<circle class="dot" cx="{x + 244}" cy="{y + 30}" r="6"/>') if cls == "wipc" else ""
        parts.append(f'<g class="cd" style="animation-delay:{0.15 * i:.2f}s"><rect class="c" x="{x}" y="{y}" width="270" height="134" rx="12"/>'
                     f'<text class="big {cls}" x="{x + 20}" y="{y + 56}">{FACTS[k][0]}</text>'
                     f'<text class="l" x="{x + 20}" y="{y + 84}">{label}</text><text class="m" x="{x + 20}" y="{y + 104}">{sub}</text>{bar}</g>')
    body = ('<text class="t" x="28" y="40">핵심 수치</text><text class="s" x="28" y="62">저장소의 결과 파일 값 (2026-11-27)</text>\n'
            + "\n".join(parts))
    src = [(k, v[1]) for k, v in FACTS.items()] + [("시뮬레이터", "hardware/sim/README.md (ngspice-47)")]
    return svg("numbers.svg", 900, 400, "핵심 수치", "ERC, 시뮬레이션, DRC, 3D 모델, 적층 수치 카드", css, body, src)


def icon():
    """96 px 아이콘: 칩(핀 달린 사각형) 안에 카메라 렌즈 — 파랑 한 계열 두 톤."""
    css = """.c1{fill:var(--core)}.c2{fill:var(--cores)}.pin{fill:var(--cores)}
.iris{fill:none;stroke:var(--bg);stroke-width:2.5;transform-box:fill-box;transform-origin:center;animation:ir 3.2s ease-in-out infinite}
@keyframes ir{0%,100%{transform:scale(1)}50%{transform:scale(.72)}}
.gl{fill:var(--bg);opacity:.85;animation:gl 3.2s ease-in-out infinite}@keyframes gl{0%,100%{opacity:.85}50%{opacity:.35}}"""
    pins = "".join(f'<rect class="pin" x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5"/>'
                   for k in (30, 44, 58) for x, y, w, h in [(k, 10, 8, 10), (k, 76, 8, 10), (10, k, 10, 8), (76, k, 10, 8)])
    body = (f'{pins}<rect class="c2" x="18" y="18" width="60" height="60" rx="10"/>'
            '<rect class="c1" x="22" y="22" width="52" height="52" rx="8"/>'
            '<circle class="c2" cx="48" cy="48" r="17"/><circle cx="48" cy="48" r="11" fill="var(--fg)" opacity=".85"/>'
            '<circle class="iris" cx="48" cy="48" r="7"/><circle class="gl" cx="43" cy="43" r="3"/>')
    return svg("icon.svg", 96, 96, "OpenHW 아이콘", "칩 안에 카메라 렌즈가 있는 아이콘", css, body, [])


def hero():
    """880 폭 히어로: 피사체 → 렌즈·센서(전면) → SG2002 AI → 캐리어 → 결과, 빛·신호 흐름."""
    css = """.ray{stroke:var(--wip);stroke-width:2;stroke-dasharray:4 8;animation:f 1.2s linear infinite}
.sig{fill:none;stroke:var(--dat);stroke-width:3;stroke-dasharray:10 10;animation:f 1s linear infinite}
@keyframes f{to{stroke-dashoffset:-24}}
.card{fill:var(--card);stroke:var(--ln)}.pcb{fill:var(--pcb2)}.chip{fill:var(--core)}
.glow{fill:none;stroke:var(--core);stroke-width:3;transform-box:fill-box;transform-origin:center;animation:gw 2s ease-out infinite}
@keyframes gw{0%{transform:scale(1);opacity:.8}100%{transform:scale(1.35);opacity:0}}
.box{fill:none;stroke:var(--ok);stroke-width:2.5;stroke-dasharray:180;animation:bx 3s ease-in-out infinite}
@keyframes bx{0%{stroke-dashoffset:180}35%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:180}}
.tag{fill:var(--ok)}.tagt{fill:#fff;font-size:11px;font-weight:700}
.st{font-size:15px;font-weight:700}.sm{font-size:12px;fill:var(--mut)}"""
    person = '<circle cx="{0}" cy="{1}" r="11" fill="var(--mut)"/><path d="M{2},{3} q{4},-30 {5},0 z" fill="var(--mut)"/>'
    p1 = person.format(70, 118, 46, 172, 24, 48)
    rays = "".join(f'<line class="ray" x1="98" y1="{y}" x2="196" y2="{136 + (y - 136) // 4}"/>' for y in (104, 126, 148, 170))
    front = ('<rect class="card" x="196" y="78" width="130" height="118" rx="12"/>'
             '<rect class="pcb" x="214" y="96" width="94" height="66" rx="6"/>'
             '<circle cx="261" cy="129" r="22" fill="var(--metal)"/><circle cx="261" cy="129" r="13" fill="var(--fg)" opacity=".85"/>'
             '<circle cx="256" cy="124" r="3" fill="var(--bg)" opacity=".8"/>'
             + "".join(f'<rect x="{x}" y="{y}" width="9" height="6" rx="1.5" fill="var(--ir)"/>' for x, y in [(220, 102), (293, 102), (220, 150), (293, 150)]))
    core = ('<rect class="card" x="380" y="78" width="130" height="118" rx="12"/>'
            '<rect class="glow" x="414" y="96" width="62" height="62" rx="8"/>'
            '<rect class="chip" x="414" y="96" width="62" height="62" rx="8"/>'
            '<text x="445" y="124" text-anchor="middle" style="fill:#fff;font-size:12px;font-weight:700">SG2002</text>'
            '<text x="445" y="142" text-anchor="middle" style="fill:#fff;font-size:11px">NPU</text>')
    car = ('<rect class="card" x="564" y="78" width="130" height="118" rx="12"/>'
           '<rect class="pcb" x="582" y="96" width="94" height="66" rx="6"/>'
           + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="var(--metal)"/>'
                     for x, y, w, h in [(590, 104, 24, 18), (622, 104, 16, 10), (646, 104, 22, 12), (590, 136, 14, 18)]))
    res = ('<rect class="card" x="742" y="78" width="118" height="118" rx="12"/>'
           '<rect x="756" y="92" width="90" height="70" rx="6" fill="var(--bg)" stroke="var(--ln)"/>'
           + person.format(801, 116, 789, 156, 12, 24).replace('r="11"', 'r="7"')
           + '<rect class="box" x="784" y="104" width="34" height="54" rx="3"/>'
           '<rect class="tag" x="784" y="94" width="40" height="13" rx="3"/><text class="tagt" x="788" y="104">사람</text>')
    sigs = ('<path class="sig" d="M326,137 H380"/><path class="sig" d="M510,137 H564"/><path class="sig" d="M694,137 H742"/>')
    labels = "".join(f'<text class="st" x="{x}" y="224" text-anchor="middle">{a}</text><text class="sm" x="{x}" y="244" text-anchor="middle">{b}</text>'
                     for x, a, b in [(70, "피사체", "가시광 · 850 nm IR"), (261, "렌즈 · 센서", "전면 보드 · GC2053"),
                                     (445, "AI 추론", "SG2002 코어 · NPU"), (629, "캐리어", "이더넷 · USB · microSD"),
                                     (801, "결과", "감지 이벤트 전송")])
    body = (f'<text class="t" x="28" y="44">보고 → 판단하고 → 알린다</text>'
            f'<text class="s" x="28" y="64">카메라 영상을 보드 안의 NPU가 바로 분석해 사람 감지 이벤트를 보낸다</text>'
            f'{p1}{rays}{front}{core}{car}{res}{sigs}{labels}'
            '<text class="sm" x="852" y="284" text-anchor="end">가상 설계 단계 · 2026-11-27</text>')
    src = [("흐름", "docs/planning/product-brief.md (카메라 입력 → NPU 감지 → 네트워크 이벤트)"), ("센서·IR", "docs/decisions/D-003-working-defaults.md #5 #6"),
           ("감지", "D-003 #3 #19"), ("캐리어", "D-003 #8 #11")]
    return svg("hero.svg", 880, 300, "OpenHW 엣지 AI 카메라 흐름", "피사체에서 렌즈와 센서, SG2002 NPU, 캐리어 보드를 거쳐 사람 감지 결과가 나가는 흐름 애니메이션", css, body, src)


if __name__ == "__main__":
    for f in (stack, block, pipeline, numbers, icon, hero):
        print(f.__name__, f())
