from bots.bot import Bot
from random import Random
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode
import zole.cards
from zole.trick import Trick
import zole.player
from bots.DataSetup import DataPaths as data
from bots.DataSetup import stateEval_func
import numpy as np
import torch
import torch.nn as nn
import os.path as path
import math

class MainNetwork:
    def __init__(self):
        self.gameListFiltered =[]
        self.n_input = 26*3 + 3
        self.n_hidden = 26*2
        self.n_out = 26
        self.learning_rate = 0.01
        self.epochCount = 100

        self.correctCount = 0
        self.incorrectCount = 0

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



    def initializeModel(self):
        self.model = nn.Sequential(nn.Linear(self.n_input, self.n_hidden),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden, self.n_hidden),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden, self.n_out),
                      nn.Sigmoid())

    def trainModel(self):
        print('==========Model training started==========')
        self.loss_function = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        data_x = torch.load(data.TRAIN_X)
        data_y = torch.load(data.TRAIN_Y)
        testData_x = torch.load(data.TEST_X)
        testData_y = torch.load(data.TEST_Y)
        print('Data loaded')
        for epoch in range(self.epochCount):
            pred_y = self.model(data_x)
            loss = self.loss_function(pred_y, data_y)
            self.model.zero_grad()   
            loss.backward()
            self.optimizer.step()
            if (epoch+1)%10==0: #get loss with test data
                testPred_y = self.model(testData_x)
                loss = self.loss_function(testPred_y, testData_y)
                print('epoch - ' + str(epoch+1) + '; loss - ' + str(loss.item()))
        print('==========Model training complete==========')
        self.countPrecision(testData_x, testData_y)

    def countPrecision(self, testData_x, testData_y):
        dataLen = len(testData_x)
        correctCount=0
        for i in range(dataLen):
            input = testData_x[i]
            output = self.model(input)
            expected = testData_y[i]
            expectedChoice = torch.argmax(expected)
            Choice = torch.argmin(output)
            if Choice==expectedChoice:
                correctCount+=1
        loss = round(self.loss_function(self.model(testData_x), testData_y).item(), 3)
        overallPrecision = round(correctCount/dataLen*100, 5)
        print(f'Overll precision: {overallPrecision}; ' + 
              f'loss: {loss}')

    def setupSelfTraining(self):
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

    def selfTrain(self, evalDiff):
        evalDiff = (math.exp(evalDiff)-math.exp(-evalDiff))/(math.exp(evalDiff)+math.exp(-evalDiff))
        self.model.zero_grad()
        self.StateEval_Loss(evalDiff).backward()
        self.optimizer.step()

    def StateEval_Loss(self, evalDiff):
        return torch.mean(self.prevOutput*evalDiff)

    def turnInputStateIntoArray(self, cardsOnHand, firstCardTable, secondCardTable, hasTrump, firstPlayer, secondPlayer):
        array = np.zeros(26*3+3)
        for card in cardsOnHand:
            array[card] = 1
        if firstCardTable != None and firstCardTable != 999:
            array[firstCardTable+26] = 1
        if secondCardTable != None and secondCardTable != 999:
            array[secondCardTable+52] = 1
        if hasTrump:
            array[78] = 1
        array[79] = firstPlayer
        array[80] = secondPlayer
        return array

    def tensorToCard(self, tensor):
        chosenCardVal = max(tensor).item()
        if chosenCardVal==-1:
            return zole.cards.all_cards[Random.randint(0,25)]
        for i in range(len(tensor)):
            if tensor[i]==chosenCardVal:
                return zole.cards.all_cards[i]
    
    def playCard(self,player:Bot, trick:Trick, validCards:zole.cards.Cards):
        input = self.formatInput(player, trick, validCards)
        outputTensor = self.model(torch.FloatTensor(input))
        self.output = outputTensor
        outputTensor = torch.mul(outputTensor, torch.FloatTensor(np.array(validCards.as_input_array())))
        card = self.tensorToCard(outputTensor)
        while card not in validCards:
            outputTensor[card.i] = -1
            card = self.tensorToCard(outputTensor)
        self.prevOutput = outputTensor
        return self.tensorToCard(outputTensor)
    
    def formatInput(self, player:Bot, trick:Trick, validCards:zole.cards.Cards):
        hand = player.hand.as_index_array()
        firstCardTable = trick.first_card().i
        secondCardTable = trick.cards[1].i
        hasTrump = False
        firstPlayerRoleInput = 0
        secondPLayerRoleInput = 0
        for card in validCards:
            if card.is_trump:
                hasTrump = True
        if trick.played_by[0] !=None:
            if trick.played_by[0].role == player.role and firstCardTable !=999:
                firstPlayerRoleInput = 1
            if trick.played_by[1] !=None:
                if trick.played_by[1].role == player.role and secondCardTable !=999:
                    secondPLayerRoleInput = 1
        return self.turnInputStateIntoArray(hand, firstCardTable, secondCardTable, hasTrump, firstPlayerRoleInput, secondPLayerRoleInput)
    

class Experiment42(Bot):
    bot_name = 'Experiment42'
    
    def __init__(self, player_name: str):
        super().__init__(player_name)
        self.rand = Random()
        self.prevStateEval = None
        self.spentCards = np.zeros(26)



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
        
        self.network.setupSelfTraining()
        

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
            self.spentCards[self.hand[8].i] = 1
            self.spentCards[self.hand[9].i] = 1
            event.discard_cards(self.hand[9], self.hand[8])

        elif event.name == EventNames.PlayCardEvent:
            trick = event.trick

            curStateEval = stateEval_func(self)
            if self.prevStateEval!=None:
                stateDiff = self.prevStateEval - curStateEval

                self.network.selfTrain(stateDiff)
            self.prevStateEval = curStateEval
            
            valid_cards = self.hand.get_valid_cards(trick.first_card())
            card_to_play = self.network.playCard(self, trick, valid_cards)     
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
            for card in trick.cards:
                self.spentCards[card.i] = 1
            
        elif event.name == EventNames.PartyEndedEvent:
            playerResults = event.party_results.player_results
            self.prevStateEval = None
            self.spentCards = np.zeros(26)

        else:
            print(f'Bot {self.bot_name} not able to handle event {event.name}')