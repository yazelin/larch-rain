"""介面音效：合成水滴聲取代晨霧玻璃的 hover/press/advance/open/close/use。python3 art/sfx_drops.py → assets/sfx/*.mp3"""
import numpy as np, subprocess, pathlib, wave
SR = 44100
OUT = pathlib.Path(__file__).resolve().parent.parent / 'assets/sfx'


def drop(f0, f1, dur, vol, decay):
    # 水滴：頻率由低往高急升（氣泡共振），音量指數衰減
    t = np.arange(int(SR * dur)) / SR
    f = f0 * (f1 / f0) ** np.clip(t / (dur * .35), 0, 1)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)
    s *= np.clip(t / .002, 0, 1)                      # 2ms 起音，免爆音
    return s * vol


def seq(*parts):  # (延遲秒, 波形)
    n = max(int(SR * d) + len(w) for d, w in parts)
    out = np.zeros(n)
    for d, w in parts:
        out[int(SR * d):int(SR * d) + len(w)] += w
    return out


SOUNDS = {
    'hover': drop(1400, 2600, .05, .12, 90),
    'press': drop(620, 1500, .11, .32, 45),
    'advance': drop(480, 1050, .13, .22, 38),
    'open': seq((0, drop(520, 1100, .1, .25, 45)), (.07, drop(760, 1600, .12, .22, 40))),
    'close': seq((0, drop(760, 1600, .1, .22, 45)), (.07, drop(480, 1000, .12, .22, 40))),
    'use': seq((0, drop(560, 1300, .3, .3, 14)), (.09, drop(1100, 2300, .2, .12, 22))),
}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name, s in SOUNDS.items():
        s = np.concatenate([s, np.zeros(int(SR * .03))])
        assert np.abs(s).max() < 1, name
        wav = OUT / f'{name}.wav'
        with wave.open(str(wav), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((s * 32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(wav), '-b:a', '96k', str(OUT / f'{name}.mp3')], check=True)
        wav.unlink()
    print('ok', sorted(p.name for p in OUT.glob('*.mp3')))
