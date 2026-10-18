"""分層地圖與獨立物件正式美術生成（遵循《正式地圖開工前：先用色塊確認 RPG 的遮擋層次》與《十一分鐘》規範）。
- 純地面底圖：無烘焙家具、無牆面、無人。
- 獨立透明物件：純色幕（綠幕/洋紅幕）生成，使用 cutout skill（~/.claude/skills/cutout/cutout.py）去背。
- 嚴格遵守：所有圖檔一律以 .webp 格式儲存！
用法：
  python3 art/objects_gen.py ground [bar|storage|bedroom]
  python3 art/objects_gen.py gen [bar|storage|bedroom]
  python3 art/objects_gen.py cut [bar|storage|bedroom]
  python3 art/objects_gen.py props
  python3 art/objects_gen.py all
"""
import glob, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

H = os.path.dirname(os.path.abspath(__file__))
G = os.path.dirname(H)
sys.path.insert(0, os.path.join(G, 'src'))
sys.path.insert(0, H)
import layout, blocks, codex11

PX = 48
CUTOUT = os.path.expanduser('~/.claude/skills/cutout/cutout.py')
RAW = os.path.join(H, 'raw')

LOOK = {
    'station': 'Taipei, Taiwan city street outside an MRT station at dusk in steady rain, wet glossy surfaces reflecting street lights, cool pale-blue and muted grey-green palette, soft painted anime RPG map style',
    'rooftop': 'rooftop of an old Taiwanese high school classroom building, weathered concrete, Taiwan, soft painted anime RPG map style',
    'store': 'small Taiwanese 24-hour convenience store interior at night, harsh white fluorescent light, Chinese signage only (no Japanese), soft painted anime RPG map style',
}

FLOOR = {
    'station': 'wide grey square paving-tile sidewalk soaked by rain with a narrow curb, and along the bottom a wet dark asphalt road with white lane markings and a yellow bus-stop box marking painted on the road (no letters). Dark building base along the top edge.',
    'rooftop': 'flat weathered grey concrete rooftop with water stains, cracks, a small floor drain and painted parapet edges, faded green waterproof paint patches. Top-down RPG map floor texture only.',
    'store': 'clean white and light-grey square floor tiles of a convenience store with slight fluorescent glare, a grey rubber entrance mat at the bottom center by the glass door.',
}

# (fw, fh, foot_depth, prompt_desc, fill_width, plate_color)
TYPES = {
    'station_exit': (5, 4, 2, 'a Taipei MRT station exit entrance: modern steel-and-glass canopy over a down escalator, a small green-and-white station sign panel with no readable text, wet with rain', True, 'magenta'),
    'station_pillar': (1, 4, 1, 'a single square grey concrete arcade pillar, rain-streaked, with a faded poster outline but no readable text', True, 'magenta'),
    'station_shelter': (5, 4, 1, 'a Taipei city bus shelter: transparent curved roof canopy, frosted back glass panel, a long metal bench, a bus route sign post with no readable text, rain dripping from the roof edge', True, 'magenta'),
    'rooftop_fence': (8, 2, 1, 'a long section of rusty chain-link fence along a rooftop parapet, with exactly three small brass padlocks hanging on the fence near the middle', True, 'magenta'),
    'rooftop_shed': (3, 4, 2, 'a small Taiwanese rooftop shed made of corrugated blue metal sheets (tie-pi jia-gai) with a narrow door', True, 'magenta'),
    'rooftop_tank': (2, 4, 2, 'a stainless steel cylindrical rooftop water tank on a rusty metal stand', True, 'magenta'),
    'store_fridge': (6, 2, 1, 'a row of glass-door drink refrigerators full of bottled tea, milk tea and soft drinks, labels are blurred with no readable text', True, 'magenta'),
    'store_counter': (4, 3, 2, 'a convenience store checkout counter with a cash register, a simmering oden pot and a dark tea-egg pot, a small hot food warmer', True, 'magenta'),
    'store_shelf_a': (2, 4, 3, 'a low double-sided convenience store snack shelf packed with chip bags and candy, no readable text', True, 'magenta'),
    'store_shelf_b': (2, 4, 3, 'a low double-sided convenience store shelf of instant noodle cups and bowls, no readable text', True, 'magenta'),
}

OBJ_TYPE_MAP = {
    '捷運出口': 'station_exit', '柱子': 'station_pillar', '公車亭': 'station_shelter',
    '鐵絲網與鎖': 'rooftop_fence', '鐵皮加蓋': 'rooftop_shed', '水塔': 'rooftop_tank',
    '冰箱牆': 'store_fridge', '收銀台': 'store_counter', '貨架一': 'store_shelf_a', '貨架二': 'store_shelf_b',
}

