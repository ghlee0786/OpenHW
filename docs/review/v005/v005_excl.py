# -*- coding: utf-8 -*-
"""V-005 O-74 판정: DRC 제외·ignore 와 라이브러리 사본 풋프린트 (KiCad 10 pcbnew, 읽기 전용).

사용: python.exe -I v005_excl.py <board.kicad_pcb> <out.json> [--pro P] [--dru D] [--fplib T] [--doc MD ...] [--board-name front]
  --pro   : .kicad_pro (기본: 보드와 같은 이름)          --dru : .kicad_dru (기본: 보드와 같은 이름)
  --fplib : 프로젝트 fp-lib-table (기본: 보드 폴더)       --doc : pcb 문서(여럿). 「O-74」가 든 줄의 참조 지정자를 제외 목록으로 본다
  --board-name : 문서 줄에 보드 이름(carrier/캐리어, front/전면)이 있으면 그 보드 것만 센다
종료 코드 0 = 검사가 끝까지 돌았다(판정은 json verdict). 1 = 입력 오류.

E1 제외·ignore 전부 나열: .kicad_pro drc_exclusions(종류·참조·주석), rule_severities 의 ignore, .kicad_dru 규칙의 (severity …)
E2 lib_footprint_mismatch 외 종류의 제외 → 불합격. 주석에 「O-74」가 없는 제외 → 경고
E3 제외 참조 목록 = 문서 목록? (문서가 없으면 판정 보류)
E4 a) 보드 위 풋프린트(라이브러리 openhw 전부 + 제외된 것)를 자기 라이브러리 풋프린트와 비교: 패드·구멍 같고, 실크 밖 그림도 같아야 한다(실크만 달라도 됨)
   b) openhw 라이브러리 풋프린트 중 KiCad 표준에 같은 이름(또는 가장 긴 접두 이름)이 있는 것: 패드·구멍 같고 실크 밖 그림도 같아야 한다
   c) (O-74b) fp-lib-table 이 실크 사본 폴더(…/lib/silk/…)로 돌린 별칭마다 그 폴더의 풋프린트 전부를 SOURCES.tsv 의 원본과 비교:
      패드·구멍·실크 밖 그림이 같고 실크만 달라야 하며, 원본 파일 sha256 이 기록과 같아야 한다. 행 없는 사본·사본 없는 행은 불합격
E2b (O-74b) DRC 제외는 0 이어야 한다(pcb 는 제외를 쓰지 않는다)
"""
import sys, os, re, json, argparse, glob
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('pcb'); ap.add_argument('out')
ap.add_argument('--pro'); ap.add_argument('--dru'); ap.add_argument('--fplib')
ap.add_argument('--doc', nargs='*', default=[])
ap.add_argument('--board-name', default=None)
ap.add_argument('--kicad-footprints', default=None)
ap.add_argument('--repo-root', default=None, help='SOURCES.tsv 의 저장소 상대 경로 기준(스냅샷 루트)')
A = ap.parse_args()
base = os.path.splitext(A.pcb)[0]
PRO = A.pro or base + '.kicad_pro'
DRU = A.dru or base + '.kicad_dru'
FPLIB = A.fplib or os.path.join(os.path.dirname(A.pcb), 'fp-lib-table')
KFP = A.kicad_footprints or os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'share', 'kicad', 'footprints')
mm = pcbnew.ToMM
ALLOWED = {'lib_footprint_mismatch'}
SILK = {'F.SilkS', 'B.SilkS', 'F.Silkscreen', 'B.Silkscreen'}

b = pcbnew.LoadBoard(A.pcb)
fp_by_uuid = {fp.m_Uuid.AsString(): fp for fp in b.Footprints()}
refs_on_board = {fp.GetReference() for fp in b.Footprints()}
R = dict(board=A.pcb, pro=PRO, dru=DRU, fplib=FPLIB, docs=A.doc)

# ---------- E1 ----------
pro = json.load(open(PRO, encoding='utf-8')) if os.path.exists(PRO) else {}
ds = pro.get('board', {}).get('design_settings', {})
excl = []
for e in ds.get('drc_exclusions', []):
    s, comment = (e[0], e[1] if len(e) > 1 else '') if isinstance(e, list) else (e, '')
    parts = s.split('|')
    typ = parts[0]
    uu = [p for p in parts[3:] if re.fullmatch(r'[0-9a-fA-F-]{36}', p)]
    refs = [fp_by_uuid[u].GetReference() for u in uu if u in fp_by_uuid]
    excl.append(dict(type=typ, refs=refs, uuids=uu, comment=comment, raw=s))
