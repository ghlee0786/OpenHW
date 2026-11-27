"""VD-001 가상 설계 완료 요약 HTML 한 장을 만든다 (docs/vd001/index.html).

python -I docs/vd001/make_index.py --cond2 <cond2-review.json> --manifest <MANIFEST.tsv> --manifest-src "<커밋 설명>"
        --ev <ev_check json> --ev-src "<입력 커밋 설명>" [--cond5 <cond5-mechanical.json>]
- 저장소 안 결과 파일(ERC·DRC·SIM)은 직접 읽는다. 조건 2·5 결과와 ev_check 결과는 실행 산출물이라 경로를 인자로 받는다.
- 외부 스크립트·폰트·이미지 없음. 체크칸 상태는 그 브라우저(localStorage)에만 남는다.
- 링크는 docs/vd001/ 기준 상대 경로다. 로컬 절대 경로를 쓰지 않는다.
"""
import argparse
import glob
import html
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/vd001/index.html"
E = html.escape


def rel(p):
    """저장소 루트 기준 경로 → docs/vd001/ 기준 링크."""
    return "../../" + p


def last_commit(path):
    r = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%h", "--", path], capture_output=True, text=True)
    return r.stdout.strip() or "—"


def head():
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def drc_rows():
    rows = []
    for b in ("carrier", "front"):
        p = f"hardware/pcb/drc/{b}-drc.json"
        d = load(ROOT / p)
        rows.append((b, len(d["violations"]), len(d["unconnected_items"]), len(d.get("schematic_parity", [])),
                     d.get("date", ""), d.get("kicad_version", ""), p, last_commit(p)))
    return rows


def erc_rows():
    rows = []
    for b in ("carrier", "front"):
        p = f"hardware/schematic/{b}/{b}-erc.json"
        d = load(ROOT / p)
        rows.append((b, sum(len(s["violations"]) for s in d["sheets"]), d.get("date", ""), p, last_commit(p)))
    return rows


def sim_rows():
    out = []
    for f in sorted(glob.glob(str(ROOT / "hardware/sim/results/SIM-*.json"))):
        d = load(f)
        out.append((d["id"], d["title"], d["verdict"], d.get("criteria_commit", "")))
    return out


def manifest_rows(p):
    rows = []
    for line in Path(p).read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            size, sha, path = line.split("\t")
            rows.append((int(size), sha, path))
    return rows


