"""Q-style vector slime renderer — rich layered rendering with gradients and gloss."""

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


# Stage-specific body base colors (without tint override)
STAGE_BODY_COLORS = {
    0: P.get("body_baby", (160, 230, 160)),
    1: P.get("body_child", (130, 215, 130)),
    2: P.get("body_teen", (100, 195, 110)),
    3: P.get("body_adult", (70, 170, 80)),
}

STAGE_SHADOW_COLORS = {
    0: (110, 180, 110),
    1: (90, 165, 90),
    2: (60, 140, 70),
    3: (40, 110, 50),
}

STAGE_HIGHLIGHT_COLORS = {
    0: (210, 250, 210),
    1: (190, 240, 190),
    2: (170, 230, 175),
    3: (140, 210, 150),
}


class VectorSlime:
    """Rich vector slime renderer with layered gradients, gloss, and expressions."""

    def __init__(self):
        self.body_squash = 1.0
        self.body_stretch = 1.0
        self.bounce = 0.0
        self.eye_scale = 1.0
        self.expression = "neutral"
        self.body_tint = None
        self.stage = 0

        # Blink state
        self._blink_timer = 0.0
        self._blinking = False
        self._blink_phase = 0  # 0=open, 1=closing, 2=closed, 3=opening

        # Eye tracking
        self._look_x = 0.0
        self._look_y = 0.0
        self._target_look_x = 0.0
        self._target_look_y = 0.0

        # Idle breathing phase
        self._breath_phase = 0.0

        # Dizzy phase
        self._dizzy_phase = 0.0

    def set_look_target(self, sx: float, sy: float):
        """Set where the eyes should look (in local window coords, center=0,0)."""
        dist = math.hypot(sx, sy)
        max_dist = 60.0
        if dist > 0:
            clamped = min(dist, max_dist) / dist
            self._target_look_x = sx * clamped / max_dist
            self._target_look_y = sy * clamped / max_dist

    def trigger_blink(self):
        if not self._blinking and self.eye_scale > 0.5:
            self._blinking = True
            self._blink_phase = 1
            self._blink_timer = 0.0

    def update(self, dt: float):
        # Blink state machine
        if self._blinking:
            self._blink_timer += dt
            if self._blink_phase == 1:  # closing
                if self._blink_timer > 0.04:
                    self._blink_phase = 2
                    self._blink_timer = 0.0
            elif self._blink_phase == 2:  # closed
                if self._blink_timer > 0.08:
                    self._blink_phase = 3
                    self._blink_timer = 0.0
            elif self._blink_phase == 3:  # opening
                if self._blink_timer > 0.04:
                    self._blinking = False
                    self._blink_phase = 0

        # Smooth eye tracking lerp
        self._look_x += (self._target_look_x - self._look_x) * min(1.0, dt * 8.0)
        self._look_y += (self._target_look_y - self._look_y) * min(1.0, dt * 8.0)

        # Breathing phase for idle
        self._breath_phase += dt * 1.5

        # Dizzy phase
        self._dizzy_phase += dt * 8.0

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

    # ── body colors accounting for tint and stage ──

    def _body_color(self):
        if self.body_tint:
            return self.body_tint
        return STAGE_BODY_COLORS.get(self.stage, P["body"])

    def _shadow_color(self):
        if self.body_tint:
            r, g, b = self.body_tint
            return (max(0, r - 40), max(0, g - 40), max(0, b - 40))
        return STAGE_SHADOW_COLORS.get(self.stage, P["body_shadow"])

    def _highlight_color(self):
        if self.body_tint:
            r, g, b = self.body_tint
            return (min(255, r + 50), min(255, g + 50), min(255, b + 50))
        return STAGE_HIGHLIGHT_COLORS.get(self.stage, P["body_light"])

    # ── main draw ──

    def draw(self, surface: pygame.Surface):
        scale = STAGE_SCALES.get(self.stage, 1.0)
        cx = WINDOW_SIZE // 2
        cy = int(WINDOW_SIZE // 2 + 15 + self.bounce)

        self._draw_shadow(surface, cx, cy, scale)
        self._draw_glow(surface, cx, cy, scale)
        self._draw_body(surface, cx, cy, scale)
        self._draw_face(surface, cx, cy, scale)

    # ── ground shadow ──

    def _draw_shadow(self, surf, cx, cy, scale):
        shadow_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        sr_x = int(88 * scale * self.body_squash)
        sr_y = int(14 * scale * self.body_stretch)
        shadow_cy = int(cy + 70 * scale * self.body_stretch)
        if sr_x > 0 and sr_y > 0:
            for i in range(3):
                r = 3 - i
                alpha = 25 - i * 7
                gfx.filled_ellipse(shadow_surf, cx, shadow_cy, sr_x + r * 4, sr_y + r,
                                   (0, 0, 0, alpha))
            surf.blit(shadow_surf, (0, 0))

    # ── rim light glow ──

    def _draw_glow(self, surf, cx, cy, scale):
        rx = int(92 * scale * self.body_squash)
        ry = int(70 * scale * self.body_stretch)
        glow_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        body_c = self._body_color()
        glow_color = (body_c[0], body_c[1], body_c[2], 30)
        for i in range(3):
            gfx.filled_ellipse(glow_surf, cx, cy, rx + 6 + i * 3, ry + 6 + i * 3, glow_color)
        surf.blit(glow_surf, (0, 0))

    # ── layered body ──

    def _draw_body(self, surf, cx, cy, scale):
        body_color = self._body_color()
        shadow_color = self._shadow_color()
        highlight_color = self._highlight_color()

        rx = int(90 * scale * self.body_squash)
        ry = int(68 * scale * self.body_stretch)

        body_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

        # ── outline ──
        outline_rx, outline_ry = rx + 3, ry + 3
        gfx.filled_ellipse(body_surf, cx, cy, outline_rx, outline_ry, P["outline"])
        gfx.aaellipse(body_surf, cx, cy, outline_rx, outline_ry, P["outline"])

        # ── layer 0: base fill ──
        gfx.filled_ellipse(body_surf, cx, cy, rx, ry, body_color)

        # ── layer 1: center bright area (gradient core) ──
        core_rx = int(rx * 0.72)
        core_ry = int(ry * 0.72)
        core_color = self._lerp_color(body_color, (255, 255, 255), 0.35)
        gfx.filled_ellipse(body_surf, cx - int(rx * 0.05), cy - int(ry * 0.08),
                           core_rx, core_ry, (*core_color, 130))
        gfx.aaellipse(body_surf, cx - int(rx * 0.05), cy - int(ry * 0.08),
                      core_rx, core_ry, (*core_color, 50))

        # ── layer 2: inner bright spot ──
        inner_rx = int(rx * 0.38)
        inner_ry = int(ry * 0.38)
        inner_color = self._lerp_color(body_color, (255, 255, 255), 0.55)
        gfx.filled_ellipse(body_surf, cx - int(rx * 0.1), cy - int(ry * 0.2),
                           inner_rx, inner_ry, (*inner_color, 120))
        gfx.aaellipse(body_surf, cx - int(rx * 0.1), cy - int(ry * 0.2),
                      inner_rx, inner_ry, (*inner_color, 40))

        # ── layer 3: bottom shadow (dark gradient at bottom) ──
        bot_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        for i in range(4):
            bot_y = cy + ry // 2 - i * 2
            bot_rx = rx - 6 - i
            bot_ry = ry // 2 - i
            alpha = 50 - i * 10
            if bot_rx > 0 and bot_ry > 0:
                gfx.filled_ellipse(bot_surf, cx, bot_y, bot_rx, bot_ry,
                                   (*shadow_color, alpha))
        body_surf.blit(bot_surf, (0, 0))

        # ── layer 4: specular highlight (glossy reflection) ──
        spec_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        spec_rx = int(rx * 0.28)
        spec_ry = int(ry * 0.18)
        spec_x = cx - int(rx * 0.32)
        spec_y = cy - int(ry * 0.38)
        # Main specular
        gfx.filled_ellipse(spec_surf, spec_x, spec_y, spec_rx, spec_ry,
                           (255, 255, 255, 170))
        gfx.aaellipse(spec_surf, spec_x, spec_y, spec_rx, spec_ry,
                      (255, 255, 255, 60))
        # Secondary smaller specular
        spec2_rx = int(spec_rx * 0.5)
        spec2_ry = int(spec_ry * 0.5)
        spec2_x = spec_x + int(spec_rx * 0.7)
        spec2_y = spec_y + int(spec_ry * 0.4)
        gfx.filled_ellipse(spec_surf, spec2_x, spec2_y, spec2_rx, spec2_ry,
                           (255, 255, 255, 120))
        body_surf.blit(spec_surf, (0, 0))

        # ── layer 5: top crescent highlight ──
        top_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        hl_rx = int(rx * 0.45)
        hl_ry = int(ry * 0.22)
        hl_x = cx - int(rx * 0.15)
        hl_y = cy - int(ry * 0.42)
        gfx.filled_ellipse(top_surf, hl_x, hl_y, hl_rx, hl_ry,
                           (*highlight_color, 100))
        gfx.aaellipse(top_surf, hl_x, hl_y, hl_rx, hl_ry,
                      (*highlight_color, 35))
        body_surf.blit(top_surf, (0, 0))

        # ── inner outline (subtle) ──
        gfx.aaellipse(body_surf, cx, cy, rx - 1, ry - 1,
                      (*P["outline"], 50))

        # ── teen/adult body texture details ──
        if self.stage >= 2:
            self._draw_body_texture(body_surf, cx, cy, rx, ry, scale)

        surf.blit(body_surf, (0, 0))

    def _draw_body_texture(self, surf, cx, cy, rx, ry, scale):
        """Subtle body details for teen/adult stages."""
        tex_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        # Subtle side markings
        for side in (-1, 1):
            mx = cx + side * int(rx * 0.6)
            my = cy + int(ry * 0.1)
            mrx = int(rx * 0.12)
            mry = int(ry * 0.25)
            gfx.filled_ellipse(tex_surf, mx, my, mrx, mry,
                               (*P["outline"], 25))
        surf.blit(tex_surf, (0, 0))

    # ── face ──

    def _draw_face(self, surf, cx, cy, scale):
        face_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

        eye_scale_s = max(0.0, self.eye_scale)
        blink = self.blink_progress
        expression = self.expression

        # Eye positions
        eye_spacing = int(28 * scale)
        eye_y = cy - int(8 * scale)
        eye_r = int(16 * scale * eye_scale_s)

        # Look offsets (clamped)
        max_look = int(5 * scale)
        lx = int(self._look_x * max_look)
        ly = int(self._look_y * max_look * 0.6)

        left_eye = (cx - eye_spacing + lx, eye_y + ly)
        right_eye = (cx + eye_spacing + lx, eye_y + ly)

        # ── blush first (behind eyes) ──
        self._draw_blush(face_surf, cx, cy, scale)

        # ── eyes ──
        if expression == "dizzy":
            self._draw_dizzy_eyes(face_surf, left_eye, right_eye, eye_r, scale)
        elif expression == "loving":
            self._draw_heart_eyes(face_surf, left_eye, right_eye, eye_r, scale)
        else:
            for ex, ey in (left_eye, right_eye):
                self._draw_eye(face_surf, ex, ey, eye_r, blink, scale, expression)

        # ── mouth ──
        self._draw_mouth(face_surf, cx, cy + int(12 * scale), scale)

        # ── eyebrows for some expressions ──
        if expression in ("sad", "mischievous", "curious"):
            self._draw_eyebrows(face_surf, left_eye, right_eye, eye_r, scale, expression)

        surf.blit(face_surf, (0, 0))

    # ── blush ──

    def _draw_blush(self, surf, cx, cy, scale):
        blush_r = int(14 * scale)
        blush_ry = int(blush_r * 0.65)
        blush_alpha = 90
        blush_color = P["blush"]  # (255, 150, 150, 120)
        r, g, b = blush_color[:3]
        for bx, by in ((cx - int(43 * scale), cy + int(4 * scale)),
                       (cx + int(43 * scale), cy + int(4 * scale))):
            # Soft layered blush
            for i in range(2):
                br = blush_r + i * 3
                bry = blush_ry + i * 2
                alpha = blush_alpha - i * 20
                gfx.filled_ellipse(surf, bx, by, br, bry, (r, g, b, alpha))
                gfx.aaellipse(surf, bx, by, br, bry, (r, g, b, alpha // 2))

    # ── eyes ──

    def _draw_eye(self, surf, ex, ey, eye_r, blink, scale, expression):
        if blink >= 0.95:
            # Fully closed — horizontal curve
            line_w = max(4, int(eye_r * 1.6))
            line_h = max(2, int(3 * scale))
            # Draw an upward-curving closed eye
            pts = [
                (ex - line_w // 2, ey),
                (ex - line_w // 4, ey - line_h),
                (ex + line_w // 4, ey - line_h),
                (ex + line_w // 2, ey),
            ]
            pygame.draw.lines(surf, P["outline"], False, pts, max(2, int(2.5 * scale)))
        elif blink > 0.1:
            # Partially closed
            er_y = max(1, int(eye_r * (1 - blink)))
            self._draw_open_eye(surf, ex, ey, eye_r, er_y, scale, expression)
        else:
            self._draw_open_eye(surf, ex, ey, eye_r, eye_r, scale, expression)

    def _draw_open_eye(self, surf, ex, ey, eye_r, er_y, scale, expression):
        """Draw a fully or partially open eye with iris, pupil, and highlight."""
        # White
        gfx.filled_ellipse(surf, ex, ey, eye_r, er_y, P["eye_white"])
        gfx.aaellipse(surf, ex, ey, eye_r, er_y, P["outline"])

        if er_y < 4:
            return

        # Iris (colored ring)
        iris_r = int(eye_r * 0.7)
        iris_color = (70, 160, 70)
        if expression == "excited":
            iris_color = (220, 180, 40)  # golden eyes when excited
        elif expression == "surprised":
            iris_r = int(eye_r * 0.55)  # smaller iris when surprised
        gfx.filled_circle(surf, ex, ey, iris_r, iris_color)
        gfx.aacircle(surf, ex, ey, iris_r, (*iris_color, 150))

        # Pupil
        pupil_r = max(2, int(iris_r * 0.6))
        pupil_ox = int(2 * scale)  # slight inward offset
        gfx.filled_circle(surf, ex + pupil_ox, ey, pupil_r, P["eye_pupil"])
        gfx.aacircle(surf, ex + pupil_ox, ey, pupil_r, P["eye_pupil"])

        # Primary highlight dot
        hl_r = max(2, int(4 * scale))
        hl_x = ex + pupil_ox + int(3 * scale)
        hl_y = ey - int(4 * scale)
        gfx.filled_circle(surf, hl_x, hl_y, hl_r, P["eye_highlight"])
        gfx.aacircle(surf, hl_x, hl_y, hl_r, P["eye_highlight"])

        # Secondary smaller highlight
        hl2_r = max(1, int(1.5 * scale))
        gfx.filled_circle(surf, hl_x + int(4 * scale), hl_y + int(3 * scale),
                          hl2_r, (255, 255, 255, 180))

    def _draw_dizzy_eyes(self, surf, left, right, eye_r, scale):
        """Swirly dizzy eyes."""
        for ex, ey in (left, right):
            # Draw spiral effect
            for i in range(3):
                r = int(eye_r * (1 - i * 0.3))
                angle_offset = self._dizzy_phase + i * 1.2
                gfx.aacircle(surf, ex, ey, r, P["outline"])
            # X_X cross pupils
            cx_r = int(eye_r * 0.5)
            pygame.draw.line(surf, P["outline"],
                             (ex - cx_r, ey - cx_r), (ex + cx_r, ey + cx_r), 2)
            pygame.draw.line(surf, P["outline"],
                             (ex - cx_r, ey + cx_r), (ex + cx_r, ey - cx_r), 2)

    def _draw_heart_eyes(self, surf, left, right, eye_r, scale):
        """Heart-shaped eyes for loving expression."""
        for ex, ey in (left, right):
            # Simplified heart: two overlapping circles + triangle
            hr = int(eye_r * 0.45)
            gfx.filled_circle(surf, ex - hr, ey - hr // 2, hr, (255, 80, 100))
            gfx.filled_circle(surf, ex + hr, ey - hr // 2, hr, (255, 80, 100))
            # Bottom triangle
            tri_pts = [
                (ex - int(hr * 1.9), ey),
                (ex + int(hr * 1.9), ey),
                (ex, ey + int(hr * 1.6)),
            ]
            pygame.draw.polygon(surf, (255, 80, 100), tri_pts)
            gfx.aapolygon(surf, tri_pts, (200, 40, 60))
            # Highlight
            gfx.filled_circle(surf, ex - hr, ey - hr // 2 - 1,
                              max(1, hr // 3), (255, 200, 200))

    # ── eyebrows ──

    def _draw_eyebrows(self, surf, left, right, eye_r, scale, expr):
        bw = int(eye_r * 1.1)
        bh = max(1, int(2 * scale))

        for ex, ey in (left, right):
            by = ey - int(eye_r * 1.3)
            if expr == "sad":
                # Angled up toward center:  /
                pts = [(ex - bw, by + bh), (ex + bw, by - bh)]
            elif expr == "mischievous":
                # One up one down
                if ex < WINDOW_SIZE // 2:
                    pts = [(ex - bw, by - bh), (ex + bw, by - bh)]  # flat
                else:
                    pts = [(ex - bw, by - bh), (ex + bw, by + bh)]  # angled
            elif expr == "curious":
                # Raised
                pts = [(ex - bw, by + bh), (ex + bw, by - bh)]
            else:
                continue
            pygame.draw.line(surf, P["outline"], pts[0], pts[1], bh + 1)

    # ── mouth ──

    def _draw_mouth(self, surf, cx, cy, scale):
        expr = self.expression
        mw = int(18 * scale)

        if expr == "happy":
            mh = int(12 * scale)
            rect = pygame.Rect(cx - mw, cy - mh, mw * 2, mh * 2)
            pygame.draw.arc(surf, P["mouth"], rect, math.pi * 0.12, math.pi * 0.88,
                            max(2, int(3 * scale)))
        elif expr == "very_happy":
            # Open happy mouth with tongue
            mh = int(10 * scale)
            gfx.filled_ellipse(surf, cx, cy + 1, mw // 2, mh, P["mouth"])
            gfx.aaellipse(surf, cx, cy + 1, mw // 2, mh, P["mouth"])
            # Tongue
            tongue_w = int(mw * 0.4)
            tongue_h = int(mh * 0.6)
            gfx.filled_ellipse(surf, cx, cy + mh // 2, tongue_w, tongue_h,
                               (255, 120, 120, 180))
        elif expr == "sad":
            mh = int(12 * scale)
            rect = pygame.Rect(cx - mw, cy - mh, mw * 2, mh * 2)
            pygame.draw.arc(surf, P["mouth"], rect, math.pi * 1.12, math.pi * 1.88,
                            max(2, int(3 * scale)))
        elif expr == "surprised":
            r = int(8 * scale)
            gfx.filled_circle(surf, cx, cy + 2, r, P["mouth_dark"])
            gfx.aacircle(surf, cx, cy + 2, r, P["outline"])
            # Inner highlight
            gfx.filled_circle(surf, cx, cy + 2, max(1, r // 2),
                              (60, 30, 30, 120))
        elif expr == "eating":
            # Wide open chomping mouth
            gfx.filled_ellipse(surf, cx, cy + 2, int(14 * scale), int(14 * scale),
                               P["mouth_dark"])
            gfx.aaellipse(surf, cx, cy + 2, int(14 * scale), int(14 * scale),
                           P["outline"])
        elif expr == "sleeping":
            r = int(5 * scale)
            gfx.filled_circle(surf, cx, cy + 3, r, P["mouth"])
            gfx.aacircle(surf, cx, cy + 3, r, P["mouth"])
        elif expr == "mischievous":
            # Lopsided smirk
            mh = int(8 * scale)
            end_x = cx + mw
            end_y = cy - mh // 2
            ctrl_x = cx + mw // 2
            ctrl_y = cy + mh
            # Approximate with arc
            rect = pygame.Rect(cx - mw // 2, cy - mh, mw, mh * 2)
            pygame.draw.arc(surf, P["mouth"], rect,
                            math.pi * 0.05, math.pi * 0.55,
                            max(2, int(2.5 * scale)))
        elif expr == "excited":
            # Wide W-shaped excited mouth
            mw_w = int(14 * scale)
            mh_w = int(7 * scale)
            pts = [
                (cx - mw_w, cy),
                (cx - mw_w // 2, cy - mh_w),
                (cx, cy),
                (cx + mw_w // 2, cy - mh_w),
                (cx + mw_w, cy),
            ]
            pygame.draw.lines(surf, P["mouth"], False, pts, max(2, int(2.5 * scale)))
        elif expr == "curious":
            # Small 'o' shape
            r = int(5 * scale)
            gfx.filled_ellipse(surf, cx, cy + 1, r, int(r * 0.8), P["mouth"])
            gfx.aaellipse(surf, cx, cy + 1, r, int(r * 0.8), P["mouth"])
        else:
            # Neutral — gentle curve
            pygame.draw.line(surf, P["mouth"],
                             (cx - mw // 2, cy), (cx + mw // 2, cy),
                             max(1, int(2 * scale)))

    # ── crown (adult) ──

    def draw_crown(self, surf, cx, cy, scale):
        crown_y = cy - int(70 * scale * self.body_stretch)
        crx = int(16 * scale)
        cry = int(12 * scale)

        crown_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

        # Crown base
        base_rect = pygame.Rect(cx - crx, crown_y, crx * 2, cry)
        pygame.draw.rect(crown_surf, P["crown"], base_rect)
        pygame.draw.rect(crown_surf, P["crown_shadow"], base_rect, 1)

        # Crown points — three peaks with jewels
        points = [
            (cx - crx, crown_y),
            (cx - crx // 2, crown_y - cry),
            (cx, crown_y),
            (cx, crown_y - int(cry * 1.3)),
            (cx + crx // 2, crown_y),
            (cx + crx // 2, crown_y - cry),
            (cx + crx, crown_y),
        ]
        pygame.draw.polygon(crown_surf, P["crown"], points)
        gfx.aapolygon(crown_surf, points, P["crown_shadow"])

        # Jewels on peaks
        jewel_colors = [(255, 80, 80), (80, 180, 255), (255, 80, 80)]
        jewel_positions = [
            (cx - crx // 2, crown_y - cry // 2),
            (cx, crown_y - int(cry * 0.65)),
            (cx + crx // 2, crown_y - cry // 2),
        ]
        for (jx, jy), jc in zip(jewel_positions, jewel_colors):
            gfx.filled_circle(crown_surf, jx, jy + 3, max(2, int(3 * scale)), jc)
            gfx.aacircle(crown_surf, jx, jy + 3, max(2, int(3 * scale)), (*jc[:3], 180))
            # Sparkle on jewel
            gfx.filled_circle(crown_surf, jx - 1, jy + 2,
                              max(1, int(1.5 * scale)), (255, 255, 255, 200))

        surf.blit(crown_surf, (0, 0))

    # ── horns (teen/adult) ──

    def draw_horns(self, surf, cx, cy, scale):
        horn_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        horn_y = cy - int(68 * scale * self.body_stretch)

        size_mult = 1.0 if self.stage < 3 else 1.4
        horn_h = int(10 * scale * size_mult)
        horn_w = int(5 * scale * size_mult)

        for hx in (cx - int(32 * scale), cx + int(32 * scale)):
            # Outer shape
            gfx.filled_ellipse(horn_surf, hx, horn_y - horn_h // 2, horn_w, horn_h,
                               P["outline"])
            gfx.aaellipse(horn_surf, hx, horn_y - horn_h // 2, horn_w, horn_h,
                           P["outline"])
            # Inner fill
            inner_w = max(1, horn_w - 1)
            inner_h = horn_h - 2
            horn_color = self._highlight_color()
            gfx.filled_ellipse(horn_surf, hx, horn_y - horn_h // 2 + 1,
                               inner_w, inner_h, horn_color)
            # Highlight on horn
            gfx.filled_ellipse(horn_surf, hx - 1, horn_y - horn_h // 2,
                               max(1, inner_w // 2), max(1, inner_h // 3),
                               (255, 255, 255, 80))

        surf.blit(horn_surf, (0, 0))

    # ── utility ──

    @staticmethod
    def _lerp_color(c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
