#!/usr/bin/env bash
# V-005 PCB 독립 감수 한 번에 돌리기 (읽기 전용 — pcb 레인 파일을 고치지 않는다)
# 사용: bash docs/review/v005/run_v005.sh <pcb 커밋> [작업 폴더]
#   <pcb 커밋>의 hardware/ 를 git archive 로 작업 폴더에 고정 사본으로 풀고, 두 보드에 대해
#   V-006: test_v006_relax·test_v006_fab·test_v006_vd001_html 시험, v006_relax(완화↔D-003), v006_cond2(조건 2 집계), v006_fab(조건 3)
#   0) test_v005_silk.py 고장 주입 시험  1) kicad-cli pcb drc --severity-all --schematic-parity  2) v005_rules.py
#   3) 회로도 넷리스트(캐소드 핀 기능) → v005_silk.py  3b) v005_excl.py(O-74 제외·라이브러리 사본)  * test_v005_excl.py 고장 주입
#   4) kicad-cli pcb render 앞·뒤, 실크 SVG  5) v005_html.py → validation/runtime/v005/<커밋>/index.html
# 종료 코드: 각 단계 종료 코드를 steps.tsv 에 남기고, 도구 실행 실패(파일 없음 등)가 있으면 1. DRC 위반 자체는 실패로 치지 않는다(판정은 보고서).
set -u
C="${1:?pcb 커밋}"
ROOT="$(git rev-parse --show-toplevel)"
# O-100: 결과(validation/runtime)는 main 체크아웃에 — 레인 worktree 안은 accept 때 지워짐. MAIN_ROOT 로 바꿀 수 있음
MAIN="${MAIN_ROOT:-$(cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && pwd)}"
HERE="$ROOT/docs/review/v005"
# KiCad 10 bin 폴더: KICAD_BIN 으로 주거나, 없으면 사용자 설치 기본 자리(%LOCALAPPDATA%)
KDIR="${KICAD_BIN:-$(cygpath -u "${LOCALAPPDATA:-}")/Programs/KiCad/10.0/bin}"
[ -x "$KDIR/kicad-cli.exe" ] || { echo "kicad-cli 없음: $KDIR (KICAD_BIN 으로 지정)"; exit 1; }
KCLI="$KDIR/kicad-cli.exe"; KPY="$KDIR/python.exe"
OUT="$MAIN/validation/runtime/v005/$C"
WORK="${2:-$OUT/snap}"
mkdir -p "$OUT" "$WORK"
# core.autocrlf=true 이면 archive 가 LF→CRLF 로 바꿔 sha256(E4c·R-010 zip)이 커밋과 달라짐 → 끔 (V-006a)
git -C "$ROOT" -c core.autocrlf=false archive --format=tar "$C" hardware | tar -xf - -C "$WORK" || { echo "archive 실패"; exit 1; }
# 제조 산출물(P-004)이 그 커밋에 있으면 함께 푼다(없으면 조건 3은 「산출물 없음」)
git -C "$ROOT" -c core.autocrlf=false archive --format=tar "$C" manufacturing 2>/dev/null | tar -xf - -C "$WORK" 2>/dev/null || true
: > "$OUT/steps.tsv"; bad=0
step() { local name="$1"; shift; "$@" > "$OUT/$name.log" 2>&1; local rc=$?; printf '%s\t%s\n' "$name" "$rc" >> "$OUT/steps.tsv"; echo "$name exit=$rc"; return $rc; }
step test_silk "$KPY" -I "$HERE/test_v005_silk.py" "$OUT/test" || bad=1
step test_excl "$KPY" -I "$HERE/test_v005_excl.py" "$OUT/test_excl" || bad=1
step test_relax python -I "$HERE/test_v006_relax.py" "$OUT/test_relax" || bad=1
step test_fab python -I "$HERE/test_v006_fab.py" "$WORK/hardware/schematic/carrier/carrier.kicad_pcb" "$OUT/test_fab" || bad=1
step test_esc "$KPY" -I "$HERE/test_v006_esc.py" "$WORK/hardware/schematic/carrier/carrier.kicad_pcb" "$OUT/test_esc" || bad=1
step test_vd001 python -I "$HERE/test_v006_vd001_html.py" "$OUT/test_vd001" || bad=1
for b in carrier front; do
  P="$WORK/hardware/schematic/$b/$b.kicad_pcb"
  [ -f "$P" ] || { echo "없음: $P"; bad=1; continue; }
  step "drc_$b" "$KCLI" pcb drc --severity-all --schematic-parity --exit-code-violations --format json --units mm -o "$OUT/drc_$b.json" "$P"
  step "rules_$b" "$KPY" -I "$HERE/v005_rules.py" "$P" "$OUT/rules_$b.json" || bad=1
  SCH="$WORK/hardware/schematic/$b/$b.kicad_sch"
  step "netlist_$b" "$KCLI" sch export netlist --format kicadsexpr -o "$OUT/$b.net" "$SCH" || bad=1
  step "silk_$b" "$KPY" -I "$HERE/v005_silk.py" "$P" "$OUT/silk_$b.json" --netlist "$OUT/$b.net" || bad=1
  # V-006: 규칙 완화·ignore ↔ D-003 (종료 코드 = 기록 없는 완화 수 — 실행 실패로 치지 않고 판정은 cond2)
  step "relax_$b" python -I "$HERE/v006_relax.py" "$P" "$OUT/relax_$b.json" --d003 "$MAIN/docs/decisions/D-003-working-defaults.md"
  # O-74: 제외·ignore 나열, 허용 종류, pcb 문서 목록 대조, openhw 사본 패드·구멍
  step "excl_$b" "$KPY" -I "$HERE/v005_excl.py" "$P" "$OUT/excl_$b.json" --board-name $b --repo-root "$WORK" --doc $(ls "$WORK"/hardware/pcb/*.md "$WORK"/hardware/pcb/*/*.md 2>/dev/null) || bad=1
  for s in top bottom; do step "render_${b}_$s" "$KCLI" pcb render --side $s --width 1400 --height 1400 --quality high --background opaque -o "$OUT/${b}_$s.png" "$P" || bad=1; done
  step "svgF_$b" "$KCLI" pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet -l F.Silkscreen,F.Mask,Edge.Cuts -o "$OUT/${b}_F_silk.svg" "$P" || bad=1
  step "svgB_$b" "$KCLI" pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet --mirror -l B.Silkscreen,B.Mask,Edge.Cuts -o "$OUT/${b}_B_silk.svg" "$P" || bad=1
  for f in "${b}_top.png" "${b}_bottom.png" "${b}_F_silk.svg" "${b}_B_silk.svg"; do [ -s "$OUT/$f" ] || { echo "출력 없음: $f"; bad=1; }; done
