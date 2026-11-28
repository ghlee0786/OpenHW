<!-- 수치는 저장소 결과 파일에서 읽은 값이다(기준 커밋 main 995b872, 2026-11-27). 값마다 출처 경로를 표 각주와 docs/readme/*.svg 주석에 적었다. -->

<div align="center">

<img src="docs/readme/icon.svg" width="96" alt="OpenHW 아이콘 — 칩 안의 카메라 렌즈">

# OpenHW

**SG2002 엣지 AI 카메라 — 직접 설계한 PCB 두 장과 구매한 코어 모듈, 렌즈·IR-cut·IR 조명을 한 몸으로**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-D22128?logo=apache&logoColor=white)](LICENSE) [![KiCad 10](https://img.shields.io/badge/KiCad-10-314CB0?logo=kicad&logoColor=white)](hardware/schematic) [![Linux 5.10](https://img.shields.io/badge/Linux-5.10-FCC624?logo=linux&logoColor=black)](firmware) [![SoC: SG2002](https://img.shields.io/badge/SoC-SG2002-6f42c1)](#사양) [![Status](https://img.shields.io/badge/Status-%EA%B0%80%EC%83%81%20%EC%84%A4%EA%B3%84%20%EC%A7%84%ED%96%89-orange)](#진행-상태)

<img src="docs/readme/hero.svg" width="880" alt="흐름 애니메이션: 피사체의 빛이 렌즈·센서로 들어가 SG2002 NPU에서 사람을 감지하고 캐리어 보드를 거쳐 이벤트로 나간다">

</div>

> **English summary**
> OpenHW is an open-hardware edge-AI camera proof of concept built around the SG2002 SoC.
> A purchased core module (reCamera Core 2002) sits between two boards we designed in KiCad 10:
> a 40×40 mm front board (image sensor, M12 lens, IR-cut filter, 850 nm IR LEDs, ambient light sensor)
> and a 40×54 mm carrier board (12 V input and protection, 5 V buck, 10/100 Ethernet, USB-C, microSD).
> The device runs Linux and detects people on the on-chip NPU.
> The project is in the virtual-design stage: schematics pass ERC with zero violations, 25 of 25 circuit simulations pass,
> and both boards pass DRC with zero violations and zero unconnected items.
> Hardware design files are released under the Apache License 2.0.

## 진행 상태

<p align="center"><img src="docs/readme/pipeline.svg" width="880" alt="설계 흐름 8단계: 요구사항·회로도·시뮬레이션·PCB 배선·DRC·3D 검증·케이스 완료, 렌더는 사람 확인 중"></p>

| 단계 | 상태 | 근거 (결과 파일) |
|---|---|---|
| 제품 기획 · 작업 기본값 | ✅ 완료 | [`product-brief.md`](docs/planning/product-brief.md) · [`D-003`](docs/decisions/D-003-working-defaults.md) |
| 회로도 2장 | ✅ ERC 위반 0 | [`carrier-erc.json`](hardware/schematic/carrier/carrier-erc.json) · [`front-erc.json`](hardware/schematic/front/front-erc.json) |
| 회로 시뮬레이션 | ✅ 25/25 통과 (ngspice-47) | [`hardware/sim/results/`](hardware/sim/results) |
| 전면 보드 PCB | ✅ DRC 위반 0 · 미연결 0 · 회로도 일치 0 | [`front-drc.json`](hardware/pcb/drc/front-drc.json) |
| 캐리어 보드 PCB | ✅ DRC 위반 0 · 미연결 0 · 회로도 일치 0 | [`carrier-drc.json`](hardware/pcb/drc/carrier-drc.json) |
| 3D 조립 판정 | ✅ 보드 995b872 + 케이스 시안 A: 27항목 불합격 0 · 간섭 0 | [`run_A.md`](mechanical/m010/run_A.md) · [`judge.md`](mechanical/m007/judge.md) |
| 케이스 | ✅ 시안 A 상세 설계 (54 × 75.5 × 71.7 mm, 앞 스모크 유리 · 뒤 알루미늄 방열 쉘) | [`o126_a.md`](mechanical/design/o126_a.md) · [`o126_thermal.md`](mechanical/design/o126_thermal.md) |
| 최종 렌더 | ✅ 시안 A 6컷 + 회전 영상 — 사실감 · 유리 너머 기판 비침 · 브래킷 광축 사용자 확인 완료(2026-11-28) | [`docs/renders/final/`](docs/renders/final) |
| 실물 제작 | ⏳ 이번 범위(가상 설계) 밖 | — |

<p align="center"><img src="docs/readme/numbers.svg" width="880" alt="핵심 수치 카드: ERC 0, 시뮬레이션 25/25, 전면 DRC 0·0, 캐리어 DRC 0·0, 3D 모델 빠짐 0, 4층 1.6 mm"></p>

## 주요 기능

- **사람 감지를 보드 안에서** — SG2002의 NPU에서 YOLOX-Nano(BF16)를 돌린다. 영상을 밖으로 보내지 않고 감지 이벤트만 보낸다. ([D-003](docs/decisions/D-003-working-defaults.md) #3 #8 #19)
- **주야 자동 전환** — 조도센서로 밤낮을 판단해 IR-cut 필터를 바꾸고, 850 nm IR LED를 켠다. LED는 듀티와 피크를 펌웨어로 제한한다. ([D-003](docs/decisions/D-003-working-defaults.md) #6 #7 #26)
- **12 V 한 줄 입력** — 퓨즈·역접속 보호 뒤 5 V 강압으로 코어를 먹이고, IR 조명 갈래는 eFuse로 전류를 제한한다. ([D-003](docs/decisions/D-003-working-defaults.md) #10 #22)
- **유선 이더넷 10/100 · USB-C · microSD** — 네트워크 서비스는 닫힌 상태가 기본이다. ([D-003](docs/decisions/D-003-working-defaults.md) #11 #30)
- **광학 일체 설계** — M12 렌즈 광축·IR LED 위치·조도 창을 PCB 배치 기준으로 삼았다. ([D-003](docs/decisions/D-003-working-defaults.md) #4 #17)

## 아키텍처

### 3층 적층

<p align="center"><img src="docs/readme/stack.svg" width="880" alt="3층 적층 분해·결합 애니메이션: 전면 보드, 코어 모듈, 캐리어 보드와 BTB 커넥터, 광축"></p>

캐리어 보드(아래) – 코어 모듈 – 전면 보드(위)를 0.5 mm 60핀 BTB 커넥터 두 쌍으로 바로 꽂는다(결합 높이 8.0 mm). 전면과 캐리어 사이 IR 전원·제어는 GH 6핀 하니스로 잇는다.

<p align="center"><a href="docs/readme/media/stack_spin.gif"><img src="docs/readme/media/stack_spin.gif" width="480" alt="3층 적층 회전 애니메이션: 캐리어 보드, 코어 모듈 자리, 전면 보드를 KiCad 3D로 쌓아 돌린 모습"></a><br><sub>실제 보드 파일로 쌓은 3층 적층 회전 (KiCad 3D 렌더)</sub></p>

### 시스템 블록도

<p align="center"><img src="docs/readme/block.svg" width="880" alt="시스템 블록도: 12 V 입력, 보호, 5 V 강압, eFuse, SG2002, 이미지 센서, IR-cut, 조도센서, IR LED, 이더넷, USB-C, microSD"></p>

## 갤러리

### 3D — 전면 보드

<table>
<tr>
<td align="center" width="33%"><a href="docs/renders/p005/front-iso.png"><img src="docs/renders/p005/front-iso.png" width="260" alt="전면 보드 비스듬한 앞면 3D 렌더"></a><br><sub>비스듬한 앞면 — 렌즈 홀더·IR LED</sub></td>
<td align="center" width="33%"><a href="docs/renders/p005/front-iso-back.png"><img src="docs/renders/p005/front-iso-back.png" width="260" alt="전면 보드 비스듬한 뒷면 3D 렌더"></a><br><sub>비스듬한 뒷면 — BTB·열 패드</sub></td>
<td align="center" width="33%"><a href="docs/readme/media/front_spin.gif"><img src="docs/readme/media/front_spin.gif" width="260" alt="전면 보드 360도 회전 애니메이션"></a><br><sub>360° 회전</sub></td>
</tr>
<tr>
<td align="center"><a href="docs/renders/p005/front-top.png"><img src="docs/renders/p005/front-top.png" width="260" alt="전면 보드 윗면 3D 렌더"></a><br><sub>윗면</sub></td>
<td align="center"><a href="docs/renders/p005/front-bottom.png"><img src="docs/renders/p005/front-bottom.png" width="260" alt="전면 보드 아랫면 3D 렌더"></a><br><sub>아랫면</sub></td>
<td align="center"><sub>캐리어 보드 3D는 아래 표<br>3층 적층 회전은 <a href="#3층-적층">아키텍처</a></sub></td>
</tr>
</table>

### 3D — 캐리어 보드

<table>
<tr>
<td align="center" width="33%"><a href="docs/renders/carrier/carrier-iso.png"><img src="docs/renders/carrier/carrier-iso.png" width="260" alt="캐리어 보드 비스듬한 앞면 3D 렌더"></a><br><sub>비스듬한 윗면 — BTB·5 V 강압·USB-C</sub></td>
<td align="center" width="33%"><a href="docs/renders/carrier/carrier-iso-back.png"><img src="docs/renders/carrier/carrier-iso-back.png" width="260" alt="캐리어 보드 비스듬한 뒤쪽 3D 렌더"></a><br><sub>비스듬한 뒤쪽 — RJ45·DC 잭·microSD</sub></td>
<td align="center" width="33%"><a href="docs/readme/media/carrier_spin.gif"><img src="docs/readme/media/carrier_spin.gif" width="260" alt="캐리어 보드 360도 회전 애니메이션"></a><br><sub>360° 회전</sub></td>
</tr>
<tr>
<td align="center"><a href="docs/renders/carrier/carrier-top.png"><img src="docs/readme/media/carrier_top.png" width="260" alt="캐리어 보드 윗면 3D 렌더"></a><br><sub>윗면 — 누르면 큰 그림</sub></td>
<td align="center"><a href="docs/renders/carrier/carrier-bottom.png"><img src="docs/readme/media/carrier_bottom.png" width="260" alt="캐리어 보드 아랫면 3D 렌더"></a><br><sub>아랫면 — 누르면 큰 그림</sub></td>
<td align="center"><sub>캐리어 40 × 54 mm · 4층<br>DRC 위반 0 · 미연결 0<br>(<a href="hardware/pcb/drc/carrier-drc.json">carrier-drc.json</a>)</sub></td>
</tr>
</table>

### 전면 보드 PCB 층 (4층)

<table>
<tr>
<td align="center"><a href="docs/readme/gallery/pcb/front-fcu.png"><img src="docs/readme/gallery/pcb/front-fcu.png" width="260" alt="전면 보드 윗면 구리층 F.Cu"></a><br><sub>F.Cu — 윗면 신호</sub></td>
<td align="center"><a href="docs/readme/gallery/pcb/front-in1.png"><img src="docs/readme/gallery/pcb/front-in1.png" width="260" alt="전면 보드 내부 1층 In1.Cu"></a><br><sub>In1.Cu — GND 기준면</sub></td>
<td align="center"><a href="docs/readme/gallery/pcb/front-in2.png"><img src="docs/readme/gallery/pcb/front-in2.png" width="260" alt="전면 보드 내부 2층 In2.Cu"></a><br><sub>In2.Cu — GND · 전원</sub></td>
</tr>
<tr>
<td align="center"><a href="docs/readme/gallery/pcb/front-bcu.png"><img src="docs/readme/gallery/pcb/front-bcu.png" width="260" alt="전면 보드 아랫면 구리층 B.Cu"></a><br><sub>B.Cu — 아랫면 신호</sub></td>
<td align="center"><a href="docs/readme/gallery/pcb/front-silk.png"><img src="docs/readme/gallery/pcb/front-silk.png" width="260" alt="전면 보드 실크 인쇄층"></a><br><sub>실크</sub></td>
<td align="center"><sub>규칙: 트랙/간격 0.15/0.16 mm 이상<br>고속 차동 100 Ω · USB 90 Ω<br>(<a href="docs/decisions/D-003-working-defaults.md">D-003</a> #21)</sub></td>
</tr>
</table>

### 회로도

<table>
<tr>
<td align="center" width="50%"><a href="docs/readme/gallery/sch/front-sch.svg"><img src="docs/readme/gallery/sch/front-sch.png" width="400" alt="전면 보드 회로도 첫 장 미리보기"></a><br><sub>전면 보드 — 누르면 원본 SVG</sub></td>
<td align="center" width="50%"><a href="docs/readme/gallery/sch/carrier-sch.svg"><img src="docs/readme/gallery/sch/carrier-sch.png" width="400" alt="캐리어 보드 회로도 첫 장 미리보기"></a><br><sub>캐리어 보드 — 누르면 원본 SVG</sub></td>
</tr>
</table>

### 회로 시뮬레이션 파형

캐리어 전원 계열 **15/15**(SIM-A·B·C·D), 전면 보드 **10/10**(SIM-L) 통과 — [`hardware/sim/results/`](hardware/sim/results)

<table>
<tr>
<td align="center" width="50%"><a href="hardware/sim/png/SIM-D1-sequence.png"><img src="hardware/sim/png/SIM-D1-sequence.png" width="400" alt="전원 순서 전체 기동 파형: 12 V에서 5 V, 코어 레일, 전면 2.8 V까지"></a><br><sub>SIM-D1 전원 순서 전체 기동 (12 V → 5 V → 코어 → 전면 2.8 V)</sub></td>
<td align="center" width="50%"><a href="hardware/sim/png/SIM-B4-startup.png"><img src="hardware/sim/png/SIM-B4-startup.png" width="400" alt="5 V 강압 기동 파형, 소프트 스타트 5 ms"></a><br><sub>SIM-B4 5 V 강압 기동 (소프트 스타트 5 ms)</sub></td>
</tr>
<tr>
<td align="center"><a href="hardware/sim/png/SIM-L1-al8860.png"><img src="hardware/sim/png/SIM-L1-al8860.png" width="400" alt="IR LED 한 줄의 전류와 리플 파형"></a><br><sub>SIM-L1 IR LED 한 줄 전류 · 리플 · 주파수</sub></td>
<td align="center"><a href="hardware/sim/png/SIM-L10-cam-on.png"><img src="hardware/sim/png/SIM-L10-cam-on.png" width="400" alt="카메라 전원 켜는 순서 파형: IOVDD 다음 AVDD가 50 µs 이상 늦게"></a><br><sub>SIM-L10 카메라 전원 켜는 순서 (IOVDD → AVDD ≥ 50 µs)</sub></td>
</tr>
</table>

### 케이스 — 시안 A 최종 렌더

<p align="center"><a href="docs/renders/final/video/concept-explode.mp4"><img src="docs/renders/final/video/concept-explode.gif" width="400" alt="케이스 시안 A 콘셉 영상: 분해된 부품이 하나씩 조립되는 모습(움직이는 GIF, 누르면 1080p MP4)"></a><br><sub>콘셉 영상 — 분해에서 조립까지 · Concept film — from exploded parts to the assembled camera (누르면 1080p MP4)</sub></p>

> 둥근 박스 54 × 75.5 × 71.7 mm · 앞면 스모크 유리(가시광 투과 약 15 %, 안쪽 검정 마스크) · 뒤쪽 알루미늄 방열 쉘 + 무광 흑색 플라스틱 · 벽 브래킷. 누르면 1600 px 원본. 근거: [시안 A 설계](mechanical/design/o126_a.md) · [조립 판정 기록](mechanical/m010/run_A.md)

<table>
<tr>
<td align="center" width="33%"><a href="docs/renders/final/blender-product.png"><img src="docs/readme/gallery/case-a/product.png" width="260" alt="케이스 시안 A 비스듬한 앞쪽 제품 렌더"></a><br><sub>제품 — 비스듬한 앞쪽</sub></td>
<td align="center" width="33%"><a href="docs/renders/final/blender-front.png"><img src="docs/readme/gallery/case-a/front.png" width="260" alt="케이스 시안 A 정면 렌더"></a><br><sub>정면 — 스모크 유리 · 렌즈 창</sub></td>
<td align="center" width="33%"><a href="docs/renders/final/blender-rear.png"><img src="docs/readme/gallery/case-a/rear.png" width="260" alt="케이스 시안 A 뒤쪽 렌더"></a><br><sub>뒤쪽 — 알루미늄 방열 핀</sub></td>
</tr>
<tr>
<td align="center" width="33%"><a href="docs/renders/final/blender-exploded.png"><img src="docs/readme/gallery/case-a/exploded.png" width="260" alt="케이스 시안 A 분해도 렌더"></a><br><sub>분해도 — 쉘 · 보드 · 유리</sub></td>
<td align="center" width="33%"><a href="docs/renders/final/blender-section.png"><img src="docs/readme/gallery/case-a/section.png" width="260" alt="케이스 시안 A 단면 렌더"></a><br><sub>단면 — 내부 적층</sub></td>
<td align="center" width="33%"><a href="docs/renders/final/blender-inuse.png"><img src="docs/readme/gallery/case-a/inuse.png" width="260" alt="케이스 시안 A 벽 브래킷 설치 모습 렌더"></a><br><sub>설치 — 벽 브래킷, 광축 수평</sub></td>
</tr>
</table>

#### 영상 · Videos

<table>
<tr>
<td align="center" width="50%"><a href="docs/renders/final/blender-turntable.mp4"><img src="docs/readme/gallery/case-a/turntable.gif" width="400" alt="케이스 시안 A 360도 회전(움직이는 GIF, 누르면 1080p MP4)"></a><br><sub>360도 회전 · 360° turntable</sub></td>
<td align="center" width="50%"><a href="docs/renders/final/video/section-open.mp4"><img src="docs/renders/final/video/section-open.gif" width="400" alt="케이스 시안 A 단면이 열리며 내부 적층이 보이는 모습(움직이는 GIF, 누르면 1080p MP4)"></a><br><sub>단면 열림 — 내부 적층 · Section opening — inside the stack</sub></td>
</tr>
<tr>
<td align="center" width="50%"><a href="docs/renders/final/video/hero-dolly.mp4"><img src="docs/renders/final/video/hero-dolly.gif" width="400" alt="케이스 시안 A 주위를 카메라가 움직이며 보여 주는 모습(움직이는 GIF, 누르면 1080p MP4)"></a><br><sub>카메라 이동 — 제품 히어로 · Hero dolly shot</sub></td>
</tr>
</table>

<sub>렌더 · 영상 속 코어 모듈 형상은 원 설계에서 가져왔고, 이 렌더 · 영상 파일은 CC BY-SA 4.0이다 — 출처 [NOTICE](docs/renders/final/NOTICE.md) · The core-module geometry in these renders and videos comes from the original design; these render and video files are CC BY-SA 4.0 — see [NOTICE](docs/renders/final/NOTICE.md).</sub>

## 기술 스택

| 분야 | 도구 · 구성 | 근거 |
|---|---|---|
| 회로도 · PCB | KiCad 10 (`kicad-cli`로 ERC · DRC · STEP · 렌더 · 그림 내보내기) | [`hardware/schematic/`](hardware/schematic) |
| 회로 시뮬레이션 | ngspice-47, 넷리스트와 판정 스크립트 | [`hardware/sim/README.md`](hardware/sim/README.md) |
| PCB 규칙 | 4층 1.6 mm, 넷클래스 + 사용자 DRC 규칙 | [`hardware/pcb/rules/`](hardware/pcb/rules) |
| 기구 | STEP 기반 3D 조립 판정 스크립트, 케이스 매개변수 설계 | [`mechanical/`](mechanical) |
| 펌웨어 | Buildroot Linux (벤더 커널 5.10.4), 사람 감지·주야 전환 앱 | [`firmware/`](firmware) |
| AI 모델 | YOLOX-Nano → NPU용 BF16 모델 변환 | [D-003](docs/decisions/D-003-working-defaults.md) #19 |
| 검사 자동화 | Python 스크립트 — 종료 코드 = 불합격 수 | [검증 방법](#사용법) |

## 사양

| 항목 | 전면 보드 | 캐리어 보드 | 코어 모듈 (구매품) |
|---|---|---|---|
| 크기 | 40 × 40 mm | 40 × 54 mm | — |
| 층 · 두께 | 4층 · 1.6 mm | 4층 · 1.6 mm | — |
| 주요 부품 | 이미지 센서 모듈 GC2053 (2 MP, MIPI CSI, 24핀 BTB) · 24 MHz 발진기 · IR-cut 구동 DRV8837 · IR LED 구동 AL8860 ×2 · 850 nm IR LED 자리 4개 (2직렬 × 2줄, PoC는 1줄 실장) · 조도센서 LTR-329 · 2.8 V LDO | 12 V DC 잭 · 퓨즈·역접속 보호 · eFuse TPS26600 (IR 전원) · 5 V 강압 TPS54302 · RJ45 10/100 · USB-C · microSD · 디버그 UART · ESD 보호 | SG2002 SoC (NPU) · 8 GB |
| 보드 간 연결 | BTB 60핀 (암) · GH 6핀 | BTB 60핀 (수) · GH 6핀 | BTB 60핀 ×2 |
| 풋프린트 수 | 100 (시험점 포함) | 103 (시험점 포함) | — |

| 시스템 | 값 |
|---|---|
| 입력 전원 | 12 V DC |
| 네트워크 | 유선 이더넷 10/100 |
| 저장 | 이벤트 전송 기본 + microSD 슬롯 |
| 운영체제 | Linux (벤더 커널 5.10) |
| 감지 | 사람 감지 — YOLOX-Nano, NPU용 BF16 모델 |
| 렌즈 | M12 고정초점, 수평 화각 약 90° |
| BTB 결합 높이 | 8.0 mm |

출처: [D-003 작업 기본값](docs/decisions/D-003-working-defaults.md) #1 #4 #5 #7 #8 #10 #11 #15 #17 #19 #21 #25 #44 · 보드 파일 [`carrier.kicad_pcb`](hardware/schematic/carrier/carrier.kicad_pcb) · [`front.kicad_pcb`](hardware/schematic/front/front.kicad_pcb)(부품 값·풋프린트 수·층 수) · [`params.md`](mechanical/m003/params.md)(btb_h 8.0)

## 저장소 구조

| 폴더 | 내용 |
|---|---|
| [`hardware/schematic/`](hardware/schematic) | KiCad 프로젝트 2개(`carrier/`, `front/`) — 회로도·PCB·ERC 결과 |
| [`hardware/pcb/`](hardware/pcb) | PCB 규칙·DRC 결과·STEP·배치 계획과 배선 도구 |
| [`hardware/libraries/`](hardware/libraries) | 프로젝트 심벌·풋프린트 라이브러리와 파생 고지 |
| [`hardware/sim/`](hardware/sim) | 회로 시뮬레이션 넷리스트·결과·파형 |
| [`hardware/datasheets/`](hardware/datasheets) | 공개 라이선스 데이터시트·참고 설계 원본과 [목록](hardware/datasheets/INDEX.md) |
| [`firmware/`](firmware) | Linux 이미지 패치·앱(사람 감지, 주야 전환)·모델 |
| [`mechanical/`](mechanical) | 적층 기준 모델·조립 판정·케이스 설계 |
| [`docs/`](docs) | 기획(`planning/`), 결정(`decisions/`), 조사(`research/`), 검토(`review/`), 렌더(`renders/`), 이 README의 그림(`readme/`) |
| [`manufacturing/`](manufacturing) | 부품표(BOM) 정리 |
| [`validation/`](validation) | 독립 검토 기록 |

그 밖의 점(.)으로 시작하는 폴더와 자동화 폴더는 작업 환경 설정이며 설계 내용이 아니다.

## 사용법

### KiCad로 열기

1. KiCad 10을 설치한다.
2. `hardware/schematic/front/front.kicad_pro` 또는 `hardware/schematic/carrier/carrier.kicad_pro`를 연다.
3. 프로젝트 라이브러리는 각 프로젝트의 `fp-lib-table`·`sym-lib-table`이 저장소 안 경로로 잡는다.

### 검증 방법

모든 판정은 도구의 종료 코드와 결과 파일로 한다. 그림이나 의견으로 통과를 정하지 않는다.

| 검사 | 명령 (저장소 루트) | 결과 파일 |
|---|---|---|
| ERC | `kicad-cli sch erc --severity-all --exit-code-violations --format json -o hardware/schematic/front/front-erc.json hardware/schematic/front/front.kicad_sch` | `hardware/schematic/*/*-erc.json` |
| DRC | `kicad-cli pcb drc --format json --severity-all --schematic-parity --exit-code-violations -o hardware/pcb/drc/front-drc.json hardware/schematic/front/front.kicad_pcb` | `hardware/pcb/drc/*-drc.json` |
| 회로 시뮬레이션 | [`hardware/sim/README.md`](hardware/sim/README.md)의 실행 방법 (종료 코드 = fail + error 수) | `hardware/sim/results/SIM-*.json` |
| 3D 조립 판정 | `python -I -B mechanical/m007/run_all.py` (종료 코드 = 불합격 수) | [`mechanical/m007/judge.md`](mechanical/m007/judge.md) |
| README 그림 | `python -I docs/readme/tools/make_svgs.py` 후 `python -I docs/readme/tools/check_readme.py` (종료 코드 = 실패 수) | `docs/readme/*.svg` |

캐리어는 위 명령의 `front`를 `carrier`로 바꾼다. ERC·DRC는 위반이 있으면 종료 코드가 0이 아니다.

## 문서

| 문서 | 내용 |
|---|---|
| [제품 기획](docs/planning/product-brief.md) | 용도·형태·미정 항목 |
| [D-003 작업 기본값](docs/decisions/D-003-working-defaults.md) | 설계 갈림길마다 「분기점 · 선택 · 이유 · 차선책」 50여 개 |
| [D-001 SoC 선택](docs/decisions/D-001-soc.md) · [D-002 모듈 + 캐리어 구조](docs/decisions/D-002-module-carrier.md) | 구조 결정 |
| [HW/FW 인터페이스](docs/decisions/hw-fw-interface.md) | 핀·버스·전원 계약 |
| [PCB 배치 계획](hardware/pcb/layout-plan.md) | 보드 배치·적층 기준 |
| [시뮬레이션](hardware/sim/README.md) | 시뮬레이션 실행 방법과 결과 |
| [3D 조립 판정](mechanical/m007/m007-assembly.md) · [케이스 시안 A](mechanical/design/o126_a.md) | 기구 판정과 케이스 상세 설계 |
| [PCB 독립 검토](docs/review/v005-pcb-review.md) | 규칙·완화 검토 |
| [데이터시트 목록](hardware/datasheets/INDEX.md) | 출처·리비전·sha256 |

## 라이선스 · 제3자 고지

- 이 저장소의 설계 파일과 문서는 [Apache License 2.0](LICENSE)을 따른다. 예외: 코어 모듈 형상이 들어간 렌더 · 영상 파일(아래 표).
- 제3자 자료는 각 폴더의 라이선스를 그대로 유지한다. 저작권 표기는 각 폴더의 `LICENSE*` 파일 원문을 따른다. 근거는 [`hardware/datasheets/INDEX.md`](hardware/datasheets/INDEX.md)다.

| 경로 | 라이선스 | 비고 |
|---|---|---|
| `hardware/datasheets/sophgo/` | BSD 2-Clause | SG2002 데이터시트·TRM·참고 회로도 원본 |
| `hardware/datasheets/seeed/` | Apache 2.0 (저장소) · 코어 회로도 PDF는 CC BY-SA 4.0 | 참고 전용 원본. 수정하지 않았다 |
| `hardware/datasheets/antmicro/` | Apache 2.0 | 참고 풋프린트 원본 |
| `hardware/libraries/` 파생 풋프린트 | Apache 2.0 | 원저작물 고지는 [`hardware/libraries/README.md`](hardware/libraries/README.md) · [`licenses/Apache-2.0.txt`](hardware/libraries/licenses/Apache-2.0.txt) |
| 사람 감지 모델 YOLOX-Nano | Apache 2.0 | [D-003](docs/decisions/D-003-working-defaults.md) #19 |
| `docs/renders/final/` · `video/` · `docs/readme/gallery/case-a/` 렌더 · 영상 | CC BY-SA 4.0 | 코어 모듈 형상(STEP, 저장소에는 넣지 않음)의 출처 · 커밋 · 바꾼 것은 [`NOTICE.md`](docs/renders/final/NOTICE.md) · Core-module geometry source and changes: see NOTICE |

라이선스가 표기되지 않았거나 배포가 제한된 데이터시트는 저장소에 넣지 않았고, 링크와 sha256만 [INDEX.md](hardware/datasheets/INDEX.md)에 남겼다.

<div align="center"><sub>그림은 움직이는 SVG다. 운영체제에서 「동작 줄이기」를 켜면 멈춘 그림으로 보이고, 밝은·어두운 테마를 따른다.</sub></div>
