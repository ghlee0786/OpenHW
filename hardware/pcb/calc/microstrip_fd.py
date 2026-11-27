"""표면(마이크로스트립) 선로 임피던스 2D 정전계 유한차분 계산 (준정적, 무손실).

단면: 아래 접지면(y=0) · 유전체 h(er) · 그 위 선로(두께 t) · 선택적 솔더마스크 · 공기 · 접지 상자.
단선 Z0 = 1/(c*sqrt(C*C0)), 차동 Zdiff = 2*Zodd (홀수 모드, +1/-1 V).
C 는 정전 에너지로 구한다: 단선 W=C/2, 홀수 모드 W=Codd(선 하나당).
검증: 단선 결과를 Hammerstad-Jensen 식과 비교한다(--check).
사용: python microstrip_fd.py            # 문서 표 재현
      python microstrip_fd.py --check    # HJ 비교
"""
import math
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

C0 = 299792458.0
EPS0 = 8.8541878128e-12


def solve(w, s, h, t, er, mask_t=0.0, mask_er=3.5, diff=True, d=0.004):
    """mm 단위. diff=False 면 단선(s 무시)."""
    d = h / max(1, round(h / d))  # 유전체 윗면과 선로 아랫면이 같은 격자선에 오도록 맞춘다
    t = max(1, round(t / d)) * d
    mask_t = round(mask_t / d) * d
    span = (2 * w + s) if diff else w
    W = span + 2 * max(12 * h, 2.0)  # 옆 벽까지 여유
    H = h + t + max(10 * h, 2.0)
    nx, ny = int(round(W / d)) + 1, int(round(H / d)) + 1
    x = np.arange(nx) * d
    y = np.arange(ny) * d
    # 셀(유전율) 격자: (nx-1, ny-1), 셀 중심 기준
    xc = (x[:-1] + x[1:]) / 2
    yc = (y[:-1] + y[1:]) / 2
    XC, YC = np.meshgrid(xc, yc, indexing="ij")
    eps = np.ones_like(XC)
    eps[YC < h] = er
    if mask_t > 0:  # 기판 위와 선로 위를 마스크가 덮는다(선로 사이는 t+mask_t 까지 채움 근사)
        eps[(YC >= h) & (YC < h + t + mask_t)] = mask_er
    # 도체 노드
    X, Y = np.meshgrid(x, y, indexing="ij")
    x0 = (W - span) / 2
    on_y = (Y >= h - 1e-9) & (Y <= h + t + 1e-9)
    if diff:
        c1 = on_y & (X >= x0 - 1e-9) & (X <= x0 + w + 1e-9)
        c2 = on_y & (X >= x0 + w + s - 1e-9) & (X <= x0 + 2 * w + s + 1e-9)
    else:
        c1 = on_y & (X >= x0 - 1e-9) & (X <= x0 + w + 1e-9)
        c2 = np.zeros_like(c1)
    fixed = np.zeros((nx, ny), bool)
    fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
    fixed |= c1 | c2
    V = np.zeros((nx, ny))
    V[c1] = 1.0
    V[c2] = -1.0

    def energy(epsgrid):
        # 링크 계수 = 링크에 닿은 두 셀 유전율 평균 (가장자리는 한 셀)
        ep = np.pad(epsgrid, 1, mode="edge")  # (nx+1, ny+1)
        kx = (ep[1:-1, :-1] + ep[1:-1, 1:]) / 2  # 수평 링크 (nx-1, ny)
        ky = (ep[:-1, 1:-1] + ep[1:, 1:-1]) / 2  # 수직 링크 (nx, ny-1)
        n = nx * ny
        idx = np.arange(n).reshape(nx, ny)
        rows, cols, vals = [], [], []
        diag = np.zeros(n)
        for (a, b, k) in (
            (idx[:-1, :], idx[1:, :], kx),
            (idx[:, :-1], idx[:, 1:], ky),
        ):
            a, b, k = a.ravel(), b.ravel(), k.ravel()
            rows += [a, b]
            cols += [b, a]
            vals += [-k, -k]
            np.add.at(diag, a, k)
            np.add.at(diag, b, k)
        L = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
        L = L + sp.diags(diag)
        f = fixed.ravel()
        free = ~f
        Vf = V.ravel().copy()
        rhs = -L[free][:, f] @ Vf[f]
        Vf[free] = spla.spsolve(L[free][:, free].tocsc(), rhs)
        Vg = Vf.reshape(nx, ny)
        Wx = (kx * (Vg[1:, :] - Vg[:-1, :]) ** 2).sum()
        Wy = (ky * (Vg[:, 1:] - Vg[:, :-1]) ** 2).sum()
        return 0.5 * EPS0 * (Wx + Wy)  # J/m (d 는 2D 에서 상쇄)

    We = energy(eps)
    Wa = energy(np.ones_like(eps))
    if diff:
        C, Ca = We, Wa  # 홀수 모드, 선 하나당
    else:
        C, Ca = 2 * We, 2 * Wa
    Z = 1.0 / (C0 * math.sqrt(C * Ca))
    eeff = C / Ca
    return (2 * Z if diff else Z), eeff


