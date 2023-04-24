import zole.cards
import zole.player
from zole.trick import Trick
from bots.bot import Bot
from zole.player import PlayerCircle, Player
from zole.cards import all_cards, no_card
import os.path as path
import json
import numpy as np
import torch
import random as rand

def givePlayersRoles(players: zole.player.PlayerCircle, gameType, type_user):
    for player in players:
        player.role = zole.player.PlayerRoles.MAZAIS
    if gameType=='t':
        players[type_user].role = zole.player.PlayerRoles.LIELAIS
    elif gameType=='d':
        for player in players:
            player.role = zole.player.PlayerRoles.GALDINS
    elif gameType=='b':
        players[type_user].role = zole.player.PlayerRoles.ZOLE
    elif gameType=='s':
        players[type_user].role = zole.player.PlayerRoles.MAZAZOLE
        
    return players

def cardArr_To_Cards(cardsArr):
    cardsClass = zole.cards.Cards(len(cardsArr))
    for card in cardsArr:
        cardsClass.add_card(zole.cards.all_cards[card])
    return cardsClass

def removeSpentCard(cardsOnHand, spentCardNumber):
    newHand = []
    for card in cardsOnHand:
        if card !=spentCardNumber:
            newHand.append(card)
    return newHand

def createFullTrick_FromData(jsonTrick, players : zole.player.PlayerCircle):
    trick = Trick()
    for i in range(3):
        trick.play_card(zole.cards.all_cards[jsonTrick['trick'][i][1]], players[jsonTrick['trick'][i][0]])
    return trick

def CardOnTableToAllowedCards(CardOnTable):
    allowedCards = np.zeros(26)
    if CardOnTable==None or CardOnTable==999:
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

