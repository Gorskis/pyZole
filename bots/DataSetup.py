import bots.NN_base as NN_base
import json
import os.path as path
import torch
import numpy as np
import torch

## setup variables
dataFolder = "500k_Rand"
resetData = False
gametypesAllowed = ('t', 'b')
## setup code

#loads the formatted data if it is found and resetData==False
if path.isfile('Resources/'+ dataFolder +'/data_x') and not resetData:
    data_x = torch.load('Resources/'+ dataFolder +'/data_x')
    data_x_minimal = torch.load('Resources/'+ dataFolder +'/data_x_minimal')
    data_y_result = torch.load('Resources/'+ dataFolder +'/data_y_result')
    data_y_card = torch.load('Resources/'+ dataFolder +'/data_y_card')
    data_mask = torch.load('Resources/'+ dataFolder +'/data_mask')
#else formats the data
else:
    data_x, data_x_minimal, data_y_result, data_y_card, data_mask = NN_base.jsonToTrainData(dataFolder, gametypesAllowed)
    torch.save(data_x, 'Resources/'+ dataFolder +'/data_x')
    torch.save(data_x_minimal, 'Resources/'+ dataFolder +'/data_x_minimal')
    torch.save(data_y_result, 'Resources/'+ dataFolder +'/data_y_result')
    torch.save(data_y_card, 'Resources/'+ dataFolder +'/data_y_card')
    torch.save(data_mask, 'Resources/'+ dataFolder +'/data_mask')

# data_allowedDistribution = np.zeros(9)
# for singleMask in data_mask:
#     data_allowedDistribution[int(torch.sum(singleMask).item())]+=1
# sum = np.sum(data_allowedDistribution)
# weightedMean = 0
# for i in range(9):
#     data_allowedDistribution[i]=data_allowedDistribution[i]/sum
#     weightedMean += i*data_allowedDistribution[i]
# weightedMean/=26

print('Data setup complete')