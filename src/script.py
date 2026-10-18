"""劇本台詞（design/重寫.md，2026-10-18 定稿）。整個遊戲在林宇的意識裡：
現在（二十一歲，捷運站外的雨）用林宇第一人稱；回憶（頂樓十七歲、超商十九歲）也用林宇第一人稱，
旁白只寫看得到的動作。配音檔名＝台詞 id；講者空字串＝旁白，不配音。
"""
import hashlib
import cards

LIN, XU, FANG = '林宇', '許帆', '方澄'
VOICE = {LIN: ('Chinese (Mandarin)_Gentle_Youth', 'calm'),
         XU: ('Chinese (Mandarin)_Unrestrained_Young_Man', 'calm'),
         FANG: ('Chinese (Mandarin)_Soft_Girl', 'calm')}

# 卡片 id → [(講者, 文字, 配音 id 或 None, 情緒)]
L = {
    # ── 序 ──
    'prologue': [
        ('', '最後一晚。三個人說好，在捷運站外的公車亭等天亮的首班車。', None, ''),
        ('', '傍晚開始下雨。', None, ''),
        (LIN, '雨總是挑在傍晚最尷尬的時候下，把捷運站外頭的柏油路洗得發亮，像一層透著冷光的薄冰。', 'p_lin_1', 'calm'),
        (LIN, '我站在柱子後面，手裡攥著兩把傘。一把是便利商店的透明傘，一把是傘骨有點歪的深藍色。', 'p_lin_2', 'calm'),
        (LIN, '深藍色那把，是要給她的。三年了，一直沒給出去。', 'p_lin_3', 'sad'),
        (LIN, '背包裡壓著一封信，信封上寫著我和許帆的名字。高中畢業那天在頂樓撿到的，我藏了三年，從沒拆開。', 'p_lin_4', 'sad'),
    ],
    # 地圖一進場：許帆替方澄披外套（被迫看著）
    'card_jacket': [
        (FANG, '我查好了，三條線的首班車都是五點二十分。', 'j_fang_bus', 'calm'),
        (XU, '明天起，就各奔東西了。', 'j_xu_tomorrow', 'sad'),
        (XU, '方澄，把外套穿上吧。初秋的雨淋久了會著涼。', 'j_xu_1', 'calm'),
        ('', '許帆把他那件草木灰綠的外套，披在方澄肩上。', None, ''),
        (FANG, '謝謝……其實還好，只是風有點涼。', 'j_fang_1', 'calm'),
        ('', '她沒有拒絕，微微側過頭，低聲笑了一下。', None, ''),
        (LIN, '那個笑很輕，像風掠過湖面。胸口卻泛起一陣青梅未熟時的微酸。', 'j_lin_1', 'sad'),
    ],
    'card_look': [(LIN, '我一直看著。看到她把外套的領子拉緊。', 'j_lin_look', 'sad')],
    'card_away': [(LIN, '我把臉轉向馬路。轉開，也是一種回答。', 'j_lin_away', 'sad')],
    # 規則：說不出口的東西會變成拿得起來的東西
    'card_rule': [
        (LIN, '口袋裡那顆薄荷糖，放到半融了。她只吃薄荷糖，我每天都在口袋放一顆，一顆也沒送出去。', 'r_lin_1', 'calm'),
        ('', '指尖碰到它的時候，糖紙底下透出一點淡淡的光。', None, ''),
        (LIN, '……我知道這是哪裡了。', 'r_lin_2', 'surprised'),
        (LIN, '這不是那天晚上。這是我腦子裡的那天晚上。', 'r_lin_3', 'calm'),
        (LIN, '在這裡，說不出口的東西，都會變成拿得起來的東西。', 'r_lin_4', 'calm'),
    ],
    # ── 頂樓：十七歲的夏天（重播） ──
    'card_r17_enter': [
        (LIN, '水窪裡映出的不是街燈。', 'r17_lin_puddle1', 'calm'),
        (LIN, '是生鏽的鐵絲網，和一片青綠色的夕陽。', 'r17_lin_puddle2', 'calm'),
    ],
    'card_r17_intro': [
        ('', '十七歲的夏天。舊教學大樓的頂樓，水塔和藍色鐵皮加蓋被夕陽曬得發燙，鐵絲網旁貼著褪色的「禁止攀爬」。', None, ''),
        (FANG, '林宇，你很慢耶。', 'r17_fang_slow', 'happy'),
        (XU, '他在樓梯口跟數學老師裝熟啦。', 'r17_xu_tease', 'happy'),
        (FANG, '好，人到齊了。我們來打賭。', 'r17_fang_bet1', 'happy'),
        (FANG, '一人掛一把鎖。誰先把心裡喜歡的人說出口，就開自己那把。', 'r17_fang_bet2', 'happy'),
        (XU, '輸的請一整個月的三分糖綠茶。', 'r17_xu_tea', 'happy'),
        (FANG, '說好了喔。不准耍賴。', 'r17_fang_deal', 'happy'),
        ('', '三把鎖扣上鐵絲網，鎖身上刻著L、X、F。', None, ''),
    ],
    'card_r17_try': [
        (LIN, '我張開嘴。', 'r17_lin_try1', 'calm'),
        ('', '可是十七歲的我，什麼都沒有說。', None, ''),
        ('', '意識把我拉回那一刻。', None, ''),
    ],
    'card_r17_candy': [
        (LIN, '我知道她要說的是誰。', 'r17_lin_know', 'sad'),
        ('', '我趁她轉頭，把手心裡那顆本來要送她的薄荷糖，塞進了她那把鎖的鎖孔。', None, ''),
        (FANG, '欸！林宇你幹嘛啦！', 'r17_fang_hey', 'surprised'),
        (LIN, '惡作劇啦。', 'r17_lin_prank', 'happy'),
        ('', '她笑著打我的手臂。許帆看了我一眼，什麼也沒說。', None, ''),
        (LIN, '她那把鎖，從那天起就再也沒人打開過。我就不用聽到她說出口的那個名字。', 'r17_lin_never', 'sad'),
    ],
    'card_r17_shift': [
        ('', '夕陽像被雨水沖掉一樣，一點一點褪成鉛灰色。', None, ''),
        ('', '雨落下來。這是二十一歲的頂樓。', None, ''),
    ],
    # ── 頂樓：二十一歲，意識裡的雨 ──
    'card_r21_intro': [
        (FANG, '林宇……你還記得嗎？', 'r21_fang_1', 'calm'),
        (FANG, '高中那年夏天，我們在這裡打賭，誰先開口坦白，誰就得請喝一整個月的三分糖綠茶。', 'r21_fang_2', 'calm'),
        (XU, '結果方澄那把鎖，從那天起就再也沒人打開過。', 'r21_xu_1', 'calm'),
        (LIN, '鎖孔裡卡著融化的糖漬。那是我塞進去的。', 'r21_lin_1', 'sad'),
    ],
    'card_r21_pull': [(LIN, '鐵絲網冰得刺骨，生鏽的鎖紋絲不動，反而劃破了指尖。我藏起來的東西，只能用我藏的東西打開。', 'r21_lin_pull', 'sad')],
    'card_r21_leave': [(LIN, '我轉身走向樓梯門。門推不開。意識不讓我走。', 'r21_lin_leave', 'sad')],
    'card_r21_open': [
        (LIN, '我掏出口袋裡那顆半融的薄荷糖，按進冰冷的鎖孔。', 'r21_lin_candy', 'calm'),
        ('', '鎖孔裡的舊糖漬跟著亮起淡藍色的光，一點一點從鎖縫退開。喀噠一聲，鎖扣彈開。', None, ''),
        ('', '背包突然一沉。我伸手進去，那封信就在手裡，草木灰綠的信封，麻繩還繫著。', None, ''),
        (FANG, '那是……我們畢業那天，我始終沒勇氣寄給你們的信。', 'r21_fang_letter', 'surprised'),
        (LIN, '畢業那天，是我在這裡撿到的。三年了，我一次也沒有拆。', 'r21_lin_kept', 'sad'),
        ('', '許帆走上前，再一次把外套輕輕披在方澄肩上。', None, ''),
        (LIN, '我下意識伸出手想替她擋風。指尖只碰到空氣裡的一點涼。', 'r21_lin_wind', 'sad'),
    ],
    'card_r21_back': [(LIN, '那一點涼沒有散。它留在我的指尖，有了重量。', 'r21_lin_back', 'calm')],
    # ── 超商：十九歲的雨夜（重播） ──
    'card_st_enter': [
        (LIN, '這次水窪裡亮著一片慘白的光。', 'st_lin_puddle1', 'calm'),
        (LIN, '是大學旁邊那間超商。', 'st_lin_puddle2', 'calm'),
    ],
    'card_st_intro': [
        ('', '十九歲。大學旁邊那間二十四小時超商。', None, ''),
        (LIN, '十九歲那年，許帆和方澄開始交往。許帆知道我喜歡她，所以在我面前，從來不牽她的手。', 'st_lin_dating', 'sad'),
        ('', '那天也下雨。我們三個擠在這裡躲雨，一人一碗關東煮。', None, ''),
        (FANG, '貢丸給你，蘿蔔分我一半。', 'st_fang_oden', 'happy'),
        (XU, '妳每次都記得。', 'st_xu_oden', 'happy'),
        (LIN, '他們很自然地交換筷子。我低頭看著湯，手裡捏緊傘柄。', 'st_lin_oden', 'sad'),
        (XU, '我先衝回宿舍拿傘，你們等我。', 'st_xu_go', 'happy'),
        ('', '許帆把外套脫下來，丟到方澄頭上，衝進雨裡。店裡只剩下我和方澄。', None, ''),
        (FANG, '林宇，你有帶傘嗎？', 'st_fang_umbrella', 'calm'),
    ],
    'card_st_try': [
        (LIN, '我把傘遞出去。', 'st_lin_try', 'calm'),
        ('', '可是十九歲的我，在她伸手的前一秒，抽回了傘柄。', None, ''),
        ('', '意識不讓我改。', None, ''),
    ],
    'card_st_pull': [
        (LIN, '……我也只有一把。', 'st_lin_one', 'calm'),
        (FANG, '沒關係，我等許帆。', 'st_fang_wait', 'calm'),
        ('', '她輕輕嘆了一口氣。我假裝沒有聽見。', None, ''),
        (LIN, '那天我抱著傘走回宿舍。傘一次也沒有撐開。', 'st_lin_walk', 'sad'),
    ],
    'card_st_shift': [
        ('', '日光燈閃了一下。貨架上的東西一排一排消失。', None, ''),
        ('', '收銀機的螢幕上，跳動著三組發綠的數字：17、19、21。', None, ''),
        (LIN, '十七歲相遇，十九歲同窗，二十一歲各奔前程。', 'st_lin_years', 'calm'),
        ('', '收銀機吐出一張便條：『需要有人放棄結帳的權利。』', None, ''),
    ],
    'card_st_hide': [
        (LIN, '我想把傘藏到身後，說我沒帶。', 'st_lin_hide', 'calm'),
        ('', '意識把我拉回抽回傘柄的那一刻。', None, ''),
    ],
    'card_st_fail': [(LIN, '收銀機嗶嗶亂叫，螢幕跳出『交易失敗：代價不足』。這不是錢能結清的帳。', 'st_lin_fail', 'surprised')],
    'card_st_door': [(LIN, '我推開門。門外不是雨，是同一間超商。', 'st_lin_door', 'sad')],
    'card_st_solve': [
        (LIN, '我把帶著那一點涼的手，覆在收銀機的掃描窗上。', 'st_lin_scan', 'calm'),
        ('', '掃描窗亮起淡藍色的光。', None, ''),
        (LIN, '假裝沒聽見她的嘆息。在雨裡默默抽回的傘柄。在許帆面前，故意裝作什麼都不知道。', 'st_lin_list', 'sad'),
        (LIN, '結帳，是算清楚誰欠誰、誰該得到誰。我不再追問誰欠我什麼。這句對不起，由我先交出去。', 'st_lin_bill', 'sad'),
        ('', '收銀台上方，凝出一隻冰藍色的紙鶴，落在我掌心。', None, ''),
        (LIN, '對不起。對方澄，也對許帆。', 'st_lin_sorry', 'sad'),
        ('', '我把紙鶴投進收銀機的紙鈔口。叮的一聲，青綠色的光一圈一圈散開，整間超商像泡沫一樣消融了。', None, ''),
    ],
    'card_st_back': [(LIN, '腳下又是濕冷的柏油路。雨聲重新湧進耳朵。', 'st_lin_back', 'calm')],
    # ── 公車亭：最後 ──
    'card_climax_lo': [

        (LIN, '我撐開那把透明傘，一步一步踏過水窪，走進公車亭。', 'c_lin_1', 'calm'),
        (XU, '林宇？你剛才去哪裡了？怎麼兩手都濕透了……', 'c_xu_1', 'surprised'),
        (FANG, '林宇……你手裡拿著的是……？', 'c_fang_1', 'calm'),
        ('', '棚頂漏著水。答、答、答，像倒數的心跳。', None, ''),
        ('', '方澄肩上的外套，綠得像剛被雨洗過。', None, ''),
    ],
    'card_climax_mid': [

        (LIN, '我撐開那把透明傘，一步一步踏過水窪，走進公車亭。', 'c_lin_1', 'calm'),
        (XU, '林宇？你剛才去哪裡了？怎麼兩手都濕透了……', 'c_xu_1', 'surprised'),
        (FANG, '林宇……你手裡拿著的是……？', 'c_fang_1', 'calm'),
        ('', '棚頂漏著水。答、答、答，像倒數的心跳。', None, ''),
        ('', '方澄肩上的外套，綠色淡了一層，像被雨水慢慢洗走。', None, ''),
    ],
    'card_climax_hi': [

        (LIN, '我撐開那把透明傘，一步一步踏過水窪，走進公車亭。', 'c_lin_1', 'calm'),
        (XU, '林宇？你剛才去哪裡了？怎麼兩手都濕透了……', 'c_xu_1', 'surprised'),
        (FANG, '林宇……你手裡拿著的是……？', 'c_fang_1', 'calm'),
        ('', '棚頂漏著水。答、答、答，像倒數的心跳。', None, ''),
        ('', '方澄肩上的外套，綠已經淡得快要看不出來了。', None, ''),
    ],
    'card_letter': [
        (LIN, '我拆開了那封信。三年來第一次。', 'l_lin_open', 'calm'),
        (FANG, '給林宇、許帆。', 'l_fang_1', 'calm'),
        (FANG, '我知道林宇喜歡我。我也知道許帆知道。', 'l_fang_2', 'calm'),
        (FANG, '我喜歡的是許帆。可是我不想讓任何一個人，變成站在外面的那一個。', 'l_fang_3', 'sad'),
        (FANG, '那時候，我一直在等你們其中一個先開口。如果你們都不說，那就讓我當那個膽小鬼吧。', 'l_fang_4', 'sad'),
        (FANG, '我們三個，可不可以一直是三個？', 'l_fang_5', 'sad'),
        ('', '信紙最下面，有一塊被水暈開的痕跡。不是今晚的雨。', None, ''),
    ],
    # ── 結局〈各自的公車〉 ──
    'ending_a1': [
        ('', '我走上前，把那封被雨水微潤的信，遞給許帆，也遞給方澄。', None, ''),
        ('', '許帆接過信的手指有點發抖。方澄低下頭，眼角泛起一點柔軟的光。', None, ''),
        ('', '我把手裡那把多出來的深藍色傘收攏。', None, ''),
        (LIN, '我們三個人的平行線，其實不用勉強交會成三角形。', 'ea_lin_lines', 'calm'),
        (XU, '林宇……我一直知道。對不起，一直沒說。', 'ea_xu_sorry', 'sad'),
        (LIN, '我知道你們在一起，也知道你們一直顧著我的感受。沒關係。這封信我藏了三年，對不起。', 'ea_lin_sorry', 'calm'),
        (XU, '原來我們一直在等彼此先開口。', 'ea_xu_wait', 'calm'),
        (FANG, '謝謝你，林宇。能遇見你們，是我青春裡最幸運的事。', 'ea_fang_thanks', 'happy'),
    ],
    'ending_a2': [
        ('', '不知道什麼時候，雨停了。', None, ''),
        ('', '天亮了。鉛灰色的雲被晨風吹開，淡藍的天空透出一點金光。', None, ''),
        ('', '三輛不同號碼的首班車，同時進站。', None, ''),
        (FANG, '到了記得傳訊息。', 'ea_fang_msg', 'happy'),
        (XU, '妳也是。林宇也要。', 'ea_xu_msg', 'happy'),
        (LIN, '好。', 'ea_lin_ok', 'calm'),
        (LIN, '我們相視一笑，各自上了車。', 'ea_lin_bus', 'calm'),
        (LIN, '雨總是挑在最尷尬的時候下。', 'ea_lin_close1', 'calm'),
        (LIN, '也總會停。', 'ea_lin_close2', 'calm'),
    ],
    # ── 結局〈雨不會停〉 ──
    'ending_b1': [
        ('', '我把信死死攥在背後，一步一步往後退，退進雨裡。', None, ''),
        (LIN, '只要不拆穿、只要不開口，我們就永遠是最好的朋友，對不對？', 'eb_lin_back', 'sad'),
        (XU, '林宇！別退了！方澄她……方澄她快撐不住了！', 'eb_xu_stop', 'fearful'),
        ('', '方澄肩上那件外套，最後一點綠也褪掉了，一片一片剝落。', None, ''),
        (FANG, '好冷……林宇……為什麼我們連一句真話都說不出口……', 'eb_fang_cold', 'sad'),
        ('', '她化成一點一點青綠色的螢火，散進雨裡。', None, ''),
        (XU, '方澄！', 'eb_xu_cry', 'fearful'),
    ],
    'ending_b2': [
        ('', '許帆跪在水窪裡。我手裡的兩把傘掉在地上，口袋裡的糖紙被雨泡爛了。', None, ''),
        (LIN, '那是我心裡的她。我把她弄丟了。', 'eb_lin_lost', 'sad'),
        ('', '雨不會停了。天沒有亮。', None, ''),
        (LIN, '我一直站在柱子後面。', 'eb_lin_pillar', 'sad'),
    ],
}


