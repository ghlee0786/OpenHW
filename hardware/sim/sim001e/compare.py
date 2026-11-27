#!/usr/bin/env python3
"""SIM-001e L3 끔 구간 잔류 개선 — 후보 비교 (기준 hardware/sim/SIM-001e-criteria.md, a3529ae).

사용: python hardware/sim/sim001e/compare.py [후보 ID ...]   (없으면 base + 전 후보)
출력: hardware/sim/sim001e/compare.json, 표준 출력 표. 종료 코드 = 0 (고른 후보 있음) / 1 (없음 → 불합격 유지)
모델: hardware/sim/sim001b/run.py 와 같다 (AL8860 동작 모델, VSMA·SS24 맞춤, LED CJO 200 pF 가정).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "sim001b"))
import run as r  # noqa: E402

CTRL = ("Vpw pw0 0 PULSE(1.71 0 1.875m 1u 1u 0.625m 2.5m)\nRpw pw0 irpwm 93.75\nR12 core irpwm 100k\nVcore core 0 1.8\n"
        "M5 ctrl irpwm 0 0 nq7\n.model nq7 nmos level=1 vto=1.0 kp=1.79\nCg5 irpwm 0 61p\n")


def cand(cid):
    """후보 → 스트링마다 넣을 소자 줄 (k = A/B). 값은 기준 문서 ②와 같다."""
    t = {
        "base": "",
        "a1": "Cpx{k} set{k} k{k} 10n\n",
        "a2": "Cpx{k} set{k} k{k} 100n\n",
        "a3": "Rpx{k} set{k} np{k} 330\nCpx{k} np{k} k{k} 10n\n",
        "b1": "Rsn{k} sw{k} ns{k} 330\nCsn{k} ns{k} 0 1n\n",
        "b2": "Rsn{k} sw{k} ns{k} 100\nCsn{k} ns{k} 0 2.2n\n",
        "b3": "Rln{k} k{k} nl{k} 330\nCln{k} nl{k} sw{k} 1n\n",
        "c1": "Rbl{k} set{k} k{k} 10k\n",
        "c2": "Rbl{k} set{k} k{k} 4.7k\n",
    }[cid]
    return t


PARTS = {"base": 0, "a1": 1, "a2": 1, "a3": 2, "b1": 2, "b2": 2, "b3": 2, "c1": 1, "c2": 1}


def body(corner, strings, cid, ctrl="open"):
    b = r.ir_body(corner, strings, ctrl)
    for k in strings:
        b = b.replace(f"D{k}1 set{k} m{k} led", f"Vd{k} set{k} sd{k} 0\nD{k}1 sd{k} m{k} led")   # LED 다이오드 전류 측정
        b += cand(cid).format(k=k)
    return b


def run_one(cid):
    out = {}
    rs = {c: r.CORNERS[c][1] for c in r.CORNERS}
    # N1·N2·N3: 한 스트링 100 % (L1 모서리)
    l1 = {}
    for c in ("typ", "imin", "imax", "fmax", "dmax", "dmin"):
        d, h = r.run_tran(body(c, ("A",), cid), ["i(VdA)", "(v(v12)-v(setA))/%g" % rs[c], "i(VilA)", "v(XA.g)", "v(sdA)-v(kA)", "v(v12)", "i(Vin)"],
                          "0.6m", "5n", "20n")
        t = d["time"]
        ild, irs, il, g, vled, v12, iin = (r.col(d, h, k) for k in range(1, 8))
        t0 = 0.4e-3
        m = t >= t0
        f, ton, duty = r.fsw_stats(t, g, t0)
        pin = r.win_mean(t, v12 * (-iin), t0, t[-1])
        pled = r.win_mean(t, vled * ild, t0, t[-1])
        l1[c] = dict(mean=r.win_mean(t, ild, t0, t[-1]), pk=float(ild[m].max()), ilpk=float(il[m].max()),
                     ripple=float(ild[m].max() - ild[m].min()), f=f, ton=ton, duty=duty, eta=pled / pin)
    out["l1"] = l1
    # N6: A+B 100 % 입력 평균
    d, h = r.run_tran(body("worst_in", ("A", "B"), cid), ["i(Vin)", "i(VdA)", "i(VdB)"], "0.6m", "5n", "20n")
    t = d["time"]
    out["in_mean"] = r.win_mean(t, -r.col(d, h, 1), 0.4e-3, t[-1])
    out["cont_led"] = r.win_mean(t, r.col(d, h, 2) + r.col(d, h, 3), 0.4e-3, t[-1])
    out["cont_rs"] = None
    # G1·G2·N4·N5: PWM 25 % A+B
    d, h = r.run_tran(body("worst_in", ("A", "B"), cid, CTRL),
                      ["i(Vin)", "(v(v12)-v(setA))/0.099", "(v(v12)-v(setB))/0.099", "i(VdA)", "i(VdB)"], "7.5m", "10n", "50n")
    t = d["time"]
    if t[-1] < 7.4e-3:
        raise RuntimeError(f"PWM 시뮬레이션 중단 t={t[-1] * 1e3:.3f} ms (ngspice timestep too small)")
    iin = -r.col(d, h, 1)
    irs = r.col(d, h, 2) + r.col(d, h, 3)
    ild = r.col(d, h, 4) + r.col(d, h, 5)
    off = (t > 2.6e-3) & (t < 4.375e-3)
    out["g1_off_rs_max"] = float(np.abs(irs[off]).max())
    m = off
    tt = t[m]
    out["g2_off_led_fwd_mean"] = float(np.trapezoid(np.clip(ild[m], 0, None), tt) / (tt[-1] - tt[0]))
    out["n5_mov"] = r.moving_max(t, iin, 20e-6, 1.0e-3)
    out["pwm_avg_led"] = r.win_mean(t, ild, 2.5e-3, 7.5e-3)
    out["pwm_avg_rs"] = r.win_mean(t, irs, 2.5e-3, 7.5e-3)
    out["ratio_led"] = out["pwm_avg_led"] / out["cont_led"]
    # Rs 기준 비율의 분모: 같은 모서리 연속 Rs 평균
    d2, h2 = r.run_tran(body("worst_in", ("A", "B"), cid), ["(v(v12)-v(setA))/0.099", "(v(v12)-v(setB))/0.099"], "0.6m", "5n", "20n")
    out["cont_rs"] = r.win_mean(d2["time"], r.col(d2, h2, 1) + r.col(d2, h2, 2), 0.4e-3, d2["time"][-1])
    out["ratio_rs"] = out["pwm_avg_rs"] / out["cont_rs"]
    return out


def judge(c, b):
    """기준 ③: G1·G2 + N1~N6. b = 기존 회로 결과."""
    res = {}
    res["G1 끔 |I_Rs| ≤ 1 mA"] = c["g1_off_rs_max"] <= 1e-3
    res["G2 순방향 평균 ≤ 기존"] = c["g2_off_led_fwd_mean"] <= b["g2_off_led_fwd_mean"] * 1.001
    res["N1 η ≥ 기존 − 0.1%p"] = c["l1"]["typ"]["eta"] >= b["l1"]["typ"]["eta"] - 0.001
    ok2 = c["l1"]["imin"]["mean"] >= 0.90 and c["l1"]["imax"]["mean"] <= 1.10
    for cc in ("imin", "imax"):
        ok2 = ok2 and abs(c["l1"][cc]["mean"] / b["l1"][cc]["mean"] - 1) <= 0.001
    res["N2 LED 평균 한계 안·변화 ≤ 0.1%"] = ok2
    l1 = c["l1"]
    res["N3 L1 항목 한계 안"] = (l1["imax"]["pk"] <= 1.5 and max(v["ilpk"] for v in l1.values()) <= 1.6 and max(v["f"] for v in l1.values()) <= 1e6
                             and min(v["ton"] for v in l1.values()) >= 500e-9 and all(0.25 <= v["duty"] <= 0.75 for v in l1.values())
                             and l1["typ"]["ripple"] / l1["typ"]["mean"] <= 0.5)
    res["N4 켬 비율 ≤0.255·≥기존−0.005 (LED·Rs 둘 다)"] = all(c[k] <= 0.255 and c[k] >= b[k] - 0.005 for k in ("ratio_led", "ratio_rs"))
    res["N5 20µs 창 ≤1.86·≤기존×1.001"] = c["n5_mov"] <= 1.86 and c["n5_mov"] <= b["n5_mov"] * 1.001
    res["N6 L2 평균 ≤ 기존×1.001"] = c["in_mean"] <= b["in_mean"] * 1.001
    return res


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ids = sys.argv[1:] or ["base", "a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2"]
    if "base" not in ids:
        ids = ["base"] + ids
    res, err = {}, {}
    for i in ids:
        try:
            res[i] = run_one(i)
        except Exception as e:  # 실행 불가 후보 → 탈락으로 기록
            err[i] = f"{type(e).__name__}: {e}"[:300]
            print(f"{i:5s} 실행 불가 — {err[i]}")
    ids = [i for i in ids if i in res]
    b = res["base"]
    table, ok = [], []
    for i in ids:
        j = judge(res[i], b) if i != "base" else {}
        res[i]["judge"] = j
        allok = i != "base" and all(j.values())
        if allok:
            ok.append(i)
        c = res[i]
        table.append(f"{i:5s} 끔|I_Rs| {c['g1_off_rs_max'] * 1e3:7.3f} mA · 순방향 {c['g2_off_led_fwd_mean'] * 1e6:8.2f} µA · η {c['l1']['typ']['eta'] * 100:6.2f}% · "
                     f"I_LED imin {c['l1']['imin']['mean']:.4f} imax {c['l1']['imax']['mean']:.4f} · 비율 LED {c['ratio_led']:.4f} Rs {c['ratio_rs']:.4f} · "
                     f"20µs {c['n5_mov']:.4f} · L2 {c['in_mean']:.4f} A" + ("" if i == "base" else "  → " + ("합격" if allok else "탈락: " + ", ".join(k.split()[0] for k, v in j.items() if not v))))
    print("\n".join(table))
    pick = sorted(ok, key=lambda i: (PARTS[i], b["l1"]["typ"]["eta"] - res[i]["l1"]["typ"]["eta"]))[:1]
    print("고른 후보:", pick[0] if pick else "없음 → 불합격 기록·근거 유지")
    for v in res.values():
        for c in v["l1"].values():
            for k in list(c):
                c[k] = float(c[k])
    with open(os.path.join(HERE, "compare.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"criteria_commit": "a3529ae", "schematic_commit": "a2d878c", "pick": pick[0] if pick else None, "errors": err, "results": res}, f, ensure_ascii=False, indent=1)
    return 0 if pick else 1


if __name__ == "__main__":
    sys.exit(main())
