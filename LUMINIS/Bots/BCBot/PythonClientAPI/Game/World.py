from PythonClientAPI.Game.PlayerAPI import PlayerAPI
from PythonClientAPI.Game.Enums import TileType, Team, MoveType
from PythonClientAPI.Game.Entities import Tile

class World:
    def __init__(self, tiles, friendlies, enemies, team_to_tiles_map, team_to_nests_map):
        self._deduce_neutral_tiles(tiles, team_to_tiles_map)
        self._create_uuid_to_friendlies_map(friendlies)
        self.api = PlayerAPI(tiles, friendlies, enemies, team_to_tiles_map, team_to_nests_map)

    def get_unit(self, uuid):
        """
        Given its uuid, returns the corresponding unit.
        If there are no living units with uuid, returns None.

        If you want to keep track of your units across turns,
        save their uuids somewhere in your PlayerAI instance
        and use this method to retrieve them at each turn.

        :param str uuid: unique uuid of desired unit
        :return: FriendlyUnit with uuid
        :rtype: FriendlyUnit
        """
        return self.uuid_to_friendlies_map.get(uuid, None)

    def move(self, unit, position):
        """
        Moves a unit one step closer to position. Use this method to assign moves for your units.

        Note: this method uses get_next_point_in_shortest_path, which does not take into account
        dynamic game elements (i.e. other units or nests) that may stand in the way between
        the source and destination. It only takes into account walls and tiles.

        To include a list of "avoid" points in path-finding, use get_shortest_path.

        :param FriendlyUnit unit: unit to move
        :param (int,int) position: target position
        :return: whether or not the move will result in MOVE or REST
        :rtype: MoveType
        """
        if unit.uuid in self.uuid_to_friendlies_map:
            unit = self.uuid_to_friendlies_map[unit.uuid]
        else:
            raise Exception("Asked to move unit that is no longer in game!")

        point = self.get_next_point_in_shortest_path(unit.position, position)
        unit._next_move_target = point
        unit._next_move_type = MoveType.REST if point == unit.position else MoveType.MOVE

        return unit._next_move_type

    def _create_uuid_to_friendlies_map(self, friendlies):
        self.uuid_to_friendlies_map = {}
        for unit in friendlies:
            self.uuid_to_friendlies_map[unit.uuid] = unit

    def _deduce_neutral_tiles(self, tiles, team_to_tiles_map):
        friendly_tiles = []
        enemy_tiles = []

        for tile_list in team_to_tiles_map.values():
            for tile in tile_list:
                if tile.is_friendly(): friendly_tiles.append(tile.position)
                elif tile.is_enemy(): enemy_tiles.append(tile.position)

        width = len(tiles)
        height = len(tiles[0])
        neutral_tiles = []
        for x in range(0, width):
            for y in range(0, height):
                if not (tiles[x][y] == TileType.WALL) and not ((x, y) in friendly_tiles or (x, y) in enemy_tiles):
                    neutral_tiles.append(Tile((x, y), Team.NEUTRAL, False))

        team_to_tiles_map[Team.NEUTRAL] = neutral_tiles

    def get_width(self):
        """
        :return: map width
        :rtype: int
        """
        return self.api.get_width()

    def get_height(self):
        """
        :return: map height
        :rtype: int
        """
        return self.api.get_height()

    def get_taxicab_distance(self, start, end):
        """
        :param (int,int) start: source
        :param (int,int) end: target
        :return: shortest taxi-cab distance between start and end
        :rtype: bool
        """
        return self.api.get_taxicab_distance(start, end)

    def is_within_bounds(self, point):
        """
        :param (int,int) point: point tuple
        :return: true iff point lies within boundaries of the map
        :rtype: bool
        """
        return self.api.is_within_bounds(point)

    def is_wall(self, point):
        """
        :param (int,int) point: point tuple
        :return: true iff there is a wall tile at point
        :rtype: bool
        """
        return self.api.is_wall(point)

    def at_edge(self, point):
        """
        :param (int,int) point: point tuple
        :return: true iff point lies on an edge of the map
        :rtype: bool
        """
        return self.api.at_edge(point)

    def get_neighbours(self, point):
        """
        Returns neighbouring points in four cardinal directions from point.

        :param (int,int) point: point tuple
        :return: dictionary in which keys are of type Direction and values are (x,y) tuples
        :rtype: dict
        """
        return self.api.get_neighbours(point)



    def get_shortest_path(self, start, end, avoid):
        """
        Returns the shortest path between start and end.
        If avoid is not None, the method will return the shortest path
        between start and end that does not visit any points in avoid.

        If there is no path, None is returned.

        Note: The path-finding algorithm may come at a cost of performance.
        For a quicker path look-up alternative, use get_next_point_shortest_path.

        :param (int,int) start: source
        :param (int,int) end: target
        :param set avoid: a set of (x,y) tuples to exclude from path-finding
        :return: list of points representing the shortest path such that the first element in the list is the next point in the path, or None.
        :rtype: list of point
        """
        return self.api.get_shortest_path(start, end, avoid)

    def get_next_point_in_shortest_path(self, start, end):
        """
        Returns the next point in the shortest path between start and end, using a cache.
        If there is no path, returns start.

        Note: This method does not take into account dynamic game elements (i.e. other units or nests)
        that may stand in the way between the source and destination. It only takes into account walls and tiles.

        :param (int,int) start: source
        :param (int,int) end: target
        :return: next point in the shortest path, or start if there is no path
        :rtype: (int, int)
        """
        return self.api.get_next_point_in_shortest_path(start, end)

    def get_shortest_path_distance(self, start, end):
        """
        Returns the distance of the shortest path between start and end, only taking into account walls.
        If there is no path, returns 0.

        :param start: 
        :param end: 
        :return: 
        """
        return self.api.get_shortest_path_distance(start, end)

    def get_closest_enemy_from(self, point, excluding_units):
        """
        Returns the closest EnemyUnit from point, excluding any of the ones in excluding_units.

        :param (int,int) point: point tuple
        :param set excluding_units: a set of EnemyUnits to exclude from search
        :return: closest EnemyUnit from point
        :rtype: EnemyUnit
        """
        return self.api.get_closest_enemy_from(point, excluding_units)

    def get_closest_friendly_from(self, point, excluding_units):
        """
        Returns the closest FriendlyUnit from point, excluding any of the ones in excluding_units.

        :param (int,int) point: point tuple
        :param set excluding_units: a set of FriendlyUnit to exclude from search
        :return: closest FriendlyUnit from point
        :rtype: FriendlyUnit
        """
        return self.api.get_closest_friendly_from(point, excluding_units)

    def get_closest_neutral_tile_from(self, point, excluding_points):
        """
        :param (int,int) point: source
        :param set excluding_points: points to exclude from search
        :return: Closest neutral Tile from point, excluding any of the ones whose positions are in excluding_points
        :rtype: Tile
        """
        return self.api.get_closest_neutral_tile_from(point, excluding_points)

    def get_closest_enemy_tile_from(self, point, excluding_points):
        """
        :param (int,int) point: source
        :param set excluding_points: points to exclude from search
        :return: Closest enemy Tile from point, excluding any of the ones whose positions are in excluding_points
        :rtype: Tile
        """
        return self.api.get_closest_enemy_tile_from(point, excluding_points)

    def get_closest_capturable_tile_from(self, point, excluding_points):
        """
        :param (int,int) point: source
        :param set excluding_points: points to exclude from search
        :return: Closest non-permanent enemy or neutral Tile from point, excluding any of the ones whose positions are in excluding_points
        :rtype: Tile
        """
        return self.api.get_closest_capturable_tile_from(point, excluding_points)

    def get_closest_friendly_tile_from(self, point, excluding_points):
        """
        :param (int,int) point: source
        :param set excluding_points: points to exclude from search
        :return: Closest friendly Tile from point, excluding any of the ones whose positions are in excluding_points
        :rtype: Tile
        """
        return self.api.get_closest_friendly_tile_from(point, excluding_points)

    def get_closest_friendly_nest_from(self, point, excluding_points):
        """
        :param (int,int) point: source
        :param set excluding_points: points to exclude from search
        :return: Closest friendly nest location from point, excluding any of the ones whose positions are in excluding_points
        :rtype: Tile
        """
        return self.api.get_closest_friendly_nest_from(point, excluding_points)

    def get_closest_enemy_nest_from(self, point, excluding_points):
        """
        :param (int,int) point: source
        :param set excluding_points: points to exclude from search
        :return: Closest enemy nest location from point, excluding any of the ones whose positions are in excluding_points
        :rtype: Tile
        """
        return self.api.get_closest_enemy_nest_from(point, excluding_points)

    def get_closest_point_from(self, source, condition):
        """
        Given source, looks for the closest point from source that satisfies condition

        :param (int,int) source: source
        :param function condition: a function that takes a single point as an argument and evaluates to True if it matches the search criteria
        :return: the closest point from source for which condition evaluates to True
        :rtype: (int,int)
        """
        return self.api.get_closest_point_from(source, condition)

    def get_nest_positions(self):
        """
        :return: list of (x,y) tuples for all nests in current game state
        :rtype: list of (int, int)
        """
        return self.api.get_nest_positions()

    def get_friendly_nest_positions(self):
        """
        :return: list of (x,y) tuples for all friendly nests in current game state
        :rtype: list of (int, int)
        """
        return self.api.get_friendly_nest_positions()

    def get_enemy_nest_positions(self):
        """
        :return: list of (x,y) tuples for all enemy nests in current game state
        :rtype: list of (int, int)
        """
        return self.api.get_enemy_nest_positions()

    def get_tiles_around(self, point):
        """
        Returns only Tile neighbours around point. If there are walls around point,
        they will not be included in the returned dictionary.

        :param (int,int) point: point tuple
        :return: dictionary in which keys are of type Direction and values are Tiles
        :rtype: dict
        """
        return self.api.get_tiles_around(point)

    def get_enemy_tiles_around(self, point):
        """
        :param (int,int) point: point tuple
        :return: a list of enemy Tiles around point
        :rtype: list of Tile
        """
        return self.api.get_enemy_tiles_around(point)

    def get_friendly_tiles_around(self, point):
        """
        :param (int,int) point: point tuple
        :return: a list of friendly Tiles around point
        :rtype: list of Tile
        """
        return self.api.get_friendly_tiles_around(point)

    def get_enemy_nest_clusters(self):
        """
        :return: list of sets of (x,y) tuples, where each set represents an enemy nest cluster
        :rtype: list of set of (int, int)
        """
        return self.api.get_enemy_nest_clusters()

    def get_friendly_nest_clusters(self):
        """
        :return: list of sets of (x,y) tuples, where each set represents a friendly nest cluster
        :rtype: list of set of (int, int)
        """
        return self.api.get_friendly_nest_clusters()

    def get_position_to_friendly_dict(self):
        """
        :return: dictionary whose keys are (x,y) tuples and values are FriendlyUnits with positions at key
        :rtype: dict with key (int, int) and value FriendlyUnit
        """
        return self.api.get_position_to_friendly_dict()

    def get_position_to_enemy_dict(self):
        """
        :return: dictionary whose keys are (x,y) tuples and values are EnemyUnits with positions at key
        :rtype: dict with key (int, int) and value EnemyUnit
        """
        return self.api.get_position_to_enemy_dict()

    def get_neutral_tiles(self):
        """
        :return: a list of all neutral Tiles
        :rtype: list of Tile
        """
        return self.api.get_neutral_tiles()

    def get_friendly_tiles(self):
        """
        :return: a list of all friendly Tiles
        :rtype: list of Tile
        """
        return self.api.get_friendly_tiles()

    def get_enemy_tiles(self):
        """
        :return: a list of all enemy Tiles
        :rtype: list of Tile
        """
        return self.api.get_enemy_tiles()

    def get_tiles(self):
        """
        :return: a list of all Tiles
        :rtype: list of Tile
        """
        return self.api.get_tiles()

    def get_tile_at(self, point):
        """
        :param point: (x,y) tuple
        :return: Tile at point, or None
        :rtype: Tile
        """
        return self.api.get_tile_at(point)

    def get_position_to_tile_dict(self):
        """
        :return: dictionary whose keys are (x,y) tuples and values of Tiles with positions at key
        :rtype: dict with key (int, int) and value Tile
        """
        return self.api.get_position_to_tile_dict()