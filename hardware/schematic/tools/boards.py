import sys, os, json, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from schgen import Sheet, R, C, TP

OUT = sys.argv[1]            # .../hardware/schematic
LIB = sys.argv[2]            # .../hardware/libraries
NETX = sys.argv[3]           # dir with b101.xml / s401.xml (kicad-cli netlists of Seeed reference, facts only)
LOCAL = {'openhw': f'{LIB}/openhw.kicad_sym'}

def btb_nets(xml, ref='J1'):
    t = ET.parse(xml).getroot(); m = {}
    for n in t.iter('net'):
        for nd in n.iter('node'):
            if nd.get('ref') == ref: m[nd.get('pin')] = n.get('name')
    return m

report = {}
# ======================= CARRIER =======================
s = Sheet('carrier', 'OpenHW carrier board (rear) - reCamera Core 2002 J2 mate', LOCAL, power=('GND','12V_IN','5V_SYS','12V_IR','CORE_3V3','SD_PWR_3V3','CHASSIS'))
s.block('BTB','코어 BTB (J2 짝, ST-BTB-058060-A / HCTL)',['계약 4절 핀맵 · 짝 핀 홀짝 반전 · VIN 4핀 = 5V_SYS 피크 1.3A (핀당 0.33A, 정격 미확인 → O-17 게이트)','고속: EPHY MDI 100R · USB 90R · SDIO0 3.3V (P-002 넷클래스)'],cols=1)
ren = {'VIN': '5V_SYS', '+3V3': 'CORE_3V3', 'MIPI_TXM2/IIC1_SDA/PWM': 'I2C1_SDA', 'MIPI_TXP2/IIC1_SCL/PWM': 'I2C1_SCL',
       'MIPI_TXM1/IIC2_SDA/PWM': 'SPARE1', 'MIPI_TXP1/IIC2_SCL/PWM': 'IR_LED_EN', 'MIPI_TXM0/GPIO12/PWM': 'STATUS_LED',
       'PWR_WAKEUP1': 'ALS_INT_RSV', 'BT_UART1_RX': 'UART1_RX', 'BT_UART1_TX': 'UART1_TX', 'BT_UART1_CTS': 'UART1_CTS', 'BT_UART1_RTS': 'UART1_RTS'}
bm = btb_nets(f'{NETX}/b101.xml')
nets = {}
for p in range(1, 61):
    n = bm.get(str(p), '')
    if n.startswith('unconnected') or n.startswith('SD1_') or 'GPIO13' in n: continue   # NC flag
    if n == 'PWR_WAKEUP1': continue   # C-016/O-83: core wake input left unconnected (ALS is i2c-dev polled, D-003 #18)
    n = ren.get(n, n).replace('/3V3', '')
    nets[str(p)] = n
s.add('J1', 'Connector_Generic:Conn_02x30_Odd_Even', 'HC-PBB05-2-60-M-H4.0 (ST-BTB-058060-A)', 'openhw:BTB_ST-BTB-058060-A_2x30_P0.5mm', nets,
      fields={'MPN': 'HCTL HC-PBB05-2-60-M-H4.0-G1-R-P-04 / alt SUNGTECH ST-BTB-058060-A', 'Note': 'mates core J2; O-17 gate: physical mating check before order'})
report['carrier_btb'] = nets
s.block('PIN','12V 입력 · 보호',['DC 12V (GST25A12 2.08A) → F1 3A → Q1 역접 P-FET → D2 SMBJ15A (클램프 24.4V)','12V_IN 최악 1.84A (계약 3.2절 v1.2)'],cols=4)
# --- 12V input & protection
s.add('J2', 'Connector:Barrel_Jack_Switch', 'DC-005-5A-2.0', 'openhw:BarrelJack_XKB_DC-005-5A-2.0_Horizontal', {'1': '12V_IN_RAW', '2': 'GND'},
      fields={'MPN': 'XKB DC-005-5A-2.0 (LCSC C381116)', 'Note': 'C-004 R6: dedicated footprint 1-2 5.90, pin3 3.0/4.70, slot 1.0x3.5'})
s.add('F1', 'Device:Fuse', '3A slow-blow 63V', 'Fuse:Fuse_1206_3216Metric', {'1': '12V_IN_RAW', '2': '12V_IN_F'}, fields={'MPN': 'Bel Fuse 0685T3000-01 (1206 Slow Blow 3A 63V, V-004b R12)'})
s.add('Q1', 'Transistor_FET:FDS9435A', 'AO4407A', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {'1': '12V_IN', '2': '12V_IN', '3': '12V_IN', '4': 'Q1_G', '5': '12V_IN_F', '6': '12V_IN_F', '7': '12V_IN_F', '8': '12V_IN_F'},
      fields={'MPN': 'AOS AO4407A (LCSC C16072)', 'Note': 'reverse-polarity P-FET, symbol FDS9435A has same SSSGDDDD pinout'})
