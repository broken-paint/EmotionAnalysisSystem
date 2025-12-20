# EmotionAnalysisSystem

Identify and analyze the facial expressions of left-behind children to generate reports on their emotional trends.

![Static Badge](https://img.shields.io/badge/python-310?logo=python)


## Quick setup

Create and activate the conda environment:
```powershell
conda env create -f environment.yml
conda activate emotion-analysis
```

## FER2013 Emotion Recognition — Training scripts

This folder contains a minimal PyTorch training pipeline for the FER2013 dataset using a ResNet18 backbone.

Files added
- `requirements.txt`: Python dependencies (pip)
- `environment.yml`: Anaconda environment specification
- `model.py`: model factory and checkpoint loader
- `data.py`: dataloaders using `torchvision.datasets.ImageFolder`
- `train.py`: training script with checkpointing and fine-tune support
- `face_detection.py`: RTSP stream face detection and cropping
 - `face_detection.py`: OpenCV Haar Cascade face detection (image/video/webcam/RTSP)


Training example (default expects `dataset/FER2013/archive/train` and `dataset/FER2013/archive/test`):
```powershell
python ./backend/src/train.py --data-dir dataset/FER2013/archive --epochs 20 --batch-size 64 --output checkpoints
```

Fine-tuning example (load a checkpoint's model weights only):
```powershell
python ./backend/src/train.py --data-dir dataset/FER2013/archive --pretrained-weights checkpoints/best.pth --epochs 10
```

Resume full training (loads optimizer and scheduler states):
```powershell
python ./backend/src/train.py --data-dir dataset/FER2013/archive --resume checkpoints/checkpoint_epoch10.pth --epochs 20
```

Notes
- The scripts use `torchvision.datasets.ImageFolder`, so ensure the `dataset/FER2013/archive/train` and `dataset/FER2013/archive/test` folders contain subfolders per class (e.g. `happy`, `sad`).
- Adjust `--img-size` if you prefer other input resolutions.
- Check `--device` to force `cpu` or `cuda`.
 
## OpenCV Face Detection (`face_detection.py`)

`face_detection.py` provides a lightweight, CPU-friendly face detector using OpenCV's Haar Cascade. It does not require YOLO or GPU and supports image, video, webcam and RTSP sources. The script will attempt to locate a local Haar cascade and will automatically download it to `models/cascades/` if not found.

Basic usage examples (PowerShell):

- Detect faces in a single image and save crops:
```powershell
python ./backend/src/face_detection.py --source Q.jpeg --output-dir faces_opencv --save-crops
```

- Run on a video file (detect every 5 frames, show preview):
```powershell
python ./backend/src/face_detection.py --source video.mp4 --interval 5 --save-crops --display
```

- Use RTSP stream (detect every N frames specified by `--interval`):
```powershell
python ./backend/src/face_detection.py --source "rtsp://user:pass@192.168.1.1:554/stream" --interval 300 --duration 300 --save-crops
```

<details open>
<summary>rtsp stream</summary>

In our project, we use `rtsp://admin:CUUNUZ@192.168.137.230:554/h264/ch1/main/av_stream` as our Ezviz monitor's rtsp stream.

</details>

Key options:
- `--cascade`: Path to a Haar Cascade XML file. If omitted the script will auto-locate or download `haarcascade_frontalface_default.xml`.
- `--scale-factor`, `--min-neighbors`, `--min-size`: Tune `detectMultiScale` parameters to reduce false positives or detect smaller faces.
- `--interval`: For video/RTSP, detect every N frames to reduce CPU usage.
- `--save-crops`: Save detected face crops to `--output-dir`.
- `--display`: Show a preview window for video processing.

Notes:
- Haar Cascades are fast and suitable for lightweight detection or when GPU/YOLO is not available, but they are less accurate than modern deep-learning detectors. Use YOLO flow when higher accuracy is required.
- Downloaded cascade files are stored under `models/cascades/` in the project for reuse.

