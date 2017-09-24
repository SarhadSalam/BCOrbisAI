class GameState:
    def __init__(self, world, player_uuid_to_player_type_map, player_index_to_uuid_map, enemy_uuid):
        self.world = world
        self.player_uuid_to_player_type_map = player_uuid_to_player_type_map
        self.player_index_to_uuid_map = player_index_to_uuid_map
        self.enemy_uuid = enemy_uuid

class PlayerState:
    def __init__(self, friendly_units, friendly_tile_positions, friendly_nest_positions):
        self.friendly_units = friendly_units
        self.friendly_tile_positions = friendly_tile_positions
        self.friendly_nest_positions = friendly_nest_positions

class PlayerTurnActionInfo:
    def __init__(self, uuid_to_core_map):
        self.uuid_to_core_map = uuid_to_core_map