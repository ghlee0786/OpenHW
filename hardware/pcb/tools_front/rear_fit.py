"""캐리어 뒷면(RJ45·microSD·USB-C·DC 잭) 배치 가능성 판정 (P-003 layout-plan.md §3.1).

courtyard 크기는 KiCad 10 표준 라이브러리 값(fpsize 조회, layout-plan.md §2)이다. 좌표는 M-001 O 기준, +Y 위.
판정 1a: 40×40에서 RJ45·microSD·USB-C를 손으로 정한 한 배치로 고정하면 DC 잭 자리가 있는지(없음 = 손 배치 실패).
판정 1b: 40×40에서 네 커넥터를 네 변·두 방향·0.5mm 격자로 전수 탐색(관통 부품은 윗면 짝 BTB 자리 회피) — 들어가는 배치와 여유.
판정 2: 차선 외형(캐리어만 −Y로 14mm 연장, y −34…+20)의 제안 좌표가 서로·구멍 금지 원과 겹치지 않는지.
종료 코드 0 = 1a 없음 · 1b 들어감 · 2 겹침 없음(계획서 §3.1 주장과 같음), 1 = 다름.
"""
import sys

HOLES = [(13, 13), (13, -13), (-13, 13), (-17, -17)]
HOLE_R = 2.0  # 구리·부품 금지 Ø4.0
JACK = (16.09, 11.59)  # BarrelJack_Horizontal courtyard (긴 변 = 삽입 방향)


def rect(cx, cy, w, h):
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def hits_hole(r):
    for hx, hy in HOLES:
        nx, ny = min(max(hx, r[0]), r[2]), min(max(hy, r[1]), r[3])
        if (nx - hx) ** 2 + (ny - hy) ** 2 < HOLE_R ** 2:
            return True
    return False


def inside(r, box, overhang=0.5):
    # 가장자리 커넥터는 외곽 밖으로 0.5mm까지 튀어나오는 것을 허용
    return r[0] >= box[0] - overhang and r[1] >= box[1] - overhang and r[2] <= box[2] + overhang and r[3] <= box[3] + overhang


def fixed40():
    return {
        "J5 RJ45": (-9.55, -20.0, 9.55, 2.39),
        "J4 microSD": (-7.9, 2.4, 7.9, 20.19),
        "J3 USB-C": (-20.0, -5.37, -10.49, 5.37),
    }


def search_jack(box, fixed):
    found = []
    for w, h in (JACK, JACK[::-1]):
        y = box[1] - 0.5
        while y + h <= box[3] + 0.5:
            x = box[0] - 0.5
            while x + w <= box[2] + 0.5:
                r = (x, y, x + w, y + h)
                if not hits_hole(r) and not any(overlap(r, f) for f in fixed.values()):
                    found.append(r)
                x += 0.1
            y += 0.1
    return found


# (폭, 깊이). 깊이 = 삽입 방향 = 패드 무게중심 반대쪽이 입구 (KiCad 풋프린트 패드 중심 vs courtyard 중심으로 확인)
PARTS = {"J5 RJ45": (19.09, 22.39), "J2 DC jack": (11.59, 16.09), "J4 microSD": (15.79, 17.79), "J3 USB-C": (10.73, 9.51)}
THT = {"J5 RJ45", "J2 DC jack", "J3 USB-C"}  # 핀이 윗면까지 관통
TOP_BTB = (9.2 - 0.5, -8.85 - 0.5, 14.4 + 0.5, 8.85 + 0.5)  # 캐리어 윗면 짝 플러그 A 몸체 + 0.5


def edge_options(box, w, d, step=0.5):
    """입구가 바깥을 보도록 변에 붙인(외곽 0.5mm 돌출 허용) 모든 자리. 깊이 d는 변과 직각. 구멍 금지 원과 겹치면 뺀다."""
    out = []
    xs = [box[0] - 0.5 + i * step for i in range(int((box[2] - box[0] + 1 - w) / step) + 1)]
    for x in xs:  # ±Y 변: 폭은 X, 깊이는 Y
        out += [(x, box[1] - 0.5, x + w, box[1] - 0.5 + d), (x, box[3] + 0.5 - d, x + w, box[3] + 0.5)]
    ys = [box[1] - 0.5 + i * step for i in range(int((box[3] - box[1] + 1 - w) / step) + 1)]
    for y in ys:  # ±X 변: 깊이는 X, 폭은 Y
        out += [(box[0] - 0.5, y, box[0] - 0.5 + d, y + w), (box[2] + 0.5 - d, y, box[2] + 0.5, y + w)]
    return [r for r in out if not hits_hole(r)]


def exhaustive(box):
    opts = [[r for r in edge_options(box, *PARTS[k]) if not (k in THT and overlap(r, TOP_BTB))] for k in PARTS]
    chosen = []

    def rec(i):
        if i == len(opts):
            return True
        for r in opts[i]:
            if not any(overlap(r, c) for c in chosen):
                chosen.append(r)
                if rec(i + 1):
                    return True
                chosen.pop()
        return False

    return rec(0), chosen


def main():
    ok = True
    box40 = (-20, -20, 20, 20)
    f = fixed40()
    bad = [k for k, r in f.items() if hits_hole(r) or not inside(r, box40)]
    spots = search_jack(box40, f)
    print(f"판정 1a (40×40, RJ45·microSD·USB-C 한 배치 고정): DC 잭 자리 {len(spots)}곳 (고정 3개 구멍·외곽 {'통과' if not bad else bad})")
    fit, sol = exhaustive(box40)
    print(f"판정 1b (40×40, 네 커넥터 × 네 변 × 입구 바깥, 0.5mm 격자 전수, 관통 부품은 윗면 BTB 자리 회피): {'들어감 ' + str(sol) if fit else '들어가는 배치 없음'}")
    ok &= not bad and len(spots) == 0 and not fit
    # 판정 3: 같은 전수 탐색으로 −Y 한쪽 연장의 최소 길이(1mm 단위)와 K3 차선 45×45(구멍은 그대로)
    ext_min = None
    for e in range(1, 21):
        if exhaustive((-20, -20 - e, 20, 20))[0]:
            ext_min = e
            break
    k45 = exhaustive((-22.5, -22.5, 22.5, 22.5))[0]
    print(f"판정 3: −Y 연장 최소 {ext_min} mm (1mm 단위, 전수) · 45×45 {'들어감' if k45 else '들어가지 않음'}")

    box_ext = (-20, -34, 20, 20)
    prop = {
        "J5 RJ45": (-12.0, -34.0, 7.09, -11.61),
        "J2 DC jack": (8.41, -34.0, 20.0, -17.91),
        "J4 microSD": (-7.9, 2.4, 7.9, 20.19),
        "J3 USB-C": (-20.0, -5.37, -10.49, 5.37),
    }
    probs = []
    names = list(prop)
    for i, a in enumerate(names):
        if hits_hole(prop[a]) or not inside(prop[a], box_ext) or (a in THT and overlap(prop[a], TOP_BTB)):
            probs.append(a)
        for b in names[i + 1:]:
            if overlap(prop[a], prop[b]):
                probs.append(f"{a}×{b}")
    print("판정 2 (40×54 제안):", "겹침 없음" if not probs else f"겹침 {probs}")
    ok &= not probs
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
