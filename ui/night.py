"""把官方「晨霧玻璃」七個部位轉成雨夜玻璃：亮玻璃→深玻璃、深字→淺字、霧藍→草木灰綠。
來源 ui/mist-original/（從 Larch 讀回的官方原檔），輸出 ui/rain-night/。依屬性分類換色，所以字色與底色各走各的表。"""
import re, pathlib
HERE = pathlib.Path(__file__).parent
SRC, OUT = HERE / 'mist-original', HERE / 'rain-night'
ACCENT = '#9dc4b2'          # 草木灰綠
INK = {'#1c2633': '#e9f0ee', '#17212d': '#eef3f1', '#2c3a4b': '#d9e4e1', '#3a4859': '#c3d1ce', '#556273': '#98aaa7',
       '#5f6b7a': '#93a5a2', '#7d8b9b': '#7f9895', '#0d2238': '#0b1418'}
FILL = {'#f4f8fb': '#141e25', '#eef4f9': '#18242c', '#ffffff': '#1a262e', '#fff': '#1a262e'}


def rgba(m, fg):
    r, g, b, a = m.group(1), m.group(2), m.group(3), float(m.group(4))
    rgb = (int(r), int(g), int(b))
    if rgb[0] >= 225 and rgb[1] >= 230:              # 亮玻璃面
        if fg:
            return f'rgba(236, 244, 241, {a})'
        if a >= .45:
            return f'rgba(17, 27, 34, {round(min(.9, a * .85), 2)})'
        return f'rgba(200, 228, 218, {round(a * .45, 3)})'   # 淡的亮邊、反光 → 淡綠灰邊
    if rgb == (40, 64, 92):                           # 深色細線
        return f'rgba(196, 226, 214, {a})'
    if rgb == (30, 52, 80):                           # 陰影
        return f'rgba(0, 6, 10, {round(min(.85, a + .25), 2)})'
    return m.group(0)


def recolor(prop, val):
    val = val.replace('38%, #0d2238', '72%, #ffffff')   # 重點深色：深底上要變亮，先換掉免得被下面的深字表吃掉
    if re.match(r'--.*edge', prop):                      # 玻璃亮邊 → 淡綠灰細邊
        return re.sub(r'rgba\(\s*255,\s*255,\s*255,\s*[\d.]+\s*\)', 'rgba(200, 228, 218, .2)', val)
    fg = prop in ('color', 'fill', 'stroke', 'caret-color', '-webkit-text-fill-color', 'text-decoration-color') or \
        re.match(r'--.*(ink|fg|soft|mute|text)', prop) is not None
    val = re.sub(r'rgba\(\s*(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\s*\)', lambda m: rgba(m, fg), val)
    def hexsub(m):
        h = m.group(0).lower()
        if h in ('#fff', '#ffffff'):
            return '#0e171c' if fg else '#1a262e'   # 亮重點底上的字改深；亮底改深玻璃
        if h in INK:
            return INK[h]
        return FILL.get(h, m.group(0))
    val = re.sub(r'#[0-9a-fA-F]{3,6}\b', hexsub, val)
    return val.replace('#8fc3ea', ACCENT)


def convert(text):
    # 只動宣告（prop: value），註解與 @larch-params 的 JSON 一起轉，預設色也跟著變
    text = text.replace('#8fc3ea', ACCENT).replace('"default": "day"', '"default": "night"')
    return re.sub(r'(?<![\w-])(--[\w-]+|[a-z-]+)\s*:\s*([^;{}]+?)(?=\s*(;|}|!important))',
                  lambda m: f'{m.group(1)}: {recolor(m.group(1), m.group(2))}', text)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for f in SRC.iterdir():
        t = convert(f.read_text())
        if f.name == 'dialogue.html':   # 玻璃上的雨痕：很淡的斜線疊在深玻璃上
            t = t.replace('</style>', '.box { background: repeating-linear-gradient(102deg, transparent 0 26px, rgba(200, 228, 218, .04) 26px 27px), linear-gradient(170deg, var(--glass-a), var(--glass-b)); }\n</style>', 1)
        if f.name == 'rpg.css':   # 這部沒有戰鬥：藏掉 HP、攻防魔、經驗、沒同行的夥伴格、內部變數
            t += ('\n.rpg-pause-menu :is(.pm-health, .pm-health-label, .pm-health-note, .pm-stat-row, .pm-exp, .pm-level, .pm-attributes),'
                  ' .rpg-pause-menu .pm-section-title:has(+ .pm-attributes), .rpg-pause-menu .pm-party-member:disabled,'
                  ' .rpg-pause-menu .pm-locked, body > header .hud-hp, body > header .hud-hp + * { display: none !important; }\n')
        if f.name == 'title.html':
            t = t.replace('In the morning mist', 'In the rain').replace('IN THE MORNING MIST', 'IN THE RAIN')
        if f.name == 'inventory.css':   # 「重要物品」那條引擎預設是淺黃底，深色版上字看不見
            t += '\n[data-larch-ui="detail-effects"] li { background: transparent; border: 0; box-shadow: none; }\n'
        (OUT / f.name).write_text(t)
    assert '#8fc3ea' not in ''.join(p.read_text() for p in OUT.iterdir())
    print('ok', sorted(p.name for p in OUT.iterdir()))
