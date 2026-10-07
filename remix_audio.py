#!/usr/bin/env python3
"""Remix v2 audio: voice was dropped from the final amix in assemble_v2.py.
Rebuilds: voice (9 beats at timeline starts) + ducked music bed + SFX, then
remuxes with the existing video stream (no video re-encode)."""
import json, subprocess, sys

BASE = "/home/hatch/workspace/youtube-video"
tl = json.load(open(f"{BASE}/timeline.json"))
TOTAL = tl["total"] + 0.5
beats = tl["beats"]

inputs = []
# 0..8: narration beats
for b in beats:
    inputs += ["-i", f"{BASE}/narration/done/{b['file']}"]
inputs += ["-i", f"{BASE}/audio/music_bed.mp3"]          # idx 9
inputs += ["-i", f"{BASE}/audio/sfx_riser.mp3"]          # idx 10
inputs += ["-i", f"{BASE}/audio/sfx_whoosh.mp3"]         # idx 11
inputs += ["-i", f"{BASE}/audio/sfx_hit.mp3"]            # idx 12

F = []
# voice: delay each beat to its start, then mix
for i, b in enumerate(beats):
    ms = int(b["start"] * 1000)
    F.append(f"[{i}:a]adelay={ms}|{ms},aresample=44100[v{i}]")
F.append("".join(f"[v{i}]" for i in range(len(beats))) +
         f"amix=inputs={len(beats)}:normalize=0,aresample=44100[voice]")
# music: loop to TOTAL, low bed
F.append(f"[9:a]aloop=loop=-1:size=2e9,atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,"
         f"volume=0.10,aresample=44100,afade=t=in:st=0:d=2[mus]")
# duck music under voice (music compressed, voice is the key).
# NOTE: [voice] is used twice -> must asplit first (a pad can only be consumed once)
F.append("[voice]asplit=2[voice_key][voice_main]")
F.append("[mus][voice_key]sidechaincompress=threshold=0.02:ratio=8:attack=200:release=800[dck]")
# sfx plan (same as assemble_v2.py)
t0 = {b["file"]: b["start"] for b in beats}
SFX = [
    (10, 0.2, 0.35),                       # riser into hook
    (11, t0["beat_01.mp3"] - 0.3, 0.4),    # whoosh into hook beat
    (12, t0["beat_03.mp3"] + 30.0, 0.5),   # hit on 51% moment
    (11, t0["beat_06.mp3"] - 0.3, 0.4),    # whoosh into pressure
    (12, t0["beat_06.mp3"] + 6.5, 0.5),    # hit on 100% tariff
    (10, t0["beat_08.mp3"] - 1.5, 0.35),   # riser into payoff
    (11, t0["beat_09.mp3"] - 0.3, 0.4),    # whoosh into close
]
parts = []
for k, (si, at, vol) in enumerate(SFX):
    ms = int(at * 1000)
    parts.append(f"[{si}:a]adelay={ms}|{ms},volume={vol},aresample=44100[sfx{k}]")
F.extend(parts)
mix_ins = "[dck][voice_main]" + "".join(f"[sfx{k}]" for k in range(len(SFX)))
F.append(f"{mix_ins}amix=inputs={len(SFX)+2}:normalize=0,"
         f"alimiter=limit=0.95,afade=t=out:st={TOTAL-3:.2f}:d=3[aout]")

cmd = (["ffmpeg", "-y"] + inputs +
       ["-filter_complex", ";".join(F), "-map", "[aout]",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        f"{BASE}/audio/fixed_mix.m4a"])
print("building mix...")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-2000:]); sys.exit(1)

# remux with existing video
cmd2 = ["ffmpeg", "-y", "-i", f"{BASE}/downthegroup-episode-1-v2.mp4",
        "-i", f"{BASE}/audio/fixed_mix.m4a",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "copy",
        "-shortest", "-movflags", "+faststart",
        f"{BASE}/downthegroup-episode-1-v2-fixed.mp4"]
print("remuxing...")
r = subprocess.run(cmd2, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-2000:]); sys.exit(1)
print("OK -> downthegroup-episode-1-v2-fixed.mp4")
