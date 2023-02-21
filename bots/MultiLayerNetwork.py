from bots.bot import Bot
from random import Random
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode
import zole.cards

import json
import numpy as np
import torch
import torch.nn as nn
import pandas as pd

class Network:
    def __init__(self):
        self.gameListFiltered =[]
        self.n_input = 26*3
        self.n_hidden = 26*2
        self.n_out = 26
        self.learning_rate = 0.01
        self.epochCount = 5000

    def importData(self):
        with open("Resources/tables.log", "r") as read_file:
            self.data = json.load(read_file)

    def initiateModel(self):
        self.model = nn.Sequential(nn.Linear(self.n_input, self.n_hidden),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden, self.n_out),
                      nn.Sigmoid())

    def trainModel(self):
        loss_function = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

        losses_Chosen = []
        losses_Available = []
        losses_Allowed = []
        losses_Combined = []
        for epoch in range(self.epochCount): #
            pred_y = self.model(self.data_x)

            loss_Chosen = loss_function(pred_y, self.data_y_Chosen)                           # Vai prognoztā kārts sakrīt ar spēlētāja izvēli
            losses_Chosen.append(loss_Chosen.item())                                     # Šīs divas rindas tikai priekš vizualizācijas nākamajā sadaļā, izņemot to losses list, kurš izmantots .backward funkcijai

            loss_Available = loss_function(pred_y, self.data_y_Available)               # Vai prognozētā ir spēlētājam rokā
            losses_Available.append(loss_Available.item())

            loss_Allowed = loss_function(pred_y, self.data_y_Allowed)                   # Vai prognozētā ir atļauta pēc noteikumiem
            losses_Allowed.append(loss_Allowed.item())
            
            loss_Combined = loss_function(pred_y, self.data_y_Allowed*self.data_y_Available) # Vai prognozētā ir gan atļauta, gan spēlētājam rokā
            losses_Combined.append(loss_Allowed.item())

            self.model.zero_grad()   
            loss_Chosen.backward()  #Šeit loss_Chosen jāaizstāj ar to, pēc kura grib trenēt

            optimizer.step()

    def filterGameList(self):
        for i in range(len(self.data['gamelist'])):
            gameType = self.data['gamelist'][i]['game']['type']
            if gameType != None:
                self.gameListFiltered.append(self.data['gamelist'][i])

    def turnInputStateIntoArray(self, cardsOnHand, firstCardTable, secondCardTable):
        array = np.zeros(26*3)
        for card in cardsOnHand:
            array[card] = 1
        if firstCardTable != None:
            array[firstCardTable+26] = 1
        if secondCardTable != None:
            array[secondCardTable+52] = 1
        return array

    def CardOnTableToAllowedCards(self, CardOnTable):
        allowedCards = np.zeros(26)
        if CardOnTable==None:
            return np.ones(26)
        elif CardOnTable<=13: #Trumps
            for i in range(14):
                allowedCards[i] = 1
        elif CardOnTable<=17: #Clubs
            for i in range(4):
                allowedCards[i+14] = 1
        elif CardOnTable<=21: #Spades
            for i in range(4):
                allowedCards[i+18] = 1
        elif CardOnTable<=25: #Hearts
            for i in range(4):
                allowedCards[i+22] = 1

        return allowedCards

    def removeSpentCard(self, cardsOnHand, spentCardNumber):
        newHand = []
        for card in cardsOnHand:
            if card !=spentCardNumber:
                newHand.append(card)
        return newHand
    
    def organizeData(self):
        self.data_x = []
        self.data_y_Chosen = []
        self.data_y_Allowed = []
        self.data_y_Available = []
        self.readableData = []
        for game in self.gameListFiltered:
            for player in range(3):
                curHand = game['game']['players'][player]['cards_dealt']
                for trick in game['game']['board']['tricks']:
                    if len(curHand)<=1:
                        break
                    firstCardTable = None
                    secondCardTable = None
                    y_Chosen = np.zeros(26)
                    y_Allowed = np.zeros(26)
                    y_Available = np.zeros(26)
                    for i in range(3):
                        if i == 1:
                            firstCardTable = trick['trick'][0][1]
                        if i == 2:
                            secondCardTable = trick['trick'][1][1]
                        if trick['trick'][i][0] == player:
                            y_Chosen[trick['trick'][i][1]] = 1
                            cardPlayed = trick['trick'][i][1]
                            break
                    #Šeit baigi daudz mainīgie, varbūt vajadzētu kko pārdomāt
                    self.readableData.append([curHand, firstCardTable, secondCardTable])
                    x = self.turnInputStateIntoArray(curHand, firstCardTable, secondCardTable)
                    self.y_Allowed = self.CardOnTableToAllowedCards(firstCardTable)
                    self.y_Available = x[:26] # pirmie 26 elementi, jeb rokā esošās kārtis
                    self.data_x.append(self.turnInputStateIntoArray(curHand, firstCardTable, secondCardTable))
                    self.data_y_Chosen.append(y_Chosen)
                    self.data_y_Allowed.append(y_Allowed)
                    self.data_y_Available.append(y_Available)
                    curHand = self.removeSpentCard(curHand, cardPlayed)
        self.data_x = torch.FloatTensor(np.array(self.data_x))
        self.data_y_Chosen = torch.FloatTensor(np.array(self.data_y_Chosen))
        self.data_y_Allowed = torch.FloatTensor(np.array(self.data_y_Allowed))
        self.data_y_Available = torch.FloatTensor(np.array(self.data_y_Available))

    def tensorToCard(self, tensor):
        maxVal = max(tensor)
        for i in range(len(tensor)):
            if tensor[i]==maxVal:
                return zole.cards.all_cards[i]
    
    def cardToInt(self, card:zole.cards.Card):
        if card==zole.cards.no_card:
            return None
        else:
            return card.i

    def cardsToIntArray(self, cards:zole.cards.Cards):
        newHand = []
        for card in cards:
            newHand.append(card.i)
        return newHand
    
    def playCard(self, hand : zole.cards.Cards, trick):
        #includes switching data types
        newHand = self.cardsToIntArray(hand)
        newFirstCard = self.cardToInt(trick.cards[0])
        newSecondCard = self.cardToInt(trick.cards[1])
        inputArray = self.turnInputStateIntoArray(newHand, newFirstCard, newSecondCard)
        inputTensor = torch.FloatTensor(np.array(inputArray))
        outputTensor = self.model(inputTensor)
        return self.tensorToCard(outputTensor)

