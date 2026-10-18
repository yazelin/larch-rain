# 《淡藍與草木灰綠的雨幕》Larch RPG 版

> 「雨總是挑在傍晚最尷尬的時候下，把捷運站外頭的柏油路洗得發亮，像一層透著冷光的薄冰。」

最後一晚，林宇、許帆、方澄說好在捷運站外的公車亭等天亮的首班車。林宇一整晚站在柱子後面，手裡握著兩把傘、口袋裡一顆半融的薄荷糖，意識困在那個下雨的傍晚。在他的意識裡，說不出口的東西會變成拿得起來的東西：他走進水窪裡映出的十七歲頂樓、十九歲的超商，想改變回憶卻被拉回真正發生過的那一下，最後帶著那封藏了三年的信走進公車亭。

設計文件：`design/重寫.md`（2026-10-18 定稿，含意識的五條規則、三人的心境、時間線、地圖與 CG 的理由）。

---

## 遊戲架構

- **平台**：[Larch Story Studio](https://larch.ink)，`larch-rpg-system` 地圖行走與事件。
- **地圖**（`src/maps.py`，分層設計在 `art/objects_*.yaml`）：
  1. `m-station` 捷運站外，雨：柱子、公車亭、兩個映著回憶的水窪；兩段回憶走完前，公車亭前那條線過不去。
  2. `m-rooftop-17` 十七歲的頂樓（重播）→ `m-rooftop-21` 意識裡二十一歲的頂樓：三把鎖、打賭、她那把打不開的鎖。
  3. `m-store` 十九歲的超商：門邊的方澄、跳著 17／19／21 的收銀機。
- **褪色**：每逃避一次 `fade` 加一，方澄的外套跟著變淡（`art/fade_jacket.py`），公車亭的開場分三種。
- **兩個結局**：〈各自的公車〉、〈雨不會停〉。
- **素材**：三人定錨立繪與行走圖（`art/gen_anchors.py`、`art/gen_walkers.py`，.11 codex-image）、七張 CG（`art/gen_cinematic_cg.py`）、六首配樂（`art/music.py`，gemini-web）、全劇配音（`src/tts_script.py`，larch-tts-bridge；林宇 Gentle_Youth、許帆 Unrestrained_Young_Man、方澄 Soft_Girl）。台詞全在 `src/script.py`。

---

## 開發與建置

```bash
python3 src/build.py                     # 組出 dist/project.json
python3 src/tts_script.py                # 補缺的配音（FORCE=1 全部強制重配；破音字替身在 SUBS）
node tests/play_full.mjs                 # 全劇自動試玩〈各自的公車〉；END=b 走〈雨不會停〉並一路逃避
python3 ~/larch-preview/serve.py dist/project.json --port 8799   # 本機預覽
```

推上 Larch（只更新專案，不上架），步驟照 [larch-sunset](https://github.com/yazelin/larch-sunset) 的 README：素材改了就 commit、推 main、打 tag，把 `src/push.py` 的 `CDN_TAG` 換成那個 tag 的 commit 編號；`DRY=1 python3 src/push.py x` 乾跑；最後一個改動之後重跑兩個結局；`python3 src/push.py "說明"`；讀回核對卡片數，再用 `LIVE=<Larch 預覽網址> node tests/play_full.mjs` 在 Larch 本站跑兩個結局。

---

## 授權與社群

- 程式碼：MIT © 林亞澤（`LICENSE`）；故事、美術、配樂與配音：CC BY-NC 4.0（`LICENSE-CONTENT.md`）
- [GitHub @yazelin](https://github.com/yazelin) · [Facebook](https://facebook.com/yazelin) · [Buy Me a Coffee](https://buymeacoffee.com/yazelin)

## 介面（雨夜玻璃）

以 Larch 官方「晨霧玻璃」為底，`ui/night.py` 把 `ui/mist-original/` 轉成深色玻璃＋草木灰綠，輸出到 `ui/rain-night/`，並藏掉這部用不到的 HP、攻防魔、未同行夥伴格與內部變數。

整包推送（`src/push.py`）不會更新介面，要另外跑 `python3 src/push_ui.py` 寫入六個部位並讀回比對。收藏頁（gallery）工具不收，要在編輯器手動換。介面截圖：`node tests/ui_shots.mjs`（`LIVE=<預覽網址>` 截線上版）。
