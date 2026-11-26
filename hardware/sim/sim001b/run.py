#!/usr/bin/env python3
"""SIM-001b 부하·제어 회로 시뮬레이션 (B1~B8) — 넷리스트 생성 → ngspice 배치 실행 → 판정 → results/*.json · png/*.png.

기준: hardware/sim/SIM-001b-criteria.md (실행 전에 커밋, CRITERIA_COMMIT).
사용: python hardware/sim/sim001b/run.py   (종료 코드 = fail + error 수)
ngspice: 환경 변수 NGSPICE (기본 C:/Users/gh/tools/ngspice/47/Spice64/bin/ngspice_con.exe)
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(SIM))
NG = os.environ.get("NGSPICE", "C:/Users/gh/tools/ngspice/47/Spice64/bin/ngspice_con.exe")
CRITERIA_COMMIT = "7cab389"
SCH_COMMIT = "a2d878c"   # C-020 (S6): 전면 R20 100k·R21 1k·D4 BAT54WS, R5 100k·D5 BAT54WS (+ C-018/C-019: R6 6.04k, R17 4.7k·C19 4.7nF, C20·C21 4.7nF)
ILIM = 1.86   # TPS26600 R6 6.04 kΩ: I(OL) 최소 1.86 A (대표 ≈1.99 A, 계약 v1.14 3.1절 L108) — "시험 회로의 ILIM"을 보수적으로 최솟값으로
ILIM_OLD = 1.49   # 7cab389 작성 때 회로(R6 8.06 kΩ)의 숫자 — 비교로만 적는다
plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def rel(p):
    return os.path.relpath(p, REPO).replace("\\", "/")


def sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ng_version():
    r = subprocess.run([NG, "-v"], capture_output=True, text=True)
    m = re.search(r"ngspice-(\S+)", r.stdout + r.stderr)
    return m.group(1) if m else "?"


# ---------------------------------------------------------------- 실행 · 파싱
def run_tran(body, vecs, tstop, tstep, tmax, save_as=None):
    """body = 소자 줄. vecs = 저장할 벡터 식 목록. 반환: dict(name -> array), 'time'."""
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.txt").replace("\\", "/")
        net = (f"* SIM-001b\n{body}\n.options reltol=1e-3 abstol=1e-9 vntol=1e-6 itl4=200\n"
               f".tran {tstep} {tstop} 0 {tmax} uic\n.control\nset wr_singlescale\nset wr_vecnames\nrun\n"
               f"wrdata {out} {' '.join(vecs)}\nquit\n.endc\n.end\n")
        if save_as:
            with open(save_as, "w", encoding="utf-8", newline="\n") as f:
                f.write(net.replace(out, "out.txt"))
        cir = os.path.join(td, "n.cir")
        with open(cir, "w", encoding="utf-8") as f:
            f.write(net)
        r = subprocess.run([NG, "-b", cir], capture_output=True, text=True, timeout=3600)
        if not os.path.exists(out):
            raise RuntimeError("ngspice 출력 없음: " + (r.stdout + r.stderr)[-800:])
        with open(out) as f:
            head = f.readline().split()
            data = np.loadtxt(f)
    d = {h: data[:, i] for i, h in enumerate(head)}
    d["time"] = data[:, 0]
    return d, [h for h in head]


def run_op(body, prints, save_as=None):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.txt").replace("\\", "/")
        net = (f"* SIM-001b op\n{body}\n.control\nop\nprint {' '.join(prints)} > {out}\nquit\n.endc\n.end\n")
        if save_as:
            with open(save_as, "w", encoding="utf-8", newline="\n") as f:
                f.write(net.replace(out, "out.txt"))
        cir = os.path.join(td, "n.cir")
        with open(cir, "w", encoding="utf-8") as f:
            f.write(net)
        r = subprocess.run([NG, "-b", cir], capture_output=True, text=True, timeout=600)
        if not os.path.exists(out):
            raise RuntimeError("ngspice op 출력 없음: " + (r.stdout + r.stderr)[-800:])
        txt = open(out).read()
    vals = {}
    for m in re.finditer(r"^\s*(\S+)\s*=\s*([-+0-9.eE]+)", txt, re.M):
        vals[m.group(1).lower()] = float(m.group(2))
    return vals


def col(d, heads, i):
    return d[heads[i]]


def cross(t, y, level, rising=True, after=0.0):
    idx = np.where(t >= after)[0]
    for i in idx[:-1]:
        a, b = y[i], y[i + 1]
        if (rising and a < level <= b) or (not rising and a > level >= b):
            return t[i] + (level - a) / (b - a) * (t[i + 1] - t[i])
    return None


def win_mean(t, y, t0, t1):
    m = (t >= t0) & (t <= t1)
    if m.sum() < 2:
        return float("nan")
    return float(np.trapezoid(y[m], t[m]) / (t[m][-1] - t[m][0]))


def moving_max(t, y, w, t0):
    """시간 가중 이동 평균(창 w)의 최댓값, t0 이후."""
    m = t >= t0
    t, y = t[m], y[m]
    acc = np.concatenate(([0.0], np.cumsum((y[1:] + y[:-1]) / 2 * np.diff(t))))
    j = np.searchsorted(t, t + w)
    ok = j < len(t)
    i = np.nonzero(ok)[0]
    if len(i) == 0:
        return float("nan")
    return float(np.max((acc[j[ok]] - acc[i]) / (t[j[ok]] - t[i])))


def check(name, op, limit, unit, value, corner):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        ok = False
    elif op == "<=":
        ok = value <= limit
    elif op == ">=":
        ok = value >= limit
    elif op == "==":
        ok = value == limit
    else:
        ok = limit[0] <= value <= limit[1]
    return {"name": name, "op": op, "limit": limit, "unit": unit,
            "value": None if value is None else (float(f"{value:.6g}") if isinstance(value, float) else value),
            "corner": corner, "pass": bool(ok)}


# ---------------------------------------------------------------- 모델
def led_model(name, vf1):
    """VSMA1085400: N=3(이중 스택), RS 0.105 Ω, 1 A 에서 VF = vf1 (Vishay 80294 p.3 두 점 맞춤)."""
    nvt, rs = 3 * 0.025852, 0.105
    is_ = math.exp(-(vf1 - rs) / nvt)
    return f".model {name} D(IS={is_:.4e} N=3 RS={rs} CJO=200p)\n"


SS24 = ".model ss24 D(IS=1.87e-6 N=1.1 RS=0.061 CJO=130p BV=40)\n"   # Vishay 89008: 0.436 V@1A · 0.517 V@2A
GEN_D = ".model dsi D(IS=1e-14 N=1)\n"                                # 일반 실리콘 ESD·바디 다이오드(가정)
BAT54 = ".model bat54 D(IS=2e-7 N=1.05 RS=1.5 CJO=10p)\n"             # BAT54WS 근사(가정)


def al8860(name, vm, rsw):
    """AL8860 동작 모델: 하이사이드 감지 히스테리시스(평균 vm, ±20 %), 소프트스타트 0.1 ms, CTRL<0.2 V 대기."""
    return f"""