class gameState:
    def __init__(self, hand, player:zole.player.Player, firstCardTable:zole.cards.Card, secondCardTable:zole.cards.Card,
                  pointsYou, pointsThem, spentCards, gameMode ='', result = 0):
        self.player = player
        self.hand = hand
        self.firstCardTable = firstCardTable
        self.secondCardTable = secondCardTable
        self.GameMode = gameMode
        self.pointsYou = pointsYou
        self.pointsThem = pointsThem
        self.resultAbsolute = result
        self.spentCards = spentCards
        self.mode_role_tensor = np.zeros(7)

    def calculateRoleInput(self):
        playerRoleArr = [self.player.role, self.player.next_player.role, self.player.next_player.next_player.role]
        if zole.player.PlayerRoles.LIELAIS in playerRoleArr:                                   #parasts
            if self.player.role == zole.player.PlayerRoles.LIELAIS:
                self.mode_role_tensor[0] = 1.0
            else:
                self.mode_role_tensor[1] = 1.0

        elif all(role == zole.player.PlayerRoles.GALDINS for role in playerRoleArr):            #galdiņš
            self.mode_role_tensor[2] = 1.0

        elif zole.player.PlayerRoles.ZOLE in playerRoleArr:                                     #zole
            if self.player.role == zole.player.PlayerRoles.ZOLE:
                self.mode_role_tensor[3] = 1.0
            else:
                self.mode_role_tensor[4] = 1.0

        elif zole.player.PlayerRoles.MAZAZOLE in playerRoleArr:                                  #mazā zole
            if self.player.role == zole.player.PlayerRoles.MAZAZOLE:
                self.mode_role_tensor[5] = 1.0
            else:
                self.mode_role_tensor[6] = 1.0

    def calculate_result(self):
        if self.GameMode == 't':                                      #parasts
            if self.player.role == zole.player.PlayerRoles.LIELAIS:
                self.resultRelative = (self.resultAbsolute+8)/14
                self.mode_role_tensor[0] = 1.0
            else:
                self.resultRelative = (self.resultAbsolute+3)/7
                self.mode_role_tensor[1] = 1.0

        elif self.GameMode == 'd':                                     #galdiņš
            self.resultRelative = (self.resultAbsolute+8)/16
            self.mode_role_tensor[2] = 1.0

        elif self.GameMode == 'b':                                     #zole
            if self.player.role == zole.player.PlayerRoles.ZOLE:
                self.resultRelative = (self.resultAbsolute+16)/30
                self.mode_role_tensor[3] = 1.0
            else:
                self.resultRelative = (self.resultAbsolute+7)/15
                self.mode_role_tensor[4] = 1.0

        elif self.GameMode == 's':                                      #mazā zole
            if self.player.role == zole.player.PlayerRoles.MAZAZOLE:
                self.resultRelative = (self.resultAbsolute+14)/26
                self.mode_role_tensor[5] = 1.0
            else:
                self.resultRelative = (self.resultAbsolute+6)/13
                self.mode_role_tensor[6] = 1.0

    def stateToInputArray(self):
        #26 priekš hand, spent, first, second
        #6 priekš game mode (parasts lielais, parasts mazais, zole lielais, zole mazais, galdins, mazá zole lielas, mazá zole mazais)
        # un pa vienam priekš pointsYou, pointsThem
        arr = np.zeros(26*4 + 7 + 2)
        for card in self.hand:
            arr[card.i] = 1.0
        for i in range(26):
            arr[26+i] = self.spentCards[i]
        if self.firstCardTable in zole.cards.all_cards:
            arr[26*2+self.firstCardTable.i] = 1.0
        if self.secondCardTable in zole.cards.all_cards:
            arr[26*3+self.secondCardTable.i] = 1.0
        for i in range(len(self.mode_role_tensor)):
            arr[26*4+i] = self.mode_role_tensor[i]
        arr[26*4+7+0] = self.pointsYou/120
        arr[26*4+7+1] = self.pointsThem/120
        return np.array(arr)
    
    def stateToInputArray_minimal(self):
        array = np.zeros(26*3)
        for card in self.hand:
            array[card.i] = 1
        if self.firstCardTable != None and self.firstCardTable != no_card:
            array[self.firstCardTable.i+26] = 1
        if self.secondCardTable != None and self.secondCardTable != no_card:
            array[self.secondCardTable.i+52] = 1
        return array
    
    def stateToInputArray_minimal2(self):
        array = np.zeros(26*3)
        for card in self.hand:
            array[card.i] = 1
        if self.firstCardTable != None and self.firstCardTable != no_card:
            array[self.firstCardTable.i+26] = 1
        if self.secondCardTable != None and self.secondCardTable != no_card:
            array[self.secondCardTable.i+52] = 1
        return array
    
    def stateToOutputArray_Result(self):
        return np.array(self.resultRelative) #tikai viens elements no 0 līdz 1

