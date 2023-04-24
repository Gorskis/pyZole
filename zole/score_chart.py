from typing import List, Tuple

from zole.game_modes import GameMode
from zole.player import Player, PlayerRoles

POINTS = {
    GameMode.PACELT: {
        '8t': (6, -3),
        '91+': (4, -2),
        '61-90': (2, -1),
        '31-60': (-4, 2),
        '30-': (-6, 3),
        '0t': (-8, 4)
    },
    GameMode.ZOLE: {
        '8t': (14, -7),
        '91+': (12, -6),
        '61-90': (10, -5),
        '31-60': (-12, 6),
        '30-': (-14, 7),
        '0t': (-16, 8)
    },
    GameMode.MAZAZOLE: {
        '1+': (-14, 7),
        '0t': (12, -6)
    },
    GameMode.GALDINS: (4, -2)
}


def get_player_res_order(game_mode: GameMode, results: 'PartyResults') -> Tuple['PlayerResult']:
    player_results: List['PlayerResult'] = [None]*3
    p_i = 1
    if game_mode == GameMode.GALDINS:  # <<< GALDINS
        winner: Player = None
        winner_tricks = 9
        winner_score = 0
        for player_res in results.player_results:
            player = player_res.player
            if player.tricks_taken < winner_tricks or (
                    player.tricks_taken == winner_tricks and player.tricks_score < winner_score):
                winner = player
                winner_tricks = player.tricks_taken
                winner_score = player.tricks_score
        player_results[0] = winner
        for player_res in results.player_results:
            if player_res.player == winner:
                player_results[0] = player_res
            else:
                player_results[p_i] = player_res
                p_i += 1
    else:
        for player_res in results.player_results:
            if player_res.player.role in (PlayerRoles.LIELAIS, PlayerRoles.ZOLE, PlayerRoles.MAZAZOLE):
                player_results[0] = player_res
            else:
                player_results[p_i] = player_res
                p_i += 1
    return tuple(player_results)


def assign_points(player_results_in_order, points):
    player_results_in_order[0].score_change = points[0]  # winner/lielais get first pos
    player_results_in_order[0].has_won = points[0] > 0
    player_results_in_order[1].score_change = points[1]  # losers/mazie get second pos
    player_results_in_order[1].has_won = points[1] > 0
    player_results_in_order[2].score_change = points[1]
    player_results_in_order[2].has_won = points[1] > 0


def set_points(game_mode: GameMode, results: 'PartyResults'):
    # lielais 8 tricks      8t      'Lielais uzvar atstājot mazos bezstiķī'
    # lielais > 60 < 91     61-90   'Lielais uzvar'
    # lielais > 90          91+     'Lielais uzvar atstājot mazos jāņos'
    # lielais > 30 <61      31-60   'Lielais zaudē'
    # lielais < 31          30-     'Lielais zaudē jāņos'
    # lielais 0 tricks      0t      'Lielais zaudē bezstiķī'

    player_results_in_order = get_player_res_order(game_mode, results)

    if game_mode == GameMode.GALDINS:
        points = POINTS[GameMode.GALDINS]
        assign_points(player_results_in_order, points)
        return results

    lielais_tricks_taken = player_results_in_order[0].player.tricks_taken
    lielais_score = player_results_in_order[0].player.tricks_score
    point_set = POINTS[game_mode]
    points = None
    if game_mode == GameMode.MAZAZOLE:
        if lielais_tricks_taken == 0:
            points = point_set['0t']
        else:
            points = point_set['1+']
        assign_points(player_results_in_order, points)
        return results

    key = None
    if lielais_tricks_taken == 8:
        key = '8t'
    elif lielais_tricks_taken == 0:
        key = '0t'
    elif lielais_score > 90:
        key = '91+'
    elif lielais_score > 60:
        key = '61-90'
    elif lielais_score > 30:
        key = '31-60'
    else:
        key = '30-'
    points = point_set[key]
    assign_points(player_results_in_order, points)
    results.lielais_won = player_results_in_order[0].has_won
    return results
