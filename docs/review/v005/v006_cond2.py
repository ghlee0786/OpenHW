# -*- coding: utf-8 -*-
"""V-006: VD-001 조건 2(PCB) 판정 집계 — run_v005.sh 결과 폴더의 json 을 모아 VD-001 항목 형식(docs/review/vd001-format.md)으로 쓴다.

사용: python -I v006_cond2.py <결과 폴더> <pcb 커밋> <out.json> [--snap <스냅샷 루트>]
종료 코드 = 불합격(pass=false) 항목 수. 사람 확인 항목(verifiable=false)은 세지 않는다.
읽는 파일(보드마다): drc_<b>.json · relax_<b>.json · excl_<b>.json · rules_<b>.json · silk_<b>.json
"""
import sys, os, re, json, argparse, datetime

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('res'); ap.add_argument('commit'); ap.add_argument('out')
ap.add_argument('--snap', default=None)
ap.add_argument('--root', default='.', help='근거 경로를 이 저장소 루트 기준 상대 경로로 쓴다')
ap.add_argument('--d003', default=None, help='D-003 문서 — #62(MDI TX 쌍 안 길이 차·비결합 예외) 한도와 #63(비결합 셈법)을 이 행에서 읽는다')
ap.add_argument('--area-baseline', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'area-baseline.json'),
                help='탈출·보정 영역(DP_BRK·DP_TUNE) 수·면적 기준 — 이보다 커지면 불합격 (D-003 #63)')
A = ap.parse_args()
BOARDS = ['carrier', 'front']
items = []


def J(name):
    p = os.path.join(A.res, name)
    return (json.load(open(p, encoding='utf-8')), name) if os.path.exists(p) else (None, name)


def add(id_, board, title, value, limit, ok, ev, note='', verifiable=True):
    def ep(e):
        f, _, frag = e.partition('#')
        p = os.path.join(A.res, f)
        if os.path.exists(p):
            return os.path.relpath(p, A.root).replace(os.sep, '/') + ('#' + frag if frag else '')
        return e
    items.append(dict(cond='2', id=id_, board=board, title=title, verifiable=verifiable, value=value, limit=limit,
                      **{'pass': (None if not verifiable else bool(ok))}, evidence=[dict(label=e, path=ep(e)) for e in ev], commit=A.commit, note=note))


# O-119 / D-003 #62: 캐리어 MDI TX 쌍만 쌍 안 길이 차·비결합 길이 예외. 한도는 #62 행의 「쌍 안 길이 차 ≤N mm」「비결합 길이 ≤N mm」에서 읽는다
#   — 행이 없거나 「MDI TX」가 없거나 그 문구가 없으면 그 예외는 없음(#28: 차 「0」, 비결합은 mdi_100_pair 한도)
TX_DIFF_MAX = TX_UNC_MAX = None
UNC63 = False   # D-003 #63: 비결합은 탈출·보정 영역(DP_BRK·DP_TUNE) 안 구간을 결합으로 셈 — 행이 있을 때만
if A.d003 and os.path.exists(A.d003):
    for _l in open(A.d003, encoding='utf-8'):
        if re.match(r'\|\s*62\s*\|', _l) and 'MDI TX' in _l:
            _m = re.search(r'쌍 안 길이 차\s*≤\s*([\d.]+)\s*mm', _l)
            TX_DIFF_MAX = float(_m.group(1)) if _m else None
            _m = re.search(r'비결합 길이\s*≤\s*([\d.]+)\s*mm', _l)
            TX_UNC_MAX = float(_m.group(1)) if _m else None
        if re.match(r'\|\s*63\s*\|', _l) and 'DP_BRK' in _l and 'DP_TUNE' in _l and '결합으로' in _l:
            UNC63 = True
AREA_GAP_MAX = {'DP_BRK': 2.2, 'DP_TUNE': 1.0}   # D-003 #46 — 보드 규칙 값은 v006_relax 가 #46 기록과 대조한다
ABASE = json.load(open(A.area_baseline, encoding='utf-8')) if os.path.exists(A.area_baseline) else {}
area_rows = []


def dru_text(b):
    if not A.snap:
        return ''
    p = os.path.join(A.snap, 'hardware', 'schematic', b, b + '.kicad_dru')
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''


