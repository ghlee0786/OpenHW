import re,os
S=r'C:/Users/gh/AppData/Local/Programs/KiCad/10.0/share/kicad/symbols'
def blocks(txt):
    # top-level (symbol "...") blocks inside kicad_symbol_lib
    out={};i=0;n=len(txt)
    for m in re.finditer(r'\n\t\(symbol "([^"]+)"',txt):
        s=m.start()+1;d=0;j=s
        while True:
            c=txt[j]
            if c=='"':
                j+=1
                while txt[j]!='"':
                    if txt[j]==chr(92): j+=1
                    j+=1
            elif c=='(': d+=1
            elif c==')':
                d-=1
                if d==0: break
            j+=1
        out[m.group(1)]=txt[s:j+1]
    return out
_cache={}
def lib(path):
    if path not in _cache: _cache[path]=blocks(open(path,encoding='utf-8').read())
    return _cache[path]
def get(libname,name,path=None):
    p=path or f'{S}/{libname}.kicad_sym'
    L=lib(p); b=L[name]
    m=re.search(r'\(extends "([^"]+)"\)',b)
    base=None
    if m: base=get(libname,m.group(1),p)
    return b,base
def pins(block):
    res=[]
    for m in re.finditer(r'\(pin (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)\s*\(length ([-\d.]+)\)(.*?)\(name "([^"]*)".*?\(number "([^"]*)"',block,re.S):
        res.append(dict(type=m.group(1),x=float(m.group(3)),y=float(m.group(4)),rot=float(m.group(5)),name=m.group(8),num=m.group(9),hidden='(hide yes)' in m.group(7)))
    return res
def sympins(libname,name,path=None):
    b,base=get(libname,name,path)
    return pins(base[0] if base else b) if base else pins(b)