R['exclusions'] = excl
R['ignored_severities'] = {k: v for k, v in ds.get('rule_severities', {}).items() if v == 'ignore'}
dru_sev = []
if os.path.exists(DRU):
    t = open(DRU, encoding='utf-8').read()
    for m in re.finditer(r'\(rule\s+"([^"]+)"(.*?)(?=\n\(rule|\Z)', t, re.S):
        sv = re.findall(r'\(severity\s+(\w+)\)', m.group(2))
        if sv:
            dru_sev.append(dict(rule=m.group(1), severity=sv))
R['dru_severity_rules'] = dru_sev

# ---------- E2 ----------
R['E2_disallowed'] = [x for x in excl if x['type'] not in ALLOWED]
R['E2_no_O74_comment'] = [x for x in excl if 'O-74' not in (x['comment'] or '')]

# ---------- E3 ----------
excl_refs = sorted({r for x in excl if x['type'] in ALLOWED for r in x['refs']})
doc_refs, doc_unknown, doc_lines = set(), set(), []
names = {'carrier': ('carrier', '캐리어'), 'front': ('front', '전면')}
for d in A.doc:
    if not os.path.exists(d):
        continue
    for ln in open(d, encoding='utf-8', errors='replace'):
        if 'O-74' not in ln:
            continue
        if A.board_name:
            mine = any(n in ln for n in names.get(A.board_name, (A.board_name,)))
            other = any(n in ln for k, v in names.items() if k != A.board_name for n in v)
            if other and not mine:
                continue
        doc_lines.append(ln.strip()[:200])
        for tok in re.findall(r'(?<![\w-])(D_IR_[AB]\d|[A-Z]{1,3}\d{1,3})(?![\w-])', ln):
            (doc_refs if tok in refs_on_board else doc_unknown).add(tok)
R['E3'] = dict(exclusion_refs=excl_refs, doc_refs=sorted(doc_refs), doc_lines=doc_lines, doc_tokens_not_on_board=sorted(doc_unknown),
               missing_in_doc=sorted(set(excl_refs) - doc_refs), missing_in_exclusions=sorted(doc_refs - set(excl_refs)),
               status=('해당 없음(제외 0 · 문서 O-74 줄 0)' if not doc_lines and not excl_refs else
                       ('보류(문서 없음)' if not doc_lines else ('일치' if set(excl_refs) == doc_refs else '불일치'))))

# ---------- E4 ----------
libs = {}
if os.path.exists(FPLIB):
    for nick, uri in re.findall(r'\(lib\s*\(name\s+"([^"]+)"\)\s*\(type\s+"?[^")]+"?\)\s*\(uri\s+"([^"]+)"\)', open(FPLIB, encoding='utf-8').read()):
        libs[nick] = os.path.normpath(uri.replace('${KIPRJMOD}', os.path.dirname(os.path.abspath(A.pcb))))


def lib_path(nick):
    if nick in libs:
        return libs[nick]
    p = os.path.join(KFP, nick + '.pretty')
    return p if os.path.isdir(p) else None


def LN(l):
    return pcbnew.BOARD.GetStandardLayerName(l)


def r3(v):
    return round(mm(v), 3)


def pad_sig(p):
    def g(f, *a):
        try:
            return f(*a)
        except TypeError:
            return f()
    sz = g(p.GetSize, pcbnew.F_Cu)
    sh = g(p.GetShape, pcbnew.F_Cu)
    rr = g(p.GetRoundRectRadiusRatio, pcbnew.F_Cu)
    ds = p.GetDrillSize()
    pos = p.GetPosition()
    return (p.GetNumber(), int(p.GetAttribute()), int(sh), r3(pos.x), r3(pos.y), round(p.GetOrientation().AsDegrees() % 360, 2),
            r3(sz.x), r3(sz.y), round(rr, 3), r3(ds.x), r3(ds.y), int(p.GetDrillShape()),
            tuple(sorted(LN(l) for l in p.GetLayerSet().Seq())))


