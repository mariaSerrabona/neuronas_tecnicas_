# -*- coding: utf-8 -*-
"""trabajo_tec.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17plAoZZIQoI9vHc7v-h5gdZjjk9KhG7O
"""

pip install datasets

from datasets import load_dataset
import PIL
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from IPython.display import display
from tqdm import tqdm
import pickle
import torchvision

dataset = load_dataset("cifar10")

train_df = dataset["train"]
test_df = dataset["test"]
to_tensor = transforms.ToTensor()
to_pil = transforms.ToPILImage()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class TrainDataset(Dataset):
  def __len__(self):
    return len(train_df)

  def __getitem__(self, index):
    img_x = train_df[index]["img"].resize((32, 32))
    return (to_tensor(img_x), torch.tensor([train_df[index]["label"]]))

class TestDataset(Dataset):
  def __len__(self):
    return len(test_df)

  def __getitem__(self, index):
    img_x = test_df[index]["img"].resize((32, 32))
    return (to_tensor(img_x), torch.tensor([test_df[index]["label"]]))

train_dataset = TrainDataset()
test_dataset = TestDataset()

train_set = DataLoader(
    train_dataset,
    batch_size = 200, 
    shuffle = True
)

test_set = DataLoader(
    test_dataset
)

df_test = pd.DataFrame(test_set)
df_train = pd.DataFrame(train_set)

df_test.to_csv("test.csv", index = False)

def train(input, real):
  optim.zero_grad()

  output = model(input)
  lost = loss_function(output, real)
  
  lost.backward()
  optim.step()

  return lost

def encode_labels(batch_size, input):
  data = torch.zeros((batch_size, 10)).to(device)
  for i, j in enumerate(input):
    data[i][j.item()] = 1
  return data

df_train.columns = ["img", "label"]
df_test.columns = ["img", "label"]

class Model(nn.Module):
  def __init__(self):
    super().__init__()
    self.features = nn.Sequential(
      nn.Conv2d(3, 64, 3, 1, 1),
      nn.BatchNorm2d(64),
      nn.ReLU(),
      
      nn.Dropout(p=0.3),

      nn.Conv2d(64, 128, 3, 1, 1),
      nn.BatchNorm2d(128),
      nn.ReLU(),

      nn.MaxPool2d(2, 2),

      nn.Conv2d(128, 256, 3, 1, 1),
      nn.BatchNorm2d(256),
      nn.ReLU(),

      nn.Dropout(p = 0.4),

      nn.Conv2d(256, 512, 3, 1, 1),
      nn.BatchNorm2d(512),
      nn.ReLU(),

      nn.MaxPool2d(2, 2),

      nn.Conv2d(512, 512, 3, 1, 1),
      nn.BatchNorm2d(512),
      nn.ReLU(),

      nn.Dropout(p = 0.4),

      nn.Conv2d(512, 512, 3, 1, 1),
      nn.BatchNorm2d(512),
      nn.ReLU(),

      nn.MaxPool2d(4, 4)
    )


    self.output = nn.Sequential(
      nn.Linear(2048, 512),
      nn.BatchNorm1d(512),
      nn.ReLU(),

      nn.Dropout(p = 0.3),

      nn.Linear(512, 10),
    )

  def forward(self, x):
    x = self.features(x)
    x = x.view(x.size(0), 2048)
    x = self.output(x)
    return x

model = Model().to(device)
loss_function = nn.CrossEntropyLoss()
optim = torch.optim.SGD(model.parameters(), lr = 0.01)

def train(input, real):
  optim.zero_grad()

  output = model(input)
  lost = loss_function(output, real)
  
  lost.backward()
  optim.step()

  return lost


def encode_labels(batch_size, input):
  data = torch.zeros((batch_size, 10)).to(device)
  for i, j in enumerate(input):
    data[i][j.item()] = 1
  return data

history_loss = []
epochs = 300
for epoch in range(epochs):
  epoch_loss = 0
  for i in tqdm(range(len(df_train)), position=0, leave=True):
    input = df_train.iloc[i]["img"].to(device)
    real = encode_labels(200, df_train.iloc[i]["label"])
    epoch_loss = epoch_loss + train(input, real)
  print(f"Epoch:{epoch}. Loss:{epoch_loss.item()/i}")
  history_loss.append(epoch_loss.item()/i)

torch.save(model, "tecnicas_optim.plt")

plt.plot(history_loss)

#label: 0-9 with the following correspondence 0 airplane 1 automobile 2 bird 3 cat 4 deer 5 dog 6 frog 7 horse 8 ship 9 truck

model = torch.load("tecnicas_optim.plt")
labeled = {0: "airplane", 1: "automobile", 2: "bird", 3: "cat", 4: "deer", 5: "dog", 6: "frog", 7: "horse", 8: "ship", 9: "truck"}
data = {i: [0, 0] for i in labeled.keys()}
model.eval()
with torch.no_grad():
  for i in range(len(df_test)):
    input = df_test.iloc[i]["img"].to(device)
    real = df_test.iloc[i]["label"]
    out = model(input)
    data[real.item()][1] += 1
    if torch.argmax(out[0]).item() == real.item():
      data[real.item()][0] += 1

print(data)

pip freeze > requirements.txt



