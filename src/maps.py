"""三張地圖、四個地圖節點（design/重寫.md「全劇流程與地圖」）。
m-station：意識裡捷運站外的雨（現在，林宇二十一歲）。兩個水窪是回憶入口；公車亭前那條線要兩段回憶都走完才消失。
m-rooftop-17：頂樓，十七歲夏天的重播。m-rooftop-21：同一張頂樓，意識裡二十一歲的雨。
m-store：大學旁的超商，十九歲的雨夜。
地圖上含「我」的 say 會在建置時轉成林宇的配音卡（script.voice_map_lines）。
"""
import os
from mapkit import *
import layout

ROOT = layout.ROOT


def _urls(a):
    d = layout.load(a)
    real = all((ROOT / f"assets/objects/{a}/{o['name']}.webp").exists() for o in layout.objects(d)) and (ROOT / f'assets/maps/{a}_ground.webp').exists()
    kind = 'objects' if real and not os.environ.get('BLOCKS') else 'blocks'
    ground = f'/files/assets/maps/{a}_{"ground" if kind == "objects" else "blocks"}.webp'
    return d, ground, {o['name']: f"/files/assets/{kind}/{a}/{o['name']}.webp" for o in layout.objects(d)}


def _map(mid, title, a, events, guidance, env, bgm=''):
    d, ground, urls = _urls(a)
    evs = events + [dict(e, id=e['id'].replace(f"obj-{d['map']['id']}", f'obj-{mid}')) for e in layout.events(d, urls)]
    m = map_dict(title, d['map']['w'], d['map']['h'], ground, layout.walls(d), evs, guidance, env)
    return map_node(mid, title, m, bgm=bgm)


def _env(dark, tint, strength, lights, particles=None):
    e = {'weather': 'clear', 'intensity': 0, 'darkness': dark, 'shake': 0,
         'lights': [dict(zip(('id', 'x', 'y', 'radius', 'color', 'flicker'), l)) for l in lights],
         'ambience': {'tint': tint, 'tintStrength': strength, 'vignette': 0.35}}
    if particles:
        e['ambience'].update({'particles': particles, 'density': 0.15})
    return e


def hero(x, y, art, who, d='up'):
    # 引擎用資料庫裡主角的行走圖蓋掉這裡給的（不綁也一樣）；十七歲要穿制服，所以綁資料庫裡另一個角色 lin17（2026-10-18 試玩截圖抓到）
    return ev('hero', x, y, actor='player', direction=d, sprite=walker(art[f'walk-{who}']), actorId='lin17' if who.endswith('-hs') else 'lin')


def fang_now(eid, x, y, art, d='left', **kw):
    """意識裡的方澄：外套隨 fade 褪色（0 原色、1 褪一半、2 以上快看不出綠）。"""
    return npc(eid, x, y, walker(art['walk-fang-now']), direction=d, name='方澄',
               pages=[page(f'{eid}-f2', [cond('fade', 2, 'gte')], [], actor='npc', sprite=walker(art['walk-fang-now-f2']), solid=True, direction=d),
                      page(f'{eid}-f1', [cond('fade', 1, 'gte')], [], actor='npc', sprite=walker(art['walk-fang-now-f1']), solid=True, direction=d)], **kw)


def puddle(eid, x, y, url):
    # 水窪道具圖：地面裝飾，畫在人物底下（引擎照 y+h-1 排序，小的先畫）
    return ev(f'{eid}-visual', 0, y, name=f'{eid} 視覺', free={'url': url, 'x': x - 0.9, 'y': y - 0.35, 'w': 1.9, 'h': 1.25})