def shape_sig(g):
    st = g.GetShape()
    pts = []
    if st == pcbnew.SHAPE_T_POLY:
        ps = g.GetPolyShape()
        for i in range(ps.OutlineCount()):
            o = ps.Outline(i)
            pts += [(r3(o.CPoint(j).x), r3(o.CPoint(j).y)) for j in range(o.PointCount())]
    else:
        pts = [(r3(g.GetStart().x), r3(g.GetStart().y)), (r3(g.GetEnd().x), r3(g.GetEnd().y))]
        if st == pcbnew.SHAPE_T_ARC:
            m = g.GetArcMid(); pts.append((r3(m.x), r3(m.y)))
    filled = g.IsSolidFill() if hasattr(g, 'IsSolidFill') else g.IsFilled()
    return (LN(g.GetLayer()), int(st), r3(g.GetWidth()), bool(filled), tuple(sorted(pts)))


TMP = pcbnew.BOARD()
IO = pcbnew.PCB_IO_KICAD_SEXPR()
_FPC = {}


def load_fp(libdir, name):
    """같은 풋프린트를 여러 번 읽으면 KiCad 10 SWIG 가 FOOTPRINT 로 못 바꾼다 → 한 번 읽고 복제해서 돌려준다"""
    k = (os.path.normcase(os.path.abspath(libdir)), name)
    if k not in _FPC:
        try:
            _FPC[k] = IO.FootprintLoad(libdir, name)
        except Exception:
            _FPC[k] = None
    raw = _FPC[k]
    if raw is None:
        return None
    c = pcbnew.FOOTPRINT(raw)
    c.ResetUuidDirect()
    return c


