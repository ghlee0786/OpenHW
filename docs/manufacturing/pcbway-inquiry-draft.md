# PCBWay 사전 문의 초안 (발주 아님)
- 작성: lead 2026-11-27 · 근거: R-010 「확인 못 한 것」, D-003 #21·#29, R-011
- 보내는 사람: 사용자(가입·로그인·전송은 사용자가 한다). 개인 정보·회사명은 이 초안에 넣지 않는다.
- 첨부: 없음(Gerber·BOM 업로드는 별도 지시 후). 아래 본문만 Live chat 또는 이메일 문의로 보낸다.

## 본문 (영문 그대로 붙여 넣기)

Subject: Pre-order questions - two 4-layer PCBA prototypes (qty 5 each)

Hello,

We are preparing two small 4-layer PCBA prototypes and would like to confirm a few points before placing an order. No order yet.

Boards
- Board A: 40 x 54 mm, Board B: 40 x 40 mm, 4 layers, FR-4 TG150-160, 1.6 mm, 1/1 oz, ENIG, qty 5 each
- Double-sided assembly, no BGA. Fine-pitch parts: 60-pin 0.5 mm board-to-board connectors, 0.4/0.5 mm pitch connectors, QFN/WSON/USON/MSOP-EP/HTSSOP-EP with exposed pads
- Files are exported from KiCad: Gerber RS-274X, Excellon drill, CPL (csv, mm) and BOM in your template

Questions
1. CPL rotation: our CPL uses KiCad footprint rotations as-is, viewed from the top for both sides, with no X-mirror for bottom parts. Do you correct rotations on your side, or should we convert to IPC-7351 zero orientation first?
2. Assembly grade: is there a Standard vs Advanced PCBA option? Which one do you recommend for the 0.5 mm 60-pin board-to-board connectors and exposed-pad packages above?
3. X-ray inspection: what is the cost for 5 + 5 boards, and is it applied automatically for leadless / exposed-pad packages or only on request?
4. BOM "Type" column: besides SMD / Thru-hole / Hybrid, do you accept "DNS" for do-not-place parts? Is there a way to mark parts we solder manually later?
5. Via-in-pad: what is the additional cost for resin-filled and cap-plated via-in-pad (VIPPO) on these two boards, qty 5 each?
6. Impedance control: we need 100 ohm differential (MIPI CSI, Ethernet) and 90 ohm differential (USB 2.0) on outer layers. Please confirm your standard 4-layer 1.6 mm stackup (layer thicknesses, dielectric constant) and the recommended trace width / gap for each.
7. Consigned parts: we will supply a few parts ourselves (IR LEDs, a filter holder, the board-to-board mating parts if needed). What packaging do you require (tape, leader length), how many spares, and how is the shipping address provided?
8. Panelization: the 40 x 40 mm board is small. Do you panelize it for assembly yourselves, and do we need to add rails or fiducials?
9. Minimum capability confirmation: QFN minimum pitch and 0.4 mm pitch connectors with your standard stencil.

Thank you.

## 회신을 받으면 반영할 곳
| 질문 | 반영 |
|---|---|
| 1 회전 | R-010 S9, CPL 생성기 |
| 2 등급 · 3 X-ray | R-010 S7, 견적 |
| 4 Type | R-011 BOM 생성기 |
| 5 via-in-pad | D-003 #29 차선 결정 |
| 6 임피던스 | D-003 #21, PCB 규칙 |
| 7 위탁 | D-003 #2, 위탁 목록 |
| 8 패널 · 9 능력 | R-010 #11, PCB 외형 |