def jsonToTrainData(dataFolder, gametypesAllowed):
    X = 'Resources/'+ dataFolder +'/data_x'
    X_MIN = 'Resources/'+ dataFolder +'/data_x_minimal'
    RESULT = 'Resources/'+ dataFolder +'/data_y_result'
    CARD = 'Resources/'+ dataFolder +'/data_y_card'
    MASK = 'Resources/'+ dataFolder +'/data_mask'
    #Opens the chosen folders data file
    with open("Resources/"+dataFolder+"/data.json", "r") as read_file:
        data = json.load(read_file)

    #filters the game list to include only allowed gameTypes
    gameListFiltered =[]
    for i in range(len(data['gamelist'])):
        gameType = data['gamelist'][i]['game']['type']
        if gameType in gametypesAllowed:
            gameListFiltered.append(data['gamelist'][i])

    print('Data formatting started')
    data_x = []
    data_x_minimal = []
    data_y_result = []
    data_y_card = []
    data_mask = []
    fileNum = 0
    len_forProgress = len(gameListFiltered)
    count = 0
    for game in gameListFiltered:
        count+=1
        if count%20000==0:
            print(f'Data formatting progress: {round(count/len_forProgress,3)*100}%')
        for player in range(3): 
            gameResult = game['game_points'][player]
            # if gameResult<0:  #filter games where the player didn't win
            #     continue
            gameType = game['game']['type']
            players = PlayerCircle(Player('1'), Player('2'), Player('3'))
            players = givePlayersRoles(players, gameType, game['game']['type_user'])
            curHand = cardArr_To_Cards(game['game']['players'][player]['cards_dealt'])
            pointsYou = 0
            pointsThem = 0
            spentCards = np.zeros(26)
            for trick in game['game']['board']['tricks']:
                #if only 1 card, stop
                if len(curHand)<=1:
                    break

                #go through the trick until find your card
                firstCardTable = no_card
                secondCardTable = no_card
                for i in range(3):
                    if trick['trick'][i][0] == player:
                        cardPlayed = all_cards[trick['trick'][i][1]]
                        break
                    if i == 0:
                        firstCardTable = all_cards[trick['trick'][0][1]]
                    if i == 1:
                        secondCardTable = all_cards[trick['trick'][1][1]]

                trickClass = createFullTrick_FromData(trick, players)
                #turn the gathered information into input, output tensors 
                state = gameState(curHand, players[player], firstCardTable, secondCardTable, pointsYou, pointsThem, spentCards, gameType, gameResult)
                state.calculate_result()

                y_card = np.zeros(26)
                for i in range(26):
                    if i==cardPlayed:
                        y_card[i]=state.resultRelative
                
                y_Available = np.zeros(26)
                for card in curHand:
                    y_Available[card.i] = 1
                trickClass = createFullTrick_FromData(trick, players)
                
                #if len(curHand)>4: #trickClass.tacker()==players[player] and
                cardsToIntArray(curHand)
                x = np.zeros(26*3+1+2)
                x_tensor = turnInputStateIntoArray(cardsToIntArray(curHand), firstCardTable.i, secondCardTable.i, array = x)
                if hasTrump(curHand):
                    x_tensor[26*3] = 1
                if players[0].role == players[player].role and firstCardTable!=no_card:
                    x_tensor[26*3+1] = 1
                if players[1] == players[player].role and secondCardTable != no_card:
                    x_tensor[26*3+2] = 1
                data_x.append(x_tensor)
                data_y_result.append(state.stateToOutputArray_Result())
                data_y_card.append(y_card)
                data_mask.append(CardOnTableToAllowedCards(firstCardTable.i)*y_Available)

                #change the state for the next iteration, remove played card, add points from this trick, add spent cards to spentCards[]
                curHand = removeSpentCard(curHand, cardPlayed)
                for card in trickClass.cards:
                    spentCards[card.i] = 1
                trickpoints = trickClass.score()
                trickTaker = trickClass.tacker()
                if trickTaker == players[player] or trickTaker.role==players[player].role:
                    pointsYou+=trickpoints
                else:
                    pointsThem+=trickpoints
                if len(data_x) >= 1000000:
                    data_x = torch.FloatTensor(np.array(data_x))
                    data_x_minimal = torch.FloatTensor(np.array(data_x_minimal))
                    data_y_result = torch.FloatTensor(np.array(data_y_result))
                    data_y_result = torch.reshape(data_y_result, [len(data_y_result), 1])
                    data_y_card = torch.FloatTensor(np.array(data_y_card))
                    data_mask = torch.FloatTensor(np.array(data_mask))
                    torch.save(data_x, X + str(fileNum))
                    torch.save(data_x_minimal, X_MIN + str(fileNum))
                    torch.save(data_y_result, RESULT + str(fileNum))
                    torch.save(data_y_card, CARD + str(fileNum))
                    torch.save(data_mask, MASK + str(fileNum))
                    data_x = [] 
                    data_x_minimal = []
                    data_y_result = []
                    data_y_card = []
                    data_mask = []
                    print("part " + str(fileNum) + " of data saved")
                    fileNum+=1

def hasTrump(cards:zole.cards.Cards):
    for card in cards:
        if card.is_trump:
            return True
    return False

def tensorToCard(tensor):
    maxVal = max(tensor)
    for i in range(len(tensor)):
        if tensor[i]==maxVal:
            return zole.cards.all_cards[i]
    
def cardToInt(card:zole.cards.Card):
    if card==zole.cards.no_card:
        return None
    else:
        return card.i

