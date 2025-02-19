# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1d_YyZts7Zoxn_z9AtLeofr49rKSCZveD
"""

import torch
import numpy as np
import os
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from torchvision import transforms
from torch import nn
from tqdm.notebook import tqdm
from torch.utils.data import TensorDataset, DataLoader
from timeit import default_timer as timer

device = "cuda" if torch.cuda.is_available() else "cpu"
device

TRAIN_DIR = "kaggle/input/New_Data"

import zipfile
with zipfile.ZipFile("New_Data.zip", "r") as zip_ref:
  zip_ref.extractall("kaggle/input")

RANDOM_SEED = 42
RANDOM_STATE=42
BATCH_SIZE = 32
torch.manual_seed(RANDOM_SEED)

def find_classes(dir: str):
  classes = sorted(entry.name for entry in os.scandir(dir) if entry.is_dir())
  class_to_idx = {class_name: i for i,class_name in enumerate(classes)}

  return classes, class_to_idx

classes, class_to_idx = find_classes(TRAIN_DIR)
classes, class_to_idx

def create_data_frame(dir):
    image_paths = []
    labels = []
    for label in os.listdir(dir):
        for imagename in os.listdir(os.path.join(dir, label)):
            image_paths.append(os.path.join(dir, label, imagename))
            labels.append(label)
        print(label, "completed")
    return image_paths, labels

def extract_features(img_paths, transform):
  features = []
  for img_path in img_paths:

    try:
      img = Image.open(img_path)
      if img.mode == "L":
        # print(f"Converting grayscale image to RGB: {img_path}")
        img = img.convert("RGB")
      img_array = transform(img)
      features.append(img_array)
    except Exception as e:
      print(f"Error processing {img_path}: {e}")
  features = torch.stack(features)
  return features

train = pd.DataFrame()
train["image"], train["label"] = create_data_frame(TRAIN_DIR)
train.head()

def train_model(model:torch.nn.Module,
          dataloader: torch.utils.data.DataLoader,
          optimizer: torch.optim.Optimizer,
          loss_fn: torch.nn.Module,
          epochs: int=5):
  model.train()
  results = {"train_loss":[],
             "train_acc": []}
  for epoch in tqdm(range(epochs)):
    train_loss=0; train_acc = 0

    for batch, (X, y) in enumerate(dataloader):
      X,y =X.to(device), y.to(device)
      y = y.float()
      y_pred = model(X)
      loss = loss_fn(y_pred, y)
      train_loss += loss.item()

      optimizer.zero_grad()
      loss.backward()
      optimizer.step()

      y_pred_class = (torch.sigmoid(y_pred) >= 0.5).int()
      train_acc += (y_pred_class == y).sum().item()/len(y)

    train_loss = train_loss/len(dataloader)
    train_acc = train_acc/len(dataloader)
    print(f"Epoch {epoch+1}: | Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
    results["train_loss"].append(train_loss)
    results["train_acc"].append(train_acc)

  return results

def test_model(model: torch.nn.Module,
               dataloader: torch.utils.data.DataLoader,
              loss_fn: torch.nn.Module):
  model.eval()

  test_loss, test_acc = 0,0

  with torch.inference_mode():
    for batch, (X,y) in enumerate(dataloader):
      X,y = X.to(device), y.to(device)
      y = y.float()
      test_pred_logits = model(X)

      loss = loss_fn(test_pred_logits, y)
      test_loss += loss.item()

      test_pred_labels = (torch.sigmoid(test_pred_logits) >= 0.5).int()
      test_acc += (test_pred_labels == y).sum().item()/len(test_pred_labels)

  test_loss = test_loss/len(dataloader)
  test_acc = test_acc/len(dataloader)
  print(f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")

import torchvision

weights = torchvision.models.EfficientNet_B0_Weights.DEFAULT
auto_transforms = weights.transforms()
auto_transforms

pretrained_model = torchvision.models.efficientnet_b0(weights=weights).to(device)

for param in pretrained_model.features.parameters():
  param.requires_grad = False

pretrained_model.classifier = nn.Sequential(
    nn.Dropout(0.3, inplace=True),
    nn.Linear(in_features=1280, out_features=1)
)
pretrained_model.classifier

import os

valid_data = [
    (img_path, label)
    for img_path, label in zip(train["image"], train["label"])
    if os.path.isfile(img_path)
]

filtered_image_paths = [data[0] for data in valid_data]
filtered_labels = [data[1] for data in valid_data]

X = extract_features(img_paths=filtered_image_paths, transform=auto_transforms)

y = [class_to_idx[label] for label in filtered_labels]
y = torch.tensor(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=RANDOM_STATE, shuffle=True)
len(X_train), len(X_test), len(y_train), len(y_test)

loss_fn2 = nn.BCEWithLogitsLoss()
optimizer2 = torch.optim.Adam(params=pretrained_model.parameters(), lr=0.001)

train_dataset = TensorDataset(X_train, y_train.unsqueeze(dim=1))
train_loader= DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_dataset = TensorDataset(X_test, y_test.unsqueeze(dim=1))
test_loader= DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=True)

start_time = timer()
pretrained_model = pretrained_model.to(device)
results = train_model(model=pretrained_model,dataloader=train_loader, optimizer=optimizer2, loss_fn=loss_fn2, epochs=50)
end_time = timer()

print(f"[INFO] Total training time: {end_time-start_time:.3f} seconds")

def predict_test(model:torch.nn.Module, dir:str, transform):
  file = open("results.csv", "w")
  file.write("Id,Label\n")
  sorted_files = sorted([image for image in os.listdir(dir)],
                        key=lambda x: int(x.split("_")[1].split(".")[0]))
  for image_path in sorted_files:
    if(image_path == "image_530.jpg" or image_path == "image_326.jpg"):
      file.write(f"{image_path.split('.jpg')[0]},Corrupt\n")
      continue
    Img = Image.open(os.path.join(dir, image_path))
    if Img.mode != "RGB":
      print(f"Converting image to RGB: {image_path}")
      Img = Img.convert("RGB")
    # plt.imshow(Img)
    # plt.show()
    model.eval()
    with torch.inference_mode():
      transform_image = transform(Img)
      transform_image = transform_image.to(device)
      predicted = torch.sigmoid(model(transform_image.unsqueeze(dim=0))) >= 0.5
      row = image_path.split(".jpg")[0] + ","
      row += "AI" if predicted == 0 else "Real"
      file.write(row+"\n")
  file.close()

TEST_DIR = "/content/aa/input/Test_Images"

predict_test(pretrained_model, TEST_DIR, auto_transforms)

