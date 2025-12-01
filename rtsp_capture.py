import cv2
import os
import time
import threading
from datetime import datetime
from ultralytics import YOLO


class RTSPFaceCapture:
    """Capture frames from RTSP stream and detect/crop faces at intervals."""
    
    def __init__(self, rtsp_url, output_dir='faces', detect_interval=10, confidence_thresh=0.5):
        """
        Args:
            rtsp_url (str): RTSP stream URL
            output_dir (str): Directory to save cropped face images
            detect_interval (int): Interval (seconds) between face detections
            confidence_thresh (float): Confidence threshold for YOLOv8 detection
        """
        self.rtsp_url = rtsp_url
        self.output_dir = output_dir
        self.detect_interval = detect_interval
        self.confidence_thresh = confidence_thresh
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Load YOLOv8 nano model for face detection
        self.model = YOLO('yolov8n-face.pt')
        
        self.cap = None
        self.running = False
        self.last_detect_time = 0
        self.frame_count = 0
        self.lock = threading.Lock()
    
    def connect(self):
        """Open RTSP stream connection."""
        print(f'[INFO] Connecting to {self.rtsp_url}...')
        self.cap = cv2.VideoCapture(self.rtsp_url)
        
        if not self.cap.isOpened():
            raise RuntimeError(f'Failed to open RTSP stream: {self.rtsp_url}')
        
        # Get stream properties
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f'[INFO] Stream info: {width}x{height} @ {fps:.2f} FPS')
    
    def detect_and_crop_faces(self, frame):
        """Run YOLOv8 face detection and save crops."""
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence_thresh, verbose=False)
            
            face_count = 0
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf)
                        
                        # Ensure coordinates are within frame bounds
                        x1 = max(0, x1)
                        y1 = max(0, y1)
                        x2 = min(frame.shape[1], x2)
                        y2 = min(frame.shape[0], y2)
                        
                        # Crop face region
                        face_crop = frame[y1:y2, x1:x2]
                        
                        if face_crop.size > 0:
                            # Save cropped face with timestamp
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                            face_filename = os.path.join(
                                self.output_dir,
                                f'face_{timestamp}_conf{confidence:.2f}.jpg'
                            )
                            cv2.imwrite(face_filename, face_crop)
                            face_count += 1
            
            return face_count
        except Exception as e:
            print(f'[ERROR] Detection failed: {e}')
            return 0
    
    def run(self, duration=None):
        """
        Capture and process RTSP stream.
        
        Args:
            duration (int or None): Run for specified seconds (None = infinite)
        """
        self.running = True
        start_time = time.time()
        
        try:
            while self.running:
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print('[INFO] Duration limit reached, stopping...')
                    break
                
                ret, frame = self.cap.read()
                if not ret:
                    print('[WARN] Failed to read frame, reconnecting...')
                    time.sleep(1)
                    self.cap.release()
                    self.connect()
                    continue
                
                self.frame_count += 1
                current_time = time.time()
                
                # Perform detection at specified interval
                if (current_time - self.last_detect_time) >= self.detect_interval:
                    with self.lock:
                        face_count = self.detect_and_crop_faces(frame)
                        self.last_detect_time = current_time
                        
                        if face_count > 0:
                            print(f'[{datetime.now().strftime("%H:%M:%S")}] '
                                  f'Frame {self.frame_count}: Detected {face_count} face(s)')
        
        except KeyboardInterrupt:
            print('[INFO] Interrupted by user')
        except Exception as e:
            print(f'[ERROR] Unexpected error: {e}')
        finally:
            self.stop()
    
    def stop(self):
        """Stop capture and cleanup."""
        self.running = False
        if self.cap:
            self.cap.release()
        print('[INFO] Capture stopped')


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Capture and detect faces from RTSP stream')
    parser.add_argument('--rtsp-url', 
                        default='rtsp://admin:CUUNUZ@192.168.137.230:554/h264/ch1/main/av_stream',
                        help='RTSP stream URL')
    parser.add_argument('--output-dir', default='faces', help='Directory to save cropped faces')
    parser.add_argument('--interval', type=int, default=10, help='Detection interval (seconds)')
    parser.add_argument('--confidence', type=float, default=0.5, help='Detection confidence threshold')
    parser.add_argument('--duration', type=int, default=None, help='Run duration (seconds, None=infinite)')
    
    args = parser.parse_args()
    
    capture = RTSPFaceCapture(
        rtsp_url=args.rtsp_url,
        output_dir=args.output_dir,
        detect_interval=args.interval,
        confidence_thresh=args.confidence
    )
    
    try:
        capture.connect()
        capture.run(duration=args.duration)
    except Exception as e:
        print(f'[ERROR] {e}')


if __name__ == '__main__':
    main()
