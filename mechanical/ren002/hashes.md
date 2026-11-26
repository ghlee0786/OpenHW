# REN-002 렌더 판정·해시 (judge.py 출력 — 불합격 0, 산출 29)

- 3D 모델 감사 (렌더용 사본, pcb 23fd8da + mechanical/models 연결): 빠짐 0
- 산출물: validation/runtime/vd001/render/ (gitignore) · manifest.json (vd001-format §4, 모두 사람 확인 verifiable 아니오 + check 열)

## 입력

| 파일 (validation/runtime/vd001/) | sha256 |
|---|---|
| pcb | 23fd8da |
| m007_assembly.step | d2e4da4fc8f284c8ad4939679b0ccf7093b580244a8a864681784f316a05745f |
| ren002/rendersrc/hardware/schematic/carrier/carrier.kicad_pcb | 15b8dd8228085e14ecc6e3b177fcfc30b8438b60052286e99300848d9845f55e |
| ren002/rendersrc/hardware/schematic/front/front.kicad_pcb | ca5b24522b4115930faef743973468c234efee7f2f094d8ef6cf03723721fec0 |
| render/mesh/index.json | 61076f3fa69bca3cfe0a092dc61998d93e420ffde8c3d01eb9e9520ac3a2a3d6 |
| render/mesh/board_carrier.glb | d0debdfa569030e022baacc7448fa71af39b7c4629d502da520231263e0d8350 |
| render/mesh/board_front.glb | 686bc3309eb45d47414967ca9c35992261e61b07236ea2e3c6970382b1993708 |

## 산출

| 파일 | 크기 | sha256 | 판정 |
|---|---|---|---|
| validation/runtime/vd001/render/pcb/carrier_top.png | 2560x1440 | 92f60774c3ae6e2c05d813f96c7b57e9ad1a84bfced8add845ead3330d95652d | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom.png | 2560x1440 | 2ab694647b04c37fd20876a71a048b70865befabf57a4ce5524b05ba6a1b80e7 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_tilt.png | 2560x1440 | 3d525c2a32fc937468c1ef93efdaba06074274bafd5d813a061eb095f07272f1 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_top_zoom1.png | 2560x1440 | cf339497cc32693be54c9b55e35bcfb8d2d2af44402731d85afd15f541ed9977 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_top_zoom2.png | 2560x1440 | fc1bb5a492a9a4af0f0252a518c78eb21bb676654a46de40c4866f987ad5b45d | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom_zoom1.png | 2560x1440 | 0197ddf28be46ef50b88168632abe45568e62ebcb671e7a8dffb1335427c87d5 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom_zoom2.png | 2560x1440 | 823aae78ac66195dca0ab00ff07746271341ad05ba4296a862b5f3e57e98272f | 통과 |
| validation/runtime/vd001/render/pcb/front_top.png | 2560x1440 | 070c78269c2a36f5201553c22d224ab9751099d0df7e4c2d43294bd442313a8c | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom.png | 2560x1440 | 0499e224747b947942dc3d7147a4ca2a830e348ce0f9d74ef8007a92dbe679d5 | 통과 |
| validation/runtime/vd001/render/pcb/front_tilt.png | 2560x1440 | 2c32a5d988c0037cd582321a0cde4e050ec21b3e72d3436f7f225ae61ac79433 | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom1.png | 2560x1440 | 7217c0b46e7c34dfea7b339469247ba64c0da7a9249b63ef6843760e187bde33 | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom2.png | 2560x1440 | 677762c49b6f0ee1676b773c725cea9016d4aca60b552e5507f9a7bdf886b72c | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom3.png | 2560x1440 | 38227925467c42008364e890b3c1a22206c13fe18e2c0701d8ad7701b9ba5421 | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom4.png | 2560x1440 | 20ea0f046f4dfaead5f7e15d7df0215ef136db8471d6beba8a455daf406b285f | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom1.png | 2560x1440 | 54cfc32d75703027329f810bfe5f9bc7ea81c1f72233bc30f4a4a48295968588 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom2.png | 2560x1440 | 5f5d096a741bebd0efa574f22f5c4df1daaf2d9300092f18e599fe9b6baaaab4 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom3.png | 2560x1440 | 8a4d8656aed887c38b7d901c0deff1465919d62e6f0e8542add33c5d7da46b14 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom4.png | 2560x1440 | 55d24c23839f1273d88a09b58589745a27d084cf275813da33735d70ca9824ad | 통과 |
| validation/runtime/vd001/render/stills/ren002_front.png | 2560x1440 | b21df03eb8e8371150279e01579f6587b198d7635027a1f5e23263b2a276d4bf | 통과 |
| validation/runtime/vd001/render/stills/ren002_back.png | 2560x1440 | dacbb809b4e1526fe6d7ee13f9ddd2a7bd796544a22dcf539d6e39fa5785d61c | 통과 |
| validation/runtime/vd001/render/stills/ren002_threequarter.png | 2560x1440 | f7d908857da4d3698eb0a0fbd3444b70f8ec50fad2aeae8760fb25bd3a318f7a | 통과 |
| validation/runtime/vd001/render/stills/ren002_exploded.png | 2560x1440 | 3b05a8277c206b60d5f751e50c7422fc2f03ad5b4cb206496edc0f114506007d | 통과 |
| validation/runtime/vd001/render/stills/ren002_section.png | 2560x1440 | b93dc39619e812213a5249a4f94716bd5386b562b557c9242dd3dec08a9b2231 | 통과 |
| validation/runtime/vd001/render/stills/ren002_window.png | 2560x1440 | 52c1487a5e6c012e5b79ce1004cb6fb57aa18d4f90664beb4c57c743ca8cd0f1 | 통과 |
| validation/runtime/vd001/render/stills/ren002_connectors.png | 2560x1440 | 771c14101047ec94ccc5767342a094d63aa5316808092255458343333e5b09c8 | 통과 |
| validation/runtime/vd001/render/stills/ren002_microsd.png | 2560x1440 | cfeea3920ebe546bf7b384a7c9909010e502293e57e52d7de2c44594ead491f8 | 통과 |
| validation/runtime/vd001/render/stills/ren002_inuse.png | 2560x1440 | eb9ba2c4c85b79754d432e4615048274bb63de6c2c11361aa3a47b684c34643e | 통과 |
| validation/runtime/vd001/render/stills/ren002_dims.png | 2560x1440 | 366f430cbc4f232bc662d1c0bbad9f34f5a0925a32bcc81b6ddea6429bbc2ffe | 통과 |
| validation/runtime/vd001/render/ren002_turntable.mp4 | 1920x1080 h264 프레임 200 · 8.00 s | 203f2bb437bfdd88d6ab15f9fd2583682bc0f104499d555e1dae72ba11b3df11 | 통과 |