def rule_max(t, rule, ctype, default):
    m = re.search(r'\(rule\s+"%s"(.*?)(?=\n\(rule|\Z)' % re.escape(rule), t, re.S)
    if m:
        k = re.search(r'\(constraint\s+%s[^)]*?\(max\s+([\d.]+)mm\)' % ctype, m.group(1))
        if k:
            return float(k.group(1))
    return default


for b in BOARDS:
    drc, fd = J('drc_%s.json' % b)
    if drc is None:
        add('2.DRC', b, 'DRC 결과 파일', '없음', '있음', False, [fd]); continue
    add('2.A1', b, 'DRC 위반 (kicad-cli pcb drc --severity-all --schematic-parity)', len(drc['violations']), 0, len(drc['violations']) == 0, [fd])
    add('2.A2', b, '미연결', len(drc['unconnected_items']), 0, len(drc['unconnected_items']) == 0, [fd])
    add('2.PAR', b, '회로도 일치(parity) 문제', len(drc.get('schematic_parity', [])), 0, len(drc.get('schematic_parity', [])) == 0, [fd])
    rx, fr = J('relax_%s.json' % b)
    if rx is None:
        add('2.RLX', b, '규칙 완화 ↔ D-003', '결과 없음', '불합격 0', False, [fr])
    else:
        bad = [r['detail'] + ' — ' + r['status'] for r in rx['relaxations'] if not r['ok']]
        add('2.RLX', b, '규칙 완화·ignore 가 D-003 기록분뿐 (완화 %d건)' % len(rx['relaxations']), len(bad), 0, not bad, [fr], '; '.join(bad[:12]))
    ex, fe = J('excl_%s.json' % b)
    if ex is not None:
        v = ex['verdict']
        add('2.E2b', b, 'DRC 제외 0 (O-74b)', v['exclusions'], 0, v.get('E2b_exclusions_zero', v['exclusions'] == 0), [fe])
        f4 = v['E4a_fail'] + v['E4b_fail'] + v.get('E4c_fail', [])
        add('2.E4', b, '라이브러리 사본·인스턴스: 패드·구멍·실크 밖 같음, 원본 sha256 (O-74b, 사본 %d)' % v.get('E4c_copies', 0), len(f4), 0, not f4, [fe], ', '.join(f4))
    ru, frr = J('rules_%s.json' % b)
    if ru is not None:
        t = dru_text(b)
        lim = {'CSI_100': rule_max(t, 'csi_100_pair', 'diff_pair_uncoupled', 4.0), 'MDI_100': rule_max(t, 'mdi_100_pair', 'diff_pair_uncoupled', 6.0),
               'USB_90': rule_max(t, 'usb_90_pair', 'diff_pair_uncoupled', 12.0)}
        twist_lim = rule_max(t, 'mdi_twist_pair', 'diff_pair_uncoupled', 20.0)
        # 안전장치: 넷클래스(.kicad_pro)를 못 읽으면 쌍이 0 이 되어 아래 판정이 통째로 빠진다 — 그 경우를 불합격으로 드러낸다
        np_ = len(ru.get('pairs', {}))
        add('2.A0', b, '고속 차동쌍 인식 수 (넷클래스 CSI_100 · MDI_100 · USB_90)', np_, '≥1', np_ >= 1, [frr],
            '' if np_ else '쌍 0 — 보드 옆 .kicad_pro(넷클래스) 없이 돌렸는지 확인')
        for k, p in ru.get('pairs', {}).items():
            vi = p.get('via')
            dj = vi['diff_judged'] if vi else p['diff']   # 판정값 = max(트랙, 트랙+비아 높이) — 꼬임 영역 안 비아는 뺌 (research 와 합의, D-003 #63)
            dn = ('트랙 %g / +비아 %g (꼬임 비아 제외)' % (p['diff'], vi['diff_with_via'])) if vi else '트랙 길이만'
            if b == 'carrier' and k == '/EPHY_TX' and TX_DIFF_MAX is not None:
                add('2.A8', b, '쌍 안 길이 차 %s (MDI TX 예외)' % k, dj, '≤%g (D-003 #62, #28 예외)' % TX_DIFF_MAX, dj <= TX_DIFF_MAX + 1e-6, [frr], dn)
            else:
                add('2.A8', b, '쌍 안 길이 차 %s' % k, dj, '≤0.025 (D-003 #28 「0」)', dj <= 0.025, [frr], dn)
            s = p['strict_0.18']
            if p['cls'] == 'MDI_100' and 'uncoupled_outside_twist' in p:
                o1 = max(p['uncoupled_outside_twist'].values())
                ar = p.get('uncoupled_area_rule')
                tx62 = b == 'carrier' and k == '/EPHY_TX' and TX_UNC_MAX is not None
                ulim = TX_UNC_MAX if tx62 else lim['MDI_100']
                if UNC63 and ar:   # ② 탈출·보정 영역 안 구간은 결합, 짝 없는 비아 높이는 더함(꼬임 비아 제외)
                    av = vi['uncoupled_area_rule_with_via'] if vi else ar
                    o = max(av['P'], av['N'])
                    add('2.A10', b, '비결합(꼬임 밖, 탈출·보정 영역은 결합 — D-003 #63) %s%s' % (k, ' (MDI TX 예외)' if tx62 else ''), o,
                        '≤%g%s' % (ulim, ' (D-003 #62, #28 예외)' if tx62 else ''), o <= ulim + 1e-6, [frr],
                        '트랙만 %g · 참고: 쌍 간격 0.18 이하만 결합으로 세면 %g' % (max(ar['P'], ar['N']), o1))
                    ot = max(ar['P'] + ar['in_twist_P'], ar['N'] + ar['in_twist_N'])
                    add('2.A10t', b, '비결합(꼬임 포함, 탈출·보정 영역은 결합) %s' % k, round(ot, 3), '≤%g' % twist_lim, ot <= twist_lim + 1e-6, [frr])
                else:
                    add('2.A10', b, '비결합(꼬임 밖, 쌍 간격 0.18 이하만 결합) %s%s' % (k, ' (MDI TX 예외)' if tx62 else ''), o1,
                        '≤%g%s' % (ulim, ' (D-003 #62, #28 예외)' if tx62 else ''), o1 <= ulim + 1e-6, [frr],
                        ('참고: 탈출·보정 영역 간격(D-003 #46 DP_BRK 2.2 · DP_TUNE 1.0)을 결합으로 보면 %g' % max(ar['P'], ar['N'])) if ar else '')
                    add('2.A10t', b, '비결합(꼬임 포함) %s' % k, s['uncoupled_max'], '≤%g' % twist_lim, s['uncoupled_max'] <= twist_lim + 1e-6, [frr])
            else:
                ar = p.get('uncoupled_area_rule')
                if UNC63 and ar:
                    av = vi['uncoupled_area_rule_with_via'] if vi else ar
                    o = max(av['P'], av['N'])
                    add('2.A10', b, '비결합(탈출·보정 영역은 결합 — D-003 #63) %s' % k, o, '≤%g' % lim[p['cls']], o <= lim[p['cls']] + 1e-6, [frr],
                        '트랙만 %g · 참고: 쌍 간격 0.18 이하만 결합으로 세면 %g' % (max(ar['P'], ar['N']), s['uncoupled_max']))
                else:
                    add('2.A10', b, '비결합 %s' % k, s['uncoupled_max'], '≤%g' % lim[p['cls']], s['uncoupled_max'] <= lim[p['cls']] + 1e-6, [frr])
        at = ru.get('area_table')
        if at is not None:   # D-003 #63: 탈출·보정 영역이 커지지 않는지 — 수·면적을 기준 파일과 대조, 영역 안 쌍 간격은 #46 상한 안
            cur = {}
            for r_ in at:
                c_ = cur.setdefault(r_['name'], dict(count=0, area_mm2=0.0)); c_['count'] += 1; c_['area_mm2'] = round(c_['area_mm2'] + r_['area_mm2'], 3)
                for pk, pv in (r_['pairs'] or {'-': dict(lenP=0, lenN=0, extraP=0, extraN=0, gap_max=None)}).items():
                    area_rows.append((b, r_['name'], r_['idx'], r_['bbox'], r_['w'], r_['h'], r_['area_mm2'], pk, pv['lenP'], pv['lenN'], pv['gap_max'], pv['extraP'], pv['extraN'], '·'.join(r_['layers'])))
            for a_ in (ru.get('esc_vias') or {}).get('areas', []):   # 0.50/0.20 비아 영역(J1_ · SD_)도 같은 기준으로 감시 (D-003 #60 · #64 「최소 크기」)
                c_ = cur.setdefault(a_['name'], dict(count=0, area_mm2=0.0)); c_['count'] += 1; c_['area_mm2'] = round(c_['area_mm2'] + a_.get('area_mm2', 0.0), 3)
                area_rows.append((b, a_['name'], 0, a_['bbox'], a_.get('w', 0), a_.get('h', 0), a_.get('area_mm2', 0), '-', 0, 0, None, 0, 0, '·'.join(a_['layers'])))
            base_ = ABASE.get(b, {})
            bad_ = [n for n, c_ in cur.items() if n not in base_ or c_['count'] > base_[n]['count'] or c_['area_mm2'] > base_[n]['area_mm2'] + 0.01]
            fmt_ = lambda d_: ' / '.join('%s %d개 %g mm²' % (n, d_[n]['count'], d_[n]['area_mm2']) for n in sorted(d_)) or '없음'
            add('2.A14', b, '규칙 완화 영역(DP_BRK·DP_TUNE·J1_·SD_) 수·면적이 기준 이하 (D-003 #63 · #60 · #64)', fmt_(cur), '≤ ' + fmt_({n: base_[n] for n in base_ if not n.startswith('_')}), not bad_, [frr, 'areas.md'],
                ('커짐·기준 없음: ' + ', '.join(bad_)) if bad_ else '')
        if ru.get('csi_skew'):
            add('2.A9', b, 'CSI 레인 skew', ru['csi_skew']['skew_net'], '≤1.0', ru['csi_skew']['skew_net'] <= 1.0, [frr])
        xc = len(ru.get('hs_cross_in2_signal', [])) + len(ru.get('hs_cross_in1_signal', []))
        add('2.A7', b, '고속선 아래 기준층 신호선 교차', xc, 0, xc == 0, [frr])
        if 'DP_TWIST' in ru.get('rule_areas', {}):
            enclosed = bool(re.search(r"enclosedByArea\('DP_TWIST'\)", t)) and not re.search(r"intersectsArea\('DP_TWIST'\)", t)
            leak = ru['area_rule_leak'].get('DP_TWIST', {}).get('outside_len', 0)
            add('2.A11', b, '꼬임 예외가 DP_TWIST 영역 안에만 (enclosedByArea 또는 누출 0)', 0 if enclosed else leak, 0, enclosed or leak == 0, [frr],
                'enclosedByArea 조건' if enclosed else 'intersectsArea 누출 길이(mm)')
        ev_ = ru.get('esc_vias')
        if ev_ is not None:   # O-114 / D-003 #60: J1 탈출 비아 0.50/0.20 은 J1 둘레 규칙 영역(enclosedByArea) 안에서만
            an = [a['name'] for a in ev_['areas']]
            add('2.V1', b, '비아 0.65/0.30 미만은 0.50/0.20 영역(J1_ · SD_) 안에만, 열·GND 이음 비아는 0.60/0.30 허용 (D-003 #21·#60·#64) — 그 밖의 작은 비아', len(ev_['outside_small']), 0, not ev_['outside_small'], [frr],
                '; '.join(sorted(set('%s/%s %s' % (v['dia'], v['drill'], v['net']) for v in ev_['outside_small']))[:8]) + (' · 걸침 %d' % len(ev_['straddle_small']) if ev_['straddle_small'] else '')
                + ' · 0.60/0.30 허용분: GND %d, 열 %d' % (sum(1 for v in ev_.get('allowed_060', []) if v['kind'] == 'GND'), sum(1 for v in ev_.get('allowed_060', []) if v['kind'] == '열')))
            if an or ev_['inside']:
                pfx = '(?:%s)' % '|'.join(re.escape(x) for x in ev_.get('prefixes', ['J1_']))
                inter = sorted(set(re.findall(r"intersectsArea\('(%s[^']*)'\)" % pfx, t)))
                encl = sorted(set(re.findall(r"enclosedByArea\('(%s[^']*)'\)" % pfx, t)))
                norule = sorted(set(an) - set(encl))   # 보드에 영역은 있는데 그 이름의 enclosedByArea 규칙이 없음
                add('2.V2', b, '0.50/0.20 비아 규칙이 enclosedByArea 뿐 (영역 %s)' % (', '.join(sorted(set(an))) or '없음'), len(inter) + len(norule), 0,
                    bool(encl) and not inter and not norule, [frr],
                    ('intersectsArea 규칙: ' + ', '.join(inter)) if inter else (('규칙 없는 영역: ' + ', '.join(norule)) if norule else ('enclosedByArea: ' + (', '.join(encl) or '규칙 없음'))))
                add('2.V3', b, '영역 안 작은 비아 %d개: 지름 ≥0.50 · 드릴 ≥0.20 · 링 ≥0.15 · 구멍 간격 ≥0.28' % len(ev_['inside']), len(ev_['inside_fail']), 0,
                    not ev_['inside_fail'], [frr], '; '.join('%s %s' % (v['at'], ','.join(v['why'])) for v in ev_['inside_fail'][:8]))
                add('2.V4', b, '영역 안 작은 비아는 그 영역 부품(J1_ → J1, SD_ → U4·U5) 핀 넷뿐', len(ev_['non_j1_net']), 0, not ev_['non_j1_net'], [frr],
                    ', '.join(sorted(set(v['net'] for v in ev_['non_j1_net']))))
                far = [a for a in ev_['areas'] if not a['beyond_ok']]
                add('2.V5', b, '0.50/0.20 영역이 그 부품 둘레 안 (부품 외곽 상자 + 3.0 [가정])', max([a['beyond_j1'] or 0 for a in ev_['areas']] or [0]), '≤3.0', bool(an) and not far, [frr])
        eg = (ru.get('esd_gnd') or {}).get('pads')
        if eg:   # O-121 / D-003 #64: ESD 어레이 GND — 핀마다 조건 맞는 비아(패드→비아 ≤1.0 · 폭 ≥0.25) 1개 이상, 가능하면 2개
            none_ = ['%s.%s' % (x['ref'], x['pad']) for x in eg if x['n_ok'] == 0]
            one_ = ['%s.%s' % (x['ref'], x['pad']) for x in eg if x['n_ok'] == 1]
            add('2.V6', b, 'ESD 어레이(U4·U5) GND 핀 %d개: 핀마다 조건 맞는 비아 ≥1 (패드→비아 ≤%g · 폭 ≥%g, D-003 #64)' % (len(eg), ru['esd_gnd']['len_max'], ru['esd_gnd']['width_min']),
                len(none_), 0, not none_, [frr], '; '.join(x for x in (('조건 맞는 비아 없음: ' + ', '.join(none_)) if none_ else '', ('비아 1개뿐(가능하면 2개): ' + ', '.join(one_)) if one_ else '') if x))
        for l in ru.get('ir_leds', []):
            add('2.A12', b, 'IR LED 열 비아 %s' % l['ref'], l['thermal_vias'], '≥4 (D-003 #29)', l['thermal_vias'] >= 4, [frr])
        for e in ru.get('exposed_pads', []):
            ok = e.get('min_dist_edge', 0) >= 0.40 - 1e-6 and e.get('min_dist_other_net_Bcu', 0) >= 0.16 - 1e-6
            add('2.A13', b, '노출 패드 %s %s 외곽·다른 넷 거리' % (e['zone'], e['net']), '%s / %s' % (e.get('min_dist_edge'), e.get('min_dist_other_net_Bcu')), '≥0.40 / ≥0.16', ok, [frr])
        for g in ru.get('exposed_pad_gaps', []):
            if g['gap'] < 1e8:
                add('2.A13g', b, '노출 패드 틈 %s–%s' % (g['a'], g['b']), g['gap'], '≥0.6 (O-43)', g['gap'] >= 0.6 - 1e-6, [frr])
        if ru.get('exposed_pads'):
            add('2.A13x', b, 'B.Mask 개구 안 다른 넷 구리', len(ru.get('bmask_other_net_exposed', [])), 0, not ru.get('bmask_other_net_exposed'), [frr])
    si, fs = J('silk_%s.json' % b)
    if si is not None:
        names = {'S1_on_mask_open': '패드·노출 동박 위 실크', 'S1v_over_via': '안 덮인 비아 위 실크 (덮인 비아는 허용, D-003 #58)', 'S1h_over_hole': '열린 구멍 위 실크',
                 'S2_clear_lt_0p15': '실크–마스크 개구 < 0.15', 'S3_line_lt_0p15': '실크 선폭 < 0.15', 'S4_text': '글자 높이·획 미달',
                 'S4r_ratio_lt_1to5': '글자 획/높이 < 1:5', 'S5_edge': '외곽까지 < 0.30', 'S6_ref_hidden': '부품 아래 숨는 참조',
                 'S7_text_text': '글자 겹침',
                 'S7l_text_line': '글자–선 겹침', 'S7s_text_space': '글자–실크 간격 < 0.127', 'S8_orient_gt2': '읽는 방향 > 2',
                 'S8m_mirror': '거울상 오류', 'S9_missing': '1번 핀·극성 표시 없음', 'S9_wrong_side': '1번 핀·극성 표시 반대'}
        for k, n in names.items():
            v = si['summary'].get(k, 0)
            add('2.' + k.split('_')[0], b, '실크 ' + n, v, 0, v == 0, [fs])
        c = si.get('counts', {})
        add('2.TXT', b, '실크 참조 지정자 수(앞/뒤) — O-65 실크에 둠', '%s / %s' % (c.get('F', {}).get('ref', 0), c.get('B', {}).get('ref', 0)), '>0',
            (c.get('F', {}).get('ref', 0) + c.get('B', {}).get('ref', 0)) > 0, [fs])
        ex_ = [p['ref'] for p in si['pin1_candidates'] if p['verdict'] == 'exempt']
        half = [p['ref'] for p in si['pin1_candidates'] if p['verdict'] == 'ok_half']
        # O-115(lead 결정 c): 참조 글자 멂·모호(S6a)는 기계 불합격이 아니라 사람 확인 — 자리 없어 떨어뜨린 글자가 어느 부품 것인지 사람이 본다
        far_ = sorted(set(x['owner'] for x in si['findings'].get('S6a_ref_far', [])))
        amb_ = sorted(set(x['owner'] for x in si['findings'].get('S6a_ref_ambiguous', [])))
        if far_ or amb_:
            add('2.H4', b, '부품에서 떨어진 참조 글자가 어느 부품 것인지 알아보는가 — 멂(>2.0) %d: %s / 다른 부품이 더 가까움 %d: %s'
                % (len(far_), ', '.join(far_) or '-', len(amb_), ', '.join(amb_) or '-'), '%d / %d' % (len(far_), len(amb_)), '사람 확인', None, [fs, 'index.html#4'], verifiable=False)
        if ex_:
            add('2.H1', b, '기구 키 커넥터는 1번 핀 표시 없어도 되는가: ' + ', '.join(ex_), '-', '사람 확인', None, [fs, 'index.html#4.1'], verifiable=False)
        if half:
            add('2.H2', b, '약한 1번 핀 표시(ok_half)를 알아보는가: ' + ', '.join(half), '-', '사람 확인', None, [fs, 'index.html#4.1'], verifiable=False)
