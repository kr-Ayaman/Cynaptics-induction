# Main_Repo

This repository contains two main projects: **AI vs Real** and **GAN**. Each folder includes scripts and resources for specific machine learning tasks. Below is a detailed overview of the repository structure and its components.

---

## Folder Structure

### **AI vs Real (Folder)**
- **Purpose**: This folder contains scripts for classifying real and fake images.
- **Scripts**:
  - `classifier.py`: Implements the classification model to distinguish between real and fake images.

---

### **GAN (Folder)**
- **Purpose**: This folder contains scripts for training and executing a Deep Convolutional GAN (DCGAN) with Wasserstein loss.
- **Scripts**:
  - `training.py`: Trains the DCGAN model on the [Minecraft Screenshots Dataset with Features](https://www.kaggle.com/datasets/sqdartemy/minecraft-screenshots-dataset-with-features).
  - `x-mas.py`: Executes the trained model to generate 256x256 images.

---

## How to Use

### **AI vs Real**
1. Navigate to the `AI vs Real` folder.
2. Run the `classifier.py` script to classify images as real or fake.
3. Ensure you have the necessary dependencies installed (see below).

### **GAN**
1. Navigate to the `GAN` folder.
2. Run `training.py` to train the DCGAN model on the dataset.
   - The dataset can be downloaded from [Kaggle](https://www.kaggle.com/datasets/sqdartemy/minecraft-screenshots-dataset-with-features).
3. Use `minecraft.py` to generate 256x256 images using the trained model.

---
