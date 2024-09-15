import tomllib

# Load the TOML file
with open('settings.toml', 'rb') as f:
    data = tomllib.load(f)

# Load game settings
game = data['game']
TILE_SIZE = game['tile_size']
GRID_WIDTH = game['grid_width']
GRID_HEIGHT = game['grid_height']
HUD_HEIGHT = game['hud_height']
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT + HUD_HEIGHT
PRECISION = game['precision']
TOLERANCE = game['tolerance']
PLAYER_LIVES = game['player_lives']
EXPLOSION_DURATION = game['explosion_duration']
BOMB_EXPLOSION_RANGE = game['bomb_explosion_range']

# Load colors
colors = data['colors']
BACKGROUND_COLOR = tuple(colors['background_color'])
GRID_COLOR = tuple(colors['grid_color'])
BREAKABLE_COLOR = tuple(colors['breakable_color'])
BREAKING_COLOR = tuple(colors['breaking_color'])
BOMB_COLOR = tuple(colors['bomb_color'])
OBSTACLE_COLOR = tuple(colors['obstacle_color'])
PLAYER_COLOR = tuple(colors['player_color'])
PLAYER_2_COLOR = tuple(colors['player_2_color'])
HUD_COLOR = tuple(colors['hud_color'])
EXPLOSION_GREEN_COLOR = tuple(colors['explosion_green_color'])
EXPLOSION_YELLOW_COLOR = tuple(colors['explosion_yellow_color'])

# __all__ to help LSP tools recognize exported variables
__all__ = [
    'TILE_SIZE', 'GRID_WIDTH', 'GRID_HEIGHT', 'HUD_HEIGHT', 'SCREEN_WIDTH', 'SCREEN_HEIGHT',
    'PRECISION', 'TOLERANCE', 'BACKGROUND_COLOR', 'GRID_COLOR', 'BREAKABLE_COLOR',
    'BREAKING_COLOR', 'BOMB_COLOR', 'OBSTACLE_COLOR', 'PLAYER_COLOR', 'PLAYER_2_COLOR',
    'HUD_COLOR', 'EXPLOSION_GREEN_COLOR', 'EXPLOSION_YELLOW_COLOR', 'PLAYER_LIVES', 'EXPLOSION_DURATION', 'BOMB_EXPLOSION_RANGE'
]
