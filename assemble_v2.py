#!/usr/bin/env python3
"""Assemble Downthegroup Ep1 v2: B-roll + Hyperframes anims + kinetic captions
+ graded look + music bed (ducked) + SFX. Single ffmpeg pass.
Reads timeline.json; SHOT_PLAN is finalized after clip inventory lands.
"""
import json, os, subprocess, sys

BASE = os.path.expanduser("~/workspace/youtube-video")
BROLL = os.path.join(BASE, "broll")
ANIM = os.path.join(BASE, "anim")
AUD = os.path.join(BASE, "audio")
NARR = os.path.join(BASE, "narration", "done")
OUT = os.path.join(BASE, "downthegroup-episode-1-v2.mp4")

XF = 0.4  # crossfade duration

with open(os.path.join(BASE, "timeline.json")) as f:
    TL = json.load(f)
TOTAL = TL["total"]
BEATS = TL["beats"]

# ---- clip inventory (filled after children report) ----
def inv(d):
    out = {}
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".mp4"):
                out[fn[:-4]] = os.path.join(d, fn)
    return out
BROLL_CLIPS = inv(BROLL)
ANIM_CLIPS = inv(ANIM)

def dur_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

# ---- SHOT PLAN: per beat: list of (kind, name, shot_len, in_point) ----
# kind: 'broll' | 'anim'. B-roll in-points are budgeted against real durations
# (TA 20.1 / RD 17.0 / RN 17.0 / CS 20.0 / MO 19.5 / DE 8.8 / WA 20.4 /
#  CU 10.3 / FS 8.1 / PJ 20.0 / CT 20.1 / SD 20.0 / TS 24.7 / PL 7.8).
# Anim clips loop/trim safely, so their in-points are always None.
def finalize_plan():
    b = BROLL_CLIPS
    a = ANIM_CLIPS
    def B(name, ln, inp=0):
        assert name in b, f"missing broll {name}"
        return ("broll", name, ln, inp)
    def A(name, ln):
        assert name in a, f"missing anim {name}"
        return ("anim", name, ln, None)

    segs = []
    # (segment duration, shots...); last segment is the outro (no outgoing xfade)
    segs.append((2.5,   [B("tanker_aerial", 2.9, 0)]))
    segs.append((16.248, [B("tanker_aerial", 4.5, 3.0), A("hit_saza", 4.5),
                          B("washington", 4.0, 0), B("tanker_aerial", 4.4, 8.0)]))
    segs.append((12.768, [A("route_map", 5.0), B("ship_deck", 4.0, 0),
                          B("refinery_day", 4.5, 0)]))
    segs.append((48.792, [A("bar_grow", 11.0), A("hit_40b", 4.0),
                          B("refinery_day", 4.5, 4.6), A("pie_fill", 10.5),
                          B("cargo_ship", 4.5, 0), A("hit_51", 4.0),
                          B("ship_deck", 4.5, 4.2), B("tanker_aerial", 4.5, 13.0),
                          B("refinery_night", 4.5, 0)]))
    segs.append((32.232, [B("currency", 5.0, 0), B("refinery_day", 4.5, 9.2),
                          B("pumpjack", 4.5, 0), B("cargo_ship", 4.5, 4.6),
                          B("fuel_station", 4.2, 0), B("city_traffic", 4.5, 0),
                          B("refinery_night", 4.5, 8.6),
                          B("refinery_night", 4.0, 12.0)]))
    segs.append((43.032, [A("hit_60cap", 4.5), A("route_map", 7.0),
                          B("cargo_ship", 4.5, 9.2), B("ship_deck", 4.5, 8.8),
                          B("pumpjack", 4.5, 4.6), B("pipeline", 4.0, 0),
                          B("refinery_night", 4.5, 12.4), B("tanker_sunset", 4.5, 0),
                          B("city_traffic", 4.5, 4.6)]))
    segs.append((53.088, [B("washington", 5.0, 4.2), A("hit_tariff", 4.5),
                          B("washington", 4.5, 9.4), B("currency", 4.5, 5.2),
                          B("delhi", 4.5, 0), B("cargo_ship", 4.5, 13.8),
                          B("ship_deck", 4.5, 13.4), B("pumpjack", 4.5, 9.2),
                          B("moscow", 4.5, 0), B("city_traffic", 4.5, 9.2),
                          B("delhi", 4.0, 4.6), B("tanker_sunset", 4.5, 4.6),
                          B("washington", 4.0, 14.0)]))
    segs.append((41.04,  [A("hit_20lakh", 4.5), B("tanker_sunset", 4.5, 9.2),
                          B("city_traffic", 4.5, 14.0), B("fuel_station", 3.9, 4.2),
                          B("pipeline", 3.8, 4.0), B("moscow", 4.5, 4.6),
                          B("tanker_sunset", 4.5, 13.8), B("refinery_night", 4.5, 3.0),
                          B("pumpjack", 4.5, 1.0), B("moscow", 4.5, 9.2)]))
    segs.append((24.888, [A("hit_wash_delhi", 5.5), B("washington", 4.0, 16.4),
                          B("delhi", 4.0, 2.0), B("tanker_sunset", 5.0, 6.0),
                          A("route_map", 6.4)]))
    segs.append((15.96,  [A("endcard", 8.5), B("tanker_sunset", 4.0, 12.0),
                          A("endcard", 3.5)]))
    segs.append((3.0,    [B("tanker_sunset", 3.0, 20.0)]))

    # Normalize: each beat segment's shots must sum to D + XF*m + GAP so that
    # after the xfade chain its contribution is exactly D + GAP (beat sync with
    # the narration timeline, which has 1.2s silences between beats).
    # Lead/outro have no gap. Pad goes on each segment's last shot (holds the
    # final visual through the pause). B-roll pad overflow is asserted.
    GAP = TL["gap"]
    normed = []
    for si, (D, shots) in enumerate(segs):
        m = len(shots)
        target = D + XF * (m if si < len(segs) - 1 else m - 1)
        if 1 <= si <= 8:  # beats 1-8: absorb the trailing inter-beat gap
            target += GAP
        cur = sum(s[2] for s in shots)
        pad = target - cur
        kind, name, ln, inp = shots[-1]
        if kind == "broll":
            src = BROLL_CLIPS[name]
            assert inp + ln + pad <= dur_of(src) + 0.05, \
                f"pad overflow {name}: {inp}+{ln}+{pad:.2f} > {dur_of(src):.2f}"
        shots = shots[:-1] + [(kind, name, ln + pad, inp)]
        normed.append(shots)
    return normed

