"""Q-style vector slime renderer. Draws a cute slime using geometric shapes."""

import math
import pygame
import pygame.gfxdraw as gfx

from config import WINDOW_SIZE, VECTOR_PALETTE as P, STAGE_SCALES


def _ease_out_quad(t: float) -> float:
    return 1 - (1 - t) ** 2


def _ease_in_out_quad(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


class VectorSlime:
    """Draws a cute slime at the center of the window.

    Animation parameters are applied each frame before draw():
        body_squash: float = 1.0   (horizontal squash, >1 = wider)
        body_stretch: float = 1.0  (vertical stretch, >1 = taller)
        bounce: float = 0.0        (pixel offset upward)
        eye_scale: float = 1.0     (eye size multiplier, 0=closed)
        expression: str = "neutral"
        body_tint: tuple | None    (optional color override for mood)
    """

    def __init__(self):
        self.body_squash = 1.0
        self.body_stretch = 1.0
        self.bounce = 0.0
        self.eye_scale = 1.0
        self.expression = "neutral"
        self.body_tint = None
        self.stage = 0
        self._blink_timer = 0
        self._blinking = False
        self._blink_phase = 0  # 0=open, 1=closing, 2=closed, 3=opening

    def trigger_blink(self):
        if not self._blinking and self.eye_scale > 0.5:
            self._blinking = True
            self._blink_phase = 1
            self._blink_timer = 0

    def update(self, dt: float):
        if self._blinking:
            self._blink_timer += dt
            if self._blink_phase == 1:  # closing
                if self._blink_timer > 0.04:
                    self._blink_phase = 2
                    self._blink_timer = 0
            elif self._blink_phase == 2:  # closed
                if self._blink_timer > 0.08:
                    self._blink_phase = 3
                    self._blink_timer = 0
            elif self._blink_phase == 3:  # opening
                if self._blink_timer > 0.04:
                    self._blinking = False
                    self._blink_phase = 0

    @property
    def blink_progress(self) -> float:
        if not self._blinking:
            return 0.0
        if self._blink_phase == 1:
            return min(1.0, self._blink_timer / 0.04)
        elif self._blink_phase == 2:
            return 1.0
        elif self._blink_phase == 3:
            return 1.0 - min(1.0, self._blink_timer / 0.04)
        return 0.0

    def draw(self, surface: pygame.Surface):
        """Draw the slime centered in the given surface."""
        scale = STAGE_SCALES.get(self.stage, 1.0)
        cx = WINDOW_SIZE // 2
        cy = int(WINDOW_SIZE // 2 + 15 + self.bounce)

        # Ground shadow
        self._draw_shadow(surface, cx, cy, scale)

        # Body
        self._draw_body(surface, cx, cy, scale)

        # Face
        self._draw_face(surface, cx, cy, scale)

    def _draw_shadow(self, surf, cx, cy, scale):
        """Elliptical ground shadow under the slime."""
        shadow_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        sr_x = int(85 * scale * self.body_squash)
        sr_y = int(12 * scale * self.body_stretch)
        shadow_cy = int(cy + 68 * scale * self.body_stretch)
        if sr_x > 0 and sr_y > 0:
            gfx.filled_ellipse(shadow_surf, cx, shadow_cy, sr_x, sr_y,
                               (0, 0, 0, 35))
            gfx.aaellipse(shadow_surf, cx, shadow_cy, sr_x, sr_y,
                           (0, 0, 0, 20))
            surf.blit(shadow_surf, (0, 0))

    def _draw_body(self, surf, cx, cy, scale):
        """Draw the slime body — squishy ellipse with outline and highlight."""
        body_color = self.body_tint or P["body"]
        rx = int(90 * scale * self.body_squash)
        ry = int(68 * scale * self.body_stretch)

        body_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

        # Outline — slightly larger
        orx, ory = rx + 3, ry + 3
        gfx.filled_ellipse(body_surf, cx, cy, orx, ory, P["outline"])
        gfx.aaellipse(body_surf, cx, cy, orx, ory, P["outline"])

        # Body fill
        gfx.filled_ellipse(body_surf, cx, cy, rx, ry, body_color)
        gfx.aaellipse(body_surf, cx, cy, rx, ry, P["outline"])

        # Bottom shadow — darker gradient arc at bottom of body
        shadow_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        gfx.filled_ellipse(shadow_surf, cx, cy + ry // 2, rx - 5, ry // 2,
                           (*P["body_shadow"], 80))
        gfx.aaellipse(shadow_surf, cx, cy + ry // 2, rx - 5, ry // 2,
                       (*P["body_shadow"], 40))
        body_surf.blit(shadow_surf, (0, 0))

        # Top highlight — light crescent on upper-left
        hl_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        hlx = cx - rx // 3
        hly = cy - ry // 3
        hlrx = int(rx * 0.4)
        hlry = int(ry * 0.3)
        gfx.filled_ellipse(hl_surf, hlx, hly, hlrx, hlry,
                           (*P["body_light"], 140))
        gfx.aaellipse(hl_surf, hlx, hly, hlrx, hlry,
                       (*P["body_light"], 60))
        body_surf.blit(hl_surf, (0, 0))

        # Small secondary highlight
        hl2x = cx - rx // 4
        hl2y = cy - ry // 2
        hl2rx = int(rx * 0.15)
        hl2ry = int(ry * 0.12)
        gfx.filled_ellipse(body_surf, hl2x, hl2y, hl2rx, hl2ry,
                           (255, 255, 255, 90))
        gfx.aaellipse(body_surf, hl2x, hl2y, hl2rx, hl2ry,
                       (255, 255, 255, 40))

        surf.blit(body_surf, (0, 0))

    def _draw_face(self, surf, cx, cy, scale):
        """Draw eyes, blush, and mouth."""
        face_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

        eye_scale_s = max(0.0, self.eye_scale)
        blink = self.blink_progress

        # Eye positions
        eye_spacing = int(28 * scale)
        eye_y = cy - int(8 * scale)
        eye_r = int(16 * scale * eye_scale_s)

        left_eye = (cx - eye_spacing, eye_y)
        right_eye = (cx + eye_spacing, eye_y)

        # Draw eyes
        for ex, ey in (left_eye, right_eye):
            if blink >= 0.95:
                # Fully closed — horizontal line
                line_w = eye_r * 2
                pygame.draw.line(face_surf, P["outline"],
                                 (ex - line_w, ey), (ex + line_w, ey), max(2, int(3 * scale)))
            elif blink > 0.1:
                # Partially closed — squished vertically
                er_y = int(eye_r * (1 - blink))
                gfx.filled_ellipse(face_surf, ex, ey, eye_r, max(1, er_y), P["eye_white"])
                gfx.aaellipse(face_surf, ex, ey, eye_r, max(1, er_y), P["outline"])
                if er_y > 3:
                    pupil_r = int(eye_r * 0.55)
                    gfx.filled_circle(face_surf, ex, ey, pupil_r, P["eye_pupil"])
                    gfx.aacircle(face_surf, ex, ey, pupil_r, P["eye_pupil"])
            else:
                # Open eye
                gfx.filled_circle(face_surf, ex, ey, eye_r, P["eye_white"])
                gfx.aacircle(face_surf, ex, ey, eye_r, P["outline"])
                # Pupil
                pupil_r = int(eye_r * 0.55)
                pupil_ox = int(2 * scale)  # slight offset toward center
                gfx.filled_circle(face_surf, ex + pupil_ox, ey, pupil_r, P["eye_pupil"])
                gfx.aacircle(face_surf, ex + pupil_ox, ey, pupil_r, P["eye_pupil"])
                # Highlight dot
                hl_dot_r = max(2, int(4 * scale))
                gfx.filled_circle(face_surf, ex + pupil_ox + int(3 * scale),
                                  ey - int(4 * scale), hl_dot_r, P["eye_highlight"])
                gfx.aacircle(face_surf, ex + pupil_ox + int(3 * scale),
                              ey - int(4 * scale), hl_dot_r, P["eye_highlight"])

        # Blush
        blush_r = int(12 * scale)
        blush_alpha = 100
        blush_color = P["blush"]  # already has alpha
        for bx, by in ((cx - int(42 * scale), cy + int(2 * scale)),
                       (cx + int(42 * scale), cy + int(2 * scale))):
            gfx.filled_ellipse(face_surf, bx, by, blush_r, int(blush_r * 0.7),
                               (*P["blush"][:3], blush_alpha))
            gfx.aaellipse(face_surf, bx, by, blush_r, int(blush_r * 0.7),
                           (*P["blush"][:3], 40))

        # Mouth
        self._draw_mouth(face_surf, cx, cy + int(12 * scale), scale)

        surf.blit(face_surf, (0, 0))

    def _draw_mouth(self, surf, cx, cy, scale):
        """Draw the mouth based on expression."""
        mw = int(16 * scale)
        mh = int(8 * scale)

        if self.expression == "happy":
            # Wide smile arc:
            rect = pygame.Rect(cx - mw, cy - mh, mw * 2, mh * 2)
            pygame.draw.arc(surf, P["mouth"], rect, math.pi * 0.15, math.pi * 0.85,
                            max(2, int(3 * scale)))
        elif self.expression == "very_happy":
            # Open happy mouth — small dark oval
            gfx.filled_ellipse(surf, cx, cy + 2, mw // 2, mh, P["mouth"])
            gfx.aaellipse(surf, cx, cy + 2, mw // 2, mh, P["mouth"])
        elif self.expression == "sad":
            # Frown — upside-down arc
            rect = pygame.Rect(cx - mw, cy, mw * 2, mh * 2)
            pygame.draw.arc(surf, P["mouth"], rect, math.pi * 1.15, math.pi * 1.85,
                            max(2, int(3 * scale)))
        elif self.expression == "surprised":
            # Small 'o' mouth
            r = int(6 * scale)
            gfx.filled_circle(surf, cx, cy + 4, r, P["mouth"])
            gfx.aacircle(surf, cx, cy + 4, r, P["mouth"])
        elif self.expression == "eating":
            # Wide open mouth
            gfx.filled_ellipse(surf, cx, cy + 4, int(10 * scale), int(12 * scale),
                               P["mouth"])
            gfx.aaellipse(surf, cx, cy + 4, int(10 * scale), int(12 * scale),
                           P["mouth"])
        elif self.expression == "sleeping":
            # Small 'o' mouth — like snoring
            r = int(4 * scale)
            gfx.filled_circle(surf, cx, cy + 4, r, P["mouth"])
            gfx.aacircle(surf, cx, cy + 4, r, P["mouth"])
        else:
            # Neutral — subtle line
            pygame.draw.line(surf, P["mouth"],
                             (cx - mw // 2, cy), (cx + mw // 2, cy),
                             max(1, int(2 * scale)))

    def draw_crown(self, surf, cx, cy, scale):
        """Draw a tiny golden crown on top (adult stage)."""
        crown_y = cy - int(70 * scale * self.body_stretch)
        crx = int(14 * scale)
        cry = int(10 * scale)

        crown_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

        # Crown points — three triangles
        points = [
            (cx - crx, crown_y),  # left base
            (cx - crx // 2, crown_y - cry),  # left peak
            (cx, crown_y),  # center base
            (cx, crown_y - int(cry * 1.2)),  # center peak
            (cx + crx // 2, crown_y),  # right base
            (cx + crx // 2, crown_y - cry),  # right peak
            (cx + crx, crown_y),  # right base
        ]
        pygame.draw.polygon(crown_surf, P["crown"], points)
        gfx.aapolygon(crown_surf, points, P["crown_shadow"])

        # Small jewel on center peak
        gfx.filled_circle(crown_surf, cx, crown_y - int(cry * 1.2) + 3,
                          max(2, int(3 * scale)), (255, 100, 100))
        gfx.aacircle(crown_surf, cx, crown_y - int(cry * 1.2) + 3,
                      max(2, int(3 * scale)), (200, 50, 50))

        surf.blit(crown_surf, (0, 0))

    def draw_horns(self, surf, cx, cy, scale):
        """Draw tiny horns for teen/adult."""
        horn_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        horn_h = int(9 * scale)
        horn_w = int(4 * scale)
        horn_y = cy - int(68 * scale * self.body_stretch)

        for hx in (cx - int(30 * scale), cx + int(30 * scale)):
            gfx.filled_ellipse(horn_surf, hx, horn_y, horn_w, horn_h, P["outline"])
            gfx.aaellipse(horn_surf, hx, horn_y, horn_w, horn_h, P["outline"])
            # Lighter fill
            gfx.filled_ellipse(horn_surf, hx, horn_y + 1, max(1, horn_w - 1),
                               horn_h - 2, P["body_shadow"])

        surf.blit(horn_surf, (0, 0))
