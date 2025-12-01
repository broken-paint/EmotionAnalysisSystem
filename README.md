# FER2013 Emotion Recognition — Training scripts

This folder contains a minimal PyTorch training pipeline for the FER2013 dataset using a ResNet18 backbone.

Files added
- `requirements.txt`: Python dependencies (pip)
- `environment.yml`: Anaconda environment specification
- `model.py`: model factory and checkpoint loader
- `data.py`: dataloaders using `torchvision.datasets.ImageFolder`
- `train.py`: training script with checkpointing and fine-tune support
- `rtsp_capture.py`: RTSP stream face detection and cropping

## Quick setup

### Option 1: Using Anaconda (recommended for GPU support)

Create and activate the conda environment:
```powershell
conda env create -f environment.yml
conda activate emotion-analysis
```

### Option 2: Using venv and pip

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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

## RTSP Face Detection & Cropping

`rtsp_capture.py` captures frames from an RTSP stream, detects faces every N seconds using YOLOv8-nano, and saves cropped face images.

Prerequisites
- If using venv, run: `pip install -r requirements.txt`
- If using conda, the dependencies are already installed via `environment.yml`
- YOLOv8 nano face detection model will be auto-downloaded on first run

Example usage (with default credentials in the RTSP URL):
```powershell
python rtsp_capture.py
```

Custom parameters:
```powershell
# Run with custom RTSP URL and detection interval (20 seconds)
python rtsp_capture.py --rtsp-url "rtsp://user:pass@192.168.1.1:554/stream" --interval 20

# Run for 300 seconds with higher confidence threshold
python rtsp_capture.py --duration 300 --confidence 0.6

# Save faces to custom directory
python rtsp_capture.py --output-dir /path/to/faces
```

Options:
- `--rtsp-url`: RTSP stream URL (default: the provided URL)
- `--output-dir`: Directory to save cropped faces (default: `faces`)
- `--interval`: Detection interval in seconds (default: `10`)
- `--confidence`: YOLOv8 confidence threshold (default: `0.5`)
- `--duration`: Run duration in seconds; `None` = infinite (default: `None`)

# EmotionAnalysisSystem