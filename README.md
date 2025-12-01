# FER2013 Emotion Recognition — Training scripts

This folder contains a minimal PyTorch training pipeline for the FER2013 dataset using a ResNet18 backbone.

Files added
- `requirements.txt`: Python dependencies
- `model.py`: model factory and checkpoint loader
- `data.py`: dataloaders using `torchvision.datasets.ImageFolder`
- `train.py`: training script with checkpointing and fine-tune support

Quick setup (recommended in a virtualenv)

PowerShell example:
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Training example (default expects `dataset/FER2013/archive/train` and `dataset/FER2013/archive/test`):
```powershell
python train.py --data-dir dataset/FER2013/archive --epochs 20 --batch-size 64 --output checkpoints
```

Fine-tuning example (load a checkpoint's model weights only):
```powershell
python train.py --data-dir dataset/FER2013/archive --pretrained-weights checkpoints/best.pth --epochs 10
```

Resume full training (loads optimizer and scheduler states):
```powershell
python train.py --data-dir dataset/FER2013/archive --resume checkpoints/checkpoint_epoch10.pth --epochs 20
```

Notes
- The scripts use `torchvision.datasets.ImageFolder`, so ensure the `dataset/FER2013/archive/train` and `dataset/FER2013/archive/test` folders contain subfolders per class (e.g. `happy`, `sad`).
- Adjust `--img-size` if you prefer other input resolutions.
- Check `--device` to force `cpu` or `cuda`.
# EmotionAnalysisSystem