done
step html python -I "$HERE/v005_html.py" "$OUT" "$C" "$OUT" || bad=1
# V-006: VD-001 조건 2 집계 (종료 코드 = 불합격 항목 수, 판정이라 실행 실패로 치지 않음)
# V-006a(O-107): 배선 무관 사전 감수 — R-020 전원 항목·3D 모델 감사(REN-002 audit_models)·참조 지정자 Fab/실크 수 → 수정 요청 목록
EV="$ROOT/docs/research/r020"
[ -f "$EV/ev_check.py" ] && step ev "$KPY" -I "$EV/ev_check.py" --config "$EV/ev_config.json" --board carrier="$WORK/hardware/schematic/carrier/carrier.kicad_pcb" --board front="$WORK/hardware/schematic/front/front.kicad_pcb" --json-out "$OUT/ev.json"
AM="$ROOT/mechanical/ren002/audit_models.py"
[ -f "$AM" ] && step models python -I -B "$AM" --src "$WORK" --out-json "$OUT/models.json" --no-md
for b in carrier front; do step "refs_$b" "$KPY" -I "$HERE/v006a_refs.py" "$WORK/hardware/schematic/$b/$b.kicad_pcb" "$OUT/refs_$b.json" || bad=1; done
step cond2 python -I "$HERE/v006_cond2.py" "$OUT" "$C" "$OUT/cond2.json" --snap "$WORK" --root "$MAIN" --d003 "$MAIN/docs/decisions/D-003-working-defaults.md"
# V-006: VD-001 조건 3 — R-010 16항 (산출물 폴더 manufacturing/pcb/<보드>/ 또는 <보드>.zip, 종료 코드 = 불합격 수)
for b in carrier front; do
  F="$WORK/manufacturing/pcb/$b"; [ -d "$F" ] || F="$WORK/manufacturing/pcb/$b.zip"
  if [ -e "$F" ]; then
    step "fab_$b" python -I "$HERE/v006_fab.py" "$F" "$OUT/cond3-review-$b.json" --board $b --pcb "$WORK/hardware/schematic/$b/$b.kicad_pcb" --commit "$C"
  else
    printf 'fab_%s	산출물 없음(manufacturing/pcb/%s)
' "$b" "$b" >> "$OUT/steps.tsv"; echo "fab_$b 산출물 없음"
  fi
done
step pre python -I "$HERE/v006a_pre.py" "$OUT" "$C" "$OUT/pre.json" "$OUT/pre.md" --root "$MAIN"
# VD-001 결과 자리로 복사 (docs/review/vd001-format.md §1)
mkdir -p "$MAIN/validation/runtime/vd001/results"
cp "$OUT/cond2.json" "$MAIN/validation/runtime/vd001/results/cond2-review.json" 2>/dev/null
for b in carrier front; do [ -f "$OUT/cond3-review-$b.json" ] && cp "$OUT/cond3-review-$b.json" "$MAIN/validation/runtime/vd001/results/"; done
mkdir -p "$MAIN/validation/runtime/vd001/pre-review/$C" && cp "$OUT/pre.json" "$OUT/pre.md" "$MAIN/validation/runtime/vd001/pre-review/$C/" 2>/dev/null
echo "결과: $OUT (steps.tsv)"; exit $bad
