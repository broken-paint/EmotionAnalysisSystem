import cv2
import os
import sys
import argparse
from datetime import datetime


class OpenCVFaceDetector:
    """Detect and crop faces using OpenCV Haar Cascade classifier."""
    
    def __init__(self, cascade_path=None, scale_factor=1.1, min_neighbors=10, min_size=(300, 300)):
        """
        Initialize face detector.
        
        Args:
            cascade_path: Path to Haar Cascade XML file. If None, uses default frontal face cascade.
            scale_factor: Scale factor for detectMultiScale
            min_neighbors: Min neighbors for detectMultiScale
            min_size: Minimum face size (width, height)
        """
        # Try to load default cascade if not provided
        if cascade_path is None:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError(f"Failed to load cascade classifier from {cascade_path}")
        
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
        print(f"[INFO] Loaded cascade classifier: {cascade_path}")
    
    def detect_faces(self, frame):
        """Detect faces in frame and return list of (x, y, w, h) tuples."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )
        return faces
    
    def crop_and_save_faces(self, frame, faces, output_dir, prefix='face'):
        """Crop detected faces and save to output_dir."""
        os.makedirs(output_dir, exist_ok=True)
        count = 0
        for (x, y, w, h) in faces:
            crop = frame[y:y+h, x:x+w]
            if crop.size == 0:
                continue
            resize = cv2.resize(crop, (48, 48))
            ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            fname = f"{prefix}_{ts}_{w}x{h}.jpg"
            path = os.path.join(output_dir, fname)
            cv2.imwrite(path, resize)
            count += 1
        return count
    
    def draw_faces(self, frame, faces, color=(0, 255, 0), thickness=2):
        """Draw rectangles around detected faces on frame."""
        frame_copy = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_copy, (x, y), (x+w, y+h), color, thickness)
        return frame_copy


def detect_from_image(detector, image_path, output_dir, save_crops=False):
    """Detect faces in image file."""
    print(f"[INFO] Loading image: {image_path}")
    frame = cv2.imread(image_path)
    if frame is None:
        raise RuntimeError(f"Failed to read image: {image_path}")
    
    faces = detector.detect_faces(frame)
    print(f"[INFO] Detected {len(faces)} face(s)")
    
    if save_crops and len(faces) > 0:
        basename = os.path.splitext(os.path.basename(image_path))[0]
        saved = detector.crop_and_save_faces(frame, faces, output_dir, prefix=basename)
        print(f"[INFO] Saved {saved} face crops to {output_dir}")
    
    # Draw and save result image
    frame_marked = detector.draw_faces(frame, faces)
    output_image = os.path.join(output_dir, f"result_{os.path.basename(image_path)}")
    cv2.imwrite(output_image, frame_marked)
    print(f"[INFO] Saved result image: {output_image}")


def detect_from_video(detector, video_path, output_dir, interval=10, save_crops=False, display=False):
    """Detect faces in video file."""
    print(f"[INFO] Loading video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Video: {frame_width}x{frame_height} @ {fps:.2f} FPS")
    
    frame_idx = 0
    detect_idx = 0
    total_faces = 0
    
    # Setup output video writer
    output_video = os.path.join(output_dir, f"result_{os.path.basename(video_path)}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect every Nth frame to reduce processing time
        if frame_idx % interval == 0:
            faces = detector.detect_faces(frame)
            detect_idx += 1
            if len(faces) > 0:
                total_faces += len(faces)
                print(f"[INFO] Frame {frame_idx}: Detected {len(faces)} face(s)")
                if save_crops:
                    saved = detector.crop_and_save_faces(frame, faces, output_dir, prefix=f"video_{frame_idx}")
        else:
            faces = []
        
        # Draw faces on frame
        frame_marked = detector.draw_faces(frame, faces)
        out.write(frame_marked)
        
        if display:
            cv2.imshow('Face Detection', frame_marked)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        frame_idx += 1
    
    cap.release()
    out.release()
    if display:
        cv2.destroyAllWindows()
    
    print(f"[INFO] Video processing finished. Total faces: {total_faces}")
    print(f"[INFO] Saved result video: {output_video}")


def detect_from_webcam(detector, cam_id=0, output_dir=None, interval=5, duration=None, save_crops=False):
    """Detect faces from webcam."""
    cap = cv2.VideoCapture(cam_id)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open webcam {cam_id}")
    
    print(f"[INFO] Webcam opened. Press 'q' to quit, 's' to save crops")
    frame_idx = 0
    total_faces = 0
    start_time = None if duration is None else datetime.now()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print('[WARN] Failed to read frame from webcam')
            break
        
        # Detect every Nth frame
        if frame_idx % interval == 0:
            faces = detector.detect_faces(frame)
            if len(faces) > 0:
                total_faces += len(faces)
                if save_crops and output_dir:
                    saved = detector.crop_and_save_faces(frame, faces, output_dir, prefix=f"webcam_{frame_idx}")
        else:
            faces = []
        
        # Draw faces
        frame_marked = detector.draw_faces(frame, faces)
        cv2.imshow('Webcam Face Detection', frame_marked)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and output_dir:
            saved = detector.crop_and_save_faces(frame, faces, output_dir, prefix=f"webcam_manual_{frame_idx}")
            print(f"[INFO] Saved {saved} face(s)")
        
        # Check duration
        if duration is not None and (datetime.now() - start_time).total_seconds() > duration:
            break
        
        frame_idx += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Webcam capture finished. Total faces: {total_faces}")


def detect_from_rtsp(detector, rtsp_url, output_dir, interval=10, duration=None, save_crops=False):
    """Detect faces from RTSP stream."""
    print(f"[INFO] Connecting to RTSP stream: {rtsp_url}")
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to connect to RTSP stream: {rtsp_url}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] RTSP Stream: {frame_width}x{frame_height} @ {fps:.2f} FPS")
    
    frame_idx = 0
    total_faces = 0
    start_time = datetime.now()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print('[WARN] Failed to read frame from RTSP, reconnecting...')
            cap.release()
            import time
            time.sleep(1)
            cap = cv2.VideoCapture(rtsp_url)
            continue
        
        # Detect every Nth frame
        if frame_idx % interval == 0:
            faces = detector.detect_faces(frame)
            if len(faces) > 0:
                total_faces += len(faces)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Frame {frame_idx}: Detected {len(faces)} face(s)")
                if save_crops:
                    saved = detector.crop_and_save_faces(frame, faces, output_dir, prefix=f"rtsp_{frame_idx}")
        
        # Check duration
        if duration is not None and (datetime.now() - start_time).total_seconds() > duration:
            print('[INFO] Duration limit reached')
            break
        
        frame_idx += 1
    
    cap.release()
    print(f"[INFO] RTSP capture finished. Total faces: {total_faces}")


def main():
    current_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_path)
    parent_dir = os.path.dirname(current_dir)

    parser = argparse.ArgumentParser(description='Face detection using OpenCV Haar Cascade')
    parser.add_argument('--source', 
                        default='rtsp://admin:CUUNUZ@192.168.137.230:554/h264/ch1/main/av_stream', 
                        help='Source: image path, video path, rtsp:// URL, or webcam id (0)')
    parser.add_argument('--cascade', default=None, help='Path to Haar Cascade XML file (default: frontal face)')
    parser.add_argument('--output-dir', default=parent_dir+'\\results\\faces', help='Directory to save crops and results')
    parser.add_argument('--scale-factor', type=float, default=1.1, help='Scale factor for detectMultiScale')
    parser.add_argument('--min-neighbors', type=int, default=10, help='Min neighbors for detectMultiScale')
    parser.add_argument('--min-size', type=int, nargs=2, default=[300, 300], help='Minimum face size (width height)')
    parser.add_argument('--interval', type=int, default=10, help='Detect every N frames (video/RTSP)')
    parser.add_argument('--duration', type=int, default=None, help='Run duration in seconds (webcam/RTSP)')
    parser.add_argument('--save-crops', action='store_true', help='Save cropped faces')
    parser.add_argument('--display', action='store_true', help='Display video (for video/webcam)')
    
    args = parser.parse_args()
    
    # Create detector
    detector = OpenCVFaceDetector(
        cascade_path=args.cascade,
        scale_factor=args.scale_factor,
        min_neighbors=args.min_neighbors,
        min_size=tuple(args.min_size)
    )
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Determine source type
    if args.source.isdigit():
        # Webcam
        detect_from_webcam(detector, int(args.source), args.output_dir, args.interval, args.duration, args.save_crops)
    elif args.source.lower().startswith('rtsp://'):
        # RTSP stream
        detect_from_rtsp(detector, args.source, args.output_dir, args.interval, args.duration, args.save_crops)
    elif os.path.isfile(args.source):
        # Image or video file
        if args.source.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
            detect_from_video(detector, args.source, args.output_dir, args.interval, args.save_crops, args.display)
        else:
            detect_from_image(detector, args.source, args.output_dir, args.save_crops)
    else:
        print(f"[ERROR] Source not found or invalid: {args.source}")
        sys.exit(1)


if __name__ == '__main__':
    main()
