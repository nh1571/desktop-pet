"""All constants for the desktop pet."""

# Window
WINDOW_SIZE = 160
SPRITE_PIXEL_SIZE = 16
SPRITE_SCALE = 10  # 16 * 10 = 160
DEFAULT_OPACITY = 0.9
TARGET_FPS = 12

# Palette: index -> (R, G, B)
# 0 = transparent (magenta key), never drawn
PALETTE = {
    0: (255, 0, 255),
    1: (15, 15, 15),       # black / outline
    2: (50, 205, 50),       # main slime green
    3: (34, 139, 34),       # dark green (shade)
    4: (144, 238, 144),     # light green (highlight)
    5: (255, 255, 255),     # white (eyes)
    6: (255, 100, 100),     # red (blush)
    7: (255, 215, 0),       # gold (sparkle)
    8: (139, 90, 43),       # brown (accessories)
    9: (100, 100, 220),     # blue (water drop)
}

# Needs
HUNGER_DECAY_PER_HOUR = 3.0
HAPPINESS_DECAY_PER_HOUR = 2.0
ENERGY_DECAY_PER_HOUR = 2.5
MAX_NEED = 100
HUNGRY_THRESHOLD = 30
STARVING_THRESHOLD = 10
TIRED_THRESHOLD = 25
SAD_THRESHOLD = 20

# Growth stages (playtime in minutes)
STAGE_BABY = 0
STAGE_CHILD = 120
STAGE_TEEN = 480
STAGE_ADULT = 1440
STAGE_NAMES = {0: "Baby", 1: "Child", 2: "Teen", 3: "Adult"}

# Save
SAVE_DIR = "~/.desktop_pet"
SAVE_FILE = "save.json"
AUTOSAVE_INTERVAL = 300  # seconds

# ASCII sprite char map
CHAR_MAP = {
    '#': 2,  # main green
    '%': 3,  # dark green
    '.': 4,  # light green / highlight
    '@': 1,  # black / outline
    '*': 5,  # white
    '~': 6,  # red
    '+': 7,  # gold
    '=': 8,  # brown
    '^': 9,  # blue
    ' ': 0,  # transparent
}