R(s, 'R1', '100k', 'Q1_G', 'GND')
s.add('D1', 'Device:D_Zener', 'BZT52C12', 'Diode_SMD:D_SOD-123', {'1': '12V_IN', '2': 'Q1_G'}, fields={'Note': 'Vgs clamp 12V (AO4407A Vgs max +-25V per V-004 R12, TVS clamp 24.4V)'})
s.add('D2', 'Device:D_Zener', 'SMBJ15A', 'Diode_SMD:D_SMB', {'1': '12V_IN', '2': 'GND'}, fields={'MPN': 'Littelfuse SMBJ15A (LCSC C83846)', 'Note': 'unidirectional TVS, K=1 (V-004 R7)'})
s.add('C1', 'Device:C_Polarized', '47uF/35V', 'Capacitor_SMD:CP_Elec_6.3x5.4', {'1': '12V_IN', '2': 'GND'}, fields={'Note': '35V recommended (V-004 R12); MPN with ripple rating pending (R-004)'})
C(s, 'C2', '10uF/25V', '12V_IN', 'GND', 'Capacitor_SMD:C_1206_3216Metric')
s.block('BUCK','5V 강압 TPS54302 (5V_SYS → 코어 VIN)',['Vout = 0.596 x (1 + 100k/13.3k) = 5.08V · 3A급, 예산 피크 1.3A (계약 3.1절)','TI SLVSDG6C 7.2 예: L 10uH, EN 개방 = 켬'],cols=5)
# --- 5V buck TPS54302 (TI SLVSDG6C 7.2 example: 100k/13.3k, 10uH, EN float)
s.add('U1', 'Regulator_Switching:TPS54302', 'TPS54302DDCR', 'Package_TO_SOT_SMD:SOT-23-6',
      {'1': 'GND', '2': 'BUCK_SW', '3': '12V_IN', '4': 'BUCK_FB', '6': 'BUCK_BOOT'}, fields={'MPN': 'TI TPS54302DDCR (LCSC C311983)', 'Note': 'EN floating = enabled (SLVSDG6C 6.3.x)'})
C(s, 'C3', '10uF/25V', '12V_IN', 'GND', 'Capacitor_SMD:C_1206_3216Metric')
C(s, 'C4', '10uF/25V', '12V_IN', 'GND', 'Capacitor_SMD:C_1206_3216Metric')
C(s, 'C5', '100nF/50V', '12V_IN', 'GND')
C(s, 'C6', '100nF', 'BUCK_BOOT', 'BUCK_SW')
s.add('L1', 'Device:L', '10uH Isat>=6A', 'Inductor_SMD:L_Bourns_SRP7028A_7.3x6.6mm', {'1': 'BUCK_SW', '2': '5V_SYS'}, fields={'Note': 'height 2.8mm (carrier top limit 6.2, M-001b)'})
R(s, 'R2', '78.7k 1%', '5V_SYS', 'BUCK_FB')  # C-019/O-93 P1 (was 100k)
R(s, 'R3', '10.7k 1%', 'BUCK_FB', 'GND')  # C-019/O-93 P1 (was 13.3k): VFB +-2.5% x R +-1% worst inside 4.75..5.25V
C(s, 'C19', '75pF C0G 50V', '5V_SYS', 'BUCK_FB')
C(s, 'C7', '22uF/25V X7R', '5V_SYS', 'GND', 'Capacitor_SMD:C_1210_3225Metric')
C(s, 'C8', '22uF/25V X7R', '5V_SYS', 'GND', 'Capacitor_SMD:C_1210_3225Metric')
C(s, 'C20', '22uF/25V X7R', '5V_SYS', 'GND', 'Capacitor_SMD:C_1210_3225Metric')
s.add('C23', 'Device:C', '22uF/25V X7R', 'Capacitor_SMD:C_1210_3225Metric', {'1': '5V_SYS', '2': 'GND'}, fields={'MPN': 'Samsung CL32B226KAJNNNE', 'Note': 'C-007/O-37: 4th output cap, DC-bias+tol worst ~40uF with 3 < TI 44uF (R-008b)'})
s.add('D7', 'Device:D_Zener', 'SMBJ6.0A', 'Diode_SMD:D_SMB', {'1': '5V_SYS', '2': 'GND'}, fields={'MPN': 'SMBJ6.0A (VRWM 6.0V > Vout max 5.30V, V-004b R5)', 'Note': 'unidirectional TVS, K=1'})
s.add('D3', 'Device:LED', 'PWR green', 'LED_SMD:LED_0603_1608Metric', {'2': 'PWR_LED_A', '1': 'GND'})
R(s, 'R4', '2.2k', '5V_SYS', 'PWR_LED_A')
s.block('EFUSE','12V_IR eFuse TPS26600 (IR LED 전원)',['SHDN = IR_LED_EN (1.8V GPIO, 10k 풀다운 = 기본 끔) · UVLO = IN · OVP/MODE/RTN = GND (O-21)','ILIM 6.04k = 약 1.99A (C-018/O-91: 12V_IR 피크 1.585A×1.15 ≤ I(OL) 최소 1.86A, 분기 C2-4) · dVdT 22nF'],cols=4)
# --- 12V_IR eFuse TPS26600 (O-21, V-002: SHDN + 10k pulldown, UVLO=IN, OVP/MODE=RTN, ILIM per 2 strings)
s.add('U2', 'Power_Management:TPS26600PWP', 'TPS26600PWPR', 'Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm',  # C-018/O-86 #21: thermal vias placed by pcb (d0.3)
      {'1': '12V_IN', '2': '12V_IN', '3': '12V_IN', '5': 'GND', '7': 'IR_LED_EN', '8': 'GND', '9': 'GND', '11': 'EFUSE_ILIM', '12': 'EFUSE_DVDT', '15': '12V_IR', '16': '12V_IR', '17': 'GND'},
      fields={'MPN': 'TI TPS26600PWPR (LCSC C544399)', 'Note': 'UVLO=IN (no UVLO); OVP=RTN internal 33V; MODE open = circuit-breaker + auto-retry (C-004 C4-6); RTN=GND allowed (SLVSDG2G, reverse polarity handled by Q1); FLT/IMON unused (leave floating per datasheet)'})
R(s, 'R5', '10k', 'IR_LED_EN', 'GND')
R(s, 'R6', '6.04k 1%', 'EFUSE_ILIM', 'GND')  # C-018/O-91 (8.06k -> C-017 6.98k -> 6.04k)
C(s, 'C9', '22nF', 'EFUSE_DVDT', 'GND')
C(s, 'C10', '1uF/25V', '12V_IN', 'GND', 'Capacitor_SMD:C_0603_1608Metric')
C(s, 'C11', '10uF/25V', '12V_IR', 'GND', 'Capacitor_SMD:C_1206_3216Metric')
s.block('USB','USB-C (디바이스, 데이터 + VBUS 검출)',['VBUS는 5V_SYS와 분리 (계약 C4) · USB_DET = VBUS / 3 (20k/10k)','D+/D- 90R (USB_90)'],cols=4)
# --- USB-C device (data + VBUS detect only, contract C4)
s.add('J3', 'Connector:USB_C_Receptacle_USB2.0_16P', 'USB-C 16P', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
      {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'A4': 'USB_VBUS', 'A9': 'USB_VBUS', 'B4': 'USB_VBUS', 'B9': 'USB_VBUS',
       'A5': 'USB_CC1', 'B5': 'USB_CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DN', 'B7': 'USB_DN', 'SH': 'GND'}, fields={'Note': 'not in R-004 BOM yet; VBUS not tied to 5V_SYS (C4)'})
R(s, 'R7', '5.1k', 'USB_CC1', 'GND'); R(s, 'R8', '5.1k', 'USB_CC2', 'GND')
s.add('U3', 'Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', 'Package_TO_SOT_SMD:SOT-23-6', {'1': 'USB_DP', '6': 'USB_DP', '3': 'USB_DN', '4': 'USB_DN', '2': 'GND', '5': 'USB_VBUS'})
R(s, 'R9', '200k', 'USB_VBUS', 'USB_DET'); R(s, 'R10', '100k', 'USB_DET', 'GND')
C(s, 'C22', '10nF', 'USB_DET', 'GND')
C(s, 'C12', '1uF', 'USB_VBUS', 'GND')
s.block('SD','microSD (SDIO0, 3.3V 전용)',['SD0_PWR_EN High = 켬 (gpio494) · CD = gpio493 (계약 7절)','R13~R17 풀업 DNP · U4/U5 ESD'],cols=4)
# --- microSD (SD0, 3.3V only, B101-equivalent power switch re-drawn)
s.add('J4', 'Connector:Micro_SD_Card_Det_Hirose_DM3AT', 'DM3AT-SF-PEJM5', 'Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5',
      {'1': 'SDIO_D2', '2': 'SDIO_D3', '3': 'SDIO_CMD', '4': 'SD_PWR_3V3', '5': 'SDIO_CLK', '6': 'GND', '7': 'SDIO_D0', '8': 'SDIO_D1', '9': 'SDIO_CD', '10': 'GND', 'SH': 'GND'},
      fields={'Note': 'R-004 BOM rep is SHOU HAN TF PUSH (C393941); Hirose DM3AT is R-004 alternative with official KiCad footprint (branch C2-1)'})
s.add('Q2', 'Transistor_FET:AO3401A', 'AO3401A', 'Package_TO_SOT_SMD:SOT-23', {'1': 'SD_PWR_G', '2': 'CORE_3V3', '3': 'SD_PWR_3V3'})
R(s, 'R11', '100k', 'CORE_3V3', 'SD_PWR_GD')
s.add('Q3', 'Transistor_FET:DMG1012T', 'DMG1012T', 'Package_TO_SOT_SMD:SOT-523', {'1': 'SD0_PWR_EN', '2': 'GND', '3': 'SD_PWR_GD'})
R(s, 'R22', '47k', 'SD_PWR_GD', 'SD_PWR_G')
C(s, 'C21', '100nF', 'SD_PWR_G', 'CORE_3V3')
R(s, 'R12', '100k', 'SD0_PWR_EN', 'GND')
C(s, 'C13', '1uF', 'SD_PWR_3V3', 'GND', 'Capacitor_SMD:C_0603_1608Metric')
R(s, 'R23', '100k', 'SD_PWR_3V3', 'GND')
C(s, 'C14', '100nF', 'SD_PWR_3V3', 'GND')
for i, n in enumerate(['SDIO_CMD', 'SDIO_D0', 'SDIO_D1', 'SDIO_D2', 'SDIO_D3']):
    R(s, f'R{13+i}', '47k', 'SD_PWR_3V3', n, dnp=True)
