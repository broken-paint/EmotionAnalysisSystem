"""
Emotion detection inference script using best.pth model and face_detection.py
Generates JSON output with detected emotions for each face in images/videos.
"""

import os
import json
import argparse
from datetime import datetime
import cv2
import torch
from torchvision import transforms
import numpy as np

from face_detection import OpenCVFaceDetector
from model.model import load_checkpoint


# Emotion class names (from FER2013 dataset)
EMOTION_CLASSES = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']


class EmotionPredictor:
    """Predict emotions from face crops using trained model."""
    
    def __init__(self, model_path, device='cpu'):
        """Load model from checkpoint."""
        self.device = device
        self.model, self.checkpoint = load_checkpoint(model_path, device=device)
        self.model.to(device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
        ])
        print(f"[INFO] Loaded model from {model_path}")
    
    def predict(self, face_crop):
        """
        Predict emotion from a face crop image.
        
        Args:
            face_crop: BGR image array (from OpenCV)
            
        Returns:
            dict with emotion prediction and confidence scores
        """
        try:
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            
            # Apply transforms
            tensor = self.transform(face_rgb).unsqueeze(0).to(self.device)
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]
                confidence, predicted = torch.max(outputs, 1)
            
            emotion = EMOTION_CLASSES[predicted.item()]
            confidence_score = probabilities[predicted.item()].item()
            
            # Get all emotion scores
            all_emotions = {
                EMOTION_CLASSES[i]: probabilities[i].item() 
                for i in range(len(EMOTION_CLASSES))
            }
            
            return {
                'emotion': emotion,
                'confidence': confidence_score,
                'scores': all_emotions
            }
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return {
                'emotion': 'unknown',
                'confidence': 0.0,
                'scores': {}
            }


def process_image(image_path, face_detector, emotion_predictor, output_dir):
    """
    Process image file, detect faces, and predict emotions.
    
    Returns:
        dict with image path, detected faces, and predictions
    """
    print(f"[INFO] Processing image: {image_path}")
    frame = cv2.imread(image_path)
    
    if frame is None:
        raise RuntimeError(f"Failed to read image: {image_path}")
    
    height, width = frame.shape[:2]
    faces = face_detector.detect_faces(frame)
    print(f"[INFO] Detected {len(faces)} face(s)")
    
    results = {
        'image': image_path,
        'timestamp': datetime.now().isoformat(),
        'image_size': {'width': width, 'height': height},
        'faces': []
    }
    
    for idx, (x, y, w, h) in enumerate(faces):
        face_crop = frame[y:y+h, x:x+w]
        
        if face_crop.size == 0:
            continue
        
        prediction = emotion_predictor.predict(face_crop)
        
        face_result = {
            'id': idx,
            'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
            'emotion': prediction['emotion'],
            'confidence': float(prediction['confidence']),
            'all_emotions': {k: float(v) for k, v in prediction['scores'].items()}
        }
        
        results['faces'].append(face_result)
    
    # Save visualization
    frame_marked = face_detector.draw_faces(frame, faces)
    vis_filename = f"emotion_{os.path.basename(image_path)}"
    vis_path = os.path.join(output_dir, vis_filename)
    cv2.imwrite(vis_path, frame_marked)
    results['visualization'] = vis_path
    
    return results


def process_video(video_path, face_detector, emotion_predictor, output_dir, interval=10):
    """
    Process video file, detect faces per frame, and predict emotions.
    
    Args:
        video_path: Path to video file
        face_detector: OpenCVFaceDetector instance
        emotion_predictor: EmotionPredictor instance
        output_dir: Directory to save outputs
        interval: Process every Nth frame
        
    Returns:
        dict with video analysis results
    """
    print(f"[INFO] Processing video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    
    print(f"[INFO] Video: {frame_width}x{frame_height} @ {fps:.2f} FPS, {frame_count} frames, {duration:.2f}s")
    
    results = {
        'video': video_path,
        'timestamp': datetime.now().isoformat(),
        'video_info': {
            'width': frame_width,
            'height': frame_height,
            'fps': fps,
            'frame_count': frame_count,
            'duration_seconds': duration
        },
        'frames': []
    }
    
    frame_idx = 0
    processed_frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % interval != 0:
            frame_idx += 1
            continue
        
        faces = face_detector.detect_faces(frame)
        
        if len(faces) > 0:
            frame_result = {
                'frame_index': frame_idx,
                'timestamp_seconds': frame_idx / fps if fps > 0 else 0,
                'faces': []
            }
            
            for idx, (x, y, w, h) in enumerate(faces):
                face_crop = frame[y:y+h, x:x+w]
                
                if face_crop.size == 0:
                    continue
                
                prediction = emotion_predictor.predict(face_crop)
                
                face_result = {
                    'id': idx,
                    'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                    'emotion': prediction['emotion'],
                    'confidence': float(prediction['confidence']),
                    'all_emotions': {k: float(v) for k, v in prediction['scores'].items()}
                }
                
                frame_result['faces'].append(face_result)
            
            results['frames'].append(frame_result)
        
        processed_frame_idx += 1
        if processed_frame_idx % 10 == 0:
            print(f"[INFO] Processed {processed_frame_idx} frames...")
        
        frame_idx += 1
    
    cap.release()
    print(f"[INFO] Processed {len(results['frames'])} frames with faces")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Emotion detection inference using best.pth model'
    )
    parser.add_argument('--input', type=str, required=True,
                       help='Input image or video file')
    parser.add_argument('--model', type=str, default='checkpoints/best.pth',
                       help='Path to best.pth model checkpoint')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for results and visualizations')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'],
                       help='Device to use for inference')
    parser.add_argument('--video-interval', type=int, default=10,
                       help='Process every Nth frame in video')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize detector and predictor
    face_detector = OpenCVFaceDetector()
    emotion_predictor = EmotionPredictor(args.model, device=args.device)
    
    # Check if input is image or video
    _, ext = os.path.splitext(args.input)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
    
    if ext.lower() in image_extensions:
        results = process_image(args.input, face_detector, emotion_predictor, args.output_dir)
    elif ext.lower() in video_extensions:
        results = process_video(args.input, face_detector, emotion_predictor, args.output_dir, 
                               interval=args.video_interval)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    # Save JSON results
    json_output = os.path.join(args.output_dir, 'results.json')
    with open(json_output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[SUCCESS] Results saved to {json_output}")
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
