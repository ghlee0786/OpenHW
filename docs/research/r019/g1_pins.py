"""R-019 G1: BTB 60핀 3자 대조 (코어 SCH 07 판독 · Seeed 짝 보드 KiCad · 우리 보드 PCB) + 계약 v1.11 대조 → CSV.

실행: python -I g1_pins.py <scratch dir> <out.csv>
입력(scratch): g_poe.json, g_s401.json, g_our_carrier.json, g_our_front.json (padglobal.py 산출), contract_pins.json
"""
import csv
import json
import sys

S, OUT = sys.argv[1], sys.argv[2]
NC = 'NC'
# 코어 회로도 PDF 8쪽(Sheet /07 BTB Connector, Rev V1.0 2024-04-25) 판독. 레일(VIN·+1V8·+3V3)은 선 연결을 그림에서 판독.
CORE_J1 = {1: 'GND', 3: 'CAM_RX0_4N', 5: 'CAM_RX0_4P', 7: 'GND', 9: 'CAM_RX0_CLKN', 11: 'CAM_RX0_CLKP', 13: 'GND',
           15: 'CAM_RX0_0N', 17: 'CAM_RX0_0P', 19: 'GND', 21: 'CAM_RX0_1N', 23: 'CAM_RX0_1P', 25: 'GND',
           27: 'CAM_RX0_3N', 29: 'CAM_RX0_3P', 31: 'GND', 33: 'GPIO15/IR_CUT', 35: 'GND', 37: 'GND', 39: 'AUD_MIC',
           41: 'GND', 43: 'AUD_AOUTR', 45: 'GND', 47: 'CAM_EN',
           2: 'RESERVE2', 4: 'RESERVE1', 6: 'WH_PWM', 8: 'GND', 10: 'CAM_I2C2_SCL', 12: 'CAM_I2C2_SDA', 14: 'GND',
           16: 'IR_PWM', 18: 'LIGHT_SENSE', 34: 'GND', 36: 'GND', 38: 'VIN', 40: 'VIN', 42: 'VIN', 44: 'VIN',
           46: 'GND', 48: 'GND', 50: '+1V8', 52: '+1V8', 54: 'GND', 56: 'GND', 58: '+3V3', 60: '+3V3'}
for n in list(range(20, 33, 2)) + list(range(49, 60, 2)):
    CORE_J1[n] = NC
CORE_J2 = {1: 'EPHY_TXP', 3: 'EPHY_TXN', 5: 'GND', 7: 'EPHY_RXP', 9: 'EPHY_RXN', 11: 'GND', 13: 'USB_DET',
           15: 'MIPI_TXM2/IIC1_SDA/PWM', 17: 'MIPI_TXP2/IIC1_SCL/PWM', 19: 'MIPI_TXM1/IIC2_SDA/PWM',
           21: 'MIPI_TXP1/IIC2_SCL/PWM', 23: 'MIPI_TXM0/GPIO12/PWM', 25: 'MIPI_TXM0/WL_BT_EN/GPIOC13 (R14 DNP 표시)',
           27: 'GND', 29: 'GND', 31: 'PWR_WAKEUP1', 33: 'nRESET', 35: 'UPGRAD_KEY', 37: 'SD0_PWR_EN', 39: 'SDIO0_D3',
           41: 'SDIO0_D2', 43: 'SDIO0_D1', 45: 'SDIO0_D0', 47: 'SDIO0_CMD', 49: 'GND', 51: 'SDIO0_CLK', 53: 'GND',
           55: 'SDIO0_CD', 57: 'DEBUG_UART0_TX', 59: 'DEBUG_UART0_RX',
           2: 'USB_DN', 4: 'USB_DP', 6: 'GND', 8: 'RESERVE1', 10: 'RESERVE2', 12: 'SD1_CLK (R48 DNP 표시)', 14: 'GND',
           16: 'SD1_CMD (R49 DNP 표시)', 18: 'SD1_D0 (R50 DNP 표시)', 20: 'SD1_D1 (R51 DNP 표시)',
           22: 'SD1_D2 (R52 DNP 표시)', 24: 'SD1_D3 (R53 DNP 표시)', 26: 'GND', 28: '+3V3', 30: 'VIN', 32: 'VIN',
           34: 'VIN', 36: 'VIN', 54: 'BT_UART1_RX (R68 DNP 표시)', 56: 'BT_UART1_TX (R67 DNP 표시)',
           58: 'BT_UART1_CTS (R70 DNP 표시)', 60: 'BT_UART1_RTS (R69 DNP 표시)'}
