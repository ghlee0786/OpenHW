"""README·인포그래픽 기계 검사. 종료 코드 = 실패 항목 수.

python -I docs/readme/tools/check_readme.py [--media-root <다른 체크아웃 루트>] [--banned-file <파일>]
  1. docs/readme/*.svg : XML 파싱 · <script> 0 · 외부 href 0 · ≤ 60 KB · prefers-color-scheme:dark · prefers-reduced-motion
  2. docs/readme/media · docs/readme/gallery : *.gif ≤ 5 MB · *.png ≤ 600 KB
  3. README.md 의 상대 링크·이미지 경로가 실제 파일·폴더로 해결되는지 (http(s)·#앵커·mailto 제외)
     --media-root : docs/readme/media/·gallery/ 가 아직 이 체크아웃에 없을 때(다른 작업에서 만드는 중) 그 루트에서 찾는다
  4. README.md · SVG 금지어 — 기본: 로컬 경로·이메일·견적/비용/가격
     --banned-file <파일> : 저장소 밖에 둔 추가 금지어 정규식(한 줄에 하나, # 주석) — 공개 저장소에 이름 목록을 싣지 않으려고
  5. README 에 보이는 이미지(<img>·![]()): alt 누락 0 · 종류별 크기(svg ≤ 60 KB · png/jpg ≤ 600 KB · gif ≤ 5 MB) · 합 ≤ 15 MB
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
README = ROOT / "README.md"
SVGDIR = ROOT / "docs/readme"
MEDIA = ("docs/readme/media/", "docs/readme/gallery/")
IMG_LIMIT = {".svg": 60 * 1024, ".png": 600 * 1024, ".jpg": 600 * 1024, ".gif": 5 * 1024 * 1024}
IMG_TOTAL = 15 * 1024 * 1024
BANNED = [r"견적", r"비용", r"가격", r"[A-Za-z]:[\\/](Users|workspace)", r"[\w.+-]+@[\w-]+\.[\w.]+"]
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


def find(link, media_root):
    """링크가 가리키는 파일(또는 폴더) 경로, 없으면 None."""
    path = link.split("#")[0].split("?")[0]
    if (ROOT / path).exists():
        return ROOT / path
    if media_root is not None and path.startswith(MEDIA) and (media_root / path).exists():
        return media_root / path
    return None


def resolve(link, media_root):
    return not link.split("#")[0].split("?")[0] or find(link, media_root) is not None


def images(md):
    """README 에 보이는 이미지: (src, alt) — <img> 태그와 마크다운 ![alt](src)."""
    out = []
    for tag in re.findall(r"<img\b[^>]*>", md):
        src = re.search(r'src="([^"]+)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        out.append((src.group(1) if src else "", alt.group(1).strip() if alt else ""))
    out += [(src, alt.strip()) for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)\)", md)]
    return out


def links(md):
    out = re.findall(r"\]\(([^)\s]+)\)", md)
    out += re.findall(r'<(?:img|a)\b[^>]*?(?:src|href)="([^"]+)"', md)
    return [u for u in out if not re.match(r"(https?:|mailto:|#)", u)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    media_root = Path(args[args.index("--media-root") + 1]) if "--media-root" in args else None
    if "--banned-file" in args:
        for line in Path(args[args.index("--banned-file") + 1]).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                BANNED.append(line.strip())
    svgs = sorted(SVGDIR.glob("*.svg"))
    if len(svgs) < 4:
        fail(f"SVG {len(svgs)}개 (4개 필요)")
    for p in svgs:
        check_svg(p)
    for base in [ROOT] + ([media_root] if media_root else []):
        for p in sorted(f for d in MEDIA for f in (base / d).rglob("*")):
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
    imgs, total, seen = images(md), 0, set()
    for src, alt in imgs:
        if not alt:
            fail(f"README 이미지 alt 없음: {src}")
        if re.match(r"https?:", src):
            continue
        f = find(src, media_root)
        lim = IMG_LIMIT.get(Path(src).suffix.lower())
        if f is None or not f.is_file():
            continue  # 해결 안 된 경로는 위 링크 검사에서 센다
        if lim is None:
            fail(f"README 이미지 형식 한도 없음: {src}")
        elif f.stat().st_size > lim:
            fail(f"README 이미지 크기 초과: {src} {f.stat().st_size} B > {lim} B")
        if src not in seen:
            seen.add(src)
            total += f.stat().st_size
    if total > IMG_TOTAL:
        fail(f"README 이미지 합 {total} B > {IMG_TOTAL} B")
    print(f"ok  README 이미지 {len(imgs)}개(로컬 고유 {len(seen)}) · alt 누락 {sum(1 for _, a in imgs if not a)} · 로컬 합 {total / 1048576:.2f} MB")
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
