#!/usr/bin/env python3
"""Analyze GUI screenshots and produce a JSON summary.

Writes results to: logs/gui_mcp/analysis_summary.json

Metrics per image:
- filename, width, height, mode, channels
- mean (per channel), std (per channel)
- entropy (grayscale)
- is_uniform (True if image has <= 2 unique colors)
"""
from __future__ import annotations

import json
import math
import os

from PIL import Image


def channel_stats(pixels: list[int], channel_count: int) -> list[tuple]:
    # pixels is a flat list of ints (0..255) in channel-major order per pixel
    totals = [0.0] * channel_count
    totalsq = [0.0] * channel_count
    n = len(pixels) // channel_count
    if n == 0:
        return [(0.0, 0.0)] * channel_count
    for i in range(n):
        for c in range(channel_count):
            v = pixels[i * channel_count + c]
            totals[c] += v
            totalsq[c] += v * v
    stats = []
    for c in range(channel_count):
        mean = totals[c] / n
        var = totalsq[c] / n - mean * mean
        var = max(var, 0.0)
        std = math.sqrt(var)
        stats.append((mean, std))
    return stats


def shannon_entropy(hist: list[int], total: int) -> float:
    if total <= 0:
        return 0.0
    ent = 0.0
    for h in hist:
        if h <= 0:
            continue
        p = h / total
        ent -= p * math.log2(p)
    return ent


def analyze_image(path: str) -> dict:
    img = Image.open(path)
    img = img.convert("RGBA")
    w, h = img.size
    pixels = list(img.getdata())
    # flatten
    flat = [v for px in pixels for v in px]
    channel_count = 4
    stats = channel_stats(flat, channel_count)

    # grayscale histogram for entropy
    gray = img.convert("L")
    hist = gray.histogram()
    total = sum(hist)
    ent = shannon_entropy(hist, total)

    # detect uniformity
    uniq = len(set(pixels))
    is_uniform = uniq <= 2

    return {
        "filename": os.path.relpath(path),
        "width": w,
        "height": h,
        "mode": img.mode,
        "channels": channel_count,
        "mean_per_channel": [round(m, 2) for m, s in stats],
        "std_per_channel": [round(s, 2) for m, s in stats],
        "entropy": round(ent, 4),
        "unique_colors": uniq,
        "is_uniform": is_uniform,
    }


def find_images(root: str) -> list[str]:
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
    out = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                out.append(os.path.join(dirpath, fn))
    out.sort()
    return out


def main() -> None:
    screenshots_dir = os.path.join("logs", "gui_mcp", "screenshots")
    out_json = os.path.join("logs", "gui_mcp", "analysis_summary.json")
    if not os.path.isdir(screenshots_dir):
        print("No screenshots directory:", screenshots_dir)
        return
    imgs = find_images(screenshots_dir)
    if not imgs:
        print("No images found in:", screenshots_dir)
        return
    results = []
    for p in imgs:
        try:
            r = analyze_image(p)
            results.append(r)
            print(f"Analyzed: {r['filename']} {r['width']}x{r['height']} entropy={r['entropy']}")
        except Exception as e:
            print("Error analyzing", p, e)

    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf8") as f:
        json.dump({"images": results}, f, indent=2)
    print("Wrote summary to", out_json)


if __name__ == "__main__":
    main()
