from bots.bot import Bot
from random import Random
from zole.game_events import GameEvent, EventNames
from zole.game_modes import GameMode
import zole.cards
from zole.trick import Trick
import zole.player
from bots.DataSetup import DataPaths
import numpy as np
import torch
import torch.nn as nn
import os.path as path

class MainNetwork:
    def __init__(self):
        self.gameListFiltered =[]
        self.n_input = 26*3+1
        self.n_hidden = 26*4
        self.n_out = 26
        self.learning_rate = 0.005
        self.epochCount = 400

        self.correctCount = 0
        self.incorrectCount = 0

    def initializeModel(self):
        self.model = nn.Sequential(nn.Linear(self.n_input, self.n_hidden),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden, self.n_hidden),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden, self.n_out),
                      nn.Sigmoid())

    def trainModel(self):
        print('Model training started')
        self.loss_function = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        data_x = torch.load(DataPaths.SIMPLE_TRAIN_X)
        data_y = torch.load(DataPaths.SIMPLE_TRAIN_Y)
        testData_x = torch.load(DataPaths.SIMPLE_TEST_X)
        testData_y = torch.load(DataPaths.SIMPLE_TEST_Y)
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
        print('Model training complete')

        for i in range (len(testData_x)):  #for debugging
            input = testData_x[i]
            output = self.model(input)
            expected = testData_y[i]
            loss = self.loss_function(output, expected)
            maxI = 0
            for i in range(26):
                if input[i]==1:
                    maxI=i
                    break
            if maxI>13:
                randomVar = 0  #breakpoint here for debugging

    def loss_masked(self, pred_y, y):
        masked_pred = torch.mul(pred_y, y)
        Loss = self.loss_function(masked_pred, y)
        return torch.mul(Loss, 26*len(y)/torch.sum(y))  #tā kā tiek ņemta vērā tikai daļa vērtību, jāsareizina lai loss būtu tādā mērogā, it kā būt visas

    def turnInputStateIntoArray(self, cardsOnHand, firstCardTable, secondCardTable, hasTrump):
        array = np.zeros(26*3+1)
        for card in cardsOnHand:
            array[card] = 1
        if firstCardTable != None and firstCardTable != 999:
            array[firstCardTable+26] = 1
        if secondCardTable != None and secondCardTable != 999:
            array[secondCardTable+52] = 1
        if hasTrump:
            array[78] = 1
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
        return self.tensorToCard(outputTensor)
    
    def formatInput(self, player:Bot, trick:Trick, validCards:zole.cards.Cards):
        hand = player.hand.as_index_array()
        firstCardTable = trick.first_card().i
        secondCardTable = trick.cards[1].i
        hasTrump =False
        for card in validCards:
            if card.is_trump:
                hasTrump = True
        return self.turnInputStateIntoArray(hand, firstCardTable, secondCardTable, hasTrump)

class Experiment25(Bot):
    bot_name = 'Experiment25'
    
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
            
            valid_cards = self.hand.get_valid_cards(trick.first_card())
            card_to_play = self.network.playCard(self, trick, valid_cards) 
            if self.hand.size==2 and trick.cards.size==1 and valid_cards.size==2:
                randomVariable = 0  #breakpoint here for debugging
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