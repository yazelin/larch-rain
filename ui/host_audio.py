"""介面 Skill 的網址只收 R2／larch.ink／相對路徑（jsDelivr 會被擋），介面用到的音訊要上傳到 Larch 拿 R2 網址。
結果記在 ui/hosted.json，night.py 讀它。python3 ui/host_audio.py（已上傳過的跳過）"""
import base64, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
import push_ui
FILES = {'press': 'assets/sfx/press.mp3', 'advance': 'assets/sfx/advance.mp3', 'bgm-rain': 'assets/bgm/rain.mp3'}
OUT = ROOT / 'ui/hosted.json'

if __name__ == '__main__':
    hosted = json.loads(OUT.read_text()) if OUT.exists() else {}
    for k, path in FILES.items():
        if k in hosted:
            continue
        r = push_ui.call('larch_upload_media', {'projectId': push_ui.build.PROJECT_ID, 'name': f'ui-{k}.mp3', 'mimeType': 'audio/mpeg',
                                                 'category': 'music' if k.startswith('bgm') else 'sfx',
                                                 'base64': base64.b64encode((ROOT / path).read_bytes()).decode()})
        url = next((v for v in json.dumps(r).split('"') if v.startswith('https://') and v.endswith('.mp3')), None)
        assert url, ('上傳結果找不到網址', json.dumps(r, ensure_ascii=False)[:400])
        hosted[k] = url
        OUT.write_text(json.dumps(hosted, ensure_ascii=False, indent=1))
        print(k, url)
