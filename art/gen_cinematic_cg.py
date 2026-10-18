"""雨幕全劇 CG（design/重寫.md「美術」）：電影感、台北、每張帶在場角色定錨。
python3 art/gen_cinematic_cg.py <名> [次數] → art/raw/cine/<名>_<n>.png；選定後 art/install_cg.py
"""
import sys, pathlib, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import codex11

R = pathlib.Path(__file__).resolve().parent.parent
A = lambda n: R / f'assets/art/p_{n}.webp'
STYLE = ('Cinematic anime feature-film still, painterly, restrained and literary, high-end Japanese-animation-quality lighting but the SETTING IS TAIPEI, TAIWAN: '
         'Chinese characters on signs only and never readable, Taiwanese street furniture, absolutely no Japanese text, no Japanese houses or utility-pole streets. '
         'Anamorphic lens feel, shallow depth of field, soft bokeh, subtle film grain, motivated light only. Palette: cold pale blue rain and muted sage grass-ash-green as the one accent. '
         'Faces and outfits must match the reference images exactly; hands with five fingers. No text, no letters, no logos, no watermark. 16:9.')
WHO = {
    'lin_now': 'LIN YU (21): short straight black hair, charcoal-brown zip jacket over white T-shirt, dark jeans',
    'xu_now': 'XU FAN (21): messy wavy black hair, dark grey hoodie, black joggers',
    'fang_now': 'FANG CHENG (21): shoulder-length black hair, white blouse, cream cardigan, light-blue jeans, often wearing XU FAN\'s oversized sage grey-green jacket over her shoulders',
    'lin_hs': 'LIN YU (17): short black hair, Taiwanese high school white short-sleeve shirt and navy trousers',
    'xu_hs': 'XU FAN (17): messy wavy black hair, Taiwanese high school white short-sleeve shirt and navy trousers',
    'fang_hs': 'FANG CHENG (17): long black hair in a low ponytail, Taiwanese high school white blouse and navy pleated skirt',
}
CG = {
    'cover': (['lin_now', 'xu_now', 'fang_now'],
        'Key art, no text. Rainy dusk outside a Taipei MRT station exit, wet glossy sidewalk tiles reflecting street lights. Foreground left, LIN YU stands half hidden behind a square concrete arcade pillar, '
        'holding two closed umbrellas in one hand (a clear convenience-store plastic umbrella and a dark-blue umbrella with one bent rib), looking toward the bus shelter. '
        'In the background right, under a lit transparent Taipei bus shelter, XU FAN is draping his sage grey-green jacket over FANG CHENG\'s shoulders; she tilts her head with a faint smile. '
        'Rain falling between them like a curtain. Lots of rain and empty space; the jacket\'s grey-green is the only warm accent.'),
    'cg_locks': (['lin_hs', 'xu_hs', 'fang_hs'],
        'Seventeen, summer, the rooftop of an old Taiwanese high school building at sunset, the sky a strange teal-green, rusty chain-link fence with three small brass padlocks. '
        'LIN YU (17) presses a small pale-green mint candy into the keyhole of one padlock, hiding it with his body; FANG CHENG (17) has turned away laughing at something; '
        'XU FAN (17) a step behind, silently watching LIN YU do it. Close on the hand and the lock, faces at the edge of the frame. Bittersweet.'),
    'cg_store': (['lin_now', 'fang_now'],
        'Nineteen, a rainy night at the glass door of a small Taiwanese 24-hour convenience store, harsh white fluorescent light inside, cold blue rain outside. '
        'FANG CHENG stands at the door wearing XU FAN\'s sage grey-green jacket over her head and shoulders, looking at the rain; beside her LIN YU is pulling a dark-blue umbrella back toward himself, '
        'his hand retreating, his face turned away. The space between their hands is the center of the picture.'),
    'cg_crane': (['lin_now'],
        'Close-up inside a dreamlike empty convenience store, shelves fading into light. LIN YU\'s open palm under the soft pale-blue glow of a cash register scanner window; '
        'on his palm rests a translucent ice-blue paper crane made of light. His face blurred above. Quiet, aching.'),
    'cg_letter': (['lin_now', 'xu_now', 'fang_now'],
        'Night, inside a Taipei bus shelter, rain dripping from the roof edge. LIN YU, wet, unfolds a letter taken from a sage grey-green envelope tied with twine; '
        'XU FAN and FANG CHENG beside him watching, FANG wearing XU\'s grey-green jacket. Close on the letter paper (handwriting is not readable) and LIN\'s hands. One old water stain on the paper.'),
    'cg_end_a': (['lin_now', 'xu_now', 'fang_now'],
        'Dawn after an all-night rain at a Taipei bus stop. Clouds parting, pale blue sky with a thin line of gold. Three different city buses arriving at the same time (no readable route numbers). '
        'The three friends stand on the wet sidewalk, each turning toward a different bus, LIN YU folding the dark-blue umbrella, FANG wearing the grey-green jacket, small smiles. Hopeful and sad.'),
    'cg_end_b': (['lin_now', 'xu_now', 'fang_now'],
        'Endless rain at night outside the Taipei bus shelter, grey and cold. FANG CHENG is dissolving into small teal-green fireflies, the grey-green jacket on her shoulders faded to grey and peeling away in pieces. '
        'XU FAN kneels in a dark puddle reaching for her. In the far foreground LIN YU stands behind a concrete pillar, two umbrellas dropped on the wet ground. Tragic.'),
}


def one(name, n):
    who, scene = CG[name]
    cast = ' '.join(f'Reference {i + 1} is {WHO[w]}.' for i, w in enumerate(who))
    return codex11.gen(f'{STYLE} {cast} Scene: {scene}', str(R / f'art/raw/cine/{name}_{n}.png'), refs=[str(A(w)) for w in who], size='1536x1024')


if __name__ == '__main__':
    names = sys.argv[1:] or list(CG)
    jobs = [(n, k) for n in names for k in (1, 2)]
    with cf.ThreadPoolExecutor(4) as ex:
        for f in ex.map(lambda j: one(*j), jobs): print(f, flush=True)
