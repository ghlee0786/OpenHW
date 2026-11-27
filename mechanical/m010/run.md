# M-010 실행 기록 (run_case.py 출력 — 종료 코드 = 막힌 단계 수 0)

- 명령: `python -I -B mechanical/m010/run_case.py --pcb-carrier 6df2865 --pcb-front be3125d`
- 시각: 2026-11-27T09:30:20
- 조건 5 (run_all.py) 종료 코드 0 = 불합격 항목 수 — 막힘 아님

| 단계 | 종료 코드 | 막힘 | 초 |
|---|---|---|---|
| run_all (보드 STEP·M007 조립·J1~J6) | 0 | 아니오 | 75.9 |
| 케이스 params.py ↔ pcb fab 커넥터 (허용 0.05) | 0 | 아니오 | 0 |
| M003 01 새 문서·보드 STEP 가져오기 | 0 | 아니오 | 8.9 |
| M003 02 외함 만들기 (params.py·geom.py) | 0 | 아니오 | 12.8 |
| M003 03 간섭 | 0 | 아니오 | 4.0 |
| M003 04 STEP/STL/f3d 내보내기 | 0 | 아니오 | 7.6 |
| PCB 렌더 (kicad-cli, 모델 연결 사본) | 0 | 아니오 | 465.6 |
| M007 문서 활성 | 0 | 아니오 | 2.9 |
| 메시 내보내기 (Fusion) | 0 | 아니오 | 4.5 |
| GLB carrier | 0 | 아니오 | 9.3 |
| GLB front | 0 | 아니오 | 7.5 |
| Blender 스틸 10 | 0 | 아니오 | 159.6 |
| 치수선 겹침 | 0 | 아니오 | 0.5 |
| 턴테이블 .blend | 0 | 아니오 | 14.1 |
| 턴테이블 렌더·MP4 | 0 | 아니오 | 113.7 |
| 렌더 판정 (judge.py) | 0 | 아니오 | 4.5 |
| 대표본 복사 → C:/Users/gh/AppData/Local/Temp/claude/152719db0d1b2c74/decb4398-40a5-4677-aeb1-556f1d7e2c56/scratchpad/m010/docs_renders | 0 | 아니오 | 0 |

## 조건 5 불합격 항목


## M003 외함 문서 간섭 (validation/runtime/vd001/case/interference.txt)

```
gen 20 / ref 191 bodies, hits involving generated: 3
BLK_J3_PLUG <-> REF_STACK_M002b/HARNESS_CORRIDOR_MX : 0.255 mm3
HW_STANDOFFS <-> REF_STACK_M002b/CORE_BOT_KEEPIN : 30.401 mm3
HW_STANDOFFS <-> REF_STACK_M002b/CORE_TOP_KEEPIN : 22.197 mm3
dropped substitute blocks (board 3D models linked): BLK_CAR_Q3 BLK_CAR_Q4 BLK_FR_Q3 BLK_FR_Q5 BLK_FR_Q7 BLK_FR_X1 BLK_J3_USBC BLK_J5_RJ45 BLK_L1_SRP7028A
```

## 산출 해시 (main 체크아웃 validation/runtime/vd001/)

- boards/carrier.step ad0dfc27fffc7c8867d00d34737477df5514ba9128b97a8feaf0908312b25d09
- boards/front.step 079c78bffc2ee2ba86daedd99a6755e4c6fd2ab41856c5a21654aa00f3ec276a
- case/M003_assembly_with_refs.step bbe73bc2674b608f4a5b0fe4cfe32a91096052dd213d6d7c0b66e344643a05a4
- case/M003_enclosure.f3d bfc07b73f21ff692d3a80205b55f9b816a45e83c22887829e81e7b29df3c4d32
- case/interference.txt 987c8f287844e95305e4153845487b12c66db4b4f108705aa8e1a55955fae7de
- case/step/ALS_WIN_PMMA.step 3e0c97021e3379204a64bb21d16f153fbdda32882ad97ba353c58a528644b784
- case/step/FOAM_ALS_GASKET.step 8ee271287eeec559726638558c2d742b46bc6496b3d6da1c01e8b38deb413325
- case/step/FOAM_LENS_RING.step 0ac884f10843594610a767ebdafa6857a835dc757a76defed14326cf1a3ab193
- case/step/FRONT_COVER.step fae2af859d99bed5098abefa526943cdf3ab10e314bed50a98223dbe2cf48afe
- case/step/GAP_PAD_PX.step a158d7e83b3beeb5c6011dd13bb33f1e170b82441b8cfead0e6a01907810ffd1
- case/step/HOUSING.step bf81ad009aeb4e5c8a75811058bdb8e65f18cfe3bbc9bb7e0906cf03c7a28407
- case/step/HS_EXTRUSION.step 0ddfe1e1506ad8c29712c65c1deb0e469432a1efa6310c5c71869692f14376e1
- case/step/HS_PEDESTAL.step 11965331ecec76bafccfb26ef11ca46c428c0869a61139ff074525e37917d166
- case/step/INS_PADS_P340.step cd2c9e99c41ec207e71da546d2a2f5fed0cb819e7a2d21913267351977ecd7e9
- case/step/LENS_WIN_PMMA.step b5447d0f11979b0e55d0340f6c1df1623041e88bf2ee495cb7ea662b304316d2
- case/step/SPREADER_M003.step 06a257d90eb76ca50001f73eb6414d2dc900b2f9b4e7d80a1278c99ec1924648
- case/step/WIN_A_PMMA.step 9a15a89027e6300fa3e79e612030e14fb072495698295b368de839b566457285
- case/step/WIN_B_PMMA.step 509ac7a7bc7f55bca53fffecb28cd6b7f0303953709f98d3ed4e7da02f863d44
- case/stl/FRONT_COVER.stl 98ec5c78024f4be40adcffe2e3369e7370b38c3e889931be4fb027b17a28f5b3
- case/stl/HOUSING.stl a4bd9a46875710f6732b193fcac3b2a65afe18a11cf6136504a2e18feb982c70
- case/stl/PRINT_COUPON.stl 81b0e09840e222987352a7af581fb52f7d2fc73a849e22e110a06f102450c112
- render/manifest.json 62e9d65ba7940686ad096c11e3b6cf42e2f7bdd406fcc9bb1a5763ae85f9f03a
- render/ren002_turntable.mp4 75e44a089d9760abbca16d97cb085db08376e06930a1e60fac52445f23708b5f
