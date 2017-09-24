import json
import PythonClientAPI.Configurator.Constants as constants
import PythonClientAPI.Communication.CommunicatorConstants as comm_constants
from PythonClientAPI.Game.Entities import *
from PythonClientAPI.Game.Enums import TileType, Team, MoveResult
from PythonClientAPI.Game.GameState import *
from PythonClientAPI.Game.World import World
from enum import Enum

def parse_config(jsn, player_index):
    dct = json.loads(jsn)
    constants.MAP_NAME = dct["mapName"]
    comm_constants.PORT_NUMBER = int(dct["portNumber"])
    comm_constants.MAXIMUM_ALLOWED_RESPONSE_TIME = int(dct["maxResponseTime"])

def parse_game_state(jsn, tiles):
    dct = json.loads(jsn)
    return as_game_state(dct, tiles)

def parse_tile_data(game_starting_state):
    dct = json.loads(game_starting_state)
    return as_tiles(dct["tiles"])

def parse_ordered_directions(game_initial_state, uuid):
    dct = json.loads(game_initial_state)["uuidToOrderedDirections"]
    return as_direction_list(dct[uuid])

def as_direction_list(directions):
    return [Direction[direction] for direction in directions]

def as_game_state(dct, tiles):
    player_uuid_to_player_type_map = {}
    team_to_tiles_map = {}
    team_to_nests_map = {}

    for uuid in dct['playerUUIDToPlayerTypeMap'].keys():
        if uuid == constants.LOCAL_PLAYER_UUID:
            player_state = as_friendly_player_state(dct['playerUUIDToPlayerTypeMap'][uuid])
            team_to_tiles_map[Team.FRIENDLY] = player_state.friendly_tile_positions
            team_to_nests_map[Team.FRIENDLY] = player_state.friendly_nest_positions
        else:
            player_state = as_enemy_player_state(dct['playerUUIDToPlayerTypeMap'][uuid])
            team_to_tiles_map[Team.ENEMY] = player_state.friendly_tile_positions
            team_to_nests_map[Team.ENEMY] = player_state.friendly_nest_positions
            enemy_uuid = uuid

        player_uuid_to_player_type_map[uuid] = player_state

    player_index_to_uuid_map = {player_index: dct['playerIndexToUUIDMap'][player_index] for player_index in dct['playerIndexToUUIDMap'].keys()}

    world = World(tiles, player_uuid_to_player_type_map[constants.LOCAL_PLAYER_UUID].friendly_units,
                  player_uuid_to_player_type_map[enemy_uuid].friendly_units,
                  team_to_tiles_map, team_to_nests_map)

    return GameState(world, player_uuid_to_player_type_map, player_index_to_uuid_map, enemy_uuid)

def as_friendly_player_state(dct):
    return PlayerState(as_friendly_unit_list(dct['friendlyUnits']),
                       as_friendly_tile_list(dct['friendlyTilePositions']),
                       as_point_list(dct['friendlyNestPositions']))

def as_enemy_player_state(dct):
    return PlayerState(as_enemy_unit_list(dct['friendlyUnits']),
                       as_enemy_tile_list(dct['friendlyTilePositions']),
                       as_point_list(dct['friendlyNestPositions']))

def as_enemy_unit_list(lst):
    return [as_enemy_unit(unit) for unit in lst]

def as_friendly_unit_list(lst):
    return [as_friendly_unit(unit) for unit in lst]

def as_enemy_unit(dct):
    return EnemyUnit(dct['team'], dct['uuid'], int(dct['LF']), as_point_from_dct(dct['position']))

def as_friendly_unit(dct):
    return FriendlyUnit(dct['team'], dct['uuid'], int(dct['LF']), as_point_from_dct(dct['position']), MoveResult[dct['lastMoveResult']], dct['mergedUnitUuids'])

def as_friendly_tile_list(lst):
    return [Tile((tile[0], tile[1]), Team.FRIENDLY,
                  True if tile[2] == 1 else False) for tile in lst]

def as_enemy_tile_list(lst):
    return [Tile((tile[0], tile[1]), Team.ENEMY,
                 True if tile[2] == 1 else False) for tile in lst]

def as_point_list(lst):
    return [as_point_from_array(point) for point in lst]

def as_tiles(lst):
    return [[TileType[tile] for tile in column] for column in lst]

def as_point_from_dct(dct):
    return (dct['x'], dct['y'])

def as_point_from_array(arr):
    return (arr[0], arr[1])

class FFEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, PlayerTurnActionInfo):
            return {'uuidToCoreMap': {uuid: obj.uuid_to_core_map[uuid] for uuid in obj.uuid_to_core_map.keys()}}
        if isinstance(obj, FriendlyUnit):
            return {'team': obj.team, 'uuid': obj.uuid, 'LF': obj.health, 'nextMoveType': obj._next_move_type.name, 'nextMoveTarget': tuple_to_point(obj._next_move_target), 'lastMoveResult': obj.last_move_result.name}
        return json.JSONEncoder.default(self, obj)

def tuple_to_point(tupl):
    if tupl is None:
        return None
    return {'x': tupl[0], 'y':tupl[1]}