def cardsToIntArray(cards:zole.cards.Cards):
    newHand = []
    for card in cards:
        newHand.append(card.i)
    return newHand

def cardsToTensor(cards:zole.cards.Cards):
    tensor = np.zeros(26)
    for card in cards:
        tensor[card.i] = 1
    return torch.FloatTensor(tensor)

def intArrayToTensor(cards):
    return torch.FloatTensor(intArrayToIndexArr(cards))

def intArrayToIndexArr(cards):
    arr = np.zeros(26)
    for card in cards:
        arr[card] = 1
    return arr

def indexArrToIntArr(arr):
    cards = []
    for i in range(26):
        if arr[i]==1:
            cards.append(i)
    return cards

def turnInputStateIntoArray(cardsOnHand, firstCardTable, secondCardTable, array = np.zeros(26*3)):
    for card in cardsOnHand:
        array[card] = 1
    if firstCardTable != zole.cards.no_card:
        array[firstCardTable+26] = 1
    if secondCardTable != zole.cards.no_card:
        array[secondCardTable+52] = 1
    return array

def getPoints(player: zole.player.Player):
    pointsYou = 0
    pointsThem = 0
    playerArr = [player, player.next_player, player.next_player.next_player]
    if playerArr[0].role == zole.player.PlayerRoles.GALDINS:
        pointsYou = playerArr[0].tricks_taken*(120/8)
        pointsThem = (playerArr[1].tricks_taken + playerArr[2].tricks_taken)/2*(120/8)
    else:
        for player in playerArr:
            if player.role==playerArr[0].role:
                pointsYou += player.tricks_score
            else:
                pointsThem += player.tricks_score
    return pointsYou, pointsThem

def formatInput(player:Bot, trick:Trick):
    hand = player.hand
    firstCardTable = trick.first_card()
    secondCardTable = trick.cards[1]
    pointsYou, pointsThem = getPoints(player)
    state = gameState(hand, player, firstCardTable, secondCardTable, pointsYou, pointsThem, player.spentCards)
    state.calculateRoleInput()
    return state.stateToInputArray()

class Archive:
    def __init__(self, input):
        self.input = input
        self.output = []

    def setDiscardInput(self, hand, place):
        self.discardOutput = np.zeros(26+3)
        for card in hand:
            self.discardOutput[card.i] = 1
        self.discardOutput[26+place] = 1

    def setOutput(self, output):
        self.output = output

    def getOutputBool(self):
        if self.output==[]: True
        else: False


def calculateRelativeResult(player, resultAbsolute):
    playerRoleArr = [player.role, player.next_player.role, player.next_player.next_player.role]
    if zole.player.PlayerRoles.LIELAIS in playerRoleArr:                                   #parasts
        if player.role == zole.player.PlayerRoles.LIELAIS:
            return (resultAbsolute+8)/14
        else:
            return (resultAbsolute+3)/7

    elif all(role == zole.player.PlayerRoles.GALDINS for role in playerRoleArr):            #galdiņš
        return (resultAbsolute+8)/16

    elif zole.player.PlayerRoles.ZOLE in playerRoleArr:                                     #zole
        if player.role == zole.player.PlayerRoles.ZOLE:
            return (resultAbsolute+16)/30
        else:
            return (resultAbsolute+7)/15

    elif zole.player.PlayerRoles.MAZAZOLE in playerRoleArr:                                  #mazā zole
        if player.role == zole.player.PlayerRoles.MAZAZOLE:
            return (resultAbsolute+14)/26
        else:
            return (resultAbsolute+6)/13

