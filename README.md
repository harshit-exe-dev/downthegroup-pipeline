# Downthegroup Video Pipeline

The full build pipeline behind Downthegroup explainer videos — everything from research to the final MP4, as code. Built for Episode 1 (*Bharat ka $40 Billion Russian Oil Daav*), reusable for any topic.

## What this pipeline does

```
research → script → voiceover → b-roll → charts → captions → assembly → QA → thumbnail
```

## Skills & tools used to make Episode 1

| Stage | What was used |
|---|---|
| Research | Web research across news outlets and reports (Economic Times, Reuters, CREA, Kpler data) + a second fact-check pass that caught a wrong date before release |
| Script | Hinglish script with a hook-first structure: Hook (0:00–0:15) → promise → 4–6 beats, each with one retention moment (a flip, reveal, or escalation) → payoff. See `script_hinglish.md` |
| Voiceover | AI text-to-speech narration, generated per beat as separate MP3s, then timed on a master timeline (`timeline.json`) |
| B-roll | Real stock footage (free libraries). Hard rule learned in QA: **never repeat the same clip more than twice** |
| Charts | Python + matplotlib (`build_assets.py`) — animated bar/pie charts from sourced numbers only, nothing invented |
| Captions | Word-by-word kinetic captions (`build_captions.py` → `captions.ass`) |
| Assembly | Python + ffmpeg (`assemble_v2.py`) — narration on timeline, B-roll cut to beats, chart overlays, burned captions, music bed + SFX mix, loudness normalized for YouTube |
| QA pass | Frame-level check for repeated footage, audio dropout and A/V sync check. Fixes applied as a surgical re-edit (`assemble_v3.py`) with identical timings so audio stays in sync |
| Thumbnail | AI-generated documentary-style thumbnail, one bold readable line |

## Repo layout

```
build_assets.py      # generates charts/cards into assets/
build_captions.py    # builds captions.ass from the script
remix_audio.py       # mixes narration + music bed + SFX, normalizes loudness
assemble_v2.py       # full assembly driven by timeline.json
assemble_v3.py       # QA fix pass: re-cut repeated B-roll, same timings (audio untouched)
timeline.json        # master timeline: per-beat audio files, start times, durations, gaps
script_hinglish.md   # the full Episode 1 script — use as a structural template
```

Expected input folders (you provide these per episode):

```
broll/       # stock footage clips (.mp4)
anim/        # animated overlays / cards (.mp4)
audio/       # narration mix, music_bed.mp3, sfx_*.mp3
narration/   # per-beat voiceover MP3s (beat_01.mp3, beat_02.mp3, ...)
```

## Requirements

- Python 3
- `ffmpeg` on PATH
- `pip install matplotlib numpy`

## Making a video on a new topic

1. **Research (1–2 hrs).** Pick the topic, gather 4–6 solid sources. Note every figure with its source. Verify dates — this is what separates good explainers from slop.
2. **Script (2–3 hrs).** Write spoken Hinglish, ~130–150 words per minute of video. Follow the `script_hinglish.md` structure: winning hook first, then beats with `[ON SCREEN]` direction notes written inline as you go.
3. **Voiceover.** Record yourself (a phone mic in a quiet room works) or use a free TTS tool. Export one MP3 per beat, measure each duration, and fill in `timeline.json`.
4. **Visuals.** Download 2–3x more B-roll than you need (Pexels / Pixabay / Coverr, all free). Generate charts with `build_assets.py` using only your sourced numbers.
5. **Build.** Run in order: `build_assets.py` → `build_captions.py` → `remix_audio.py` → `assemble_v2.py`.
6. **QA.** Watch the whole thing once: any clip repeating more than twice? Audio dropouts? Captions in sync? Any claim you're unsure about? Fix with a targeted re-edit like `assemble_v3.py` — keep timings identical so audio stays in sync.
7. **Thumbnail + title.** 1280×720, one big readable line (3–5 words), high contrast. Title under ~60 characters with a curiosity gap.
8. **Mobile version.** Re-encode at 720p for easy sharing:
   ```
   ffmpeg -i final.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 -c:a aac mobile.mp4
   ```

## Notes

- Scripts use `~/workspace/youtube-video` as the base path — change `BASE` at the top of each script to your own folder.
- `timeline.json` fields: `lead_in` (silence before beat 1), `gap` (pause between beats), `outro` (tail), and per-beat `file` / `start` / `dur`.
- Loudness target for YouTube: −14 LUFS (handled in `remix_audio.py`).
- The Episode 1 narration audio and stock footage are not in this repo (size + licensing) — the code is the reusable part.
