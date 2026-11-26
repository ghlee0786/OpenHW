"""M-003c 가공 도면 (CAD 독립, params.py 기준): PMMA 창 4장, 흑색 폼 2종, Tflex P340 재단 4장, 바깥 방열판 AL_HEATSINK_PX.
출력: fab/*.dxf (R12, 단위 mm, 레이어 CUT = 외곽, HOLE = 구멍, REF = 참고선) + fab/m003-fab-drawings.pdf·png
실행: python -I -B mechanical/m003/fab_drawings.py"""
import math, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
g = {}
exec(open(os.path.join(HERE, 'params.py'), encoding='utf-8').read(), g)
d = g['derive'](g['P'])
OUT = os.path.join(HERE, 'fab')
os.makedirs(OUT, exist_ok=True)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# ---------------- DXF R12 최소 작성기 ----------------
class DXF:
    def __init__(self):
        self.e = []

    def line(self, a, b, layer='CUT'):
        self.e.append('0\nLINE\n8\n%s\n10\n%.4f\n20\n%.4f\n30\n0.0\n11\n%.4f\n21\n%.4f\n31\n0.0\n' % (layer, a[0], a[1], b[0], b[1]))

    def circle(self, c, r, layer='CUT'):
        self.e.append('0\nCIRCLE\n8\n%s\n10\n%.4f\n20\n%.4f\n30\n0.0\n40\n%.4f\n' % (layer, c[0], c[1], r))

    def arc(self, c, r, a0, a1, layer='CUT'):
        self.e.append('0\nARC\n8\n%s\n10\n%.4f\n20\n%.4f\n30\n0.0\n40\n%.4f\n50\n%.4f\n51\n%.4f\n' % (layer, c[0], c[1], r, a0, a1))

    def poly(self, pts, layer='CUT'):
        for a, b in zip(pts, pts[1:] + pts[:1]):
            self.line(a, b, layer)

    def rrect(self, x0, y0, x1, y1, r, layer='CUT'):
        if r <= 0:
            return self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer)
        self.line((x0 + r, y0), (x1 - r, y0), layer); self.line((x1, y0 + r), (x1, y1 - r), layer)
        self.line((x1 - r, y1), (x0 + r, y1), layer); self.line((x0, y1 - r), (x0, y0 + r), layer)
        self.arc((x1 - r, y0 + r), r, 270, 360, layer); self.arc((x1 - r, y1 - r), r, 0, 90, layer)
        self.arc((x0 + r, y1 - r), r, 90, 180, layer); self.arc((x0 + r, y0 + r), r, 180, 270, layer)

    def rpoly(self, pts, r, layer='CUT'):
        """축 정렬 반시계 다각형, 볼록 모서리만 R (오목은 직각)."""
        for a, b in rpoly_segs(pts, r):
            if a == 'arc':
                self.arc(*b, layer=layer)
            else:
                self.line(a, b, layer)

    def save(self, name):
        hdr = '0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n'
        open(os.path.join(OUT, name), 'w', encoding='ascii').write(hdr + ''.join(self.e) + '0\nENDSEC\n0\nEOF\n')


def rpoly_segs(pts, r):
    n = len(pts); segs = []; ends = []
    for i in range(n):
        p0, v, p1 = pts[i - 1], pts[i], pts[(i + 1) % n]
        ui = ((v[0] - p0[0]) / max(abs(v[0] - p0[0]) + abs(v[1] - p0[1]), 1e-9), (v[1] - p0[1]) / max(abs(v[0] - p0[0]) + abs(v[1] - p0[1]), 1e-9))
        uo = ((p1[0] - v[0]) / max(abs(p1[0] - v[0]) + abs(p1[1] - v[1]), 1e-9), (p1[1] - v[1]) / max(abs(p1[0] - v[0]) + abs(p1[1] - v[1]), 1e-9))
        convex = ui[0] * uo[1] - ui[1] * uo[0] > 0
        if convex and r > 0:
            a = (v[0] - r * ui[0], v[1] - r * ui[1]); b = (v[0] + r * uo[0], v[1] + r * uo[1]); c = (a[0] + r * uo[0], a[1] + r * uo[1])
            segs.append(('arc', (c, r, math.degrees(math.atan2(a[1] - c[1], a[0] - c[0])) % 360, math.degrees(math.atan2(b[1] - c[1], b[0] - c[0])) % 360)))
            ends.append((a, b))
        else:
            ends.append((v, v))
    for i in range(n):
        segs.append((ends[i][1], ends[(i + 1) % n][0]))
    return segs


