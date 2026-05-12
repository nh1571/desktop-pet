"""All constants for the desktop pet."""

# Window
WINDOW_SIZE = 256
DEFAULT_OPACITY = 0.95
TARGET_FPS = 30

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

# Growth stage scale factors
STAGE_SCALES = {0: 0.65, 1: 0.80, 2: 0.95, 3: 1.0}

# Save
SAVE_DIR = "~/.desktop_pet"
SAVE_FILE = "save.json"
AUTOSAVE_INTERVAL = 300  # seconds

# Vector palette — soft, cute, modern
VECTOR_PALETTE = {
    "body":          (120, 210, 120),   # soft grass green
    "body_shadow":   (80, 170, 80),     # shadow side
    "body_light":    (170, 240, 170),   # highlight
    "outline":       (40, 100, 40),     # dark green outline
    "eye_white":     (255, 255, 255),   # eye white
    "eye_pupil":     (30, 30, 30),      # pupil
    "eye_highlight": (255, 255, 255),   # eye specular
    "blush":         (255, 150, 150, 120),  # blush with alpha
    "mouth":         (50, 100, 50),     # mouth line
    "crown":         (255, 215, 0),     # gold crown
    "crown_shadow":  (200, 160, 0),     # crown dark
    "sparkle":       (255, 230, 100),   # sparkle particles
    "tear":          (100, 150, 220),   # tear drops
    "bg":            (240, 255, 240),   # background tint
    "ground_shadow": (0, 0, 0, 30),     # ground shadow (low alpha)
}
