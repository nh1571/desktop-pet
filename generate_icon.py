"""Generate app icon: a slime face at 512x512."""
import math, os, sys

# Must set before importing pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import pygame.gfxdraw as gfx

PALETTE = {
    "body": (120, 210, 120),
    "body_shadow": (80, 170, 80),
    "body_light": (170, 240, 170),
    "outline": (40, 100, 40),
    "eye_white": (255, 255, 255),
    "eye_pupil": (30, 30, 30),
    "eye_highlight": (255, 255, 255),
    "blush": (255, 150, 150),
    "mouth": (50, 100, 50),
    "crown": (255, 215, 0),
    "crown_shadow": (200, 170, 0),
}


def draw_icon(size=512):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2 + 20
    s = size / 256  # scale factor from design coords

    # Body
    rx, ry = int(90 * s), int(68 * s)
    orx, ory = rx + 4, ry + 4
    gfx.filled_ellipse(surf, cx, cy, orx, ory, PALETTE["outline"])
    gfx.aaellipse(surf, cx, cy, orx, ory, PALETTE["outline"])
    gfx.filled_ellipse(surf, cx, cy, rx, ry, PALETTE["body"])
    gfx.aaellipse(surf, cx, cy, rx, ry, PALETTE["outline"])

    # Highlight
    hlx, hly = cx - rx // 3, cy - ry // 3
    hlrx, hlry = int(rx * 0.4), int(ry * 0.3)
    gfx.filled_ellipse(surf, hlx, hly, hlrx, hlry, (*PALETTE["body_light"], 140))
    gfx.aaellipse(surf, hlx, hly, hlrx, hlry, (*PALETTE["body_light"], 60))

    hl2x, hl2y = cx - rx // 4, cy - ry // 2
    hl2rx, hl2ry = int(rx * 0.15), int(ry * 0.12)
    gfx.filled_ellipse(surf, hl2x, hl2y, hl2rx, hl2ry, (255, 255, 255, 90))
    gfx.aaellipse(surf, hl2x, hl2y, hl2rx, hl2ry, (255, 255, 255, 40))

    # Eyes
    eye_spacing = int(28 * s)
    eye_y = cy - int(8 * s)
    eye_r = int(18 * s)
    for ex in (cx - eye_spacing, cx + eye_spacing):
        gfx.filled_circle(surf, ex, eye_y, eye_r, PALETTE["eye_white"])
        gfx.aacircle(surf, ex, eye_y, eye_r, PALETTE["outline"])
        pr = int(eye_r * 0.55)
        pox = int(2 * s)
        gfx.filled_circle(surf, ex + pox, eye_y, pr, PALETTE["eye_pupil"])
        gfx.aacircle(surf, ex + pox, eye_y, pr, PALETTE["eye_pupil"])
        hdr = max(2, int(4 * s))
        gfx.filled_circle(surf, ex + pox + int(3 * s), eye_y - int(4 * s), hdr, PALETTE["eye_highlight"])
        gfx.aacircle(surf, ex + pox + int(3 * s), eye_y - int(4 * s), hdr, PALETTE["eye_highlight"])

    # Blush
    blush_r = int(14 * s)
    for bx in (cx - int(44 * s), cx + int(44 * s)):
        gfx.filled_ellipse(surf, bx, cy + int(4 * s), blush_r, int(blush_r * 0.7), (*PALETTE["blush"], 100))
        gfx.aaellipse(surf, bx, cy + int(4 * s), blush_r, int(blush_r * 0.7), (*PALETTE["blush"], 40))

    # Mouth (happy arc)
    mw, mh = int(18 * s), int(10 * s)
    rect = pygame.Rect(cx - mw, cy + int(10 * s) - mh, mw * 2, mh * 2)
    pygame.draw.arc(surf, PALETTE["mouth"], rect, math.pi * 0.15, math.pi * 0.85, max(2, int(3 * s)))

    # Crown
    crown_y = cy - int(72 * s)
    crx, cry = int(16 * s), int(12 * s)
    points = [
        (cx - crx, crown_y),
        (cx - crx // 2, crown_y - cry),
        (cx, crown_y),
        (cx, crown_y - int(cry * 1.2)),
        (cx + crx // 2, crown_y),
        (cx + crx // 2, crown_y - cry),
        (cx + crx, crown_y),
    ]
    pygame.draw.polygon(surf, PALETTE["crown"], points)
    gfx.aapolygon(surf, points, PALETTE["crown_shadow"])
    gfx.filled_circle(surf, cx, crown_y - int(cry * 1.2) + 4, max(2, int(4 * s)), (255, 100, 100))
    gfx.aacircle(surf, cx, crown_y - int(cry * 1.2) + 4, max(2, int(4 * s)), (200, 50, 50))

    return surf


def main():
    pygame.init()
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    png_path = os.path.join(out_dir, "app_icon.png")
    surf = draw_icon(512)
    pygame.image.save(surf, png_path)
    print(f"Saved {png_path}")

    # Convert to .icns using macOS sips
    icns_path = os.path.join(out_dir, "app_icon.icns")
    os.system(f'sips -s format icns "{png_path}" --out "{icns_path}" 2>/dev/null')
    if os.path.exists(icns_path):
        print(f"Saved {icns_path}")
    else:
        print("Warning: .icns conversion failed (non-critical, will use png)")

    pygame.quit()


if __name__ == "__main__":
    main()
