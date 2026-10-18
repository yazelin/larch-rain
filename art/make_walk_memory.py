"""回憶一、二的沈淮便服行走圖(還不是調酒師:白襯衫捲袖、沒穿背心、沒打領帶)。
流程:codex 綠幕生圖 → cutout.py key → 依連通區塊切出 12 格 → 每格照現有 walk-shen 的高度、腳底 y=251、水平置中
→ 朝左那排(第 2 列)用朝右(第 3 列)鏡射。生圖原檔在 art/raw/mem/,成品進 assets/。
用法:python3 art/make_walk_memory.py gen|build
"""
import sys, pathlib, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, str(pathlib.Path(__file__).parent))
R = pathlib.Path(__file__).resolve().parent.parent
RAW = R / 'art/raw/mem'
CUT = pathlib.Path.home() / '.claude/skills/cutout/cutout.py'
REF = '/tmp/claude-1000/-home-ct/80451013-2244-4197-890a-ba15e9231496/scratchpad/walk_shen_ref.png'
ROW_H = [239, 229, 229, 224]          # 現有 walk-shen 每列人物高度(像素)
FOOT = 251
GREEN = ('Solid flat pure green #00FF00 background, even lighting, crisp edges, no shadow, no ground, no gradient, '
         'nothing touches the image border. No text.')

WALK = ('Reference 1 is a walking sprite sheet of SHEN: 3 columns x 4 rows (rows top to bottom: facing down, facing left, facing right, facing up; '
        'columns: left foot forward, standing, right foot forward). Redraw a NEW sprite sheet with exactly the same 3x4 grid, same chibi proportions, '
        'same poses and same soft anime style. Reference 2 is his portrait for the face and hair. Outfit change, casual clothes, NOT a bartender: '
        'plain white shirt with the collar open and sleeves rolled up, NO waistcoat, NO tie, dark trousers, dark shoes. '
        'Twelve separate full-body figures, evenly spaced, none touching. ' + GREEN)


def gen():
    import codex11
    codex11.gen(WALK, str(RAW / 'walk_shen_casual_raw.png'), refs=[REF, str(R / 'assets/art/p_shen.webp')], size='1024x1536')


def key(src, dst):
    subprocess.run([sys.executable, str(CUT), 'key', str(src), '-o', str(dst), '--key', 'green'], check=True)


def premul_resize(im, size):
    a = np.asarray(im, np.float32); al = a[..., 3:4] / 255.0
    pre = np.concatenate([a[..., :3] * al, a[..., 3:4]], -1)
    r = np.asarray(Image.fromarray(pre.round().astype(np.uint8), 'RGBA').resize(size, Image.LANCZOS), np.float32)
    al2 = np.clip(r[..., 3:4] / 255.0, 1e-4, 1.0)
    return Image.fromarray(np.concatenate([np.clip(r[..., :3] / al2, 0, 255), r[..., 3:4]], -1).round().astype(np.uint8), 'RGBA')


def build():
    key(RAW / 'walk_shen_casual_raw.png', RAW / 'walk_shen_casual_cut.png')
    im = Image.open(RAW / 'walk_shen_casual_cut.png').convert('RGBA')
    # 生成圖本身就排成 3×4 等分格,照格子切(連通區塊會把手臂靠近的鄰格黏在一起)
    cw, ch = im.width / 3, im.height / 4
    rows = [[(slice(round(r * ch), round((r + 1) * ch)), slice(round(c * cw), round((c + 1) * cw))) for c in range(3)] for r in range(4)]
    sheet = Image.new('RGBA', (576, 1024), (0, 0, 0, 0))
    for r, row in enumerate(rows):
        for c, (ys, xs) in enumerate(row):
            fig = im.crop((xs.start, ys.start, xs.stop, ys.stop))
            # 生圖常在腳底畫一條陰影線:只留最大的那塊人形,零碎小塊清掉
            fa = np.asarray(fig).copy(); lab, n = ndimage.label(fa[..., 3] > 40)
            if n > 1:
                keep = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
                fa[(lab != keep) & (lab > 0), 3] = 0
                fig = Image.fromarray(fa, 'RGBA')
            bb = fig.getbbox(); fig = fig.crop(bb)
            h = ROW_H[r]; w = round(fig.width * h / fig.height)
            fig = premul_resize(fig, (w, h))
            sheet.alpha_composite(fig, (c * 192 + (192 - w) // 2, r * 256 + FOOT - h + 1))
    # 這次生出來第二列(朝左)最確定,第三列的朝向不一定對:朝右那列一律用朝左鏡射
    left = sheet.crop((0, 256, 576, 512))
    right = Image.new('RGBA', (576, 256), (0, 0, 0, 0))
    for c in range(3):
        right.alpha_composite(left.crop((c * 192, 0, (c + 1) * 192, 256)).transpose(Image.FLIP_LEFT_RIGHT), ((2 - c) * 192, 0))
    sheet.paste(right, (0, 512))
    out = R / 'assets/art/walk/walk-shen-casual.webp'
    sheet.save(out, 'WEBP', quality=90, lossless=False)
    subprocess.run([sys.executable, str(CUT), 'check', str(out), '--key', 'green'], check=True)
    print(out)


if __name__ == '__main__':
    {'gen': gen, 'build': build}[sys.argv[1]]()