for n in range(38, 53, 2):
    CORE_J2[n] = NC


def norm(s):
    s = s.lstrip('/').replace('{slash}', '/')
    if s.startswith('unconnected') or s == '':
        return NC
    s = s.split(' (')[0]
    return {'+3V3': '3V3', '+1V8': '1V8', 'SDIO0_D3': 'SDIO_D3', 'SDIO0_D2': 'SDIO_D2', 'SDIO0_D1': 'SDIO_D1',
            'SDIO0_D0': 'SDIO_D0', 'SDIO0_CMD': 'SDIO_CMD', 'SDIO0_CLK': 'SDIO_CLK', 'SDIO0_CD': 'SDIO_CD'}.get(s, s).replace('/3V3', '')


def nets(name):
    d = json.load(open(f'{S}/g_{name}.json', encoding='utf-8'))
    return {int(n): net for n, x, y, net, a in d['J1']['pads'] if n}


contract = json.load(open(f'{S}/contract_pins.json', encoding='utf-8'))
rows, summary = [], {}
for board, seeed, ours, core, corename in (('carrier', 'poe', 'our_carrier', CORE_J2, 'J2'),
                                          ('front', 's401', 'our_front', CORE_J1, 'J1')):
    A, B = nets(seeed), nets(ours)
    for p in range(1, 61):
        cp = p + 1 if p % 2 else p - 1
        c = core.get(cp, '?')
        sa, ob = A.get(p, ''), B.get(p, '')
        ct = contract[board].get(str(p), {})
        mate_ok = norm(sa) == norm(c)
        if norm(ob) == norm(sa):
            j = '일치'
        elif norm(ob) in ('5V_SYS', 'CORE_3V3', 'CORE_1V8') and norm(sa) in ('VIN', '3V3', '1V8', '+3V3'):
            j = '일치(전원 이름만 다름)'
        elif norm(ob) == NC:
            j = '의도된 미사용(NC)'
        elif norm(sa).replace('BT_', '') == norm(ob) or norm(sa).endswith('/' + norm(ob)) or norm(ob) in norm(sa):
            j = '일치(이름만 다름)'
        else:
            j = '재배정(계약)'
        ct_net = ct.get('net', '')
        ct_ok = '계약 행 있음' if ct else '계약 행 없음'
        rows.append([board, p, corename, cp, c, sa.replace('{slash}', '/'), ob.lstrip('/'), ct_net, ct.get('use', ''),
                     ct.get('line', ''), '예' if mate_ok else '아니오', j])
        summary.setdefault(board, {}).setdefault(j, 0)
        summary[board][j] += 1
        if not mate_ok:
            summary[board].setdefault('Seeed짝≠코어', []).append(p)
w = csv.writer(open(OUT, 'w', encoding='utf-8-sig', newline=''), lineterminator='\n')
w.writerow(['보드', '짝 핀', '코어 커넥터', '코어 핀(n±1)', '코어 SCH 07 넷(판독)', 'Seeed 짝 보드 넷(KiCad)', '우리 PCB 넷',
            '계약 v1.11 넷', '계약 용도', '계약 줄', 'Seeed짝=코어', '판정'])
w.writerows(rows)
print(json.dumps(summary, ensure_ascii=False))
