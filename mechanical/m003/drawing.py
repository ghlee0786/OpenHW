"""M-003 2D 도면 (외형·개구·보스) — params.py 값으로 그린다(CAD 독립). 출력 drawing/m003-drawing.pdf·.png
실행: python -I -B -X utf8 mechanical/m003/drawing.py"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages

HERE = os.path.dirname(os.path.abspath(__file__))
g = {}
exec(open(os.path.join(HERE, 'params.py'), encoding='utf-8').read(), g)
d = g['derive'](g['P'])
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
OUT = os.path.join(HERE, 'drawing')
os.makedirs(OUT, exist_ok=True)
K = dict(fill=False, lw=1.0, ec='k')
H = dict(fill=False, lw=0.9, ec='#c0392b')
HID = dict(fill=False, lw=0.7, ec='#2c7fb8', ls='--')


def dim(ax, a, b, off, txt=None, horiz=True):
    if horiz:
        y = off
        ax.annotate('', (a, y), (b, y), arrowprops=dict(arrowstyle='<->', lw=0.6))
        ax.text((a + b) / 2, y + 0.6, txt or '%.2f' % abs(b - a), ha='center', va='bottom', fontsize=6)
    else:
        x = off
        ax.annotate('', (x, a), (x, b), arrowprops=dict(arrowstyle='<->', lw=0.6))
        ax.text(x - 0.6, (a + b) / 2, txt or '%.2f' % abs(b - a), ha='right', va='center', fontsize=6, rotation=90)


def label(ax, x, y, s):
    ax.text(x, y, s, fontsize=5.5, color='#333')


def frame(ax, title):
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=8)
    ax.grid(True, lw=0.2, alpha=0.4)
    ax.tick_params(labelsize=5)


zt, zo, zb = d['z_bez_in'], d['z_bez_out'], d['z_back_out']
xo0, xo1, yo0 = d['x_out_min'], d['x_out_max'], d['y_out_min']
zc = d['z_car_bot']


def profile_yz():
    # +Y 벽 45° 단을 포함한 바깥 윤곽 (y, z)
    import math
    zs_o = d['step_z0'] - d['t_w'] * (math.sqrt(2) - 1)
    yl, yh = d['y_out_lo'], d['y_out_hi']
    return [(yo0, zb), (yl, zb), (yl, zs_o), (yh, zs_o + (yh - yl)), (yh, zo), (yo0, zo)]


fig, axs = plt.subplots(2, 3, figsize=(16.5, 11.7))
# 1 앞면 (+Z 에서)
ax = axs[0][0]
frame(ax, '① 앞면 (+Z에서 봄) — 덮개·창 주머니·나사')
ax.add_patch(Rectangle((xo0, yo0), xo1 - xo0, d['y_out_hi'] - yo0, **K))
ax.add_patch(Circle((0, 0), d['lens_win_d'] / 2 + 0.2, **K)); ax.add_patch(Circle((0, 0), d['lens_ap_d'] / 2, **HID))
xi0, xi1, ry = d['x_in_min'], d['x_in_max'], d['rib_y']
ax.add_patch(Rectangle((xi0, ry), xi1 - xi0, d['y_in_hi'] + 1 - ry, **K))
ax.add_patch(Rectangle((xi0, d['b_pocket_y0']), xi1 - xi0, -ry - d['b_pocket_y0'], **K))
(ax0, ax1), (ay0, ay1) = d['als_in']
ax.add_patch(Rectangle((ax0 - 1.1, ay0 - 1.1), ax1 - ax0 + 2.2, ay1 - ay0 + 2.7, **K))
for (x, y) in d['cov_screws']:
    ax.add_patch(Circle((x, y), 1.4, **H)); label(ax, x + 1.6, y, '(%.1f, %.1f) Ø2.8' % (x, y))
label(ax, -9, 1.5, '렌즈 창 Ø%.1f / 개구 Ø%.0f' % (d['lens_win_d'], d['lens_ap_d']))
label(ax, -20, 24, 'LED A 창 (PMMA 3t)'); label(ax, -20, -22, 'LED B 창 (PMMA 3t)'); label(ax, -24, 8, 'ALS 창')
dim(ax, xo0, xo1, yo0 - 4); dim(ax, yo0, d['y_out_hi'], xo0 - 3, horiz=False)
dim(ax, -ry, ry, xo1 + 4, '가운데 띠 %.1f' % (2 * ry), horiz=False)
ax.set_xlim(xo0 - 8, xo1 + 18); ax.set_ylim(yo0 - 8, d['y_out_hi'] + 4)
# 2 뒷면
ax = axs[0][1]
frame(ax, '② 뒷면 (-Z에서 봄, x 좌우 반전) — 기둥·삼각대·버튼·LED 구멍')
ax.add_patch(Rectangle((-xo1, yo0), xo1 - xo0, d['y_out_lo'] - yo0, **K))
for (x, y) in d['holes']:
    ax.add_patch(Circle((-x, y), d['post_cb_d'] / 2, **H)); ax.add_patch(Circle((-x, y), d['post_d'] / 2, **HID))
    label(ax, -x + 2.4, y, '기둥 (%.0f,%.0f) 카운터보어 Ø%.1f → M1.6×8' % (x, y, d['post_cb_d']))
tx, ty = d['tripod']
ax.add_patch(Circle((-tx, ty), d['tripod_hole_d'] / 2, **H)); ax.add_patch(Circle((-tx, ty), d['tripod_boss_d'] / 2, **HID))
label(ax, -tx + 7.5, ty - 2, '1/4"-20 인서트 Ø%.1f (보스 Ø%.0f)' % (d['tripod_hole_d'], d['tripod_boss_d']))
for (x, y) in d['btn']:
    ax.add_patch(Circle((-x, y), 1.1, **H)); label(ax, -x - 9, y + 1, '버튼 Ø2.2')
for (x, y) in d['stat_led']:
    ax.add_patch(Circle((-x, y), 1.0, **H)); label(ax, -x - 9, y - 2, 'LED Ø2.0')
dim(ax, -xo1, -xo0, yo0 - 4)
ax.set_xlim(-xo1 - 6, -xo0 + 22); ax.set_ylim(yo0 - 8, d['y_out_lo'] + 4)
# 3 -Y 면 (x, z)
ax = axs[0][2]
frame(ax, '③ -Y 면 (-Y에서 봄) — RJ45·DC 잭')
ax.add_patch(Rectangle((xo0, zb), xo1 - xo0, zt - zb, **K)); ax.add_patch(Rectangle((xo0, zt), xo1 - xo0, zo - zt, **K))
rjc = sum(d['rj_x']) / 2
ax.add_patch(Rectangle((rjc - d['rj_open_w'] / 2, zc - d['rj_open_h']), d['rj_open_w'], d['rj_open_h'], **H))
label(ax, rjc - 8, zc - d['rj_open_h'] - 3, 'RJ45 개구 %.2f×%.2f (HR911105A 권장)' % (d['rj_open_w'], d['rj_open_h']))
dcx = sum(d['dc_x']) / 2
ax.add_patch(Circle((dcx, zc - d['dc_axis_below']), d['dc_open_d'] / 2, **H))
label(ax, dcx - 4, zc - d['dc_axis_below'] + 6, 'DC Ø%.1f 중심 (%.2f, %.2f)' % (d['dc_open_d'], dcx, zc - d['dc_axis_below']))
ax.axhline(zc, lw=0.4, ls=':', c='g'); label(ax, xo0, zc + 0.5, '캐리어 아랫면 z %.1f' % zc)
dim(ax, zb, zo, xo0 - 3, horiz=False); dim(ax, xo0, xo1, zb - 4)
ax.set_xlim(xo0 - 8, xo1 + 4); ax.set_ylim(zb - 8, zo + 4)
# 4 -X 면 (y, z)
ax = axs[1][0]
frame(ax, '④ -X 면 (-X에서 봄) — USB-C·외형 단')
ax.add_patch(Polygon(profile_yz(), closed=True, **K)); ax.axhline(zt, lw=0.4, c='k')
uzc = zc - d['usb_h'] / 2
ax.add_patch(Rectangle((-d['usb_open_w'] / 2, uzc - d['usb_open_h'] / 2), d['usb_open_w'], d['usb_open_h'], **H))
label(ax, -6, uzc - 6, 'USB-C 개구 %.1f×%.1f 중심 z %.2f' % (d['usb_open_w'], d['usb_open_h'], uzc))
dim(ax, yo0, d['y_out_hi'], zb - 4); dim(ax, zb, zo, yo0 - 3, horiz=False)
label(ax, d['y_out_lo'] + 1, d['step_z0'] - 4, '45° 단 (LED A 바깥 %.0f°)' % d['led_out_deg'])
ax.set_xlim(yo0 - 8, d['y_out_hi'] + 6); ax.set_ylim(zb - 8, zo + 4)
# 5 +Y 면 (x, z)
ax = axs[1][1]
frame(ax, '⑤ +Y 아래 벽 (+Y에서 봄) — microSD')
ax.add_patch(Rectangle((xo0, zb), xo1 - xo0, d['step_z0'] - zb, **K))
sx = sum(d['sd_x']) / 2
ax.add_patch(Rectangle((sx - d['sd_slot_w'] / 2, zc + d['sd_slot_z'][0]), d['sd_slot_w'], d['sd_slot_z'][1] - d['sd_slot_z'][0], **H))
ax.add_patch(Rectangle((sx - 9, zc - 4.6), 18, 7.0, **HID))
label(ax, sx - 12, zc - 7, '슬롯 %.0f×%.1f · 손가락 홈 18×7 깊이 1.2' % (d['sd_slot_w'], d['sd_slot_z'][1] - d['sd_slot_z'][0]))
dim(ax, xo0, xo1, zb - 4)
ax.set_xlim(xo0 - 6, xo1 + 4); ax.set_ylim(zb - 8, d['step_z0'] + 4)
# 6 +X 면 (y, z)
ax = axs[1][2]
frame(ax, '⑥ +X 면 (+X에서 봄) — 알루미늄 옆판 창·나사')
ax.add_patch(Polygon(profile_yz(), closed=True, **K))
(wy0, wy1), (wz0, wz1) = d['al_win_y'], d['al_win_z']
ax.add_patch(Rectangle((wy0, wz0), wy1 - wy0, wz1 - wz0, **H))
ax.add_patch(Rectangle((d['al_y'][0], d['al_z'][0]), d['al_y'][1] - d['al_y'][0], d['al_z'][1] - d['al_z'][0], **HID))
for (y, z) in d['al_holes']:
    ax.add_patch(Circle((y, z), 1.4, **H))
label(ax, wy0 + 1, wz1 + 1, '창 %.0f×%.0f / 옆판 5052 %.0f×%.0f×%.1f (점선) / M2.5 4곳' % (wy1 - wy0, wz1 - wz0, d['al_y'][1] - d['al_y'][0], d['al_z'][1] - d['al_z'][0], d['al_t']))
ax.set_xlim(yo0 - 6, d['y_out_hi'] + 6); ax.set_ylim(zb - 8, zo + 4)
fig.suptitle('M-003 외함 2D 도면 (단위 mm, 원점 O = 코어 중심·아랫면, +Z 앞) — params.py 기준, 검은선 외형 / 빨간선 개구·구멍 / 파란 점선 보스·숨은선', fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.97))
with PdfPages(os.path.join(OUT, 'm003-drawing.pdf')) as pdf:
    pdf.savefig(fig)
fig.savefig(os.path.join(OUT, 'm003-drawing.png'), dpi=160)
print('ok', os.listdir(OUT))
