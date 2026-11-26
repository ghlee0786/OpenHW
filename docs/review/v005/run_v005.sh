#!/usr/bin/env bash
# V-005 PCB 독립 감수 한 번에 돌리기 (읽기 전용 — pcb 레인 파일을 고치지 않는다)
# 사용: bash docs/review/v005/run_v005.sh <pcb 커밋> [작업 폴더]
#   <pcb 커밋>의 hardware/ 를 git archive 로 작업 폴더에 고정 사본으로 풀고, 두 보드에 대해
#   1) kicad-cli pcb drc --severity-all --schematic-parity  2) v005_rules.py  3) v005_silk.py
#   4) kicad-cli pcb render 앞·뒤, 실크 SVG  5) v005_html.py → validation/runtime/v005/<커밋>/index.html
# 종료 코드: 각 단계 종료 코드를 steps.tsv 에 남기고, 도구 실행 실패(파일 없음 등)가 있으면 1. DRC 위반 자체는 실패로 치지 않는다(판정은 보고서).
set -u
C="${1:?pcb 커밋}"
ROOT="$(git rev-parse --show-toplevel)"
HERE="$ROOT/docs/review/v005"
KDIR="${KICAD_BIN:-/c/Users/gh/AppData/Local/Programs/KiCad/10.0/bin}"
KCLI="$KDIR/kicad-cli.exe"; KPY="$KDIR/python.exe"
OUT="$ROOT/validation/runtime/v005/$C"
WORK="${2:-$OUT/snap}"
mkdir -p "$OUT" "$WORK"
git -C "$ROOT" archive --format=tar "$C" hardware | tar -xf - -C "$WORK" || { echo "archive 실패"; exit 1; }
: > "$OUT/steps.tsv"; bad=0
step() { local name="$1"; shift; "$@" > "$OUT/$name.log" 2>&1; local rc=$?; printf '%s\t%s\n' "$name" "$rc" >> "$OUT/steps.tsv"; echo "$name exit=$rc"; return $rc; }
for b in carrier front; do
  P="$WORK/hardware/schematic/$b/$b.kicad_pcb"
  [ -f "$P" ] || { echo "없음: $P"; bad=1; continue; }
  step "drc_$b" "$KCLI" pcb drc --severity-all --schematic-parity --exit-code-violations --format json --units mm -o "$OUT/drc_$b.json" "$P"
  step "rules_$b" "$KPY" -I "$HERE/v005_rules.py" "$P" "$OUT/rules_$b.json" || bad=1
  step "silk_$b" "$KPY" -I "$HERE/v005_silk.py" "$P" "$OUT/silk_$b.json" || bad=1
  for s in top bottom; do step "render_${b}_$s" "$KCLI" pcb render --side $s --width 1400 --height 1400 --quality high --background opaque -o "$OUT/${b}_$s.png" "$P" || bad=1; done
  step "svgF_$b" "$KCLI" pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet -l F.Silkscreen,F.Mask,Edge.Cuts -o "$OUT/${b}_F_silk.svg" "$P" || bad=1
  step "svgB_$b" "$KCLI" pcb export svg --mode-single --page-size-mode 2 --exclude-drawing-sheet --mirror -l B.Silkscreen,B.Mask,Edge.Cuts -o "$OUT/${b}_B_silk.svg" "$P" || bad=1
  for f in "${b}_top.png" "${b}_bottom.png" "${b}_F_silk.svg" "${b}_B_silk.svg"; do [ -s "$OUT/$f" ] || { echo "출력 없음: $f"; bad=1; }; done
done
step html python -I "$HERE/v005_html.py" "$OUT" "$C" "$OUT" || bad=1
echo "결과: $OUT (steps.tsv)"; exit $bad
