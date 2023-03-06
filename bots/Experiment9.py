from bots.bot import Bot
from random import Random
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode
import zole.cards
from zole.trick import Trick
import zole.player
import bots.NN_base as NN_base
import bots.DataSetup as data

import json
import numpy as np
import torch
import torch.nn as nn
import os.path as path

class MainNetwork:
    def __init__(self):
        self.gameListFiltered =[]
        self.n_input = 26*3
        self.n_hidden = 26*2
        self.n_out = 26
        self.learning_rate = 0.01
        self.epochCount = 50

        self.data_x = data.data_x_minimal
        self.data_y = data.data_y_card

    def initializeModel(self):
        self.model = nn.Sequential(nn.Linear(self.n_input, self.n_hidden),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden, self.n_out),
                      nn.Sigmoid())

    def trainModel(self):
        print('Model training started')
        loss_function = nn.CrossEntropyLoss()#.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        for epoch in range(self.epochCount):
            if epoch%100==0:
                print(f'Model training progress: {round(100*epoch/self.epochCount,3)}%')
            pred_y = self.model(self.data_x)

            loss_Chosen = loss_function(pred_y, self.data_y)                           # Vai prognoztā kārts sakrīt ar spēlētāja izvēli
            
            self.model.zero_grad()   
            loss_Chosen.backward()  #Šeit loss_Chosen jāaizstāj ar to, pēc kura grib trenēt

            optimizer.step()
        print('Model training complete')

    def turnInputStateIntoArray(self, cardsOnHand, firstCardTable, secondCardTable):
        array = np.zeros(26*3)
        for card in cardsOnHand:
            array[card] = 1
        if firstCardTable != None and firstCardTable != 999:
            array[firstCardTable+26] = 1
        if secondCardTable != None and secondCardTable != 999:
            array[secondCardTable+52] = 1
        return array

    def removeSpentCard(self, cardsOnHand, spentCardNumber):
        newHand = []
        for card in cardsOnHand:
            if card !=spentCardNumber:
                newHand.append(card)
        return newHand

    def tensorToCard(self, tensor):
        chosenCardVal = max(tensor)
        # Ja atļauti bija tikai slikti varianti, labākajai izvēlei būs negatīva vērtība un tik izvēlēta pirmā no aizliegtajām kārtīm, jo tām ir 0
        if chosenCardVal == 0:
            tensor *=-1
            chosenCardVal = min(tensor)
        for i in range(len(tensor)):
            if tensor[i]==chosenCardVal:
                return zole.cards.all_cards[i]
    
    def playCard(self, input):
        outputTensor = self.model(torch.FloatTensor(input))
        self.output = outputTensor
        return self.tensorToCard(outputTensor)
    
    def formatInput(self, player:Bot, trick:Trick):
        hand = player.hand.as_index_array()
        firstCardTable = trick.first_card().i
        secondCardTable = trick.cards[1].i
        return self.turnInputStateIntoArray(hand, firstCardTable, secondCardTable)

class Experiment9(Bot):
    bot_name = 'Experiment9'
    
    def __init__(self, player_name: str):
        super().__init__(player_name)
        self.rand = Random()

        pathName = 'Resources/Models/'+Experiment9.bot_name+'.pkl'
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
            card_to_play = self.network.playCard(input)     
            if card_to_play in valid_cards:
                event.play_card(card_to_play)
            else:
                event.play_card(valid_cards[self.rand.randint(0, len(valid_cards) - 1)])
        elif event.name == EventNames.TrickEndedEvent:
            trick = event.trick
            taker_of_the_trick = trick.tacker()
            trick_score = trick.score()
            
        elif event.name == EventNames.PartyEndedEvent:
            playerResults = event.party_results.player_results
            

        else:
            print(f'Bot {self.bot_name} not able to handle event {event.name}')