def stateEval_func(player : Player):
    pointsYou, pointsThem = getPoints(player)
    cardsLeft = np.zeros(26)
    pointsLeftCoef = (120-pointsYou-pointsThem)/120
    pointDiffCoef = (pointsYou-pointsThem+120)/240
    for i in range(len(player.spentCards)):
        if player.spentCards[i]==0:
            cardsLeft[i]=1
    trumpsLeft = cardsLeft[:14]
    cardValues = np.zeros(26)
    value = 0
    for i in range(sum(trumpsLeft.astype(int))):
        if trumpsLeft[13-i]==1:
            cardValues[13-i]=value
            value+=1
    totalValue = sum(cardValues)
    personalValue = 0
    for card in player.hand:
        personalValue+=cardValues[card.i]
    if totalValue!=0:
        if player.role == zole.player.PlayerRoles.MAZAIS:
            personalValueCoef = (personalValue+(totalValue-personalValue)/2)/totalValue
        else:
            personalValueCoef = personalValue/totalValue
    else: personalValueCoef = 0
    stateEval = personalValueCoef*pointsLeftCoef+pointDiffCoef*(1-pointsLeftCoef)
    if player.role==zole.player.PlayerRoles.GALDINS:
        return 1-stateEval
    else:
        return stateEval
    
def generateFullHandData(dataPaths, dataAmount):
    generateHandData(round(dataAmount*0.7,0), dataPaths.TEST_X, dataPaths.TEST_Y)
    generateHandData(round(dataAmount*0.3,0), dataPaths.TRAIN_X, dataPaths.TRAIN_Y)

def generateHandData(dataAmount, savePath_x, savePath_y):
    data_x = []
    data_y = []
    while len(data_x)<dataAmount:
        handLen = rand.randint(1,8)
        list_n = [rand.randint(0,25) for i in range(handLen)]
        while len(list_n) != len(set(list_n)):
            list_n = [rand.randint(0,25) for i in range(handLen)]
        tensor = intArrayToIndexArr(list_n)
        data_y.append(tensor)
        tensor = np.concatenate((tensor, np.zeros(52)))
        data_x.append(tensor)
        if len(tensor) !=26:
            pass
    data_x = np.array(data_x)
    data_y = np.array(data_y)
    data_x = torch.FloatTensor(data_x)
    data_y = torch.FloatTensor(data_y)
    torch.save(data_x, savePath_x)
    torch.save(data_y, savePath_y)

def generateSimpleFullData(paths, cardAmount, dataAmount, cardAmountMin = None, cardsOnTable = 2, cardsOnTableMin = None):
    print("----------Generating train data----------")
    generateSimpleData(cardAmount, round(dataAmount*0.7,0), paths.TRAIN_X, paths.TRAIN_Y, cardAmountMin, cardsOnTable, cardsOnTableMin)
    print("----------Generating test data----------")
    generateSimpleData(cardAmount, round(dataAmount*0.3,0), paths.TEST_X, paths.TEST_Y, cardAmountMin, cardsOnTable, cardsOnTableMin)

