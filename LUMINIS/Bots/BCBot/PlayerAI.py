from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World
import time

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.count = 0
        self.defend = [0]
        self.movespot=[0,0]
        self.defendlist = [[0,-1],[0,1],[1,0],[-1,0]]
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
        if (len(self.defend) != len(ourNests)):
            self.defend += [0]
        for i in range(len(ourNests)):
            nest = ourNests[i]
            for unit in friendly_units:
                if unit == friendly_units[0]:
                    self.movespot = [unit.position[0] + self.movelist[self.count][0], unit.position[1] + self.movelist[self.count][1]]
                    self.count += 1
                    if self.count == len(self.movelist):
                        self.count = 0
                elif (unit.position == nest):
                    self.movespot = [nest[0] + self.defendlist[self.defend[i]][0], nest[1] + self.defendlist[self.defend[i]][1]]
                    self.defend[i] += 1
                    if self.defend[i] == len(self.defendlist):
                        self.defend[i] = 0
                world.move(unit, self.movespot)
        time.sleep(0.5)
