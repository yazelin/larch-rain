"""三人對話立繪第四輪（2026-10-18 作者：直接畫進 CG 的人物都比較好，獨立畫就比較差）。
差別在四件事，這一輪照遊戲實際顯示的方式畫：
1. 光：拿掉「光線均勻」，照台北雨夜的光打（一側冷主光、另一側暖路燈反光、頭髮與肩膀雨水濕亮）；背景仍是平的洋紅幕好去背。
2. 演：每人一個帶情緒的動作，不是設定圖的站法。
3. 尺寸：只畫大腿以上的半身，臉用整張解析度畫（遊戲裡本來就是半身顯示）。
4. 參考：定錨立繪（臉、髮、衣服）＋同角色的 CG 裁切（畫法與光影）。
python3 art/gen_standees.py gen [名…] / cut [名…]  → art/raw/standee/<名>_<n>.png
"""
import os, sys, pathlib, subprocess, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
R = pathlib.Path(__file__).resolve().parent.parent
RAW = R / 'art/raw/standee'
APPEAL = ''   # 每人一句好看的方向，寫在 WHO 的描述裡（作者 2026-10-18：是因為人不夠帥嗎）
CUT = pathlib.Path.home() / '.claude/skills/cutout/cutout.py'
BASE = ('A premium visual-novel character standee, HALF BODY from mid-thigh up, the figure fills the height of the image, face large and highly detailed. '
        'Cinematic anime feature-film rendering exactly like Reference 2 (a film still of this same character from our own CG): painterly light and shadow, '
        'unless told otherwise, lit as if standing on a rainy Taipei street at night: cool blue-white key light from the left, warm amber street-light bounce on the right side of the face, '
        'a thin bright rim light on the hair and shoulders, damp hair with a few raindrops catching light, rich hand-painted fabric texture and folds, subtle film color grading. '
        'Face, hairstyle and outfit exactly like Reference 1, but drawn as an attractive lead character of a romance anime film: refined, well-proportioned features, '
        'expressive deep eyes with layered irises and soft lower-lid shadow, defined jawline and nose bridge, beautiful natural skin, appealing and memorable; still clearly the same person. '
        + APPEAL + ' '
        'Background: a completely flat, uniform pure magenta #FF00FF, no gradient, no scenery, no rain drawn on the background, nothing touches the left, right or top border. '
        'No text, no letters, no logos.')
WHO = {
    'lin_now': ('lin_now', 'LIN YU, 21, cool and delicately handsome, slender: quiet, holding two closed umbrellas in his right hand (a clear plastic one and a dark-blue one with a bent rib), '
                'body half turned, eyes looking away to the side, the faint ache of someone who cannot say something.'),
    'xu_now': ('xu_now', 'XU FAN, 21, sunny warm handsome with a bright charming smile: both hands in the pocket of his dark grey hoodie, warm easy smile, head slightly tilted, kind eyes that notice everything.'),
    'fang_now': ('fang_now', 'FANG CHENG, 21, gentle graceful beauty with a soft lasting charm: one hand holding the collar of the oversized sage grey-green jacket closed at her chest, '
                 'head slightly lowered with a soft small smile, eyes gentle and a little sad.'),
    'lin_hs': ('lin_hs', 'LIN YU, 17, cool and delicately handsome boy, in summer high school uniform: hands behind his back hiding something, a nervous half smile, looking sideways. '
               'Lit by a warm teal-green summer sunset instead of rainy night light.'),
    'xu_hs': ('xu_hs', 'XU FAN, 17, sunny charming handsome boy, in summer high school uniform: one hand on the back of his neck, laughing, sleeves rolled. '
              'Lit by a warm teal-green summer sunset instead of rainy night light.'),
    'fang_hs': ('fang_hs', 'FANG CHENG, 17, a gentle pretty girl with lasting charm, in summer high school uniform: holding a small brass padlock up with both hands, bright teasing smile. '
                'Lit by a warm teal-green summer sunset instead of rainy night light.'),
}


def gen(job):
    import codex11
    name, n = job
    anchor, desc = WHO[name]
    return codex11.gen(BASE + ' Character: ' + desc, str(RAW / f'{name}_{n}.png'),
                       refs=[str(R / f'assets/art/anchor_{anchor}.webp'), str(R / f'art/raw/styleref/{name}.png')], size='1024x1536')


def cut(name, n):
    subprocess.run([sys.executable, str(CUT), 'key', str(RAW / f'{name}_{n}.png'), '-o', str(RAW / f'{name}_{n}_cut.png'), '--key', 'magenta'], check=True, capture_output=True)


KS = [int(x) for x in os.environ.get('KS', '1,2').split(',')]

if __name__ == '__main__':
    cmd, names = sys.argv[1], sys.argv[2:] or list(WHO)
    if cmd == 'gen':
        with cf.ThreadPoolExecutor(4) as ex:
            for f in ex.map(gen, [(nm, k) for nm in names for k in KS]): print(f, flush=True)
    else:
        for nm in names:
            for k in KS: cut(nm, k)