def voice_lines():
    """[(檔名, 文字, 聲線, 情緒)]"""
    return [(f'{vid}.mp3', tx, VOICE[sp][0], emo or VOICE[sp][1])
            for ls in list(L.values()) + list(MAP_LINES.values()) for sp, tx, vid, emo in ls if vid]


SHOW_SCALE, SHOW_Y = 1.75, -70


def _actors(cid, art, era):
    names = [n for n in (LIN, XU, FANG) if any(sp == n for sp, *_ in L[cid])]
    key = {LIN: 'lin', XU: 'xu', FANG: 'fang'}
    slot = {LIN: 'left', XU: 'right', FANG: 'right' if XU not in names else 'center'}
    # 立繪是全身的，原尺寸放在對話畫面太小、看不到臉；放大成半身（大腿以上），往下推讓腳出框（2026-10-18 作者：看不出立繪）
    return [cards.actor(n, art[f'p-{key[n]}-{era}'], slot[n], offsetY=SHOW_Y, scale=SHOW_SCALE) for n in names]


def card(cid, title, art, bg='', era='now', **kw):
    lines = [(sp, tx, f'/files/assets/voice/{vid}.mp3' if vid else None) for sp, tx, vid, _ in L[cid]]
    return cards.dialogue(cid, title, lines, bg=bg, actors=[] if bg else _actors(cid, art, era), **kw)


