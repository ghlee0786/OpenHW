# M-010 실행 기록 (run_case.py 출력 — 종료 코드 = 막힌 단계 수 0)

- 명령: `python -I -B mechanical/m010/run_case.py --pcb-carrier 995b872 --pcb-front 995b872 --case A`
- 시각: 2026-11-28T09:59:27
- 조건 5 (run_all.py) 종료 코드 0 = 불합격 항목 수 — 막힘 아님

| 단계 | 종료 코드 | 막힘 | 초 |
|---|---|---|---|
| run_all --no-fusion (보드 사본·STEP·커넥터) | 0 | 아니오 | 16.9 |
| O-126 시안 A 케이스 (Fusion o126_a.py → case/A) | 0 | 아니오 | 48.7 |
| run_all --case A (보드 STEP·M007 조립·J1~J6) | 0 | 아니오 | 85.8 |
| D5 틈 (10_part_gap, 읽기만) | 0 | 아니오 | 3.0 |

## 조건 5 불합격 항목


## 산출 해시 (main 체크아웃 validation/runtime/vd001/)

- boards/carrier.step 1ffaa95243bd6aed808604b8124904d5bb51abfedf846b2d1c5974491270640d
- boards/front.step 2657c02ec6d086e74ac5bd59fc63b3bb8894bd2b52130f3526b7ff45280740d3
- case/A/A.f3d 8a3e4518dd9eaf38a0413ea571c2d1236424bd635708a894f54fcb46f8bdc940
- case/A/A.step 55666891a2bd8cb2b4b97da3b61ec80fa83ec67e9769a233920ffcef6ed5a5eb
- case/A/A_ALS_WIN_CLEAR.stl 2f437b84bf1a4b81041144cff3147545df282f94d1b339b777a807d97bfec85a
- case/A/A_CABLE_GROMMET.stl 2a91b2087040873fa05dd235c6233d891d923ac23b2359df67cc746bb0bf30bb
- case/A/A_COVER_MICROSD.stl efe070672a9040aac61076a7ebdd1ac99199e0165bd5c9559b0a4e10d49e2b21
- case/A/A_COVER_USBC.stl 74e47fcfa7b5c518805c8e5f7888515fa4d76ef238a643fcf96c5de918e01a24
- case/A/A_FRONT_GLASS_IR.stl 5eb65d811ba922d639f67813d7f927e39a9f9a4d7a70629859aee48eadb1f91d
- case/A/A_GASKET_SPLIT.stl 7cae1037ed2ae786663b9669d25b09ad8c44fb747fab857cef0e4de5070ebe47
- case/A/A_GLASS_MASK.stl 9eb9b2341a4a0b9d7b9ba23bd195b64f23343efa399434c5c30888e692b97cb8
- case/A/A_INNER_MASK_PLATE.stl 97f6a6f77ebee0f525d7ef7dd8e07a4d3bd8fc91f816238dac0eb0665edc8049
- case/A/A_INSERT_1_4_20.stl c2ca5090c69abc83d3fa5fe2df1d478bc45f851a31e8c9754a5b939abab4feed
- case/A/A_INSERT_M25_1.stl b650d23b75a107bc95e2d298068038284d441e83a7cbd73fcf007f76ca0be412
- case/A/A_INSERT_M25_2.stl ebfe012554bf7eaaee25da55da36938012c0a5da6be3f889b6bfc86757d55b01
- case/A/A_INSERT_M25_3.stl c420b1f8c2a14f6b3257d4270515ae8a6c0e0372fcff26da15ceed77fe60e871
- case/A/A_INSERT_M25_4.stl 60064af7b92e1816d36d70881d4ad6f3d5c80bff363dcd3d2cb24cbbc2ce3393
- case/A/A_LENS_WIN_CLEAR.stl 17f89eb9193bc74d68d163b7b903230ca03d5490c42378beb78c71f4dad9b5f7
- case/A/A_LIGHT_PIPE.stl 0bb4dc5a39906e744983bb0d15bb2c29a37101aed2d8a1afa04fe37b2fedda49
- case/A/A_SHELL_ALU.stl 8ae88da6763adf4c64a537d9eec2236c9020fcb26e7dd3bdb74c3a19bed4c446
- case/A/A_SHELL_PLASTIC.stl 675f6d9026ca874ef9ede79d597e84f91863054292afcebb6bdfaf0d70b45e73
- case/A/A_WALL_BRACKET_ARM.stl 7f7e31169fa2ead1da26d01fea9f0c0f3cb2e15a5457f27ceabeff4eac8d9340
- case/A/A_WALL_BRACKET_PAN.stl 276653c1bfac4597affa1c26a96d55859f324a42cc44c614a093d7e1c729b6ee
- case/A/A_WALL_BRACKET_PIN.stl 7680d78c2538a9f352b0009ddb033ec8e9d2f9f76550ea0164aefcd99914d101
- case/A/A_WALL_BRACKET_SCREW.stl c4bb47ac4fa070280c5bc7594ec30e6a588d8970938790c45b8ebd93ce09c999
- case/A/A_WALL_BRACKET_TILT.stl 9266ac4bcb9cc749ac74cc58da7e0c06262daf30bacf923d85a08cec9400bc2a
- case/A/A_view_back.png e21ed27a19ac7990f8f3e61674be13ada3b5655cc5e5c7cbe1d0c767be22e8f1
- case/A/A_view_front.png 92de831d112a212ac31b721537266a1d7da8a74a863a80a5885e84aa2f95add2
- case/A/A_view_section.png dab1ccd11c51956e20ca858726c667d33d44a4f9e56c35e84304b493a40321b9
- case/A/result.json 5a801cfd1d9efb73700810deaa2bb55fc67eed3b491ca22c6d9ae70f29d75ac6
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
