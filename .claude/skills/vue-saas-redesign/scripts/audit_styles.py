#!/usr/bin/env python3
"""Audit style consistency in a Vue 3 app.

Scans <style> blocks in .vue files and plain .css/.scss files under a directory and
reports, per file:
  - spacing values (margin/padding/gap/inset) that are off the 4px scale
  - font sizes off the type scale
  - raw hex/rgb colors used outside token definitions (lines declaring --custom-props)
  - how many declarations already use var(--...)

Usage:
  python audit_styles.py <src-dir> [--json] [--top N]

Run it before and after a redesign and compare the totals. Zero is not the goal;
a sharp drop, with the remaining hits being deliberate one-offs, is.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SPACING_SCALE_PX = {0, 1, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96}
FONT_SCALE_PX = {11, 12, 13, 14, 15, 16, 18, 20, 24, 28, 30, 32, 36, 40, 48}

SPACING_PROPS = re.compile(
    r"^(margin|padding|gap|row-gap|column-gap|inset)(-(top|right|bottom|left|inline|block)(-(start|end))?)?$"
)
DECL = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;{}]+)")
LENGTH = re.compile(r"(?<![\w.-])(-?\d*\.?\d+)(px|rem)\b")
HEX = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RGB = re.compile(r"\brgba?\(\s*\d")
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
SKIP_DIRS = {"node_modules", "dist", "build", ".git", ".vite", "coverage"}


def to_px(num, unit):
    return float(num) * (16 if unit == "rem" else 1)


def on_scale(px, scale):
    return any(abs(abs(px) - s) < 0.26 for s in scale)


def style_text(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".vue":
        # Keep line numbers meaningful: blank out everything outside <style> blocks.
        out = [""] * (text.count("\n") + 1)
        for m in STYLE_BLOCK.finditer(text):
            start_line = text.count("\n", 0, m.start(1))
            for i, line in enumerate(m.group(1).split("\n")):
                out[start_line + i] = line
        return out
    return text.split("\n")


def audit_file(path):
    res = {"spacing_off_scale": [], "font_off_scale": [], "raw_colors": [], "var_uses": 0, "declarations": 0}
    for lineno, line in enumerate(style_text(path), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("/*", "*", "//")):
            continue
        for prop, value in DECL.findall(line):
            prop = prop.lower()
            if prop.startswith("--"):
                continue  # token definition
            res["declarations"] += 1
            if "var(--" in value:
                res["var_uses"] += 1
            if SPACING_PROPS.match(prop) and "calc(" not in value:
                for num, unit in LENGTH.findall(value):
                    if not on_scale(to_px(num, unit), SPACING_SCALE_PX):
                        res["spacing_off_scale"].append((lineno, f"{prop}: {value.strip()}"))
                        break
            if prop == "font-size" and "calc(" not in value and "clamp(" not in value:
                for num, unit in LENGTH.findall(value):
                    if not on_scale(to_px(num, unit), FONT_SCALE_PX):
                        res["font_off_scale"].append((lineno, f"{prop}: {value.strip()}"))
                        break
        # Colors: anything literal outside a token definition line.
        if re.search(r"--[\w-]+\s*:", line):
            continue
        if HEX.search(line) or RGB.search(line):
            res["raw_colors"].append((lineno, stripped[:100]))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="app source directory, e.g. client/src")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    ap.add_argument("--top", type=int, default=3, help="example hits to show per file and category")
    args = ap.parse_args()

    root = Path(args.src)
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")

    files = sorted(
        p for p in root.rglob("*")
        if p.suffix in {".vue", ".css", ".scss"} and not any(part in SKIP_DIRS for part in p.parts)
    )
    report = {str(p.relative_to(root)).replace("\\", "/"): audit_file(p) for p in files}
    totals = {
        "files": len(report),
        "declarations": sum(r["declarations"] for r in report.values()),
        "var_uses": sum(r["var_uses"] for r in report.values()),
        "spacing_off_scale": sum(len(r["spacing_off_scale"]) for r in report.values()),
        "font_off_scale": sum(len(r["font_off_scale"]) for r in report.values()),
        "raw_colors": sum(len(r["raw_colors"]) for r in report.values()),
    }
    totals["token_coverage_pct"] = round(100 * totals["var_uses"] / totals["declarations"], 1) if totals["declarations"] else 0.0

    if args.json:
        print(json.dumps({"totals": totals, "files": report}, indent=2))
        return

    print(f"Scanned {totals['files']} files, {totals['declarations']} declarations")
    print(f"  token coverage (declarations using var(--)): {totals['token_coverage_pct']}%")
    print(f"  spacing values off the 4px scale:            {totals['spacing_off_scale']}")
    print(f"  font sizes off the type scale:               {totals['font_off_scale']}")
    print(f"  raw colors outside token definitions:        {totals['raw_colors']}")
    print()
    ranked = sorted(
        report.items(),
        key=lambda kv: -(len(kv[1]["spacing_off_scale"]) + len(kv[1]["font_off_scale"]) + len(kv[1]["raw_colors"])),
    )
    for name, r in ranked:
        n = len(r["spacing_off_scale"]) + len(r["font_off_scale"]) + len(r["raw_colors"])
        if n == 0:
            continue
        print(f"{name}: {len(r['spacing_off_scale'])} spacing, {len(r['font_off_scale'])} font, {len(r['raw_colors'])} color")
        for key in ("spacing_off_scale", "font_off_scale", "raw_colors"):
            for lineno, snippet in r[key][: args.top]:
                print(f"    L{lineno}: {snippet}")


if __name__ == "__main__":
    main()
