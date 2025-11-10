"""
Animal Detection Module
Uses YOLO (You Only Look Once) with OpenCV for real-time animal detection
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import urllib.request
import os


class AnimalDetector:
    """
    Animal detector using YOLOv3-tiny pre-trained model
    Optimized for Raspberry Pi performance
    """

    # COCO dataset animal classes
    ANIMAL_CLASSES = {
        'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant',
        'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
        'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
        'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife',
        'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli',
        'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
        'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
        'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven',
        'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
        'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    }

    # Core animal classes to focus on
    CORE_ANIMALS = {
        'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant',
        'bear', 'zebra', 'giraffe'
    }

    def __init__(self, confidence_threshold: float = 0.5, nms_threshold: float = 0.4):
        """
        Initialize the animal detector

        Args:
            confidence_threshold: Minimum confidence for detection (0.0-1.0)
            nms_threshold: Non-maximum suppression threshold
        """
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.net = None
        self.classes = []
        self.output_layers = []
        self.colors = None
        self.models_dir = Path(__file__).parent.parent / "models"
        self.models_dir.mkdir(exist_ok=True)

    def download_model_files(self):
        """Download YOLO model files if not present"""
        print("Downloading YOLO model files...")

        files = {
            'yolov3-tiny.weights': 'https://pjreddie.com/media/files/yolov3-tiny.weights',
            'yolov3-tiny.cfg': 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg',
            'coco.names': 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
        }

        for filename, url in files.items():
            filepath = self.models_dir / filename
            if not filepath.exists():
                print(f"Downloading {filename}...")
                try:
                    urllib.request.urlretrieve(url, str(filepath))
                    print(f"✓ Downloaded {filename}")
                except Exception as e:
                    print(f"✗ Failed to download {filename}: {e}")
                    raise
            else:
                print(f"✓ {filename} already exists")

    def load_model(self):
        """Load YOLO model and configuration"""
        weights_path = self.models_dir / "yolov3-tiny.weights"
        config_path = self.models_dir / "yolov3-tiny.cfg"
        names_path = self.models_dir / "coco.names"

        # Download files if not present
        if not weights_path.exists() or not config_path.exists() or not names_path.exists():
            self.download_model_files()

        # Load COCO class labels
        with open(names_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

        # Generate random colors for each class
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

        # Load YOLO network
        print("Loading YOLO network...")
        self.net = cv2.dnn.readNet(str(weights_path), str(config_path))

        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        print("✓ Model loaded successfully")

    def detect_animals(self, image_path: str) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect animals in an image

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (processed_image, detections_list)
        """
        if self.net is None:
            self.load_model()

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

        height, width, channels = image.shape

        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)

        # Run forward pass
        outs = self.net.forward(self.output_layers)

        # Process detections
        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # Filter by confidence and animal classes
                if confidence > self.confidence_threshold:
                    class_name = self.classes[class_id]
                    if class_name in self.CORE_ANIMALS:
                        # Object detected
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

        # Apply non-maximum suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)

        # Prepare results
        detections = []

        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                label = self.classes[class_ids[i]]
                confidence = confidences[i]
                color = self.colors[class_ids[i]]

                # Draw bounding box
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

                # Draw label
                text = f"{label}: {confidence:.2f}"
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                detections.append({
                    'class': label,
                    'confidence': confidence,
                    'box': {'x': x, 'y': y, 'width': w, 'height': h}
                })

        return image, detections

    def get_detection_summary(self, detections: List[Dict]) -> str:
        """
        Create a human-readable summary of detections

        Args:
            detections: List of detection dictionaries

        Returns:
            Summary string
        """
        if not detections:
            return "No animals detected in the image."

        animal_counts = {}
        for det in detections:
            animal = det['class']
            animal_counts[animal] = animal_counts.get(animal, 0) + 1

        summary_parts = []
        for animal, count in animal_counts.items():
            if count == 1:
                summary_parts.append(f"1 {animal}")
            else:
                summary_parts.append(f"{count} {animal}s")

        return f"Detected: {', '.join(summary_parts)}"
