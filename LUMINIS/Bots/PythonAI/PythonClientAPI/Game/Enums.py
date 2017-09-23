import json
from collections import OrderedDict
from enum import Enum

from PythonClientAPI.Game.PointUtils import *


class Direction(Enum):
    """
    Represents cardinal directions that units can move in.
    Their value is a coordinate offset represented by a single move of 1 tile in that direction.
    """
    NOWHERE = (0, 0)
    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    def move_point(self, point):
        """
        Returns a new point who's values are that of the given point moved 1 tile in this direction.

        :param (int,int) point: (x,y) point
        :rtype: (int,int)
        """
        return add_points(point, self.value)

Direction._delta_to_direction = {
    dir.value: dir for dir in Direction
    }

Direction.ORDERED_DIRECTIONS = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]

Direction.INDEX_TO_DIRECTION = {0: Direction.NOWHERE, 1: Direction.NORTH, 2: Direction.EAST, 3: Direction.SOUTH, 4: Direction.WEST}
Direction.DIRECTION_TO_INDEX = {Direction.INDEX_TO_DIRECTION[idx]: idx for idx in Direction.INDEX_TO_DIRECTION.keys()}

class TileType(Enum):
    WALL = 0
    TILE = 1

class Team(Enum):
    FRIENDLY = 0
    ENEMY = 1
    NEUTRAL = -1

class MoveType(Enum):
    MOVE = 0
    REST = 1

class MoveResult(Enum):
    MOVE_SUCCESS = 0
    DAMAGE_SUCCESS = 1
    BLOCKED_BY_WALL = 2
    BLOCKED_BY_NEST = 3
    NEWLY_SPAWNED = 4
    MOVE_INVALID = 5
    NEWLY_MERGED = 6