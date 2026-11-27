# M-010 실행 기록 (run_case.py 출력 — 종료 코드 = 막힌 단계 수 0)

- 명령: `python -I -B mechanical/m010/run_case.py --pcb-carrier 995b872 --pcb-front 995b872`
- 시각: 2026-11-27T16:49:12
- 조건 5 (run_all.py) 종료 코드 0 = 불합격 항목 수 — 막힘 아님

| 단계 | 종료 코드 | 막힘 | 초 |
|---|---|---|---|
| run_all (보드 STEP·M007 조립·J1~J6) | 0 | 아니오 | 31.8 |
| 케이스 params.py ↔ pcb fab 커넥터 (허용 0.05) | 0 | 아니오 | 0 |
| M003 01 새 문서·보드 STEP 가져오기 | 0 | 아니오 | 3.3 |
| M003 02 외함 만들기 (params.py·geom.py) | 0 | 아니오 | 4.7 |
| M003 03 간섭 | 0 | 아니오 | 3.9 |
| M003 04 STEP/STL/f3d 내보내기 | 0 | 아니오 | 3.1 |
| PCB 렌더 (kicad-cli, 모델 연결 사본) | 0 | 아니오 | 373.6 |
| M007 문서 활성 | 0 | 아니오 | 0.4 |
| 메시 내보내기 (Fusion) | 0 | 아니오 | 1.8 |
| GLB carrier | 0 | 아니오 | 7.7 |
| GLB front | 0 | 아니오 | 4.7 |
| Blender 스틸 10 | 0 | 아니오 | 151.3 |
| 치수선 겹침 | 0 | 아니오 | 1.7 |
| 턴테이블 .blend | 0 | 아니오 | 13.3 |
| 턴테이블 렌더·MP4 | 0 | 아니오 | 85.3 |
| 렌더 판정 (judge.py) | 0 | 아니오 | 1.1 |
| 대표본 복사 → (저장소 밖 폴더) | 0 | 아니오 | 0 |

## 조건 5 불합격 항목


## M003 외함 문서 간섭 (validation/runtime/vd001/case/interference.txt)

```
gen 20 / ref 190 bodies, hits involving generated: 3
BLK_J3_PLUG <-> REF_STACK_M002b/HARNESS_CORRIDOR_MX : 0.255 mm3
HW_STANDOFFS <-> REF_STACK_M002b/CORE_BOT_KEEPIN : 30.401 mm3
HW_STANDOFFS <-> REF_STACK_M002b/CORE_TOP_KEEPIN : 22.197 mm3
dropped substitute blocks (board 3D models linked): BLK_CAR_Q3 BLK_CAR_Q4 BLK_FR_Q3 BLK_FR_Q5 BLK_FR_Q7 BLK_FR_X1 BLK_J3_USBC BLK_J5_RJ45 BLK_L1_SRP7028A
```

## 산출 해시 (main 체크아웃 validation/runtime/vd001/)

- boards/carrier.step e663efb45eb42b0ed49c5dc6f5a859805b9d20f58198d5ab92fc9da1208370b0
- boards/front.step d8db5f01b5ebb07072aaf043411714031c892c2f4cf1ae397867ac7e8ca3ce77
- case/M003_assembly_with_refs.step 925dafe625fb6dc3d1dc54d184b87580f125c002e77a5011c2b4ce0fb7a02b31
- case/M003_enclosure.f3d 5fa128ac711f70954e2f334326835d0679ab9b05a80d404e3f789fcb9605b2f8
- case/interference.txt 48f96085ffc3bf808723beec508272b5aee262606e3d918d815a8018671e55f7
- case/step/ALS_WIN_PMMA.step 0487edf5f548b8ce9c455a1659c2b350d6b24cc127d775b68edfb1035e5893e6
- case/step/FOAM_ALS_GASKET.step cbab598fba0c69a7de01c52779027225d66d78d95d87265c1f24e201f10ab07a
- case/step/FOAM_LENS_RING.step 281437f1399aa4be7406029361bd07dbae22e59209f6ecf8719f36f76d4127ee
- case/step/FRONT_COVER.step 964f7f8bea8e45a8dd4c2eaaa343da81ae9f058f1f46bf5dbc4a0a31f06b2c22
- case/step/GAP_PAD_PX.step ad501035a32b987ce9ec1c592075b9431f97f77683944b117b28c80e9ac24e30
- case/step/HOUSING.step fbd5053e4619efc7cd61a4b3dd661c7f0a27b648e21d732b00bd69a27d151907
- case/step/HS_EXTRUSION.step ce515d88a49738b2d2161ffd88495d15ba5673a097dcaa2424c3c473373b1af5
- case/step/HS_PEDESTAL.step a62ef2f95d3b993189608b875b2da265709e3154106b651f926a4b1eb528ef49
- case/step/INS_PADS_P340.step b3bf236331245300c36aceb954a17cf37fee06660a0c3f3e1b08260afab25cd4
- case/step/LENS_WIN_PMMA.step 3b61ff73cb9b188965aa90cbcb5d25e6e4d0967537dc6b38a1ae812fca77a7c5
- case/step/SPREADER_M003.step c46cfae8d672e5dbd51fa67ca940441c6ac6568b02523f82150b69b89523197b
- case/step/WIN_A_PMMA.step f2350bee26deda3436ea912649e12c904a787de2d479719a665df8d1db4f0cf8
- case/step/WIN_B_PMMA.step 218ec8da9e84b807c321691137ee6db9e59236a68f7a606ee518f6f3bbdd590f
- case/stl/FRONT_COVER.stl 98ec5c78024f4be40adcffe2e3369e7370b38c3e889931be4fb027b17a28f5b3
- case/stl/HOUSING.stl a4bd9a46875710f6732b193fcac3b2a65afe18a11cf6136504a2e18feb982c70
- case/stl/PRINT_COUPON.stl 81b0e09840e222987352a7af581fb52f7d2fc73a849e22e110a06f102450c112
- render/blender/ren002_turntable.mp4 798c50a8608d97d520073bd3c56790f758580af6eda5c29fb831a68926c63f19
- render/manifest.json f890f61eba2a6fa7321ada6b478deebd58bb7b809010c636a61d7d5a1ebe188e
