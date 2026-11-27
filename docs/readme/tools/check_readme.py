"""README·인포그래픽 기계 검사. 종료 코드 = 실패 항목 수.

python -I docs/readme/tools/check_readme.py [--media-root <다른 체크아웃 루트>]
  1. docs/readme/*.svg : XML 파싱 · <script> 0 · 외부 href 0 · ≤ 60 KB · prefers-color-scheme:dark · prefers-reduced-motion
  2. docs/readme/media : *.gif ≤ 5 MB · *.png ≤ 600 KB
  3. README.md 의 상대 링크·이미지 경로가 실제 파일·폴더로 해결되는지 (http(s)·#앵커·mailto 제외)
     --media-root : docs/readme/media/ 가 아직 이 체크아웃에 없을 때(다른 작업에서 만드는 중) 그 루트에서 찾는다
  4. README.md · SVG 금지어 (내부 운영 도구·제조사·비용·로컬 경로·이메일)
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
README = ROOT / "README.md"
SVGDIR = ROOT / "docs/readme"
MEDIA = "docs/readme/media/"
BANNED = [r"\bherdr\b", r"\bhc\b", r"\borch\b", r"칸", r"\bpilot\b", r"pcbway", r"\bjlc", r"\blcsc\b", r"견적", r"비용", r"가격",
          r"[A-Za-z]:[\\/](Users|workspace)", r"[\w.+-]+@[\w-]+\.[\w.]+", r"\bgop\b", r"opennvr", r"ironwall", r"sensorway",
          r"seeed", r"sophgo", r"ghlee"]
# 라이선스 고지 표의 폴더 경로(제3자 저작물 위치)는 금지어 검사에서 뺀다
ALLOW_PATHS = ["hardware/datasheets/sophgo/", "hardware/datasheets/seeed/", "hardware/datasheets/antmicro/"]

fails = []


def fail(msg):
    fails.append(msg)
    print("FAIL", msg)


def check_svg(p):
    raw = p.read_bytes()
    txt = raw.decode("utf-8")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        return fail(f"{p.name}: XML 파싱 오류 {e}")
    tags = [el.tag.split("}")[-1] for el in root.iter()]
    if "script" in tags:
        fail(f"{p.name}: <script> 있음")
    for el in root.iter():
        for k, v in el.attrib.items():
            if k.split("}")[-1] == "href" and not v.startswith("#"):
                fail(f"{p.name}: 외부 href {v}")
    if re.search(r"url\((?!#)", txt) or "@import" in txt:
        fail(f"{p.name}: 외부 url()/@import")
    if len(raw) > 60 * 1024:
        fail(f"{p.name}: {len(raw)} B > 60 KB")
    if "prefers-color-scheme:dark" not in txt.replace(" ", ""):
        fail(f"{p.name}: 어두운 테마 미디어쿼리 없음")
    if "prefers-reduced-motion:reduce" not in txt.replace(" ", ""):
        fail(f"{p.name}: reduced-motion 미디어쿼리 없음")
    if "<animate" in txt:
        fail(f"{p.name}: SMIL <animate> 는 reduced-motion 으로 멈추지 않음 — CSS 애니메이션만")
    print(f"ok  {p.name} {len(raw)} B, 요소 {len(tags)}")


def resolve(link, media_root):
    path = link.split("#")[0].split("?")[0]
    if not path:
        return True
    if (ROOT / path).exists():
        return True
    return media_root is not None and path.startswith(MEDIA) and (media_root / path).exists()


def links(md):
    out = re.findall(r"\]\(([^)\s]+)\)", md)
    out += re.findall(r'<(?:img|a)\b[^>]*?(?:src|href)="([^"]+)"', md)
    return [u for u in out if not re.match(r"(https?:|mailto:|#)", u)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    media_root = Path(args[args.index("--media-root") + 1]) if "--media-root" in args else None
    svgs = sorted(SVGDIR.glob("*.svg"))
    if len(svgs) < 4:
        fail(f"SVG {len(svgs)}개 (4개 필요)")
    for p in svgs:
        check_svg(p)
    for base in [ROOT] + ([media_root] if media_root else []):
        for p in sorted((base / MEDIA).glob("*")):
            lim = {".gif": 5 * 1024 * 1024, ".png": 600 * 1024}.get(p.suffix.lower())
            if lim and p.stat().st_size > lim:
                fail(f"{p.name}: {p.stat().st_size} B > {lim} B")
            elif lim:
                print(f"ok  media {p.name} {p.stat().st_size} B ({base})")
    md = README.read_text(encoding="utf-8")
    ls = links(md)
    bad = [u for u in ls if not resolve(u, media_root)]
    for u in bad:
        fail(f"README 링크 해결 안 됨: {u}")
    print(f"ok  README 링크 {len(ls) - len(bad)}/{len(ls)} 해결")
    for name, text in [("README.md", md)] + [(p.name, p.read_text(encoding="utf-8")) for p in svgs]:
        t = text
        for a in ALLOW_PATHS:
            t = t.replace(a, "")
        for pat in BANNED:
            for m in re.finditer(pat, t, re.I):
                fail(f"{name}: 금지어 /{pat}/ → …{t[max(0, m.start() - 20):m.end() + 20]!r}…")
    print(f"실패 {len(fails)}")
    return len(fails)


if __name__ == "__main__":
    sys.exit(main())
