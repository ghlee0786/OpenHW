# REN-002 렌더 판정·해시 (judge.py 출력 — 불합격 0, 산출 29)

- 3D 모델 감사 (렌더용 사본 pcbsrc/<보드>, pcb carrier 6df2865 · front be3125d + mechanical/models 연결): 빠짐 0
- 산출물: validation/runtime/vd001/render/ (gitignore) · manifest.json (vd001-format §4, 모두 사람 확인 verifiable 아니오 + check 열)

## 입력

| 파일 (validation/runtime/vd001/) | sha256 |
|---|---|
| pcb | carrier 6df2865 · front be3125d |
| m007_assembly.step | 18c1fb0c6f4650b17e9ff59381e621504d7219da4305d5919af14163c86a494d |
| pcbsrc/carrier/hardware/schematic/carrier/carrier.kicad_pcb | ec9f1079998e6e22f824589c0f761d5aeb4ef8ee240fbc772144a4ab71c8fcde |
| pcbsrc/front/hardware/schematic/front/front.kicad_pcb | 4be04083137487d667fa62688509f2a01a05ae5a41a025f2d9b0dca1f1e08df7 |
| render/mesh/index.json | 61076f3fa69bca3cfe0a092dc61998d93e420ffde8c3d01eb9e9520ac3a2a3d6 |
| render/mesh/board_carrier.glb | 4df33390522f96711c62aeee3b565179c190292d9349e87e073ce35ad52bcd56 |
| render/mesh/board_front.glb | a659648eb08ad7712bcc6fd907fa731328545c5d1488090b9e310efe7530a578 |

## 산출

| 파일 | 크기 | sha256 | 판정 |
|---|---|---|---|
| validation/runtime/vd001/render/pcb/carrier_top.png | 2560x1440 | 6925cbc2f8b586b63964134fddd15040b5515aa6a07957d8da9dacdb21fefbd5 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom.png | 2560x1440 | 46d00fba55544c604e0dd8672748b2b6cdab106941cda4905ceb127bd50776fc | 통과 |
| validation/runtime/vd001/render/pcb/carrier_tilt.png | 2560x1440 | e0f02ff8dc176726df4b2982479103fcdbd67a6248d00b7f99b484301e544874 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_top_zoom1.png | 2560x1440 | 5eeaebc714d1e1184564a16567c6f313995d5b30c1c4ff10b2f221dcff459a60 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_top_zoom2.png | 2560x1440 | 16aff89fdfafcf7a67da2b5bb68e4335ef5780ce723968e5457408765097af80 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom_zoom1.png | 2560x1440 | d2f41a19ccda533cfd3b39cf7b05acb27f3e3221e7f0fcaf60d76e166b4206c5 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom_zoom2.png | 2560x1440 | a2b1b1348c1173a320aae92f754dce36b25a869fc0948392ffc2e26248c6afc0 | 통과 |
| validation/runtime/vd001/render/pcb/front_top.png | 2560x1440 | 3d786c68277451a56dd10f6eb976784fc1f85ec287eec796e73c65dce7785452 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom.png | 2560x1440 | a78990392aa8a143a41aa5c4a5e8171f8518badb8a575be549886c8ab13a96f4 | 통과 |
| validation/runtime/vd001/render/pcb/front_tilt.png | 2560x1440 | beeeb65b8792d33252f600694d155cef288cbfff0a00bb187765105645bf297e | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom1.png | 2560x1440 | f289becb3965c137dec56f90068f1520cf56a71ffcd461a4ff14e1b7144ad09b | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom2.png | 2560x1440 | 0a10fa7e45cb86101f21e3d3d1ca0468204135ef7b6d6edbd7d5faff810b3f0c | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom3.png | 2560x1440 | a21a777d394aa8375a7f5d247dec7000ef347880ed354f9a640ce42780a4073e | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom4.png | 2560x1440 | bae0e6cf9a43dbda09493bc401b84f09b4165d3356e3971ce58e68b3b9514f2d | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom1.png | 2560x1440 | cd371bde5da6760b4abeb0a728ee8908af60db58515873ac45dbcda7635b9b37 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom2.png | 2560x1440 | 6ce73f4e13dcbbd8bbe9b522b05271d847c9fc3b24a6e76143975c43fa858d00 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom3.png | 2560x1440 | 15ff787f99f8621914d96a50c0ed4da2d3cbe2b743773145ab1a911236e3ba14 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom4.png | 2560x1440 | 5ca138fc8cabe3a69b94e0cf9efd5b353a14386665a52ea59135ea0d7e702fcd | 통과 |
| validation/runtime/vd001/render/stills/ren002_front.png | 2560x1440 | cff631629671d90937d22c359d4b1be4a6f04f2306af8f8ce5a69a17bf1feaa3 | 통과 |
| validation/runtime/vd001/render/stills/ren002_back.png | 2560x1440 | 12c5600b6776a2be52e64fc8ef070adfd2ca626ae15c72d31222057c534a02e3 | 통과 |
| validation/runtime/vd001/render/stills/ren002_threequarter.png | 2560x1440 | 3f5c80e7f0ef606b148df3c05a56ab0e9213fb07af48f1d11d061e1ad8566821 | 통과 |
| validation/runtime/vd001/render/stills/ren002_exploded.png | 2560x1440 | a740165119d376472706c8d792692be0166a9637bcd71b8858f0a7483ab96b42 | 통과 |
| validation/runtime/vd001/render/stills/ren002_section.png | 2560x1440 | b7213ca2a547cb0d00e9dbe25406d10b6adc2114afc49719c453fa26f6cd216b | 통과 |
| validation/runtime/vd001/render/stills/ren002_window.png | 2560x1440 | 3c24ab05898f4c10608384bd22cc1eaf166837c362efa81993a2aba5bc6a39ea | 통과 |
| validation/runtime/vd001/render/stills/ren002_connectors.png | 2560x1440 | 22de6f0c83e39b93c50d8c7ce25e51533b35ebc4108969a8fc90a29b5867d6ff | 통과 |
| validation/runtime/vd001/render/stills/ren002_microsd.png | 2560x1440 | 7ab1c58bb67b04479c340a121e5f0d7724826c53ee05daa28344eb0a609d1fc1 | 통과 |
| validation/runtime/vd001/render/stills/ren002_inuse.png | 2560x1440 | 854f61acfa58dd242c2ceba74bdd117f76c58a24250735337be7c34e6cd97605 | 통과 |
| validation/runtime/vd001/render/stills/ren002_dims.png | 2560x1440 | e9b4bd50218b77e5f6af218dee16506a0c685237ba3155613263a0f37dd9a8f6 | 통과 |
| validation/runtime/vd001/render/ren002_turntable.mp4 | 1920x1080 h264 프레임 200 · 8.00 s | 75e44a089d9760abbca16d97cb085db08376e06930a1e60fac52445f23708b5f | 통과 |
