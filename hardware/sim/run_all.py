"""SIM-001a 전원 경로 시뮬레이션 — 모든 시험을 다시 돌려 results/*.json, png/*.png, <ID>.cir 를 만든다.
기준: criteria.md (결과보다 먼저 커밋, CRITERIA_COMMIT). 모델: 데이터시트 수치로 만든 동작(평균) 모델 — 근거는 PARAM 의 출처 문자열.
usage: python run_all.py            종료 코드 = fail + error 수
ngspice: 환경변수 NGSPICE(실행 파일 경로), 없으면 PATH 의 ngspice_con"""
import json, math, os, subprocess, sys, tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
NG = os.environ.get('NGSPICE', 'ngspice_con')
CRITERIA_COMMIT = '64bde61'  # d00a3ac + A4(781961b) + 개정 1 ef3c0d0 + 개정 2 (R-021 GST40A12-P1J)
SCH_COMMIT = 'a2d878c'  # C-020 (S6 전면 R20·R5 100k, R21 1k, D4·D5 BAT54) — C-019 R2 78.7k/R3 10.7k·C20/C21, C-018 R6 6.04k 포함
FB_R2, FB_R3 = 78.7e3, 10.7e3   # 캐리어 TPS54302 FB 분압 (C-019; C-018 까지 100k/13.3k)
TOOL = {'name': 'ngspice', 'version': 'ngspice-47 (공식 SourceForge ng-spice-rework/47/ngspice-47_64.7z)',
        'sha256': '59225971… (7z, firmware 설치·검증 — orch O-81)', 'path': os.path.basename(NG)}  # 결과에는 실행 파일 이름만(로컬 경로를 남기지 않는다)
for d in ('results', 'png'): os.makedirs(os.path.join(HERE, d), exist_ok=True)

# ------------------------------------------------------------------ 데이터시트 수치 (출처)
DS = {
    'TPS2660': 'TI SLVSDG2G (Dec 2019) https://www.ti.com/lit/ds/symlink/tps2660.pdf sha256 b781cbce…e1de',
    'TPS54302': 'TI SLVSDG6C (Mar 2026) https://www.ti.com/lit/ds/symlink/tps54302.pdf sha256 d81679ba…51b8',
    'SRP7028A': 'Bourns SRP7028A 데이터시트 https://www.bourns.com/docs/Product-Datasheets/SRP7028A.pdf sha256 64bc2dfa…226f',
    'CL32B': 'Samsung Electro-Mechanics Component Library DC-Bias 차트 API (CL32B226KAJNNN, 25 °C, 2026-11-27 받음) sha256 501635c3…13e0',
    'AO3401A': 'AOS AO3401A Rev 3.1 (2023-12) aosmd.com/res/datasheets/AO3401A.pdf sha256 0d8e3261…a785c',
    'DMG2305UX': 'Diodes DMG2305UX DS36196 Rev 8-2 (2021-07) sha256 7421a751…eb2d',
    'RT9013': 'Richtek DS9013-09 (2010-10, LCSC 사본 C58464) sha256 15023cfb…1ac8',
    'GST40A': 'Mean Well GST40A12-P1J 값 — research R-021 `19a69d0` docs/research/r021-bom-c017-psu.md §2.3',
    'GST25A': 'MEAN WELL GST25A-SPEC.PDF https://www.meanwell.com/Upload/PDF/GST25A/GST25A-SPEC.PDF sha256 95f99967…9345',
    'CORE': 'reCamera Core 2002w SCH v1.2 시트 03 Power IN (저장소 hardware/datasheets/seeed, CC BY-SA 4.0)',
}
PMOS = {'AO3401A': dict(vth=(-0.5, -0.9, -1.3), r45=0.060, r25=0.085, ciss=645e-12),
        'DMG2305UX': dict(vth=(-0.5, -0.7, -0.9), r45=0.052, r25=0.100, r18=0.200, ciss=808e-12)}   # 최대 RDS(on), 25 °C
LDO = dict(acc=0.02, vdo_max=0.400, i_do=0.5, ilim=(0.5, 0.6, 0.85))   # RT9013 DS9013-09 3쪽
EF = dict(POR_R=(3.9, 4.0, 4.1), POR_HYS=0.275, OVP_R=(31.0, 32.6, 34.0), OVP_F=(28.5, 30.3, 31.5),
          IDVDT=(4.0e-6, 4.7e-6, 5.5e-6), GAIN=(23.75, 24.6, 25.5), RDVDT=14.0, RON=(0.08, 0.15, 0.25),
          IOL_TOL=0.05, TCB=4e-3, TRETRY=540e-3, SHUTF=(0.55, 0.76, 0.94))   # SLVSDG2G 7.5·7.6
BK = dict(VFB=(0.581, 0.596, 0.611), GM=240e-6, RC=20e3, CC=2.04e-9, CP=2e-12, TSS=5e-3, FSW=(290e3, 400e3, 510e3),
          ILIM_HS=(4.0, 5.0, 6.0), RHS=0.085, RLS=0.040, UVLO_R=(3.8, 4.1, 4.4))   # SLVSDG6C 5.5·5.6·6.2·6.3.3
# 전류 감지 이득 Gcs: 7.2.3 Equation 14 fo = 5.1/(Vout·Co) 와 평균 전류 모드 fo = gm·Rc·Gcs·Vref/(2π·Vout·Co) 를 맞춰 역산
BK['GCS'] = 5.1 * 2 * math.pi / (BK['GM'] * BK['RC'] * BK['VFB'][1])
L1 = dict(L=10e-6, TOL=0.2, DCR=0.085, ISAT=6.0, IRMS=3.5)   # SRP7028A-100M (최대 DCR)
VIN12 = (11.4, 12.0, 12.6)
ADP = dict(rated=3.34, ocp=3.51, vout=11.64, rout=0.11 + 0.026)   # GST40A12-P1J (R-021 19a69d0 §2.3): OLP 3.51~5.01 A hiccup, Vout 11.64~12.36
ADAPTER = ADP['rated']
GST = dict(rated=2.08, ocp=2.29)   # 참고: GST25A-SPEC OVERLOAD 110~150%
GST60 = dict(ocp=5.25)            # 참고: GST60A12 OLP 5.25~7.5 A (R-021)
LOAD12_IR = 1.22   # 계약 3.2 AL8860 ×2 입력 최악
BUCK_IN = 0.62     # 계약 3.2 5V 벅 입력 (5V 1.3A 피크, 88%)
R6 = 6.04e3        # 캐리어 TPS26600 ILIM (C-018 a61dc63; C-017 6.98k, 그 전 8.06k)