FALLBACK_RAW = {}


def get_type(o, a):
    n = o['name']
    t = OBJ_TYPE_MAP.get(n)
    if callable(t):
        return t(a)
    return t


def raw_path(t):
    base = os.path.join(RAW, f'{t}_raw.png')
    if not os.path.exists(base) and t in FALLBACK_RAW:
        fallback = os.path.join(RAW, f'{FALLBACK_RAW[t]}_raw.png')
        if os.path.exists(fallback):
            return fallback
    return base


def prompt_for(t, a):
    fw, fh, dd, desc, fill_w, plate = TYPES[t]
    bg_desc = '#00FF00 pure green' if plate == 'green' else '#FF00FF pure magenta'
    p = (
        f"Game map object sprite, one single object only, {LOOK[a]}. "
        f"3/4 top-down camera view from the south (about 50 degrees elevation, showing top and south-facing front), soft even lighting. "
        f"Redraw the object cleanly and completely as a standalone sprite.\n"
        f"Draw: {desc}.\n"
        f"Proportions: bounding box is {fw} grid cells wide and {fh} grid cells tall (aspect ratio {fw}:{fh}). "
        f"The bottom {dd} cells are its floor footprint; the top {fh - dd} cells rise up.\n"
        f"Draw only this object: no floor, no shadows on floor, no people, no background scenery. Clean edges.\n"
        f"Background: a completely flat opaque solid {bg_desc} fill, uniform color, absolutely no gradient, no drop shadow. No text, no letters."
    )
    return p


def gen_ground(a):
    d = layout.load(a)
    W, Hh = d['map']['w'], d['map']['h']
    os.makedirs(os.path.join(G, 'assets/maps'), exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    
    # 產構圖
    # 地面只照地面區塊畫：物件的色塊不能進構圖，不然地面會把物件位置畫成亮塊（雨幕 2026-10-18）
    compose_path = os.path.join(G, f'art/check/compose-{a}-ground.webp')
    if not os.path.exists(compose_path):
        subprocess.run([sys.executable, os.path.join(H, 'compose.py'), a], check=True, env=dict(os.environ, NOOBJ='1'))
        os.replace(os.path.join(G, f'art/check/compose-{a}.webp'), compose_path)
    
    out_raw = os.path.join(RAW, f'ground_{a}_raw.png')
    prompt = (
        f"Top-down painted anime RPG game map floor, {LOOK[a]}. Follow the floor region layout of image 1 exactly. "
        f"{FLOOR[a]} "
        f"Dimensions: {W} cells wide by {Hh} cells tall. Rich textures, atmospheric lighting. "
        f"Draw ONLY the floor surface materials: absolutely NO furniture, NO counters, NO walls rising up, NO doors, NO people, NO text."
    )
    if not os.path.exists(out_raw):
        print(f'Generating ground for {a}...')
        codex11.gen(prompt, out_raw, refs=[compose_path], size='1536x1024')
    
    # 縮放成 W * 48 x H * 48 並存為 .webp
    im = Image.open(out_raw).convert('RGB')
    target_size = (W * PX, Hh * PX)
    im_resized = im.resize(target_size, Image.LANCZOS)
    out_webp = os.path.join(G, f'assets/maps/{a}_ground.webp')
    im_resized.save(out_webp, 'WEBP', quality=95)
    print(f'Saved clean ground: {out_webp} ({target_size[0]}x{target_size[1]})')


def gen_objects(a, redo=False):
    d = layout.load(a)
    obs = layout.objects(d)
    jobs = {}
    for o in obs:
        t = get_type(o, a)
        if not t:
            print(f'Warning: no type for object {o["name"]}')
            continue
        if t in FALLBACK_RAW:
            continue
        rp = raw_path(t)
        if redo or not os.path.exists(rp):
            jobs[t] = prompt_for(t, a)
    
    if not jobs:
        print(f'All raw objects for {a} already exist.')
        return

    print(f'Generating {len(jobs)} raw object sprites for {a}...')
    def run_one(item):
        t, p = item
        rp = raw_path(t)
        size = '1024x1536' if TYPES[t][1] > TYPES[t][0] else '1536x1024'
        try:
            codex11.gen(p, rp, size=size)
            print(f'Generated {t} -> {rp}')
        except Exception as e:
            print(f'Failed {t}: {e}')

    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(run_one, jobs.items()))


