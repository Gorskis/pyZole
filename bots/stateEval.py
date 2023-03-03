from zole.trick import Trick
from bots.bot import Bot
import bots.NN_base as NN_base
import bots.DataSetup as data

import numpy as np
import torch
import torch.nn as nn

class stateEvalNN():
    def __init__(self):

        self.n_input = 26*4 + 7 + 2
        self.n_hidden1 = 26*5
        self.n_hidden2 = 26*5
        self.n_hidden3 = 26*3
        self.n_out = 1
        self.learning_rate = 0.05
        self.epochCount = 500

        self.data_x = data.data_x
        self.data_y = data.data_y_result
    
    def initializeModel(self):
        self.model = nn.Sequential(nn.Linear(self.n_input, self.n_hidden1),
                            nn.Sigmoid(),
                            nn.Linear(self.n_hidden1, self.n_hidden2),
                            nn.ReLU(),
                            nn.Linear(self.n_hidden2, self.n_hidden3),
                            nn.ReLU(),
                            nn.Linear(self.n_hidden3, self.n_out),
                            nn.Hardsigmoid()
                            )
        self.loss_function = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

    def retrainModel(self, archives):
        self.data_x = []
        self.data_y = []
        for singleArchive in archives:
            self.data_x.append(singleArchive.input)
            self.data_y.append(singleArchive.output)
        self.data_x = torch.FloatTensor(np.array(self.data_x))
        self.data_y = torch.FloatTensor(np.array(self.data_y))
        self.trainModel()

    def trainOnOne(self, x, y):
        pred_y = self.model(torch.FloatTensor(x))
        self.model.zero_grad()   
        self.loss_function(pred_y, torch.FloatTensor(y)).backward()   # Vai prognoztā kārts sakrīt ar spēlētāja izvēli
        self.optimizer.step()

    def trainModel(self):
        self.initializeModel()
        for epoch in range(self.epochCount): #
            pred_y = self.model(self.data_x)
            self.model.zero_grad()   
            self.loss_function(pred_y, self.data_y).backward()   # Vai prognoztā kārts sakrīt ar spēlētāja izvēli
            self.optimizer.step()

    def forward(self, player:Bot, trick:Trick):
        input = NN_base.formatInput(player, trick)
        return self.model(torch.FloatTensor(input))


    



