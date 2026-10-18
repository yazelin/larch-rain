"""語音生成：走 .11 larch-tts-bridge (http://192.168.11.11:8072/tts)。
為《晚霞是舌尖最後的刺痛》全劇角色台詞生成精緻專屬配音。
沈淮：Chinese (Mandarin)_Gentle_Youth
安雅：Chinese (Mandarin)_Soft_Girl
"""
import json, os, urllib.request, subprocess

URL = 'http://192.168.11.11:8072/tts'
KEY = open(os.path.expanduser('~/.config/larch-tts/key')).read().strip()
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets/voice'))


def gen_tts(text, voice, emotion, out_filename, force=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, out_filename)
    
    # 清理文字中的符號與多餘空白，保留自然語氣
    clean_text = text.replace('\n', ' ').strip()
    # 特殊同音替換或停頓處理
    speak_text = clean_text.replace('……', '，').replace('…', '，')
    
    body = json.dumps({
        'text': speak_text,
        'voice': voice,
        'format': 'mp3',
        'emotion': emotion,
        **({'force': True} if force else {}),   # 橋接服務 PR #8：丟掉這句快取重新產
    }).encode('utf-8')
    
    req = urllib.request.Request(
        URL,
        method='POST',
        data=body,
        headers={'Content-Type': 'application/json', 'X-API-Key': KEY}
    )
    
    print(f'Generating TTS: [{voice} | {emotion}] -> {out_filename}...')
    data = urllib.request.urlopen(req, timeout=300).read()
    
    with open(out_path, 'wb') as f:
        f.write(data)
    
    print(f'Done: {out_path} ({len(data)} bytes)')
    return out_path


LINES = [
    # 序幕
    {
        'id': 'shen-start',
        'file': 'shen_start.mp3',
        'voice': 'Chinese (Mandarin)_Gentle_Youth',
        'emotion': 'calm',
        'text': '吧檯上的燈還亮著，空氣裡卻沒有往常那股濃郁的香氣。只有安雅壓在杯底的一張便條。初遇的滋味……金黃的甜白酒、泛著淡粉色的微辣感。我得把那杯酒調出來。'
    },
    # 吧檯便條紙
    {
        'id': 'anya-note',
        'file': 'anya_note.mp3',
        'voice': 'Chinese (Mandarin)_Soft_Girl',
        'emotion': 'calm',
        'text': '沈淮，如果你還記得我們初遇的滋味，就替我把它完成吧。吧檯上方牆上的老掛鐘停在零兩點十七分……那是我們故事開始的時刻，也是我留給你的密碼。'
    },
    # 臥室回憶
    {
        'id': 'anya-memory',
        'file': 'anya_memory.mp3',
        'voice': 'Chinese (Mandarin)_Soft_Girl',
        'emotion': 'happy',
        'text': '沈淮，粉紅胡椒不是辣椒，但咬碎的時候，喉嚨會有一種像觸電一樣的麻辣感……就像我第一次牽你手時一樣。'
    },
    # 遺書告白
    {
        'id': 'anya-confession',
        'file': 'anya_confession.mp3',
        'voice': 'Chinese (Mandarin)_Soft_Girl',
        'emotion': 'sad',
        'text': '當你調出這杯酒時，我已經先喝下它了。我的世界早就失去所有味道，痛卻一天比一天清楚。我研發了三年，把神經止痛毒劑做成這杯酒……它很美，金黃像日出，粉紅像晚霞。沈淮，這是我為自己選的終點。你調出來的這一杯，不要嚐它，替我倒掉。'
    },
    # 結局 A：喝下雞尾酒 1
    {
        'id': 'shen-burn-1',
        'file': 'shen_burn_1.mp3',
        'voice': 'Chinese (Mandarin)_Gentle_Youth',
        'emotion': 'calm',
        'text': '我沒有聽妳的話。我端起酒杯，一口飲盡。'
    },
    # 結局 A：心跳的刺痛 2（去除「半透明立繪」與見鬼感！）
    {
        'id': 'shen-burn-2',
        'file': 'shen_burn_2.mp3',
        'voice': 'Chinese (Mandarin)_Gentle_Youth',
        'emotion': 'sad',
        'text': '入口先是番紅花的溫潤金黃，隨即，粉紅胡椒那股狂暴的辛辣在咽喉裡燃燒撕裂。胸口像被火灼燒，但那股微辣的刺痛感……確實是心跳的感覺。朦朧的淚光中，吧檯對面彷彿映出了她初遇時溫柔的微笑。'
    },
    # 結局 A：終局 3
    {
        'id': 'shen-burn-3',
        'file': 'shen_burn_3.mp3',
        'voice': 'Chinese (Mandarin)_Gentle_Youth',
        'emotion': 'calm',
        'text': '眼前的光線逐漸暈散成一片金黃與淡粉。安雅……這一次，妳不必一個人走。'
    },
    # 結局 B：倒進水槽 1
    {
        'id': 'shen-cold-1',
        'file': 'shen_cold_1.mp3',
        'voice': 'Chinese (Mandarin)_Gentle_Youth',
        'emotion': 'sad',
        'text': '手在發抖，但我還是把杯子翻轉，倒進了水槽。金黃的液體被流水沖淡，淡粉色的胡椒碎粒在不鏽鋼表面旋轉著消逝。空氣裡那股短暫的辣香，轉瞬間被冰冷的水氣沖刷得一乾二淨。'
    },
    # 結局 B：冷卻的餘溫 2
    {
        'id': 'shen-cold-2',
        'file': 'shen_cold_2.mp3',
        'voice': 'Chinese (Mandarin)_Gentle_Youth',
        'emotion': 'sad',
        'text': '屋子裡重新歸於死寂。我遵從了妳最後的願望活了下來，但從此以後，我的舌尖與心臟……再也嚐不出任何溫度。'
    },
]


def gen_all():
    results = {}
    for item in LINES:
        out_path = gen_tts(item['text'], item['voice'], item['emotion'], item['file'])
        results[item['id']] = f'/files/assets/voice/{item["file"]}'
    return results


if __name__ == '__main__':
    gen_all()
