"""Pygame-native right-click context menu. No tkinter dependency."""

import pygame
import pygame.gfxdraw as gfx


MENU_FONT: pygame.font.Font | None = None


def _get_font():
    global MENU_FONT
    if MENU_FONT is None:
        MENU_FONT = pygame.font.Font(None, 16)
    return MENU_FONT


def show_menu(screen_pos: tuple[int, int], callback, screen: pygame.Surface):
    """Show a pygame-native context menu and block until selection or dismiss.

    Returns the selected action string, or None if dismissed.
    """
    font = _get_font()
    items = [
        ("Feed", "feed"),
        ("Play", "play"),
        ("Talk", "talk"),
        ("---", None),
        ("Sleep", "sleep"),
        ("Status", "status"),
        ("---", None),
        ("Toggle Always-on-Top", "toggle_top"),
        ("Mute / Unmute", "toggle_mute"),
        ("---", None),
        ("Quit", "quit"),
    ]

    # Measure menu
    item_h = 22
    pad_x = 14
    pad_y = 8
    max_w = max(font.render(label, True, (0, 0, 0)).get_width()
                for label, _ in items if label != "---")
    sep_h = 6
    total_h = sum(item_h if label != "---" else sep_h for label, _ in items) + pad_y * 2
    menu_w = max_w + pad_x * 2

    # Create menu surface
    menu_surf = pygame.Surface((menu_w, total_h), pygame.SRCALPHA)
    bg = (255, 255, 255, 245)
    outline = (180, 200, 180, 220)
    menu_surf.fill(bg)
    pygame.draw.rect(menu_surf, outline, menu_surf.get_rect(), 1)

    # Draw items
    menu_items = []  # (rect, action)
    y = pad_y
    for label, action in items:
        if label == "---":
            pygame.draw.line(menu_surf, (200, 200, 200, 150),
                             (pad_x, y + 2), (menu_w - pad_x, y + 2), 1)
            y += sep_h
        else:
            text = font.render(label, True, (40, 40, 40))
            menu_surf.blit(text, (pad_x, y + 3))
            menu_items.append((pygame.Rect(0, y, menu_w, item_h), action))
            y += item_h

    # Position menu at click point
    menu_x, menu_y = screen_pos

    # Show menu inline: draw it on screen, wait for click
    clock = pygame.time.Clock()
    selected = None

    while selected is None:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                rx = mx - menu_x
                ry = my - menu_y
                for rect, action in menu_items:
                    if rect.collidepoint(rx, ry):
                        selected = action
                        break
                # Click outside menu = dismiss
                if selected is None:
                    # Check if click was on menu at all
                    menu_rect = pygame.Rect(menu_x, menu_y, menu_w, total_h)
                    if not menu_rect.collidepoint(mx, my):
                        selected = ""  # dismiss
            elif event.type == pygame.QUIT:
                selected = ""

        # Redraw menu with hover effect
        mx, my = pygame.mouse.get_pos()
        rx, ry = mx - menu_x, my - menu_y

        # Re-draw items with hover
        y = pad_y
        item_idx = 0
        for label, action in items:
            if label == "---":
                y += sep_h
            else:
                rect = pygame.Rect(0, y, menu_w, item_h)
                if rect.collidepoint(rx, ry):
                    # Hover highlight
                    highlight = pygame.Surface((menu_w, item_h), pygame.SRCALPHA)
                    highlight.fill((100, 180, 100, 60))
                    menu_surf.blit(highlight, (0, y))
                    text = font.render(label, True, (20, 60, 20))
                    menu_surf.blit(text, (pad_x, y + 3))
                else:
                    # Reset to normal
                    menu_surf.fill(bg, rect)
                    text = font.render(label, True, (40, 40, 40))
                    menu_surf.blit(text, (pad_x, y + 3))
                item_idx += 1
                y += item_h

        # Draw menu onto screen
        screen.blit(menu_surf, (menu_x, menu_y))
        pygame.display.flip()
        clock.tick(30)

    if selected and selected != "":
        callback(selected)
