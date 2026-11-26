# Freerouting 설치 기록과 시험 결과 (P-003, O-51 · O-52 · O-54)

## 설치 (O-54: Temurin 25 LTS 포터블 JRE + Freerouting v2.5.0)

- 위치: `C:/Users/gh/tools/freerouting/download/` 한 곳에만 받았고, 빈 폴더에서 풀었다.
- PATH · JAVA_HOME · 시스템 Java 는 바꾸지 않았다. 아래 전체 경로로만 실행한다.
- 해시 대조: 「공개값」은 GitHub 릴리스 API 의 asset `digest`(Freerouting)와 Adoptium 릴리스 checksum 이다. 확인일은 2026-11-26 이다.

| 파일 | 크기 (B) | 받은 곳 | sha256 (로컬) | 공개값 대조 |
|---|---|---|---|---|
| freerouting-2.5.0.jar | 64,599,107 | https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar | `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7` | 일치 |
| OpenJDK25U-jre_x64_windows_hotspot_25.0.5_8.zip | 58,589,419 | https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jre_x64_windows_hotspot_25.0.5_8.zip | `da78d54a2fcdbba1e92d5e3f07dd30236f96297891c4a21a781c3f38f5c0beae` | 일치 |

- 실행에 쓰는 경로:
  - java: `C:/Users/gh/tools/freerouting/download/jre25/jdk-25.0.5+8-jre/bin/java.exe`
  - `java -version`: `openjdk version "25.0.5" 2026-10-20 LTS`, Temurin-25.0.5+8
- 설정 파일: Freerouting 이 처음 실행 때 `%APPDATA%/freerouting/freerouting.json` 을 만든다. 저장소 밖이며 손대지 않았다.

### 받았지만 쓰지 않는 파일 (지우지 않음, O-54)

| 파일 | sha256 | 쓰지 않는 이유 |
|---|---|---|
| freerouting-2.4.1.jar | `251101c3eeac22d7e7dfcf6796603279e5d1000283eb82d8f093780f7afc6aa9` | 클래스 형식 69(Java 25 필요). Java 21 로는 LinkageError (O-52 시험) |
| freerouting-2.3.0.jar | `3cf18d608437740bc497db6b8ef5888e2e60a08de0def20691d1bad0c0e0ee24` | 같은 이유(클래스 69) |
| freerouting-2.2.4.jar | `f5ed374182900ccc78e473518bbb9f6b869f4a07159495f663a76f52bb10523b` | 같은 이유(클래스 69) |
| freerouting-2.2.0.jar | `c5642db8dbf00cf906a00e1c2099acc957a82346704e1bf6083e549383afdb27` | 같은 이유(클래스 69) |
| freerouting-2.1.0.jar | `2c07d58f75dac03782664081e7a58b41c25400d871a9fcf166a2ea6fe60d5def` | 클래스 65(Java 21). GitHub digest 가 없어 공개값 대조를 못 했다. O-54 에서 v2.5.0 으로 정해 쓰지 않음 |
| OpenJDK21U-jre_x64_windows_hotspot_21.0.13_9.zip (+ `jre/`) | `2332c0b4cff6bed722da3567c91d5e47568bcba863fa4945d0a8d6fc76158628` (공개값 일치) | O-52 (C) 시험용. O-54 에서 Java 25 로 바뀜 |

## 흐름 (`hardware/pcb/tools/fr_board.ps1`, hc 칸에서 일반 프로그램으로 실행, O-48)

1. `freeroute.py export`: 고정할 배선을 잠그고 pcbnew `ExportSpecctraDSN` 으로 DSN 을 만든다(헤드리스, GUI 안 씀). 잠근 트랙은 DSN 에 `(type fix)` 로 나간다.
2. Freerouting 을 `-de <dsn> -do <ses> -mp <패스> -mt 8 --gui.enabled=false` 로 돌린다.
3. `freeroute.py import`: pcbnew `ImportSpecctraSES` → 면 다시 채우기 → 저장.
4. `sync_project.py` 를 돌린 뒤 `kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations` 로 판정한다.

### 고정 구간 (Freerouting 이 건드리지 않음)

- 넷클래스: CSI_100 · MDI_100 · USB_90(고속 차동), PWR_12V_IN · PWR_5V · PWR_12V_IR · PWR_LOGIC(전원)
- 넷: /IRA_SET · /IRA_M · /IRB_SET · /IRB_M (IR LED 열 패드 · 열 구리)
- GND 비아 전부(EP 둘레 · 패드 팬아웃 · 쌍 귀환 비아)
- 캐리어 1차 내보내기 결과: 고정 441 · 자유 552 · 고정 넷 14

## 시험 결과 (캐리어 1차, 2026-11-27)

- 30패스로 시작해 9패스까지 봤다.
  - 미배선이 112 ~ 147 사이를 오갔다.
  - Freerouting 자체 위반은 821에서 줄지 않았다.
  - `/5V_SYS` 정규화 2000회 경고가 반복됐다.
  - 누적 메모리 할당 230GB.
- 수렴하지 않아 중단했다(G-002 GUI 작업 전환, O-59). SES 는 가져오지 않았고 보드 파일은 바뀌지 않았다.
- 위반 821은 DSN 쪽 문제로 추정한다. 프로젝트 DRU(구역 규칙 · 고속 간격 0.30)는 DSN 에 들어가지 않는다. 잠긴 고정 배선도 Freerouting 의 기본 간격과 맞지 않는다. **확인하지 않았다.**
- 판단: 자동 배선 결과가 최적이라고 하지 않는다. 지금 보드는 스크립트 배선기(`route.py`)로 만들었다. 판정은 같은 DRC 종료 코드다.
