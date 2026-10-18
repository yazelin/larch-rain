"""組出 dist/project.json：原版骨架（skeleton/project.json）＋三張 RPG 地圖＋劇情卡＋配音（design/重寫.md）。"""
import json, pathlib, shutil, collections
import cards, variables, art, mapkit, maps, script
from script import L, card

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROJECT_ID = 'project-0b41ff6f-6947-464b-9ed2-c2cd05b87a5a'


def rpg_database(a):
    def actor(id, name, who, join):
        return {'id': id, 'name': name, 'title': '', 'profile': '', 'role': 'party', 'walk': mapkit.walker(a[f'walk-{who}-now']),
                'portrait': a[f'p-{who}-now'], 'join': join, 'kit': 'none', 'rig': '', 'joinVariable': ''}
    return {'version': 1, 'heroId': 'lin', 'leadSwitch': False,
            'actors': [actor('lin', '林宇', 'lin', 'stay'), actor('xu', '許帆', 'xu', 'later'), actor('fang', '方澄', 'fang', 'later'),
                       dict(actor('lin17', '林宇（十七歲）', 'lin', 'later'), walk=mapkit.walker(a['walk-lin-hs']), portrait=a['p-lin-hs'])]}


CHAR = {
    '林宇': dict(role='主角，大學四年級', backstory='十七歲起喜歡方澄，從沒說出口。高中頂樓打賭那天，把薄荷糖塞進她的鎖孔；畢業那天撿到她沒寄出的信，三年沒拆。',
                personality='安靜、溫和，對兩個人都好，所以更說不出口。', speakingStyle='低聲、克制，想說的話常常停在一半。', who='lin'),
    '許帆': dict(role='林宇的摯友，大學四年級', backstory='方澄喜歡的人，大學起和她在一起。知道林宇的心意，所以從不在他面前牽方澄的手。',
                personality='開朗、會照顧人，把話放在心裡。', speakingStyle='直接、帶笑，說到林宇就變小心。', who='xu'),
    '方澄': dict(role='三人之一，大學四年級', backstory='喜歡許帆，也知道林宇喜歡她。高中畢業那天寫了一封給兩個人的信，沒寄出去。',
                personality='溫柔、怕任何一個人被留在外面。', speakingStyle='輕聲、慢，常先笑再說。', who='fang'),
}


