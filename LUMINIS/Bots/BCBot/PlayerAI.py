from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
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

        ourNests = get_friendly_nest_positions()

        for unit in friendly_units:
            for nest in ourNests:
                if (unit.position == nest.position:
                        world.move(unit, nest.position +(1,0)
                            # path = world.get_shortest_path(unit.position,
                            #              world.get_closest_capturable_tile_from(unit.position, None).position,
                            #               None)
                            #  if path: world.move(unit, path[0])
