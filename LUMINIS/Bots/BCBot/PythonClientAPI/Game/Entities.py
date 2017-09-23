from PythonClientAPI.Game.Enums import MoveType, Team, Direction
from PythonClientAPI.Game.PointUtils import *

class Entity:
    def __init__(self, position):
        self.position = position

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.position == other.position)

    def __ne__(self, other):
        return not self.__eq__(other)

class Tile(Entity):
    """
    Represents a colour-changing tile on the board.

    :ivar (int,int) position: tile's position
    """
    def __init__(self, position, team, permanent):
        self.position = position

        self._team = team
        self._permanent = permanent

    def is_permanently_owned(self):
        """
        :return: True iff Tile is permanently owned
        :rtype: bool
        """
        return self._permanent

    def is_friendly(self):
        """
        :return: True iff Tile is owned by your team
        :rtype: bool
        """
        return self._team == Team.FRIENDLY

    def is_enemy(self):
        """
        :return: True iff Tile is owned by the enemy team
        :rtype: bool
        """
        return self._team == Team.ENEMY

    def is_neutral(self):
        """
        :return: True iff Tile is not yet owned by any team
        :rtype: bool
        """
        return self._team == Team.NEUTRAL

    def __hash__(self):
        return 31 + self.position[0] * 31  + self.position[1];

    def __repr__(self):
        return "{} TILE: {}".format(self._team.name, self.position)

class Unit(Entity):
    def __init__(self, team, uuid, health, position):
        self.uuid = uuid
        self.health = health
        self.position = position
        self.team = team

    def __hash__(self):
        return hash(self.team) * 31 + hash(self.uuid)

    def __repr__(self):
        if self.is_friendly():
            return str(self.uuid)
        else:
            return str(self.uuid)

    def __lt__(self, other):
        return self.health < other.health

    def __le__(self, other):
        return self.health <= other.health

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uuid == other.uuid

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return self.health > other.health

    def __ge__(self, other):
        return self.health >= other.health

    def is_friendly(self):
        return NotImplementedError()

class FriendlyUnit(Unit):
    """
    Represents a friendly unit.

    :ivar str uuid: unique uuid for this unit
    :ivar int health: health point
    :ivar (int,int) position: unit position
    :ivar MoveResult last_move_result: last move result
    """
    def __init__(self, team, uuid, health, position, last_move_result, merged_units_uuid):
        super().__init__(team, uuid, health, position)
        self.last_move_result = last_move_result

        self._next_move_target = None
        self._next_move_type = None
        self._merged_units_uuid = set(merged_units_uuid)

    def get_next_move_target(self):
        """
        :return: next move target assigned for this turn
        :rtype: (int, int)
        """
        return self._next_move_target

    def get_next_move_type(self):
        """
        :return: next move type assigned for this turn
        :rtype: MoveType
        """
        return self._next_move_type

    def is_merged_with_unit(self, uuid):
        """
        :param str uuid: uuid of merged unit
        :return: True if a unit with uuid was merged into this FriendlyUnit
        :rtype: bool
        """
        return uuid in self._merged_units_uuid

    def is_friendly(self):
        return True


class EnemyUnit(Unit):
    """
    Represents an enemy unit.

    :ivar str uuid: unique uuid for this unit
    :ivar int health: health point
    :ivar (int,int) position: unit position
    """
    def __init__(self, team, uuid, health, position):
        super().__init__(team, uuid, health, position)

    def is_friendly(self):
        return False