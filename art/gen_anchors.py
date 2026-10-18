"""三人的定錨立繪（design/重寫.md 美術）：二十一歲便服、十七歲台灣高中制服。
臉與髮型沿用原版立繪（art/original/1x_sprite_*），衣服照設計重做；洋紅幕生成（方澄穿草木灰綠外套，不能用綠幕），再用 cutout skill 去背。
python3 art/gen_anchors.py gen [名…] / cut [名…]   → art/raw/anchor/<名>.png → assets/art/p_<名>.webp
"""
import sys, pathlib, subprocess, glob, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
R = pathlib.Path(__file__).resolve().parent.parent
RAW = R / 'art/raw/anchor'
import os
SUFFIX = os.environ.get('SUFFIX', '')   # 重產第二輪：SUFFIX=_v2a / _v2b（2026-10-18 作者要求更細緻）
EXTRA = {}
CUT = pathlib.Path.home() / '.claude/skills/cutout/cutout.py'
ORIG = {k: glob.glob(str(R / f'art/original/*sprite_{v}*'))[0] for k, v in (('lin', 'linyu'), ('xu', 'xufan'), ('fang', 'fangcheng'))}
BASE = ('Full-body standing character portrait for a premium visual novel, extremely detailed high-end anime illustration: '
        'fine individual hair strands with soft highlights, detailed eyes with layered irises and catchlights, natural skin shading, '
        'realistic fabric folds, stitching, seams and texture on every garment, subtle rim light, painterly cel shading with depth, clean confident linework, '
        'realistic proportions (NOT chibi), '
        'slight three-quarter view facing the viewer, relaxed natural pose, arms at the sides. Keep the face and hairstyle exactly like Reference 1. '
        'Set in Taipei, Taiwan. Solid flat pure magenta #FF00FF background, even lighting, crisp edges, no shadow, no ground, no gradient, '
        'nothing touches the image border. No text, no letters, no logos, no name tag.')
WHO = {
    'lin_now': ('lin', 'LIN YU, 21-year-old Taiwanese university senior, slim, short straight black hair, quiet thoughtful eyes. '
                'Outfit: dark charcoal-brown casual zip jacket over a plain white T-shirt, dark blue jeans, white sneakers. Empty hands.'),
    'xu_now': ('xu', 'XU FAN, 21-year-old Taiwanese university senior, a little taller and broader, messy wavy black hair, warm easy smile. '
               'Outfit: dark grey hoodie, black joggers, sneakers. Empty hands.'),
    'fang_now': ('fang', 'FANG CHENG, 21-year-old Taiwanese university senior, slender, long straight black hair, gentle eyes, soft faint smile. '
                 'Outfit: a man\'s oversized muted sage grass-ash-green (grey-green) jacket draped over her shoulders, under it a white blouse and a cream knit cardigan, '
                 'light-blue straight jeans, white sneakers. Empty hands.'),
    'lin_hs': ('lin', 'LIN YU at 17, Taiwanese high-school boy, same face but younger. Taiwanese high school summer uniform: white short-sleeve shirt, '
               'navy blue trousers, black belt, black shoes. No embroidery, no badge, no text.'),
    'xu_hs': ('xu', 'XU FAN at 17, Taiwanese high-school boy, same face but younger, grinning. Taiwanese high school summer uniform: white short-sleeve shirt, '
              'navy blue trousers, black shoes, sleeves a little rolled. No embroidery, no badge, no text.'),
    'fang_hs': ('fang', 'FANG CHENG at 17, Taiwanese high-school girl, same face but younger, long straight black hair in a low ponytail. Taiwanese high school summer uniform: '
                'white short-sleeve blouse, navy blue pleated knee-length skirt, white socks, black shoes. No embroidery, no badge, no text.'),
}


def gen(name):
    import codex11
    ref, desc = WHO[name]
    return codex11.gen(BASE + ' Reference 1 is the same character (face and hair only; ignore its clothes and dark background). Character: ' + desc,
                       str(RAW / f'{name}{SUFFIX}.png'), refs=[ORIG[ref]] + EXTRA.get(name, []), size='1024x1536')


def cut(name):
    subprocess.run([sys.executable, str(CUT), 'key', str(RAW / f'{name}.png'), '-o', str(RAW / f'{name}_cut.png'), '--key', 'magenta'], check=True)
    from PIL import Image
    im = Image.open(RAW / f'{name}_cut.png').convert('RGBA'); im = im.crop(im.getbbox())
    im.thumbnail((900, 1500)); im.save(R / f'assets/art/p_{name}.webp', 'WEBP', quality=90)
    print(name, im.size)


if __name__ == '__main__':
    cmd, names = sys.argv[1], sys.argv[2:] or list(WHO)
    if cmd == 'gen':
        with cf.ThreadPoolExecutor(3) as ex:
            for f in ex.map(gen, names): print(f)
    else:
        for n in names: cut(n)
