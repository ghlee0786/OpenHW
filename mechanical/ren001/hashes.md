# REN-001 렌더 해시 (judge.py 출력 — 불합격 0)

- 산출물: validation/runtime/vd001/render/ (gitignore) · manifest.json (vd001-format §4)
- 보기 확인은 사람 눈(verifiable 아니오) — VD-001 HTML 에서 체크

## 입력

| 파일 (validation/runtime/vd001/) | sha256 |
|---|---|
| m007_assembly.step | a330f6b21abffd1ca11b444283c3158b42e44988c840d3c120454ce4d01ecef7 |
| pcbsrc/hardware/schematic/carrier/carrier.kicad_pcb | db82652a5e7adaba3ada980c38d987183e6f427212276d7a4c08cf0f2de45422 |
| pcbsrc/hardware/schematic/front/front.kicad_pcb | c546c86b922f7f2477003ce9cbf70e673ee9141d79266991eb3d1544b0ce9944 |
| render/mesh/index.json | 27383cccf4903f1c6e047d840ccb0c33645c6ba84588beb0cc04ddd00f0600e4 |
| render/mesh/board_carrier.glb | 010da8a40df37d9bfcc968a233a7aaf1e66ee74806ae0929c735160b51f15b92 |
| render/mesh/board_front.glb | 968ebc0bf79e51c68cce49f15413a1e2d5cc5519c45153cae50824097970081c |

## 산출

| 파일 | 크기 | sha256 | 판정 |
|---|---|---|---|
| validation/runtime/vd001/render/pcb/carrier_top.png | 2560x1440 | 70f14954730f5b04f0519e9ecae45c9a1a88801c157c53ba5ccc3026ffaa7633 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom.png | 2560x1440 | 7e8b9602e4c65d4f7d7569904dac8629a256d88fa5dede86a55d0e665f1593b3 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_tilt.png | 2560x1440 | 369290b692c5d20eec564380710d2d4774ad6769a8309ed35ca9c83035e115d9 | 통과 |
| validation/runtime/vd001/render/pcb/front_top.png | 2560x1440 | 5b61de2a9443a71b8f3468cb1062fe5261554b78d65411ca5fa2f16c7b743fdc | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom.png | 2560x1440 | 96ade7219de4d9c3080a5721fbf1a452cef8add7d0f6113483238d7e07afb996 | 통과 |
| validation/runtime/vd001/render/pcb/front_tilt.png | 2560x1440 | 54b88e5aeaac684f24927b908a6c51dfc0d5cb14a7b4afaa4d5fa67ca64b70bc | 통과 |
| validation/runtime/vd001/render/stills/ren001_front.png | 2560x1440 | eba6f01cbb912005496c84e0755c9f63a13380d5e7e838a9b2ba1a16140ff9ae | 통과 |
| validation/runtime/vd001/render/stills/ren001_back.png | 2560x1440 | e75a704088041f612cf3b0c1dd792ac007e5b7cfe329809f5a57f35d5206728a | 통과 |
| validation/runtime/vd001/render/stills/ren001_threequarter.png | 2560x1440 | 0858d66827c4f9d9d0bb32b52b2c8504f520d677c3c83853f465e126a2afa869 | 통과 |
| validation/runtime/vd001/render/stills/ren001_exploded.png | 2560x1440 | 011fbf2a13e5e1f9025ecdbb9b1c079b62d8f2e8f3e6dfba804039bb677d34a5 | 통과 |
| validation/runtime/vd001/render/stills/ren001_section.png | 2560x1440 | 21a997a77d786aa2b9ca99301a3a9b368362ca5ad1a1e001d4be3bf8eaeff473 | 통과 |
| validation/runtime/vd001/render/stills/ren001_window.png | 2560x1440 | ce4124b6ba80a8334bff4d1d769f6f76a9be6da9b4b71739323634ca278cb3eb | 통과 |
| validation/runtime/vd001/render/ren001_turntable.mp4 | 1920x1080 h264 프레임 200 · 8.00 s | 9d40355a6933ae3a1d0ef0ded2451f3bc8fb9105af74ba5e4dc1948fdde0982d | 통과 |
