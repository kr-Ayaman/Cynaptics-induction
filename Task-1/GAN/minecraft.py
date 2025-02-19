# -*- coding: utf-8 -*-
"""minecraft (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wRO5Kz6FcmbBlcRzjxwo9MG2NJOllAD1
"""

import torch
from torch import nn
import torch.nn.functional as F
from torchvision.utils import make_grid
import os
import matplotlib.pyplot as plt
torch.manual_seed(0)

img_channels=3
device = "cuda" if torch.cuda.is_available() else "cpu"
z_dim = 64
def show_tensor_images(image_tensor, num_images=25, size=(3, 64, 64), nrow=5):
    image_tensor = (image_tensor + 1) / 2
    image_unflat = image_tensor.detach().cpu()
    image_grid = make_grid(image_unflat[:num_images], nrow=nrow)
    plt.imshow(image_grid.permute(1, 2, 0).squeeze())
    plt.show()

def get_noise(n_samples, z_dim, device='cpu'):
    return torch.randn(n_samples, z_dim, device=device)

class Generator(nn.Module):
    def __init__(self, z_dim):
        super().__init__()
        self.z_dim=z_dim
        self.model = nn.Sequential(
            nn.ConvTranspose2d(z_dim, 1024, 4, 1, 0),
            nn.BatchNorm2d(1024),
            nn.ReLU(True),
            nn.ConvTranspose2d(1024, 512, 4, 2, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.ConvTranspose2d(512, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.ConvTranspose2d(256, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.ConvTranspose2d(64, img_channels, 4, 4, 0),
            nn.Tanh()
        )

    def unsqueeze_noise(self, noise):
        return noise.view(len(noise), self.z_dim, 1, 1)

    def forward(self, noise):
        x = self.unsqueeze_noise(noise)
        return self.model(x)

device = "cuda" if torch.cuda.is_available() else "cpu"
gen = nn.DataParallel(Generator(z_dim).to(device))
gen.load_state_dict(torch.load("/models/generator_epoch_300.pth", map_location=device))

show_tensor_images(gen(get_noise(25, z_dim, device=device)))