add('2.H3', '-', '첫 보드 실물 실크 인쇄 품질(0.15 선·1.0 글자) — bring-up 으로 넘김', '-', '실물 확인', None, ['docs/review/v005-pcb-review.md'], verifiable=False)

# 영역 표 (D-003 #63 감시용) — 결과 폴더의 areas.md
_L = ['# 탈출·보정 영역 표 (pcb %s, D-003 #63)' % A.commit, '',
      '「영역 덕에 결합으로 센 길이」 = 쌍 간격이 0.18 초과 ~ 영역 상한 이하라서, 이 영역이 없으면 비결합으로 셌을 길이.', '',
      '| 보드 | 영역 | # | 층 | 범위 (x0, y0, x1, y1) | 크기 | 면적 mm² | 쌍 | 영역 안 길이 P / N | 영역 덕에 결합으로 센 길이 P / N | 결합 구간 쌍 간격 최대 | 상한 |',
      '|---|---|---|---|---|---|---|---|---|---|---|---|']
for r_ in area_rows:
    _L.append('| %s | %s | %d | %s | %s | %g × %g | %g | %s | %g / %g | %g / %g | %s | %s |' % (
        r_[0], r_[1], r_[2], r_[13], ', '.join('%g' % v for v in r_[3]), r_[4], r_[5], r_[6], r_[7], r_[8], r_[9], r_[11], r_[12],
        '-' if r_[10] is None else '%g' % r_[10], ('%g' % AREA_GAP_MAX[r_[1]]) if r_[1] in AREA_GAP_MAX else '-'))
open(os.path.join(os.path.dirname(os.path.abspath(A.out)), 'areas.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(_L) + '\n')

fails = [i for i in items if i['verifiable'] and i['pass'] is False]
R = dict(cond='2', owner='review', title='PCB DRC·미연결·parity·완화 기록·V-005 최종', commit=A.commit,
         generated=datetime.datetime.now().isoformat(timespec='seconds'), command='bash docs/review/v005/run_v005.sh %s' % A.commit,
         exit_code=len(fails), items=items)
json.dump(R, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('조건 2 항목 %d · 불합격 %d · 사람 확인 %d' % (len(items), len(fails), sum(1 for i in items if not i['verifiable'])))
sys.exit(len(fails))
