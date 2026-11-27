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
ap.add_argument('--d003', default=None, help='D-003 문서 — #62(MDI TX 쌍 안 길이 차 예외) 한도를 이 행에서 읽는다')
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


# O-119 / D-003 #62: 캐리어 MDI TX 쌍만 쌍 안 길이 차 예외. 한도는 #62 행의 「≤N mm」에서 읽는다 — 행이 없거나 「MDI TX」가 없으면 예외 없음(#28 「0」)
TX_DIFF_MAX = None
if A.d003 and os.path.exists(A.d003):
    for _l in open(A.d003, encoding='utf-8'):
        if re.match(r'\|\s*62\s*\|', _l) and 'MDI TX' in _l:
            _m = re.search(r'쌍 안 길이 차\s*≤\s*([\d.]+)\s*mm', _l)
            TX_DIFF_MAX = float(_m.group(1)) if _m else None


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
        for k, p in ru.get('pairs', {}).items():
            if b == 'carrier' and k == '/EPHY_TX' and TX_DIFF_MAX is not None:
                add('2.A8', b, '쌍 안 길이 차 %s (MDI TX 예외)' % k, p['diff'], '≤%g (D-003 #62, #28 예외)' % TX_DIFF_MAX, p['diff'] <= TX_DIFF_MAX + 1e-6, [frr])
            else:
                add('2.A8', b, '쌍 안 길이 차 %s' % k, p['diff'], '≤0.025 (D-003 #28 「0」)', p['diff'] <= 0.025, [frr])
            s = p['strict_0.18']
            if p['cls'] == 'MDI_100' and 'uncoupled_outside_twist' in p:
                o = max(p['uncoupled_outside_twist'].values())
                ar = p.get('uncoupled_area_rule')
                add('2.A10', b, '비결합(꼬임 밖, 쌍 간격 0.18 이하만 결합) %s' % k, o, '≤%g' % lim['MDI_100'], o <= lim['MDI_100'] + 1e-6, [frr],
                    ('참고: 탈출·보정 영역 간격(D-003 #46 DP_BRK 2.2 · DP_TUNE 1.0)을 결합으로 보면 %g' % max(ar['P'], ar['N'])) if ar else '')
                add('2.A10t', b, '비결합(꼬임 포함) %s' % k, s['uncoupled_max'], '≤%g' % twist_lim, s['uncoupled_max'] <= twist_lim + 1e-6, [frr])
            else:
                add('2.A10', b, '비결합 %s' % k, s['uncoupled_max'], '≤%g' % lim[p['cls']], s['uncoupled_max'] <= lim[p['cls']] + 1e-6, [frr])
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
            add('2.V1', b, '비아 0.65/0.30 미만은 J1 탈출 영역 안에만, 열·GND 이음 비아는 0.60/0.30 허용 (D-003 #21·#60) — 그 밖의 작은 비아', len(ev_['outside_small']), 0, not ev_['outside_small'], [frr],
                '; '.join(sorted(set('%s/%s %s' % (v['dia'], v['drill'], v['net']) for v in ev_['outside_small']))[:8]) + (' · 걸침 %d' % len(ev_['straddle_small']) if ev_['straddle_small'] else '')
                + ' · 0.60/0.30 허용분: GND %d, 열 %d' % (sum(1 for v in ev_.get('allowed_060', []) if v['kind'] == 'GND'), sum(1 for v in ev_.get('allowed_060', []) if v['kind'] == '열')))
            if an or ev_['inside']:
                inter = sorted(set(re.findall(r"intersectsArea\('(%s[^']*)'\)" % re.escape(ev_['prefix']), t)))
                encl = sorted(set(re.findall(r"enclosedByArea\('(%s[^']*)'\)" % re.escape(ev_['prefix']), t)))
                add('2.V2', b, 'J1 탈출 규칙이 enclosedByArea 뿐 (영역 %s)' % (', '.join(an) or '없음'), len(inter), 0, bool(encl) and not inter, [frr],
                    ('intersectsArea 규칙: ' + ', '.join(inter)) if inter else ('enclosedByArea: ' + (', '.join(encl) or '규칙 없음')))
                add('2.V3', b, '영역 안 작은 비아 %d개: 지름 ≥0.50 · 드릴 ≥0.20 · 링 ≥0.15 · 구멍 간격 ≥0.28' % len(ev_['inside']), len(ev_['inside_fail']), 0,
                    not ev_['inside_fail'], [frr], '; '.join('%s %s' % (v['at'], ','.join(v['why'])) for v in ev_['inside_fail'][:8]))
                add('2.V4', b, '영역 안 작은 비아는 J1 핀 넷뿐', len(ev_['non_j1_net']), 0, not ev_['non_j1_net'], [frr],
                    ', '.join(sorted(set(v['net'] for v in ev_['non_j1_net']))))
                far = [a for a in ev_['areas'] if not a['beyond_ok']]
                add('2.V5', b, '탈출 영역이 J1 둘레 안 (J1 외곽 상자 + 3.0 [가정])', max([a['beyond_j1'] or 0 for a in ev_['areas']] or [0]), '≤3.0', bool(an) and not far, [frr])
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

fails = [i for i in items if i['verifiable'] and i['pass'] is False]
R = dict(cond='2', owner='review', title='PCB DRC·미연결·parity·완화 기록·V-005 최종', commit=A.commit,
         generated=datetime.datetime.now().isoformat(timespec='seconds'), command='bash docs/review/v005/run_v005.sh %s' % A.commit,
         exit_code=len(fails), items=items)
json.dump(R, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('조건 2 항목 %d · 불합격 %d · 사람 확인 %d' % (len(items), len(fails), sum(1 for i in items if not i['verifiable'])))
sys.exit(len(fails))