def station(art):
    P = {k: tuple(v) for k, v in layout.load('station')['points'].items()}
    both = [cond('rooftop_done', True), cond('store_done', True)]
    events = [
        hero(*P['hero_start'], art, 'lin-now', 'right'),
        npc('xu', *P['shelter_xu'], walker(art['walk-xu-now']), direction='right', name='許帆'),
        fang_now('fang', *P['shelter_fang'], art, d='left'),
        # 進場：許帆替方澄披外套（被迫看著）→ 意識的規則
        ev('intro', 1, 12, trigger='auto', once=True, actions=[
            card('card_jacket'),
            choice_action('許帆替她披上外套的那一下。', [
                ('看著', [card('card_look')]),
                ('轉開頭', [card('card_away'), addv('fade', 1)]),
            ], speaker='player'),
            card('card_rule'),
            item('candy', '半融的薄荷糖'), item('umbrellas', '兩把傘'),
            setv('phase', 'hub'),
        ]),
        puddle('puddle-rooftop', *P['puddle_rooftop'], '/files/assets/props/puddle_rooftop.webp'),
        puddle('puddle-store', *P['puddle_store'], '/files/assets/props/puddle_store.webp'),
        ev('puddle_rooftop', *P['puddle_rooftop'], name='水窪', marker={'label': '水窪', 'kind': 'quest'},
           conditions=[cond('rooftop_done', False)],
           actions=[card('card_r17_enter'), jump('m-rooftop-17', arrive={'x': 8, 'y': 9, 'direction': 'up'})]),
        ev('puddle_store', *P['puddle_store'], name='水窪', marker={'label': '水窪', 'kind': 'quest'},
           conditions=[cond('store_done', False)],
           actions=[branch([cond('rooftop_done', True)],
                           [card('card_st_enter'), jump('m-store', arrive={'x': 7, 'y': 8, 'direction': 'up'})],
                           [say('水窪裡有一片慘白的光，太遠了，我看不清楚。', speaker='player')])]),
        ev('look_exit', 4, 4, name='捷運出口', trigger='action', marker={'label': '捷運出口', 'kind': 'talk'},
           actions=[say('出口上方的站名牌寫著「青禾站」。末班捷運早就開走了，我們說好一起等天亮的首班公車。', speaker='player')]),
        ev('look_pillar', 12, 7, name='柱子', trigger='action',
           actions=[say('這根柱子剛好擋住我。從他們那邊，看不到我。', speaker='player')]),
        # 公車亭入口（14,6）：兩段回憶都走完之前擋住；走完後換成「走進公車亭」（一格一個事件，用 page 切換）
        ev('shelter_gate', 14, 6, name='公車亭', trigger='touch', solid=True,
           actions=[say('還不是現在。我還不能過去。', speaker='player')],
           pages=[page('gate-open', both, [
               setv('phase', 'climax'),
               # 先播卡再 jump 會把卡跳掉（2026-10-18 試玩：外套描述沒出現），改成判斷後直接跳到三張開場之一
               branch([cond('fade', 2, 'gte')], [jump('card_climax_hi')],
                      [branch([cond('fade', 1, 'gte')], [jump('card_climax_mid')], [jump('card_climax_lo')])]),
           ], trigger='touch', solid=False)]),
    ]
    # 靠近公車亭（x=13 那一排）：心跳聲（設計：越靠近，雨聲越小、心跳越清楚）
    for y in range(2, 11):
        if (13, y) != (12, 6):
            events.append(ev(f'heart{y}', 13, y, name='心跳', trigger='touch', actions=[A('sound', audio={'url': '/sfx/heartbeat.mp3', 'volume': 0.8})]))
    # 公車亭前那條線（x=14，人行道到車道）：兩段回憶都走完之前擋住
    for y in list(range(2, 6)) + list(range(7, 11)):
        events.append(ev(f'line{y}', 14, y, name='還不是現在', trigger='touch', solid=True,
                         conditions=[cond('store_done', False)],
                         actions=[say('還不是現在。我還不能過去。', speaker='player')]))
    guidance = [
        {'text': '水窪裡映出的頂樓', 'eventId': 'puddle_rooftop', 'conditions': [cond('phase', 'hub'), cond('rooftop_done', False)]},
        {'text': '水窪裡映出的超商', 'eventId': 'puddle_store', 'conditions': [cond('rooftop_done', True), cond('store_done', False)]},
        {'text': '走進公車亭', 'eventId': 'shelter_gate', 'conditions': both},
    ]
    env = _env(0.4, '#4f6f9f', 0.32, [
        ('shelter', 17, 4, 4, '#cfe4ff', False), ('exit', 4, 3, 4, '#bfe8d2', False),
        ('street', 9, 9, 6, '#ffd9a0', True), ('lamp2', 19, 9, 4, '#ffd9a0', False)], particles='motes')
    return _map('m-station', '捷運站外，雨', 'station', events, guidance, env, art.get('bgm-rain', ''))


def rooftop17(art):
    P = {k: tuple(v) for k, v in layout.load('rooftop')['points'].items()}
    events = [
        hero(*P['hero_start'], art, 'lin-hs'),
        npc('xu17', *P['xu'], walker(art['walk-xu-hs']), direction='down', name='許帆'),
        npc('fang17', *P['fang'], walker(art['walk-fang-hs']), direction='down', name='方澄'),
        ev('intro17', 1, 11, trigger='auto', once=True, actions=[A('hero', value='lin17'), card('card_r17_intro'), setv('r17', 'locks')]),   # 切成十七歲的林宇（制服）
        ev('locks17', *P['locks'], name='三把鎖', marker={'label': '三把鎖', 'kind': 'quest'}, conditions=[cond('r17', 'locks')], actions=[
            say('三把鎖掛在鐵絲網上。我的、許帆的、她的。', speaker='player'),
            choice_action('輪到我了。', [
                ('說出口', [card('card_r17_try')]),
                ('不說', [addv('fade', 1)]),
            ], speaker='player'),
            card('card_r17_candy'),
            setv('r17', 'done'),
            jump('card_r17_shift'),
        ]),
    ]
    guidance = [{'text': '鐵絲網上的三把鎖', 'eventId': 'locks17', 'conditions': [cond('r17', 'locks')]}]
    env = _env(0.1, '#7fd0a8', 0.28, [('sun', 13, 1, 9, '#b8f0c8', False), ('glow', 8, 2, 4, '#ffe9b0', False)], particles='motes')
    return _map('m-rooftop-17', '十七歲的頂樓', 'rooftop', events, guidance, env, art.get('bgm-summer', ''))


