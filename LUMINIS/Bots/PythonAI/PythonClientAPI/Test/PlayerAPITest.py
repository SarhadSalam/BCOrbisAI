from unittest import TestCase
import unittest

from PythonClientAPI.Game.Entities import Tile, FriendlyUnit, EnemyUnit
from PythonClientAPI.Game.Enums import TileType, Team, Direction
from PythonClientAPI.Game.PlayerAPI import PlayerAPI
from PythonClientAPI.Game.World import World
from PythonClientAPI.Navigation.NavigationCache import navigation_cache


class TestPlayerAPI(TestCase):

    def setUp(self):
        self.height, self.width = 19, 19
        self.tiles = [[TileType.TILE for x in range(self.width)] for y in range(self.height)]

    def tearDown(self):
        self.world = None
        self.tiles = None

    def test_get_width(self):
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertEqual(self.width, world.get_width())

    def test_get_height(self):
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertEqual(self.height, world.get_height())

    def test_taxicab_distance(self):
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertEqual(3, world.get_taxicab_distance((0, 0), (18, 17)))

    def test_is_within_bounds(self):
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertTrue(world.is_within_bounds((0, 0)))
        self.assertFalse(world.is_within_bounds((19, 0)))
        self.assertFalse(world.is_within_bounds((0, -1)))

    def test_is_wall(self):
        self.tiles[self.width // 2][self.height // 2] = TileType.WALL
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertTrue(world.is_wall((self.width // 2, self.height // 2)))
        self.assertFalse(world.is_wall((0, 0)))

    def test_at_edge(self):
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertTrue(world.at_edge((0, 3)))
        self.assertFalse(world.at_edge((self.width // 2, self.height // 2)))
        self.assertFalse(world.at_edge((-1, 0)))

    def test_get_neighbours(self):
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        point = (0, 0)
        expected = {Direction.WEST: (18, 0), Direction.EAST:(1, 0), Direction.SOUTH:(0, 1), Direction.NORTH:(0, 18)}
        actual = world.get_neighbours(point)
        for direction in actual.keys():
            self.assertEqual(expected[direction], actual[direction])
        self.assertEqual(len(expected), len(actual))

    def test_get_tiles_around(self):
        self.tiles[10][8] = TileType.WALL
        world = World(self.tiles, [], [], {Team.FRIENDLY: [Tile((9, 7), Team.FRIENDLY, False)], Team.ENEMY: [Tile((11, 8), Team.ENEMY, False)]}, {Team.FRIENDLY: [], Team.ENEMY: []})
        point = (10, 7)
        expected = {Direction.WEST: (9, 7), Direction.EAST: (11, 7), Direction.NORTH: (10, 6)}
        actual = world.get_tiles_around(point)
        for direction in actual.keys():
            self.assertEqual(expected[direction], actual[direction].position)
        self.assertEqual(len(expected), len(actual))

    def test_get_shortest_path(self):
        Direction.ORDERED_DIRECTIONS = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        avoid = [(0, 18), (18, 0)]
        start = (0, 0)
        end = (18, 18)
        expected = [(1, 0), (1, 18), (1, 17), (0, 17), (18, 17), (18, 18)]
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        actual = world.get_shortest_path(start, end, avoid)
        self.assertEqual(expected, actual)

    def test_navigation_cache_path_finding(self):
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        navigation_cache.load_compiled_data("U:\\orbis challenge\\Orbis Challenge 2017\\Game\\Maps\\test_map.nac")
        self.assertEqual((10, 7), world.get_next_point_in_shortest_path((9, 7), (9, 11)))
        self.assertEqual(8, world.get_shortest_path_distance((9, 7), (9, 11)))

    def test_get_nest_positions(self):
        expected = {Team.FRIENDLY: [(1, 12), (3, 12), (6, 13)], Team.ENEMY: [(6, 18), (8, 16)]}
        expected['all'] = expected[Team.FRIENDLY] + expected[Team.ENEMY]
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, expected)
        actual = {}
        actual[Team.FRIENDLY] = world.get_friendly_nest_positions()
        actual[Team.ENEMY] = world.get_enemy_nest_positions()
        actual['all'] = world.get_nest_positions()
        for team in [Team.FRIENDLY, Team.ENEMY, 'all']:
            self.assertEqual(set(expected[team]), set(actual[team]))

    def test_get_friendly_tiles_around(self):
        self.tiles[8][8] = TileType.WALL

        world = World(self.tiles, [], [], {Team.FRIENDLY: [Tile(p, Team.FRIENDLY, False) for p in [(0, 1), (18, 0), (0, 18), (10, 7), (9, 6)]], Team.ENEMY: [Tile(p, Team.ENEMY, False) for p in [(1, 0), (8, 7)]]},
                      {Team.FRIENDLY: [(0, 0), (9, 7)], Team.ENEMY: []})

        expected = [(0, 1), (18, 0), (0, 18)]
        actual = world.get_friendly_tiles_around((0, 0))
        for tile in actual:
            self.assertTrue(tile.position in expected)
        self.assertEqual(len(expected), len(actual))

        expected = [(10, 7), (9, 6)]
        actual = world.get_friendly_tiles_around((9, 7))
        for tile in actual:
            self.assertTrue(tile.position in expected)
        self.assertEqual(len(expected), len(actual))

        expected = [(1, 0)]
        actual = world.get_enemy_tiles_around((0, 0))
        for tile in actual:
            self.assertTrue(tile.position in expected)
        self.assertEqual(len(expected), len(actual))

    def test_get_nest_clusters(self):
        nests = {Team.FRIENDLY: [(1, 7), (2, 5), (4, 5), (5, 3), (6, 7)], Team.ENEMY: [(4, 8), (8, 6), (7, 4), (10, 4)]}
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, nests)

        expected = [set(nests[Team.FRIENDLY][:-1]), set(nests[Team.FRIENDLY][-1:])]
        actual = world.get_friendly_nest_clusters()
        self.assertTrue(all([expected[i] in actual for i in range(0, len(expected))]))
        self.assertEqual(len(expected), len(actual))

        expected = [set(nests[Team.ENEMY][:1]), set(nests[Team.ENEMY][1:])]
        actual = world.get_enemy_nest_clusters()
        self.assertTrue(all([expected[i] in actual for i in range(0, len(expected))]))
        self.assertEqual(len(expected), len(actual))

    def test_get_closest_nest_from(self):
        expected = {Team.FRIENDLY: [(1, 1)], Team.ENEMY: [(18, 18)]}
        world = World(self.tiles, [], [], {Team.FRIENDLY: [], Team.ENEMY: []}, expected)
        self.assertEqual((1, 1), world.get_closest_friendly_nest_from((3, 3), None))
        self.assertEqual((18, 18), world.get_closest_enemy_nest_from((15, 15), None))

    def test_get_closest_unit_from(self):
        units = {Team.FRIENDLY: [FriendlyUnit("friendly", "test1", 1, (1, 1), None, []), FriendlyUnit("friendly", "test2", 1, (2, 0), None, [])],
                 Team.ENEMY: [EnemyUnit("enemy", "test3", 1, (5, 2)), EnemyUnit("enemy", "test4", 1, (1, 16))]}
        world = World(self.tiles, units[Team.FRIENDLY], units[Team.ENEMY], {Team.FRIENDLY: [], Team.ENEMY: []}, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertEqual((1, 16), world.get_closest_enemy_from((1, 1), None).position)
        self.assertEqual((2, 0), world.get_closest_friendly_from((1, 1), [(1, 1)]).position)

    def test_get_closest_capturable_tile_from(self):
        team_tiles = {Team.FRIENDLY: [Tile(p, Team.FRIENDLY, True) for p in [(2,0), (1,1), (2,1), (2,2)]],
                      Team.ENEMY: [Tile(p, Team.ENEMY, True) for p in [(3,1)]]}
        world = World(self.tiles, [], [], team_tiles, {Team.FRIENDLY: [], Team.ENEMY: []})
        self.assertEqual((3,1), world.get_closest_enemy_tile_from((2,1), None).position)
        self.assertEqual((2,18), world.get_closest_capturable_tile_from((2,1), None).position)

if __name__ == '__main__':
    unittest.main()