def build():
    p = json.loads((ROOT / 'skeleton/project.json').read_text(encoding='utf-8'))
    a = art.paths()
    board = p['boards'][0]
    board['description'] = '捷運站外的雨、十七歲的頂樓、十九歲的超商，在林宇的意識裡，兩個結局。'
    board['nodes'], board['edges'] = [], []
    p['nodes'], p['edges'] = board['nodes'], board['edges']
    p['variables'] = variables.project_variables()
    for c in p['characters']:
        info = CHAR.get(c.get('name'))
        if info:
            c.update({k: v for k, v in info.items() if k != 'who'})
            c['portraitUrl'] = a[f"p-{info['who']}-now"]
            c['expressions'] = [{'id': f"expression-{info['who']}-now", 'kind': 'expression', 'name': '二十一歲', 'emotion': 'calm', 'imageUrl': a[f"p-{info['who']}-now"]},
                                {'id': f"expression-{info['who']}-hs", 'kind': 'expression', 'name': '十七歲', 'emotion': 'young', 'imageUrl': a[f"p-{info['who']}-hs"]}]
    p['settings'].setdefault('plugins', {})['larch-rpg-system'] = {'enabled': True, 'settings': {'database': json.dumps(rpg_database(a), ensure_ascii=False)}}
    p['settings']['titleCoverImage'] = a['cover']
    p['settings']['projectThumbnail'] = a['cover']
    p['projectThumbnail'] = a['cover']   # 專案最外層也有一份縮圖（原版是日式車站那張）
    if a.get('bgm-rain'):
        p['settings'].setdefault('titleScreen', {})['bgm'] = a['bgm-rain']
    p['settings']['cgGallerySource'] = 'picked'
    p['settings']['cgGalleryItems'] = [{'url': a[k], 'title': t} for k, t in (
        ('cover', '淡藍與草木灰綠的雨幕'), ('cg-locks', '三把鎖'), ('cg-store', '抽回的傘柄'), ('cg-crane', '一聲對不起'),
        ('cg-letter', '給林宇、許帆'), ('cg-end-a', '各自的公車'), ('cg-end-b', '雨不會停')) if a[k] != a['bg-black']]
    p['settings']['menuUi'] = {'preset': 'night', 'accent': '#8fbfa8', 'title': '淡藍與草木灰綠的雨幕', 'eyebrow': '林宇的意識裡', 'buttons': ['bag', 'save', 'load', 'title']}

    N = board['nodes'].append
    link = lambda x, y: cards.link(board, x, y)
    for m in maps.all_maps(a):
        N(m)

    bg = a['bg-black']
    N(card('prologue', '序：最後一晚', a, bg=a['cover'], start=True, bgm=a.get('bgm-rain') or None))
    # 接在 CG 後面的卡片也要有背景，不然上一張 CG 會留在畫面上、立繪疊在 CG 的人身上（作者 2026-10-18 截圖）
    big = {'ending_a1': a['cg-letter'], 'card_r17_candy': a['cg-locks'], 'card_st_pull': a['cg-store'], 'card_st_solve': a['cg-crane'], 'card_letter': a['cg-letter'],
           'ending_a2': a['cg-end-a'], 'ending_b1': a['cg-end-b'], 'ending_b2': a['cg-end-b']}
    era = {k: 'hs' for k in ('card_r17_intro', 'card_r17_try', 'card_r17_candy')}
    jumped = {'card_st_shift': bg, 'card_r17_enter': bg, 'card_r17_shift': bg, 'card_r21_back': bg, 'card_st_enter': bg, 'card_st_back': bg,
              'card_letter': None}
    for cid in L:
        if cid == 'prologue':
            continue
        b = big.get(cid) if big.get(cid) != bg else None
        if cid in jumped and jumped[cid]:
            b = jumped[cid]
        extra = {}
        if cid.startswith('card_climax') and a.get('bgm-climax'):
            extra['bgm'] = a['bgm-climax']
        if cid == 'ending_a1' and a.get('bgm-end-a'):
            extra['bgm'] = a['bgm-end-a']
        if cid == 'ending_b1' and a.get('bgm-end-b'):
            extra['bgm'] = a['bgm-end-b']
        N(card(cid, cid, a, bg=b or '', era=era.get(cid, 'now'), **extra))
    N(cards.choice('card_choice', '最後的雨幕', '雨越下越大。手裡的信微微發燙，兩把傘還是冰的。',
                   ['交出信，承認平行線不必勉強交會', '緊握兩把傘退後，把秘密藏起來'], speaker='林宇', bg=a['cg-letter'] if a['cg-letter'] != bg else ''))

    link('prologue', 'm-station')
    link('card_r17_shift', 'm-rooftop-21')
    link('card_r21_back', 'm-station')
    link('card_st_back', 'm-station')
    for k in ('lo', 'mid', 'hi'):
        link(f'card_climax_{k}', 'card_letter')
    link('card_letter', 'card_choice')
    cards.choice_link(board, 'card_choice', 'ending_a1', 0)
    cards.choice_link(board, 'card_choice', 'ending_b1', 1)
    link('ending_a1', 'ending_a2')
    link('ending_b1', 'ending_b2')
    print('地圖內心話轉成配音卡：', script.voice_map_lines(board))

    # 檢查：一格一個事件、選擇題不能是事件的第一個動作（晚霞踩過）
    for n in board['nodes']:
        if n['id'].startswith('m-'):
            m = json.loads(n['data']['pluginValues']['map'])
            dup = [k for k, v in collections.Counter((e['x'], e['y']) for e in m['events']).items() if v > 1]
            assert not dup, (n['id'], '同一格多個事件', dup)
            for e in m['events']:
                for acts in [e.get('actions') or []] + [pg.get('actions') or [] for pg in e.get('pages') or []]:
                    assert not acts or acts[0].get('kind') != 'choice', (n['id'], e['id'], '選擇題是第一個動作')

    (ROOT / 'dist').mkdir(exist_ok=True)
    out = ROOT / 'dist/project.json'
    out.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding='utf-8')
    dst = ROOT / 'dist/assets'
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(ROOT / 'assets', dst)
    print(f'Build finished! {out} ({len(board["nodes"])} nodes, {len(board["edges"])} edges)')
    return p


if __name__ == '__main__':
    build()
