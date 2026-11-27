# REN-002 렌더 판정·해시 (judge.py 출력 — 불합격 0, 산출 29)

- 3D 모델 감사 (렌더용 사본 pcbsrc/<보드>, pcb 995b872 + mechanical/models 연결): 빠짐 0
- 산출물: validation/runtime/vd001/render/ (gitignore) · manifest.json (vd001-format §4, 모두 사람 확인 verifiable 아니오 + check 열)

## 입력

| 파일 (validation/runtime/vd001/) | sha256 |
|---|---|
| pcb | 995b872 |
| m007_assembly.step | 93537dc84a4c3ab074995881690d9a276e419744751de305318f60604f0b315f |
| pcbsrc/carrier/hardware/schematic/carrier/carrier.kicad_pcb | 3a80e59686070d8360680fa20f786dc13366ac33652f47360f5469b05df1401a |
| pcbsrc/front/hardware/schematic/front/front.kicad_pcb | b4559925cff00ae1554daeee4e473409f6878b629548d45331ae552cfb6000d9 |
| render/mesh/index.json | 61076f3fa69bca3cfe0a092dc61998d93e420ffde8c3d01eb9e9520ac3a2a3d6 |
| render/mesh/board_carrier.glb | 8858cafd569da95c56ca6c49be293286c48981aa50d4e0e31b332c7ff8a59752 |
| render/mesh/board_front.glb | d82ebae103bf6801f8c835072dee42a171ed0e73fa32a1e2e8ddeb7a9814e13b |

## 산출

| 파일 | 크기 | sha256 | 판정 |
|---|---|---|---|
| validation/runtime/vd001/render/pcb/carrier_top.png | 2560x1440 | 7186280a5ba1f2ba4125a8905bb11d6c42eac98cd74b3de19ee42e47f5ad6ca4 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom.png | 2560x1440 | 0d0b49d8d403e1f919005efdafb4363190c2ed30a448c5d0ea04c4a6ab23a4fd | 통과 |
| validation/runtime/vd001/render/pcb/carrier_tilt.png | 2560x1440 | 483f1b62c9a495893e8492d1ff88bbf298101b7dd49e1506a84206a053bd2806 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_top_zoom1.png | 2560x1440 | fbe940f983d6baf384534227ae671ec02993ca09728bc0df957edecdd0b461d3 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_top_zoom2.png | 2560x1440 | 105cca1f3ec4dbbcc40bce8159bee73a4d75b7c3421f98e4c3dc325b0dbfe55a | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom_zoom1.png | 2560x1440 | 7926f2c7b6ff976a2793757066448de3fb5ddb320efdbf8cfce0b986196dfc46 | 통과 |
| validation/runtime/vd001/render/pcb/carrier_bottom_zoom2.png | 2560x1440 | cdcbf76830bc3a5861e98d859035105df25565796c276bdc714611657176d181 | 통과 |
| validation/runtime/vd001/render/pcb/front_top.png | 2560x1440 | 5366939c51f882ec5ed492689a7a2af07fe4a1ee6e82e7f12c2061c4ea8e9cf3 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom.png | 2560x1440 | 12c0c3e55797236db0b0df38c7b6f3dbc802f90c2ca850cef6a4fee6eb7e608a | 통과 |
| validation/runtime/vd001/render/pcb/front_tilt.png | 2560x1440 | b6f6d511e689f07ca7e1967ae453b37367b7d975cf1bc1abb2f2a0a1e5e613bc | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom1.png | 2560x1440 | 7d7aef9ae79515b15caa6380cdd7c43276e6e025f7dddb23d5eea160f430803c | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom2.png | 2560x1440 | d8deead1ad4a3d9f082c109438a69b6cde73203a385c13f8361e4aab46a21e7e | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom3.png | 2560x1440 | 6ede48fec17cadc460ce9a56f3a28b185d64f8a57f7b0f4f8d24609c2c1ac471 | 통과 |
| validation/runtime/vd001/render/pcb/front_top_zoom4.png | 2560x1440 | 2dc0a55ecd52e10e3e930f96fb25fc12caa3bc251e4f51395de371f921f5c3ab | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom1.png | 2560x1440 | 73cb316a2b649712239c6ad1dc603c2397a3ea032888401fd491a1c04cc5c001 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom2.png | 2560x1440 | f39f9d428f6693d06b28f559ebd7eeb91363709ad5d2c5c304ed0170dc5a8e02 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom3.png | 2560x1440 | d9da80850ab1502572236744528359ee3b200585d34638d8c61e29f02f476688 | 통과 |
| validation/runtime/vd001/render/pcb/front_bottom_zoom4.png | 2560x1440 | 0d39f1b6eecf815c8aad533bbe009ff6e2f01168b20df0b8d20eef58c59d8354 | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_front.png | 2560x1440 | 0b6c9d23098f1f756d0fb3956142c8a258fc184a0ba8100e2b413c9a70d87fbe | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_back.png | 2560x1440 | af624eeb83bf8e69e54069966077813369de773fabfccb92740500edba98652e | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_threequarter.png | 2560x1440 | 834f79a04abca99347ff4fd2533f8c0d960ee431f69aabae91e315f4c2e24ae5 | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_exploded.png | 2560x1440 | 0f42501605e9f9558c285716e1e61eb5f17720866b8b939f2ba81f6bd3aa6c84 | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_section.png | 2560x1440 | d0cb33d44f311a8928d8d80afa1cfa0cb30c701063d7edb3075d23c359d6b806 | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_window.png | 2560x1440 | 3c15e2efb61594672d0c6a160e310d9b40acea9c7a68cb845afdda54ae921c84 | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_connectors.png | 2560x1440 | 138eb365acb0673231652aaee1f2916a11b6add7d310339bd47b15e55094423a | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_microsd.png | 2560x1440 | 4ea64158c4d459b557ab36a18466dfd19ad62a34d662c13e32b148248fc3a26a | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_inuse.png | 2560x1440 | 32653401c4e5f8b2f3585d9736bb92c9008ea46c8b3f0665de9be08fd239d57c | 통과 |
| validation/runtime/vd001/render/blender/stills/ren002_dims.png | 2560x1440 | abbfd4ce385bdbaeebb2fce73a0ef790c4a5c8d204dc0c391383d696f8e275ee | 통과 |
| validation/runtime/vd001/render/blender/ren002_turntable.mp4 | 1920x1080 h264 프레임 200 · 8.00 s | 798c50a8608d97d520073bd3c56790f758580af6eda5c29fb831a68926c63f19 | 통과 |
