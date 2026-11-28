"""REN-003b 무료(CC0) HDRI 받기 — Poly Haven 공식 배포처에서 사용자 홈의 격리 폴더로. 결제 · 계정 · 유료 에셋 없음.

  python -I -B mechanical/ren003b/fetch_hdri.py [--name studio_small_09] [--res 2k]

- 받는 곳: 환경 변수 OPENHW_HDRI_DIR 또는 ~/tools/hdri/polyhaven/ (저장소 밖 — 파일은 커밋하지 않는다)
- 기록: mechanical/ren003b/assets.json 에 이름 · 출처 URL · 라이선스 · 바이트 · sha256 을 적는다(커밋 대상).
  이미 기록이 있으면 받은 파일의 sha256 이 기록과 같아야 한다(다르면 종료 코드 1).
- 요청에는 일반 클라이언트 이름만 쓴다(프로젝트 · 사용자 정보 없음).
종료 코드: 0 = 파일 있음 · sha256 일치."""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(HERE, 'assets.json')
DIR = os.environ.get('OPENHW_HDRI_DIR') or os.path.join(os.path.expanduser('~'), 'tools', 'hdri', 'polyhaven')
LICENSE = 'CC0 1.0 (Poly Haven — https://polyhaven.com/license)'


def path_of(name, res):
    return os.path.join(DIR, '%s_%s.hdr' % (name, res))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='studio_small_09')
    ap.add_argument('--res', default='2k')
    a = ap.parse_args()
    url = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/%s/%s_%s.hdr' % (a.res, a.name, a.res)
    p = path_of(a.name, a.res)
    os.makedirs(DIR, exist_ok=True)
    if not os.path.exists(p):
        req = urllib.request.Request(url, headers={'User-Agent': 'python-urllib'})
        with urllib.request.urlopen(req, timeout=120) as r, open(p + '.part', 'wb') as f:
            f.write(r.read())
        os.replace(p + '.part', p)
    d = open(p, 'rb').read()
    sha = hashlib.sha256(d).hexdigest()
    ok_fmt = d[:10] == b'#?RADIANCE'
    rec = json.load(open(REC, encoding='utf-8')) if os.path.exists(REC) else {'hdri': []}
    key = '%s_%s.hdr' % (a.name, a.res)
    old = next((h for h in rec['hdri'] if h['file'] == key), None)
    if old is None:
        rec['hdri'].append({'file': key, 'page': 'https://polyhaven.com/a/' + a.name, 'url': url, 'license': LICENSE, 'bytes': len(d), 'sha256': sha})
        json.dump(rec, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    same = old is None or old['sha256'] == sha
    print('HDRI %s · %d 바이트 · sha256 %s · Radiance 형식 %s · 기록과 %s' % (key, len(d), sha[:16], ok_fmt, '같음' if same else '다름'))
    return 0 if ok_fmt and same else 1


if __name__ == '__main__':
    sys.exit(main())