.subckt {name} vin set sw ctrl gnd
Rpu ctrl n5 50k
V5 n5 gnd 5
Ben en gnd V = 0.5*(1+tanh((V(ctrl)-0.225)/0.01))
Css ss gnd 1n
Rss ss gnd 1g
Bss gnd ss I = 10u*V(en)*0.5*(1-tanh((V(ss)-1)/0.01)) - (1-V(en))*V(ss)/100
Bx x gnd V = (V(vin)-V(set)) / max(V(ss), 0.02)
Ahy x cmp hy_{name}
.model hy_{name} hyst(in_low={vm - 1e-5} in_high={vm + 1e-5} hyst={0.2 * vm} out_lower_limit=0 out_upper_limit=1 input_domain=0.002 fraction=TRUE)
Bg g0 gnd V = V(en) * (1 - V(cmp))
* 게이트 10 ns 평활 (전파지연 45 ns 의 일부 · 수치 안정)
Rgf g0 g 1k
Cgf g gnd 10p
Ssw sw gnd g gnd swm_{name}
.model swm_{name} sw vt=0.5 vh=0.05 ron={rsw} roff=10meg
Csw sw gnd 20p
.ends
"""


def string(k, rs, L, dcr, ledm):
    return f"""
R{13 if k == 'A' else 14} v12 set{k} {rs}
D{k}1 set{k} m{k} {ledm}
D{k}2 m{k} k{k} {ledm}
Vil{k} k{k} li{k} 0
L{k} li{k} lx{k} {L}
RL{k} lx{k} sw{k} {dcr}
DF{k} sw{k} v12 ss24
X{k} v12 set{k} sw{k} ctrl 0 al_{k}
C{k}1 v12 c{k}e 10u
RC{k} c{k}e 0 5m
C{k}2 v12 0 100n
"""


CORNERS = {
    # name: vm, rs, L, vf1, vin
    "typ": (0.100, 0.100, 47e-6, 3.1, 12.0),
    "imin": (0.096, 0.101, 47e-6, 3.3, 11.4),
    "imax": (0.104, 0.099, 37.6e-6, 2.8, 12.6),
    "fmax": (0.096, 0.101, 37.6e-6, 2.8, 12.6),
    "dmax": (0.100, 0.100, 47e-6, 3.3, 11.4),
    "dmin": (0.100, 0.100, 47e-6, 2.8, 12.6),
    "worst_in": (0.104, 0.099, 47e-6, 3.3, 11.4),
}


def ir_body(corner, strings=("A",), ctrl="open"):
    vm, rs, L, vf1, vin = CORNERS[corner]
    b = f"Vin vs 0 {vin}\nRsrc vs v12 10m\n" + led_model("led", vf1) + SS24
    for k in strings:
        b += al8860(f"al_{k}", vm, 0.3) + string(k, rs, L, 0.24 if corner != "typ" else 0.2, "led")
    if ctrl == "open":
        b += "Rctrl ctrl 0 1g\n"
    else:
        b += ctrl
    return b


def fsw_stats(t, isw_on, t0):
    """스위치 게이트(켜짐 1) 파형에서 주파수 · tON · 듀티."""
    m = t >= t0
    t, g = t[m], isw_on[m]
    up = [cross(t, g, 0.5, True, t[0])]
    ups, dns = [], []
    for i in range(len(t) - 1):
        if g[i] < 0.5 <= g[i + 1]:
            ups.append(t[i])
        elif g[i] >= 0.5 > g[i + 1]:
            dns.append(t[i])
    del up
    if len(ups) < 3 or len(dns) < 3:
        return float("nan"), float("nan"), float("nan")
    per = np.diff(ups)
    tons = [d - u for u in ups for d in dns if d > u][:0]
    tons = []
    for u in ups:
        later = [d for d in dns if d > u]
        if later:
            tons.append(later[0] - u)
    T = float(np.median(per))
    return 1 / T, float(min(tons)), float(np.median(tons)) / T


# ---------------------------------------------------------------- 시험
def b1():
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L1-al8860.png")
    res = {}
    for c in ("typ", "imin", "imax", "fmax", "dmax", "dmin"):
        body = ir_body(c)
        vecs = ["v(v12)-v(setA)", "i(VilA)", "v(XA.g)"]
        d, h = run_tran(body, vecs, "0.6m", "5n", "20n", save_as=os.path.join(SIM, "SIM-L1.cir") if c == "imax" else None)
        t = d["time"]
        rs = CORNERS[c][1]
        iled = col(d, h, 1) / rs
        il = col(d, h, 2)
        g = col(d, h, 3)
        t0 = 0.4e-3
        f, ton, duty = fsw_stats(t, g, t0)
        m = t >= t0
        res[c] = dict(t=t, iled=iled, il=il, mean=win_mean(t, iled, t0, t[-1]), pk=float(iled[m].max()),
                      ilpk=float(il[m].max()), ripple=float(iled[m].max() - iled[m].min()), f=f, ton=ton, duty=duty)
    checks.append(check("LED 평균 전류 (최소 모서리)", ">=", 0.90, "A", res["imin"]["mean"], "imin: VSENSE 96mV, Rs 0.101, VF 최대, 11.4V"))
    checks.append(check("LED 평균 전류 (최대 모서리)", "<=", 1.10, "A", res["imax"]["mean"], "imax: VSENSE 104mV, Rs 0.099, L −20%, VF 최소, 12.6V"))
    checks.append(check("LED 피크 전류", "<=", 1.5, "A", res["imax"]["pk"], "imax"))
    checks.append(check("인덕터 피크 전류", "<=", 1.6, "A", max(r["ilpk"] for r in res.values()), "전 모서리 최대"))
    checks.append(check("스위칭 주파수", "<=", 1.0e6, "Hz", max(r["f"] for r in res.values()), "전 모서리 최대"))
    checks.append(check("스위치 켜짐 시간 tON", ">=", 500e-9, "s", min(r["ton"] for r in res.values()), "전 모서리 최소"))
    dmin, dmax = min(r["duty"] for r in res.values()), max(r["duty"] for r in res.values())
    checks.append(check("듀티 최소", "between", [0.25, 0.75], "-", dmin, "전 모서리"))
    checks.append(check("듀티 최대", "between", [0.25, 0.75], "-", dmax, "전 모서리"))
    checks.append(check("LED 전류 리플 p-p ÷ 평균", "<=", 0.5, "-", res["typ"]["ripple"] / res["typ"]["mean"], "typ"))
    notes.append("모서리별: " + "; ".join(f"{c} 평균 {r['mean']:.3f}A 피크 {r['pk']:.3f}A IL피크 {r['ilpk']:.3f}A f {r['f'] / 1e3:.0f}kHz tON {r['ton'] * 1e6:.2f}µs D {r['duty']:.2f}" for c, r in res.items()))
    fig, ax = plt.subplots(2, 1, figsize=(9, 6))
    for c in ("typ", "imin", "imax"):
        r = res[c]
        m = r["t"] >= 0.55e-3
        ax[0].plot(r["t"][m] * 1e6, r["iled"][m], label=f"{c} 평균 {r['mean']:.3f} A")
        ax[1].plot(r["t"][m] * 1e6, r["il"][m], label=c)
    ax[0].set_ylabel("LED 전류 [A]"); ax[0].legend(); ax[0].grid(alpha=.3)
    ax[1].axhline(1.6, color="r", ls="--", lw=.8, label="기준 1.6 A"); ax[1].set_ylabel("인덕터 전류 [A]"); ax[1].set_xlabel("시간 [µs]"); ax[1].legend(); ax[1].grid(alpha=.3)
    ax[0].set_title("SIM-L1 AL8860 한 스트링 정상 상태 (마지막 50 µs)")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L1", title="AL8860 한 스트링 LED 전류·리플·주파수", refs=["U4", "R13", "L1", "D1", "D_IR_A1", "D_IR_A2", "C14", "C15"],
                checks=checks, png=[png], net="SIM-L1.cir", notes=notes,
                model=dict(source="데이터시트 동작 모델 (AL8860 히스테리시스·소프트스타트·CTRL, VSMA·SS24 다이오드 맞춤)",
                           url="https://www.diodes.com/assets/Datasheets/AL8860.pdf", license="—", behavioral=True,
                           basis="AL8860 DS39014 Rev.8-2 p.2·4·11–13; VSMA1085400 80294 p.3; SS24S 89008 p.2; SRN6045TA REV.06/24 p.1"))


def b2():
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L2-ab-input.png")
    out = {}
    for c in ("worst_in", "typ"):
        body = ir_body(c, ("A", "B"))
        d, h = run_tran(body, ["i(Vin)", "i(VilA)", "i(VilB)"], "0.6m", "5n", "20n",
                        save_as=os.path.join(SIM, "SIM-L2.cir") if c == "worst_in" else None)
        t = d["time"]
        iin = -col(d, h, 1)
        out[c] = dict(t=t, iin=iin, mean=win_mean(t, iin, 0.4e-3, t[-1]), mov=moving_max(t, iin, 20e-6, 0.3e-3))
    checks.append(check("12V_IR 입력 평균 전류 (최대 모서리) ≤ ILIM", "<=", ILIM, "A", out["worst_in"]["mean"], f"104mV, Rs 0.099, VF 최대, 11.4V · 옛 1.49A 대비 {'ok' if out['worst_in']['mean'] <= ILIM_OLD else '초과'}"))
    checks.append(check("12V_IR 입력 20µs 이동 평균 최댓값 ≤ ILIM", "<=", ILIM, "A", out["worst_in"]["mov"], f"같은 모서리 (소프트스타트 뒤 0.3 ms~) · 옛 1.49A 대비 {'ok' if out['worst_in']['mov'] <= ILIM_OLD else '초과'}"))
    checks.append(check("12V_IR 입력 평균 전류 (대표)", "<=", 1.30, "A", out["typ"]["mean"], "typ"))
    # 민감도(판정 밖): 전원 임피던스를 10 mΩ → 케이블·eFuse 근사 0.1 Ω + 30 nH 로 바꾸면 리플을 입력 캡이 더 맡는다
    ds, hs = run_tran(ir_body("worst_in", ("A", "B")).replace("Rsrc vs v12 10m", "Rsrc vs vx 0.1\nLsrc vx v12 30n"),
                      ["i(Vin)"], "0.6m", "5n", "20n")
    sens = moving_max(ds["time"], -col(ds, hs, 1), 20e-6, 0.3e-3)
    notes.append(f"20µs 이동 평균 최댓값 {out['worst_in']['mov']:.3f} A 는 정상 상태(약 0.575 ms)에서 두 스트링 켬 구간이 겹치는 맥놀이 — 평균 {out['worst_in']['mean']:.3f} A. "
                 f"민감도(판정 밖): 전원 임피던스 0.1 Ω + 30 nH(케이블·eFuse 근사, 가정)이면 {sens:.3f} A. TPS26600 은 ILIM 을 넘는 짧은 구간을 전류 제한으로 다루고 차단은 고장 타이머 뒤라(데이터시트 확인 필요) 경계 판정")
    fig, ax = plt.subplots(figsize=(9, 4))
    for c, r in out.items():
        ax.plot(r["t"] * 1e3, r["iin"], lw=.6, label=f"{c} 평균 {r['mean']:.3f} A")
    ax.axhline(ILIM, color="r", ls="--", label=f"ILIM {ILIM} A (R6 6.04k, I(OL) 최소)"); ax.axhline(ILIM_OLD, color="gray", ls=":", label="옛 ILIM 1.49 A")
    ax.set_xlabel("시간 [ms]"); ax.set_ylabel("12V_IR 입력 전류 [A]"); ax.legend(); ax.grid(alpha=.3)
    ax.set_title("SIM-L2 스트링 A+B 동시 100 % — 12V_IR 입력 전류 (입력 캡 C14·C16 포함)")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L2", title="스트링 A+B 동시 — 12V_IR eFuse 입력 전류 합", refs=["U4", "U5", "R13", "R14", "L1", "L2", "C14", "C16", "U2·R6 6.04k(carrier TPS26600)"],
                checks=checks, png=[png], net="SIM-L2.cir", notes=notes, out=out,
                model=b1_model())


def b1_model():
    return dict(source="데이터시트 동작 모델 (AL8860 히스테리시스·소프트스타트·CTRL)", url="https://www.diodes.com/assets/Datasheets/AL8860.pdf",
                license="—", behavioral=True, basis="AL8860 DS39014 Rev.8-2 p.2·4·11–13; VSMA1085400 80294 p.3; SS24S 89008 p.2; TPS26600 R6 6.04k I(OL) 최소 1.86A·대표 1.99A (계약 v1.14 3.1절, C-018)")


GPIO = "93.75"   # SoC 1.8V IO 출력 저항 ≈ (1.8-1.35)/4.8mA (Table 2-8, DS=00)


def b3(b2res):
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L3-pwm25.png")
    ctrl = (f"Vpw pw0 0 PULSE(1.71 0 1.875m 1u 1u 0.625m 2.5m)\nRpw pw0 irpwm {GPIO}\nR12 core irpwm 100k\nVcore core 0 1.8\n"
            "M5 ctrl irpwm 0 0 nq7\n.model nq7 nmos level=1 vto=1.0 kp=1.79\nCg5 irpwm 0 61p\n")
    body = ir_body("worst_in", ("A", "B"), ctrl)
    d, h = run_tran(body, ["i(Vin)", "i(VilA)", "i(VilB)", "v(ctrl)", "v(irpwm)", "(v(v12)-v(setA))/0.099", "(v(v12)-v(setB))/0.099"],
                    "7.5m", "10n", "50n", save_as=os.path.join(SIM, "SIM-L3.cir"))
    t = d["time"]
    iin = -col(d, h, 1)
    ileds = col(d, h, 6) + col(d, h, 7)
    vctrl = col(d, h, 4)
    cont = None
    for k in ("A", "B"):
        pass
    r2 = b2res["out"]["worst_in"]
    # 100 % 연속 A+B LED 평균 = 같은 모서리 B2 의 LED 합 → B2 에서 다시 계산하지 않고 이 실행의 켬 구간 정상값 대신 B2 입력과 독립으로
    cont_body = ir_body("worst_in", ("A", "B"))
    dc, hc = run_tran(cont_body, ["(v(v12)-v(setA))/0.099", "(v(v12)-v(setB))/0.099"], "0.6m", "5n", "20n")
    cont = win_mean(dc["time"], col(dc, hc, 1) + col(dc, hc, 2), 0.4e-3, dc["time"][-1])
    avg = win_mean(t, ileds, 2.5e-3, 7.5e-3)
    ratio = avg / cont
    off = (t > 2.5e-3 + 0.1e-3) & (t < 2.5e-3 + 1.875e-3)
    checks.append(check("A+B LED 평균 ÷ 100 % 평균 (최대 모서리)", "<=", 0.255, "-", ratio, "worst_in, 400Hz, 켬 625µs"))
    checks.append(check("끔 구간 LED 전류 (끌어내림 100µs 뒤)", "<=", 1e-3, "A", float(np.abs(ileds[off]).max()), "worst_in"))
    mv3 = moving_max(t, iin, 20e-6, 1.0e-3)
    checks.append(check("켬 순간 12V_IR 20µs 이동 평균 최댓값 ≤ ILIM", "<=", ILIM, "A", mv3, f"worst_in, A+B 동시, 1 ms 이후(uic 초기 충전 제외) · 옛 1.49A 대비 {'ok' if mv3 <= ILIM_OLD else '초과'}"))
    checks.append(check("IR_CTRL 끔 레벨", "<=", 0.2, "V", float(vctrl[off].max()), "IR_PWM = 1.71V − 93.75Ω, Q5 vto 1.0V kp 최소"))
    notes.append(f"기록만: 100 % 평균 {cont:.3f} A, PWM 평균 {avg:.3f} A, 켬 비율 실효 {ratio:.3f} (소프트스타트 0.1 ms 손실 포함 — 조사량 하한)")
    offm = (t > 2.6e-3) & (t < 2.7e-3)
    notes.append(f"끔 구간 LED 전류: 끈 뒤 100 µs 의 |I| 최대는 인덕터와 LED·다이오드 접합 용량의 감쇠 링잉(역방향 변위 전류, 평균 {np.mean(ileds[offm]) * 1e6:.1f} µA)이고 3 ms 에 0.5 mA, 4 ms 에 0 — 발광(순방향 평균)이 아니다. 기준을 '순방향 평균'으로 고칠지는 orch 판단")
    notes.append("분석 창 수정(결과 본 뒤, 기준 변경 아님): 켬 순간 이동 평균을 t ≥ 1 ms 로 — 첫 실행은 t = 0 의 uic 입력 캡 초기 충전(11.5 A)을 넣었다")
    fig, ax = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    ax[0].plot(t * 1e3, col(d, h, 5)); ax[0].set_ylabel("IR_PWM [V]")
    ax[1].plot(t * 1e3, ileds, lw=.5); ax[1].set_ylabel("LED A+B [A]")
    ax[2].plot(t * 1e3, iin, lw=.5); ax[2].axhline(ILIM, color="r", ls="--", lw=.8); ax[2].set_ylabel("12V_IR 입력 [A]"); ax[2].set_xlabel("시간 [ms]"); ax[2].set_ylim(0, 3)
    for a in ax:
        a.grid(alpha=.3)
    ax[0].set_title(f"SIM-L3 PWM 25 % (400 Hz) — 실효 켬 비율 {ratio:.3f}")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L3", title="IR PWM 25 % 디밍 (IR_PWM → Q5 → IR_CTRL)", refs=["Q5", "R12", "U4", "U5"], checks=checks, png=[png],
                net="SIM-L3.cir", notes=notes, model=b1_model())


def drv_sub(rh, rl):
    return f"""
