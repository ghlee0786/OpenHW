"""M-010 00 (Fusion): openhw/doc 속성이 DOC 인 문서 중 마지막 것을 활성으로. mechanical/fusion_run.py --set DOC=M007_assembly"""
import adsk.core, adsk.fusion

LANE = r"C:\workspace_python\OpenHW"   # fusion_run.py 규약 (이 스크립트는 쓰지 않음)
DOC = r"M007_assembly"


def run(_c):
    app = adsk.core.Application.get()
    hit = None
    for i in range(app.documents.count):
        d = app.documents.item(i)
        des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
        a = des.attributes.itemByName('openhw', 'doc') if des else None
        if a and a.value == DOC:
            hit = d
    assert hit is not None, 'no document ' + DOC
    hit.activate()
    print('ACTIVE', DOC, hit.name)
