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

    def save(self, name):
        hdr = '0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n'
        open(os.path.join(OUT, name), 'w', encoding='ascii').write(hdr + ''.join(self.e) + '0\nENDSEC\n0\nEOF\n')


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
    'WIN_A': ('rrect', (xi1 - 0.2) - (xi0 + 0.2), (d['y_in_hi'] + 0.8) - (ry + 0.2), d['win_t']),
    'WIN_B': ('rrect', (xi1 - 0.2) - (xi0 + 0.2), (-ry - 0.2) - (d['b_pocket_y0'] + 0.2), d['win_t']),
    'WIN_ALS': ('rrect', (ax1 + 0.9) - (ax0 - 0.9), (ay1 + 1.4) - (ay0 - 0.9), 1.5),
}
for name, spec in W.items():
    dx = DXF()
    if spec[0] == 'circle':
        dx.circle((0, 0), spec[1] / 2)
    else:
        dx.rrect(0, 0, spec[1], spec[2], wr)
    dx.save('PMMA_%s_t%.1f.dxf' % (name, spec[-1]))
# ---- 폼 (9, 10) ----
fi, fo, ft = d['lens_foam']
dx = DXF(); dx.circle((0, 0), fo); dx.circle((0, 0), fi, 'HOLE'); dx.save('FOAM_LENS_RING_t%.1f.dxf' % ft)
gw, gh = ax1 - ax0 + 2 * d['als_wall'], ay1 - ay0 + 2 * d['als_wall']
dx = DXF(); dx.poly([(0, 0), (gw, 0), (gw, gh), (0, gh)]); dx.poly([(1, 1), (gw - 1, 1), (gw - 1, gh - 1), (1, gh - 1)], 'HOLE'); dx.save('FOAM_ALS_GASKET_t1.5.dxf')
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
for (y, z) in d['al_holes']:
    dx.circle((y, z), 1.4, 'HOLE')
dx.poly([(ped_y[0], ped_z[0]), (ped_y[1], ped_z[0]), (ped_y[1], ped_z[1]), (ped_y[0], ped_z[1])], 'REF')
for zc_ in d['hs_fin_zc']:
    dx.line((hy0, zc_ - d['hs_t'] / 2), (hy1, zc_ - d['hs_t'] / 2), 'REF'); dx.line((hy0, zc_ + d['hs_t'] / 2), (hy1, zc_ + d['hs_t'] / 2), 'REF')
dx.save('AL_HEATSINK_PX_base_face_YZ.dxf')
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
dx.save('AL_HEATSINK_PX_fin_section_XZ.dxf')

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
        draw_rrect(ax, 0, 0, spec[1], spec[2], wr, ec='k')
        dim(ax, 0, spec[1], -2.5); dim(ax, 0, spec[2], -2, horiz=False)
        ax.set_xlim(-6, spec[1] + 4); ax.set_ylim(-6, spec[2] + 4)
    frame(ax, 'PMMA %s — t%.1f 투명, 모서리 R%.1f' % (name, spec[-1], wr if spec[0] != 'circle' else 0))
    ax.text(0.02, 0.02, '레이저 컷 · 양면 보호지 유지(조립 직전 제거)\n외형 공차 ±0.1 (print-prep.md §5) · 버·녹은 자국 없이', transform=ax.transAxes, fontsize=5.5)
ax = axs.flat[k]; k += 1
ax.add_patch(plt.Circle((0, 0), fo, fill=False, lw=1)); ax.add_patch(plt.Circle((0, 0), fi, fill=False, lw=1, ec='#c0392b'))
dim(ax, -fo, fo, -fo - 1.5, txt='OD %.1f' % (2 * fo)); dim(ax, -fi, fi, fi + 0.6, txt='ID %.1f' % (2 * fi))
frame(ax, '흑색 폼 렌즈 링 t%.1f → 0.7 압축 (30%%)' % ft); ax.set_xlim(-12, 12); ax.set_ylim(-12, 12)
ax = axs.flat[k]; k += 1
ax.add_patch(Rectangle((0, 0), gw, gh, fill=False, lw=1)); ax.add_patch(Rectangle((1, 1), gw - 2, gh - 2, fill=False, lw=1, ec='#c0392b'))
dim(ax, 0, gw, -1.2); dim(ax, 0, gh, -1, horiz=False)
frame(ax, '흑색 폼 ALS 개스킷 t1.5 → %.1f 압축 (20%%)' % d['als_gap']); ax.set_xlim(-4, gw + 3); ax.set_ylim(-4, gh + 2)
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
for (y, z) in d['al_holes']:
    ax.add_patch(plt.Circle((y, z), 1.4, fill=False, ec='#c0392b', lw=1))
    ax.text(y + 1.8, z, '(%.1f, %.2f)' % (y, z), fontsize=6)
dim(ax, hy0, hy1, hz0 - 4); dim(ax, hz0, hz1, hy0 - 4, horiz=False)
dim(ax, ped_y[0], ped_y[1], ped_z[0] + 2, txt='받침대 %.1f' % (ped_y[1] - ped_y[0])); dim(ax, ped_z[0], ped_z[1], ped_y[1] - 3, horiz=False, txt='%.1f' % (ped_z[1] - ped_z[0]))
frame(ax, '바닥판 정면 (+X 에서 봄, 가로 y / 세로 z) — 구멍 Ø2.8 관통 4 (M2.5 틈새), 회색 = 핀 위치, 파란 점선 = 받침대')
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
notes = ('재질 Al 6061-T6 · 표면 흑색 아노다이즈 Type II (ε 약 0.85 가정; 받침대 안쪽 접촉면은 아노다이즈 허용 — 절연 갭 패드 접촉)\n'
         '일반 공차 ISO 2768-m · 받침대 접촉면(x = %.2f) 평면도 0.05 · 핀 두께 %.1f ±0.1 · 날카로운 모서리 C0.2\n'
         '구멍 Ø2.8 (M2.5 틈새) 4곳 — 좌표는 왼쪽 그림 · 핀 사이 나사·드라이버 통로 확보 · 차선: 압출 핀 방열판 + 받침 블록 접합\n'
         '좌표계: M-003 원점 O (코어 중심·아랫면), x = +X 바깥 방향. STEP: out/step/AL_HEATSINK_PX.step, DXF: fab/AL_HEATSINK_PX_*.dxf') % (d['x_al_in'], d['hs_t'])
fig.text(0.03, 0.02, notes, fontsize=7)
fig.suptitle('M-003c 가공 도면 2/2 — 바깥 방열판 AL_HEATSINK_PX (H3)', fontsize=9)
fig.tight_layout(rect=(0, 0.08, 1, 0.97)); pdf.savefig(fig); fig.savefig(os.path.join(OUT, 'm003-fab-2.png'), dpi=130); plt.close(fig)
pdf.close()
print('ok', sorted(os.listdir(OUT)))