def draw_rpoly(ax, pts, r, **kw):
    for a, b in rpoly_segs(pts, r):
        if a == 'arc':
            (cx, cy), rr, a0, a1 = b
            a1 = a1 if a1 > a0 else a1 + 360
            ts = [math.radians(a0 + (a1 - a0) * k / 8) for k in range(9)]
            ax.plot([cx + rr * math.cos(t) for t in ts], [cy + rr * math.sin(t) for t in ts], 'k', lw=1.0)
        else:
            ax.plot([a[0], b[0]], [a[1], b[1]], 'k', lw=1.0)


def draw_rrect(ax, x0, y0, x1, y1, r, **kw):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x0 + r, y0 + r), x1 - x0 - 2 * r, y1 - y0 - 2 * r, boxstyle='round,pad=%.3f' % r, fill=False, lw=1.0, **kw))


def dim(ax, a, b, at, horiz=True, txt=None, fs=6):
    if horiz:
        ax.annotate('', (a, at), (b, at), arrowprops=dict(arrowstyle='<->', lw=0.5))
        ax.text((a + b) / 2, at + 0.4, txt or '%.2f' % abs(b - a), ha='center', va='bottom', fontsize=fs)
    else:
        ax.annotate('', (at, a), (at, b), arrowprops=dict(arrowstyle='<->', lw=0.5))
        ax.text(at - 0.4, (a + b) / 2, txt or '%.2f' % abs(b - a), ha='right', va='center', fontsize=fs, rotation=90)


def frame(ax, title):
    ax.set_aspect('equal'); ax.set_title(title, fontsize=8); ax.tick_params(labelsize=5); ax.grid(True, lw=0.2, alpha=0.4)


ry, xi0, xi1, wr = d['rib_y'], d['x_in_min'], d['x_in_max'], d['win_r']
(ax0, ax1), (ay0, ay1) = d['als_in']
ITEMS = []   # (파일, 그리기 함수, 제목, 노트)

# ---- PMMA 창 (부품표 5–8) ----
W = {
    'WIN_LENS': ('circle', d['lens_win_d'], d['win_t']),
    'WIN_A': ('rrect', (xi1 - xi0) - 2 * d['win_clr'], (d['y_in_hi'] + 1.0 - ry) - 2 * d['win_clr'], d['win_t']),
    'WIN_B': ('rrect', (xi1 - xi0) - 2 * d['win_clr'], (-ry - d['b_pocket_y0']) - 2 * d['win_clr'], d['win_t']),
    'WIN_ALS': ('rrect', (ax1 - ax0 + 2.2) - 2 * d['win_clr'], (ay1 - ay0 + 2.7) - 2 * d['win_clr'], 1.5),
}
if d.get('b_ext'):   # M-007 J5 V4: T자 B 창 (기구 좌표 → 창 왼쪽 아래 원점)
    k_, ex0, ex1, ey0, yb = d['win_clr'], *d['b_ext'], d['b_pocket_y0']
    mx0, mx1, my0, my1, tx0, tx1, ty0 = xi0 + k_, xi1 - k_, yb + k_, -ry - k_, ex0 + k_, ex1 - k_, ey0 + k_
    T = [(tx0, ty0), (tx1, ty0), (tx1, my0), (mx1, my0), (mx1, my1), (mx0, my1), (mx0, my0), (tx0, my0)]
    T = [(round(x - mx0, 4), round(y - ty0, 4)) for x, y in T]
    W['WIN_B'] = ('tee', mx1 - mx0, my1 - ty0, T, d['win_t'])
