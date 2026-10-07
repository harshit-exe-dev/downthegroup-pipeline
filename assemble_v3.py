#!/usr/bin/env python3
"""Assemble Downthegroup Ep1 v3: QA fix pass.
- New shot plan: no source clip used more than 2x (fresh Mixkit clips +
  mirror variants + route_map_b color variant).
- Shot TIMINGS identical to v2 (audio stays in sync).
- Video-only render; audio muxed separately from audio/final_mix.m4a.
"""
import json, os, subprocess, sys

BASE = os.path.expanduser("~/workspace/youtube-video")
BROLL = os.path.join(BASE, "broll")
ANIM = os.path.join(BASE, "anim")
OUT = os.path.join(BASE, "build", "v3_video_only.mp4")

XF = 0.4

with open(os.path.join(BASE, "timeline.json")) as f:
    TL = json.load(f)
TOTAL = TL["total"]

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
    # seg0: lead-in
    segs.append((2.5,   [B("tanker_aerial", 2.9, 0)]))
    # seg1: beat1
    segs.append((16.248, [B("tanker_aerial", 4.5, 3.0), A("hit_saza", 4.5),
                          B("washington", 4.0, 0), B("tanker_aerial_2", 4.4, 0)]))
    # seg2: beat2
    segs.append((12.768, [A("route_map", 5.0), B("ship_deck", 4.0, 0),
                          B("refinery_day", 4.5, 0)]))
    # seg3: beat3
    segs.append((48.792, [A("bar_grow", 11.0), A("hit_40b", 4.0),
                          B("refinery_day", 4.5, 4.6), A("pie_fill", 10.5),
                          B("cargo_ship", 4.5, 0), A("hit_51", 4.0),
                          B("ship_deck", 4.5, 4.2), B("tanker_aerial_2", 4.5, 4.6),
                          B("refinery_night", 4.5, 0)]))
    # seg4: beat4
    segs.append((32.232, [B("currency", 5.0, 0), B("refinery_day_2", 4.5, 0),
                          B("pumpjack", 4.5, 0), B("cargo_ship", 4.5, 4.6),
                          B("fuel_station", 4.2, 0), B("city_traffic", 4.5, 0),
                          B("refinery_night", 4.5, 8.6),
                          B("refinery_night_2", 4.0, 0)]))
    # seg5: beat5
    segs.append((43.032, [A("hit_60cap", 4.5), A("route_map", 7.0),
                          B("cargo_ship_2", 4.5, 0), B("ship_deck_2", 4.5, 0),
                          B("pumpjack", 4.5, 4.6), B("pipeline", 4.0, 0),
                          B("refinery_night_2", 4.5, 4.5), B("sunset_ship_2", 4.5, 0),
                          B("city_traffic", 4.5, 4.6)]))
    # seg6: beat6
    segs.append((53.088, [B("washington", 5.0, 4.2), A("hit_tariff", 4.5),
                          B("capitol_2", 4.5, 0), B("currency", 4.5, 5.2),
                          B("delhi", 4.5, 0), B("cargo_ship_2", 4.5, 5.0),
                          B("ship_deck_2", 4.5, 5.0), B("pumpjack_2", 4.5, 0),
                          B("moscow", 4.5, 0), B("city_traffic_2", 4.5, 0),
                          B("delhi", 4.0, 4.6), B("sunset_ship_2", 4.5, 5.0),
                          B("capitol_2", 4.0, 5.0)]))
    # seg7: beat7
    segs.append((41.04,  [A("hit_20lakh", 4.5), B("sunset_ship_3", 4.5, 0),
                          B("city_traffic_2", 4.5, 5.0), B("fuel_station", 3.9, 4.2),
                          B("pipeline", 3.8, 4.0), B("moscow", 4.5, 4.6),
                          B("sunset_ship_4", 4.5, 0), B("refinery_night_3", 4.5, 0),
                          B("pumpjack_2", 4.5, 5.0), B("moscow_m", 4.5, 0)]))
    # seg8: beat8
    segs.append((24.888, [A("hit_wash_delhi", 5.5), B("capitol_3", 4.0, 0),
                          B("delhi_m", 4.0, 0), B("sunset_ship_3", 5.0, 0),
                          A("route_map_b", 6.4)]))
    # seg9: beat9
    segs.append((15.96,  [A("endcard", 8.5), B("sunset_ship_4", 4.0, 4.5),
                          A("endcard", 3.5)]))
    # seg10: outro
    segs.append((3.0,    [B("sunset_ship_2m", 3.0, 0)]))

    GAP = TL["gap"]
    normed = []
    for si, (D, shots) in enumerate(segs):
        m = len(shots)
        target = D + XF * (m if si < len(segs) - 1 else m - 1)
        if 1 <= si <= 8:
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
    shots = []
    for seg in plan:
        shots.extend(seg)
    n = len(shots)
    durs = [s[2] for s in shots]
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
    nV = len(shots)
    F = []
    for i, (kind, name, ln, inp) in enumerate(shots):
        F.append(f"[{i}:v]trim=0:{ln:.3f},setpts=PTS-STARTPTS,{GRADE}[v{i}]")
    off = durs[0] - XF
    F.append(f"[v0][v1]xfade=transition=fade:duration={XF}:offset={off:.3f}[x1]")
    total_v = durs[0] + durs[1] - XF
    for i in range(2, nV):
        off = total_v - XF
        F.append(f"[x{i-1}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
        total_v = total_v + durs[i] - XF
    F.append(f"[x{nV-1}]fade=t=in:st=0:d=0.6,fade=t=out:st={total_v-1.2:.3f}:d=1.2,"
             f"subtitles={BASE}/captions.ass:fontsdir=/usr/share/fonts[vout]")
    cmd += ["-filter_complex", ";".join(F),
            "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-movflags", "+faststart", OUT]
    print(f"inputs: {nV} video shots; expected video len ~{total_v:.2f}s")
    # audit: no source clip more than 2x
    from collections import Counter
    c = Counter(s[1] for s in shots)
    bad = {k: v for k, v in c.items() if v > 2}
    if bad:
        raise SystemExit(f"REPEAT VIOLATION: {bad}")
    print("repeat audit OK (all sources <=2x)")
    r = subprocess.run(cmd)
    return r.returncode

if __name__ == "__main__":
    sys.exit(build())