def check(cid, label, detail, links=""):
    return (f'<li class="chk"><label><input type="checkbox" data-id="{E(cid)}"> <b>{E(cid)}</b> {E(label)}</label>'
            f'<div class="d">{detail}{links}</div></li>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond2", required=True)
    ap.add_argument("--cond5")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--manifest-src", required=True)
    ap.add_argument("--ev", required=True)
    ap.add_argument("--ev-src", required=True)
    a = ap.parse_args()

    c2 = load(a.cond2)
    c5 = load(a.cond5) if a.cond5 else None
    ev = load(a.ev)
    drc, erc, sim, man = drc_rows(), erc_rows(), sim_rows(), manifest_rows(a.manifest)
    c2_items = c2["items"]
    c2_fail = sum(1 for i in c2_items if i.get("pass") is False)
    c2_pass = sum(1 for i in c2_items if i.get("pass") is True)
    c2_human = [i for i in c2_items if not i.get("verifiable")]
    sim_pass = sum(1 for s in sim if s[2] == "pass")
    ev_area = {}
    for i in ev["items"]:
        ev_area.setdefault(i["area"], [0, 0])
        ev_area[i["area"]][0] += 1
        ev_area[i["area"]][1] += i["result"] == "불합격"
    ev_unr_script = {k: v["nets"] for k, v in ev["unrouted"].items() if v["nets"]}

    def card(v, label, sub, ok=True):
        return f'<div class="card {"ok" if ok else "ng"}"><div class="big">{E(str(v))}</div><div class="l">{E(label)}</div><div class="s">{sub}</div></div>'

    cards = "".join([
        card("0 · 0", "ERC 위반 (캐리어 · 전면)", "조건 1", all(r[1] == 0 for r in erc)),
        card(" · ".join(f"{r[1]}/{r[2]}/{r[3]}" for r in drc), "DRC 위반/미연결/parity (캐리어 · 전면)", "조건 2", all(r[1] == r[2] == r[3] == 0 for r in drc)),
        card(f"통과 {c2_pass}/{len(c2_items)} · 불합격 {c2_fail}", "review 조건 2 판정 항목", f"사람 확인 {len(c2_human)}", c2_fail == 0),
        card(f"{len(man)}개", "P-004 제조 산출물 파일", E(a.manifest_src), True),
        card(f"{ev['fails']}/{len(ev['items'])}", "ev_check 불합격/판정 항목", "조건 4", ev["fails"] == 0),
        card(f"{sim_pass}/{len(sim)}", "회로 시뮬레이션 통과", "조건 7", sim_pass == len(sim)),
    ])

    t_erc = "".join(f"<tr><td>{b}</td><td>{n}</td><td>{E(dt)}</td><td><a href='{rel(p)}'>{p}</a></td><td><code>{c}</code></td></tr>" for b, n, dt, p, c in erc)
    t_drc = "".join(f"<tr><td>{b}</td><td>{v}</td><td>{u}</td><td>{pa}</td><td>{E(dt)} · KiCad {E(kv)}</td><td><a href='{rel(p)}'>{p}</a></td><td><code>{c}</code></td></tr>"
                    for b, v, u, pa, dt, kv, p, c in drc)
    t_c2 = "".join(f"<tr class='{'' if i.get('pass') is not False else 'bad'}'><td>{E(i['id'])}</td><td>{E(i.get('board', ''))}</td><td>{E(i['title'][:110])}</td>"
                   f"<td>{E(str(i.get('value', ''))[:40])}</td><td>{E(str(i.get('limit', ''))[:30])}</td>"
                   f"<td>{'통과' if i.get('pass') is True else ('불합격' if i.get('pass') is False else '사람 확인')}</td></tr>" for i in c2_items)
    t_ev = "".join(f"<tr><td>{E(k)}</td><td>{n}</td><td>{f}</td></tr>" for k, (n, f) in ev_area.items())
    t_pairs = "".join(f"<tr><td>{r['board']}:{r['name']}</td><td>{r['mismatch_track']:.3f} / {r['mismatch_with_via']:.3f}</td>"
                      f"<td>{(r['uncoupled_outside_twist'] if r['class'] == 'MDI' else r['uncoupled_max']):.3f}</td>"
                      f"<td>{'—' if r['z_min'] is None else '%.1f~%.1f' % (r['z_min'], r['z_max'])}</td></tr>" for r in ev["pairs"])
    t_sim = "".join(f"<tr><td>{E(i)}</td><td>{E(t)}</td><td>{E(v)}</td><td><code>{E(c)}</code></td></tr>" for i, t, v, c in sim)
    t_man = "".join(f"<tr><td>{E(p)}</td><td>{s:,}</td><td><code>{h[:16]}…</code></td></tr>" for s, h, p in man)

    human = []
    for i in c2_human:
        links = " · ".join(f"<a href='{rel(e['path'].split('#')[0]) + ('#' + e['path'].split('#')[1] if '#' in e['path'] else '')}'>{E(e.get('label', e['path']))}</a>"
                           for e in i.get("evidence", []) if not e["path"].startswith("commit:"))
        human.append(check(f"review {i['id']} {i.get('board', '')}", i["title"][:120], f"값 {E(str(i.get('value', '')))} · {E(str(i.get('limit', '')))} — ", links))
    renders = [("REN-006 캐리어 렌더", ["../renders/carrier/carrier-iso.png", "../renders/carrier/carrier-iso-back.png",
                                    "../renders/carrier/carrier-top.png", "../renders/carrier/carrier-bottom.png", "../readme/media/carrier_spin.gif"]),
               ("REN-006 전면 렌더", ["../renders/p005/front-iso.png", "../renders/p005/front-iso-back.png",
                                   "../renders/p005/front-top.png", "../renders/p005/front-bottom.png", "../readme/media/front_spin.gif"]),
               ("REN-006 3층 적층 회전", ["../readme/media/stack_spin.gif"])]
    for name, imgs in renders:
        th = "".join(f"<a href='{p}'><img src='{p}' alt='{E(name)} {os.path.basename(p)}' loading='lazy'></a>" for p in imgs)
        human.append(check(name, "그림이 보드와 맞고 모델 빠짐·색 이상이 없는가", f"<div class='th'>{th}</div>"))
    fusion = [("Fusion 케이스 조립 간섭(눈 확인)", "docs/renders/final/fusion-case-section.png"),
              ("Fusion 케이스 외관·재질", "docs/renders/final/fusion-case-iso.png"),
              ("Fusion 분해도·조립 순서", "docs/renders/final/fusion-case-exploded.png"),
              ("Blender 제품 렌더(정지)", "docs/renders/final/blender-product.png"),
              ("Blender 회전 영상", "docs/renders/final/blender-turntable.mp4")]
    for name, slot in fusion:
        human.append(check(name, "verifiable 아니오 — 자리만", f"<span class='slot'>자리: <code>{slot}</code> (파일 없음, 만들면 이 이름으로)</span>"))

    unr_note = ("" if not ev_unr_script else
                "<p class='s'>ev_check 자체 연결 근사(구리면 넷 제외)가 섬으로 본 넷: "
                + E(", ".join(f"{k} {list(v)}" for k, v in ev_unr_script.items()))
                + " — 판정 항목이 아니고 KiCad 미연결은 0(위 DRC)이다.</p>")
    c5_txt = "" if not c5 else (f"<p>조건 5(mechanical): {len(c5['items'])}항목 · 불합격 {sum(1 for i in c5['items'] if i.get('pass') is False)} · 종료 코드 {c5['exit_code']} · "
                                f"입력 <code>{E(c5['commit'])}</code> · 명령 <code>{E(c5['command'])}</code> (중간 보드 기준 — 최종 보드로 다시)</p>")

    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VD-001 가상 설계 요약</title>
<style>
:root{{--bg:#fff;--fg:#1f2328;--mut:#59636e;--ln:#d0d7de;--card:#f6f8fa;--ok:#1a7f37;--ng:#cf222e;--ac:#0969da}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d1117;--fg:#e6edf3;--mut:#9198a1;--ln:#3d444d;--card:#161b22;--ok:#3fb950;--ng:#f85149;--ac:#4493f8}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI","Noto Sans KR",sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 64px}} a{{color:var(--ac)}} h1{{margin:.2em 0}} h2{{border-bottom:1px solid var(--ln);padding-bottom:.25em;margin-top:2em}}
.s{{color:var(--mut);font-size:13px}} code{{font-size:12px;background:var(--card);padding:1px 4px;border-radius:4px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}}
.card{{background:var(--card);border:1px solid var(--ln);border-radius:10px;padding:12px 14px}} .card .big{{font-size:26px;font-weight:800}}
.card.ok .big{{color:var(--ok)}} .card.ng .big{{color:var(--ng)}} .card .l{{font-weight:600}} .card .s{{font-size:12px}}
table{{border-collapse:collapse;width:100%;font-size:13px;display:block;overflow:auto}} th,td{{border:1px solid var(--ln);padding:4px 8px;text-align:left;vertical-align:top}}
tr.bad td{{color:var(--ng)}} details{{margin:.6em 0}} summary{{cursor:pointer;font-weight:600}}
ul.cl{{list-style:none;padding:0}} li.chk{{border:1px solid var(--ln);border-radius:8px;padding:8px 12px;margin:8px 0}} li.chk .d{{margin:.3em 0 0 1.6em;font-size:13px;color:var(--mut)}}
.th img{{height:120px;margin:4px;border:1px solid var(--ln);border-radius:6px;background:#fff}} .slot{{color:var(--mut)}}
#prog{{font-weight:700}}
</style></head><body><main>
<h1>VD-001 가상 설계 요약</h1>
<p class="s">생성: <code>docs/vd001/make_index.py</code> · 저장소 HEAD <code>{head()}</code> · 판정은 각 도구의 종료 코드와 결과 파일이다. 아래 숫자마다 출처 파일과 커밋을 적었다.
사람 확인 항목(verifiable 아니오)은 체크해야 통과이며, 체크는 이 브라우저에만 남는다.</p>
<div class="cards">{cards}</div>

<h2>사람 확인 <span id="prog"></span></h2>
<ul class="cl">{''.join(human)}</ul>

<h2>조건 1 · 회로도 ERC</h2>
<table><tr><th>보드</th><th>위반</th><th>날짜</th><th>결과 파일</th><th>커밋</th></tr>{t_erc}</table>

<h2>조건 2 · PCB DRC</h2>
<table><tr><th>보드</th><th>위반</th><th>미연결</th><th>parity</th><th>실행</th><th>결과 파일</th><th>커밋</th></tr>{t_drc}</table>
<p>review 조건 2: {len(c2_items)}항목 — 통과 {c2_pass} · 불합격 {c2_fail} · 사람 확인 {len(c2_human)} · 종료 코드 {c2['exit_code']} · 입력 커밋 <code>{E(c2['commit'])}</code> · 생성 {E(c2['generated'])} · 명령 <code>{E(c2['command'])}</code></p>
<details><summary>조건 2 항목 전체 ({len(c2_items)})</summary><table><tr><th>id</th><th>보드</th><th>항목</th><th>값</th><th>한도</th><th>결과</th></tr>{t_c2}</table></details>

<h2>조건 3 · 제조 산출물 (P-004)</h2>
<p>목록 <a href="{rel('manufacturing/pcb/MANIFEST.tsv')}">manufacturing/pcb/MANIFEST.tsv</a> — {len(man)}개 · 합 {sum(s for s, _, _ in man):,} B · 출처 {E(a.manifest_src)}. 제조사에 낸 것은 없다(파일만).</p>
<details><summary>파일 목록 ({len(man)})</summary><table><tr><th>경로 (manufacturing/pcb/ 기준)</th><th>bytes</th><th>sha256</th></tr>{t_man}</table></details>

<h2>조건 4 · 전기 가상 검증 (ev_check)</h2>
<p>{len(ev['items'])}항목 — 불합격 {ev['fails']} · 미배선 {ev['unrouted_items']} · 입력 {E(a.ev_src)} · 명령 <code>python -I docs/research/r020/ev_check.py --config docs/research/r020/ev_config.json --board carrier=… --board front=…</code> · 셈법 D-003 #62 · #63 (문서 <a href="{rel('docs/research/r020-electrical-vv.md')}">r020-electrical-vv.md</a> §9)</p>
<table><tr><th>영역</th><th>항목</th><th>불합격</th></tr>{t_ev}</table>
<table><tr><th>쌍</th><th>쌍 안 길이 차 mm (트랙 / +비아)</th><th>비결합 mm</th><th>Zdiff Ω</th></tr>{t_pairs}</table>
{unr_note}

<h2>조건 5 · 기구</h2>
{c5_txt or '<p class="s">조건 5 결과 파일을 주지 않았다.</p>'}

<h2>조건 7 · 회로 시뮬레이션</h2>
<p>{sim_pass}/{len(sim)} 통과 — <a href="{rel('hardware/sim/results/')}">hardware/sim/results/</a> · 실행 방법 <a href="{rel('hardware/sim/README.md')}">hardware/sim/README.md</a></p>
<details><summary>시뮬레이션 항목 ({len(sim)})</summary><table><tr><th>id</th><th>내용</th><th>판정</th><th>기준 커밋</th></tr>{t_sim}</table></details>

<h2>최종 렌더 (자리)</h2>
<p class="s">Fusion 케이스 렌더와 Blender 렌더는 아직 없다. 위 「사람 확인」의 자리 파일 이름으로 만들면 이 페이지를 다시 생성해 그림을 붙인다.</p>
</main>
<script>
(function(){{var boxes=document.querySelectorAll('input[data-id]');function key(b){{return 'vd001:'+b.getAttribute('data-id');}}
function prog(){{var n=0;boxes.forEach(function(b){{if(b.checked)n++;}});document.getElementById('prog').textContent='('+n+'/'+boxes.length+')';}}
boxes.forEach(function(b){{try{{b.checked=localStorage.getItem(key(b))==='1';}}catch(e){{}}
b.addEventListener('change',function(){{try{{localStorage.setItem(key(b),b.checked?'1':'0');}}catch(e){{}}prog();}});}});prog();}})();
</script>
</body></html>
"""
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print("ok", OUT.relative_to(ROOT), len(page.encode("utf-8")), "B")


if __name__ == "__main__":
    main()
