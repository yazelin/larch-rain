"""全劇配音：台詞在 script.L（含建置時轉成卡片的地圖內心話）。已存在的檔跳過；FORCE=1 全部重產（連橋接服務的快取一起繞過）。
破音字照 SUBS 換成同音字（橋接服務的替身表只涵蓋「調酒」「調出來」）。3 線並行：Larch 帳號並行太高會被凍結，不要調高。
"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
import script, tts11, build

build.build()   # 先建置一次，地圖內心話才會進 script.MAP_LINES
FORCE = bool(os.environ.get('FORCE'))
lines = script.voice_lines()


# 破音字替身：送出前換成同音字，畫面上的字不動（「柏油」的柏唸ㄅㄛˊ，引擎常唸成ㄅㄞˇ）
SUBS = [('調', '條'), ('柏油', '伯油'), ('許帆', '許翻')]   # 帆唸ㄈㄢ；翻只有一個讀音


def say(text):
    for a, b in SUBS:
        text = text.replace(a, b)
    return text


def one(item):
    fn, text, voice, emo = item
    if not FORCE and os.path.exists(os.path.join(tts11.OUT_DIR, fn)):
        return
    for k in range(3):
        try:
            return tts11.gen_tts(say(text), voice, emo, fn, force=FORCE)
        except Exception as e:  # noqa: BLE001
            print('retry', fn, k + 1, repr(e)[:80], flush=True)
    print('FAIL', fn, flush=True)


with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, lines))
print('done', len(lines))