s.add('U4', 'Power_Protection:TPD4E05U06DQA', 'TPD4E05U06DQA', 'Package_SON:USON-10_2.5x1.0mm_P0.5mm', {'1': 'SDIO_CLK', '2': 'SDIO_CMD', '4': 'SDIO_D0', '5': 'SDIO_D1', '3': 'GND', '8': 'GND'})
s.add('U5', 'Power_Protection:TPD4E05U06DQA', 'TPD4E05U06DQA', 'Package_SON:USON-10_2.5x1.0mm_P0.5mm', {'1': 'SDIO_D2', '2': 'SDIO_D3', '4': 'SDIO_CD', '3': 'GND', '8': 'GND'})
s.block('ETH','이더넷 HR911105A (내장 마그네틱)',['EPHY MDI 100R (MDI_100) · 센터탭 C15/C16 DNP (R-004 P6)','실드 CHASSIS = 1M || 1nF/2kV → GND'],cols=4)
# --- Ethernet HR911105A (EPHY MDI direct, CT caps DNP per R-004 P6)
s.add('J5', 'Connector:RJ45_Hanrun_HR911105A_Horizontal', 'HR911105A', 'Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal',
      {'1': 'EPHY_TXP', '2': 'EPHY_TXN', '3': 'EPHY_RXP', '6': 'EPHY_RXN', '4': 'MDI_TCT', '5': 'MDI_RCT', '8': 'GND', 'SH': 'CHASSIS'},
      fields={'MPN': 'HanRun HR911105A (LCSC C12074)', 'Note': 'LED pins 9-12 unused; pin 8 per KiCad symbol (power)'})
C(s, 'C15', '100nF', 'MDI_TCT', 'GND', dnp=True); C(s, 'C16', '100nF', 'MDI_RCT', 'GND', dnp=True)
s.add('D4', 'Device:D_TVS', 'UDD32C03L01', 'Diode_SMD:D_SOD-323', {'1': 'EPHY_TXP', '2': 'EPHY_TXN'})
s.add('D5', 'Device:D_TVS', 'UDD32C03L01', 'Diode_SMD:D_SOD-323', {'1': 'EPHY_RXP', '2': 'EPHY_RXN'})
R(s, 'R18', '1M', 'CHASSIS', 'GND', 'Resistor_SMD:R_0603_1608Metric')
C(s, 'C17', '1nF/2kV', 'CHASSIS', 'GND', 'Capacitor_SMD:C_1206_3216Metric')
s.block('MISC','보드 간 커넥터 · 디버그 UART · 버튼 · 상태 LED',['보드 간 JST GH 6P 대칭 (계약 12A절 v1.3): 1/6 GND · 2/5 12V_IR · 3 SPARE1 · 4 ALS_INT_RSV','디버그 TX = 부트 스트랩 (풀다운·LED 금지) · UPGRAD_KEY 직렬 1k (C16)'],cols=4)
# --- debug UART header (JST SH 3P, height < 6.2)
s.add('J6', 'Connector_Generic_MountingPin:Conn_01x03_MountingPin', 'DEBUG UART', 'Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal',
      {'1': 'GND', '2': 'DEBUG_UART0_TX', '3': 'DEBUG_UART0_RX', 'MP': 'GND'}, fields={'Note': 'no pull-down/LED on TX (boot strap)'})
# --- buttons
s.add('SW1', 'Switch:SW_Push', 'RESET', 'Button_Switch_SMD:SW_SPST_PTS810', {'1': 'nRESET', '2': 'GND'})
s.add('SW2', 'Switch:SW_Push', 'UPGRADE', 'Button_Switch_SMD:SW_SPST_PTS810', {'1': 'UPGRAD_KEY_SW', '2': 'GND'})
R(s, 'R19', '1k', 'UPGRAD_KEY', 'UPGRAD_KEY_SW')
C(s, 'C18', '10nF', 'UPGRAD_KEY', 'GND')
# --- status LED (1.8V GPIO -> low-Vth NMOS)
s.add('Q4', 'Transistor_FET:DMG1012T', 'DMG1012T', 'Package_TO_SOT_SMD:SOT-523', {'1': 'STATUS_LED', '2': 'GND', '3': 'STAT_LED_K'})
R(s, 'R20', '100k', 'STATUS_LED', 'GND')
s.add('D6', 'Device:LED', 'STATUS blue', 'LED_SMD:LED_0603_1608Metric', {'2': 'STAT_LED_A', '1': 'STAT_LED_K'})
R(s, 'R21', '1.5k', '5V_SYS', 'STAT_LED_A')
# --- FPC 10P to front board (symmetric pinout, contract v1.2 12)
fpc = {'1': 'GND', '2': '12V_IR', '3': 'SPARE1', '4': 'ALS_INT_RSV', '5': '12V_IR', '6': 'GND', 'MP': 'GND'}
s.add('J7', 'Connector_Generic_MountingPin:Conn_01x06_MountingPin', 'JST GH 6P (board link)', 'Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal', fpc,
      fields={'MPN': 'JST SM06B-GHS-TB', 'Cable': 'JST GHR-06V-S + SSHL-002T-P0.2 AWG26, 1:1 (V-004 C1)', 'Note': 'C-003 C3-1: 1.0A/contact AWG26 (JST eGH); 12V_IR on 2 contacts, symmetric pinout'})
