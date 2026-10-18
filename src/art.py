"""素材路徑（本機 /files/assets/…；推 Larch 時 push.py 換成 jsDelivr）。還沒產的 CG 先用黑底。"""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
F = '/files/assets/'


def paths():
    a = {'bg-black': F + 'art/bg_black.webp', 'cover': F + 'art/cover.webp'}
    for who in ('lin', 'xu', 'fang'):
        for era in ('now', 'hs'):
            a[f'p-{who}-{era}'] = F + f'art/p_{who}_{era}.webp'
            a[f'walk-{who}-{era}'] = F + f'art/walk/walk-{who}-{era}.webp'
    for k in ('f1', 'f2'):
        a[f'walk-fang-now-{k}'] = F + f'art/walk/walk-fang-now-{k}.webp'
    for k in ('cg-locks', 'cg-store', 'cg-crane', 'cg-letter', 'cg-end-a', 'cg-end-b'):
        f = ROOT / f'assets/art/{k.replace("-", "_")}.webp'
        a[k] = F + f'art/{f.name}' if f.exists() else a['bg-black']
    for k in ('rain', 'summer', 'store', 'climax', 'end-a', 'end-b'):
        f = ROOT / f'assets/bgm/{k}.mp3'
        a[f'bgm-{k}'] = F + f'bgm/{k}.mp3' if f.exists() else ''
    return a
