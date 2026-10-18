"""地圖上的道具圖：兩個回憶入口的水窪（意識：水窪裡映出的不是街燈）。洋紅幕生成、cutout 去背。
python3 art/gen_props.py gen / cut → assets/props/<名>.webp
"""
import sys, pathlib, subprocess, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
R = pathlib.Path(__file__).resolve().parent.parent
RAW = R / 'art/raw/props'
CUT = pathlib.Path.home() / '.claude/skills/cutout/cutout.py'
BASE = ('Game map decal sprite, top-down 3/4 view, soft painted anime RPG map style, matching a rainy Taipei sidewalk of grey square paving tiles at dusk. '
        'One single irregular rain puddle, seen from above, with soft wet edges and gentle ripples. '
        'Solid flat pure magenta #FF00FF background around the puddle, no gradient, no shadow, nothing touches the border. No text.')
PROPS = {
    'puddle_rooftop': BASE + ' Inside the puddle, instead of street lights, the reflection shows a rusty chain-link fence against a sickly teal-green sunset sky, faintly glowing.',
    'puddle_store': BASE + ' Inside the puddle, instead of street lights, the reflection shows the harsh white fluorescent glow of a convenience store window at night, faintly glowing.',
}


def gen(k):
    import codex11
    return codex11.gen(PROPS[k], str(RAW / f'{k}.png'), size='1536x1024')


def cut(k):
    subprocess.run([sys.executable, str(CUT), 'key', str(RAW / f'{k}.png'), '-o', str(RAW / f'{k}_cut.png'), '--key', 'magenta'], check=True, capture_output=True)
    from PIL import Image
    im = Image.open(RAW / f'{k}_cut.png').convert('RGBA'); im = im.crop(im.getbbox()); im.thumbnail((360, 240))
    im.save(R / f'assets/props/{k}.webp', 'WEBP', quality=90); print(k, im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'gen':
        with cf.ThreadPoolExecutor(2) as ex: print(list(ex.map(gen, PROPS)))
    else:
        for k in PROPS: cut(k)