def run(cir_name, netlist, wr):
    """netlist 를 <ID>.cir 로 저장하고 ngspice -b 로 돌려 wrdata 파일(들)을 numpy 로 돌려준다."""
    path = os.path.join(HERE, cir_name)
    open(path, 'w', encoding='utf-8', newline='\n').write(netlist)
    tmp = tempfile.mkdtemp(prefix='sim_')
    r = subprocess.run([NG, '-b', path], cwd=tmp, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
    out = {}
    for w in wr:
        f = os.path.join(tmp, w)
        if not os.path.exists(f):
            raise RuntimeError(f'{cir_name}: {w} 없음\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}')
        out[w] = np.loadtxt(f, skiprows=1)
    return out

def chk(name, op, limit, value, unit, corner=''):
    if op == '<=': ok = value <= limit
    elif op == '>=': ok = value >= limit
    elif op == 'between': ok = limit[0] <= value <= limit[1]
    else: ok = value == limit
    v = round(float(value), 6) if isinstance(value, (int, float, np.floating)) else value
    return {'name': name, 'op': op, 'limit': limit, 'unit': unit, 'value': v, 'corner': corner, 'pass': bool(ok)}

def save(id_, title, board, refs, model, checks, pngs, cir, notes):
    res = {'id': id_, 'title': title, 'owner': 'schematic',
           'circuit': {'board': board, 'refs': refs, 'schematic_commit': SCH_COMMIT},
           'model': model, 'criteria_commit': CRITERIA_COMMIT, 'checks': checks,
           'verdict': 'pass' if all(c['pass'] for c in checks if not c['name'].startswith('[참고')) else 'fail',
           'waveforms': [f'hardware/sim/png/{p}' for p in pngs], 'netlist': f'hardware/sim/{cir}' if cir else None,
           'tool': TOOL, 'notes': notes}
    json.dump(res, open(os.path.join(HERE, 'results', f'{id_}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return res

def fig(name, panels, title):
    """panels: [(x, [(y, label)], ylabel)] — 공통 x"""
    f, ax = plt.subplots(len(panels), 1, figsize=(9, 2.6 * len(panels)), sharex=True)
    ax = np.atleast_1d(ax)
    for a, (x, ys, yl) in zip(ax, panels):
        for it in ys:
            xx, y, lab = (x, *it) if len(it) == 2 else it
            a.plot(xx, y, label=lab, lw=1.2)
        a.set_ylabel(yl); a.grid(alpha=.3); a.legend(fontsize=8, loc='best')
    ax[-1].set_xlabel('time (ms)' if 'ms' not in title else 'time (ms)')
    f.suptitle(title, fontsize=10); f.tight_layout()
    f.savefig(os.path.join(HERE, 'png', name), dpi=110); plt.close(f)
    return name

# ------------------------------------------------------------------ TPS26600 동작 모델
def iol_tol(rilim):
    """SLVSDG2G 7.5 I(OL) 표: 8k 행 ±5.0 %, 5.36k 행 ±5.4 % → R < 8k 이면 5.4 %"""
    return 0.054 if rilim < 8e3 else 0.05

def efuse_subckt(i, g, rilim, tol_sign, ron):
    """TPS26600 평균 모델: SHDN·POR·OVP 로 켜짐, dVdT 전류 I·C → 출력 = GAIN·V(dVdT) 추종(RON), 전류 제한 I(OL)=12/R(kΩ)·(1±5%),
    회로차단기(MODE 개방): 제한 4 ms 지속 → 끔, 540 ms 뒤 재시도. 근거 SLVSDG2G 7.5·7.6·8.3·Table 1."""
    iol = 12.0 / (rilim / 1e3) * (1 + tol_sign * iol_tol(rilim))
    return f"""
.subckt TPS26600 in out shdn dvdt
* 켜짐 조건 (POR 상승 {EF['POR_R'][2]} V 최악, OVP 상승 {EF['OVP_R'][0]} V 최악 — 히스테리시스는 A2 에서 따로)
Ben en0 0 V = (v(shdn) > {EF['SHUTF'][1]}) && (v(in) > {EF['POR_R'][2]}) && (v(in) < {EF['OVP_R'][0]}) && (v(flt) < 0.5) ? 1 : 0
Ren en0 en 1k
Cen en 0 1n
* dVdT: 켜지면 I(dVdT) 충전, 꺼지면 14 Ω 방전
Bdv 0 dvdt I = v(en) > 0.5 ? ({i} * (v(dvdt) * {g} < v(in) + 1 ? 1 : 0)) : -v(dvdt) / {EF['RDVDT']}
* 통과 FET: 목표 = min(GAIN·VdVdT, VIN), 전류 = (목표 − OUT)/RON, 0 ~ I(OL) 로 제한
Bfet in out I = v(en) > 0.5 ? max(0, min({iol:.6g}, (min({g} * v(dvdt), v(in)) - v(out)) / {ron})) : 0
* 회로차단기 타이머: 제한 중이면 1 V / 4 ms 로 오르고, 아니면 빨리 내림. 1 V 넘으면 flt 래치
Blim lim 0 V = ((min({g} * v(dvdt), v(in)) - v(out)) / {ron} > {iol * 0.995:.6g}) && (v(en) > 0.5) ? 1 : 0
Btm 0 tmr I = v(lim) > 0.5 ? (v(tmr) < 1.2 ? {1e-6 / EF['TCB']:.6g} : 0) : (v(tmr) > 0 ? -1e-4 : 0)
Ctm tmr 0 1u
Bfl 0 flt I = v(tmr) > 1 ? max(0, 1 - v(flt)) : (v(flt) > 0 ? {-0.5e-6 / EF['TRETRY']:.6g} : 0)
Cfl flt 0 1u
.ends
""", iol

def sim_a():
    out = []
    cout_max = 1.1 * (10e-6 * 3) + 0.2e-6            # C11 + 전면 C14·C16 (10µF K) + C15·C17 100nF
    cout_nom = 30.2e-6
    c9 = 22e-9
    # --- A1 돌입: 빠른 코너(전류 최대) · 느린 코너(램프 시간)
    corners = {'fast': (EF['IDVDT'][2], EF['GAIN'][2], c9 * 0.9, cout_max, VIN12[2]),
               'slow': (EF['IDVDT'][0], EF['GAIN'][0], c9 * 1.1, cout_nom * 0.9, VIN12[0])}
    data = {}
    for k, (i, g, cdv, co, vin) in corners.items():
        sub, iol = efuse_subckt(i, g, R6, -1, EF['RON'][1])
        net = f"""* SIM-A1 TPS26600 기동 돌입 ({k} 코너) — 캐리어 U2, C9 dVdT, 출력 C = C11 + 전면 C14..C17
{sub}
Vin in 0 {vin}
Vsh shdn 0 PULSE(0 1.8 1m 10u 10u 1 2)
X1 in out shdn dvdt TPS26600
Cdv dvdt 0 {cdv:.4g}
Cout out 0 {co:.4g}
Rbl out 0 100k
.control
set wr_singlescale
set wr_vecnames
tran 2u 15m uic
wrdata a1_{k}.dat v(out) i(Vin)
quit
.endc
.end
"""
        data[k] = run(f'SIM-A1-{k}.cir', net, [f'a1_{k}.dat'])[f'a1_{k}.dat']
    f_ = data['fast']; s_ = data['slow']
    ipk = float(np.max(-f_[:, 2]))
    iol_min = 12.0 / (R6 / 1e3 * 1.01) * (1 - iol_tol(R6))
    t, v = s_[:, 0], s_[:, 1]; vf = VIN12[0]
    t10 = t[np.argmax(v > 0.1 * vf)]; t90 = t[np.argmax(v > 0.9 * vf)]
    pngs = [fig('SIM-A1-inrush.png', [(f_[:, 0] * 1e3, [(f_[:, 1], 'V(12V_IR) fast'), (s_[:, 0] * 1e3, s_[:, 1], 'V(12V_IR) slow')], 'V'),
                                      (f_[:, 0] * 1e3, [(-f_[:, 2], 'I(12V_IN→IR) fast'), (s_[:, 0] * 1e3, -s_[:, 2], 'slow')], 'A')],
                'SIM-A1 TPS26600 inrush (C9 22nF, Cout max 33.2uF) — time ms')]
    out.append(save('SIM-A1', 'TPS26600 기동 돌입전류 (dVdT 22nF)', 'carrier', ['U2', 'C9', 'C11', 'front C14..C17'],
        {'source': '데이터시트 동작 모델 (TPS26600 평균)', 'url': DS['TPS2660'], 'license': '모델은 이 저장소 작성 (데이터시트 수치만 인용)',
         'behavioral': True, 'basis': 'SLVSDG2G 7.5: I(dVdT) 4.0/4.7/5.5 µA, GAIN(dVdT) 23.75/24.6/25.5 V/V, R(dVdT) 14 Ω, I(OL) 표 (R 8k 1.425~1.575 A)'},
        [chk('돌입 피크 전류 ≤ I(OL) 최소', '<=', round(iol_min, 3), ipk, 'A', '빠른: I(dVdT) 5.5µA·GAIN 25.5·C9 −10%·Cout +10%·VIN 12.6V'),
         chk('출력 램프 10→90% 시간', '<=', 10.0, (t90 - t10) * 1e3, 'ms', '느린: I(dVdT) 4.0µA·GAIN 23.75·C9 +10%·VIN 11.4V')],
        pngs, 'SIM-A1-fast.cir',
        'LED 부하는 기동 중 꺼진 것으로 둔다(FW 규칙: IR_LED_EN 전에 IR_PWM High). 출력 C DC 바이어스 감액은 무시(돌입 쪽 보수적).'))
    # --- A2 켜짐/OVP 창: VIN 0→36→0 V 쓸기 (최악 코너 문턱)
    hyst = f"""
Bpor p0 0 V = v(in) > {EF['POR_R'][2]} ? 1 : (v(in) < {EF['POR_R'][2] - EF['POR_HYS']} ? 0 : v(p))
Rp p0 p 1k
Cp p 0 1n
Bovp o0 0 V = v(in) > {EF['OVP_R'][0]} ? 1 : (v(in) < {EF['OVP_F'][0]} ? 0 : v(o))
Ro o0 o 1k
Co o 0 1n
Bon on 0 V = v(p) > 0.5 && v(o) < 0.5 ? 1 : 0
"""
    net = f"""* SIM-A2 TPS26600 켜짐(POR, UVLO→IN) · OVP(→RTN, 내부 고정) 창 — 최악 문턱
Vin in 0 PWL(0 0 36m 36 72m 0)
{hyst}
.control
set wr_singlescale
set wr_vecnames
tran 10u 72m
wrdata a2.dat v(in) v(on)
quit
.endc
.end
"""
    d = run('SIM-A2.cir', net, ['a2.dat'])['a2.dat']
    vin, on = d[:, 1], d[:, 2]; half = len(vin) // 2
    v_on = float(vin[np.argmax(on > 0.5)])
    up = np.where((on[:half] > 0.5))[0]; v_ovp = float(vin[up[-1]]) if len(up) else float('nan')
    pngs = [fig('SIM-A2-window.png', [(d[:, 0] * 1e3, [(vin, 'VIN'), (on * 10, 'FET on ×10')], 'V')], 'SIM-A2 POR/OVP window (worst thresholds) — time ms')]
    out.append(save('SIM-A2', 'TPS26600 켜짐(UVLO→IN = POR)·OVP 문턱', 'carrier', ['U2'],
        {'source': '데이터시트 동작 모델 (문턱 비교기)', 'url': DS['TPS2660'], 'license': '이 저장소 작성', 'behavioral': True,
         'basis': 'SLVSDG2G 7.5: V(PORR) 3.9~4.1 V, 히스테리시스 275 mV; V(IN_OVP) 상승 31~34 V / 하강 28.5~31.5 V (OVP = 0 V → 내부 고정); UVLO 가 IN 에 묶여 UVLO 비교기는 항상 참'},
        [chk('켜짐 문턱 최대 ≤ 입력 최소 − 역접 FET 강하', '<=', round(VIN12[0] - 0.1, 2), v_on, 'V', 'POR 4.1 V 최악, AO4407A 강하 0.1 V 가정'),
         chk('OVP 상승 문턱 최소 ≥ 입력 최대', '>=', VIN12[2], v_ovp, 'V', 'OVP 31 V 최악')],
        pngs, 'SIM-A2.cir',
        '「분압 저항 ±1% 최악」은 해당 없음: 회로도는 UVLO→IN, OVP→RTN 이라 분압 저항이 없다(내부 고정 문턱). 입력 쪽 TVS SMBJ15A 가 OVP 보다 먼저 클램프한다.'))
    # --- A3 전류 제한·회로차단기
    iol_max = 12.0 / (R6 / 1e3 * 0.99) * (1 + iol_tol(R6))
    sub, iol = efuse_subckt(EF['IDVDT'][1], EF['GAIN'][1], R6 * 0.99, +1, EF['RON'][1])
    net = f"""* SIM-A3 TPS26600 과부하 (I(OL) 최대 코너, R6 6.98k −1%) — 12V_IR 를 2 Ω 로 단락에 가깝게, 5V 벅 입력 0.62 A 동시
{sub}
Vin in 0 {VIN12[1]}
Vsh shdn 0 PULSE(0 1.8 1m 10u 10u 2 3)
X1 in out shdn dvdt TPS26600
Cdv dvdt 0 22n
Cout out 0 30.2u
Sov out 0 sw 0 SWM
Vsw sw 0 PULSE(0 1 20m 1u 1u 2 3)
.model SWM SW(Ron=2 Roff=1e6 Vt=0.5)
.options method=gear
Ibk in 0 {BUCK_IN}
.control
set wr_singlescale
set wr_vecnames
tran 20u 1.2 uic
wrdata a3.dat v(out) i(Vin) v(x1.flt) v(x1.tmr)
quit
.endc
.end
"""
    d = run('SIM-A3.cir', net, ['a3.dat'])['a3.dat']
    t, vo, iin = d[:, 0], d[:, 1], -d[:, 2]
    iir = iin - BUCK_IN
    after = t > 20.5e-3
    pk_in = float(np.max(iin[after]))
    win = (t > 30e-3) & (t < 1.15)
    avg_ir = float(np.trapezoid(iir[win], t[win]) / (t[win][-1] - t[win][0]))
    pngs = [fig('SIM-A3-overload.png', [(t * 1e3, [(vo, 'V(12V_IR)')], 'V'), (t * 1e3, [(iin, 'I 12V input total'), (iir, 'I 12V_IR')], 'A')],
                'SIM-A3 TPS26600 overload, circuit breaker auto-retry (ILIM max corner) — time ms')]
    out.append(save('SIM-A3', f'TPS26600 전류 제한 (ILIM R6 {R6 / 1e3:.2f}k)·회로차단기', 'carrier', ['U2', 'R6'],
        {'source': '데이터시트 동작 모델 (TPS26600 평균)', 'url': DS['TPS2660'], 'license': '이 저장소 작성', 'behavioral': True,
         'basis': 'SLVSDG2G 7.5 I(OL): 12k 1.0 A / 8k 1.5 A / 5.36k 2.23 A → I(OL) ≈ 12/R(kΩ), ±5%; 7.6 tCB(dly) 4 ms, tCBretry(dly) 540 ms; Table 1 MODE 개방 = 회로차단기 자동 재시도'},
        [chk('I(OL) 최소 ≥ 2스트링 최악 부하', '>=', LOAD12_IR, round(iol_min, 4), 'A', 'R6 +1%, I(OL) −5%'),
         chk('과부하 중 12V 입력 피크 (I(OL) 최대 + 벅 0.62 A)', '<=', ADAPTER, pk_in, 'A', 'R6 −1%, I(OL) +5% (시뮬), 3A급 어댑터 (O-88)'),
         chk('[참고 GST25A12] 과부하 중 12V 입력 피크 ≤ 2.08 A', '<=', GST['rated'], pk_in, 'A', '판정 제외'),
         chk('과부하 지속 시 12V_IR 평균 (재시도 주기)', '<=', LOAD12_IR, avg_ir, 'A', '2 Ω 과부하 1.1 s')],
        pngs, 'SIM-A3.cir',
        f'회로도 R6 = 6.98k (C-017, ≈1.72 A typ; 이전 8.06k ≈1.49 A). lead 문구의 10k(1.2 A)와 다름 — 10k 이면 I(OL) 최소 1.13 A < 1.22 A 부하라 2스트링이 제한에 걸린다. I(OL) 최대 {iol_max:.3f} A. 빠른 차단(1.87×I(OL)) 은 모델에 없음.'))
    return out

# ------------------------------------------------------------------ TPS54302 평균 모델
def buck_subckt(vfb, ilim, ac=False):
    """TPS54302 평균 전류 모드 모델: gm EA(240 µA/V) + 내부 보상 20k/2.04nF/2pF(6.2 블록도) → 전류 명령 Gcs·Vcomp,
    인덕터 전류는 명령을 fsw/2 2차 지연으로 따르고 기울기는 (VIN−VOUT)/L, −VOUT/L 로 제한, HS 피크 제한 −ΔI/2,
    소프트 스타트 5 ms(VIN UVLO 상승 뒤), EA 출력 클램프 0 ~ I(LIM_HS)/Gcs (6.3.1), OV 비교기 108 % (6.1). 펄스 스킵·히컵은 없음."""
    s = f"""
.subckt TPS54302 vin sw fb params: L=10u FSW=400k
Buv uv0 0 V = v(vin) > {BK['UVLO_R'][1]} ? 1 : 0
Ruv uv0 uv 1k
Cuv uv 0 1n
* 소프트 스타트 기준: 켜진 뒤 0 → VFB 를 5 ms 에
Bss 0 ss I = v(uv) > 0.5 ? (v(ss) < {vfb} ? {vfb / BK['TSS'] * 1e-6:.6g} : 0) : -v(ss) * 1e-3
Css ss 0 1u
Gea 0 comp VALUE = {{ {BK['GM']} * (min(v(ss), {vfb}) - v(fb)) }}
* EA 출력 클램프 (6.3.1): 0 ~ I(LIM_HS)/Gcs 밖으로 나가면 1 mS 로 되돌림 (연속 함수 — 수렴용)
Bclp comp 0 I = 1e-3 * (max(v(comp) - {ilim / BK['GCS']:.5g}, 0) + min(v(comp), 0))
Rc comp cz {BK['RC']}
Cc cz 0 {BK['CC']}
Cp comp 0 {BK['CP']}
Rcl comp 0 10Meg
* 전류 명령 → fsw/2 2차 지연 (평균 전류 모드 샘플링 근사)
Bcmd cmd 0 V = (v(fb) > {1.08 * vfb:.5g} ? 0 : 1) * max(0, min({BK['GCS']:.6g} * v(comp), {ilim} - (v(vin) - v(sw)) * v(sw) / (v(vin) + 1e-3) / ({{L}} * {{FSW}}) / 2))
Rf1 cmd f1 1
Lf1 f1 f2 {{0.64 / (3.14159 * FSW)}}
Cf1 f2 0 {{1 / (0.64 * 3.14159 * FSW)}}
* 인덕터 전류 (전압 노드 il = 암페어), 기울기 제한
Bil 0 il I = v(uv) > 0.5 ? 1e-6 * max(-max(v(sw), 0) / {{L}}, min((v(vin) - v(sw)) / {{L}}, (v(f2) - v(il)) * 3.14159 * {{FSW}})) : -v(il) * 1e-3
Cil il 0 1u
Gout 0 sw VALUE = {{ max(v(il), 0) }}
Bin vin 0 I = max(v(il), 0) * v(sw) / max(v(vin), 1) / 0.92
.ends
"""
    if ac:   # 소신호용: 소프트 스타트·UVLO·기울기 적분기 대신 정상 상태 고정 (동작점 특이 행렬 회피)
        s = s.replace(s[s.index('Buv'):s.index('Gea')], f'Vuv uv 0 1\nVss ss 0 {vfb}\n')
        s = s.replace(s[s.index('Bil'):s.index('Gout')], 'Eil il 0 f2 0 1\n')
    return s

def sim_b():
    out = []
    cpart = 22e-6
    # DC 바이어스: 결과는 DCB(0..1) 로 받는다 — 근거는 dcbias() 참조
    dcb, dcb_src = dcbias()
    c_eff_min = 4 * cpart * 0.9 * dcb
    c_eff_nom = 4 * cpart * dcb
    # --- B1 DC 공차
    vals = []
    for vfb in BK['VFB']:
        for s in (-1, 1):
            r2 = FB_R2 * (1 + 0.01 * s); r3 = FB_R3 * (1 - 0.01 * s)
            vals.append(vfb * (1 + r2 / r3))
    net = f"""* SIM-B1 TPS54302 FB 분압 DC (VFB 최대·최소 × R2 {FB_R2 / 1e3:g}k/R3 {FB_R3 / 1e3:g}k ±1%) — .op
Vref1 r1 0 {BK['VFB'][2]}
Vref2 r2 0 {BK['VFB'][0]}
Eo1 o1 0 VALUE = {{ v(r1) * (1 + {FB_R2 * 1.01:.6g} / {FB_R3 * 0.99:.6g}) }}
Eo2 o2 0 VALUE = {{ v(r2) * (1 + {FB_R2 * 0.99:.6g} / {FB_R3 * 1.01:.6g}) }}
.control
op
let vmax = v(o1)
let vmin = v(o2)
echo vmax $&vmax > b1.dat
echo vmin $&vmin >> b1.dat
print vmax vmin
quit
.endc
.end
"""
    open(os.path.join(HERE, 'SIM-B1.cir'), 'w', encoding='utf-8', newline='\n').write(net)
    tmp = tempfile.mkdtemp(); subprocess.run([NG, '-b', os.path.join(HERE, 'SIM-B1.cir')], cwd=tmp, capture_output=True)
    sv = {l.split()[0]: float(l.split()[1]) for l in open(os.path.join(tmp, 'b1.dat'))}
    vmax, vmin = sv['vmax'], sv['vmin']
    out.append(save('SIM-B1', 'TPS54302 출력 전압 공차 (FB 분압 최악)', 'carrier', ['U1', 'R2', 'R3'],
        {'source': '계산 (ngspice .op)', 'url': DS['TPS54302'], 'license': '—', 'behavioral': True, 'basis': 'SLVSDG6C 5.5 VFB 0.581/0.596/0.611 V (−40~125 °C); Equation 3 VOUT = VFB(1+R2/R3)'},
        [chk('출력 최대 (VFB 0.611, R2 +1%, R3 −1%)', '<=', 5.25, vmax, 'V', 'VFB max · R ±1%'),
         chk('출력 최소 (VFB 0.581, R2 −1%, R3 +1%)', '>=', 4.75, vmin, 'V', 'VFB min · R ±1%'),
         chk('출력 최대 < D7 SMBJ6.0A VRWM', '<=', 6.0, vmax, 'V', '')],
        [], 'SIM-B1.cir',
        f'R2 {FB_R2 / 1e3:g}k / R3 {FB_R3 / 1e3:g}k (C-019), 전형값 {BK["VFB"][1] * (1 + FB_R2 / FB_R3):.3f} V. C-018 까지 100k/13.3k 는 최악 5.298 V 로 fail. 코어 VIN 저전압 차단 3.0 V 까지 여유 {vmin - 3.0:.2f} V. VFB 공차 ±2.5% 는 온도 전 범위 값.'))
    # --- B2 리플 (스위칭 모델)
    vin = VIN12[2]; L = L1['L'] * (1 - L1['TOL']); fsw = BK['FSW'][0]; iout = 1.3
    D = (5.0 + iout * (BK['RLS'] + L1['DCR'])) / (vin + iout * (BK['RLS'] - BK['RHS']))
    T = 1 / fsw
    net = f"""* SIM-B2 TPS54302 출력 리플 — 이상 스위치(HS 85 mΩ / LS 40 mΩ) 고정 듀티, VIN 12.6 V, L −20% (8 µH, DCR 85 mΩ), fsw 최소 290 kHz, C 유효 최소
Vin vin 0 {vin}
Vg g 0 PULSE(0 1 0 1n 1n {D * T:.6g} {T:.6g})
Shs vin sw g 0 SHS
Sls sw 0 0 g SLS
.model SHS SW(Ron={BK['RHS']} Roff=1e6 Vt=0.5)
.model SLS SW(Ron={BK['RLS']} Roff=1e6 Vt=-0.5)
L1 sw l2 {L:.4g} ic={iout}
Rdcr l2 out {L1['DCR']}
C1 out c1 {c_eff_min / 4:.4g} ic=5
Resr1 c1 0 8m
C2 out c2 {c_eff_min / 4:.4g} ic=5
Resr2 c2 0 8m
C3 out c3 {c_eff_min / 4:.4g} ic=5
Resr3 c3 0 8m
C4 out c4 {c_eff_min / 4:.4g} ic=5
Resr4 c4 0 8m
Rl out 0 {5 / iout:.4g}
.options method=gear
.control
set wr_singlescale
set wr_vecnames
tran 5n 1.5m uic
linearize
wrdata b2.dat v(out) i(L1)
quit
.endc
.end
"""
    d = run('SIM-B2.cir', net, ['b2.dat'])['b2.dat']
    t, vo, il = d[:, 0], d[:, 1], d[:, 2]
    last = t > t[-1] - 20 * T
    rip = float(vo[last].max() - vo[last].min()); ipk = float(il[last].max()); ipp = float(il[last].max() - il[last].min())
    pngs = [fig('SIM-B2-ripple.png', [(t[last] * 1e3, [(vo[last], 'V(5V_SYS)')], 'V'), (t[last] * 1e3, [(il[last], 'I(L1)')], 'A')],
                'SIM-B2 TPS54302 ripple, VIN 12.6V, L 8uH, fsw 290kHz, 1.3A — time ms')]
    out.append(save('SIM-B2', 'TPS54302 출력 리플', 'carrier', ['U1', 'L1', 'C7', 'C8', 'C20', 'C23'],
        {'source': '이상 스위치 스위칭 모델 (고정 듀티)', 'url': DS['TPS54302'], 'license': '이 저장소 작성', 'behavioral': True,
         'basis': f'SLVSDG6C 5.5 R(HSD) 85 mΩ·R(LSD) 40 mΩ·fsw 290~510 kHz; SRP7028A-100M DCR 85 mΩ max·L ±20%; 출력 C {dcb_src}; ESR 8 mΩ/개 가정'},
        [chk('출력 리플 (VIN 12.6 V, L 8 µH, fsw 290 kHz)', '<=', 0.030, rip, 'Vpp', f'C 유효 {c_eff_min * 1e6:.1f} µF')],
        pngs, 'SIM-B2.cir', f'인덕터 리플 {ipp:.3f} App, 피크 {ipk:.3f} A (1.3 A 부하). 레이아웃 ESL·프로브 영향 없음.'))
    # --- B3 부하 과도 + 루프
    def buck_net(title, extra, analysis, vin=12.0, vfb=BK['VFB'][1], c=c_eff_nom, cff='75p', ac=False):
        return f"""* {title}
{buck_subckt(vfb, BK['ILIM_HS'][0], ac)}
Vin vin 0 {vin}
X1 vin sw fb TPS54302 params: L={L1['L']} FSW={BK['FSW'][1]}
Cout sw ce {c:.4g}
Resr ce 0 2m
Rtop vs fb {FB_R2:g}
Rbot fb 0 {FB_R3:g}
Cff vs fb {cff}
{extra}
{analysis}
.end
"""
    tr = buck_net('SIM-B3 TPS54302 부하 과도 0.1→1.5→0.1 A (1 A/µs), C 유효 공칭',
        f"Vinj sw vs 0\nIld sw 0 PWL(0 0 6m 0 6.1m 0.1 8m 0.1 {8e-3 + 1.4e-6} 1.5 9m 1.5 {9e-3 + 1.4e-6} 0.1 10m 0.1)",
        """.control
set wr_singlescale
set wr_vecnames
tran 0.2u 10m
wrdata b3.dat v(sw) v(x1.il)
quit
.endc""", vin='PWL(0 0 100u 12)')
    d = run('SIM-B3-tran.cir', tr, ['b3.dat'])['b3.dat']
    t, vo, il = d[:, 0], d[:, 1], d[:, 2]
    base = float(np.mean(vo[(t > 7.5e-3) & (t < 8e-3)]))
    w = (t > 7.9e-3) & (t < 10e-3)
    dev = float(np.max(np.abs(vo[w] - base)))
    ac = buck_net('SIM-B3 TPS54302 루프 이득 (직렬 주입, 1.3 A)',
        "Vinj sw vs DC 0 AC 1\nIld sw 0 1.3\n" + f".nodeset v(sw)=5.0 v(vs)=5.0 v(fb)={BK['VFB'][1]} v(x1.ss)={BK['VFB'][1]} v(x1.uv)=1 v(x1.il)=1.3 v(x1.f2)=1.3 v(x1.f1)=1.3 v(x1.cmd)=1.3 v(x1.comp)={1.3 / BK['GCS']:.5f} v(x1.cz)={1.3 / BK['GCS']:.5f}",
        """.control
set wr_singlescale
set wr_vecnames
ac dec 50 100 200k
let T = -v(sw)/v(vs)
let tm = mag(T)
let tp = cph(T)
wrdata b3ac.dat tm tp
quit
.endc""", ac=True)
    a = run('SIM-B3-loop.cir', ac, ['b3ac.dat'])['b3ac.dat']
    fq, tm, tp = a[:, 0], a[:, 1], a[:, 2]
    i = int(np.argmax(tm < 1)); fc = float(fq[i])
    ph = np.degrees(np.unwrap(tp)); ph -= 360 * np.round((ph[0] + 90) / 360)   # 저주파 적분기 −90° 기준
    pm = float(180 + ph[i])
    f2, ax = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
    ax[0].semilogx(fq, 20 * np.log10(tm)); ax[0].axhline(0, c='k', lw=.6); ax[0].set_ylabel('|T| dB'); ax[0].grid(alpha=.3)
    ax[1].semilogx(fq, ph); ax[1].axhline(-180, c='k', lw=.6); ax[1].set_ylabel('phase deg'); ax[1].grid(alpha=.3); ax[1].set_xlabel('Hz')
    f2.suptitle(f'SIM-B3 loop gain: fc {fc / 1e3:.1f} kHz, PM {pm:.0f} deg'); f2.tight_layout(); f2.savefig(os.path.join(HERE, 'png', 'SIM-B3-loop.png'), dpi=110); plt.close(f2)
    pngs = [fig('SIM-B3-step.png', [(t[w] * 1e3, [(vo[w], 'V(5V_SYS)')], 'V'), (t[w] * 1e3, [(il[w], 'I(L) avg')], 'A')],
                'SIM-B3 TPS54302 load step 0.1-1.5-0.1A — time ms'), 'SIM-B3-loop.png']
    out.append(save('SIM-B3', 'TPS54302 부하 과도 0→1.5A·루프 안정도', 'carrier', ['U1', 'L1', 'C7', 'C8', 'C20', 'C23', 'C19'],
        {'source': '데이터시트 동작 모델 (평균 전류 모드)', 'url': DS['TPS54302'], 'license': '이 저장소 작성', 'behavioral': True,
         'basis': f'SLVSDG6C 6.3.3 gm 240 µA/V, 6.2 블록도 내부 보상 20 kΩ + 2.04 nF, 2 pF; Gcs = {BK["GCS"]:.2f} A/V 는 Equation 14 fo = 5.1/(Vout·Co) 에서 역산; {dcb_src}'},
        [chk('부하 과도 편차 0.1↔1.5 A', '<=', 0.25, dev, 'V', f'VIN 12 V, C 유효 {c_eff_nom * 1e6:.1f} µF'),
         chk('교차 주파수', '<=', 40e3, fc, 'Hz', '1.3 A'),
         chk('위상 여유', '>=', 45, pm, 'deg', '1.3 A')],
        pngs, 'SIM-B3-tran.cir',
        '0 A 가 아니라 0.1 A 에서 시작(평균 모델에 펄스 스킵이 없어 0 A 경계가 의미 없음). Gcs 역산·2차 샘플 지연은 근사 — 교차 주파수·위상 여유는 실측(주입)으로 확인 권장.'))
    # --- B4 기동
    res = {}
    for k, ld in (('noload', '1G'), ('1A3', f'{5 / 1.3:.4g}')):
        n = buck_net(f'SIM-B4 TPS54302 기동 ({k}) — VIN 0→12 V 100 µs',
                     f"Vinj sw vs 0\nRld sw 0 {ld}", """.control
set wr_singlescale
set wr_vecnames
tran 2u 12m
wrdata b4.dat v(sw) v(x1.il)
quit
.endc""").replace('Vin vin 0 12.0', 'Vin vin 0 PWL(0 0 100u 12)')
        res[k] = run(f'SIM-B4-{k}.cir', n, ['b4.dat'])['b4.dat']
    chks = []
    for k, d in res.items():
        t, vo = d[:, 0], d[:, 1]; vf = float(np.mean(vo[t > 11e-3]))
        chks.append(chk(f'기동 오버슈트 ({k})', '<=', 4.0, (vo.max() / vf - 1) * 100, '%', ''))
        chks.append(chk(f'95% 도달 시간 ({k})', '<=', 10.0, float(t[np.argmax(vo > 0.95 * vf)]) * 1e3, 'ms', ''))
    pngs = [fig('SIM-B4-startup.png', [(res['noload'][:, 0] * 1e3, [(res['noload'][:, 1], 'V(5V_SYS) no load'), (res['1A3'][:, 0] * 1e3, res['1A3'][:, 1], '1.3 A')], 'V'),
                                       (res['1A3'][:, 0] * 1e3, [(res['1A3'][:, 2], 'I(L) 1.3 A')], 'A')], 'SIM-B4 TPS54302 soft-start — time ms')]
    out.append(save('SIM-B4', 'TPS54302 기동 (소프트 스타트 5 ms)', 'carrier', ['U1'],
        {'source': '데이터시트 동작 모델 (평균 전류 모드)', 'url': DS['TPS54302'], 'license': '이 저장소 작성', 'behavioral': True, 'basis': 'SLVSDG6C 5.6 tSS 5 ms, 5.5 VIN UVLO 4.1 V'},
        chks, pngs, 'SIM-B4-noload.cir', '무부하 기동은 실제로 펄스 스킵이지만 모델은 연속 모드.'))
    # --- B5 인덕터 / B6 출력 C (계산 + B2 시뮬 피크)
    out.append(save('SIM-B5', '인덕터 포화·실효 전류 여유 (L1 SRP7028A-100M)', 'carrier', ['L1', 'U1'],
        {'source': '데이터시트 값 대조 + SIM-B2 피크', 'url': DS['SRP7028A'] + ' · ' + DS['TPS54302'], 'license': '—', 'behavioral': False,
         'basis': 'SRP7028A-100M: 10 µH ±20%, DCR 75/85 mΩ, Irms 3.5 A, Isat 6.0 A (L 20% 감소점); SLVSDG6C I(LIM_HS) 4/5/6 A'},
        [chk('Isat ≥ HS 전류 제한 최대', '>=', BK['ILIM_HS'][2], L1['ISAT'], 'A', '과부하에서 피크가 제한 최대까지'),
         chk('Irms ≥ 5V_SYS 피크 부하', '>=', 1.3, L1['IRMS'], 'A', ''),
         chk('정상 피크 (SIM-B2) ≤ Isat', '<=', L1['ISAT'], ipk, 'A', '1.3 A, VIN 12.6 V, L −20%')],
        ['SIM-B2-ripple.png'], None,
        'Isat 6.0 A = I(LIM_HS) 최대 6 A 로 여유 0 (같음). Isat 정의가 L −20% 라 그 점에서도 급격한 포화는 아니다. L1 MPN 은 회로도 값 「10uH Isat>=6A」·풋프린트 SRP7028A 로 추정.'))
    out.append(save('SIM-B6', '출력 커패시터 DC 바이어스 감액 (22 µF ×4)', 'carrier', ['C7', 'C8', 'C20', 'C23'],
        {'source': '제조사 DC 바이어스 자료 + 계산', 'url': dcb_src, 'license': '—', 'behavioral': False, 'basis': f'5 V 에서 C/C0 = {dcb:.3f}; 공차 −10% (K)'},
        [chk('출력 C 유효 최소 (5 V 바이어스, −10%)', '>=', 30e-6, c_eff_min, 'F', '')],
        [], None, f'유효 공칭 {c_eff_nom * 1e6:.1f} µF, 최소 {c_eff_min * 1e6:.1f} µF. SIM-B2·B3 는 이 값을 쓴다.'))
    return out

def dcbias():
    """CL32B226KAJNNNE 5 V DC 바이어스 비율: Samsung 차트 API 0 V 21.92 µF → 5 V 17.42 µF (−20.5 %)."""
    return 17.42 / 21.92, DS['CL32B'] + ' — 5 V 17.42 µF / 0 V 21.92 µF'


# ------------------------------------------------------------------ 공통 조각: 어댑터 · 12V 입력 · 벅 시스템
def adapter_subckt(ilim, hiccup, vout=ADP['vout'], rout=ADP['rout']):
    """어댑터 동작 모델: Vout(최소 11.64 V), 출력 저항 0.11 Ω + 케이블 26 mΩ (R-021), 출력 C 100 µF(가정), 전류 ilim 에서 (a) 정전류 또는 (b) hiccup(1 ms 감지 → 1 s 끔).
    근거: R-021 §2.3 · GST25A-SPEC OVERLOAD 「Hiccup mode」 — 감지 시간·주기·출력 C 는 자료에 없어 가정."""
    hic = f"""Blim lim 0 V = (({vout} * min(1, v(on)) - v(out)) / {rout} > {ilim * 0.995:.4g}) ? 1 : 0
Btm 0 tmr I = v(lim) > 0.5 ? (v(tmr) < 1.2 ? 1e-3 : 0) : (v(tmr) > 0 ? -1e-4 : 0)
Ctm tmr 0 1u
Bfl 0 flt I = v(tmr) > 1 ? max(0, 1 - v(flt)) : (v(flt) > 0 ? -0.5e-6 : 0)
Cfl flt 0 1u""" if hiccup else "Vfl flt 0 0"
    return f"""
.subckt ADAPTER out on
{hic}
Bsrc 0 out I = v(flt) < 0.5 ? max(0, min({ilim}, ({vout} * min(1, v(on)) - v(out)) / {rout})) : 0
Cad out 0 100u
Rbl out 0 10k
.ends
"""

def front_end(adapter_on, shdn, iol_sign=+1):
    """어댑터 → Iad(측정) → 역접 FET(AO4407A ≈ 20 mΩ) → 12V_IN(C1 47µ + C2..C4 10µ×3 + C10 1µ + C5 0.1µ) → eFuse → 12V_IR(C11 + 전면 C14..C17)"""
    sub, iol = efuse_subckt(EF['IDVDT'][1], EF['GAIN'][1], R6 * (1 - 0.01 * iol_sign), iol_sign, EF['RON'][1])
    return sub + f"""
Von on 0 {adapter_on}
Xad ad on ADAPTER
Vad ad adm 0
Rq1 adm in12 0.02
Cin1 in12 0 47u
Cin2 in12 0 31.1u
Vsh shdn 0 {shdn}
Xef in12 ir shdn dvdt TPS26600
Cdv dvdt 0 22n
Cir ir 0 30.2u
""", iol

def sim_a4():
    out = []
    cases = [('GST40_cc', ADP['ocp'], False), ('GST40_hiccup', ADP['ocp'], True), ('GST_cc', GST['ocp'], False), ('GST_hiccup', GST['ocp'], True), ('GST60_cc', GST60['ocp'], False)]
    res = {}
    for k, ilim, hic in cases:
        fe, iol = front_end('PWL(0 0 1m 1)', 'PWL(0 0 8m 0 8.01m 1.8)', +1)
        net = f"""* SIM-A4 어댑터({k}: {ilim} A, {'hiccup' if hic else '정전류'}) + 12V 최악 부하: IR A+B 25 % 듀티 500 Hz(켬 1.22 A) + 5V 벅(1.3 A) → 20 ms 에 12V_IR 0.1 Ω 과부하
{adapter_subckt(ilim, hic)}
{fe}
{buck_subckt(BK['VFB'][1], BK['ILIM_HS'][0])}
Xbk in12 v5 fb TPS54302 params: L={L1['L']} FSW={BK['FSW'][1]}
Cv5 v5 0 {4 * 22e-6 * dcbias()[0]:.4g}
Rtop v5 fb {FB_R2:g}
Rbot fb 0 {FB_R3:g}
Cff v5 fb 75p
Rld v5 0 {5 / 1.3:.4g}
Vpwm pwm 0 PULSE(0 1 9m 1u 1u 0.5m 2m)
Bir ir 0 I = v(pwm) > 0.5 ? {LOAD12_IR} * min(1, max(v(ir), 0) / 9) : 0
Sov ir 0 sc 0 SWM
Vsc sc 0 PULSE(0 1 20m 1u 1u 1 2)
.model SWM SW(Ron=0.1 Roff=1e6 Vt=0.5)
.options method=gear
.control
set wr_singlescale
set wr_vecnames
tran 2u 40m
wrdata a4.dat i(Vad) v(in12) v(ir) v(v5)
quit
.endc
.end
"""
        res[k] = run(f'SIM-A4-{k}.cir', net, ['a4.dat'])['a4.dat']
    def meas(d):
        t, ia, v12, vir, v5 = d[:, 0], d[:, 1], d[:, 2], d[:, 3], d[:, 4]
        n = (t > 12e-3) & (t < 20e-3); o = (t > 20e-3) & (t < 40e-3)
        return dict(pk_n=float(ia[n].max()), avg_n=float(np.trapezoid(ia[n], t[n]) / (t[n][-1] - t[n][0])),
                    pk_o=float(ia[o].max()), v5min=float(v5[o].min()), v12min=float(v12[o].min()))
    m = {k: meas(d) for k, d in res.items()}
    a, h, g, gh, g6 = m['GST40_cc'], m['GST40_hiccup'], m['GST_cc'], m['GST_hiccup'], m['GST60_cc']
    checks = [chk('정상 최악 12V 입력 피크 (IR 25 % 켬 + 벅) ≤ GST40A12 정격', '<=', ADP['rated'], a['pk_n'], 'A', 'GST40A12 Vout 11.64 V'),
              chk('정상 최악 12V 입력 평균', '<=', 1.9, a['avg_n'], 'A', '8 ms 창'),
              chk('12V_IR 과부하 중 12V 입력 피크 ≤ OLP 최소 3.51 A (eFuse 먼저)', '<=', ADP['ocp'], a['pk_o'], 'A', f'I(OL) 최대 (R6 −1 %, +5 %)'),
              chk('12V_IR 과부하 중 5V_SYS 최소 (a 정전류 3.51 A)', '>=', 4.75, a['v5min'], 'V', ''),
              chk('12V_IR 과부하 중 5V_SYS 최소 (b hiccup 3.51 A)', '>=', 4.75, h['v5min'], 'V', '1 ms 감지 가정'),
              chk('[참고 GST60A12] 과부하 중 5V_SYS 최소 (정전류 5.25 A)', '>=', 4.75, g6['v5min'], 'V', '판정 제외'),
              chk('[참고 GST25A12] 정상 최악 피크 ≤ 2.08 A', '<=', GST['rated'], g['pk_n'], 'A', '판정 제외'),
              chk('[참고 GST25A12] 과부하 중 피크 ≤ OCP 2.29 A', '<=', GST['ocp'], g['pk_o'], 'A', '판정 제외'),
              chk('[참고 GST25A12] 과부하 중 5V_SYS 최소 (정전류 2.29 A)', '>=', 4.75, g['v5min'], 'V', '판정 제외'),
              chk('[참고 GST25A12] 과부하 중 5V_SYS 최소 (hiccup 2.29 A)', '>=', 4.75, gh['v5min'], 'V', '판정 제외')]
    pngs = []
    for k in ('GST40_cc', 'GST_hiccup'):
        d = res[k]; t = d[:, 0] * 1e3
        pngs.append(fig(f'SIM-A4-{k}.png', [(t, [(d[:, 1], 'I adapter')], 'A'), (t, [(d[:, 2], 'V 12V_IN'), (d[:, 3], 'V 12V_IR')], 'V'), (t, [(d[:, 4], 'V 5V_SYS')], 'V')],
                        f'SIM-A4 adapter {k}: IR 25% duty from 9ms, 12V_IR overload at 20ms — time ms'))
    out.append(save('SIM-A4', '어댑터 GST40A12-P1J + 12V 최악 부하·과부하 (GST25A12·GST60A12 참고)', 'carrier', ['U2', 'R6', 'U1', 'J2(어댑터)'],
        {'source': '데이터시트 동작 모델 (어댑터·TPS26600·TPS54302 평균) + IR 부하 25 % 듀티 전류원', 'url': DS['GST40A'] + ' · ' + DS['GST25A'] + ' · ' + DS['TPS2660'], 'license': '이 저장소 작성',
         'behavioral': True, 'basis': 'GST40A12-P1J OLP 3.51~5.01 A hiccup, Vout 11.64 V 최소, Rout 0.11 Ω + 케이블 26 mΩ (R-021) · GST25A OVERLOAD 110~150 % · 계약 3.2 부하'},
        checks, pngs, 'SIM-A4-GST40_cc.cir',
        f"GST40A12 정전류: 정상 피크 {a['pk_n']:.3f} A·평균 {a['avg_n']:.3f} A, 과부하 피크 {a['pk_o']:.3f} A, 5V 최소 {a['v5min']:.3f} V / hiccup 5V 최소 {h['v5min']:.3f} V. GST60A12 정전류 5V 최소 {g6['v5min']:.3f} V. "
        f"GST25A12(2.29 A): 과부하 피크 {g['pk_o']:.3f} A, 5V 최소 정전류 {g['v5min']:.3f} V · hiccup {gh['v5min']:.3f} V, 12V_IN 최소 {gh['v12min']:.2f} V. "
        "IR 두 스트링을 같은 위상(최악)으로 둠. 어댑터 출력 C 100 µF·감지 1 ms 는 가정."))
    return out

# ------------------------------------------------------------------ C. 보드 레일
def pmos_model(name, part, worst):
    d = PMOS[part]
    vth = d['vth'][2] if worst else d['vth'][1]
    if part == 'AO3401A':
        r, vg = (d['r25'], 2.5) if worst else (d['r25'] * 0.7, 2.5)
    else:
        r, vg = (d['r18'], 1.8) if worst else (d['r18'] * 0.34, 1.8)
    kp = 1 / (r * (vg - abs(vth)))
    return f".model {name} PMOS(LEVEL=1 VTO={vth} KP={kp:.4g} W=1 L=1 CGSO=0 CGDO=0)", r, vg, vth

def sim_c():
    out = []
    # C1 RT9013: VIN 최소 4.75 V, 부하 0~50 mA 쓸기 (드롭아웃 = 400 mV @ 500 mA 최대 → 0.8 Ω 등가)
    rdo = LDO['vdo_max'] / LDO['i_do']
    net = f"""* SIM-C1 RT9013-28 (전면 U1) — VIN 4.75 V, 출력 정확도 −2 %, 드롭아웃 최대 400 mV@500 mA (0.8 Ω 등가), 부하 0~50 mA
Vin vin 0 4.75
Bldo out 0 V = min({2.8 * (1 - LDO['acc'])}, v(vin) - {rdo} * i(Vld))
Vld out o2 0
Ild o2 0 0
.control
set wr_singlescale
set wr_vecnames
dc Ild 0 50m 1m
wrdata c1.dat v(out) v(vin)
quit
.endc
.end
"""
    d = run('SIM-C1.cir', net, ['c1.dat'])['c1.dat']
    i, vo, vi = d[:, 0], d[:, 1], d[:, 2]
    out.append(save('SIM-C1', 'FRONT_2V8 RT9013-28 드롭아웃·부하', 'front', ['U1', 'C1', 'C2'],
        {'source': '데이터시트 동작 모델 (LDO 정확도 + 드롭아웃 등가 저항)', 'url': DS['RT9013'], 'license': '이 저장소 작성', 'behavioral': True,
         'basis': 'DS9013-09 3쪽: 정확도 ±2 % (10 mA), 드롭아웃 250/400 mV @ 500 mA (VIN ≥ 2.7 V), 전류 제한 0.5 A 최소'},
        [chk('FRONT_2V8 최소 (VIN 4.75 V, 0~50 mA)', '>=', 2.744, float(vo.min()), 'V', '정확도 −2 %'),
         chk('입력−출력 여유 − 드롭아웃(50 mA)', '>=', 0.0, float((vi - vo).min() - rdo * 0.05), 'V', '드롭아웃 최대 등가 0.8 Ω')],
        [], 'SIM-C1.cir', '2010년 판 데이터시트(LCSC 사본). 5V_SYS 최소는 SIM-B1 의 4.863 V 이지만 계약 하한 4.75 V 로 판정.'))
    # C2 스위치 강하 (DC): 레벨 1 최악 모델
    mA, rA, vgA, _ = pmos_model('PAO', 'AO3401A', True)
    mD, rD, vgD, _ = pmos_model('PDM', 'DMG2305UX', True)
    net = f"""* SIM-C2 부하 스위치 DC 강하 — 최악 RDS(on) (레벨 1: VTO 최악, RDS(on) 최대 점 맞춤)
{mA}
{mD}
Vc3 c3 0 3.3
Vc18 c18 0 1.764
* SD_PWR_3V3: Q2 AO3401A, 게이트 0 V (VGS −3.3 V), 0.2 A
Msd sd 0 c3 c3 PAO
Isd sd 0 0.2
* CAM_IOVDD·CAM_AVDD: AO3401A, 게이트 0 V, 0.1 A 씩
Mio io 0 c3 c3 PAO
Iio io 0 0.1
* CAM_1V8: Q6 DMG2305UX, 게이트 = R17 4.7k / (R18 1k + Q7 2 Ω) 분압 (C-018), 부하 20 mA + R19 블리더
Rg17 c18 g18 4.7k
Rg18 g18 0 1.002k
Mc18 v18 g18 c18 c18 PDM
Ic18 v18 0 20m
R19 v18 0 10k
.control
op
let dsd = 3.3 - v(sd)
let dio = 3.3 - v(io)
let v18 = v(v18)
let vg = v(g18) - 1.764
echo $&dsd $&dio $&v18 $&vg > c2.dat
quit
.endc
.end
"""
    path = os.path.join(HERE, 'SIM-C2.cir'); open(path, 'w', encoding='utf-8', newline='\n').write(net)
    tmp = tempfile.mkdtemp(); subprocess.run([NG, '-b', path], cwd=tmp, capture_output=True)
    dsd, dio, v18, vg = [float(x) for x in open(os.path.join(tmp, 'c2.dat')).read().split()]
    out.append(save('SIM-C2', '부하 스위치 강하 (SD_PWR_3V3 · CAM_IOVDD/AVDD · CAM_1V8)', 'carrier+front', ['carrier Q2', 'front Q1', 'front Q2', 'front Q6', 'R17', 'R18', 'R19'],
        {'source': '레벨 1 MOSFET (데이터시트 VGS(th) 최악·RDS(on) 최대 점 맞춤)', 'url': DS['AO3401A'] + ' · ' + DS['DMG2305UX'], 'license': '이 저장소 작성', 'behavioral': True,
         'basis': f'AO3401A RDS(on) 최대 85 mΩ @ −2.5 V, VGS(th) −1.3 V 최악 / DMG2305UX 200 mΩ @ −1.8 V, VGS(th) −0.9 V 최악'},
        [chk('SD_PWR_3V3 강하 (0.2 A)', '<=', 0.099, dsd, 'V', 'VGS −3.3 V'),
         chk('CAM_IOVDD·AVDD 강하 (0.1 A)', '<=', 0.099, dio, 'V', 'VGS −3.3 V'),
         chk('CAM_1V8 (CORE_1V8 1.764 V, 20 mA)', '>=', 1.71, v18, 'V', f'VGS {vg:.3f} V (R17 4.7k/R18 1k 분압, C-018)')],
        [], 'SIM-C2.cir', 'CORE_1V8 최소 1.764 V(−2 %)는 가정(코어 SGM2036 정확도 미조사).'))
    # C3 켜질 때 코어 레일 순간 강하
    mA, *_ = pmos_model('PAO', 'AO3401A', False)
    mD, *_ = pmos_model('PDM', 'DMG2305UX', False)
    net = f"""* SIM-C3 스위치 켬 순간 CORE_3V3·CORE_1V8 강하 — 코어 레일 = 이상 전원 + 경로 0.1 Ω + 로컬 C (코어 SCH 03 출력 10 µF ×2 X5R → 3.3 V 바이어스 12 µF, 1V8 10 µF → 8.5 µF 가정)
{mA}
{mD}
V33 s33 0 3.32
R33 s33 c33 0.1
C33 c33 0 12u
V18 s18 0 1.8
R18p s18 c18 0.1
C18p c18 0 8.5u
* 전면 CAM_EN (1 ms): Q3 → CAM_PG (→ R20 1k → Q1, → R5 10k → Q2), Q7 → CAM_1V8_PD
Ven en 0 PULSE(0 1 1m 1u 1u 1 2)
R4 c33 pg 100k
Sq3 pg 0 en 0 SQ
* C-020 S6: Q1 게이트 R20 100k ∥ (R21 1k + D4 BAT54, 애노드 pgiod → 캐소드 pg), Q2 게이트 R5 100k ∥ D5 BAT54 (애노드 pg → 캐소드 pgav)
R5 pg pgav 100k
Df5 pg pgav DBAT
Rf20 pg pgio 100k
Rf21 pgio pgiod 1k
Df4 pgiod pg DBAT
Cf20 pgio iov 4.7n
Mq1 iov pgio c33 c33 PAO
Cg1 pgio c33 645p
Cf21 pgav avd 4.7n
Mq2 avd pgav c33 c33 PAO
Cg2 pgav c33 645p
C7 iov 0 1u
C8 avd 0 1.1u
Ri iov 0 110
Ra avd 0 110
* CAM_1V8 (C-018): R17 4.7k 풀업, Q7 → R18 1k, C19 4.7 nF 게이트–드레인
R17 c18 g6 4.7k
Sq7 pd 0 en 0 SQ
R18 pd g6 1k
C19 g6 v18 4.7n
Mq6 v18 g6 c18 c18 PDM
Cg6 g6 c18 808p
C11 v18 0 1.1u
R19 v18 0 10k
Rx1 v18 0 450
* 캐리어 SD (10 ms): Q3 → SD_PWR_GD, R22 47k / C21 100 nF
Vsd sden 0 PULSE(0 1 10m 1u 1u 1 2)
R11 c33 gd 100k
Sq3c gd 0 sden 0 SQ
R22 gd gsd 47k
C21 gsd c33 100n
Mq2c sdv gsd c33 c33 PAO
Cg2c gsd c33 645p
Csd sdv 0 11.1u
Rsd sdv 0 16.5
R23 sdv 0 100k
.model SQ SW(Ron=1 Roff=1e9 Vt=0.5)
* BAT54WS: VF 0.32 V @ 10 mA (최대값에 맞춘 근사 — Diodes BAT54WS 데이터시트), CJ 10 pF
.model DBAT D(IS=4e-8 N=1 RS=2 CJO=10p BV=30)
.options method=gear
.control
set wr_singlescale
set wr_vecnames
tran 0.1u 40m
wrdata c3.dat v(c33) v(c18) v(iov) v(avd) v(v18) v(sdv)
quit
.endc
.end
"""
    d = run('SIM-C3.cir', net, ['c3.dat'])['c3.dat']
    t, c33, c18 = d[:, 0], d[:, 1], d[:, 2]
    def dip(v, t0, t1):
        b = float(np.mean(v[(t > t0 - 0.2e-3) & (t < t0)])); w = (t > t0) & (t < t1)
        return b - float(v[w].min()), b
    d33c, b33 = dip(c33, 1e-3, 9e-3); d18, b18 = dip(c18, 1e-3, 9e-3); d33s, _ = dip(c33, 10e-3, 39e-3)
    w1 = (t > 0.9e-3) & (t < 1.6e-3); w2 = (t > 9.5e-3) & (t < 40e-3)
    pngs = [fig('SIM-C3-cam.png', [(t[w1] * 1e3, [(c33[w1], 'CORE_3V3'), (d[w1, 3], 'CAM_IOVDD'), (d[w1, 4], 'CAM_AVDD')], 'V'),
                                   (t[w1] * 1e3, [(c18[w1], 'CORE_1V8'), (d[w1, 5], 'CAM_1V8')], 'V')], 'SIM-C3 CAM_EN on at 1ms — time ms'),
            fig('SIM-C3-sd.png', [(t[w2] * 1e3, [(c33[w2], 'CORE_3V3'), (d[w2, 6], 'SD_PWR_3V3')], 'V')], 'SIM-C3 SD0_PWR_EN on at 10ms — time ms')]
    out.append(save('SIM-C3', '스위치 켬 순간 코어 레일 강하 (CAM_EN · SD0_PWR_EN)', 'carrier+front', ['front Q1', 'Q2', 'Q3', 'Q6', 'Q7', 'R18', 'C19', 'carrier Q2', 'R22', 'C21'],
        {'source': '레벨 1 MOSFET(전형) + 코어 레일 등가(가정)', 'url': DS['AO3401A'] + ' · ' + DS['DMG2305UX'] + ' · ' + DS['CORE'], 'license': '이 저장소 작성', 'behavioral': True,
         'basis': '코어 레일: 이상 전원 + 0.1 Ω(SIM-001b 와 같은 가정) + 로컬 C (코어 SCH 03 출력 C, DC 바이어스 감액 가정). 센서 레일 부하 30 mA, X1 450 Ω, SD 카드 10 µF·0.2 A (가정)'},
        [chk('CAM_EN 켬: CORE_3V3 강하', '<=', 0.166, d33c, 'V', 'C-020 S6: Q1 R20 100k ∥ (R21 1k + D4), Q2 R5 100k ∥ D5, C20·C21 4.7 nF (밀러)'),
         chk('CAM_EN 켬: CORE_1V8 강하 (C-018 R17 4.7k·R18·C19 4.7n)', '<=', 0.09, d18, 'V', ''),
         chk('SD0_PWR_EN 켬: CORE_3V3 강하', '<=', 0.166, d33s, 'V', 'R22 47k / C21 100 nF')],
        pngs, 'SIM-C3.cir', f'기준선 CORE_3V3 {b33:.3f} V, CORE_1V8 {b18:.3f} V (0.1 Ω 경로 강하 포함). 코어 쪽 실제 디커플링(SoC 주변 C)은 더 크므로 강하는 이보다 작을 수 있다.'))
    return out

# ------------------------------------------------------------------ D. 전원 순서
def sim_d():
    fe, iol = front_end('PWL(0 0 50m 1)', '0', +1)
    net = f"""* SIM-D1 전원 순서: 어댑터 GST40A12 (Vout 11.64 V, 50 ms 상승, R-021) → 12V_IN → TPS54302 5V_SYS → 코어 3V3/1V8(가정 모델) → 전면 RT9013 2V8; IR_LED_EN = 0 (R5 풀다운)
{adapter_subckt(ADAPTER, False)}
{fe}
{buck_subckt(BK['VFB'][1], BK['ILIM_HS'][0])}
Xbk in12 v5 fb TPS54302 params: L={L1['L']} FSW={BK['FSW'][1]}
Cv5 v5 0 {4 * 22e-6 * dcbias()[0]:.4g}
Rtop v5 fb {FB_R2:g}
Rbot fb 0 {FB_R3:g}
Cff v5 fb 75p
* 코어: 5V 부하 0.3 A (3V3 뜬 뒤), 3V3 = VIN > 4 V 뒤 1 ms 램프 (SY80004 소프트 스타트 가정), 1V8 = 3V3 따라 (SGM2036)
Bon33 e33 0 V = v(v5) > 4.0 ? 1 : 0
Re33 e33 e33f 1k
Ce33 e33f 0 1n
Bss 0 r33 I = v(e33f) > 0.5 ? (v(r33) < 3.32 ? 3.32e-3 : 0) : -v(r33) * 1e-3
Cs33 r33 0 1u
E33 s33 0 r33 0 1
R33 s33 c33 0.1
C33 c33 0 12u
Rl33 c33 0 11
Bc18 s18 0 V = min(1.8, max(v(c33) - 0.2, 0))
R18p s18 c18 0.1
C18p c18 0 8.5u
Rl18 c18 0 18
Bcore v5 0 I = (v(c33) > 3.0 ? 0.3 : 0.02) * min(1, max(v(v5), 0) / 4)
* 전면 RT9013-28: VIN = 5V_SYS(BTB 통과), EN = VIN, 출력 = min(2.8, VIN − 0.8 Ω·I) 를 40 µs 로 따라감
Bldo l0 0 V = v(v5) > 2.2 ? min(2.8, v(v5) - 0.8 * 0.03) : 0
Rldo l0 f28 1.2
Cf28 f28 0 2.2u
Rf28 f28 0 93
.options method=gear
.control
set wr_singlescale
set wr_vecnames
tran 2u 80m
wrdata d1.dat v(in12) v(v5) v(c33) v(c18) v(f28) v(ir)
quit
.endc
.end
"""
    d = run('SIM-D1.cir', net, ['d1.dat'])['d1.dat']
    t = d[:, 0]; v12, v5, v33, v18, v28, vir = (d[:, i] for i in range(1, 7))
    t12 = float(t[np.argmax(v12 > BK['UVLO_R'][2])]); t5 = float(t[np.argmax(v5 > 4.75)])
    def ovs(v, nom): return (float(v.max()) / nom - 1) * 100
    end = t > 75e-3
    mono = bool(np.all(np.diff(v28[t < t[np.argmax(v28 > 0.99 * 2.8)]]) > -1e-3))
    pngs = [fig('SIM-D1-sequence.png', [(t * 1e3, [(v12, '12V_IN'), (vir, '12V_IR')], 'V'),
                                         (t * 1e3, [(v5, '5V_SYS'), (v33, 'CORE_3V3'), (v28, 'FRONT_2V8'), (v18, 'CORE_1V8')], 'V')],
                'SIM-D1 power-up sequence (GST40A12 rise 50ms, IR_LED_EN=0) — time ms')]
    return [save('SIM-D1', '전원 순서 전체 기동 (12V → 5V_SYS → 코어 레일 → 전면 2V8)', 'carrier+front', ['J2', 'Q1', 'U2', 'U1(carrier)', 'U1(front)'],
        {'source': '데이터시트 동작 모델 조합 (어댑터·TPS26600·TPS54302·RT9013) + 코어 레일 가정 모델', 'url': DS['TPS54302'] + ' · ' + DS['TPS2660'] + ' · ' + DS['RT9013'], 'license': '이 저장소 작성',
         'behavioral': True, 'basis': '코어 SY80004·SGM2036 기동 순서는 코어 SCH 03 PWR_SEQ 기준 미조사 → 1 ms 램프·3V3 추종 가정'},
        [chk('12V_IN > 4.4 V(UVLO 최대) 뒤 5V_SYS 4.75 V 도달', '<=', 15.0, (t5 - t12) * 1e3, 'ms', '어댑터 50 ms 상승'),
         chk('12V_IN 오버슈트', '<=', 5.0, ovs(v12, float(np.mean(v12[end]))), '%', ''),
         chk('5V_SYS 오버슈트', '<=', 5.0, ovs(v5, float(np.mean(v5[end]))), '%', ''),
         chk('FRONT_2V8 오버슈트', '<=', 5.0, ovs(v28, 2.8), '%', ''),
         chk('IR_LED_EN = 0 동안 12V_IR 최대', '<=', 0.5, float(vir.max()), 'V', 'SHDN 0 V'),
         chk('FRONT_2V8 단조 증가', '==', True, mono, '', ''),
         chk('FRONT_2V8 최종값 오차', '<=', 2.0, abs(float(np.mean(v28[end])) / 2.8 - 1) * 100, '%', '')],
        pngs, 'SIM-D1.cir', '코어 내부 순서(VDDC·VDDQ·PWR_SEQ)는 모델에 없음. CAM_EN·SD0_PWR_EN·IR_LED_EN 은 FW 가 나중에 켠다(SIM-C3).')]


# ------------------------------------------------------------------ A5. 12V 전류 순서 표 (계산)
IR_PK, IR_AVG = 1.585, 1.425        # firmware SIM-001b′ B2 (20 µs 창 피크 / 평균)
BUCK_IN_WORST = 6.5 / 0.88 / 11.4   # 계약 3.2 5V_SYS 6.5 W, 88 %, 입력 최소 11.4 V
E96 = [5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 8.06]

def iol_range(r_k):
    tol = iol_tol(r_k * 1e3)
    return 12 / (r_k * 1.01) * (1 - tol), 12 / r_k, 12 / (r_k * 0.99) * (1 + tol)

def sim_a5():
    need = IR_PK * 1.15
    rows = []
    for r in E96:
        lo, ty, hi = iol_range(r)
        rows.append((r, lo, ty, hi, lo >= need, hi + BUCK_IN_WORST < ADP['ocp']))
    ok = [x for x in rows if x[4] and x[5]]
    best = min(ok, key=lambda x: x[2]) if ok else None
    lo, ty, hi = iol_range(R6 / 1e3)
    L = ['# SIM-A5 12V 전류 순서 표 (run_all.py 가 만든다)', '',
         f'- 회로도 R6 = **{R6 / 1e3:.2f} kΩ** (`{SCH_COMMIT}`) · 기준 `{CRITERIA_COMMIT}` · I(OL) = 12 / R(kΩ) (SLVSDG2G Equation 3, 22쪽), 허용 오차 {iol_tol(R6) * 100:.1f} % (7.5 표) + R ±1 %', '',
         '| 줄 | 최소 | 전형 | 최대 | 근거 |', '|---|---|---|---|---|',
         f'| 12V_IR 정상 최악 (eFuse 뒤) | — | 평균 {IR_AVG:.3f} A | 20 µs 피크 **{IR_PK:.3f} A** | firmware SIM-001b′ B2 |',
         f'| 12V_IR 피크 × 1.15 (필요 제한 최소) | {need:.3f} A | | | lead 조건 |',
         f'| 벅 입력 최악 | | | {BUCK_IN_WORST:.3f} A | 6.5 W / 0.88 / 11.4 V |',
         f'| 12V 입력 정상 최악 (합계) | | ≈1.84 A (계약 3.2) | {IR_PK + BUCK_IN_WORST:.3f} A (피크 + 벅) | |',
         f'| eFuse I(OL), R6 {R6 / 1e3:.2f}k | **{lo:.3f} A** | {ty:.3f} A | **{hi:.3f} A** | Equation 3 |',
         f'| eFuse I(OL) 최대 + 벅 입력 최악 | | | **{hi + BUCK_IN_WORST:.3f} A** | |',
         f'| 어댑터 GST40A12-P1J OLP | **{ADP["ocp"]:.2f} A** | | 5.01 A | R-021 |', '',
         '| R(ILIM) E96 | I(OL) 최소 | 전형 | 최대 | 피크×1.15 ≤ 최소 | 최대+벅 < OLP 최소 |', '|---|---|---|---|---|---|']
    L += [f'| {r:.2f}k{" ← 회로도" if abs(r * 1e3 - R6) < 1 else ""}{" ← 추천" if best and r == best[0] else ""} | {a:.3f} | {b:.3f} | {c:.3f} | {"예" if d else "아니오"} | {"예" if e else "아니오"} |' for r, a, b, c, d, e in rows]
    open(os.path.join(HERE, 'SIM-A5-current-order.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    return [save('SIM-A5', '12V 전류 순서 표 (12V_IR · eFuse 제한 · 어댑터 OLP)', 'carrier', ['U2', 'R6'],
        {'source': '계산 (데이터시트 식)', 'url': DS['TPS2660'] + ' · ' + DS['GST40A'], 'license': '—', 'behavioral': False,
         'basis': 'I(OL) = 12/R(kΩ) Equation 3 (22쪽) · 7.5 표 허용 오차 · 12V_IR 피크 SIM-001b′ · 벅 입력 계약 3.2'},
        [chk('12V_IR 피크 × 1.15 ≤ eFuse I(OL) 최소', '<=', round(lo, 4), round(need, 4), 'A', f'R6 {R6 / 1e3:.2f}k +1 %, −{iol_tol(R6) * 100:.1f} %'),
         chk('eFuse I(OL) 최대 + 벅 입력 최악 < 어댑터 OLP 최소', '<=', ADP['ocp'], round(hi + BUCK_IN_WORST, 4), 'A', f'R6 −1 %, +{iol_tol(R6) * 100:.1f} %')],
        [], None, f'표: hardware/sim/SIM-A5-current-order.md. 두 조건을 만족하는 E96 중 I(OL) 최저 = {best[0]:.2f}k' + (f' (I(OL) {best[1]:.3f}~{best[3]:.3f} A)' if best else '') if best else '조건 만족 E96 없음')]

if __name__ == '__main__':
    which = sys.argv[1:] or ['a', 'a4', 'a5', 'b', 'c', 'd']
    allres = []
    for w in which:
        try:
            allres += globals()[f'sim_{w}']()
        except Exception as e:
            allres.append(save(f'SIM-{w.upper()}-ERROR', f'{w} 실행 오류', '', [], {}, [], [], None, str(e)[:2000]) | {'verdict': 'error'})
            print('ERROR', w, e)
    bad = 0
    for r in allres:
        print(f"{r['id']:8s} {r['verdict']:5s} {r['title']}")
        for c in r['checks']:
            print(f"    {'OK ' if c['pass'] else 'NG '} {c['name']}: {c['value']} {c['unit']} ({c['op']} {c['limit']})")
        bad += r['verdict'] != 'pass'
    print('fail+error =', bad)
    sys.exit(bad)
