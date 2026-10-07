#!/usr/bin/env python3
"""Kinetic word-by-word captions (ASS karaoke) for Downthegroup Ep1 v2.
Word timing is proportional to character count within each beat's known duration.
Key numbers/names get a permanent saffron override; all words get a saffron
karaoke sweep as they're 'sung'. Also emits timeline.json for the assembler.
"""
import json, os, re

BASE = os.path.expanduser("~/workspace/youtube-video")
TXT_DIR = os.path.join(BASE, "narration", "hinglish")
DONE_DIR = os.path.join(BASE, "narration", "done")

BEATS = [
    ("beat_01_hook.txt",    "beat_01.mp3", 16.248),
    ("beat_02_turn.txt",    "beat_02.mp3", 12.768),
    ("beat_03_numbers.txt", "beat_03.mp3", 48.792),
    ("beat_04_discount.txt","beat_04.mp3", 32.232),
    ("beat_05_loophole.txt","beat_05.mp3", 43.032),
    ("beat_06_pressure.txt","beat_06.mp3", 53.088),
    ("beat_07_why.txt",     "beat_07.mp3", 41.040),
    ("beat_08_payoff.txt",  "beat_08.mp3", 24.888),
    ("beat_09_close.txt",   "beat_09.mp3", 15.960),
]

LEAD_IN = 2.5
GAP = 1.2
OUTRO = 3.0

KEY_RE = re.compile(r"\d")  # any word containing a digit
KEY_WORDS = {"discount", "tariff", "sanctions", "survival", "saza", "maafi",
             "dabav", "loophole", "bharat", "russia", "america", "china"}

def esc(t):
    return t.replace("{", r"\{").replace("}", r"\}")

def ass_time(s):
    s = max(0, s)
    h = int(s // 3600); m = int((s % 3600) // 60)
    sec = int(s % 60); cs = int(round((s - int(s)) * 100))
    return f"{h}:{m:02d}:{sec:02d}.{cs:02d}"

def split_phrases(text):
    """Split into caption phrases: sentences, then comma-chunks, capped length."""
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.?!:])\s+", text)
    phrases = []
    for sent in sentences:
        chunks = re.split(r"(?<=,)\s+", sent)
        cur = ""
        for ch in chunks:
            if cur and len(cur) + 1 + len(ch) > 52:
                phrases.append(cur.strip())
                cur = ch
            else:
                cur = (cur + " " + ch).strip()
        if cur.strip():
            phrases.append(cur.strip())
    # merge tiny trailing phrases
    merged = []
    for p in phrases:
        if merged and len(merged[-1].split()) <= 2 and len(p.split()) + len(merged[-1].split()) <= 10:
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return [p for p in merged if p]

def wrap_lines(phrase, width=34):
    words = phrase.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines[:2]  # never more than 2 lines

def build():
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,58,&H00FFFFFF,&H003399FF,&H80000000,&H80000000,-1,0,0,0,100,100,0.5,0,1,2.5,0,2,60,60,84,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    timeline = {"lead_in": LEAD_IN, "gap": GAP, "outro": OUTRO, "beats": []}
    t = LEAD_IN
    for txt_name, mp3, dur in BEATS:
        with open(os.path.join(TXT_DIR, txt_name), encoding="utf-8") as f:
            text = f.read()
        phrases = split_phrases(text)
        words_all = text.split()
        total_chars = sum(len(w) for w in words_all) or 1
        # word durations proportional to length, floor 0.10s, then normalize to dur
        raw = [max(0.10, dur * len(w) / total_chars) for w in words_all]
        scale = dur / sum(raw)
        wdurs = [r * scale for r in raw]

        # map words to phrases
        wi = 0
        cur_t = t
        for ph in phrases:
            pwords = ph.split()
            n = len(pwords)
            ph_dur = sum(wdurs[wi:wi + n])
            # build karaoke text with line wraps
            lines = wrap_lines(ph)
            # assign words to lines for karaoke order (reading order = line order)
            kara = []
            k = 0
            for li, line in enumerate(lines):
                lw = line.split()
                parts = []
                for w in lw:
                    d = max(10, int(round(wdurs[wi + k] * 100)))
                    clean = esc(w)
                    if KEY_RE.search(w) or w.strip(".,:;?!\"'").lower() in KEY_WORDS:
                        clean = r"{\c&H003399FF&\b1}" + clean + r"{\c&H00FFFFFF&\b0}"
                    parts.append(r"{\kf%d}%s" % (d, clean))
                    k += 1
                kara.append(" ".join(parts))
                if li < len(lines) - 1:
                    kara.append(r"\N")
            start, end = cur_t, cur_t + ph_dur
            # small gap between phrases so karaoke resets readably
            events.append(
                f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,"
                f"{{\\fad(120,120)}}{''.join(kara)}"
            )
            cur_t = end
            wi += n
        timeline["beats"].append({"file": mp3, "start": round(t, 3), "dur": dur})
        t += dur + GAP

    total = t - GAP + OUTRO
    timeline["total"] = round(total, 3)
    with open(os.path.join(BASE, "captions.ass"), "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")
    with open(os.path.join(BASE, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    print(f"captions: {len(events)} events, total runtime {total:.2f}s")
    print(json.dumps(timeline["beats"], indent=1))

if __name__ == "__main__":
    build()
