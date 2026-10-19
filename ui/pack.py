"""把 ui/rain-night/ 七個部位包成一個「雨夜玻璃」Skills 檔（每段第一行是部位標記），給 Larch 編輯器「匯入 HTML／貼上」用。
gallery 部位 agent 工具寫不進去，靠這個檔一次貼齊。python3 ui/pack.py → ui/雨夜玻璃.html"""
import pathlib
HERE = pathlib.Path(__file__).parent
ORDER = ('title', 'dialogue', 'choices', 'menu', 'inventory', 'gallery', 'rpg')
parts = []
for k in ORDER:
    f = next((HERE / 'rain-night').glob(f'{k}.*'))
    mark = f'<!-- larch-skill-part: {k} -->' if f.suffix == '.html' else f'/* larch-skill-part: {k} */'
    parts.append(mark + '\n' + f.read_text(encoding='utf-8').strip() + '\n')
out = HERE / '雨夜玻璃.html'
out.write_text('\n'.join(parts), encoding='utf-8')
assert all(f'larch-skill-part: {k}' in out.read_text() for k in ORDER)
print(out, out.stat().st_size)
