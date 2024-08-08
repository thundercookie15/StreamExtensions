'''Game folder for DIVEKICK'''
GAME_DIVEKICK = {'name': 'Divekick', 'config': 'data/config/Divekick_T2T3.json'}
'''Game folder for Duck Game'''
GAME_DUCKGAME = {'name': 'Duck Game', 'config': 'data/config/DuckGame_T2T3.json'}
'''Game folder for Grand Theft Auto V'''
GAME_GTA = {'name': 'Grand Theft Auto V', 'config': 'data/config/gta_remote.json'}
'''Game folder for Jump King'''
GAME_JUMPKING = {'name': 'Jump King', 'config': 'data/config/jumpking_remote.json'}
'''Game folder for Stick Fight'''
GAME_STICKFIGHT = {'name': 'Stick Fight', 'config': 'data/config/StickFight_GP2_localremote.json'}
'''Game folder for Honkai Star Rail'''
GAME_HSR = {'name': 'Honkai Star Rail', 'config': 'data/config/honkaistarrail.json'}
GAME_DESERT_BUS = {'name': 'Desert Bus', 'config': 'data/config/desertbus.json'}
GAME_POKEMON_FIRE_RED = {'name': 'Pokemon Fire Red', 'config': 'data/config/pokemon_fire_red.json'}
GAME_POKEMON_EMERALD = {'name': 'Pokemon Emerald', 'config': 'data/config/pokemon_emerald.json'}
GAME_EARTHBOUND = {'name': 'Earthbound', 'config': 'data/config/snes.json'}


def get_games():
    """Returns a list of all games"""
    return [GAME_DESERT_BUS, GAME_DIVEKICK, GAME_DUCKGAME, GAME_EARTHBOUND, GAME_GTA, GAME_HSR, GAME_JUMPKING, GAME_POKEMON_FIRE_RED, GAME_POKEMON_EMERALD, GAME_STICKFIGHT]


def get_game_names():
    """Returns a list of all game names"""
    return [game['name'] for game in get_games()]


def get_selected_game_config(game_name):
    """Returns the config for the selected game"""
    return [game['config'] for game in get_games() if game['name'] == game_name][0]