report['fpc'] = fpc
s.block('TP','시험점 (계약 11절)',cols=9)
# --- test points
for i, n in enumerate(['12V_IN', '5V_SYS', '12V_IR', 'CORE_3V3', 'SD_PWR_3V3', 'GND', 'GND', 'USB_DP', 'USB_DN', 'USB_DET', 'nRESET', 'UPGRAD_KEY',
                       'STATUS_LED', 'IR_LED_EN', 'SPARE1', 'I2C1_SDA', 'I2C1_SCL', 'RESERVE1', 'RESERVE2', 'UART1_RX', 'UART1_TX', 'UART1_CTS', 'UART1_RTS',
                       'DEBUG_UART0_TX', 'DEBUG_UART0_RX', 'ALS_INT_RSV']):
    TP(s, f'TP{i+1}', n)
os.makedirs(f'{OUT}/carrier', exist_ok=True)
report['carrier'] = s.write(f'{OUT}/carrier/carrier.kicad_sch')

# ======================= FRONT =======================
f = Sheet('front', 'OpenHW front (sensor) board - reCamera Core 2002 J1 mate', LOCAL, power=('GND','VIN','12V_IR','CORE_3V3','CORE_1V8','FRONT_2V8','CAM_1V8'))
fm = btb_nets(f'{NETX}/s401.xml')
f.block('BTB','코어 BTB (J1 짝, ST-BTB-058060-B / HCTL, 전면 보드 아랫면)',['계약 5절 핀맵 · CSI 2레인 (CLK=RX2, D0=RX0, D1=RX3) 100R · I2C2 1.8V','VIN 4핀 (코어 5V) · CORE_1V8 300mA · CORE_3V3 1A (코어와 공유)'],cols=1)
fren = {'VIN': 'VIN', '1V8': 'CORE_1V8', '3V3': 'CORE_3V3', 'GPIO15/IR_CUT': 'IR_CUT'}
nets = {}
for p in range(1, 61):
    n = fm.get(str(p), '')
    if n.startswith('unconnected') or n.startswith('AUD_') or n.startswith('RESERVE') or n.startswith('CAM_RX0_3') or n.startswith('CAM_RX0_4'): continue
    nets[str(p)] = fren.get(n, n)
f.add('J1', 'Connector_Generic:Conn_02x30_Odd_Even', 'HC-PBB05-2-60-F-H4.0 (ST-BTB-058060-B)', 'openhw:BTB_ST-BTB-058060-B_2x30_P0.5mm', nets,
      fields={'MPN': 'HCTL HC-PBB05-2-60-F-H4.0-G1-R-P-04 / alt SUNGTECH ST-BTB-058060-B', 'Note': 'mates core J1 (bottom side of front board); O-17 gate'})
report['front_btb'] = nets
f.block('LDO','전면 2.8V LDO (RT9013-28, C-004 R9)',['VIN 5V → FRONT_2V8 (DRV8837 VCC: VIH max 0.5×2.8 = 1.4V → 1.8V GPIO 여유 0.4V · LTR-329 VDD 2.4~3.6V)'],cols=4)
# --- front 3.3V LDO (RT9013-33GB; AP2112K symbol has same SOT-23-5 pinout 1 VIN 2 GND 3 EN 5 VOUT)
f.add('U1', 'Regulator_Linear:AP2112K-3.3', 'RT9013-28GB', 'Package_TO_SOT_SMD:SOT-23-5', {'1': 'VIN', '2': 'GND', '3': 'VIN', '5': 'FRONT_2V8'},
      fields={'MPN': 'Richtek RT9013-28GB (stock check pending)', 'Note': 'symbol AP2112K has same SOT-23-5 pinout; pin4 = NC (DS9013, V-004 R12)'})
C(f, 'C1', '1uF', 'VIN', 'GND'); C(f, 'C2', '1uF', 'FRONT_2V8', 'GND')
f.block('ICR','ICR 구동 DRV8837 + CLA216-ICR',['VM = VIN 5V · VCC = 2.8V (C-004 R9) · IN1 = IR_CUT (gpio495) · IN2 = WH_PWM (gpio352)','코일 20R 약 0.245A, 펄스 100~500ms (FW) · 기본 IN1 = IN2 = 0 (계약 C13)'],cols=4)
# --- ICR driver DRV8837 (C13): VM=VIN 5V, VCC=FRONT_3V3, IN1=IR_CUT, IN2=WH_PWM
f.add('U2', 'Driver_Motor:DRV8837', 'DRV8837DSGR', 'openhw:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm',
      {'1': 'VIN', '2': 'ICR_A', '3': 'ICR_B', '4': 'GND', '5': 'WH_PWM', '6': 'IR_CUT', '7': 'ICR_NSLEEP', '8': 'FRONT_2V8', '9': 'GND'},
      fields={'MPN': 'TI DRV8837DSGR (LCSC C39159)', 'Note': 'openhw copy of official land with installed WSON-8 STEP (C-003)'})
