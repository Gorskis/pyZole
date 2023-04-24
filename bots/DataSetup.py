import bots.NN_base as NN_base
import json
import os.path as path
import torch
import numpy as np
import torch
from bots.NN_base import stateEval_func

## setup variables
resetData = False
resetSimpleData = False
resetHandData = False
resetCompData = False
#dataFolder = "1m_Rand" #<games count>_<bot type>
dataFolder = "Complexity3/12-28" #Complexity<Complexity>/<cards on table minimumu = None><cards on table>-<cards on hand_minimun = None><cards on hand>
#dataFolder = "Hand"

data_Amount = 1000000
data_CardCount = 8
data_minCardCount = 2
data_tableCardCount = 2
data_minTableCardCount = 1
gametypesAllowed = ('t', 'b')
## setup code

class DataPaths:
    X = 'Resources/'+ dataFolder +'/data_x'
    X_MIN = 'Resources/'+ dataFolder +'/data_x_minimal'
    RESULT = 'Resources/'+ dataFolder +'/data_y_result'
    CARD = 'Resources/'+ dataFolder +'/data_y_card'
    MASK = 'Resources/'+ dataFolder +'/data_mask'
    TRAIN_X = 'Resources/'+dataFolder+'/train_x'
    TRAIN_Y = 'Resources/'+dataFolder+'/train_y'
    TEST_X = 'Resources/'+dataFolder+'/test_x'
    TEST_Y = 'Resources/'+dataFolder+'/test_y'


def checkExistance(dataPath: DataPaths, i = "") -> bool:
    return path.isfile(dataPath+str(i))

def loadData(dataPath: DataPaths, i):
    return torch.load(dataPath+str(i))

#formats data if needed
if resetData:
    NN_base.jsonToTrainData(dataFolder, gametypesAllowed)

if resetSimpleData:
    NN_base.generateSimpleFullData(DataPaths, data_CardCount, data_Amount, data_minCardCount, data_tableCardCount, data_minTableCardCount)

if resetCompData:
    NN_base.generateSimple2FullData(DataPaths, data_CardCount, data_Amount, data_minCardCount, data_tableCardCount, data_minTableCardCount)

if resetHandData:
    NN_base.generateFullHandData(DataPaths, (26*25*24*23*22*21*20*19)/(8*7*6*5*4*3*2))

# data_allowedDistribution = np.zeros(9)
# for singleMask in data_mask:
#     data_allowedDistribution[int(torch.sum(singleMask).item())]+=1
# sum = np.sum(data_allowedDistribution)
# weightedMean = 0
# for i in range(9):
#     data_allowedDistribution[i]=data_allowedDistribution[i]/sum
#     weightedMean += i*data_allowedDistribution[i]
# weightedMean/=26

print('===========Data setup complete===========')