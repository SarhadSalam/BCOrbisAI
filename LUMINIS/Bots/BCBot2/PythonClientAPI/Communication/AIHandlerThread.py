import cProfile
import io
import pstats
import sys
import threading
import traceback
import time

from PythonClientAPI.Communication.Signals import Signals
from PythonClientAPI.Configurator import Constants
from PythonClientAPI.Game.GameState import PlayerTurnActionInfo
from PythonClientAPI.Game.Enums import MoveType


class AIHandlerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None):
        threading.Thread.__init__(self, group=group, target=target, daemon=daemon, args=args, kwargs=kwargs)
        self.player_move = Signals.NO_RESPONSE.name

    def run(self):
        player_ai = self._kwargs['player_ai']
        decoded_game_data = self._kwargs['decoded_game_data']
        player_move_event = self._kwargs['player_move_event']
        friendly_units = decoded_game_data.player_uuid_to_player_type_map[Constants.LOCAL_PLAYER_UUID].friendly_units
        enemy_units = decoded_game_data.player_uuid_to_player_type_map[decoded_game_data.enemy_uuid].friendly_units
        friendly_units.sort(key=lambda unit: unit.health)
        enemy_units.sort(key=lambda unit: unit.health)
        try:
            start_time = time.time()
            player_ai.do_move(decoded_game_data.world, friendly_units, enemy_units)

            self.player_move = PlayerTurnActionInfo({unit.uuid: unit for unit in friendly_units if unit.get_next_move_type() == MoveType.MOVE})
            end_time = time.time()
            print("[TIME] " + str(round((end_time - start_time) * 1000)) + " ms")

            player_move_event.set()
        except:
            print("An exception occurred in calling do_move: \n", file=sys.stderr)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      file=sys.stderr)
            player_move_event.set()

    def get_move(self):
        return self.player_move
