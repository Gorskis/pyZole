from bots.bot import Bot
from random import Random
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode
import zole.cards
from zole.trick import Trick
import zole.player
from bots.DataSetup import DataPaths as data
from bots.DataSetup import checkExistance
from bots.DataSetup import loadData

import numpy as np
import torch
import torch.nn as nn
import os.path as path
import math

class MainNetwork:
    def __init__(self):
        self.gameListFiltered =[]
        self.n_input = 26*3
        self.n_hidden = 26*2
        self.n_out = 26
        self.learning_rate = 0.01
        self.epochCount = 30


        self.correctCount = 0
        self.incorrectCount = 0

    def initializeModel(self):
        self.model = nn.Sequential(nn.Linear(self.n_input, self.n_hidden),
                      nn.ELU(),
                      nn.Linear(self.n_hidden, self.n_out),
                      nn.Tanh())

    def TrainOnPartData(self, loss_function, optimizer):
        for epoch in range(self.epochCount):
            if epoch%10==0:
                print(f'Model training progress: {round(100*epoch/self.epochCount,3)}%')
            pred_y = self.model(self.data_x)

            loss = self.loss_masked(pred_y, self.data_mask, self.data_result, loss_function)                           # Vai prognoztā kārts sakrīt ar spēlētāja izvēli
            self.model.zero_grad()   
            loss.backward()

            optimizer.step()

    def trainModel(self):
        print('Model training started')
        loss_function = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        i=0
        while checkExistance(data.X_MIN, i):
            print('Model training on part '+ str(i) + ' of data')
            self.data_x = loadData(data.X_MIN, i)
            self.data_mask = loadData(data.MASK, i)
            self.data_result = loadData(data.RESULT, i)
            self.TrainOnPartData(loss_function, optimizer)
            i+=1
        print('Model training complete')

    def loss_masked(self, pred_y, mask, y, loss_function):
    	# error of elements where y is not 0
        masked_pred = torch.mul(pred_y, mask)
        expected_card_result = torch.mul(mask, y)
        MSE = loss_function(masked_pred, expected_card_result)
        #multiplier = 26*len(y)/torch.sum(y)
        MSEMult = torch.mul(MSE, 26*len(y)/torch.sum(y))
        return MSEMult

    def turnInputStateIntoArray(self, cardsOnHand, firstCardTable, secondCardTable):
        array = np.zeros(26*3)
        for card in cardsOnHand:
            array[card] = 1
        if firstCardTable != None and firstCardTable != 999:
            array[firstCardTable+26] = 1
        if secondCardTable != None and secondCardTable != 999:
            array[secondCardTable+52] = 1
        return array

    def tensorToCard(self, tensor):
        chosenCardVal = max(tensor)
        # Ja atļauti bija tikai slikti varianti, labākajai izvēlei būs negatīva vērtība un tik izvēlēta pirmā no aizliegtajām kārtīm, jo tām ir 0
        if chosenCardVal == 0:
            tensor *=-1
            chosenCardVal = min(tensor)
        for i in range(len(tensor)):
            if tensor[i]==chosenCardVal:
                return zole.cards.all_cards[i]
    
    def playCard(self, input, mask):
        outputTensor = self.model(torch.FloatTensor(input))
        self.output = outputTensor
        return self.tensorToCard(outputTensor)
    
    def formatInput(self, player:Bot, trick:Trick):
        hand = player.hand.as_index_array()
        firstCardTable = trick.first_card().i
        secondCardTable = trick.cards[1].i
        return self.turnInputStateIntoArray(hand, firstCardTable, secondCardTable)

class Experiment15(Bot):
    bot_name = 'Experiment15'
    
    def __init__(self, player_name: str):
        super().__init__(player_name)
        self.rand = Random()

        pathName = 'Resources/Models/'+self.bot_name+'.pkl'
        if path.isfile(pathName):
            self.network = MainNetwork()
            self.network.model = torch.load(pathName)
            print('Model loaded')

        else:
            self.network = MainNetwork()
            self.network.initializeModel()
            self.network.trainModel()
            torch.save(self.network.model, pathName)
            print('Model Trained')
        
        

    def handle_game_event(self, event: GameEvent):
        if event.name == EventNames.PartyStartedEvent:
            # my_cards = self.hand
            # party = event.party
            # TODO get my position in seating
            pass
        elif event.name == EventNames.SelectGameModeEvent:
            modes = [GameMode.PASS, GameMode.PACELT, GameMode.ZOLE, GameMode.MAZAZOLE]
            selected_game_mode = self.rand.choices(modes, [0.5, 0.5, 0, 0])[0]
            event.set_selected_game_mode(selected_game_mode)
        elif event.name == EventNames.GameModeSelectedEvent:
            # game_mode = event.selected_game_mode
            # role = self.role
            pass
        elif event.name == EventNames.CardPickUpEvent:
            # self.hand is still the same
            event.take_cards()
            # self.hand now has 2 more cards: event.new_card1 and event.new_card2
        elif event.name == EventNames.DiscardCardsEvent:
            event.discard_cards(self.hand[9], self.hand[8])
        elif event.name == EventNames.PlayCardEvent:
            trick = event.trick
            input = self.network.formatInput(self, trick)
            valid_cards = self.hand.get_valid_cards(trick.first_card())
            card_to_play = self.network.playCard(input, valid_cards.as_input_array())     
            if card_to_play in valid_cards:
                self.network.correctCount+=1
                event.play_card(card_to_play)
            else:
                event.play_card(valid_cards[self.rand.randint(0, len(valid_cards) - 1)])
                self.network.incorrectCount+=1
        elif event.name == EventNames.TrickEndedEvent:
            trick = event.trick
            taker_of_the_trick = trick.tacker()
            trick_score = trick.score()
            
        elif event.name == EventNames.PartyEndedEvent:
            playerResults = event.party_results.player_results
            

        else:
            print(f'Bot {self.bot_name} not able to handle event {event.name}')