for name, spec in W.items():
    dx = DXF()
    if spec[0] == 'circle':
        dx.circle((0, 0), spec[1] / 2)
    elif spec[0] == 'tee':
        dx.rpoly(spec[3], wr)
    else:
        dx.rrect(0, 0, spec[1], spec[2], wr)
    dx.save('PMMA_%s_t%.1f.dxf' % (name, spec[-1]))
# ---- 폼 (9, 10) ----
fi, fo, ft = d['lens_foam']
dx = DXF(); dx.circle((0, 0), fo); dx.circle((0, 0), fi, 'HOLE'); dx.save('FOAM_LENS_RING_t%.1f.dxf' % ft)
gw, gh = ax1 - ax0 + 2 * d['als_wall'], ay1 - ay0 + 2 * d['als_wall']
dx = DXF(); dx.poly([(0, 0), (gw, 0), (gw, gh), (0, gh)]); dx.poly([(1, 1), (gw - 1, 1), (gw - 1, gh - 1), (1, gh - 1)], 'HOLE'); dx.save('FOAM_ALS_GASKET_t%.1f.dxf' % d['als_gasket_t'])
# ---- P340 패드 (11, 12) ----
(nx0, nx1), (ny0, ny1) = d['b2_notch']
PADS = {}
for i, ((px0, px1), (py0, py1)) in enumerate(d['ins_pads']):
    nm = ['P340_PAD_A', 'P340_PAD_B1', 'P340_PAD_B2'][i]
    pts = [(px0, py0), (px1, py0), (px1, py1), (px0, py1)]
    if nm == 'P340_PAD_B2':   # 스탠드오프 (13,−13) 자리 따냄
        pts = [(px0, py0), (px1, py0), (px1, ny0), (nx0, ny0), (nx0, py1), (px0, py1)]
    pts = [(x - px0, y - py0) for x, y in pts]
    PADS[nm] = pts
    dx = DXF(); dx.poly(pts); dx.save('%s_t1.0.dxf' % nm)
(fx0, fx1), (fy0, fy1), (fz0, fz1) = d['flange']
side = (fy1 - fy0, (d['core_t'] + d['spr_gap'] + d['spr_t']) - fz0)
PADS['P340_SIDE'] = [(0, 0), (side[0], 0), (side[0], side[1]), (0, side[1])]
dx = DXF(); dx.poly(PADS['P340_SIDE']); dx.save('P340_SIDE_t1.0.dxf')
# ---- 방열판 (3) ----
(hb0, hb1), (hy0, hy1), (hz0, hz1) = d['x_hs_base'], d['hs_y'], d['hs_z']
c = d['hs_ped_clr']
ped_y = (d['al_win_y'][0] + c, d['al_win_y'][1] - c)
ped_z = (d['al_win_z'][0] + c, d['al_win_z'][1] - c)
# 바닥판 정면 (+X 에서 봄: 가로 y, 세로 z) — 외곽·구멍·받침대(참고)
dx = DXF()
dx.poly([(hy0, hz0), (hy1, hz0), (hy1, hz1), (hy0, hz1)])
for (y, z) in d['al_holes'] + d['hs_ped_screws']:
    dx.circle((y, z), 1.025, 'HOLE')   # M2.5 탭 밑구멍 Ø2.05 (바닥 관통, 핀 사이)
dx.poly([(ped_y[0], ped_z[0]), (ped_y[1], ped_z[0]), (ped_y[1], ped_z[1]), (ped_y[0], ped_z[1])], 'REF')
for zc_ in d['hs_fin_zc']:
    dx.line((hy0, zc_ - d['hs_t'] / 2), (hy1, zc_ - d['hs_t'] / 2), 'REF'); dx.line((hy0, zc_ + d['hs_t'] / 2), (hy1, zc_ + d['hs_t'] / 2), 'REF')
