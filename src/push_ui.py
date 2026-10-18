"""把 ui/rain-night/ 七個介面部位寫進 Larch（整包 PUT 不會動 customInterfaces，要走 MCP 的 larch_update_interface）。
每個部位帶 expectedHtml＝線上現值，防止蓋掉別人在編輯器的修改。python3 src/push_ui.py"""
import json, os, pathlib, urllib.request
import build
ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = open(os.path.expanduser(os.environ.get('LARCH_KEY_FILE', '~/.config/larch/key'))).read().strip()
# ponytail: 收藏頁（gallery）工具不收，只能在編輯器手動換
SURFACES = ('title', 'dialogue', 'choices', 'menu', 'inventory', 'rpg')
H = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}


def call(name, args, i=[0]):
    i[0] += 1
    body = json.dumps({'jsonrpc': '2.0', 'id': i[0], 'method': 'tools/call', 'params': {'name': name, 'arguments': args}}).encode()
    with urllib.request.urlopen(urllib.request.Request('https://larch.ink/mcp', body, H), timeout=180) as r:
        raw = r.read().decode()
    if raw.startswith('event:') or '\ndata:' in raw:
        raw = [l[5:] for l in raw.splitlines() if l.startswith('data:')][-1]
    res = json.loads(raw)
    if 'error' in res or res['result'].get('isError'):
        raise SystemExit(f'{name} 失敗：{json.dumps(res, ensure_ascii=False)[:500]}')
    return json.loads(res['result']['content'][0]['text'])


def live():
    return call('larch_get_project', {'projectId': build.PROJECT_ID})['project']['settings'].get('customInterfaces', {})


if __name__ == '__main__':
    cur = live()
    for f in sorted(x for x in (ROOT / 'ui/rain-night').iterdir() if x.stem in SURFACES):
        k, html = f.stem, f.read_text(encoding='utf-8')
        old = cur.get(k, {}).get('html', '')
        if old == html:
            print(k, '已是最新'); continue
        call('larch_update_interface', {'projectId': build.PROJECT_ID, 'surface': k, 'html': html, 'enabled': True,
                                         'expectedHtml': old, 'summary': f'雨夜玻璃：{k}（改自晨霧玻璃，深色玻璃＋草木灰綠）'})
        print(k, '已寫入')
    after = live()
    bad = [f.stem for f in (ROOT / 'ui/rain-night').iterdir() if f.stem in SURFACES and after.get(f.stem, {}).get('html') != f.read_text(encoding='utf-8')]
    assert not bad, ('讀回不一致', bad)
    print('讀回一致：', sorted(after))