R(f, 'R1', '10k', 'FRONT_2V8', 'ICR_NSLEEP')
C(f, 'C3', '10uF', 'VIN', 'GND', 'Capacitor_SMD:C_0603_1608Metric'); C(f, 'C4', '100nF', 'VIN', 'GND'); C(f, 'C5', '100nF', 'FRONT_2V8', 'GND')
R(f, 'R2', '100k', 'IR_CUT', 'GND'); R(f, 'R3', '100k', 'WH_PWM', 'GND')
f.add('J2', 'Connector_Generic:Conn_01x02', 'CLA216 lead solder pads 2P 2.54mm', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
      {'1': 'ICR_A', '2': 'ICR_B'}, in_bom=False,
      fields={'MPN': '- (solder pads only, no header fitted; excluded from BOM/CPL)', 'Note': 'C-016/O-84: CLA216 leads soldered directly (connector family not identifiable from official data). pin1 (square pad) = ICR_A = red(+) assumed: IN1=1 pulse -> filter open (night), IN2=1 -> closed (day); polarity check on hardware'})
f.add('MH1', 'Mechanical:MountingHole', 'CLA216-ICR M12 holder', 'openhw:M12_Holder_20mm_CLA216-ICR', {}, fields={'MPN': 'Commonlands CLA216-ICR'})
f.block('SENS','센서 모듈 DF30 24P (BXF4677-GC2053) · 24MHz · 전원 스위치',['모듈 3.3V 전원 3핀 ← CAM_EN 스위치 · CAM_1V8(Q6, 게이트 Q7/R17 → 자기 소스 풀업, N1) = MCLK(OE=VDD)·I2C 풀업 · RESET RC + BAT54 · C6 DNP 유지','MCLK 24MHz 발진기 (BTB에 MCLK 없음, 계약 9절) · 모듈↔J3 번호 대응은 추론 → 실물 도통'],cols=5)
# --- sensor module DF30 24P (BXF4677-GC2053) - pin numbering = S401 J2
df = {'1': 'CAM_I2C2_SDA', '3': 'CAM_I2C2_SCL', '4': 'CAM_MCLK', '5': 'CAM_RX0_0N', '7': 'CAM_RX0_0P', '9': 'CAM_RX0_CLKN', '11': 'CAM_RX0_CLKP',
      '12': 'CAM_AVDD', '13': 'CAM_RX0_1N', '14': 'CAM_IOVDD', '15': 'CAM_RX0_1P', '16': 'CAM_AVDD', '24': 'CAM_RESET'}
for p in ['2', '6', '8', '10', '17', '18', '19', '20', '21', '22', '23']: df[p] = 'GND'
f.add('J3', 'Connector_Generic:Conn_02x12_Odd_Even', 'DF30FC-24DS-0.4V(81)', 'openhw:Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm', df,
      fields={'MPN': 'Hirose DF30FC-24DS-0.4V(81) (LCSC C5137456)', 'Note': 'module BXF4677-GC2053; module<->J numbering inferred (V-002) - continuity check'})
report['df30'] = df
# camera rails: CORE_3V3 -> AO3401A switches, gate pulled low by DMG1012T when CAM_EN=1 (AVDD delayed by RC)
f.add('Q1', 'Transistor_FET:AO3401A', 'AO3401A', 'Package_TO_SOT_SMD:SOT-23', {'1': 'CAM_PG_IO', '2': 'CORE_3V3', '3': 'CAM_IOVDD'})
f.add('Q2', 'Transistor_FET:AO3401A', 'AO3401A', 'Package_TO_SOT_SMD:SOT-23', {'1': 'CAM_PG_AV', '2': 'CORE_3V3', '3': 'CAM_AVDD'})
R(f, 'R4', '100k', 'CORE_3V3', 'CAM_PG')
R(f, 'R5', '10k', 'CAM_PG', 'CAM_PG_AV')
C(f, 'C6', '100nF', 'CORE_3V3', 'CAM_PG_AV', dnp=True, )
# C-019/O-93 P2: Miller soft start for Q1/Q2 (SIM-C3: CORE_3V3 dip 0.230V -> 0.046V, IOVDD on 10us, AVDD 81us)
R(f, 'R20', '1k', 'CAM_PG', 'CAM_PG_IO')
C(f, 'C20', '4.7nF', 'CAM_PG_IO', 'CAM_IOVDD')
C(f, 'C21', '4.7nF', 'CAM_PG_AV', 'CAM_AVDD')
f.add('Q3', 'Transistor_FET:DMG1012T', 'DMG1012T', 'Package_TO_SOT_SMD:SOT-523', {'1': 'CAM_EN', '2': 'GND', '3': 'CAM_PG'})
R(f, 'R6', '100k', 'CAM_EN', 'GND')
C(f, 'C7', '1uF', 'CAM_IOVDD', 'GND'); C(f, 'C8', '1uF', 'CAM_AVDD', 'GND'); C(f, 'C9', '100nF', 'CAM_AVDD', 'GND')
R(f, 'R7', '10k', 'CAM_EN', 'CAM_RESET'); C(f, 'C10', '100nF', 'CAM_RESET', 'GND')
f.add('D3', 'Device:D_Schottky', 'BAT54WS', 'Diode_SMD:D_SOD-323', {'1': 'CAM_EN', '2': 'CAM_RESET'}, fields={'Note': 'V-004 R3: RESET discharges first when CAM_EN falls'})
R(f, 'R16', '10k', 'CAM_RESET', 'GND', dnp=True)
f.add('Q6', 'Transistor_FET:Q_PMOS_GSD', 'DMG2305UX', 'Package_TO_SOT_SMD:SOT-23', {'1': 'CAM_1V8_G', '2': 'CORE_1V8', '3': 'CAM_1V8'}, fields={'MPN': 'Diodes DMG2305UX', 'Note': 'CAM_1V8 switch (V-004 R1, O-33): RDS(on) <=200mR @ VGS -1.8V, VGS(th) -0.5..-0.9V (DS36196 Rev 8-2); AO3401A unsuitable'})
C(f, 'C18', '1uF', 'CAM_1V8', 'GND')
R(f, 'R17', '4.7k', 'CORE_1V8', 'CAM_1V8_G')  # C-018 S5 (was 10k): off 47us with C19 4.7n (SIM-001b' 55480c0)
f.add('Q7', 'Transistor_FET:DMG1012T', 'DMG1012T', 'Package_TO_SOT_SMD:SOT-523', {'1': 'CAM_EN', '2': 'GND', '3': 'CAM_1V8_PD'}, fields={'Note': 'V-004b N1: Q6 gate pulled to its own source (CORE_1V8), driven by CAM_EN (S401 pattern); C-017: via R18 1k'})
# C-017/O-87 S1: Miller soft start for Q6 (inrush 5.11A -> 0.133A, on 36us, SIM-001b) · S4: CAM_1V8 bleeder
R(f, 'R18', '1k', 'CAM_1V8_PD', 'CAM_1V8_G')
C(f, 'C19', '4.7nF', 'CAM_1V8_G', 'CAM_1V8')  # C-018 S5 (was 10nF): inrush 0.242A
R(f, 'R19', '10k', 'CAM_1V8', 'GND')
# MCLK 24MHz (OT7EL89, OE=CAM_EN, supply CORE_1V8 always-on)
f.add('X1', 'Oscillator:ASE-xxxMHz', 'OT7EL89CJI-111YLC-24M', 'Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm',
      {'1': 'CAM_1V8', '2': 'GND', '3': 'MCLK_OSC', '4': 'CAM_1V8'}, fields={'MPN': 'YXC OT7EL89CJI-111YLC-24M (LCSC C5280583)', 'Note': '2016 4P OE/GND/OUT/VDD; footprint SiT 2.0x1.6 - verify land vs YXC drawing'})