def key_out(src, plate):
    """嚴格使用 cutout skill（~/.claude/skills/cutout/cutout.py），絕不用模型。"""
    out_png = src.replace('.png', '-keyed.png')
    cmd = [
        sys.executable, CUTOUT, 'key', src,
        '-o', out_png,
        '--key', plate,
        '--fuzz', '18',
        '--erode', '1',
        '--band', '2'
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(out_png).convert('RGBA')
    if os.path.exists(out_png):
        os.remove(out_png)
    bbox = im.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def resize_premul(im, w, h):
    """Premultiplied alpha LANCZOS 縮放（防止縮圖把底色混回邊緣）"""
    import numpy as np
    a = np.asarray(im.convert("RGBA"), np.float32)
    al = a[..., 3:4] / 255.0
    pre = np.concatenate([a[..., :3] * al, a[..., 3:4]], -1)
    r = np.asarray(Image.fromarray(pre.round().astype(np.uint8), "RGBA").resize((w, h), Image.LANCZOS), np.float32)
    al2 = np.clip(r[..., 3:4] / 255.0, 1e-4, 1.0)
    rgb = np.clip(r[..., :3] / al2, 0, 255)
    out_arr = np.concatenate([rgb, r[..., 3:4]], -1).round().astype(np.uint8)
    return Image.fromarray(out_arr, "RGBA")


def fit_sprite(fig, fw, fh, fill_w=False, plate='green'):
    """縮進圖框 (fw*48, fh*48)：等比縮放、下緣貼齊、水平置中。使用 premultiplied alpha。"""
    W, Hh = fw * PX, fh * PX
    if fill_w:
        s = W / fig.width
    else:
        s = min(W / fig.width, Hh / fig.height)
    nw, nh = max(1, round(fig.width * s)), max(1, round(fig.height * s))
    f = resize_premul(fig, nw, nh)
    if nh > Hh:
        f = f.crop((0, nh - Hh, nw, nh))
        nh = Hh
    canvas = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    canvas.alpha_composite(f, ((W - nw) // 2, Hh - nh))
    return canvas


def cut_objects(a):
    d = layout.load(a)
    od = os.path.join(G, f'assets/objects/{a}')
    os.makedirs(od, exist_ok=True)
    obs = layout.objects(d)
    
    for o in obs:
        t = get_type(o, a)
        fw, fh = o['frame'][2], o['frame'][3]
        rp = raw_path(t)
        if not os.path.exists(rp):
            print(f'Error: missing raw image for {t} ({rp})')
            continue
        plate = TYPES[t][5]
        fill_w = TYPES[t][4]
        fig = key_out(rp, plate)
        canvas = fit_sprite(fig, fw, fh, fill_w=fill_w)
        out_webp = os.path.join(od, f"{o['name']}.webp")
        canvas.save(out_webp, 'WEBP')
        print(f'Saved object: {out_webp} ({fw*PX}x{fh*PX})')


def process_props():
    """處理 assets/props/ 與 assets/objects/obj_wood_box.webp"""
    props = {
        'prop_spoon': ('art/raw/prop_spoon_raw.webp', 'magenta', 'assets/props/prop_spoon.webp'),
        'prop_saffron': ('art/raw/prop_saffron_raw.webp', 'magenta', 'assets/props/prop_saffron.webp'),
        'prop_key': ('art/raw/prop_key_raw.webp', 'magenta', 'assets/props/prop_key.webp'),
        'prop_pepper': ('art/raw/prop_pepper_raw.webp', 'magenta', 'assets/props/prop_pepper.webp'),
        'obj_wood_box': ('art/raw/obj_wood_box_green.webp', 'green', 'assets/objects/obj_wood_box.webp'),
    }
    for k, (src, plate, dst) in props.items():
        src_path = os.path.join(G, src)
        dst_path = os.path.join(G, dst)
        if not os.path.exists(src_path):
            print(f'Skip prop {k}: {src_path} not found')
            continue
        print(f'Keying prop {k} via cutout skill...')
        fig = key_out(src_path, plate)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        fig.save(dst_path, 'WEBP')
        print(f'Saved prop {k} -> {dst_path} {fig.size}')


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    maps = ['station', 'rooftop', 'store']
    
    if cmd == 'props':
        process_props()
    elif cmd == 'ground':
        target = sys.argv[2] if len(sys.argv) > 2 else 'bar'
        gen_ground(target)
    elif cmd == 'gen':
        target = sys.argv[2] if len(sys.argv) > 2 else 'bar'
        gen_objects(target)
    elif cmd == 'cut':
        target = sys.argv[2] if len(sys.argv) > 2 else 'bar'
        cut_objects(target)
    elif cmd == 'all':
        process_props()
        for m in maps:
            print(f'=== Processing {m} ===')
            gen_ground(m)
            gen_objects(m)
            cut_objects(m)


if __name__ == '__main__':
    main()
