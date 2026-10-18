"""推到 Larch：快照 → 驗證 → 整包 PUT（包在 {"project": …}）→ 讀回比對。

    python3 src/push.py "這次改了什麼"
"""
import json, os, re, sys, time, pathlib, urllib.parse, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
import build

ROOT = build.ROOT
KEY = open(os.path.expanduser(os.environ.get('LARCH_KEY_FILE', '~/.config/larch/key'))).read().strip()
BASE = f'https://larch.ink/api/agent/projects/{build.PROJECT_ID}'
# 素材走 jsDelivr（作者 2026-10-17）：/files/assets/… 只有本機預覽讀得到，推之前換成 GitHub tag 的固定網址。
# 改了素材要先 commit、推 main、打新 tag，再改這裡。
# 用 tag 指向的 commit 編號：新 tag 要等 jsDelivr 刷新版本清單（實測幾分鐘以上回 404），commit 編號馬上能用、一樣固定不變。
# 這裡是 tag v2d-20261018 的 commit。
CDN_TAG = os.environ.get('CDN_TAG', '9f5b135ccce5388cfd6121c95bad87445e14cf95')
CDN = f'https://cdn.jsdelivr.net/gh/yazelin/larch-rain@{CDN_TAG}/'


def to_cdn(project):
    """把 /files/assets/… 換成 jsDelivr 網址，逐一確認打得開；有一個打不開就停下來，不推。"""
    text = json.dumps(project, ensure_ascii=False)
    paths = sorted(set(re.findall(r'/files/(assets/[^"\\]+)', text)))
    url = lambda p: CDN + urllib.parse.quote(p)

    def ok(p):
        for t in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(url(p), method='HEAD'), timeout=60) as r:
                    return r.status == 200
            except Exception:  # noqa: BLE001
                time.sleep(2 * (t + 1))
        return False
    with ThreadPoolExecutor(8) as ex:
        bad = [p for p, good in zip(paths, ex.map(ok, paths)) if not good]
    if bad:
        raise SystemExit(f'jsDelivr 打不開 {len(bad)} 個素材（還沒推 GitHub 或 tag 不對？）：{bad[:5]}')
    for p in paths:
        text = text.replace('/files/' + p, url(p))
    print(f'素材換成 jsDelivr：{len(paths)} 個，全部打得開（{CDN_TAG}）')
    return json.loads(text)


def req(method, path='', body=None, etag=None, tries=5):
    h = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'}
    if etag:
        h['If-Match'] = etag
    last = None
    for t in range(tries):
        try:
            r = urllib.request.Request(
                BASE + path,
                method=method,
                headers=h,
                data=json.dumps(body).encode() if body is not None else None
            )
            with urllib.request.urlopen(r, timeout=120) as resp:
                return resp.headers.get('ETag'), json.loads(resp.read() or b'{}')
        except urllib.error.HTTPError as e:
            last = f'{e.code} {e.read()[:300]}'
            if e.code != 429 and e.code < 500:
                raise SystemExit(f'{method} {path} → {last}')
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = repr(e)
        print(f'{method} {path} 失敗（{last}），{5 * (t + 1)} 秒後重試', flush=True)
        time.sleep(5 * (t + 1))
    raise SystemExit(f'{method} {path} 重試 {tries} 次仍失敗：{last}')


def merge_settings(online, built):
    m = json.loads(json.dumps(online or {}))
    plugins = m.setdefault('plugins', {})
    rpg = plugins.setdefault('larch-rpg-system', {'enabled': True, 'settings': {}})
    rpg['enabled'] = True
    rpg.setdefault('settings', {})['database'] = built['settings']['plugins']['larch-rpg-system']['settings']['database']
    for k in ('titleCoverImage', 'projectThumbnail', 'cgGallerySource', 'cgGalleryItems', 'menuUi', 'battleUi'):
        if k in built.get('settings', {}):
            m[k] = built['settings'][k]
    if (built.get('settings', {}).get('titleScreen') or {}).get('bgm'):
        m.setdefault('titleScreen', {})['bgm'] = built['settings']['titleScreen']['bgm']
    return m


def main(summary='升級 RPG 地圖系統與互動探索'):
    etag, cur = req('GET')
    online = cur.get('project', cur)
    snap = ROOT / 'snapshots' / time.strftime('%Y%m%d-%H%M%S.json')
    snap.parent.mkdir(exist_ok=True)
    snap.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding='utf-8')
    print('已存線上快照：', snap)

    built = to_cdn(build.build())
    built['settings'] = merge_settings(online.get('settings'), built)
    if os.environ.get('DRY'):
        (ROOT / 'dist/project-larch.json').write_text(json.dumps(built, ensure_ascii=False, indent=2), encoding='utf-8')
        print('DRY：只寫 dist/project-larch.json，沒有推')
        return

    body = {'project': built, 'summary': summary}
    new_etag, res = req('PUT', '', body, etag=etag)
    print(f'成功推送到 Larch！新 ETag: {new_etag}')
    return res


if __name__ == '__main__':
    msg = sys.argv[1] if len(sys.argv) > 1 else '升級 RPG 地圖系統與互動探索'
    main(msg)
