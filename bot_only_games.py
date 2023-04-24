from bots.Rando_Calrissian import RandoCalrissian
import bots.bot_manager as all_bots
from game_json_logger import GameJSONLogger
from game_logger import GameLogger
from game_csv_logger import GameCSVLogger
from zole.game_events import EventNames, GameEvent
from zole.game_session_factory import GameSessionFactory

import time

if __name__ == '__main__':
    print('Started bot only games')

    gsf = GameSessionFactory()

    player1 = all_bots.Experiment42('Exper 1')
    player2 = all_bots.RandoCalrissian('Rando 2')
    player3 = all_bots.RandoCalrissian('Rando 3')

    gsf.add_player(player1)
    gsf.add_player(player2)
    gsf.add_player(player3)

    game_session = gsf.make_session()

    #logger = GameJSONLogger(game_session)
    #logger2 = GameLogger()
    logger3 = GameCSVLogger(player1, player2, player3)

    game_i = 0
    games_to_play = 25000

    timePoint = time.perf_counter()
    event: GameEvent = None
    while True:
        event = game_session.update()
        if event.name == EventNames.ContinueSessionEvent:
            game_i += 1
            if game_i%1000==0:
                curTime = time.perf_counter() - timePoint
                print(F'{game_i}:{curTime}')
            logger3.log(game_i, player1, player2, player3)

            event.set_continue(game_i < games_to_play)
        elif event.name == EventNames.SessionEndedEvent:
            break
        
        #logger.log(event)
        #logger2.log(event)

    logger3.graph(player1, player2, player3)
    #logger.close()
    #logger2.close()

    print(f'End of bot only game. Played {game_i} games')
