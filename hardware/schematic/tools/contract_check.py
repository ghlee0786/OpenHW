"""C-014 (VD-001 조건 1): hw-fw-contract.md 의 핀·넷 표와 값 문구를 두 보드 kicad-cli 넷리스트와 한 줄씩 대조한다.

대조하는 것 (계약 절):
  4절  캐리어 BTB 60핀 (넷, 짝 핀 홀짝 반전, 「미사용」= NC)        5절  전면 BTB 60핀 (같은 규칙)
  5.1  DF30 24P 센서 커넥터 핀                                     6절  I2C2 풀업 레일·LTR-329 결선
  7절  GPIO 표 (커넥터 핀 넷, 4·5절과 같은 넷인지, 「→ J7-n」, DRV8837 IN1/IN2)
  12A  하니스 J7-n ↔ J4-(7−n) 결선                                 3.1·9·12절 전원 레일·보호 값 문구 (정규식으로 읽은 값)
  DNP  계약 문구가 실장/미실장을 말하는 부품 · 12B절 DNP 목록 = 넷리스트 DNP 집합(값 포함)
함께 (같은 실행): 두 보드 ERC --exit-code-violations, netcompare(기준 커밋 넷리스트 대비).

usage:
  python contract_check.py [--contract FILE] [--base ea1336b] [--md OUT.md] [--json OUT.json]
  python contract_check.py --selftest          # 고장 주입: 계약 표 한 줄을 바꾼 사본마다 불일치가 늘어나는지
종료 코드 = 계약 불일치 수 + ERC 실패 보드 수 + netcompare 차이 보드 수 (255 상한). --selftest 는 놓친 고장 수.
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCH = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(SCH))
KICAD_CLI = os.environ.get('KICAD_CLI') or next((p for p in (
    os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe'),
    r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe') if os.path.exists(p)), 'kicad-cli')
BOARDS = ('carrier', 'front')

# 계약의 코어 넷 이름 → 회로도 넷 이름. 근거: 3.1절(VIN = 5V_SYS 공급, +3V3 = 코어 3V3), 6절(IIC1 → 예비 I2C 패드),
# 7절 「넷」 열(SPARE1·IR_LED_EN·STATUS_LED·ALS_INT_RSV(PWR_WAKEUP1)·GPIO15/IR_CUT), 4절 BT_UART1 = UART1 예비 패드.
# 「/3V3」 꼬리표는 전압 표기라 뗀다 (SDIO_D3/3V3 → SDIO_D3).
ALIAS = {
    'carrier': {'VIN': '5V_SYS', '+3V3': 'CORE_3V3', 'MIPI_TXM2/IIC1_SDA/PWM': 'I2C1_SDA', 'MIPI_TXP2/IIC1_SCL/PWM': 'I2C1_SCL',
                'MIPI_TXM1/IIC2_SDA/PWM': 'SPARE1', 'MIPI_TXP1/IIC2_SCL/PWM': 'IR_LED_EN', 'MIPI_TXM0/GPIO12/PWM': 'STATUS_LED',
                'PWR_WAKEUP1': 'ALS_INT_RSV', 'BT_UART1_RX': 'UART1_RX', 'BT_UART1_TX': 'UART1_TX',
                'BT_UART1_CTS': 'UART1_CTS', 'BT_UART1_RTS': 'UART1_RTS'},
    'front': {'1V8': 'CORE_1V8', '3V3': 'CORE_3V3', 'GPIO15/IR_CUT': 'IR_CUT'},
}

def alias(board, n):
    n = n.strip().strip('*')
    return ALIAS[board].get(n, n.replace('/3V3', ''))

# ---------------------------------------------------------------- netlist
class Net:
    def __init__(self, path):
        t = open(path, encoding='utf-8').read()
        self.comps, self.dnp = {}, set()
        for m in re.finditer(r'\(comp\s+\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)(.*?)(?=\n\t\t\(comp\s|\n\t\)\n)', t, re.S):
            self.comps[m.group(1)] = m.group(2)
            if '(name "dnp")' in m.group(3): self.dnp.add(m.group(1))
        self.pin, self.func, self.members = {}, {}, {}
        for m in re.finditer(r'\(net\s+\(code "?\d+"?\)\s+\(name "([^"]*)"\)(.*?)\n\t\t\)', t, re.S):
            name = m.group(1).rsplit('/', 1)[-1]
            for r, p, f in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)(?:\s*\(pinfunction "([^"]*)"\))?', m.group(2)):
                self.pin[(r, p)] = name
                if f: self.func[(r, f.rsplit('_', 1)[0])] = name
                self.members.setdefault(name, []).append((r, p))

    def at(self, ref, pin):
        n = self.pin.get((ref, str(pin)), '')
        return 'NC' if not n or n.startswith('unconnected-') else n

    def fn(self, ref, func):
        n = self.func.get((ref, func), '')
        return 'NC' if not n or n.startswith('unconnected-') else n

    def two_pin(self, a, b):
        """refs of 2-pin parts between nets a and b"""
        out = []
        for r in self.comps:
            ns = sorted(n for (rr, p), n in self.pin.items() if rr == r)
            if len(ns) == 2 and sorted((a, b)) == ns: out.append(r)
        return out

# ---------------------------------------------------------------- contract parsing
def table_after(t, heading):
    """rows (list of cells) of the first markdown table after the heading line that starts with `heading`"""
    i = t.index('\n' + heading)
    rows = []
    for line in t[i:].split('\n')[1:]:
        if line.startswith('|'):
            if set(line.replace('|', '').strip()) <= set('-: '): continue
            rows.append([c.strip() for c in line.strip().strip('|').split('|')])
        elif rows:
            break
    return rows[1:]  # drop header

FOUND = {}
def find(t, rx):
    out = [m.groups() for m in re.finditer(rx, t)]
    FOUND[rx] = FOUND.get(rx, 0) + len(out)
    return out

def mate(p):
    p = int(p); return p + 1 if p % 2 else p - 1

# ---------------------------------------------------------------- checks
def check(t, N):
    res = []; FOUND.clear()
    def add(sec, item, exp, act, info=False):
        res.append({'sec': sec, 'item': item, 'expected': str(exp), 'actual': str(act), 'ok': str(exp) == str(act), 'info': info})
    C, F = N['carrier'], N['front']

    # 4절·5절 BTB
    btb = {}
    for sec, board, head in (('4절', 'carrier', '## 4.'), ('5절', 'front', '## 5. ')):
        net = N[board]
        for row in table_after(t, head):
            pin, core, cn, use = row[0], row[1], row[2], row[5]
            add(sec, f'{board} J1-{pin} 짝 핀', mate(pin), core)
            nc = cn == 'NC' or (use.startswith('미사용') and '시험점' not in use)
            exp = 'NC' if nc else alias(board, cn)
            btb[(board, pin)] = exp
            add(sec, f'{board} J1-{pin} ({cn})', exp, net.at('J1', pin))

    # 5.1 DF30
    kw = {'MCLK': 'CAM_MCLK', 'AVDD': 'CAM_AVDD', 'IOVDD': 'CAM_IOVDD', 'DVDD': 'CAM_AVDD', 'RESET': 'CAM_RESET'}
    for row in table_after(t, '### 5.1'):
        for pins, txt in ((row[0], row[1]), (row[2], row[3])):
            first = re.match(r'\**([A-Z0-9_]+)', txt).group(1)
            exp = kw.get(first, first)
            a, _, b = pins.partition('~')
            for p in range(int(a), int(b or a) + 1):
                add('5.1', f'front J3-{p} ({txt[:24]})', exp, F.at('J3', p))
    for ref, val in find(t, r'MCLK 24MHz \(X1 → (R\d+) ([\d.]+)Ω[,)]'):
        r = F.two_pin(F.fn('X1', 'OUT'), F.at('J3', 4))
        add('5.1', 'MCLK 직렬 저항 (X1 OUT → J3-4) 참조·값', f'{ref} {val}R', ' '.join(f'{x} {F.comps[x]}' for x in r) or '없음')

    # 6절 I2C2
    for val, rail in find(t, r'전면 보드가 ([\d.]+k)를 \*\*(\w+)'):
        for sig in ('CAM_I2C2_SDA', 'CAM_I2C2_SCL'):
            add('6절', f'{sig} 풀업 {val} → {rail}', val, ','.join(F.comps[r] for r in F.two_pin(rail, sig)) or '없음')
    for (rail,) in find(t, r'I2C2 풀업은 (\w+)'):
        add('13절 C18', 'I2C2 풀업 레일 (C18 ④ 문구)', rail, 'CAM_1V8' if F.two_pin('CAM_1V8', 'CAM_I2C2_SDA') else '?')
    if find(t, r'LTR-329 VDD = 전면 2\.8V'):
        u = next(r for r, v in F.comps.items() if v.startswith('LTR-329'))
        add('6절', 'LTR-329 VDD = 전면 2.8V', 'FRONT_2V8', F.fn(u, 'VDD'))
        add('6절', 'LTR-329 SDA = CAM_I2C2', 'CAM_I2C2_SDA', F.fn(u, 'SDA'))
        add('6절', 'LTR-329 SCL = CAM_I2C2', 'CAM_I2C2_SCL', F.fn(u, 'SCL'))

    # 7절 GPIO
    for row in table_after(t, '## 7.'):
        func, cn, conn, link = row[0], row[1], row[4], row[8]
        m = re.match(r'J(\d)-(\d+) / (전면|캐리어) (\d+)(?: → (?:FPC |J7-)(\d+))?', conn)
        board = 'front' if m.group(3) == '전면' else 'carrier'
        pin = m.group(4)
        add('7절', f'{func}: 코어 J{m.group(1)}-{m.group(2)} ↔ {board} {pin} 짝', mate(pin), m.group(2))
        add('7절', f'{func}: {board} J1-{pin} 넷', alias(board, cn), N[board].at('J1', pin))
        add('7절', f'{func}: 4·5절 표의 같은 핀 넷과 같음', alias(board, cn), btb.get((board, pin)))
        if m.group(5):
            add('7절', f'{func}: 「→ {m.group(5)}」 = 캐리어 J7-{m.group(5)}', alias(board, cn), C.at('J7', m.group(5)))
        d = re.search(r'DRV8837 (IN\d)', link)
        if d:
            u = next(r for r, v in F.comps.items() if v.startswith('DRV8837'))
            add('7절', f'{func}: DRV8837 {d.group(1)}', alias('front', cn), F.fn(u, d.group(1)))
    for txt, n in find(t, r'\| ([A-Z_0-9]+) → (?:FPC |J7-)(\d+)[ |]'):
        add('4절', f'용도 「{txt} → {n}」 = 캐리어 J7-{n}', txt, C.at('J7', n))

    # 12A 하니스
    for row in table_after(t, '## 12A.'):
        n, sig, cside, fp = row[0], row[1], row[2], row[3].strip('*')
        add('12A', f'J7-{n} 넷', sig, C.at('J7', n))
        add('12A', f'J4-{fp} 넷', sig, F.at('J4', fp))
        if n != 'MP': add('12A', f'J7-{n} ↔ J4-(7−n)', 7 - int(n), fp)
        m = re.search(r'캐리어 (\d+)', cside)
        if m: add('12A', f'J7-{n} 캐리어 쪽 「캐리어 {m.group(1)}」', sig, C.at('J1', m.group(1)))

    # 3.1·9·12절 값 문구
    efuse = next(r for r, v in C.comps.items() if v.startswith('TPS26600'))
    for (v,) in find(t, r'ILIM ([\d.]+)kΩ'):
        add('3.1·12절', 'TPS26600 ILIM 저항', f'{v}k', ','.join(C.comps[r].split()[0] for r in C.two_pin(C.fn(efuse, 'ILIM'), 'GND')))
    for (v,) in find(t, r'dVdT ([\d.]+)nF'):
        add('12절', 'TPS26600 dVdT 커패시터', f'{v}nF', ','.join(C.comps[r] for r in C.two_pin(C.fn(efuse, 'dVdT'), 'GND')))
    for (v,) in find(t, r'SHDN ← IR_LED_EN\(?,? ?(\d+)k 풀다운'):
        add('3.1·12절', 'TPS26600 SHDN 넷', 'IR_LED_EN', C.fn(efuse, '~{SHDN}'))
        add('3.1·12절', 'IR_LED_EN 풀다운', f'{v}k', ','.join(C.comps[r] for r in C.two_pin('IR_LED_EN', 'GND')))
    for uf, volt, cnt, refs in find(t, r'출력 (\d+)µF/(\d+)V 1210 ×(\d) \(([^)]*?),'):
        rl = refs.split('·')
        add('3.1', f'5V_SYS 출력 커패시터 개수 ({refs})', cnt, len(rl))
        for r in rl:
            add('3.1', f'5V_SYS {r}', f'{uf}uF/{volt}V on 5V_SYS', f'{C.comps.get(r, "없음").split()[0]} on {C.at(r, 1)}')
    if find(t, r'UVLO → IN\('):
        add('12절', 'TPS26600 UVLO → IN', '12V_IN', C.fn(efuse, 'UVLO'))
    if find(t, r'OVP → RTN\('):
        add('12절', 'TPS26600 OVP → RTN', C.fn(efuse, 'RTN'), C.fn(efuse, 'OVP'))
    if find(t, r'MODE 개방'):
        add('3.1·12절', 'TPS26600 MODE 개방', 'NC', C.fn(efuse, 'MODE'))
    for (pct,) in find(t, r'5V ±(\d+)%로 계약'):
        r2 = C.two_pin('5V_SYS', 'BUCK_FB'); r3 = C.two_pin('BUCK_FB', 'GND')
        rv = lambda r: float(C.comps[r].split()[0].rstrip('k')) * 1e3
        r2 = [r for r in r2 if C.comps[r].split()[0].endswith('k')]
        vout = 0.596 * (1 + rv(r2[0]) / rv(r3[0]))  # TPS54302 VREF 0.596V (SLVSDC9 7.3.x 표)
        add('3.1', f'5V 벅 출력 (R {C.comps[r2[0]]}/{C.comps[r3[0]]}, VREF 0.596V) ±{pct}% 안', True, abs(vout - 5) <= 5 * int(pct) / 100)
    for g, val in find(t, r'게이트 (CAM_1V8_G) = R17 (\d+k)'):
        add('3.1', 'R17 값·넷', f'{val} ' + '-'.join(sorted(('CORE_1V8', g))), f'{F.comps.get("R17")} {"-".join(sorted({F.at("R17", 1), F.at("R17", 2)}))}')
    if find(t, r'전면 Q6 DMG2305UX'):
        add('3.1', 'Q6 품명', 'DMG2305UX', F.comps.get('Q6'))
        add('3.1', 'Q6 S/G/D', 'CORE_1V8/CAM_1V8_G/CAM_1V8', '/'.join(F.fn('Q6', k) for k in 'SGD'))
    for ref, val in find(t, r'Q7 DMG1012T\(G = CAM_EN, D → (R\d+) (\d+k) → 게이트\)'):
        add('3.1', 'Q7 G', 'CAM_EN', F.fn('Q7', 'G'))
        add('3.1', f'Q7 D → {ref} {val} → Q6 게이트', f'{ref} {val}', ' '.join(f'{r} {F.comps[r]}' for r in F.two_pin(F.fn('Q7', 'D'), F.fn('Q6', 'G'))) or '없음')
    for ref, val in find(t, r'게이트–드레인 (C\d+) (\d+nF) 밀러'):
        add('3.1', f'Q6 게이트–드레인 {ref}', f'{ref} {val}', ' '.join(f'{r} {F.comps[r]}' for r in F.two_pin(F.fn('Q6', 'G'), F.fn('Q6', 'D'))) or '없음')
    for ref, val in find(t, r'CAM_1V8 → GND (R\d+) (\d+k) 블리더'):
        add('3.1', f'CAM_1V8 블리더 {ref}', f'{ref} {val}', ' '.join(f'{r} {F.comps[r]}' for r in F.two_pin('CAM_1V8', 'GND') if r.startswith('R')) or '없음')
    for (part,) in find(t, r'전면 LDO (RT9013-\d+GB) \(입력 코어 VIN\)'):
        u = next(r for r, v in F.comps.items() if v.startswith('RT9013'))
        add('3.1', 'FRONT_2V8 LDO 품명·VIN·VOUT', f'{part} VIN FRONT_2V8', f'{F.comps[u]} {F.fn(u, "VIN")} {F.fn(u, "VOUT")}')
    if find(t, r'OE = VDD = CAM_1V8'):
        add('9절', 'X1 OE / VDD', 'CAM_1V8/CAM_1V8', f'{F.fn("X1", "EN")}/{F.fn("X1", "Vdd")}')
    for (part,) in find(t, r'\*\*D7 (SMBJ[\d.]+A)\*\*'):
        add('12절', 'D7 품명·K 넷', f'{part} 5V_SYS', f'{C.comps.get("D7")} {C.fn("D7", "K")}')
    for (part,) in find(t, r'TVS (SMBJ\d+A)급'):
        add('12절', '12V 입력 TVS', part, ','.join(C.comps[r] for r in C.two_pin('12V_IN', 'GND') if C.comps[r].startswith('SMBJ')))
    for lo, hi in find(t, r'퓨즈 ([\d.]+)~([\d.]+)A'):
        a = float(re.match(r'[\d.]+', C.comps['F1']).group(0))
        add('12절', f'F1 정격 {lo}~{hi}A 안 ({C.comps["F1"]})', True, float(lo) <= a <= float(hi))
    for (val,) in find(t, r'R12 (\d+k) → CORE_1V8 풀업'):
        add('7절', 'IR_PWM 풀업 R12', f'{val} CORE_1V8', f'{F.comps.get("R12")} {F.at("R12", 1)}')
    for (val,) in find(t, r'버튼 → \*\*직렬 (\d+)kΩ\*\*'):
        sw = C.at('SW2', 1)
        add('7절', 'UPGRAD_KEY 직렬 저항', f'{val}k', ','.join(C.comps[r] for r in C.two_pin('UPGRAD_KEY', sw)) or '없음')
    for a, b, c in find(t, r'VBUS \*\*(\d+)k/(\d+)k\*\* 분압 \+ C22 (\d+)nF'):
        add('4절', 'USB_DET 분압 위', f'{a}k', ','.join(C.comps[r] for r in C.two_pin('USB_VBUS', 'USB_DET')))
        add('4절', 'USB_DET 분압 아래', f'{b}k', ','.join(C.comps[r] for r in C.two_pin('USB_DET', 'GND') if r.startswith('R')))
        add('4절', 'C22 USB_DET 필터', f'{c}nF USB_DET', f'{C.comps.get("C22")} {C.at("C22", 1)}')
    for (rs,) in find(t, r'AL8860 Rs ([\d.]+)Ω'):
        for u in [r for r, v in F.comps.items() if v.startswith('AL8860')]:
            add('13절 C17', f'{u} Rs (12V_IR–SET)', f'{rs}R', ','.join(F.comps[r].split()[0] for r in F.two_pin('12V_IR', F.fn(u, 'SET'))))
    if find(t, r'두 AL8860 CTRL이 IR_PWM 하나를 공유'):
        us = [r for r, v in F.comps.items() if v.startswith('AL8860')]
        q = [r for r in F.comps if F.fn(r, 'G') == 'IR_PWM']
        add('13절 C18', 'AL8860 CTRL 공유 넷 = IR_PWM N-MOSFET 드레인', F.fn(q[0], 'D') if q else '?', ','.join(sorted({F.fn(u, 'CTRL') for u in us})))
    for (val,) in find(t, r'nSLEEP:\*\* VCC\(2\.8V, v1\.4\)로 (\d+)k 풀업'):
        u = next(r for r, v in F.comps.items() if v.startswith('DRV8837'))
        add('7절', 'DRV8837 nSLEEP 풀업 → VCC', f'{val}k FRONT_2V8', ','.join(F.comps[r] for r in F.two_pin('FRONT_2V8', F.fn(u, '~{SLEEP}'))) + f' {F.fn(u, "VCC")}')

    # DNP
    leds = [r for r, v in F.comps.items() if v.startswith('VSMA') or v.startswith('AL8860')]
    if find(t, r'스트링 A·B 실장'):
        add('DNP', '3.1 「스트링 A·B 실장」: IR LED·AL8860 DNP 수', 0, len([r for r in leds if r in F.dnp]))
    for r_, c_, d_ in find(t, r'CAM_EN → (\d+)k \+ (\d+)nF(\(DNP\))? RC'):
        st = lambda r: 'DNP' if r in F.dnp else '실장'
        rr = [r for r in F.two_pin('CAM_EN', 'CAM_RESET') if r.startswith('R')]; cc = [r for r in F.two_pin('CAM_RESET', 'GND') if r.startswith('C')]
        add('DNP', f'5.1 RESET RC 저항 {r_}k 실장', f'{r_}k 실장', ','.join(f'{F.comps[r]} {st(r)}' for r in rr))
        add('DNP', f'5.1 RESET RC 커패시터 {c_}nF', f'{c_}nF {"DNP" if d_ else "실장"}', ','.join(f'{F.comps[r]} {st(r)}' for r in cc))
    if find(t, r'LIGHT_SENSE \| .*미실장 패드'):
        parts = sorted({r for r, p in F.members.get('LIGHT_SENSE', []) if not r.startswith(('J', 'TP'))})
        add('DNP', '7절 LIGHT_SENSE 「미실장 패드」: 부품 모두 DNP', ','.join(parts), ','.join(r for r in parts if r in F.dnp))
    # 12B절 DNP 목록 = 넷리스트 DNP 집합 (보드마다, 값도)
    rows = table_after(t, '## 12B.')
    for b in BOARDS:
        listed = {r[1]: r[2] for r in rows if r[0] == b}
        add('12B', f'{b} DNP 집합', ','.join(sorted(listed)), ','.join(sorted(N[b].dnp)))
        for ref, val in sorted(listed.items()):
            add('12B', f'{b} {ref} 값', val, N[b].comps.get(ref, '없음').split()[0] if ref in N[b].comps else '없음')
    # 값 문구 정규식이 계약에서 사라지면 대조가 조용히 빠지므로 불일치로 센다
    for rx, n in FOUND.items():
        if n == 0: add('문구', f'계약 문구를 찾지 못함: {rx}', '1개 이상', 0)
    return res

# ---------------------------------------------------------------- kicad runs
def cli(*a):
    return subprocess.run([KICAD_CLI, *a], capture_output=True, text=True, encoding='utf-8', errors='replace')

def netlists(tmp, sch_of):
    out = {}
    for b in BOARDS:
        p = os.path.join(tmp, f'{b}.net')
        r = cli('sch', 'export', 'netlist', '--format', 'kicadsexpr', '-o', p, sch_of(b))
        if r.returncode: sys.exit(f'netlist export failed {b}: {r.stderr}')
        out[b] = p
    return out

def main(argv):
    sys.stdout.reconfigure(encoding='utf-8')
    contract = os.path.join(SCH, 'hw-fw-contract.md'); base = 'ea1336b'; md = js = None  # C-016 netlist baseline
    it = iter(argv)
    for a in it:
        if a == '--contract': contract = next(it)
        elif a == '--base': base = next(it)
        elif a == '--md': md = next(it)
        elif a == '--json': js = next(it)
        elif a == '--selftest': return selftest(contract)
    t = open(contract, encoding='utf-8').read()
    tmp = tempfile.mkdtemp(prefix='c014_')
    cur = netlists(tmp, lambda b: os.path.join(SCH, b, f'{b}.kicad_sch'))
    N = {b: Net(p) for b, p in cur.items()}
    res = check(t, N)
    bad = [r for r in res if not r['ok'] and not r['info']]
    # ERC
    erc = {}
    for b in BOARDS:
        r = cli('sch', 'erc', '--severity-all', '--exit-code-violations', '-o', os.path.join(tmp, f'{b}-erc.rpt'), os.path.join(SCH, b, f'{b}.kicad_sch'))
        erc[b] = r.returncode
    # netcompare vs base commit
    sys.path.insert(0, HERE); import netcompare
    bdir = os.path.join(tmp, 'base'); nc = {}
    for b in BOARDS:
        os.makedirs(os.path.join(bdir, b), exist_ok=True)
        blob = subprocess.run(['git', '-C', REPO, 'show', f'{base}:hardware/schematic/{b}/{b}.kicad_sch'], capture_output=True).stdout
        open(os.path.join(bdir, b, f'{b}.kicad_sch'), 'wb').write(blob)
    old = netlists(bdir, lambda b: os.path.join(bdir, b, f'{b}.kicad_sch'))
    for b in BOARDS:
        nc[b] = netcompare.main(old[b], cur[b])
    # report
    head = subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    ver = re.search(r'v(\d+\.\d+)', t[t.index('개정'):] if '개정' in t else t)
    print(f'contract {os.path.relpath(contract, REPO)} · HEAD {head} · checks {len(res)} · mismatches {len(bad)}')
    for r in res:
        if not r['ok'] or r['info']:
            print(f"  {'INFO' if r['info'] else 'NG  '} [{r['sec']}] {r['item']}: 계약 {r['expected']!r} / 회로도 {r['actual']!r}")
    print('ERC exit', erc, '· netcompare vs', base, nc)
    code = len(bad) + sum(1 for v in erc.values() if v) + sum(1 for v in nc.values() if v)
    if js:
        json.dump({'head': head, 'base': base, 'checks': res, 'mismatches': len(bad), 'erc': erc, 'netcompare': nc, 'exit': min(code, 255)},
                  open(js, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if md:
        secs = {}
        for r in res:
            s = secs.setdefault(r['sec'], [0, 0]); s[0] += 1; s[1] += (not r['ok'] and not r['info'])
        L = [f'| 절 | 대조 줄 | 불일치 |', '|---|---|---|'] + [f'| {k} | {v[0]} | {v[1]} |' for k, v in secs.items()]
        L += ['', '| 판정 | 절 | 항목 | 계약 | 회로도 |', '|---|---|---|---|---|']
        L += [f"| {'정보' if r['info'] else '불일치'} | {r['sec']} | {r['item']} | {r['expected']} | {r['actual']} |".replace('\n', ' ')
              for r in res if not r['ok'] or r['info']]
        L += ['', f'ERC 종료 코드: carrier {erc["carrier"]} · front {erc["front"]} / netcompare({base} 대비): carrier {nc["carrier"]} · front {nc["front"]}',
              f'종료 코드 = {len(bad)} + {sum(1 for v in erc.values() if v)} + {sum(1 for v in nc.values() if v)} = {min(code, 255)}']
        open(md, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    return min(code, 255)

# ---------------------------------------------------------------- fault injection
FAULTS = [
    ('4절 캐리어 22 넷 IR_LED_EN → STATUS_LED', '| 22 | 21 | MIPI_TXP1/IIC2_SCL/PWM |', '| 22 | 21 | MIPI_TXM0/GPIO12/PWM |'),
    ('4절 캐리어 7 짝 핀 8 → 6', '| 7 | 8 | RESERVE1 |', '| 7 | 6 | RESERVE1 |'),
    ('5절 전면 48 넷 CAM_EN → WH_PWM', '| 48 | 47 | CAM_EN |', '| 48 | 47 | WH_PWM |'),
    ('5절 전면 4 미사용 → 예비 (NC 아님)', '| MIPI CSI | 미사용 | — | 05 |\n| 5 | 6 |', '| MIPI CSI | 예비 | — | 05 |\n| 5 | 6 |'),
    ('5.1 DF30 13 D1− → D1+', '| 13 | CAM_RX0_1N (D1−)', '| 13 | CAM_RX0_1P (D1−)'),
    ('6절 I2C2 풀업 4.7k → 2.2k', '전면 보드가 4.7k를', '전면 보드가 2.2k를'),
    ('7절 IR_LED_EN 커넥터 캐리어 22 → 24', 'J2-21 / 캐리어 22', 'J2-21 / 캐리어 24'),
    ('12A J7-4 ↔ J4-3 → J4-4', '| 4 | ALS_INT_RSV | 시험점 TP26만 (BTB 미연결, v1.12 O-83) | **3** |', '| 4 | ALS_INT_RSV | 시험점 TP26만 (BTB 미연결, v1.12 O-83) | **4** |'),
    ('12A J7-2 신호 12V_IR → GND', '| 2 | 12V_IR | TPS26600 OUT |', '| 2 | GND | TPS26600 OUT |'),
    ('3.1 ILIM 6.98kΩ → 10kΩ', 'ILIM 6.98kΩ ≈', 'ILIM 10kΩ ≈'),
    ('3.1 Q7 → R18 1k → 2k', 'D → R18 1k → 게이트', 'D → R18 2k → 게이트'),
    ('3.1 블리더 R19 → R20', 'GND R19 10k 블리더', 'GND R20 10k 블리더'),
    ('3.1 5V_SYS C23 → C24', 'C7·C8·C20·C23,', 'C7·C8·C20·C24,'),
    ('3.1 R17 10k → 100k', '= R17 10k', '= R17 100k'),
    ('12절 D7 SMBJ6.0A → SMBJ5.0A', '**D7 SMBJ6.0A**', '**D7 SMBJ5.0A**'),
    ('12B DNP 목록 front C6 → C5', '| front | C6 | 100nF |', '| front | C5 | 100nF |'),
    ('12B DNP 목록 carrier R17 행 빠짐', '| carrier | R17 | 47k | SD D3 풀업 옵션 | 위와 같음 |\n', ''),
    ('5.1 MCLK 문구 R8 22Ω → R18 0Ω', 'X1 → R8 22Ω', 'X1 → R18 0Ω'),
    ('「스트링 A·B 실장」 문구 모두 삭제', '스트링 A·B 실장', '스트링 A 실장'),
    ('7절 SPARE1 → J7-3 → J7-4', '캐리어 20 → J7-3', '캐리어 20 → J7-4'),
]

def selftest(contract):
    t = open(contract, encoding='utf-8').read()
    tmp = tempfile.mkdtemp(prefix='c014st_')
    N = {b: Net(p) for b, p in netlists(tmp, lambda b: os.path.join(SCH, b, f'{b}.kicad_sch')).items()}
    count = lambda txt: sum(1 for r in check(txt, N) if not r['ok'] and not r['info'])
    base = count(t); missed = 0
    print(f'selftest: 원본 계약 불일치 {base}')
    for name, a, b in FAULTS:
        if a not in t:
            print(f'  MISSING-ANCHOR {name}'); missed += 1; continue
        n = count(t.replace(a, b))  # 같은 문구가 여러 곳이면 모두 바꾼다
        ok = n > base; missed += not ok
        print(f"  {'DETECTED' if ok else 'MISSED  '} {name}: 불일치 {base} → {n}")
    print(f'selftest: {len(FAULTS)}건 중 놓침 {missed}')
    return missed

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