def generateSimpleData(cardAmountMax, dataAmount, x_savePath, y_savePath, cardAmountMin = None, cardsOnTableMax = 2, cardsOnTableMin = None):
    data_x = []
    data_y = []
    count = 0
    printTimes = 5
    printInterval = round(dataAmount/printTimes, 0)
    curLen = 0
    attemptCount = 0
    cardAmount = cardAmountMax
    cardsOnTable = cardsOnTableMax
    while curLen<dataAmount:
        if cardAmountMin != None: 
            cardAmount = rand.randint(cardAmountMin, cardAmountMax)
        if cardsOnTableMin != None:
            cardsOnTable = rand.randint(cardsOnTableMin, cardsOnTableMax)

        attemptCount+=1
        list_n = [rand.randint(0,25) for i in range(cardAmount+cardsOnTable)]
        while len(list_n) != len(set(list_n)):
            list_n = [rand.randint(0,25) for i in range(cardAmount+cardsOnTable)]
        cardObj_OnHand = []
        cardI_OnHand = []
        firstCardTable = all_cards[list_n[0]]
        secondCardTable = all_cards[list_n[1]]
        for i in range(cardsOnTable,cardsOnTable+cardAmount):
            cardI_OnHand.append(list_n[i])
            cardObj_OnHand.append(all_cards[list_n[i]])
        
        allowedArr = CardOnTableToAllowedCards(firstCardTable.i)
        availableArr = intArrayToIndexArr(cardI_OnHand)
        legalArr = allowedArr*availableArr
        legalCards = indexArrToIntArr(legalArr)
        if sum(legalArr)==0:
            legalArr = availableArr
            legalCards = cardI_OnHand
        correctCards = []
        if cardsOnTable==2 and zole.cards.new_card_is_stronger(firstCardTable, secondCardTable):
            strongestCard = secondCardTable
        else:
            strongestCard = firstCardTable
        for card in legalCards:
            if zole.cards.new_card_is_stronger(strongestCard, all_cards[card]):
                correctCards.append(card)

        if len(correctCards)==1:  #ja vajag lai ir tieši viena derīga
        #if len(correctCards)!=0: # ja ir vairākas atļutas, pareizā ir vājākā no atļautajā
            #correctCards = [max(correctCards)]  #šis arī
            y = np.zeros(26)
            hasTrump = False
            hasQueen = False
            hasJack = False
            hasAce = False
            for card in correctCards:
                y[card] = 1
                if all_cards[card].is_trump:
                    hasTrump = True
                if all_cards[card].rank=='A':
                    hasAce = True
                if all_cards[card].rank=='Q':
                    hasQueen = True
                if all_cards[card].rank=='J':
                    hasJack = True
            appendAmount = 1  # lai mākslīgi izmainītu proporciju retākām situācijām
            if hasTrump==False:
                appendAmount+=1
            #if hasTrump==False and hasAce==False:
            #    appendAmount+=1
            if hasTrump==True and hasQueen==False:
                appendAmount+=1
                if hasJack==False:
                    appendAmount+=1

            x = np.zeros(26*3+1)
            x_tensor = turnInputStateIntoArray(cardI_OnHand, firstCardTable.i, secondCardTable.i, x)
            if hasTrump:
                x_tensor[26*3] = 1
            for i in range(appendAmount):
                data_x.append(x_tensor)
                data_y.append(y)
            curLen = len(data_x)
            if curLen%printInterval<appendAmount:
                print(f'Data generation progress: {round(curLen/dataAmount,3)*100}%')
            #if attemptCount%10000==0:  
                #print(f'attemptCount: {attemptCount}, success percentage: {curLen/attemptCount}')
    data_x = torch.FloatTensor(np.array(data_x))
    data_y = torch.FloatTensor(np.array(data_y))
    torch.save(data_x, x_savePath)
    torch.save(data_y, y_savePath)
    return data_x, data_y

def generateSimple2FullData(paths, cardAmount, dataAmount, cardAmountMin = None, cardsOnTable = 2, cardsOnTableMin = None):
    print("----------Generating train data----------")
    generateSimple2Data(cardAmount, round(dataAmount*0.7,0), paths.TRAIN_X, paths.TRAIN_Y, cardAmountMin, cardsOnTable, cardsOnTableMin)
    print("----------Generating test data----------")
    generateSimple2Data(cardAmount, round(dataAmount*0.3,0), paths.TEST_X, paths.TEST_Y, cardAmountMin, cardsOnTable, cardsOnTableMin)