# 地圖上林宇的第一人稱內心話（地圖對話框掛不了音檔）：建置時轉成一句一張的配音卡（沿用晚霞 memory.voice_map_lines）
MAP_LINES = {}


def voice_map_lines(board):
    import json as _j
    have = {n['id'] for n in board['nodes']}
    added = []

    def walk(o):
        if isinstance(o, str) and o[:1] in '{[':
            try:
                d = _j.loads(o)
            except ValueError:
                return o
            return _j.dumps(walk(d), ensure_ascii=False)
        if isinstance(o, dict):
            if o.get('kind') == 'dialogue' and not o.get('cardId') and '我' in (o.get('text') or ''):
                t = o['text']; vid = 'mv_' + hashlib.md5(t.encode()).hexdigest()[:8]
                MAP_LINES['card_' + vid] = [(LIN, t, vid, 'calm')]
                if 'card_' + vid not in have:
                    have.add('card_' + vid); added.append(cards.dialogue('card_' + vid, LIN, [(LIN, t, f'/files/assets/voice/{vid}.mp3')]))
                o['text'] = ''   # text 要留空字串：引擎讀地圖時每個動作都會處理 text（晚霞 2026-10-17 踩過）
                o.pop('speaker', None)
                o['cardId'] = 'card_' + vid
            for k in list(o): o[k] = walk(o[k])
        elif isinstance(o, list):
            for i in range(len(o)): o[i] = walk(o[i])
        return o
    for n in board['nodes']:
        if n['id'].startswith('m-'):
            walk(n['data'])
    board['nodes'].extend(added)
    return len(added)
