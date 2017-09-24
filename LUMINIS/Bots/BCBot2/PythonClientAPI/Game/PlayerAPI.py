from PythonClientAPI.Game.Enums import TileType, Direction, Team
from PythonClientAPI.Game.PointUtils import mod_point, mod_taxi_cab_distance
from PythonClientAPI.DataStructures.Collections import Queue, PriorityQueue, recursively_flatten_list
from PythonClientAPI.Navigation.NavigationCache import navigation_cache


class PlayerAPI:

    def __init__(self, tiles, friendlies, enemies, team_to_tiles_map, team_to_nests_map):
        self.tiles = tiles
        self.width = len(tiles)
        self.height = len(tiles[0])
        self.friendlies = friendlies
        self.enemies = enemies
        self.team_to_tiles_map = team_to_tiles_map
        self.team_to_nests_map = team_to_nests_map

        self._position_to_tile_cache = None
        self._position_to_unit_cache = None
        self._nest_clusters_cache = None

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_taxicab_distance(self, start, end):
        return mod_taxi_cab_distance(start, end, self.width, self.height)

    def is_within_bounds(self, point):
        return (0 <= point[0] < self.width) and (0 <= point[1] < self.height)

    def is_wall(self, point):
        return self.tiles[point[0]][point[1]] == TileType.WALL

    def at_edge(self, point):
        return self.is_within_bounds(point) and \
               (point[0] == 0 or point[1] == 0 or point[0] == self.width - 1 or point[1] == self.height - 1)

    def get_neighbours(self, point):
        neighbours = {}
        for direction in Direction.ORDERED_DIRECTIONS:
            neighbours[direction] = mod_point(direction.move_point(point), (self.width, self.height))
        return neighbours

    # A* path-finding
    def get_shortest_path(self, start, end, avoid):
        if start == end: return [end]
        if self.is_wall(start) or self.is_wall(end): return None

        queue = PriorityQueue()

        queue.add(start, 0)

        inverted_tree = {}
        movement_costs = {}

        inverted_tree[start] = None
        movement_costs[start] = 0

        while not queue.is_empty():
            current = queue.poll()

            neighbours = self.get_neighbours(current)
            for direction in Direction.ORDERED_DIRECTIONS:
                neighbour = neighbours[direction]
                if self.is_wall(neighbour) or (avoid and (neighbour in avoid)):
                    continue
                cost = movement_costs[current] + 1
                if (neighbour not in movement_costs) or (cost < movement_costs[neighbour]):
                    movement_costs[neighbour] = cost
                    queue.add(neighbour,
                              cost + mod_taxi_cab_distance(neighbour, end, self.get_width(), self.get_height()))
                    inverted_tree[neighbour] = current

            if current == end:
                path = []
                cursor = end
                peek_cursor = inverted_tree[cursor]
                while peek_cursor:
                    path.append(cursor)
                    cursor = peek_cursor
                    peek_cursor = inverted_tree[cursor]
                path.reverse()
                return path

        return None

    def get_next_point_in_shortest_path(self, start, end):
        if not navigation_cache.loaded:
            path = self.get_shortest_path(start, end, None)
            if path: return path.get(0)
            return start
        direction = navigation_cache.get_next_direction_in_path(start, end)
        return mod_point(direction.move_point(start), (self.get_width(), self.get_height()))

    def get_shortest_path_distance(self, start, end):
        if not navigation_cache.loaded:
            path = self.get_shortest_path(start, end, None)
            if path: return len(path)
            return 0
        return navigation_cache.get_distance(start, end)

    def get_closest_enemy_from(self, point, excluding_units):
        if not self._position_to_unit_cache: self._create_position_to_unit_cache()
        target = self.get_closest_point_from(point, lambda p: (p in self._position_to_unit_cache) and (not self._position_to_unit_cache[p].is_friendly()) and ((not excluding_units) or (p not in excluding_units)))
        if target: return self._position_to_unit_cache[target]
        return None

    def get_closest_friendly_from(self, point, excluding_units):
        if not self._position_to_unit_cache: self._create_position_to_unit_cache()
        target = self.get_closest_point_from(point, lambda p: (p in self._position_to_unit_cache) and self._position_to_unit_cache[p].is_friendly() and ((not excluding_units) or (p not in excluding_units)))
        if target: return self._position_to_unit_cache[target]
        return None

    def _create_position_to_unit_cache(self):
        self._position_to_unit_cache = {}
        for unit in self.friendlies + self.enemies:
            self._position_to_unit_cache[unit.position] = unit

    def get_closest_neutral_tile_from(self, point, excluding_points):
        if not self._position_to_tile_cache: self._create_position_to_tile_cache()
        target = self.get_closest_point_from(point, lambda p: (p in self._position_to_tile_cache) and (self._position_to_tile_cache[p].is_neutral()) and ((not excluding_points) or (p not in excluding_points)))
        if target: return self._position_to_tile_cache[target]
        return None

    def get_closest_enemy_tile_from(self, point, excluding_points):
        if not self._position_to_tile_cache: self._create_position_to_tile_cache()
        target = self.get_closest_point_from(point, lambda p: (p in self._position_to_tile_cache) and (self._position_to_tile_cache[p].is_enemy()) and ((not excluding_points) or (p not in excluding_points)))
        if target: return self._position_to_tile_cache[target]
        return None

    def get_closest_capturable_tile_from(self, point, excluding_points):
        if not self._position_to_tile_cache: self._create_position_to_tile_cache()
        target = self.get_closest_point_from(point, lambda p: (p in self._position_to_tile_cache) and (not self._position_to_tile_cache[p].is_friendly()) and (not self._position_to_tile_cache[p].is_permanently_owned()) and ((not excluding_points) or (p not in excluding_points)))
        if target: return self._position_to_tile_cache[target]
        return None

    def get_closest_friendly_tile_from(self, point, excluding_points):
        if not self._position_to_tile_cache: self._create_position_to_tile_cache()
        target = self.get_closest_point_from(point, lambda p: (p in self._position_to_tile_cache) and (self._position_to_tile_cache[p].is_friendly()) and ((not excluding_points) or (p not in excluding_points)))
        if target: return self._position_to_tile_cache[target]
        return None

    def get_closest_friendly_nest_from(self, point, excluding_points):
        friendly_nests = self.team_to_nests_map[Team.FRIENDLY]
        return self.get_closest_point_from(point, lambda p: (p in friendly_nests) and ((not excluding_points) or (p not in excluding_points)))

    def get_closest_enemy_nest_from(self, point, excluding_points):
        enemy_nests = self.team_to_nests_map[Team.ENEMY]
        return self.get_closest_point_from(point, lambda p: (p in enemy_nests) and ((not excluding_points) or (p not in excluding_points)))

    def get_closest_point_from(self, source, condition):
        queue = Queue()
        visited = set()
        queue.add(source)
        visited.add(source)

        while not (queue.is_empty()):
            cursor = queue.poll()
            neighbours = self.get_neighbours(cursor)

            for direction in Direction.ORDERED_DIRECTIONS:
                neighbour = neighbours[direction]
                if not ((neighbour in visited) or self.is_wall(neighbour)):
                    queue.add(neighbour)
                    visited.add(neighbour)

            if condition(cursor): return cursor

        return None

    def get_nest_positions(self):
        nests = [team_nests for team_nests in self.team_to_nests_map.values()]
        return recursively_flatten_list(nests)

    def get_friendly_nest_positions(self):
        return self.team_to_nests_map[Team.FRIENDLY]

    def get_enemy_nest_positions(self):
        return self.team_to_nests_map[Team.ENEMY]

    def get_enemy_nest_clusters(self):
        if not self._nest_clusters_cache: self._create_nest_clusters_cache()
        return self._nest_clusters_cache[Team.ENEMY]

    def get_friendly_nest_clusters(self):
        if not self._nest_clusters_cache: self._create_nest_clusters_cache()
        return self._nest_clusters_cache[Team.FRIENDLY]

    def _create_nest_clusters_cache(self):
        environ_to_nests = self._get_extension_to_nests_map()

        self._nest_clusters_cache = {Team.FRIENDLY: [], Team.ENEMY: []}

        visited = set()

        for team in self.team_to_nests_map.keys():
            team_nests = self.team_to_nests_map[team]
            for nest in team_nests:
                if not (nest in visited):
                    queue = Queue()
                    cluster = set()

                    queue.add(nest)
                    cluster.add(nest)
                    visited.add(nest)

                    while not queue.is_empty():
                        current = queue.poll()

                        for environ in self.get_tiles_around(current).values():
                            for connected_nest in environ_to_nests[environ.position]:
                                self._check_and_visit(connected_nest, queue, cluster, visited, team_nests)
                            for ext_environ in self.get_tiles_around(environ.position).values():
                                if ext_environ.position in environ_to_nests:
                                    for touching_nest in environ_to_nests[ext_environ.position]:
                                        self._check_and_visit(touching_nest, queue, cluster, visited, team_nests)

                    self._nest_clusters_cache[team].append(cluster)

    def _check_and_visit(self, nest, queue, cluster, visited, team_nests):
        if (not (nest in cluster)) and (nest in team_nests):
            queue.add(nest)
            cluster.add(nest)
            visited.add(nest)

    def _get_extension_to_nests_map(self):
        environ_to_nests = {}
        for team in self.team_to_nests_map.keys():
            for nest in self.team_to_nests_map[team]:
                for environ in self.get_tiles_around(nest).values():
                    if not (environ.position in environ_to_nests):
                        environ_to_nests[environ.position] = []
                    environ_to_nests[environ.position].append(nest)

        return environ_to_nests

    def get_position_to_friendly_dict(self):
        position_to_unit = {}
        for unit in self.friendlies:
            position_to_unit[unit.position] = unit
        return position_to_unit

    def get_position_to_enemy_dict(self):
        position_to_unit = {}
        for unit in self.enemies:
            position_to_unit[unit.position] = unit
        return position_to_unit

    def get_tiles_around(self, point):
        tile_neighbours = {}
        if not self._position_to_tile_cache:
            self._create_position_to_tile_cache()
        neighbours = self.get_neighbours(point)
        for direction in neighbours:
            if neighbours[direction] in self._position_to_tile_cache:
                tile_neighbours[direction] = self._position_to_tile_cache[neighbours[direction]]
        return tile_neighbours

    def get_enemy_tiles_around(self, point):
        return self._get_team_tiles_around(point, Team.ENEMY)

    def get_friendly_tiles_around(self, point):
        return self._get_team_tiles_around(point, Team.FRIENDLY)

    def _get_team_tiles_around(self, point, team):
        belongs_to_team = []
        for tile in self.get_tiles_around(point).values():
            is_team = tile.is_friendly() if team == Team.FRIENDLY else tile.is_enemy()
            if is_team: belongs_to_team.append(tile)
        return belongs_to_team

    def get_neutral_tiles(self):
        return self.team_to_tiles_map[Team.NEUTRAL]

    def get_friendly_tiles(self):
        return self.team_to_tiles_map[Team.FRIENDLY]

    def get_enemy_tiles(self):
        return self.team_to_tiles_map[Team.ENEMY]

    def get_tiles(self):
        tiles = [t for t in self.team_to_tiles_map.values()]
        return recursively_flatten_list(tiles)

    def get_tile_at(self, point):
        if not self._position_to_tile_cache: self._create_position_to_tile_cache()
        if point in self._position_to_tile_cache: return self._position_to_tile_cache[point]
        return None

    def get_position_to_tile_dict(self):
        if not self._position_to_tile_cache: self._create_position_to_tile_cache()
        return self._position_to_tile_cache

    def _create_position_to_tile_cache(self):
        self._position_to_tile_cache = {}
        for tiles in self.team_to_tiles_map.values():
            for tile in tiles:
                self._position_to_tile_cache[tile.position] = tile