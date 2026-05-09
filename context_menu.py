"""Right-click context menu using tkinter popup.

Creates and destroys a throwaway tkinter root for each invocation
to avoid event-loop conflicts with pygame's SDL main loop.
"""

import tkinter as tk


def show_menu(screen_pos: tuple[int, int], callback):
    """Show context menu at the given screen coordinates.

    callback(action_name: str) is called when a menu item is selected.
    """
    mx, my = screen_pos

    root = tk.Tk()
    root.withdraw()
    root.attributes('-alpha', 0.0)

    # Calculate screen position
    root.update_idletasks()
    try:
        screen_x = root.winfo_pointerx()
        screen_y = root.winfo_pointery()
    except Exception:
        screen_x, screen_y = mx + 100, my + 100

    menu = tk.Menu(root, tearoff=0, font=('Monaco', 11))

    def select(action):
        try:
            root.destroy()
        except tk.TclError:
            pass
        callback(action)

    menu.add_command(label='Feed (+30)',
                     command=lambda: select('feed'))
    menu.add_command(label='Play (+30)',
                     command=lambda: select('play'))
    menu.add_command(label='Talk',
                     command=lambda: select('talk'))
    menu.add_separator()
    menu.add_command(label='Sleep',
                     command=lambda: select('sleep'))
    menu.add_command(label='Status',
                     command=lambda: select('status'))
    menu.add_separator()
    menu.add_command(label='Toggle Always-on-Top',
                     command=lambda: select('toggle_top'))
    menu.add_separator()
    menu.add_command(label='Quit',
                     command=lambda: select('quit'))

    try:
        menu.tk_popup(screen_x, screen_y)
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass
