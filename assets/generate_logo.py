"""
generate_logo.py
-----------------
Generates the original "open book" logo mark used by the Streamlit app
(assets/logo.png). Kept as a script rather than just shipping the PNG so
the mark is reproducible and easy to re-tune (colors, proportions).

This is an original design made for this project -- it is not based on
GitLab's or any other company's actual logo/branding, specifically to
avoid any trademark confusion in a public demo.

Usage:
    python assets/generate_logo.py
"""

from PIL import Image, ImageDraw
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

SIZE = 512
NAVY = (27, 42, 65, 255)      # #1B2A41 -- primary ink
PAPER = (247, 248, 250, 255)  # #F7F8FA -- page color
AMBER = (201, 138, 44, 255)   # #C98A2C -- single accent, used sparingly


def generate() -> None:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded-square badge base
    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=110, fill=NAVY)

    # Open-book glyph: two curved "pages" meeting at a center spine
    cx, cy = SIZE // 2, SIZE // 2 + 10
    page_w, page_h = 150, 130

    left_page = [
        (cx, cy - page_h),
        (cx - page_w, cy - page_h + 40),
        (cx - page_w + 20, cy + page_h - 10),
        (cx, cy + page_h),
    ]
    right_page = [
        (cx, cy - page_h),
        (cx + page_w, cy - page_h + 40),
        (cx + page_w - 20, cy + page_h - 10),
        (cx, cy + page_h),
    ]
    draw.polygon(left_page, fill=PAPER)
    draw.polygon(right_page, fill=PAPER)

    # Spine
    draw.line([(cx, cy - page_h - 4), (cx, cy + page_h + 4)], fill=NAVY, width=6)

    # Simple "text lines" on each page, just enough to read as a handbook
    for y_off in (-55, -15, 25):
        y = cy + y_off
        draw.line([(cx - 110, y), (cx - 30, y)], fill=(27, 42, 65, 120), width=8)
        draw.line([(cx + 30, y), (cx + 110, y)], fill=(27, 42, 65, 120), width=8)

    # Single amber accent -- a bookmark-style dot, the one deliberate
    # spot of color, tying visually to the app's citation highlights.
    dot_r = 34
    dot_cx, dot_cy = SIZE - 118, 118
    draw.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=AMBER,
    )

    img.save(OUT_PATH)
    print(f"Logo written to {OUT_PATH}")


if __name__ == "__main__":
    generate()
