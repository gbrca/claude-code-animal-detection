"""
Enhanced Animal Detection Module
Supports multiple YOLO models with configurable accuracy/speed tradeoff
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import urllib.request
import os


class EnhancedAnimalDetector:
    """
    Enhanced animal detector with multiple model support and accuracy options
    """

    # Available models with their configurations
    MODELS = {
        'yolov3-tiny': {
            'weights': 'https://pjreddie.com/media/files/yolov3-tiny.weights',
            'config': 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg',
            'size': '~35MB',
            'speed': 'Very Fast',
            'accuracy': 'Low',
            'description': 'Fastest model, good for real-time on Raspberry Pi'
        },
        'yolov3': {
            'weights': 'https://pjreddie.com/media/files/yolov3.weights',
            'config': 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg',
            'size': '~237MB',
            'speed': 'Medium',
            'accuracy': 'High',
            'description': 'Balanced accuracy and speed'
        },
        'yolov4-tiny': {
            'weights': 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights',
            'config': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg',
            'size': '~23MB',
            'speed': 'Very Fast',
            'accuracy': 'Medium',
            'description': 'Faster than YOLOv3-tiny with better accuracy'
        },
        'yolov4': {
            'weights': 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights',
            'config': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg',
            'size': '~246MB',
            'speed': 'Slow',
            'accuracy': 'Very High',
            'description': 'Highest accuracy, slower processing'
        }
    }

    # Core animal classes to focus on
    CORE_ANIMALS = {
        'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant',
        'bear', 'zebra', 'giraffe'
    }

    def __init__(
        self,
        model: str = 'yolov3-tiny',
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.4,
        input_size: int = 416,
        preprocess: bool = False
    ):
        """
        Initialize the enhanced animal detector

        Args:
            model: Model name ('yolov3-tiny', 'yolov3', 'yolov4-tiny', 'yolov4')
            confidence_threshold: Minimum confidence for detection (0.0-1.0)
            nms_threshold: Non-maximum suppression threshold
            input_size: Input image size (416, 608, or 832)
            preprocess: Apply image preprocessing for better accuracy
        """
        if model not in self.MODELS:
            raise ValueError(f"Model must be one of: {list(self.MODELS.keys())}")

        if input_size not in [320, 416, 512, 608, 832]:
            print(f"Warning: Unusual input size {input_size}. Recommended: 416, 608, or 832")

        self.model_name = model
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.input_size = input_size
        self.preprocess = preprocess

        self.net = None
        self.classes = []
        self.output_layers = []
        self.colors = None
        self.models_dir = Path(__file__).parent.parent / "models"
        self.models_dir.mkdir(exist_ok=True)

        # Statistics
        self.stats = {
            'total_detections': 0,
            'total_images': 0,
            'avg_confidence': 0.0
        }

    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        return {
            'name': self.model_name,
            **self.MODELS[self.model_name],
            'confidence_threshold': self.confidence_threshold,
            'nms_threshold': self.nms_threshold,
            'input_size': f"{self.input_size}x{self.input_size}",
            'preprocessing': self.preprocess
        }

    @staticmethod
    def list_models() -> None:
        """Print information about all available models"""
        print("\nAvailable Models:")
        print("=" * 80)
        for name, info in EnhancedAnimalDetector.MODELS.items():
            print(f"\n{name.upper()}")
            print(f"  Size: {info['size']}")
            print(f"  Speed: {info['speed']}")
            print(f"  Accuracy: {info['accuracy']}")
            print(f"  Description: {info['description']}")
        print("\n" + "=" * 80)

    def download_model_files(self):
        """Download YOLO model files if not present"""
        model_info = self.MODELS[self.model_name]

        print(f"Setting up {self.model_name} model...")
        print(f"Size: {model_info['size']} | Speed: {model_info['speed']} | Accuracy: {model_info['accuracy']}")

        # Determine file names
        weights_file = f"{self.model_name}.weights"
        config_file = f"{self.model_name}.cfg"
        names_file = "coco.names"

        files = {
            weights_file: model_info['weights'],
            config_file: model_info['config'],
            names_file: 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
        }

        for filename, url in files.items():
            filepath = self.models_dir / filename
            if not filepath.exists():
                print(f"Downloading {filename}...")
                try:
                    # Show download progress
                    def report_progress(block_num, block_size, total_size):
                        downloaded = block_num * block_size
                        percent = min(100, downloaded * 100 / total_size)
                        print(f"  Progress: {percent:.1f}%", end='\r')

                    urllib.request.urlretrieve(url, str(filepath), reporthook=report_progress)
                    print(f"\n✓ Downloaded {filename}")
                except Exception as e:
                    print(f"\n✗ Failed to download {filename}: {e}")
                    raise
            else:
                print(f"✓ {filename} already exists")

    def load_model(self):
        """Load YOLO model and configuration"""
        weights_path = self.models_dir / f"{self.model_name}.weights"
        config_path = self.models_dir / f"{self.model_name}.cfg"
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
        print(f"Loading {self.model_name} network...")
        self.net = cv2.dnn.readNet(str(weights_path), str(config_path))

        # Optimize for CPU (Raspberry Pi)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        print(f"✓ {self.model_name} loaded successfully")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply image preprocessing to improve detection

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        if not self.preprocess:
            return image

        # Denoise
        image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

        # Increase contrast using CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Sharpen
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        image = cv2.filter2D(image, -1, kernel)

        return image

    def detect_animals(
        self,
        image_path: str,
        draw_boxes: bool = True,
        filter_animals_only: bool = True
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect animals in an image

        Args:
            image_path: Path to the image file
            draw_boxes: Whether to draw bounding boxes on the image
            filter_animals_only: Only return animal detections (not all objects)

        Returns:
            Tuple of (processed_image, detections_list)
        """
        if self.net is None:
            self.load_model()

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

        # Preprocess if enabled
        if self.preprocess:
            image = self.preprocess_image(image)

        height, width, channels = image.shape

        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(
            image,
            0.00392,
            (self.input_size, self.input_size),
            (0, 0, 0),
            True,
            crop=False
        )
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

                # Filter by confidence
                if confidence > self.confidence_threshold:
                    class_name = self.classes[class_id]

                    # Filter by animal classes if requested
                    if filter_animals_only and class_name not in self.CORE_ANIMALS:
                        continue

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

                # Draw bounding box if requested
                if draw_boxes:
                    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

                    # Draw label with background
                    text = f"{label}: {confidence:.2f}"
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    cv2.rectangle(
                        image,
                        (x, y - text_size[1] - 10),
                        (x + text_size[0], y),
                        color,
                        -1
                    )
                    cv2.putText(
                        image,
                        text,
                        (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0),
                        2
                    )

                detections.append({
                    'class': label,
                    'confidence': confidence,
                    'box': {'x': x, 'y': y, 'width': w, 'height': h}
                })

        # Update statistics
        self.stats['total_images'] += 1
        self.stats['total_detections'] += len(detections)
        if detections:
            avg_conf = sum(d['confidence'] for d in detections) / len(detections)
            self.stats['avg_confidence'] = (
                (self.stats['avg_confidence'] * (self.stats['total_images'] - 1) + avg_conf) /
                self.stats['total_images']
            )

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

    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        return {
            **self.stats,
            'avg_detections_per_image': (
                self.stats['total_detections'] / self.stats['total_images']
                if self.stats['total_images'] > 0 else 0
            )
        }

    def print_statistics(self):
        """Print detection statistics"""
        stats = self.get_statistics()
        print("\n" + "=" * 50)
        print("Detection Statistics")
        print("=" * 50)
        print(f"Total images processed: {stats['total_images']}")
        print(f"Total detections: {stats['total_detections']}")
        print(f"Avg detections per image: {stats['avg_detections_per_image']:.2f}")
        print(f"Avg confidence: {stats['avg_confidence']:.2%}")
        print("=" * 50 + "\n")
