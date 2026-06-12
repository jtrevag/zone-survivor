# Window / loop
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Stalker Survivor"

# Arena (play area — equals window for now; update if HUD insets the field)
ARENA_LEFT = 0
ARENA_TOP = 0
ARENA_RIGHT = WIDTH
ARENA_BOTTOM = HEIGHT

# Colors
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (30, 30, 30)
INDICATOR_COLOR = (200, 200, 200)

# Player
PLAYER_SPEED = 200        # px/s
PLAYER_RADIUS = 16
PLAYER_INDICATOR_LENGTH = 24  # direction line length
PLAYER_MAX_HP = 100
PLAYER_DAMAGE = 55
PLAYER_MAG_SIZE = 6
PLAYER_RELOAD_TIME = 1.2  # seconds
PLAYER_SHOT_COOLDOWN = 0.4  # seconds

# Mutant
MUTANT_COLOR = (180, 40, 40)
MUTANT_SIZE = 20
MUTANT_SPEED = 140        # px/s
MUTANT_MAX_HP = 25
MUTANT_CONTACT_DAMAGE = 15
MUTANT_CONTACT_COOLDOWN = 0.5  # seconds

HIT_FLASH_DURATION = 0.15   # seconds
HIT_FLASH_COLOR = (220, 40, 40)
HIT_FLASH_ALPHA_MAX = 100   # 0–255

SOUND_SAMPLE_RATE = 44100
SOUND_CHANNELS = 2
SOUND_BUFFER_SIZE = 512

# Wave difficulty base values (scaled per room by difficulty multiplier)
BASE_SPAWN_INTERVAL = 2.2   # seconds between spawns at difficulty 1.0
BASE_HP_MULT = 1.0           # enemy HP multiplier at difficulty 1.0
DEFAULT_MUTANT_RATIO = 0.4  # fallback when no room-level ratio is set

# Per-room mutant spawn ratio (randomised within this range each room)
ROOM_MUTANT_RATIO_MIN = 0.2
ROOM_MUTANT_RATIO_MAX = 0.8

# Room sequence for a full run (boss room added in Milestone 11)
ROOM_SEQUENCE = [
    {'type': 'survive',    'duration': 90,  'difficulty': 1.0},
    {'type': 'kill_count', 'target': 25,    'difficulty': 1.4},
    {'type': 'survive',    'duration': 60,  'difficulty': 1.8},
]

# Bullet
BULLET_SPEED = 500        # px/s
BULLET_RADIUS = 4
BULLET_COLOR = (255, 255, 0)  # yellow

# Bandit
BANDIT_COLOR = (60, 100, 220)
BANDIT_SIZE = 24
BANDIT_SPEED = 60
BANDIT_MAX_HP = 55
BANDIT_PREFERRED_RANGE = 250
BANDIT_RESUME_CHASE_RANGE = 300
BANDIT_PREFERRED_RANGE_SQ = BANDIT_PREFERRED_RANGE ** 2
BANDIT_RESUME_CHASE_RANGE_SQ = BANDIT_RESUME_CHASE_RANGE ** 2
BANDIT_FIRE_INTERVAL = 1.25
BANDIT_PROJECTILE_SPEED = 180
BANDIT_PROJECTILE_RADIUS = 3
BANDIT_PROJECTILE_COLOR = (255, 140, 0)
BANDIT_PROJECTILE_DAMAGE = 12

# XP orb
XP_ORB_RADIUS = 5
XP_ORB_COLOR = (50, 200, 50)
XP_ORB_LIFETIME = 10.0          # seconds before despawn
XP_ORB_PICKUP_RADIUS = 20
XP_ORB_PICKUP_RADIUS_SQ = XP_ORB_PICKUP_RADIUS ** 2

# Enemy XP values
MUTANT_XP_VALUE = 8
BANDIT_XP_VALUE = 15

# XP / leveling
XP_PER_LEVEL_BASE = 35          # xp_to_next = 35 * current_level

# Upgrade multipliers
UPGRADE_MAG_BONUS      = 2
UPGRADE_RELOAD_MULT    = 0.80   # -20% reload time
UPGRADE_DAMAGE_MULT    = 1.25   # +25% damage
UPGRADE_SPEED_MULT     = 1.10   # +10% speed
UPGRADE_HP_BONUS       = 20
UPGRADE_FIRE_RATE_MULT = 0.85   # -15% shot cooldown

# Upgrade definitions
UPGRADES = [
    {'id': 'mag',       'name': 'Larger Mag',    'desc': '+2 rounds'},
    {'id': 'reload',    'name': 'Faster Reload',  'desc': '-20% reload time'},
    {'id': 'damage',    'name': 'More Damage',    'desc': '+25% damage'},
    {'id': 'speed',     'name': 'Move Speed',     'desc': '+10% speed'},
    {'id': 'hp',        'name': 'Max HP',         'desc': '+20 HP'},
    {'id': 'fire_rate', 'name': 'Fire Rate',      'desc': '-15% shot cooldown'},
]

# HUD
HUD_FONT_SIZE = 24
HUD_FONT_SIZE_LARGE = 64
HUD_FONT_SIZE_SMALL = 18
HUD_BAR_WIDTH = 150
HUD_BAR_HEIGHT = 14
HUD_MARGIN = 12
HUD_COLOR_AMMO = (220, 220, 220)
HUD_COLOR_RELOAD_BG = (60, 60, 60)
HUD_COLOR_RELOAD_FILL = (200, 160, 40)
HUD_COLOR_HP_BG = (60, 60, 60)
HUD_COLOR_HP_FILL = (180, 40, 40)
HUD_COLOR_XP_BG = (30, 30, 80)
HUD_COLOR_XP_FILL = (80, 130, 255)
HUD_COLOR_CARD_BG = (40, 40, 60)
HUD_COLOR_CARD_BORDER = (80, 80, 120)
HUD_COLOR_CARD_HOVER = (160, 200, 255)
HUD_UPGRADE_CARD_W = 260
HUD_UPGRADE_CARD_H = 150
HUD_UPGRADE_CARD_GAP = 30
