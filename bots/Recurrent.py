from bots.bot import Bot
from random import Random
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode
import zole.cards
import bots.stateEval
import bots.NN_base as NN_base

import json
import numpy as np
import torch
import torch.nn as nn
import pandas as pd

class MainNetwork:
    def __init__(self):
        self.gameListFiltered =[]
        self.n_input = 26*4 + 7 + 2
        self.n_hidden1 = 200
        self.n_hidden2 = 400
        self.n_hidden3 = 200
        self.n_out = 26
        self.learning_rate = 0.05
        self.epochCount = 50

        self.data_x = data.data_x
        self.data_y = data.data_y_card
        self.data_mask = data.data_mask

        self.retrainStateEval_gameCount = 1500

    def importData(self):
        with open("Resources/tables.log", "r") as read_file:
            self.data = json.load(read_file)

    def initiateModel(self):
        self.model = nn.Sequential(nn.Linear(self.n_input, self.n_hidden1),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden1, self.n_hidden2),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden2, self.n_hidden3),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden3, self.n_out),
                      nn.ReLU())
        
    def forward(self, x, mask):

        output = self.model(x)
        maskedOutput = output*mask
        softM = nn.Softmax()
        return softM(maskedOutput)

    def trainModel(self):
        loss_function = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        for epoch in range(self.epochCount):
            pred_y = self.forward(self.data_x, self.data_mask)

            loss_Chosen = loss_function(pred_y, self.data_y)                           # Vai prognoztā kārts sakrīt ar spēlētāja izvēli
            
            self.model.zero_grad()   
            loss_Chosen.backward()  #Šeit loss_Chosen jāaizstāj ar to, pēc kura grib trenēt

            optimizer.step()

    def setupSelfTraining(self):
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

    def selfTrain(self, evalDiff):
        self.model.zero_grad()
        self.StateEval_Loss(evalDiff).backward()
        self.optimizer.step()

    def StateEval_Loss(self, evalDiff:torch.FloatTensor):
        return torch.mean(self.prevOutput*evalDiff.item())

    def turnInputStateIntoArray(self, cardsOnHand, firstCardTable, secondCardTable):
        array = np.zeros(26*3)
        for card in cardsOnHand:
            array[card] = 1
        if firstCardTable != None:
            array[firstCardTable+26] = 1
        if secondCardTable != None:
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
    
    def playCard(self, input, validCards:zole.cards.Cards):
        mask = np.zeros(26)
        for card in validCards.cards:
            if card!=zole.cards.no_card:
                mask[card.i] = 1
        outputTensor = self.forward(torch.FloatTensor(input), torch.FloatTensor(mask))
        self.prevOutput = outputTensor
        return self.tensorToCard(outputTensor), outputTensor

class Recurrent(Bot):
    bot_name = 'Recurrent bot'
    
    def __init__(self, player_name: str):
        super().__init__(player_name)
        self.rand = Random()

        self.network = MainNetwork()
        #self.network.importData()
        self.network.initiateModel()
        self.network.trainModel()
        self.network.setupSelfTraining()

        self.stateEvalNetwork = bots.stateEval.stateEvalNN()
        self.stateEvalNetwork.initializeModel()
        self.stateEvalNetwork.trainModel()
        self.prevStateEval = None
        self.archives = []

    def handle_game_event(self, event: GameEvent):
        if event.name == EventNames.PartyStartedEvent:
            self.spentCards = np.zeros(26)
            # my_cards = self.hand
            # party = event.party
            # TODO get my position in seating
            pass
        elif event.name == EventNames.SelectGameModeEvent:
            modes = [GameMode.PASS, GameMode.PACELT, GameMode.ZOLE, GameMode.MAZAZOLE]
            selected_game_mode = self.rand.choices(modes, [0.5, 0.5, 0, 0])[0]
            #Te vajag atsevisku log, kurā piefiksē veikto izvēli, kārtis rokā, un kurā roka bija
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
            
            c1i = 9
            c2i = 8 
            discard_card1 = self.hand[c1i]
            discard_card2 = self.hand[c2i]
            event.discard_cards(discard_card1, discard_card2)
        elif event.name == EventNames.PlayCardEvent:
            trick = event.trick
            input = NN_base.formatInput(self, trick)
            self.archives.append(NN_base.Archive(input))
            curStateEval = self.stateEvalNetwork.model(torch.FloatTensor(input))[0]
            stateDiff = torch.zeros(1, requires_grad=True)
            if self.prevStateEval!=None:
                stateDiff = curStateEval-self.prevStateEval
                #šajā ir problēma ar .backwards
                self.network.selfTrain(stateDiff)
            self.prevStateEval = curStateEval
            valid_cards = self.hand.get_valid_cards(trick.first_card())
            card_to_play, outputTensor_debug = self.network.playCard(input, valid_cards)
            if card_to_play in valid_cards:
                event.play_card(card_to_play)
            else:
                event.play_card(valid_cards[self.rand.randint(0, len(valid_cards) - 1)])
        elif event.name == EventNames.TrickEndedEvent:
            trick = event.trick
            taker_of_the_trick = trick.tacker()
            trick_score = trick.score()

            for card in trick.cards:
                self.spentCards[card.i] = 1
            
        elif event.name == EventNames.PartyEndedEvent:
            self.prevStateEval = None
            i = len(self.archives)-1
            playerResults = event.party_results.player_results
            
            for playerResult in playerResults:
                if playerResult.player == self:
                    result = playerResult.score_change
            result = NN_base.calculateRelativeResult(self, result)
            while i<=0 and not self.archives[i].getOutputBool():
                self.archives[i].setOutput(result)
                i-=1
                #self.stateEvalNetwork.trainOnOne(self.archives[i].input, y = self.archives[i].output)
            if len(self.archives) >=self.network.retrainStateEval_gameCount*8+1:
                #ik pa game_count spēlēm pārtrenē stateEval uz iepriekšējo spēļu datiem, reseto arhīvu
                self.stateEvalNetwork.retrainModel(self.archives)
                #self.network.initiateModel()
                #self.archives = []
                #self.points = 0
                #self.next_player.points = 0
                #self.next_player.next_player.points = 0
                self.network.retrainStateEval_gameCount += self.network.retrainStateEval_gameCount
        else:
            print(f'Bot {self.bot_name} not able to handle event {event.name}')