.subckt drv vm out1 out2 in1 in2 vcc gnd
Ri1 in1 gnd 100k
Ri2 in2 gnd 100k
Ba a gnd V = V(in1) > 0.46*V(vcc) ? 1 : 0
Bb b gnd V = V(in2) > 0.46*V(vcc) ? 1 : 0
Bh1 h1 gnd V = V(a)*(1-V(b))
Bh2 h2 gnd V = V(b)*(1-V(a))
Bl1 l1 gnd V = V(b)*(1-V(a)) + V(a)*V(b)
Bl2 l2 gnd V = V(a)*(1-V(b)) + V(a)*V(b)
S1 vm out1 h1 gnd sh
S2 out1 gnd l1 gnd sl
S3 vm out2 h2 gnd sh
S4 out2 gnd l2 gnd sl
D1 out1 vm dsi
D2 gnd out1 dsi
D3 out2 vm dsi
D4 gnd out2 dsi
.model sh sw vt=0.5 vh=0.05 ron={rh} roff=100meg
.model sl sw vt=0.5 vh=0.05 ron={rl} roff=100meg
.ends
"""


def b4():
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L4-drv8837.png")
    res = {}
    for c, vm, rc, rh in (("max", 5.25, 18.0, 0.14), ("min", 4.75, 22.0, 0.165)):
        body = (GEN_D + drv_sub(rh, rh) + f"Vm vm 0 {vm}\nVcc vcc 0 2.744\n"
                f"Vi1 i1 0 PWL(0 0 10m 0 10.001m 1.71 210m 1.71 210.001m 0)\nR1g i1 in1 {GPIO}\n"
                f"Vi2 i2 0 PWL(0 0 500m 0 500.001m 1.71 700m 1.71 700.001m 0)\nR2g i2 in2 {GPIO}\n"
                f"X2 vm icra icrb in1 in2 vcc 0 drv\nVsc icra c1 0\nRcoil c1 icrb {rc}\n")
        d, h = run_tran(body, ["i(Vsc)", "v(icra)-v(icrb)", "v(in2)", "v(in1)"], "800m", "10u", "100u",
                        save_as=os.path.join(SIM, "SIM-L4.cir") if c == "max" else None)
        res[c] = (d, h)
    d, h = res["max"]
    t, i = d["time"], col(d, h, 1)
    checks.append(check("코일 전류 (밤, 최대 모서리)", "<=", 0.30, "A", float(np.abs(i).max()), "5.25V, 18Ω, rDS 0.28Ω"))
    dm, hm = res["min"]
    tm, imn, vdm = dm["time"], col(dm, hm, 1), col(dm, hm, 2)
    night = (tm > 0.05) & (tm < 0.2)
    checks.append(check("코일 전류 (밤, 최소 모서리)", ">=", 0.19, "A", float(imn[night].min()), "4.75V, 22Ω, rDS 0.33Ω"))
    pk = np.abs(imn).max()
    on = np.abs(imn) > 0.5 * pk
    tt = tm[on & (tm < 0.4)]
    width = float(tt[-1] - tt[0]) if len(tt) else float("nan")
    checks.append(check("펄스 시간 (|I|>50 %)", "between", [0.195, 0.205], "s", width, "min 모서리, 밤 펄스"))
    checks.append(check("극성 밤 V(ICR_A)-V(ICR_B)", ">=", 4.0, "V", float(vdm[night].min()), "IN1=1 IN2=0, min 모서리"))
    day = (tm > 0.55) & (tm < 0.69)
    checks.append(check("극성 낮 V(ICR_A)-V(ICR_B)", "<=", -4.0, "V", float(vdm[day].max()), "IN1=0 IN2=1, min 모서리"))
    coast = (tm > 0.22) & (tm < 0.49)
    checks.append(check("펄스 끝 10 ms 뒤 코일 전류 (코스트)", "<=", 1e-3, "A", float(np.abs(imn[(tm > 0.22) & (tm < 0.23)]).max()), "코일 인덕턴스 미확인 → 저항 부하"))
    vin2 = float(col(dm, hm, 3)[day].min())
    checks.append(check("IN2 High − VIH 최대(0.5×2.856V)", ">=", 0.1, "V", vin2 - 0.5 * 2.856, "VDDIO 1.71V, 출력 저항 93.75Ω, 100k 풀다운"))
    notes.append(f"코스트 구간 최대 |I| {float(np.abs(imn[coast]).max()) * 1e3:.3f} mA; IN2 High {vin2:.3f} V")
    fig, ax = plt.subplots(2, 1, figsize=(9, 5), sharex=True)
    ax[0].plot(tm * 1e3, imn * 1e3, label="min"); ax[0].plot(t * 1e3, i * 1e3, label="max", alpha=.7)
    ax[0].set_ylabel("코일 전류 [mA]"); ax[0].legend(); ax[0].grid(alpha=.3)
    ax[1].plot(tm * 1e3, vdm); ax[1].set_ylabel("V(ICR_A)−V(ICR_B) [V]"); ax[1].set_xlabel("시간 [ms]"); ax[1].grid(alpha=.3)
    ax[0].set_title("SIM-L4 DRV8837 ICR 펄스 200 ms — 밤(IN1) 10 ms · 낮(IN2) 500 ms")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L4", title="DRV8837 ICR 펄스 — 코일 전류·시간·극성", refs=["U2(front DRV8837)", "R1", "J2", "CLA216"], checks=checks, png=[png],
                net="SIM-L4.cir", notes=notes,
                model=dict(source="데이터시트 동작 모델 (H-브리지 스위치 + 진리표)", url="https://www.ti.com/lit/ds/symlink/drv8837.pdf", license="—",
                           behavioral=True, basis="TI SLVSBA4F p.8–9 §6.5–6.6, p.13 Table 7-1; 코일 20Ω ±10% 가정(계약 3.2절), 인덕턴스 미확인"))


def q_models(q6vto, q6kp, q7vto, q7kp):
    return (f".model pq6 pmos level=1 vto={q6vto} kp={q6kp}\n.model nq7 nmos level=1 vto={q7vto} kp={q7kp}\n" + GEN_D)


def cam_sw(vcore, q):
    return (q + f"Vcore core 0 {vcore}\nRcore core c18 0.1\n"
            f"Ven e0 0 PWL(0 0 1m 0 1.001m 1.71 6m 1.71 6.001m 0)\nRen e0 en {GPIO}\n"
            "M6 cam g6i c18 c18 pq6\nRg6 g6 g6i 15.2\nCgs6 g6i c18 731p\nCgd6 g6i cam 77p\nDb6 cam c18 dsi\n"
            "R17 c18 g6 4.7k\nR18 g7 g6 1k\nM7 g7 en 0 0 nq7\nCg7 en 0 55p\nCd7 en g7 5.4p\nC19 g6 cam 4.7n\n"
            "C18 cam c18e 1u\nR18e c18e 0 5m\nC11 cam 0 100n\nRx1 cam 0 450\nR19 cam 0 10k\n")   # C-017/C-018: R17 4.7k · R18 1k · C19 4.7nF · R19 10k


def b5():
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L5-cam1v8.png")
    # 돌입 최악: Q6 강함(vto -0.5, kp 13.4 = RDS 68mΩ@-1.8V 대표), Q7 강함, CORE_1V8 1.89
    di, hi = run_tran(cam_sw(1.89, q_models(-0.5, 13.4, 0.5, 4.0)), ["-i(Vcore)", "v(cam)", "v(en)", "v(g6)-v(c18)"], "8m", "1n", "20n",
                      save_as=os.path.join(SIM, "SIM-L5.cir"))
    # 켜짐·꺼짐 최악: Q6 약함(vto -0.9, kp 5.56 = 0.2Ω@-1.8V), Q7 약함(vto 1.0, kp 1.79), CORE_1V8 1.8 (기준 1.71V = 95 %)
    ds, hs = run_tran(cam_sw(1.8, q_models(-0.9, 5.56, 1.0, 1.79)), ["-i(Vcore)", "v(cam)", "v(en)", "v(g6)-v(c18)"], "8m", "1n", "20n")
    ti, ii = di["time"], col(di, hi, 1)
    ts, vcam, ven, vgs = ds["time"], col(ds, hs, 2), col(ds, hs, 3), col(ds, hs, 4)
    t_en = cross(ts, ven, 0.855, True)
    t_on = cross(ts, vcam, 1.71, True, t_en or 0)
    checks.append(check("켜짐 시간 (CAM_EN 50 % → CAM_1V8 ≥ 1.71 V)", "<=", 1e-3, "s", (t_on - t_en) if (t_on and t_en) else None, "Q6·Q7 약함, CORE_1V8 1.8V"))
    after = ti > 0.9e-3   # uic 초기 충전 제외 — CAM_EN 상승(1 ms) 돌입만
    checks.append(check("CORE_1V8 돌입 피크 전류", "<=", 0.3, "A", float(ii[after].max()), "Q6·Q7 강함, CORE_1V8 1.89V, 경로 0.1Ω(가정), CAM_EN 상승 뒤"))
    ii = np.where(after, ii, 0.0)
    notes.append("분석 창 수정(결과 본 뒤, 기준 변경 아님): 돌입을 CAM_EN 상승 뒤(t > 0.9 ms)로 — 첫 실행은 t = 0 의 uic 초기 충전(7.8 A)을 넣었다")
    t_dn = cross(ts, ven, 0.855, False, 5e-3)
    t_off = cross(ts, vgs, -0.3, True, t_dn or 0)
    checks.append(check("꺼짐: CAM_EN 하강 → Q6 VGS > −0.3 V", "<=", 100e-6, "s", (t_off - t_dn) if (t_off and t_dn) else None, "Q6·Q7 약함"))
    t_low = cross(ts, vcam, 0.3, False, t_dn or 0)
    notes.append(f"기록만: 꺼진 뒤 CAM_1V8 < 0.3V 까지 {((t_low - t_dn) * 1e3) if (t_low and t_dn) else float('nan'):.2f} ms (X1 부하 450Ω 가정)")
    notes.append("C-018 회로(7760f38): Q7 드레인 → R18 1 kΩ → Q6 게이트, C19 4.7 nF, R17 4.7 kΩ(S5), R19 10 kΩ 블리더. 이전 결과: 656b50a a3b988c(돌입 5.11 A) · f0745ed 55480c0(꺼짐 347 µs)")
    fig, ax = plt.subplots(2, 1, figsize=(9, 5))
    m = (ti > 0.999e-3) & (ti < 1.02e-3)
    ax[0].plot((ti[m] - 1e-3) * 1e6, ii[m]); ax[0].axhline(0.3, color="r", ls="--", lw=.8); ax[0].set_ylabel("CORE_1V8 전류 [A]"); ax[0].set_xlabel("CAM_EN 상승 뒤 [µs]"); ax[0].grid(alpha=.3)
    ax[1].plot(ts * 1e3, vcam, label="CAM_1V8"); ax[1].plot(ts * 1e3, ven, label="CAM_EN"); ax[1].legend(); ax[1].set_xlabel("시간 [ms]"); ax[1].set_ylabel("[V]"); ax[1].grid(alpha=.3)
    ax[0].set_title("SIM-L5 CAM_1V8 스위치 Q6/Q7 — 돌입(위, 강한 모서리) · 켜짐/꺼짐(아래, 약한 모서리)")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L5", title="CAM_1V8 스위치 Q6/Q7 켜짐·꺼짐·돌입", refs=["Q6", "Q7", "R17", "R18", "C19", "R19", "C18", "C11", "X1"], checks=checks, png=[png],
                net="SIM-L5.cir", notes=notes,
                model=dict(source="레벨 1 MOSFET 맞춤 (데이터시트 VGS(th)·RDS(on)·Ciss·Rg)", url="https://www.diodes.com/assets/Datasheets/DMG2305UX.pdf",
                           license="—", behavioral=True, basis="DMG2305UX DS36196 Rev.8-2 p.2; DMG1012T DS31783 Rev.8-2 p.2; SG2002 Table 2-8 VOH; CORE_1V8 경로 0.1Ω·X1 450Ω 가정"))


def backfeed_body(soc_pu):
    pu = "Rpu_d sda core 55k\nRpu_c scl core 55k\n" if soc_pu else ""
    return (GEN_D + "Vcore core 0 1.89\nIq6 core cam 1u\nDb6 cam core dsi\nRx1 cam 0 100k\nR19 cam 0 10k\n"
            "R9 cam sda 4.7k\nR10 cam scl 4.7k\n"
            "Rpd_d sda 0 51k\nRpd_c scl 0 51k\nIlk_d 0 sda 10u\nIlk_c 0 scl 10u\n" + pu +
            "Vsd sda sd 0\nDs_d sd srail dsi\nVsc scl scx 0\nDs_c scx srail dsi\nRsr srail 0 10k\n"
            "R8 mclko mclk 22\nRx1o mclko 0 1meg\nVsm mclk smk 0\nDs_m smk srail dsi\n")


def b6():
    checks, notes = [], []
    pr = ["v(sda)", "v(scl)", "v(cam)", "v(mclk)", "i(vsd)", "i(vsc)"]
    v = run_op(backfeed_body(False), pr, save_as=os.path.join(SIM, "SIM-L6.cir"))
    vs = run_op(backfeed_body(True), pr)
    checks.append(check("센서 SDA → 꺼진 레일 전류", "<=", 1e-6, "A", abs(v.get("i(vsd)", float("nan"))), "PD 51k, 누설 +10µA, VCORE 1.89"))
    checks.append(check("센서 SCL → 꺼진 레일 전류", "<=", 1e-6, "A", abs(v.get("i(vsc)", float("nan"))), "같음"))
    checks.append(check("센서 SDA/SCL 핀 전압", "<=", 0.3, "V", max(v.get("v(sda)", 9), v.get("v(scl)", 9)), "같음"))
    checks.append(check("CAM_1V8 넷 전압 (꺼짐)", "<=", 0.3, "V", v.get("v(cam)", float("nan")), "Q6 IDSS 1µA, X1 꺼짐 100k(가정)"))
    checks.append(check("CAM_MCLK 전압 (X1 꺼짐)", "<=", 0.3, "V", v.get("v(mclk)", float("nan")), "X1 출력 1M(가정)"))
    notes.append(f"기록만(민감도 — SW가 IIC2 내부 풀업 55k 를 켠 경우): SDA {vs.get('v(sda)', float('nan')):.3f} V, 센서로 {abs(vs.get('i(vsd)', float('nan'))) * 1e6:.2f} µA, CAM_1V8 {vs.get('v(cam)', float('nan')):.3f} V")
    notes.append("가정: 센서 핀 ESD 다이오드 IS 1e-14, 꺼진 센서 레일 부하 10k, LTR-329 핀 누설 0(데이터시트 미확인)")
    notes.append("C-017/C-018 회로(7760f38): CAM_1V8–GND R19 10 kΩ 블리더 포함. 이전 회로 결과는 a3b988c")
    return dict(id="SIM-L6", title="꺼진 센서 역급전 (CAM_EN=0, O-33)", refs=["R9", "R10", "R19", "Q6", "X1", "R8", "J3(DF30)", "U3(LTR-329)"], checks=checks, png=[],
                net="SIM-L6.cir", notes=notes,
                model=dict(source="DC 동작점 (저항·다이오드·전류원)", url="", license="—", behavioral=True,
                           basis="SG2002 Table 2-8 RPD 51k(최소)·누설 ±10µA, PINOUT 시트 IIC2 패드 기본 PD, SDK cvi_board_init.c L12–13; DMG2305UX IDSS"))


def b7():
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L7-i2c-rise.png")
    sys.path.insert(0, os.path.join(REPO, "hardware", "pcb", "calc"))
    import microstrip_fd as ms
    Z, e = ms.solve(0.152, 0, 0.1855, 0.035, 4.74, mask_t=0.015, diff=False)
    cpm = math.sqrt(e) / (ms.C0 * Z) / 1000   # F/mm
    trace = (50 + 60) * cpm
    cb = 3 * 10e-12 + trace + 3e-12
    cbw = cb * 1.5
    rp = 4.7e3 * 1.05
    body = (f"Vdd vdd 0 1.71\nRp vdd bus {rp}\nCb bus 0 {cbw}\nVd d 0 PULSE(1 0 1u 1n 1n 10u 20u)\nSd bus 0 d 0 sod\n.model sod sw vt=0.5 vh=0.01 ron=50 roff=1g\n")
    d, h = run_tran(body, ["v(bus)"], "12u", "1n", "2n", save_as=os.path.join(SIM, "SIM-L7.cir"))
    t, vb = d["time"], col(d, h, 1)
    t30 = cross(t, vb, 0.3 * 1.71, True, 1e-6)
    t70 = cross(t, vb, 0.7 * 1.71, True, 1e-6)
    tr = (t70 - t30) if (t30 and t70) else None
    checks.append(check("tr 30→70 % — Fast-mode 400 kHz", "<=", 300e-9, "s", tr, f"Cb 최악 {cbw * 1e12:.1f} pF, Rp 4.935k"))
    checks.append(check("tr — Standard-mode 100 kHz", "<=", 1000e-9, "s", tr, "같음"))
    checks.append(check("Cb 최악", "<=", 400e-12, "F", cbw, "추정 × 1.5"))
    checks.append(check("Rp ≥ Rp(min)", ">=", 437, "Ω", 4.7e3 * 0.95, "4.7k −5 %"))
    notes.append(f"Cb 추정: 핀 3×10 pF(UM10204 Ci 최대, SG2002·LTR-329·GC2053 미확인) + 트랙 110 mm × {cpm * 1e15:.1f} fF/mm = {trace * 1e12:.1f} pF (microstrip_fd: w 0.152, h 0.1855, Er 4.74, 마스크 0.015) + 커넥터 3 pF = {cb * 1e12:.1f} pF; 최악 ×1.5 = {cbw * 1e12:.1f} pF")
    notes.append(f"해석식 0.8473·Rp·Cb = {0.8473 * rp * cbw * 1e9:.0f} ns")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot((t - 1e-6) * 1e9, vb); ax.axhline(0.3 * 1.71, ls=":", c="k"); ax.axhline(0.7 * 1.71, ls=":", c="k")
    ax.set_xlim(-50, 1200); ax.set_xlabel("해제 뒤 [ns]"); ax.set_ylabel("SDA/SCL [V]"); ax.grid(alpha=.3)
    ax.set_title(f"SIM-L7 I2C2 상승 (Rp 4.935k, Cb {cbw * 1e12:.1f} pF) tr = {tr * 1e9 if tr else float('nan'):.0f} ns")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L7", title="I2C2 풀업 상승 시간 (100/400 kHz)", refs=["R9", "R10", "U3", "J3", "SoC IIC2"], checks=checks, png=[png], net="SIM-L7.cir",
                notes=notes, model=dict(source="RC (버스 용량 추정 + 풀업)", url="https://www.nxp.com/docs/en/user-guide/UM10204.pdf", license="—",
                                        behavioral=True, basis="UM10204 Rev.7 Table 10·11, §7.1; hardware/pcb/calc/microstrip_fd.py; fab-rules-pcbway.md §2.1"))


AO3401A = ".model pa pmos level=1 vto={vto} kp=10\n"   # AOS AO3401A Rev3.1: VGS(th) -0.5/-0.9/-1.3, RDS(on) 60/85 mΩ@-2.5V → kp≈10


def rails_body(vto=-0.9, rli=110, rla=110, t_on=1e-3, t_off=20e-3):
    """센서 레일 (C-020 a2d878c): CORE_3V3 → Q1(AO3401A, 게이트 R20 100k ∥ (R21 1k + D4 BAT54WS → CAM_PG), C20 4.7n G–D) → CAM_IOVDD,
    Q2(게이트 R5 100k ∥ D5 BAT54WS(CAM_PG →), C21 4.7n G–D) → CAM_AVDD, CAM_PG = R4 100k 풀업 · Q3 DMG1012T(G=CAM_EN). 리셋 R7·C10·D3."""
    return (GEN_D + BAT54 + ".model nq nmos level=1 vto=1.0 kp=1.79\n" + AO3401A.format(vto=vto) +
            f"V33s v33s 0 3.3\nR33 v33s v33 0.1\nC33 v33 0 22u\n"
            f"Ven e0 0 PWL(0 0 {t_on:.6g} 0 {t_on + 1e-6:.6g} 1.71 {t_off:.6g} 1.71 {t_off + 1e-6:.6g} 0)\nRen e0 en {GPIO}\nR6 en 0 100k\n"
            "R7 en rst 10k\nC10 rst 0 100n\nD3 rst en bat54\n"
            "M3 pg en 0 0 nq\nCg3 en 0 61p\nR4 v33 pg 100k\n"
            "R20 pg pgio 100k\nR21 pgio d4a 1k\nD4 d4a pg bat54\nM1 iov g1i v33 v33 pa\nRg1 pgio g1i 7.8\nCgs1 g1i v33 590p\nCgd1 g1i iov 55p\nC20 pgio iov 4.7n\nDb1 iov v33 dsi\n"
            "R5 pg pgav 100k\nD5 pg pgav bat54\nM2 avd g2i v33 v33 pa\nRg2 pgav g2i 7.8\nCgs2 g2i v33 590p\nCgd2 g2i avd 55p\nC21 pgav avd 4.7n\nDb2 avd v33 dsi\n"
            f"C7 iov 0 1u\nRli iov 0 {rli}\nC8 avd 0 1u\nC9 avd 0 100n\nRla avd 0 {rla}\n")


RAIL_VECS = ["v(en)", "v(rst)", "v(iov)", "v(avd)", "v(v33)", "i(V33s)"]


def b8():
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L8-reset.png")
    d, h = run_tran(rails_body(), RAIL_VECS, "25m", "100n", "2u", save_as=os.path.join(SIM, "SIM-L8.cir"))
    t, ven, vr, vi, va = d["time"], col(d, h, 1), col(d, h, 2), col(d, h, 3), col(d, h, 4)
    t_rel = cross(t, vr, 0.7 * 1.8, True, 1e-3)
    t_pw = max(cross(t, vi, 0.9 * 3.3, True, 1e-3) or 1, cross(t, va, 0.9 * 3.3, True, 1e-3) or 1)
    checks.append(check("리셋 해제 − 센서 전원 90 % 시각", ">=", 0.0, "s", (t_rel - t_pw) if t_rel else None, "C-020 레일, AO3401A vto −0.9, 부하 30mA(가정)"))
    t_dn = cross(t, ven, 0.855, False, 19e-3)
    t_rl = cross(t, vr, 0.3 * 1.8, False, t_dn or 0)
    checks.append(check("CAM_EN 하강 → CAM_RESET < 0.54 V", "<=", 50e-6, "s", (t_rl - t_dn) if (t_rl and t_dn) else None, "D3 BAT54WS"))
    t_iv = cross(t, vi, 0.9 * 3.3, False, t_dn or 0)
    checks.append(check("전원 90 % 하강 − 리셋 하강", ">=", 0.0, "s", (t_iv - t_rl) if (t_iv and t_rl) else None, "같음"))
    notes.append(f"기록만: 리셋 해제 {((t_rel - 1e-3) * 1e3) if t_rel else float('nan'):.2f} ms (CAM_EN 뒤) vs X1 기동 최대 3 ms — GC2053 'MCLK 뒤 리셋 해제' 수치 요구는 미확인이라 판정 밖. 첫 I2C는 FW 가 CAM_EN 뒤 ≥5 ms")
    notes.append("C-020 레일(a2d878c: R20 100k·R21 1k·D4 / R5 100k·D5, C20·C21 4.7nF). AO3401A AOS Rev3.1 수치. 센서 레일 부하 30 mA(가정)")
    fig, ax = plt.subplots(figsize=(9, 4))
    for y, lb in ((ven, "CAM_EN"), (vr, "CAM_RESET"), (vi, "CAM_IOVDD"), (va, "CAM_AVDD")):
        ax.plot(t * 1e3, y, label=lb)
    ax.legend(); ax.set_xlabel("시간 [ms]"); ax.set_ylabel("[V]"); ax.grid(alpha=.3)
    ax.set_title("SIM-L8 센서 리셋 RC (R7 10k · C10 100 nF · D3) 와 센서 전원 (C-020)")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L8", title="센서 리셋 RC 시간과 전원 순서", refs=["R7", "C10", "D3", "Q1", "Q2", "Q3", "R4", "R5", "R6", "R20", "R21", "D4", "D5", "C20", "C21", "C7", "C8", "C9"],
                checks=checks, png=[png], net="SIM-L8.cir", notes=notes, model=rails_model())


def rails_model():
    return dict(source="RC + 레벨 1 MOSFET 근사", url="https://www.aosmd.com/res/datasheets/AO3401A.pdf", license="—", behavioral=True,
                basis="회로 boards.py a2d878c L181–196; D4·D5 BAT54WS 근사(가정); AO3401A AOS Rev3.1(VGS(th) -0.5/-0.9/-1.3, RDS(on) 60/85mΩ@-2.5V, Ciss 645 Crss 55 pF, Rg 7.8); DMG1012T DS31783; GC2053 사본 V1.1 §2.3·§9.2·§9.3; CORE_3V3 경로 0.1Ω·22µF(가정)")


# 부하 경우: (이름, IOVDD 부하 Ω, AVDD 부하 Ω) — GC2053 §2.3 최대 IIOVDD 2.5mA · IAVDD 18mA · IDVDD 39mA 를 3.3V 입력 전류로 근사
LOADS = (("DVDD→IOVDD", 3.3 / 41.5e-3, 3.3 / 18e-3), ("DVDD→AVDD", 3.3 / 2.5e-3, 3.3 / 57e-3))


def rail_runs(mod=None):
    runs = []
    for vto in (-0.5, -1.3):
        for lname, rli, rla in LOADS:
            body = rails_body(vto, rli, rla, 1e-3, 6e-3)
            d, h = run_tran(mod(body) if mod else body, RAIL_VECS, "40m", "50n", "2u",
                            save_as=os.path.join(SIM, "SIM-L9.cir") if (not mod and vto == -1.3 and lname == LOADS[0][0]) else None)
            runs.append((f"vto {vto} · {lname}", d, h))
    return runs


def b9(runs):
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L9-cam-off.png")
    rows = []
    for name, d, h in runs:
        t, ven, vr, vi, va, v3, i3 = (d["time"], *[col(d, h, k) for k in range(1, 7)])
        tdn = cross(t, ven, 0.855, False, 5.9e-3)
        ti = cross(t, vi, 0.9 * 3.3, False, tdn or 0)
        ta = cross(t, va, 0.9 * 3.3, False, tdn or 0)
        tr = cross(t, vr, 0.54, False, tdn or 0)
        m = t > 5.9e-3
        rows.append(dict(name=name, io_av=(ti - ta) if (ti and ta) else float("nan"), av_rst=(ta - tr) if (ta and tr) else float("nan"),
                         v3min=float(v3[m].min()), rev=float(max(0.0, i3[m].max())), t=t, vi=vi, va=va, vr=vr, ven=ven))
    w = lambda k, f=min: f(r[k] for r in rows)  # noqa: E731
    checks.append(check("IOVDD<90% − AVDD<90% (IOVDD 마지막)", ">=", 0.0, "s", w("io_av"), "최악 경우 (vto ±, DVDD 부하 두 경우)"))
    checks.append(check("AVDD<90% − RESET<0.54V (리셋 먼저)", ">=", 0.0, "s", w("av_rst"), "같음"))
    checks.append(check("끄는 동안 CORE_3V3 최저", ">=", 3.135, "V", w("v3min"), "같음 (경로 0.1Ω·22µF 가정)"))
    checks.append(check("레일 → CORE_3V3 역류 최대", "<=", 1e-3, "A", w("rev", max), "i(V33s) 양수 = 전원으로 되돌아감"))
    notes.append("경우별: " + "; ".join(f"{r['name']}: IOVDD−AVDD {r['io_av'] * 1e6:.1f} µs, AVDD−RESET {r['av_rst'] * 1e6:.1f} µs, CORE_3V3 최저 {r['v3min']:.3f} V" for r in rows))
    notes.append("가정: 모듈 BXF4677 내부 LDO 지연·문턱 미상 → 보드 레일 90 % 로 대신. DVDD12 공급 레일 미상 → 두 경우 중 나쁜 쪽")
    fig, axs = plt.subplots(len(rows), 1, figsize=(9, 2.2 * len(rows)), sharex=True)
    for ax, r in zip(axs, rows):
        m = (r["t"] > 5.95e-3) & (r["t"] < 7.5e-3)
        for y, lb in ((r["ven"], "CAM_EN"), (r["vr"], "RESET"), (r["vi"], "IOVDD"), (r["va"], "AVDD")):
            ax.plot((r["t"][m] - 6e-3) * 1e3, y[m], label=lb)
        ax.set_title(r["name"], fontsize=9); ax.grid(alpha=.3)
    axs[0].legend(fontsize=8, ncol=4); axs[-1].set_xlabel("CAM_EN 하강 뒤 [ms]")
    fig.suptitle("SIM-L9 CAM_EN 끄는 순서 (C-020)"); fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L9", title="CAM_EN 끄는 순서 — IOVDD·AVDD·리셋·CORE_3V3", refs=["Q1", "Q2", "Q3", "R4", "R5", "R20", "R21", "D4", "D5", "C20", "C21", "C7", "C8", "C9", "R7", "C10", "D3"],
                checks=checks, png=[png], net="SIM-L9.cir", notes=notes, model=rails_model())


def b10(runs):
    checks, notes, png = [], [], os.path.join(SIM, "png", "SIM-L10-cam-on.png")
    rows = []
    for name, d, h in runs:
        t, ven, vr, vi, va, v3, i3 = (d["time"], *[col(d, h, k) for k in range(1, 7)])
        ten = cross(t, ven, 0.855, True, 0.9e-3)
        ti = cross(t, vi, 0.9 * 3.3, True, ten or 0)
        ta = cross(t, va, 0.9 * 3.3, True, ten or 0)
        m = (t > 0.9e-3) & (t < 5.9e-3)
        rows.append(dict(name=name, av_io=(ta - ti) if (ti and ta) else float("nan"), ti=(ti - ten) if (ti and ten) else float("nan"),
                         ta=(ta - ten) if (ta and ten) else float("nan"), v3min=float(v3[m].min()), ipk=float((-i3[m]).max()),
                         t=t, vi=vi, va=va, ven=ven, i3=-i3))
    w = lambda k, f=min: f(r[k] for r in rows)  # noqa: E731
    checks.append(check("AVDD≥90% − IOVDD≥90% (IOVDD 먼저)", ">=", 50e-6, "s", w("av_io"), "최악 경우 (vto ±, DVDD 부하 두 경우)"))
    checks.append(check("켜는 동안 CORE_3V3 최저", ">=", 3.135, "V", w("v3min"), "같음"))
    checks.append(check("CORE_3V3 돌입 피크 전류", "<=", 1.0, "A", w("ipk", max), "같음 (CAM_EN 상승 뒤, uic 초기 충전 제외)"))
    notes.append("경우별: " + "; ".join(f"{r['name']}: IOVDD 90% {r['ti'] * 1e6:.1f} µs, AVDD 90% {r['ta'] * 1e6:.1f} µs, 차 {r['av_io'] * 1e6:.1f} µs, CORE_3V3 최저 {r['v3min']:.3f} V, 돌입 {r['ipk'] * 1e3:.0f} mA" for r in rows))
    notes.append("가정: GC2053 §9.2 t1(IOVDD→AVDD28 ≥50µs)을 보드 레일(모듈 LDO 입력) 90 % 로 대신 — 모듈 LDO 지연은 넣지 않음")
    fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    for r in rows:
        m = (r["t"] > 0.98e-3) & (r["t"] < 1.4e-3)
        ax[0].plot((r["t"][m] - 1e-3) * 1e6, r["vi"][m], label=f"IOVDD {r['name']}")
        ax[0].plot((r["t"][m] - 1e-3) * 1e6, r["va"][m], ls="--", label=f"AVDD {r['name']}")
        ax[1].plot((r["t"][m] - 1e-3) * 1e6, r["i3"][m] * 1e3, label=r["name"])
    ax[0].set_ylabel("[V]"); ax[0].legend(fontsize=7, ncol=2); ax[0].grid(alpha=.3)
    ax[1].set_ylabel("CORE_3V3 전류 [mA]"); ax[1].set_xlabel("CAM_EN 상승 뒤 [µs]"); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3)
    ax[0].set_title("SIM-L10 CAM_EN 켜는 순서 (C-020)")
    fig.tight_layout(); fig.savefig(png, dpi=110); plt.close(fig)
    return dict(id="SIM-L10", title="CAM_EN 켜는 순서 — IOVDD→AVDD ≥50µs·CORE_3V3", refs=["Q1", "Q2", "Q3", "R4", "R5", "R20", "R21", "D4", "D5", "C20", "C21", "C7", "C8", "C9"],
                checks=checks, png=[png], net="SIM-L9.cir", notes=notes, model=rails_model())


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.makedirs(os.path.join(SIM, "results"), exist_ok=True)
    os.makedirs(os.path.join(SIM, "png"), exist_ok=True)
    tool = dict(name="ngspice", version=ng_version(), sha256=sha256(NG))
    bad = 0
    order = [("SIM-L1", b1), ("SIM-L2", b2), ("SIM-L3", None), ("SIM-L4", b4), ("SIM-L5", b5), ("SIM-L6", b6), ("SIM-L7", b7), ("SIM-L8", b8),
             ("SIM-L9", None), ("SIM-L10", None)]
    runs = None
    b2res = None
    for tid, fn in order:
        try:
            if tid in ("SIM-L9", "SIM-L10") and runs is None:
                runs = rail_runs()
            r = b3(b2res) if tid == "SIM-L3" else b9(runs) if tid == "SIM-L9" else b10(runs) if tid == "SIM-L10" else fn()
            if tid == "SIM-L2":
                b2res = r
            verdict = "pass" if all(c["pass"] for c in r["checks"]) else "fail"
            js = {"id": r["id"], "title": r["title"], "owner": "firmware",
                  "circuit": {"board": "front", "refs": r["refs"], "schematic_commit": SCH_COMMIT},
                  "model": r["model"], "criteria_commit": CRITERIA_COMMIT, "checks": r["checks"], "verdict": verdict,
                  "waveforms": [rel(p) for p in r["png"]], "netlist": "hardware/sim/" + r["net"], "tool": tool,
                  "notes": " | ".join(r["notes"])}
        except Exception as e:  # 실행 불가 → error
            verdict = "error"
            js = {"id": tid, "title": "", "owner": "firmware", "circuit": {"board": "front", "refs": [], "schematic_commit": SCH_COMMIT},
                  "model": {}, "criteria_commit": CRITERIA_COMMIT, "checks": [], "verdict": "error", "waveforms": [], "netlist": "",
                  "tool": tool, "notes": f"실행 불가: {type(e).__name__}: {e}"[:1500]}
        bad += verdict != "pass"
        with open(os.path.join(SIM, "results", f"{tid}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(js, f, ensure_ascii=False, indent=2)
        print(f"{tid} {verdict}: " + "; ".join(f"{c['name']}={c['value']} {c['op']} {c['limit']} {'ok' if c['pass'] else 'FAIL'}" for c in js["checks"])
              + ("" if verdict != "error" else " " + js["notes"][:400]))
    print(f"SIM-001b: fail+error {bad}건")
    return bad


if __name__ == "__main__":
    sys.exit(main())
