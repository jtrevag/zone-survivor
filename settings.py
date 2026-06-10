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
PLAYER_DAMAGE = 40
PLAYER_MAG_SIZE = 5
PLAYER_RELOAD_TIME = 2.0  # seconds
PLAYER_SHOT_COOLDOWN = 0.4  # seconds

# Mutant
MUTANT_COLOR = (180, 40, 40)
MUTANT_SIZE = 20
MUTANT_SPEED = 140        # px/s
MUTANT_MAX_HP = 35
MUTANT_CONTACT_DAMAGE = 15
MUTANT_CONTACT_COOLDOWN = 0.5  # seconds

# Spawner
SPAWN_INTERVAL = 3.0      # seconds (wave 0-1 rate)

# Bullet
BULLET_SPEED = 500        # px/s
BULLET_RADIUS = 4
BULLET_COLOR = (255, 255, 0)  # yellow

# Bandit
BANDIT_COLOR = (60, 100, 220)
BANDIT_SIZE = 24
BANDIT_SPEED = 60
BANDIT_MAX_HP = 80
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
MUTANT_XP_VALUE = 5
BANDIT_XP_VALUE = 10

# XP / leveling
XP_PER_LEVEL_BASE = 50          # xp_to_next = 50 * current_level

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
