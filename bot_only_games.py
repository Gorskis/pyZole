from bots.MultiLayerNetwork import MultiLayerNetwork
from bots.Rando_Calrissian import RandoCalrissian
from game_json_logger import GameJSONLogger
from game_logger import GameLogger
from zole.game_events import EventNames, GameEvent
from zole.game_session_factory import GameSessionFactory

if __name__ == '__main__':
    print('Started bot only games')
    gsf = GameSessionFactory()

    player1 = RandoCalrissian('Rando 0') #MultiLayerNetwork('NetBot')
    player2 = RandoCalrissian('Rando 1')
    player3 = RandoCalrissian('Rando 2')

    gsf.add_player(player1)
    gsf.add_player(player2)
    gsf.add_player(player3)

    game_session = gsf.make_session()

    logger = GameJSONLogger(game_session)
    logger2 = GameLogger()

    game_i = 0
    games_to_play = 10

    event: GameEvent = None
    while True:
        event = game_session.update()
        if event.name == EventNames.ContinueSessionEvent:
            game_i += 1
            event.set_continue(game_i < games_to_play)
        elif event.name == EventNames.SessionEndedEvent:
            break
        logger.log(event)
        logger2.log(event)

    logger.close()
    logger2.close()

    print(f'End of bot only game. Played {game_i} games')
