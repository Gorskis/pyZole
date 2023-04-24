from datetime import datetime
from bots.bot import Bot
import csv

import pandas as pd
import matplotlib.pyplot as plt


class GameCSVLogger:
    def __init__(self, player1:Bot, player2:Bot, player3:Bot):
        self.now = str(datetime.now())[:19].replace(':', '')
        self.file = None
        self.file = open(f'./logs/log-{self.now}.csv', 'w')
        self.writer = csv.writer(self.file, lineterminator = '\n')
        self.writer.writerow(['game', player1.bot_name, player2.bot_name, player3.bot_name])

    def log(self, gameNum, player1:Bot, player2:Bot, player3:Bot):
        self.writer.writerow([gameNum, player1.points, player2.points, player3.points])

    def graph(self, player1:Bot, player2:Bot, player3:Bot):
        self.file.close()
        df = pd.read_csv(f'./logs/log-{self.now}.csv')
        plt.plot(df[player1.bot_name], label = player1.bot_name)
        plt.plot(df[player2.bot_name], label = player2.bot_name)
        plt.plot(df[player3.bot_name+'.1'], label = player3.bot_name)
        plt.xlabel('spēles')
        plt.ylabel('punkti')
        plt.legend()
        # sns.lineplot(data = df, x='game', y=player1.bot_name)
        # sns.lineplot(data = df, x='game', y=player2.bot_name)
        # sns.lineplot(data = df, x='game', y=player3.bot_name)
        plt.show()