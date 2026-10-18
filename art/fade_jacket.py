"""方澄外套褪色（design/重寫.md：每逃避一次，意識裡的她褪一點色）。
只動外套的灰綠：HSV 色相落在綠色區間、飽和度夠的像素，降飽和、略提亮。f1＝褪一半、f2＝快看不出綠。
這是調色，不改形狀（記憶 feedback_regenerate_dont_warp_art 管的是形狀）。
python3 art/fade_jacket.py → walk-fang-now-f1/f2.webp、p_fang_now_f1/f2.webp
"""
import pathlib
import numpy as np
from PIL import Image
R = pathlib.Path(__file__).resolve().parent.parent
STAGES = {'f1': (0.45, 0.06), 'f2': (0.08, 0.14)}   # (飽和度倍數, 亮度加多少)


def fade(src, dst, sat_k, light):
    im = Image.open(src).convert('RGBA'); a = np.asarray(im).astype(np.float32)
    hsv = np.asarray(im.convert('RGB').convert('HSV')).astype(np.float32)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    m = (h > 55) & (h < 165) & (s > 0.10) & (a[..., 3] > 10)
    s2 = np.where(m, s * sat_k, s); v2 = np.where(m, np.clip(v + light, 0, 1), v)
    out = np.stack([hsv[..., 0], s2 * 255, v2 * 255], -1).astype(np.uint8)
    rgb = np.asarray(Image.fromarray(out, 'HSV').convert('RGB'))
    Image.fromarray(np.concatenate([rgb, a[..., 3:4].astype(np.uint8)], -1), 'RGBA').save(dst, 'WEBP', quality=92)
    return int(m.sum())


for k, (sk, li) in STAGES.items():
    print(k, fade(R / 'assets/art/walk/walk-fang-now.webp', R / f'assets/art/walk/walk-fang-now-{k}.webp', sk, li),
          fade(R / 'assets/art/p_fang_now.webp', R / f'assets/art/p_fang_now_{k}.webp', sk, li))