def hj_single(w, h, t, er):
    """Hammerstad-Jensen + 두께 보정(Wheeler)."""
    u = w / h
    if t > 0:
        du1 = t / (math.pi * h) * math.log(1 + 4 * math.e / ((t / h) * (1 / math.tanh(math.sqrt(6.517 * u))) ** 2))
        dur = 0.5 * (1 + 1 / math.cosh(math.sqrt(er - 1))) * du1
        u1, ur = u + du1, u + dur
    else:
        u1 = ur = u

    def z01(uu):
        f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / uu) ** 0.7528))
        return 60 * math.log(f / uu + math.sqrt(1 + (2 / uu) ** 2))

    def ee(uu):
        a = 1 + math.log((uu**4 + (uu / 52) ** 2) / (uu**4 + 0.432)) / 49 + math.log(1 + (uu / 18.1) ** 3) / 18.7
        b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
        return (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / uu) ** (-a * b)

    e = ee(ur) * (z01(u1) / z01(ur)) ** 2
    return z01(ur) / math.sqrt(ee(ur)), e


# PCBWay 현행 4층 1.6mm 1oz/1oz 표준 적층 (multi-layer-laminated-structure.html)
H_NOM = 0.1855  # L1-L2 7628 적층 후 두께 (잔동률 70%)
H_MIN = 0.1715  # 잔동률 30%
ER = 4.74       # 7628 RC46%
T = 0.035       # 외층 완성 1oz


def main():
    if "--check" in sys.argv:
        for w in (0.20, 0.30, 0.35):
            zf, ef = solve(w, 0, H_NOM, T, ER, diff=False)
            zh, eh = hj_single(w, H_NOM, T, ER)
            print(f"단선 w={w:.3f}  FD {zf:6.2f}Ω (eeff {ef:.3f})  HJ {zh:6.2f}Ω (eeff {eh:.3f})  차 {100*(zf-zh)/zh:+.1f}%")
        return
    print("== 단선 50Ω (참고) ==")
    for w in (0.30, 0.32, 0.34):
        z, _ = solve(w, 0, H_NOM, T, ER, diff=False)
        print(f"w={w:.3f}  Z0={z:6.2f}")
    print("== 차동 (마스크 없음, h=%.4f er=%.2f t=%.3f) ==" % (H_NOM, ER, T))
    cases = [(0.14, 0.16), (0.15, 0.16), (0.17, 0.20), (0.18, 0.16), (0.20, 0.16), (0.22, 0.20), (0.25, 0.20)]
    for w, s in cases:
        z, _ = solve(w, s, H_NOM, T, ER)
        zm, _ = solve(w, s, H_NOM, T, ER, mask_t=0.015)
        print(f"w={w:.3f} s={s:.3f}  Zdiff={z:6.2f}  마스크0.015/3.5={zm:6.2f}")
    print("== 민감도: 선정안 ==")
    for name, w, s in (("100Ω안", 0.15, 0.16), ("90Ω안", 0.20, 0.16)):
        for lbl, h, er, mt in (("공칭", H_NOM, ER, 0), ("h=0.1715", H_MIN, ER, 0), ("er=4.4", H_NOM, 4.4, 0),
                               ("마스크 0.015/3.5", H_NOM, ER, 0.015)):
            z, _ = solve(w, s, h, T, er, mask_t=mt)
            print(f"{name} w={w:.3f} s={s:.3f} {lbl:16s} Zdiff={z:6.2f}")


if __name__ == "__main__":
    main()