dx.save('HS_EXTRUSION_SK444_base_face_YZ.dxf')
# 받침대 판 (가로 y, 세로 z) — 접시 구멍 2
dx = DXF()
dx.poly([(ped_y[0], ped_z[0]), (ped_y[1], ped_z[0]), (ped_y[1], ped_z[1]), (ped_y[0], ped_z[1])])
for (y, z) in d['hs_ped_screws']:
    dx.circle((y, z), 1.4, 'HOLE'); dx.circle((y, z), 2.45, 'REF')
dx.save('HS_PEDESTAL_plate_YZ.dxf')
# 핀 단면 (Y 방향으로 본 압출 단면: 가로 x, 세로 z) — 받침대 + 바닥판 + 핀
dx = DXF()
prof = [(d['x_al_in'], ped_z[0]), (hb0, ped_z[0]), (hb0, hz0), (hb1, hz0)]
for zc_ in d['hs_fin_zc']:
    z0, z1 = zc_ - d['hs_t'] / 2, zc_ + d['hs_t'] / 2
    if z0 > hz0 + 1e-6:
        prof.append((hb1, z0))
    else:
        prof[-1] = (hb1, hz0)
    prof += [(d['x_hs_tip'], max(z0, hz0)), (d['x_hs_tip'], min(z1, hz1))]
    if z1 < hz1 - 1e-6:
        prof.append((hb1, z1))
prof += [(hb1, hz1), (hb0, hz1), (hb0, ped_z[1]), (d['x_al_in'], ped_z[1])]
dx.poly(prof)
dx.save('HS_EXTRUSION_SK444_fin_section_XZ.dxf')

# ---------------- PDF ----------------
pdf = PdfPages(os.path.join(OUT, 'm003-fab-drawings.pdf'))
# 1쪽: 창·폼·패드
fig, axs = plt.subplots(3, 4, figsize=(16.5, 11.7))
k = 0
for name, spec in W.items():
    ax = axs.flat[k]; k += 1
    if spec[0] == 'circle':
        ax.add_patch(plt.Circle((0, 0), spec[1] / 2, fill=False, lw=1))
        dim(ax, -spec[1] / 2, spec[1] / 2, -spec[1] / 2 - 2, txt='Ø%.2f' % spec[1])
        ax.set_xlim(-14, 14); ax.set_ylim(-15, 13)
    else:
        if spec[0] == 'tee':
            draw_rpoly(ax, spec[3], wr)
            tp = spec[3]; dim(ax, tp[0][0], tp[1][0], -1.0, txt='탭 %.2f' % (tp[1][0] - tp[0][0])); dim(ax, tp[0][1], tp[2][1], tp[0][0] - 1.5, txt='탭 %.2f' % (tp[2][1] - tp[0][1]), horiz=False)
        else:
            draw_rrect(ax, 0, 0, spec[1], spec[2], wr, ec='k')
        dim(ax, 0, spec[1], -2.5); dim(ax, 0, spec[2], -2, horiz=False)
        ax.set_xlim(-6, spec[1] + 4); ax.set_ylim(-6, spec[2] + 4)
    frame(ax, 'PMMA %s — t%.1f 투명, 모서리 R%.1f' % (name, spec[-1], wr if spec[0] != 'circle' else 0))
    ax.text(0.02, 0.02, '레이저 컷 · 양면 보호지 유지(조립 직전 제거)\n외형 공차 ±0.25 (업체 표준) — 주머니 틈 %.2f/변 · 버·녹은 자국 없이' % d['win_clr'], transform=ax.transAxes, fontsize=5.5)
