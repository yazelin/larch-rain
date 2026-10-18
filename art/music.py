# -*- coding: utf-8 -*-
"""《雨幕》配樂：走 .11 的 gemini-web /api/music（作者 2026-10-17 指定；腳本沿用《十一分鐘》art/music.py），產完切 60 秒循環、量響度（沿用 larch-taoyuan/bgm.py 的 find_start／make／seam_score）。
服務偶爾逾時，重試就好（記憶：音樂會撞 548 秒逾時，跟 worker 無關）。這台連 ddns 會被擋，走內網 IP、不驗憑證。
  python3 art/music.py gen [名字…]   → art/music_raw/<名字>.mp3
  python3 art/music.py loop [名字…]  → assets/bgm/<名字>.mp3（60 秒循環、-16 LUFS）"""
import base64, importlib.util, json, os, ssl, subprocess, sys, threading, urllib.request
H = os.path.dirname(os.path.abspath(__file__)); G = os.path.dirname(H)
RAW, OUT = os.path.join(H, 'music_raw'), os.path.join(G, 'assets/bgm')
URL = 'https://192.168.11.11/gemini-web/api/music'
CTX = ssl._create_unverified_context()
TRACKS = {
    # design/重寫.md「配樂與配音」：器樂、無人聲、可循環
    'rain': 'Melancholic ambient piano in steady city rain at dusk, soft felt piano, a quiet cello, distant traffic hiss, a gentle four-note motif that never resolves, '
            'unspoken love between three friends, cold pale blue mood, 66 BPM, minor key, instrumental, no vocals, loopable',
    'summer': 'Nostalgic warm summer afternoon on a high school rooftop, soft acoustic guitar and light piano, cicadas faint in the distance, youthful and bittersweet, '
              'the same four-note motif played brighter, 84 BPM, instrumental, no vocals, loopable',
    'store': 'Late night in an empty fluorescent-lit convenience store during rain, sparse electric piano, a soft humming synth pad like fluorescent lights, '
             'lonely and guilty, 60 BPM, minor, instrumental, no vocals, loopable',
    'climax': 'Tense and tender piano with strings building slowly at a bus shelter in heavy rain, heartbeat-like low pulse, the four-note motif finally reaching for resolution, '
              '72 BPM, instrumental, no vocals, loopable',
    'end-a': 'Rain stopping at dawn, gentle piano and warm strings, the four-note motif resolving for the first time, hopeful farewell between friends, 70 BPM, major key, instrumental, no vocals, loopable',
    'end-b': 'Endless cold rain at night, slow dissonant strings and a music-box version of the four-note motif breaking apart, frozen grief, 52 BPM, minor, instrumental, no vocals, loopable',
}


def key():
    for line in open(os.path.expanduser('~/.bashrc'), encoding='utf-8'):
        if line.startswith('export GEMINI_IMAGE_KEY='): return line.split('=', 1)[1].strip().strip('"')
    raise RuntimeError('找不到 GEMINI_IMAGE_KEY')


def one(name, k, tries=4):
    os.makedirs(RAW, exist_ok=True)
    for n in range(tries):
        req = urllib.request.Request(URL, method='POST', data=json.dumps({'prompt': TRACKS[name], 'timeout': 720}).encode(),
                                     headers={'Content-Type': 'application/json', 'x-goog-api-key': k})
        try: d = json.load(urllib.request.urlopen(req, timeout=900, context=CTX))
        except Exception as e: print(f'{name} 第{n + 1}次 例外 {e!r}', flush=True); continue
        if d.get('success'):
            p = os.path.join(RAW, f'{name}.mp3'); open(p, 'wb').write(base64.b64decode(d['audio']))
            print(f"{name} 好了 worker={d.get('worker_id')} {d.get('elapsed_seconds', 0):.0f} 秒", flush=True); return
        print(f"{name} 第{n + 1}次 失敗 {d.get('message') or d.get('error')}", flush=True)
    print(f'{name} 四次都失敗', flush=True)


def loop(name):
    spec = importlib.util.spec_from_file_location('tybgm', os.path.expanduser('~/larch-taoyuan/bgm.py'))
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)   # 只借函式，不跑它的 main（它的路徑是桃園的）
    src = os.path.join(RAW, f'{name}.mp3'); os.makedirs(OUT, exist_ok=True); out = os.path.join(OUT, f'{name}.mp3')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout)
    B.LEN = min(60, int(dur) - 4)
    base, best = B.find_start(src), None
    for off in [0, .5, -.5, 1, -1, 1.5, -1.5, 2, -2]:
        s = max(0.0, base + off); B.make(src, s, out); z, d = B.seam_score(out)
        if best is None or abs(z) < abs(best[0]): best = (z, s, d)
        if abs(z) < 3: break
    z, s, d = best; B.make(src, s, out)
    print(f'{name} 原曲 {dur:.0f} 秒 → 循環 {d:.1f} 秒，從 {s:.0f} 秒起，接縫 z={z:+.1f}', flush=True)


if __name__ == '__main__':
    cmd, names = sys.argv[1], sys.argv[2:] or list(TRACKS)
    if cmd == 'gen':
        k = key(); ts = [threading.Thread(target=one, args=(n, k)) for n in names]
        for t in ts: t.start()
        for t in ts: t.join()
    else:
        for n in names: loop(n)