R(f, 'R8', '22R', 'MCLK_OSC', 'CAM_MCLK'); C(f, 'C11', '100nF', 'CAM_1V8', 'GND')
f.block('ALS','조도 LTR-329 · I2C2 상시 풀업',['I2C2 1.8V · GC2053 0x3f · LTR-329 0x29 (VIO 1.7~3.6V) · 풀업 4.7k → CAM_1V8 스위칭 (O-33, V-004 R1) · LTR-329는 CAM_EN=1일 때만 폴링','LIGHT_SENSE 아날로그 차선 Q4/R11 DNP'],cols=4)
# I2C2 always-on 1.8V pull-ups (O-22)
R(f, 'R9', '4.7k', 'CAM_1V8', 'CAM_I2C2_SDA'); R(f, 'R10', '4.7k', 'CAM_1V8', 'CAM_I2C2_SCL')
# ALS LTR-329 (VDD FRONT_3V3, I2C 1.8V direct: VIO 1.7-3.6V)
f.add('U3', 'openhw:LTR-329ALS-01', 'LTR-329ALS-01', 'openhw:Lite-On_LTR-329ALS-01_2x2mm_P1.2mm', {'1': 'FRONT_2V8', '2': 'GND', '3': 'CAM_I2C2_SDA', '4': 'CAM_I2C2_SCL'},
      fields={'MPN': 'Lite-On LTR-329ALS-01 (LCSC C284894)'})
C(f, 'C12', '1uF', 'FRONT_2V8', 'GND'); C(f, 'C13', '100nF', 'FRONT_2V8', 'GND')
# LIGHT_SENSE alternative pads (DNP)
f.add('Q4', 'Device:Q_Photo_NPN', 'ALS-PT19 (alt)', 'openhw:Everlight_ALS-PT19_1.7x0.8mm', {'1': 'CORE_1V8', '2': 'LIGHT_SENSE'}, dnp=True,
      fields={'Note': 'alternative analog ALS (contract C15); footprint placeholder - ALS-PT19 land to be drawn if used'})