ax = axs.flat[k]; k += 1
ax.add_patch(plt.Circle((0, 0), fo, fill=False, lw=1)); ax.add_patch(plt.Circle((0, 0), fi, fill=False, lw=1, ec='#c0392b'))
dim(ax, -fo, fo, -fo - 1.5, txt='OD %.1f' % (2 * fo)); dim(ax, -fi, fi, fi + 0.6, txt='ID %.1f' % (2 * fi))
frame(ax, '흑색 폼 렌즈 링 t%.1f → 0.7 압축 (30%%)' % ft); ax.set_xlim(-12, 12); ax.set_ylim(-12, 12)
ax = axs.flat[k]; k += 1
ax.add_patch(Rectangle((0, 0), gw, gh, fill=False, lw=1)); ax.add_patch(Rectangle((1, 1), gw - 2, gh - 2, fill=False, lw=1, ec='#c0392b'))
dim(ax, 0, gw, -1.2); dim(ax, 0, gh, -1, horiz=False)
frame(ax, '흑색 폼 ALS 개스킷 t%.1f → %.1f 압축 (%.0f%%)' % (d['als_gasket_t'], d['als_gap'], 100 * (1 - d['als_gap'] / d['als_gasket_t']))); ax.set_xlim(-4, gw + 3); ax.set_ylim(-4, gh + 2)
for nm, pts in PADS.items():
    ax = axs.flat[k]; k += 1
    xs = [p[0] for p in pts] + [pts[0][0]]; ys = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs, ys, 'k-', lw=1)
    W_, H_ = max(xs), max(ys)
    dim(ax, 0, W_, -1.0); dim(ax, 0, H_, -0.8, horiz=False)
    if nm == 'P340_PAD_B2':
        ax.text(nx0 - d['ins_pads'][2][0][0] - 3, H_ + 0.4, '모서리 따냄 %.1f × %.1f (스탠드오프)' % (W_ - (nx0 - d['ins_pads'][2][0][0]), H_ - (ny0 - d['ins_pads'][2][1][0])), fontsize=5.5)
    frame(ax, 'Tflex P340 %s t1.0 → 0.75 압축 (25%%), 라이너 면 = Al 쪽' % nm.replace('P340_', ''))
    ax.set_xlim(-3, W_ + 2); ax.set_ylim(-3, H_ + 2)
while k < 12:
    axs.flat[k].axis('off'); k += 1
fig.suptitle('M-003c 가공 도면 1/2 — 창 PMMA · 흑색 폼 · Tflex P340 재단 (단위 mm, DXF: fab/*.dxf 레이어 CUT/HOLE/REF)', fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.97)); pdf.savefig(fig); fig.savefig(os.path.join(OUT, 'm003-fab-1.png'), dpi=130); plt.close(fig)
# 2쪽: 방열판
fig, axs = plt.subplots(1, 2, figsize=(16.5, 11.7))
ax = axs[0]
ax.add_patch(Rectangle((hy0, hz0), hy1 - hy0, hz1 - hz0, fill=False, lw=1.2))
ax.add_patch(Rectangle((ped_y[0], ped_z[0]), ped_y[1] - ped_y[0], ped_z[1] - ped_z[0], fill=False, lw=0.8, ls='--', ec='#2c7fb8'))
for zc_ in d['hs_fin_zc']:
    ax.plot([hy0, hy1], [zc_, zc_], c='#888', lw=0.6)
for (y, z) in d['al_holes'] + d['hs_ped_screws']:
    ax.add_patch(plt.Circle((y, z), 1.025, fill=False, ec='#c0392b', lw=1))
    ax.text(y + 1.8, z, 'M2.5 탭 (%.1f, %.2f)' % (y, z), fontsize=6)
