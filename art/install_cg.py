"""選定的 CG：art/raw/cine/<名>_<n>.png → 裁 16:9（垂直位置可調）→ 1376x774 webp → assets/art/<名>.webp
python3 art/install_cg.py cg_ending_burn 1 [垂直偏移 0~1，預設 0.5 置中]"""
import sys, pathlib
from PIL import Image
R = pathlib.Path(__file__).resolve().parent.parent
name, n = sys.argv[1], sys.argv[2]
off = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
im = Image.open(R / f'art/raw/cine/{name}_{n}.png').convert('RGB')
w, h = im.size; ch = round(w * 9 / 16); top = round((h - ch) * off)
out = R / f'assets/art/{name}.webp'
im.crop((0, top, w, top + ch)).resize((1376, 774), Image.LANCZOS).save(out, 'WEBP', quality=88)
print(out, out.stat().st_size // 1024, 'KB')
