from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.count = 0
        self.movespot=[0,0]
        self.movelist = [[-1,0],[-1,0],[0,1],[-1,0],[-1,0],[0,-1],[0,-1],[1,0]]
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

        ourNests = world.get_friendly_nest_positions()

        for unit in friendly_units:
            for nest in ourNests:
                if unit == friendly_units[0]:
                    self.movespot = [unit.position[0] + self.movelist[self.count][0], unit.position[1] + self.movelist[self.count][1]]
                    self.count += 1
                    if self.count == 7:
                        self.count = 0
                elif (unit.position == nest):
                    self.movespot = [nest[0], nest[1] - 1]
                world.move(unit, self.movespot)