def rooftop21(art):
    P = {k: tuple(v) for k, v in layout.load('rooftop')['points'].items()}
    events = [
        hero(*P['hero_start'], art, 'lin-now'),
        npc('xu21', *P['xu'], walker(art['walk-xu-now']), direction='down', name='許帆'),
        fang_now('fang21', *P['fang'], art, d='down'),
        ev('intro21', 1, 11, trigger='auto', once=True, actions=[A('hero', value='lin'), card('card_r21_intro')]),   # 切回二十一歲
        ev('locks21', *P['locks'], name='她的鎖', marker={'label': '她的鎖', 'kind': 'quest'}, conditions=[cond('rooftop_done', False)], actions=[
            say('她那把鎖的鎖孔裡，卡著乾掉的糖。', speaker='player'),
            choice_action('怎麼打開它？', [
                ('用半融的薄荷糖化開鎖孔', [card('card_r21_open'), remove('candy', '半融的薄荷糖'),
                                       item('letter', '未寄出的草木灰綠信封'), item('warmth', '冰冷的指尖餘溫'),
                                       setv('rooftop_done', True), jump('card_r21_back')]),
                ('伸手硬扳生鏽的鎖', [card('card_r21_pull')]),
                ('轉身離開', [card('card_r21_leave'), addv('fade', 1)]),
            ], speaker='player'),
        ]),
    ]
    guidance = [{'text': '她那把打不開的鎖', 'eventId': 'locks21', 'conditions': [cond('rooftop_done', False)]}]
    env = _env(0.35, '#58708a', 0.35, [('grey', 8, 3, 7, '#c8d6e0', False)], particles='motes')
    return _map('m-rooftop-21', '頂樓，雨', 'rooftop', events, guidance, env, art.get('bgm-rain', ''))


def store(art):
    P = {k: tuple(v) for k, v in layout.load('store')['points'].items()}
    events = [
        hero(*P['hero_start'], art, 'lin-now', 'left'),
        npc('fang19', *P['fang_door'], walker(art['walk-fang-now']), direction='down', name='方澄', marker={'label': '方澄', 'kind': 'quest'},
            conditions=[cond('store', 'umbrella')], actions=[
               say('她站在門邊，看著外面的雨。我手裡有一把傘。', speaker='player'),
               choice_action('要把傘給她嗎？', [
                   ('把傘給她', [card('card_st_try')]),
                   ('說沒帶', [card('card_st_hide'), addv('fade', 1)]),
               ], speaker='player'),
               card('card_st_pull'), card('card_st_shift'), setv('store', 'register'),
           ]),
        ev('intro_st', 1, 9, trigger='auto', once=True, actions=[card('card_st_intro'), setv('store', 'umbrella')]),
        ev('register', *P['register'], name='收銀機', marker={'label': '收銀機', 'kind': 'quest'},
           conditions=[cond('store', 'register'), cond('store_done', False)], actions=[
               say('收銀機上的數字一直在跳：17、19、21。', speaker='player'),
               choice_action('怎麼結這筆帳？', [
                   ('用冰冷的指尖餘溫感應，承認我欠他們一句對不起', [card('card_st_solve'), remove('warmth', '冰冷的指尖餘溫'),
                                           setv('store_done', True), jump('card_st_back')]),
                   ('隨便按結帳鍵', [card('card_st_fail')]),
                   ('推門出去', [card('card_st_door'), addv('fade', 1)]),
               ], speaker='player'),
           ]),
        ev('look_fridge', 3, 2, name='冰箱', trigger='action', marker={'label': '冰箱', 'kind': 'talk'},
           actions=[say('冰箱裡一排一排的三分糖綠茶。那個月，最後是我請的。我說我輸了，沒說輸了什麼。', speaker='player')]),
        ev('look_oden', 11, 4, name='關東煮', trigger='action', marker={'label': '關東煮', 'kind': 'talk'},
           actions=[say('關東煮的湯還在冒煙。方澄永遠只點白蘿蔔和米血，我每次都記得，卻從來沒替她點過。', speaker='player')]),
    ]
    guidance = [
        {'text': '門邊的方澄', 'eventId': 'fang19', 'conditions': [cond('store', 'umbrella')]},
        {'text': '跳著數字的收銀機', 'eventId': 'register', 'conditions': [cond('store', 'register'), cond('store_done', False)]},
    ]
    env = _env(0.15, '#dfe8f0', 0.18, [('fluor', 7, 4, 8, '#f4fbff', True), ('door', 7, 9, 3, '#8fb0d0', False)])
    return _map('m-store', '十九歲的超商', 'store', events, guidance, env, art.get('bgm-store', ''))


def all_maps(art):
    return [station(art), rooftop17(art), rooftop21(art), store(art)]