R(f, 'R11', '10k', 'LIGHT_SENSE', 'GND', dnp=True)
f.block('IR','IR LED 2스트링 · AL8860 x2 (A·B 실장, O-69)',['12V_IR → Rs 0.1R → VSMA1085400 x2 직렬 → L 68uH → SW · 스트링당 1.0A (O-25, V-001 6)','IR_PWM High = 끔 · R12 풀업 → 기본 끔 (K1) · CTRL = IR_PWM 오픈드레인 공통 (분기 C2-5) · 기본 12V_IR 꺼짐 (eFuse SHDN) · 열: 스트링 평균 ≤1.6W = IR_PWM 듀티 ≤25% (O-31, FW 강제)'],cols=6)
# IR PWM -> CTRL (open drain, both strings share CTRL - branch C18)
f.add('Q5', 'Transistor_FET:DMG1012T', 'DMG1012T', 'Package_TO_SOT_SMD:SOT-523', {'1': 'IR_PWM', '2': 'GND', '3': 'IR_CTRL'})
R(f, 'R12', '100k', 'CORE_1V8', 'IR_PWM')
# IR strings A / B both populated (O-69, R-016); AL8860 1.0A (Rs 0.1R), 2x VSMA1085400 each
for k, dn in (('A', False), ('B', False)):
    u = 'U4' if k == 'A' else 'U5'; base = 0 if k == 'A' else 10
    f.add(u, 'Driver_LED:AL8860MP', 'AL8860MP-13', 'openhw:Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860',
          {'1': f'IR{k}_SET', '2': 'GND', '3': 'GND', '4': 'IR_CTRL', '5': f'IR{k}_SW', '6': f'IR{k}_SW', '8': '12V_IR', '9': 'GND'}, dnp=dn,
          fields={'MPN': 'Diodes AL8860MP-13 (LCSC C500782)', 'Note': f'string {k}' + (' DNP (R-006 O-25)' if dn else '')})
    R(f, f'R{13+base//10}', '0.1R 1% 0.25W', '12V_IR', f'IR{k}_SET', 'Resistor_SMD:R_1206_3216Metric', dnp=dn)
    f.add(f'D_IR_{k}1', 'Device:LED', 'VSMA1085400', 'openhw:Vishay_VSMA1085600_3.4x3.4mm', {'2': f'IR{k}_SET', '1': f'IR{k}_M'}, dnp=dn,
          fields={'MPN': 'Vishay VSMA1085400 (+-40deg; package drawing 6.550-5367.01-4; land drawing 6.550-5366.9-3 = VSMA1085600 land)'})
    f.add(f'D_IR_{k}2', 'Device:LED', 'VSMA1085400', 'openhw:Vishay_VSMA1085600_3.4x3.4mm', {'2': f'IR{k}_M', '1': f'IR{k}_K'}, dnp=dn,
          fields={'MPN': 'Vishay VSMA1085400'})
    f.add(f'L{1 if k=="A" else 2}', 'Device:L', '47uH Irms>=1.3A Isat>=2A', 'openhw:L_Bourns_SRN6045TA', {'1': f'IR{k}_K', '2': f'IR{k}_SW'}, dnp=dn,
          fields={'MPN': 'Bourns SRN6045TA-470M (Irms 1.6A, Isat 2.0A per V-004 R10)'})
    f.add(f'D{1 if k=="A" else 2}', 'Device:D_Schottky', 'SS24 (40V 2A, SMA)', 'Diode_SMD:D_SMA', {'1': '12V_IR', '2': f'IR{k}_SW'}, dnp=dn, fields={'MPN': 'Vishay SS24S-E3/61T (SMA 40V 2A, LCSC C84317)', 'Note': 'alt Vishay SSA24-M3/61T (O-38: stock 0, 15wk)'})
    C(f, f'C{14 if k=="A" else 16}', '10uF/50V X7R', '12V_IR', 'GND', 'Capacitor_SMD:C_1206_3216Metric', dnp=dn)
    C(f, f'C{15 if k=="A" else 17}', '100nF/50V', '12V_IR', 'GND', dnp=dn)
f.block('FPC','보드 간 JST GH 6P (직선 케이블 J7-n ↔ J4-(7−n), O-41)',['계약 12A절 v1.8 · 3 ALS_INT_RSV · 4 SPARE1 (캐리어와 3·4 맞바꿈) · 12V_IR 2접점 x 1.0A'],cols=3)
# FPC 10P (symmetric, mirror of carrier J7)
f.add('J4', 'Connector_Generic_MountingPin:Conn_01x06_MountingPin', 'JST GH 6P (board link)', 'Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal', {**fpc, '3': 'ALS_INT_RSV', '4': 'SPARE1'},
      fields={'MPN': 'JST SM06B-GHS-TB', 'Note': 'C-009/O-41: straight cable J7-n <-> J4-(7-n) (both -X entry, U-bend); pins 3/4 swapped vs carrier J7'})
# C-016/O-83: R15 10k ALS_INT_RSV pull-up removed (J2-32 unconnected, LTR-329ALS-01 has no INT; ALS_INT_RSV = harness spare only)
f.block('TP','시험점 (계약 11절)',cols=9)
# test points
for i, n in enumerate(['VIN', 'FRONT_2V8', 'CORE_1V8', 'CORE_3V3', 'CAM_AVDD', 'CAM_IOVDD', 'CAM_MCLK', 'CAM_EN', 'CAM_RESET', 'ICR_A', 'ICR_B',
                       'IRA_SW', 'IRA_SET', 'IR_PWM', 'IR_CTRL', 'LIGHT_SENSE', 'CAM_I2C2_SDA', 'CAM_I2C2_SCL', '12V_IR', 'GND', 'GND', 'SPARE1', 'CAM_1V8', 'ALS_INT_RSV']):  # TP24 ALS_INT_RSV: C-016 harness spare end
    TP(f, f'TP{i+1}', n)
os.makedirs(f'{OUT}/front', exist_ok=True)
report['front'] = f.write(f'{OUT}/front/front.kicad_sch')
json.dump(report, open(os.path.join(os.path.dirname(__file__),'c002-gen-report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: report[k] for k in ('carrier', 'front')}, ensure_ascii=False))