class MultiLayerNetwork(Bot):
    bot_name = 'Multi Layer Network'

    def __init__(self, player_name: str):
        super().__init__(player_name)
        self.rand = Random()
        self.network = Network()
        self.network.importData()
        self.network.filterGameList()
        self.network.organizeData()
        self.network.initiateModel()
        self.network.trainModel()

    def handle_game_event(self, event: GameEvent):
        if event.name == EventNames.PartyStartedEvent:
            # my_cards = self.hand
            # party = event.party
            # TODO get my position in seating
            pass
        elif event.name == EventNames.SelectGameModeEvent:
            modes = [GameMode.PASS, GameMode.PACELT, GameMode.ZOLE, GameMode.MAZAZOLE]
            selected_game_mode = self.rand.choices(modes, [0.3, 0.4, 0.2, 0.1])[0]
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
            c1i = c2i = self.rand.randint(0, 9)
            while c1i == c2i:
                c2i = self.rand.randint(0, 9)
            discard_card1 = self.hand[c1i]
            discard_card2 = self.hand[c2i]
            event.discard_cards(discard_card1, discard_card2)
        elif event.name == EventNames.PlayCardEvent:
            trick = event.trick
            card_to_play = self.network.playCard(self.hand, trick)
            event.play_card(card_to_play)
        elif event.name == EventNames.TrickEndedEvent:
            trick = event.trick
            taker_of_the_trick = trick.tacker()
            trick_score = trick.score()
        elif event.name == EventNames.PartyEndedEvent:
            party_results = event.party_results
        else:
            print(f'Bot {self.bot_name} not able to handle event {event.name}')
