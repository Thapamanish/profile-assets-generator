#!/usr/bin/env python3
"""Generate the self-contained SVG assets used by this profile README.

Only the Python standard library is used. Run from the repository root:
    python3 scripts/generate_assets.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import random
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

PALETTE = {
    "bg": "#0b1020",
    "panel": "#111936",
    "border": "#232c55",
    "text": "#e8ecf8",
    "muted": "#8b95b8",
    "periwinkle": "#7c9cff",
    "mint": "#5eead4",
    "amber": "#ffb86b",
    "nepal": "#dc143c",
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace"
DEVANAGARI = "'Noto Sans Devanagari', Mangal, 'Nirmala UI', sans-serif"


def svg_document(title: str, description: str, view_box: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
{body}
</svg>
'''


def write_asset(name: str, content: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / name).write_text(content, encoding="utf-8")


def grapheme_clusters(text: str) -> list[str]:
    """Split text safely for this profile's English and Devanagari lines.

    A Devanagari consonant joined with a virama stays with its following
    consonant; combining marks stay with their base. Thus a conjunct is never
    revealed mid-cluster. This is intentionally stdlib-only.
    """
    clusters: list[str] = []
    current = ""
    virama = "\u094d"
    joiners = {"\u200c", "\u200d"}

    for char in text:
        category = unicodedata.category(char)
        is_mark = category.startswith("M")
        if not current:
            current = char
        elif is_mark or char == virama or char in joiners or current[-1] in {virama, *joiners}:
            current += char
        else:
            clusters.append(current)
            current = char
    if current:
        clusters.append(current)
    return clusters


def typing_delay(index: int) -> float:
    """Deterministic 55-95 ms typing jitter."""
    jitter = (-17, -11, -6, 0, 5, 11, 17, 8, -3)
    return (75 + jitter[index % len(jitter)]) / 1000


def fmt(value: float) -> str:
    return f"{value:.5f}".rstrip("0").rstrip(".")


def header_svg() -> str:
    width, height, duration = 900, 340, 20.0
    cols, rows = 12, 3
    brick_w, brick_h, gap = 64, 34, 6
    start_x, start_y = 33, 86
    row_gap = 10
    colors = [PALETTE["periwinkle"], PALETTE["mint"], PALETTE["amber"]]

    grid_centers: list[tuple[float, float]] = []
    for row in range(rows - 1, -1, -1):
        indices = range(cols) if (rows - 1 - row) % 2 == 0 else range(cols - 1, -1, -1)
        for col in indices:
            x = start_x + col * (brick_w + gap)
            y = start_y + row * (brick_h + row_gap)
            grid_centers.append((x + brick_w / 2, y + brick_h / 2))

    # Fixed seed = reproducibly random: every loop breaks the same deliberately
    # scattered pattern, never a left-to-right sweep.
    centers = [grid_centers[index] for index in random.Random(2027).sample(range(len(grid_centers)), len(grid_centers))]

    # Every shot leaves the paddle, clears one brick, then returns to the
    # paddle. Uneven x targets make it read as a game, not a scanner.
    hit_times = [0.9 + index * 0.36 for index in range(len(centers))]
    return_times = [hit + 0.18 for hit in hit_times]
    reset_start, reset_end = 16.8, 17.7
    bricks: list[str] = []
    for index in range(rows * cols):
        row, col = divmod(index, cols)
        x = start_x + col * (brick_w + gap)
        y = start_y + row * (brick_h + row_gap)
        hit = hit_times[centers.index((x + brick_w / 2, y + brick_h / 2))]
        key_times = [0, hit / duration, min((hit + 0.04) / duration, 0.99), reset_start / duration, reset_end / duration, 1]
        bricks.append(
            f'''  <rect x="{fmt(x)}" y="{fmt(y)}" width="{brick_w}" height="{brick_h}" rx="7" fill="{colors[(row + col) % len(colors)]}">
    <animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="{';'.join(fmt(v) for v in key_times)}" dur="{duration}s" repeatCount="indefinite"/>
  </rect>'''
        )

    ball_y = 296.0
    points = [(450.0, ball_y)]
    point_times = [0.0]
    paddle_values = [360.0]
    paddle_x = 360.0
    for index, ((brick_x, brick_y), hit, returned) in enumerate(zip(centers, hit_times, return_times)):
        target = max(40.0, min(700.0, brick_x - 90.0))
        paddle_x = paddle_x * 0.30 + target * 0.70
        landing = (paddle_x + 90.0, ball_y) if index < len(centers) - 1 else (872.0, 344.0)
        points.extend([(brick_x, brick_y), landing])
        point_times.extend([hit, returned])
        paddle_values.extend([paddle_x, paddle_x])
    points.extend([(450.0, ball_y), (450.0, ball_y)])
    point_times.extend([reset_start, duration])
    paddle_values.extend([360.0, 360.0])
    x_values = ";".join(fmt(x) for x, _ in points)
    y_values = ";".join(fmt(y) for _, y in points)
    key_times = ";".join(fmt(t / duration) for t in point_times)

    miss_time = return_times[-1]
    body = f'''  <rect width="900" height="340" rx="22" fill="{PALETTE['bg']}"/>
  <rect x="1" y="1" width="898" height="338" rx="21" fill="{PALETTE['panel']}" stroke="{PALETTE['border']}" stroke-width="2"/>
  <text x="34" y="39" fill="{PALETTE['muted']}" font-family="{MONO}" font-size="14">manish@nepal:~/motto</text>
  <text x="34" y="62" fill="{PALETTE['text']}" font-family="{MONO}" font-size="17" font-weight="700">CLEAR THE WAY. KEEP BUILDING.</text>

  <text x="450" y="142" fill="{PALETTE['text']}" text-anchor="middle" font-family="{MONO}" font-size="42" font-weight="700">Build things that matter.</text>
  <text x="450" y="191" fill="{PALETTE['mint']}" text-anchor="middle" font-family="{MONO}" font-size="42" font-weight="700">Learn in public.</text>

{chr(10).join(bricks)}

  <rect y="288" width="900" height="1" fill="{PALETTE['border']}"/>
  <rect y="305" width="180" height="10" rx="5" fill="{PALETTE['periwinkle']}">
    <animate attributeName="x" values="{';'.join(fmt(v) for v in paddle_values)}" keyTimes="{key_times}" dur="{duration}s" repeatCount="indefinite" calcMode="linear"/>
  </rect>
  <circle r="9" fill="{PALETTE['amber']}" stroke="{PALETTE['bg']}" stroke-width="3">
    <animate attributeName="cx" values="{x_values}" keyTimes="{key_times}" dur="{duration}s" repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="cy" values="{y_values}" keyTimes="{key_times}" dur="{duration}s" repeatCount="indefinite" calcMode="linear"/>
    <animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="0;{fmt(miss_time / duration)};{fmt((miss_time + 0.05) / duration)};0.94;0.98;1" dur="{duration}s" repeatCount="indefinite"/>
  </circle>
  <text x="866" y="326" fill="{PALETTE['muted']}" text-anchor="end" font-family="{MONO}" font-size="13">loop 20s</text>'''
    return svg_document(
        "Breakout animation revealing Manish Thapa's motto",
        "A scripted ball breaks 36 bricks and reveals Build things that matter. Learn in public. before the game resets.",
        "0 0 900 340",
        body,
    )


def typing_svg() -> tuple[str, dict[str, int | float]]:
    lines = [
        "Hi, I'm Manish",
        "नमस्ते, मेरो नाम मनिष।",
        "MS CS @ SDSU, graduating Aug 2027",
        "ex-backend engineer: Target",
        "EX-SWE Intern @ Google X",
    ]
    clusters = [grapheme_clusters(line) for line in lines]
    longest = max(len(line) for line in clusters)
    if longest > 56:
        raise ValueError(f"Terminal line is {longest} clusters; the limit is 56.")

    advance = 13
    line_advances = [13, 15, 13, 13, 13]
    prompt_width = 28
    padding = 40
    longest_text_width = max(len(line) * line_advances[index] for index, line in enumerate(clusters))
    panel_width = longest_text_width + prompt_width + padding
    if panel_width > 860:
        raise ValueError(f"Terminal panel would be {panel_width}px wide, exceeding the 860px safety limit.")
    panel_x = (900 - panel_width) / 2
    text_x = panel_x + 20 + prompt_width

    # One master timeline. Each state is (time, line, visible-cluster-count, mode).
    states: list[tuple[float, int, int, str]] = [(0.0, 0, 0, "idle")]
    t = 0.4
    segments: list[tuple[float, float, str]] = []
    for line_index, line_clusters in enumerate(clusters):
        for visible in range(1, len(line_clusters) + 1):
            start = t
            t += typing_delay(visible - 1)
            segments.append((start, t, "active"))
            states.append((t, line_index, visible, "active"))
        start = t
        t += 1.4
        segments.append((start, t, "idle"))
        states.append((t, line_index, len(line_clusters), "idle"))
        for visible in range(len(line_clusters) - 1, -1, -1):
            start = t
            t += 0.03
            segments.append((start, t, "active"))
            states.append((t, line_index, visible, "active"))
        start = t
        t += 0.3
        segments.append((start, t, "idle"))
        states.append((t, line_index, 0, "idle"))
    duration = t

    text_frames: list[str] = []
    for index, (start, line_index, visible, _) in enumerate(states[:-1]):
        if visible == 0:
            continue
        end = states[index + 1][0]
        start_key = start / duration
        end_key = end / duration
        epsilon = min(0.0001, (end_key - start_key) / 3)
        # NBSP preserves a typed trailing space in SVG and avoids trailing
        # whitespace in the generated XML, which would fail a diff check.
        prefix = escape("".join(clusters[line_index][:visible])).replace(" ", "&#160;")
        font = DEVANAGARI if line_index == 1 else MONO
        text_length = visible * line_advances[line_index]
        text_frames.append(
            f'''  <text x="{fmt(text_x)}" y="72" fill="{PALETTE['text']}" font-family="{font}" font-size="22" font-weight="600" textLength="{text_length}" lengthAdjust="spacing">{prefix}
    <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{fmt(start_key)};{fmt(start_key + epsilon)};{fmt(end_key)};{fmt(min(end_key + epsilon, 0.9999))};1" dur="{fmt(duration)}s" repeatCount="indefinite" calcMode="discrete"/>
  </text>'''
        )

    x_values = []
    x_times = []
    for time, line_index, visible, _ in states:
        x_values.append(fmt(text_x + visible * line_advances[line_index]))
        x_times.append(fmt(time / duration))

    # Solid cursor during active segments; it blinks every 500ms during idle segments.
    opacity_times: list[float] = [0.0]
    opacity_values: list[str] = ["1"]
    for start, end, mode in segments:
        if mode == "active":
            opacity_times.extend([start / duration, end / duration])
            opacity_values.extend(["1", "1"])
        else:
            cursor_time = start
            visible = True
            while cursor_time < end:
                opacity_times.append(cursor_time / duration)
                opacity_values.append("1" if visible else "0")
                visible = not visible
                cursor_time += 0.5
            opacity_times.append(end / duration)
            opacity_values.append("1" if visible else "0")
    opacity_pairs = sorted(zip(opacity_times, opacity_values), key=lambda item: item[0])
    opacity_key_times = ";".join(fmt(time) for time, _ in opacity_pairs)
    opacity_value_string = ";".join(value for _, value in opacity_pairs)

    metrics = {
        "longest_clusters": longest,
        "longest_text_width": longest_text_width,
        "panel_width": panel_width,
        "padding": padding,
        "duration": duration,
    }
    body = f'''  <rect width="900" height="112" rx="18" fill="{PALETTE['bg']}"/>
  <rect x="{fmt(panel_x)}" y="12" width="{panel_width}" height="88" rx="14" fill="{PALETTE['panel']}" stroke="{PALETTE['border']}" stroke-width="2"/>
  <circle cx="{fmt(panel_x + 20)}" cy="31" r="5" fill="{PALETTE['nepal']}"/>
  <circle cx="{fmt(panel_x + 37)}" cy="31" r="5" fill="{PALETTE['amber']}"/>
  <circle cx="{fmt(panel_x + 54)}" cy="31" r="5" fill="{PALETTE['mint']}"/>
  <text x="{fmt(panel_x + 20)}" y="72" fill="{PALETTE['periwinkle']}" font-family="{MONO}" font-size="22" font-weight="700">$</text>
{chr(10).join(text_frames)}
  <rect y="46" width="3" height="30" rx="1.5" fill="{PALETTE['amber']}">
    <animate attributeName="x" values="{';'.join(x_values)}" keyTimes="{';'.join(x_times)}" dur="{fmt(duration)}s" repeatCount="indefinite" calcMode="discrete"/>
    <animate attributeName="opacity" values="{opacity_value_string}" keyTimes="{opacity_key_times}" dur="{fmt(duration)}s" repeatCount="indefinite" calcMode="discrete"/>
  </rect>
'''
    return (
        svg_document(
            "Animated terminal introduction for Manish Thapa",
            f"Five deterministic terminal lines. Longest line is {longest} grapheme clusters and fits a {panel_width}px panel with {padding}px horizontal padding.",
            "0 0 900 112",
            body,
        ),
        metrics,
    )


def journey_svg() -> str:
    # Kathmandu -> Target -> SDSU -> X -> Next. All marks are inline paths or simple vector geometry.
    nodes = [(92, 124), (277, 92), (462, 124), (647, 92), (832, 124)]
    values_x = ";".join(str(x) for x, _ in [*nodes, nodes[-1], nodes[0]])
    values_y = ";".join(str(y) for _, y in [*nodes, nodes[-1], nodes[0]])
    times = ";".join(["0", "0.18", "0.36", "0.54", "0.72", "0.86", "1"])
    body = f'''  <rect width="900" height="220" rx="20" fill="{PALETTE['bg']}"/>
  <rect x="1" y="1" width="898" height="218" rx="19" fill="{PALETTE['panel']}" stroke="{PALETTE['border']}" stroke-width="2"/>
  <text x="32" y="38" fill="{PALETTE['muted']}" font-family="{MONO}" font-size="14">journey.log</text>
  <path d="M92 124 C154 58 215 58 277 92 S400 158 462 124 S585 58 647 92 S770 158 832 124" fill="none" stroke="{PALETTE['border']}" stroke-width="5" stroke-linecap="round"/>
  <path d="M92 124 C154 58 215 58 277 92 S400 158 462 124 S585 58 647 92 S770 158 832 124" fill="none" stroke="{PALETTE['periwinkle']}" stroke-width="2" stroke-linecap="round" opacity="0.8"/>

  <!-- Kathmandu / Nepal flag: inline vector geometry -->
  <g transform="translate(72 104)">
    <path d="M0 0 L24 10 L0 20 L24 31 L0 42 Z" fill="{PALETTE['nepal']}" stroke="{PALETTE['text']}" stroke-width="1.5"/>
    <circle cx="8" cy="13" r="3" fill="{PALETTE['text']}"/>
    <circle cx="8" cy="31" r="3" fill="{PALETTE['text']}"/>
  </g>
  <text x="92" y="171" text-anchor="middle" fill="{PALETTE['text']}" font-family="{MONO}" font-size="17" font-weight="700">NEPAL</text>
  <text x="92" y="191" text-anchor="middle" fill="{PALETTE['muted']}" font-family="{MONO}" font-size="12">origin</text>

  <!-- Target bullseye: inline vector geometry -->
  <g transform="translate(277 92)">
    <circle r="21" fill="#cc0000"/>
    <circle r="12" fill="{PALETTE['panel']}"/>
    <circle r="5" fill="#cc0000"/>
  </g>
  <text x="277" y="171" text-anchor="middle" fill="{PALETTE['text']}" font-family="{MONO}" font-size="17" font-weight="700">TARGET</text>
  <text x="277" y="191" text-anchor="middle" fill="{PALETTE['muted']}" font-family="{MONO}" font-size="12">backend systems</text>

  <!-- SDSU: a clean custom vector S lettermark, not an official Aztec mark -->
  <g transform="translate(442 104)">
    <rect width="40" height="40" rx="8" fill="#c41230"/>
    <path d="M28 10 H14 C10 10 9 14 13 16 L24 20 C29 22 28 30 23 30 H11" fill="none" stroke="{PALETTE['text']}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <text x="462" y="53" text-anchor="middle" fill="{PALETTE['text']}" font-family="{MONO}" font-size="17" font-weight="700">SDSU</text>
  <text x="462" y="72" text-anchor="middle" fill="{PALETTE['muted']}" font-family="{MONO}" font-size="12">MS CS · Aug 2027</text>

  <!-- Clean inline Google wordmark; no external image dependency -->
  <text x="647" y="103" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="27" font-weight="600" letter-spacing="-1.5"><tspan fill="#4285f4">G</tspan><tspan fill="#ea4335">o</tspan><tspan fill="#fbbc05">o</tspan><tspan fill="#4285f4">g</tspan><tspan fill="#34a853">l</tspan><tspan fill="#ea4335">e</tspan></text>
  <text x="647" y="171" text-anchor="middle" fill="{PALETTE['text']}" font-family="{MONO}" font-size="17" font-weight="700">GOOGLE X</text>
  <text x="647" y="191" text-anchor="middle" fill="{PALETTE['muted']}" font-family="{MONO}" font-size="12">the Moonshot Factory</text>

  <g transform="translate(812 104)">
    <circle cx="20" cy="20" r="19" fill="none" stroke="{PALETTE['mint']}" stroke-width="3" stroke-dasharray="4 5"/>
    <path d="M16 15 C16 9 25 9 25 15 C25 20 20 20 20 25 M20 32 L20 32" fill="none" stroke="{PALETTE['amber']}" stroke-width="4" stroke-linecap="round"/>
  </g>
  <text x="832" y="171" text-anchor="middle" fill="{PALETTE['text']}" font-family="{MONO}" font-size="17" font-weight="700">NEXT</text>
  <text x="832" y="191" text-anchor="middle" fill="{PALETTE['muted']}" font-family="{MONO}" font-size="12">keep building</text>

  <circle r="9" fill="{PALETTE['amber']}" stroke="{PALETTE['bg']}" stroke-width="4">
    <animate attributeName="cx" values="{values_x}" keyTimes="{times}" dur="12s" repeatCount="indefinite" calcMode="spline" keySplines=".42 0 .58 1;.42 0 .58 1;.42 0 .58 1;.42 0 .58 1;.42 0 .58 1;.42 0 .58 1"/>
    <animate attributeName="cy" values="{values_y}" keyTimes="{times}" dur="12s" repeatCount="indefinite" calcMode="spline" keySplines=".42 0 .58 1;.42 0 .58 1;.42 0 .58 1;.42 0 .58 1;.42 0 .58 1;.42 0 .58 1"/>
  </circle>'''
    return svg_document(
        "Manish Thapa's animated career journey",
        "A moving dot travels from Kathmandu to Target, San Diego State University, Google X the Moonshot Factory, and the next chapter.",
        "0 0 900 220",
        body,
    )


def main() -> None:
    write_asset("header.svg", header_svg())
    typing, metrics = typing_svg()
    write_asset("typing.svg", typing)
    write_asset("journey.svg", journey_svg())
    print("Generated assets:")
    print(f"  typing longest line: {metrics['longest_clusters']} grapheme clusters")
    print(f"  typing text width:   {metrics['longest_text_width']}px")
    print(f"  typing panel width:  {metrics['panel_width']}px")
    print(f"  typing padding:      {metrics['padding']}px total horizontal padding")
    print("  header brick coverage: 36/36 bricks hit by scripted ball path")


if __name__ == "__main__":
    main()