GRADE = ("scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
         "setsar=1,fps=30,format=yuv420p,"
         "eq=contrast=1.06:saturation=0.92:brightness=-0.015,"
         "colorbalance=rs=0.07:gs=0.015:bs=-0.07:rm=0.04:bm=-0.04,"
         "vignette=PI/4.6,noise=alls=5:allf=t")

def build():
    plan = finalize_plan()
    # flatten shots, compute xfade offsets
    shots = []
    for seg in plan:
        shots.extend(seg)
    # adjust: shot lens include XF overlap compensation on last shot of each segment;
    # here we just chain everything with xfade; total video target = TOTAL
    n = len(shots)
    # compute offsets
    durs = [s[2] for s in shots]
    # inputs
    cmd = ["ffmpeg", "-y"]
    nshots = []
    for kind, name, ln, inp in shots:
        src = (BROLL_CLIPS if kind == "broll" else ANIM_CLIPS)[name]
        sd = dur_of(src)
        if sd < ln - 0.05:
            if kind == "broll":
                raise SystemExit(f"broll clip {name} too short ({sd:.1f}s < {ln:.1f}s)")
            cmd += ["-stream_loop", "-1", "-i", src]
        else:
            cmd += ["-ss", str(inp or 0), "-i", src]
        nshots.append((kind, name, ln, inp))
    shots = nshots
    # audio inputs: narration beats + silences
    a_idx = []
    tl_beats = BEATS
    # lead silence
    cmd += ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={TL['lead_in']}"]
    a_idx.append(("sil", TL["lead_in"]))
    for i, bt in enumerate(tl_beats):
        cmd += ["-i", os.path.join(NARR, bt["file"])]
        a_idx.append(("narr", bt["dur"]))
        if i < len(tl_beats) - 1:
            cmd += ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={TL['gap']}"]
            a_idx.append(("sil", TL["gap"]))
    cmd += ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={TL['outro']}"]
    a_idx.append(("sil", TL["outro"]))
    # music bed looped
    mus = os.path.join(AUD, "music_bed.mp3")
    cmd += ["-stream_loop", "-1", "-i", mus]
    # sfx inputs (placed later via adelay) - filled from SFX_PLAN
    sfx_files = []
    SFX = sfx_plan()
    for name, at, vol in SFX:
        p = os.path.join(AUD, name + ".mp3")
        if os.path.exists(p):
            cmd += ["-i", p]
            sfx_files.append((name, at, vol))

    nV = len(shots)
    # filter graph
    F = []
    for i, (kind, name, ln, inp) in enumerate(shots):
        F.append(f"[{i}:v]trim=0:{ln:.3f},setpts=PTS-STARTPTS,{GRADE}[v{i}]")
    # xfade chain
    off = durs[0] - XF
    F.append(f"[v0][v1]xfade=transition=fade:duration={XF}:offset={off:.3f}[x1]")
    total_v = durs[0] + durs[1] - XF
    for i in range(2, nV):
        off = total_v - XF
        F.append(f"[x{i-1}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
        total_v = total_v + durs[i] - XF
    F.append(f"[x{nV-1}]fade=t=in:st=0:d=0.6,fade=t=out:st={total_v-1.2:.3f}:d=1.2,"
             f"subtitles={BASE}/captions.ass:fontsdir=/usr/share/fonts[vout]")
    # audio: normalize then concat
    base_a = nV
    for j in range(len(a_idx)):
        F.append(f"[{base_a+j}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{j}]")
    concat_ins = "".join(f"[a{j}]" for j in range(len(a_idx)))
    F.append(f"{concat_ins}concat=n={len(a_idx)}:v=0:a=1[narr]")
    # music: trim, low volume, duck under narration
    mus_i = base_a + len(a_idx)
    F.append(f"[{mus_i}:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,volume=0.10,aresample=44100[mus]")
    F.append("[mus][narr]sidechaincompress=threshold=0.015:ratio=10:attack=250:release=900:makeup=1[dck]")
    # sfx
    if sfx_files:
        parts = []
        for k, (name, at, vol) in enumerate(sfx_files):
            si = mus_i + 1 + k
            parts.append(f"[{si}:a]adelay={int(at*1000)}|{int(at*1000)},volume={vol},aresample=44100[sfx{k}]")
        F.extend(parts)
        mix_ins = "[dck]" + "".join(f"[sfx{k}]" for k in range(len(sfx_files)))
        F.append(f"{mix_ins}amix=inputs={len(sfx_files)+1}:normalize=0[aout]")
    else:
        F.append("[dck]anull[aout]")
    F.append("[aout]alimiter=limit=0.95,atrim=0:{:.2f},asetpts=PTS-STARTPTS[aenc]".format(TOTAL))

    cmd += ["-filter_complex", ";".join(F),
            "-map", "[vout]", "-map", "[aenc]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
            "-movflags", "+faststart", "-shortest", OUT]
    print(f"inputs: {nV} video, {len(a_idx)} narr segs, music, {len(sfx_files)} sfx")
    print(f"expected video len ~{total_v:.2f}s vs audio {TOTAL:.2f}s")
    r = subprocess.run(cmd)
    return r.returncode

def sfx_plan():
    """(name, time_sec, volume) — sparse hits, never over voice-heavy moments."""
    tl = {b["file"]: b["start"] for b in BEATS}
    return [
        ("sfx_riser", 0.2, 0.35),                       # into hook
        ("sfx_whoosh", tl["beat_01.mp3"] - 0.3, 0.4),    # into hook beat (over lead gap)
        ("sfx_hit", tl["beat_03.mp3"] + 30.0, 0.5),      # 51% number moment (approx)
        ("sfx_whoosh", tl["beat_06.mp3"] - 0.3, 0.4),    # into pressure (gap)
        ("sfx_hit", tl["beat_06.mp3"] + 6.5, 0.5),       # 100% tariff hit
        ("sfx_riser", tl["beat_08.mp3"] - 1.5, 0.35),    # riser into payoff (over gap)
        ("sfx_whoosh", tl["beat_09.mp3"] - 0.3, 0.4),    # into close (gap)
    ]

if __name__ == "__main__":
    sys.exit(build())
