import bots.DataSetup as data
import torch
import torch.nn as nn
import random

class AutoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.gameListFiltered =[]
        self.n_input = 26*3
        self.n_hidden1 = 26*1.5 #39
        self.n_hidden2 = 20
        self.n_out = 10
        self.learning_rate = 0.01
        self.epochCount = 500
        self.data_x_full = data.data_x_minimal
        self.data_x_train = self.data_x_full #set(random.sample(self.data_x_full, 6))  ## te kļūda, šis neder ar šo datu tipu
        self.data_x_test = self.data_x_full - self.data_x_train
      
        self.encoder = nn.Sequential(nn.Linear(self.n_input, self.n_hidden1),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden1, self.n_hidden2),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden2, self.n_out))
        self.decoder = nn.Sequential(nn.Linear(self.n_out, self.n_hidden2),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden2, self.n_hidden1),
                      nn.ReLU(),
                      nn.Linear(self.n_hidden1, self.n_input))
        
        # Validation using MSE Loss function
        self.loss_function = torch.nn.MSELoss()
        
        # Using an Adam Optimizer with lr = 0.1
        self.optimizer = torch.optim.Adam(self.parameters(),
                             lr = 1e-1,
                             weight_decay = 1e-8)
        def forward(self, x):
            encoded = self.encoder(x)
            decoded = self.decoder(encoded)
            return decoded
        
        def trainEncoder(self, x):
            epochs = 20
            outputs = []
            losses = []
            for epoch in range(epochs):
                # Output of Autoencoder
                reconstructed = self(self.data_x_train)
                
                # Calculating the loss function
                loss = self.loss_function(reconstructed, self.data_x_train)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                # Storing the losses in a list for plotting
                losses.append(loss)
                outputs.append((epochs, self.data_x_train, reconstructed))
        def testEncoder(self, x):
            reconstructed = self(self.data_x_test)
            loss = self.loss_function(reconstructed, self.data_x_test)
            return loss