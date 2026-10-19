// 全劇試玩：序幕 → 吧檯 → 回憶一 → 匙 → 回憶二 → 儲藏間 → 回憶三 → 臥室木盒（輸入 0217）→ 回憶四 → 床 → 調〈晚霞〉→ 遺言 → 抉擇 → 結局。
// END=cold 走〈冷卻的餘溫〉，預設〈共赴晚霞〉。node tests/play_full.mjs（先 python3 src/build.py；HEADED=1 看畫面）。截圖 art/check/full-<n>.png
import { serve, open, sleep, assert } from './lib.mjs';
fs_mk();
function fs_mk() { import('node:fs').then(fs => fs.mkdirSync('art/check', { recursive: true })); }
const COLD = process.env.END === 'b';   // END=b 走〈雨不會停〉，並且一路選逃避（測褪色）
const CHOICES = {
  '許帆替她披上外套的那一下。': COLD ? '轉開頭' : '看著',
  '輪到我了。': '說出口',
  '怎麼打開它？': COLD ? ['轉身離開', '用半融的薄荷糖化開鎖孔'] : '用半融的薄荷糖化開鎖孔',
  '要把傘給她嗎？': '把傘給她',
  '怎麼結這筆帳？': COLD ? ['推門出去', '用冰冷的指尖餘溫感應，承認我欠他們一句對不起'] : '用冰冷的指尖餘溫感應，承認我欠他們一句對不起',
  '雨越下越大。': COLD ? '緊握兩把傘退後，把秘密藏起來' : '交出信，承認平行線不必勉強交會',
};
const GUIDE = ['水窪裡映出的頂樓', '鐵絲網上的三把鎖', '她那把打不開的鎖', '水窪裡映出的超商', '門邊的方澄', '跳著數字的收銀機', '走進公車亭'];
const END_RE = COLD ? /我一直站在柱子後面/ : /也總會停/;
const MUST = [/雨總是挑在傍晚最尷尬的時候下/, /說不出口的東西，都會變成拿得起來的東西/, /誰先把心裡喜歡的人說出口/, /意識把我拉回那一刻/,
  /我始終沒勇氣寄給你們的信/, /三年了，我一次也沒有拆/, /意識不讓我改/, /需要有人放棄結帳的權利/, /對方澄，也對許帆/,
  /我喜歡的是許帆/, /我們三個，可不可以一直是三個/, COLD ? /我把她弄丟了/ : /三輛不同號碼的首班車/, COLD ? /快要看不出來/ : /綠得像剛被雨洗過/];
const used = {};
// LIVE=<Larch 預覽網址>：直接在 Larch 本站的播放器上跑（推上去之後驗收用）
const s = process.env.LIVE ? { base: process.env.LIVE, kill() {} } : await serve('dist/project.json');
const ui = await open(s.base, { width: 1600, height: 900 });
const { page } = ui;
// 預覽器的「跳到…」下拉選單有全部卡片標題，讀畫面文字時要拿掉，不然會把卡名當成任務提示
const text = async () => (await Promise.all(page.frames().map(f => f.evaluate(() => {
  const c = document.body.cloneNode(true); c.querySelectorAll('select, option, script, style').forEach(e => e.remove()); return c.textContent;
}).catch(() => '')))).join(' | ').replace(/\s+/g, ' ');
let seen = '', n = 0;
const shot = () => page.screenshot({ path: `art/check/full-${COLD ? 'b' : 'a'}-${String(n++).padStart(2, '0')}.png` });
const vis = async (t, f0) => { for (const f of f0 ? [f0] : page.frames()) if (await f.getByText(t, { exact: false }).first().isVisible().catch(() => false)) return true; return false; };
const boxOpen = async () => { for (const f of page.frames()) { const b = f.locator('.vn2-box'); if (await b.count() && await b.first().isVisible().catch(() => false)) return true; } return false; };
async function inputBox() { for (const f of page.frames()) { const i = f.locator('input[type=text], input:not([type])'); if (await i.count() && await i.first().isVisible().catch(() => false)) return i.first(); } return null; }
const guided = new Map();
// 先點按鈕：選項文字可能也出現在題目裡（「把傘給她」⊂「要把傘給她嗎？」），點到題目會原地繞圈
const clickVisible = async t => {
  for (const f of page.frames()) { const b = f.getByRole('button', { name: t }).filter({ visible: true }); if (await b.count()) { await b.first().click(); return true; } }
  for (const f of page.frames()) { const l = f.getByText(t, { exact: false }).filter({ visible: true }); if (await l.count()) { await l.last().click(); return true; } }
  return false; };
// 截圖前先 hover 要點的選項，順便留下選項選中狀態的畫面（外框壞過一次）
const hoverVisible = async t => { for (const f of page.frames()) { const b = f.getByRole('button', { name: t }).filter({ visible: true }); if (await b.count()) { await b.first().hover(); return; } } };
try {
  await ui.clickText('開始遊戲'); await sleep(1500);
  const end = Date.now() + 25 * 60000;
  while (Date.now() < end) {
   try {
    const t = await text(); seen += t;
    if (END_RE.test(seen)) break;   // 用累積讀到的文字判斷：加速時最後一句可能只在畫面上一閃
    const inp = await inputBox();
    if (inp) { await inp.fill('0217'); await page.keyboard.press('Enter'); await sleep(800); continue; }
    const q = Object.keys(CHOICES).find(k => t.includes(k));
    const pick = q && (Array.isArray(CHOICES[q]) ? CHOICES[q][Math.min(used[q] || 0, CHOICES[q].length - 1)] : CHOICES[q]);
    if (q && await vis(pick)) { await hoverVisible(pick); await sleep(400); await shot(); await clickVisible(pick); used[q] = (used[q] || 0) + 1; await sleep(700); continue; }
    if (q) { await sleep(300); continue; }
    // 翻頁前後各讀一次：Larch 本站比較慢，長句打字還沒完就翻過去會漏讀
    if (await boxOpen()) { await sleep(300); seen += await text(); await ui.advance(); await sleep(700); seen += await text(); continue; }
    let g = null; for (const x of GUIDE) if (t.includes(x) && await vis(x)) { g = x; break; }
    if (g) {
      const k = (guided.get(g) || 0) + 1; guided.set(g, k);
      if (k > 6) throw new Error('卡在任務：' + g);
      await shot(); await clickVisible(g); await sleep(5000); await page.keyboard.press('Space'); await sleep(900); continue;
    }
    await ui.advance(); await sleep(400);
   } catch (e) {
    // 換場時畫面框架會整個換掉，剛好讀到就會丟 detached；等一下再讀
    if (!/detached|Target closed|Execution context/.test(e.message)) throw e;
    await sleep(800);
   }
  }
  await shot();
  assert(END_RE.test(seen), '走到結局 ' + (COLD ? '〈雨不會停〉' : '〈各自的公車〉'));
  for (const r of MUST) assert(r.test(seen), '有出現 ' + r);
  console.log(ui.errors.length ? ui.errors : '沒有頁面錯誤');
} catch (e) { await shot(); console.error(e.message, '\n畫面：', (await text()).slice(-500)); process.exitCode = 1; }
finally { await ui.close(); s.kill(); }