def generateSimple2Data(cardAmountMax, dataAmount, x_savePath, y_savePath, cardAmountMin = None, cardsOnTableMax = 2, cardsOnTableMin = None):
    data_x = []
    data_y = []
    printTimes = 5
    printInterval = round(dataAmount/printTimes, 0)
    curLen = 0
    attemptCount = 0
    cardAmount = cardAmountMax
    cardsOnTable = cardsOnTableMax
    while curLen<dataAmount:
        if cardAmountMin != None: 
            cardAmount = rand.randint(cardAmountMin, cardAmountMax)
        if cardsOnTableMin != None:
            cardsOnTable = rand.randint(cardsOnTableMin, cardsOnTableMax)

        playerRoles = [1,0,0]
        rand.shuffle(playerRoles)
        selfRole = playerRoles[cardsOnTable]
        firstPlayerRole = playerRoles[0]
        if cardsOnTable == 1:
            secondPlayerRole = playerRoles[2]
        if cardsOnTable == 2:
            secondPlayerRole = playerRoles[1]
        attemptCount+=1



        list_n = [rand.randint(0,25) for i in range(cardAmount+cardsOnTable)]
        while len(list_n) != len(set(list_n)):
            list_n = [rand.randint(0,25) for i in range(cardAmount+cardsOnTable)]

        cardObj_OnHand = []
        cardI_OnHand = []
        firstCardTable = all_cards[list_n[0]]
        secondCardTable = all_cards[list_n[1]]
        for i in range(cardsOnTable,cardsOnTable+cardAmount):
            cardI_OnHand.append(list_n[i])
            cardObj_OnHand.append(all_cards[list_n[i]])

        if cardsOnTable==2 and zole.cards.new_card_is_stronger(firstCardTable, secondCardTable):
            strongestCard = secondCardTable
            takerRole = playerRoles[1]
        else:
            strongestCard = firstCardTable
            takerRole = playerRoles[0]

        ourTrick = False
        if selfRole==takerRole and cardsOnTable==2:
            ourTrick = True

        allowedArr = CardOnTableToAllowedCards(firstCardTable.i)
        availableArr = intArrayToIndexArr(cardI_OnHand)
        legalArr = allowedArr*availableArr
        legalCards = indexArrToIntArr(legalArr)
        if sum(legalArr)==0:
            legalArr = availableArr
            legalCards = cardI_OnHand
        correctCards = []
        maxScore = 0
        for card in legalCards:
            if all_cards[card].score>maxScore:
                maxScore = all_cards[card].score
        if ourTrick!=True:
            for card in legalCards:
                if zole.cards.new_card_is_stronger(strongestCard, all_cards[card]):
                    correctCards.append(card)
        if ourTrick:
            for card in legalCards:
                if all_cards[card].score==maxScore:
                    correctCards.append(card)


        #if len(correctCards)>0 and len(correctCards)<cardAmount:  #ja vajag lai ir vismaz 1 derīga, bet ne visas derīgs
        if len(correctCards)!=0: # ja ir vairākas atļutas, pareizā ir vājākā no atļautajā
            if ourTrick!=True: 
                correctCards = [max(correctCards)]
            else:
                correctCards = [min(correctCards)]
            y = np.zeros(26)
            hasTrump = False
            hasQueen = False
            hasJack = False
            hasAce = False
            for card in correctCards:
                y[card] = 1
                if all_cards[card].is_trump:
                    hasTrump = True
                if all_cards[card].rank=='A':
                    hasAce = True
                if all_cards[card].rank=='Q':
                    hasQueen = True
                if all_cards[card].rank=='J':
                    hasJack = True
            appendAmount = 1  # lai mākslīgi izmainītu proporciju retākām situācijām
            if hasTrump==False:
                appendAmount+=1
            #if hasTrump==False and hasAce==False:
            #    appendAmount+=1
            if hasTrump==True and hasQueen==False:
                appendAmount+=1
                if hasJack==False:
                    appendAmount+=1

            x = np.zeros(26*3+1+2)
            x_tensor = turnInputStateIntoArray(cardI_OnHand, firstCardTable.i, secondCardTable.i, array = x)
            if hasTrump:
                x_tensor[26*3] = 1
            if firstPlayerRole == selfRole:
                x_tensor[26*3+1] = 1
            if secondPlayerRole == selfRole and cardsOnTable == 2:
                x_tensor[26*3+2] = 1
            for i in range(appendAmount):
                data_x.append(x_tensor)
                data_y.append(y)
            curLen = len(data_x)
            if curLen%printInterval<appendAmount:
                print(f'Data generation progress: {round(curLen/dataAmount,3)*100}%')
            #if attemptCount%10000==0:  
                #print(f'attemptCount: {attemptCount}, success percentage: {curLen/attemptCount}')
    data_x = torch.FloatTensor(np.array(data_x))
    data_y = torch.FloatTensor(np.array(data_y))
    torch.save(data_x, x_savePath)
    torch.save(data_y, y_savePath)
    return data_x, data_y
