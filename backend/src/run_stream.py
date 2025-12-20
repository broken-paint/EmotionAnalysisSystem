import os
import sys
import time
import argparse
import json
from datetime import datetime

# Ensure local src directory is on path so relative imports work when run from repo root
sys.path.insert(0, os.path.dirname(__file__))

import cv2

from face_detection import OpenCVFaceDetector
from inference import EmotionPredictor


def run_stream(source, model_path, output_dir, interval=5, device='cpu', display=True, save_json=True, save_crops=False):
    os.makedirs(output_dir, exist_ok=True)

    # Initialize detector and predictor
    detector = OpenCVFaceDetector()
    predictor = EmotionPredictor(model_path, device=device)

    # Open capture
    try:
        cam_id = int(source) if str(source).isdigit() else source
    except Exception:
        cam_id = source

    cap = cv2.VideoCapture(cam_id)

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 最小缓冲
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        raise RuntimeError(f"Failed to open source: {source}")

    results = {
        'source': source,
        'timestamp': datetime.now().isoformat(),
        'frames': []
    }

    frame_idx = 0
    processed = 0
    consecutive_failures = 0
    max_failures = 10

    print(f"[INFO] Started stream from {source}. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            consecutive_failures += 1
            if consecutive_failures >= max_failures:
                print('[ERROR] Maximum consecutive frame read failures reached, stopping')
                break
            print('[WARN] Failed to read frame, stopping')
            time.sleep(0.5)
            continue
        consecutive_failures = 0
        # print(f"[DEBUG] Read frame {frame_idx}")

        if frame_idx % interval == 0:
            faces = detector.detect_faces(frame)
            frame_result = {
                'frame_index': frame_idx,
                'timestamp': datetime.now().isoformat(),
                'faces': []
            }

            for idx, (x, y, w, h) in enumerate(faces):
                face_crop = frame[y:y+h, x:x+w]
                if face_crop.size == 0:
                    continue

                resize = cv2.resize(face_crop, (48, 48))
                pred = predictor.predict(resize)
                print(f"[DEBUG] emotion {pred.get('emotion', 'unknown')}")

                face_entry = {
                    'id': idx,
                    'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                    'emotion': pred.get('emotion', 'unknown'),
                    'confidence': float(pred.get('confidence', 0.0)),
                    'scores': {k: float(v) for k, v in pred.get('scores', {}).items()}
                }

                frame_result['faces'].append(face_entry)

                # Draw box and label
                label = f"{face_entry['emotion']} {face_entry['confidence']:.2f}"
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, max(y-8, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Optionally save crop
                if save_crops:
                    crop_dir = os.path.join(output_dir, 'crops')
                    os.makedirs(crop_dir, exist_ok=True)
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    fname = f"crop_{ts}_{frame_idx}_{idx}.jpg"
                    cv2.imwrite(os.path.join(crop_dir, fname), face_crop)

            if len(frame_result['faces']) > 0:
                results['frames'].append(frame_result)
                processed += 1

        if display:
            cv2.imshow('Emotion Stream', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        frame_idx += 1

    cap.release()
    if display:
        cv2.destroyAllWindows()

    # Save aggregated results
    if save_json:
        print("[INFO] Saving JSON results...")
        out_path = os.path.join(output_dir, 'stream_results.json')
        with open(out_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[INFO] Saved JSON results to {out_path}")

    print(f"[INFO] Stopped. Processed {processed} frames with faces")


def main():
    current_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_path)
    parent_dir = os.path.dirname(current_dir)

    parser = argparse.ArgumentParser(description='Run continuous face -> emotion inference')
    parser.add_argument('--source', type=str, 
                        default='rtsp://admin:CUUNUZ@192.168.137.230:554/h264/ch1/main/av_stream', 
                        help='Webcam id, video file, or RTSP URL')
    parser.add_argument('--model', type=str, default='checkpoints/best.pth', help='Path to model checkpoint')
    parser.add_argument('--output-dir', type=str, default=parent_dir+'\\results\\emotion', help='Directory to save outputs')
    parser.add_argument('--interval', type=int, default=10, help='Detect every Nth frame')
    parser.add_argument('--device', type=str, default='cpu', choices=['cpu', 'cuda'], help='Device for inference')
    parser.add_argument('--no-display', action='store_true', help='Disable display window')
    parser.add_argument('--no-json', action='store_true', help='Disable saving aggregated JSON results')
    parser.add_argument('--save-crops', action='store_true', help='Save face crops')

    args = parser.parse_args()

    
    run_stream(
        source=args.source,
        model_path=args.model,
        output_dir=args.output_dir,
        interval=args.interval,
        device=args.device,
        display=(not args.no_display),
        save_json=(not args.no_json),
        save_crops=args.save_crops
    )


if __name__ == '__main__':
    main()
