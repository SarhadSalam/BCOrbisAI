from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.bugsList = []
        pass

    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.
        
        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world
        for unit in friendly_units:
            if unit.uuid not in self.bugsList:
                self.bugsList.append(unit.uuid)
            path = world.get_shortest_path(unit.position, world.get_closest_capturable_tile_from(unit.position, None).position, None)
            
            for i in range(0, len(self.bugsList), 2):
                if unit.uuid == self.bugsList[i]:
                    path = world.get_shortest_path(unit.position, world.get_closest_enemy_from(unit.position, None).position, None)
            
            if unit.health >= 3:
                path = world.get_shortest_path(unit.position, world.get_closest_enemy_nest_from(unit.position, None), None)

            if (unit.health == 2):
                path = world.get_shortest_path(unit.position, unit.position, None)

            if path: world.move(unit, path[0])
