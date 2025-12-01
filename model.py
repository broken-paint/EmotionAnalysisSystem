import torch
import torch.nn as nn
from torchvision import models


def get_model(num_classes=7, pretrained=True):
    """Return a ResNet18 model with the final layer adapted to num_classes."""
    model = models.resnet18(pretrained=pretrained)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


def load_checkpoint(path, device='cpu'):
    """Load a checkpoint saved by `save_checkpoint` and return (model, checkpoint_dict)."""
    checkpoint = torch.load(path, map_location=device)
    num_classes = checkpoint.get('num_classes', 7)
    model = get_model(num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    return model, checkpoint