dim(ax, hy0, hy1, hz0 - 4); dim(ax, hz0, hz1, hy0 - 4, horiz=False)
dim(ax, ped_y[0], ped_y[1], ped_z[0] + 2, txt='받침대 %.1f' % (ped_y[1] - ped_y[0])); dim(ax, ped_z[0], ped_z[1], ped_y[1] - 3, horiz=False, txt='%.1f' % (ped_z[1] - ped_z[0]))
frame(ax, '압출재 바닥 (+X 에서 봄, 가로 y / 세로 z) — 75 → %.0f 절단, M2.5 탭 6 (바닥 관통, 핀 사이): 외함 4 + 받침대 2, 파란 점선 = 받침대 판' % (hy1 - hy0))
ax.set_xlim(hy0 - 10, hy1 + 12); ax.set_ylim(hz0 - 10, hz1 + 6)
ax = axs[1]
ax.plot([p[0] for p in prof] + [prof[0][0]], [p[1] for p in prof] + [prof[0][1]], 'k-', lw=1)
dim(ax, d['x_al_in'], hb0, ped_z[0] - 3, txt='받침대 %.1f' % (hb0 - d['x_al_in']))
dim(ax, hb0, hb1, hz0 - 3, txt='바닥 %.1f' % (hb1 - hb0)); dim(ax, hb1, d['x_hs_tip'], hz0 - 3, txt='핀 %.1f' % d['hs_H'])
pitch = d['hs_fin_zc'][1] - d['hs_fin_zc'][0]
dim(ax, d['hs_fin_zc'][0], d['hs_fin_zc'][1], d['x_hs_tip'] + 3, horiz=False, txt='피치 %.2f' % pitch)
dim(ax, hz0, hz1, d['x_hs_tip'] + 8, horiz=False)
frame(ax, '핀 단면 (가로 x / 세로 z) — 핀 %d × %.1f × t%.1f, 길이(y) %.0f' % (d['hs_n'], d['hs_H'], d['hs_t'], hy1 - hy0))
ax.set_xlim(d['x_al_in'] - 6, d['x_hs_tip'] + 14); ax.set_ylim(hz0 - 8, hz1 + 4)
notes = ('① 압출재: Fischer SK 444 75 SA (흑색 아노다이즈 완제품) 1개를 %.0f mm 로 절단 (한쪽 끝, 절단면 무처리 — 줄로 버 제거). 폭·핀은 가공 없음.\n'
         '   M2.5 탭 6곳: 밑구멍 Ø2.05, 바닥 %.1f 관통 (핀 사이 간격 약 %.1f), 좌표는 왼쪽 그림 (y = 압출 방향, z = 폭 방향, 원점 O). 탭 깊이 = 바닥 두께.\n'
         '② 받침대 판: Al 6061-T6 %.1f × %.1f × %.1f (판재 절단, 표면 처리 없음), 접시 구멍 2 (Ø2.8 + 90° 접시 Ø4.9) — 압출 바닥에 M2.5 × 6 접시머리, 사이 열 그리스.\n'
         '   받침대 안쪽 면 (x = %.2f) = 옆 갭 패드 접촉면: 평면도 0.05, 접시머리는 면보다 0~0.1 낮게. 일반 공차 ISO 2768-m.\n'
         '③ 외함 고정: 외함 안쪽에서 M2.5 × 5 냄비머리 4 (벽 Ø2.8 → 바닥 탭). 핀 간격이 머리 Ø4.5 보다 좁아 바깥에서 넣지 않는다. 차선: CNC 단품 H3 (M-003 2차).\n'
         '좌표계 M-003 원점 O. STEP: out/step/HS_EXTRUSION.step · HS_PEDESTAL.step, DXF: fab/HS_*.dxf') % (
    hy1 - hy0, d['hs_tb'], d['hs_fin_zc'][1] - d['hs_fin_zc'][0] - d['hs_t'], ped_y[1] - ped_y[0], ped_z[1] - ped_z[0], d['hs_ped_t'], d['x_al_in'])
fig.text(0.03, 0.02, notes, fontsize=7)
fig.suptitle('M-005 가공 도면 2/2 — 바깥 방열판: 기성 압출 SK 444 2차가공 + 받침대 판', fontsize=9)
fig.tight_layout(rect=(0, 0.08, 1, 0.97)); pdf.savefig(fig); fig.savefig(os.path.join(OUT, 'm003-fab-2.png'), dpi=130); plt.close(fig)
pdf.close()
print('ok', sorted(os.listdir(OUT)))