def compare(inst, libfp):
    """libfp 를 inst 와 같은 자리·면·각도에 놓고 패드·그림을 비교"""
    lf = libfp
    if lf.GetParent() is None:
        TMP.Add(lf)  # 보드에 붙지 않은 풋프린트의 Flip 은 KiCad 10 에서 죽는다(access violation) → 빈 임시 보드에 붙인다
    lf.SetPosition(inst.GetPosition())
    if inst.IsFlipped() != lf.IsFlipped():
        lf.Flip(lf.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    lf.SetOrientation(inst.GetOrientation())
    pa = sorted(pad_sig(p) for p in inst.Pads())
    pb = sorted(pad_sig(p) for p in lf.Pads())
    ga = [shape_sig(g) for g in inst.GraphicalItems() if g.GetClass() == 'PCB_SHAPE']
    gb = [shape_sig(g) for g in lf.GraphicalItems() if g.GetClass() == 'PCB_SHAPE']
    na = sorted(s for s in ga if s[0] not in SILK)
    nb = sorted(s for s in gb if s[0] not in SILK)
    sa = sorted(s for s in ga if s[0] in SILK)
    sb = sorted(s for s in gb if s[0] in SILK)
    pad_diff = [x for x in pa if x not in pb][:6] + [('lib',) + x for x in pb if x not in pa][:6]
    ns_diff = [x[:3] for x in na if x not in nb][:6] + [('lib',) + x[:3] for x in nb if x not in na][:6]
    return dict(pads_equal=(pa == pb), holes_equal=([x[9:12] for x in pa] == [x[9:12] for x in pb]), pad_count=(len(pa), len(pb)),
                nonsilk_equal=(na == nb), silk_equal=(sa == sb), pad_diff=[str(x) for x in pad_diff], nonsilk_diff=[str(x) for x in ns_diff])


excluded_uuids = {u for x in excl for u in x['uuids']}
# O-74b: fp-lib-table 별칭 중 실크 사본 폴더(hardware/pcb/lib/silk/…)를 가리키는 것
silk_libs = {n: p for n, p in libs.items() if re.search(r'[\\/]lib[\\/]silk[\\/]', p.replace('\\', '/') + '/')}
R['silk_lib_redirects'] = silk_libs
inst_rows = []
for fp in b.Footprints():
    lib = fp.GetFPID().GetLibNickname().wx_str() if hasattr(fp.GetFPID().GetLibNickname(), 'wx_str') else str(fp.GetFPID().GetLibNickname())
    name = fp.GetFPID().GetLibItemName().wx_str() if hasattr(fp.GetFPID().GetLibItemName(), 'wx_str') else str(fp.GetFPID().GetLibItemName())
    if lib != 'openhw' and fp.m_Uuid.AsString() not in excluded_uuids and lib not in silk_libs:
        continue
    lp = lib_path(lib)
    lf = load_fp(lp, name) if lp else None
    row = dict(ref=fp.GetReference(), fpid='%s:%s' % (lib, name), excluded=fp.m_Uuid.AsString() in excluded_uuids)
    if lf is None:
        row.update(ok=False, error='라이브러리 풋프린트 없음 (%s)' % lp)
    else:
        c = compare(fp, lf)
        row.update(c, ok=c['pads_equal'] and c['nonsilk_equal'])
    inst_rows.append(row)
R['E4a_instances'] = inst_rows

lib_rows = []
oh = lib_path('openhw')
std_names = {}
for d in glob.glob(os.path.join(KFP, '*.pretty')):
    for f in glob.glob(os.path.join(d, '*.kicad_mod')):
        std_names.setdefault(os.path.splitext(os.path.basename(f))[0], d)
if oh and os.path.isdir(oh):
    for f in sorted(glob.glob(os.path.join(oh, '*.kicad_mod'))):
        name = os.path.splitext(os.path.basename(f))[0]
        match = name if name in std_names else None
        how = 'exact'
        if not match:
            cands = [n for n in std_names if name.startswith(n) and len(n) >= 8]
            if cands:
                match = max(cands, key=len); how = 'prefix'
        if not match:
            lib_rows.append(dict(name=name, original=None, note='표준 원본 없음(사용자 작성)'))
            continue
        a = load_fp(oh, name)
        o = load_fp(std_names[match], match)
        c = compare(a, o)
        lib_rows.append(dict(name=name, original='%s:%s' % (os.path.basename(std_names[match])[:-7], match), match=how, **c,
                             ok=c['pads_equal'] and c['nonsilk_equal']))
R['E4b_library_copies'] = lib_rows

# ---------- E4c (O-74b): 실크 사본 폴더의 풋프린트 전부 ↔ SOURCES.tsv 원본 ----------
# SOURCES.tsv: 사본 폴더 또는 그 위(…/lib/silk 까지)에 둔다. 머리글로 열을 찾는다(없으면 순서 = 사본, 원본, sha256).
#   사본 열: copy·사본·footprint·fp·name  원본 열: source·원본·src·origin  sha 열: sha256·sha
#   원본 표기: ${KICAD10_FOOTPRINT_DIR}/Lib.pretty/X.kicad_mod · 절대 경로(…/share/kicad/footprints/… 는 이 PC 의 KiCad 로 바꿔 읽음)
#             · 저장소 상대 경로(--repo-root 기준) · TSV 상대 경로 · 별칭:이름(openhw → hardware/libraries/openhw.pretty)
import hashlib


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def find_sources(d):
    out, cur = [], os.path.abspath(d)
    for _ in range(4):
        f = os.path.join(cur, 'SOURCES.tsv')
        if os.path.exists(f):
            out.append(f)
        if os.path.basename(cur) == 'silk':
            break
        cur = os.path.dirname(cur)
    return out


def parse_sources(f):
    rows = []
    lines = [l.rstrip('\r\n') for l in open(f, encoding='utf-8-sig') if l.strip() and not l.lstrip().startswith('#')]
    if not lines:
        return rows
    head = [h.strip().lower() for h in lines[0].split('\t')]

    def col(keys):
        for i, h in enumerate(head):
            if any(k in h for k in keys):
                return i
        return None
    ci, si, hi = col(('copy', '사본', 'footprint', 'fp', 'name')), col(('source', '원본', 'src', 'origin')), col(('sha',))
    body = lines[1:]
    if ci is None or si is None:
        ci, si, hi, body = 0, 1, 2, lines
    for l in body:
        c = l.split('\t')
        if len(c) <= max(ci, si):
            continue
        rows.append(dict(copy=c[ci].strip(), source=c[si].strip(), sha256=(c[hi].strip().lower() if hi is not None and hi < len(c) else ''), tsv=f))
    return rows


def resolve_source(src, tsv):
    s = src.strip().strip('"')
    s2 = re.sub(r'\$\{KICAD\d*_FOOTPRINT_DIR\}', KFP.replace('\\', '/'), s)
    if s2 != s:
        return os.path.normpath(s2)
    m = re.fullmatch(r'([^/\\:]+):([^/\\]+)', s)
    if m:
        nick, name = m.group(1), m.group(2)
        if nick == 'openhw' and A.repo_root:
            return os.path.join(A.repo_root, 'hardware', 'libraries', 'openhw.pretty', name + '.kicad_mod')
        return os.path.join(KFP, nick + '.pretty', name + '.kicad_mod')
    if os.path.isabs(s):
        if os.path.exists(s):
            return s
        t = s.replace('\\', '/')
        k = t.find('/share/kicad/footprints/')
        return os.path.normpath(os.path.join(KFP, t[k + len('/share/kicad/footprints/'):])) if k >= 0 else s
    for base_ in ([A.repo_root] if A.repo_root else []) + [os.path.dirname(tsv)]:
        p = os.path.normpath(os.path.join(base_, s))
        if os.path.exists(p):
            return p
    return os.path.normpath(os.path.join(A.repo_root or os.path.dirname(tsv), s))


copy_rows = []
for nick, d in sorted(silk_libs.items()):
    srcs = []
    for f in find_sources(d):
        srcs += parse_sources(f)
    copies = sorted(glob.glob(os.path.join(d, '*.kicad_mod')))
    for cp in copies:
        name = os.path.splitext(os.path.basename(cp))[0]
        lib_dir_name = os.path.basename(d)
        cand = [r for r in srcs if os.path.splitext(os.path.basename(r['copy'].replace('\\', '/').split(':')[-1]))[0] == name
                and (lib_dir_name in r['copy'] or nick in r['copy'] or '/' not in r['copy'].replace('\\', '/'))]
        row = dict(lib=nick, dir=d, name=name, copy_sha256=sha256(cp))
        if not cand:
            row.update(ok=False, error='SOURCES.tsv 에 행 없음'); copy_rows.append(row); continue
        r0 = cand[0]
        orig = resolve_source(r0['source'], r0['tsv'])
        row.update(source=r0['source'], source_path=orig, recorded_sha256=r0['sha256'])
        if not os.path.exists(orig):
            row.update(ok=False, error='원본 파일 없음'); copy_rows.append(row); continue
        row['source_sha256'] = sha256(orig)
        row['sha_ok'] = (row['source_sha256'] == r0['sha256'])
        a = load_fp(d, name)
        o = load_fp(os.path.dirname(orig), os.path.splitext(os.path.basename(orig))[0])
        if a is None or o is None:
            row.update(ok=False, error='풋프린트 읽기 실패'); copy_rows.append(row); continue
        c = compare(a, o)
        row.update(c, ok=c['pads_equal'] and c['nonsilk_equal'] and row['sha_ok'])
        copy_rows.append(row)
    # SOURCES 행인데 사본 파일이 없는 것
    names = {os.path.splitext(os.path.basename(c))[0] for c in copies}
    for r in srcs:
        n = os.path.splitext(os.path.basename(r['copy'].replace('\\', '/').split(':')[-1]))[0]
        if (os.path.basename(d) in r['copy'] or nick in r['copy']) and n not in names:
            copy_rows.append(dict(lib=nick, dir=d, name=n, ok=False, error='SOURCES.tsv 행의 사본 파일 없음'))
R['E4c_silk_copies'] = copy_rows

R['verdict'] = dict(
    E2_pass=not R['E2_disallowed'],
    E2_warn_no_comment=len(R['E2_no_O74_comment']),
    E3=R['E3']['status'],
    E4a_fail=[r['ref'] for r in inst_rows if not r.get('ok')],
    E4b_fail=[r['name'] for r in lib_rows if r.get('original') and not r.get('ok')],
    E2b_exclusions_zero=(len(excl) == 0),
    silk_redirects=sorted(silk_libs),
    E4c_copies=len(copy_rows),
    E4c_fail=['%s:%s' % (r['lib'], r['name']) for r in copy_rows if not r.get('ok')],
    exclusions=len(excl), ignored_severities=len(R['ignored_severities']), dru_severity_rules=len(dru_sev))
json.dump(R, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(R['verdict'], ensure_ascii=False))
