"""
Ultra-Accurate Animal Detection Module
Maximum accuracy using ensemble detection, YOLOv8, and advanced techniques
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from detector_enhanced import EnhancedAnimalDetector


class UltraAccurateDetector:
    """
    Ultra-accurate animal detector using advanced techniques:
    - Ensemble detection (multiple models voting)
    - Test-time augmentation
    - Advanced preprocessing
    - YOLOv8 integration (if available)
    - Confidence calibration
    """

    # Core animal classes
    CORE_ANIMALS = {
        'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant',
        'bear', 'zebra', 'giraffe'
    }

    def __init__(
        self,
        use_ensemble: bool = True,
        use_augmentation: bool = True,
        use_yolov8: bool = False,
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.3,
        input_size: int = 608
    ):
        """
        Initialize ultra-accurate detector

        Args:
            use_ensemble: Use multiple models and vote on results
            use_augmentation: Apply test-time augmentation
            use_yolov8: Use YOLOv8 if available (requires ultralytics)
            confidence_threshold: Minimum confidence threshold
            nms_threshold: Non-maximum suppression threshold
            input_size: Input image size
        """
        self.use_ensemble = use_ensemble
        self.use_augmentation = use_augmentation
        self.use_yolov8 = use_yolov8
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.input_size = input_size

        # Initialize detectors for ensemble
        self.detectors = []
        if use_ensemble:
            print("Initializing ensemble detectors...")
            self._init_ensemble()
        else:
            # Single best detector
            self.detectors = [
                EnhancedAnimalDetector(
                    model='yolov4',
                    confidence_threshold=confidence_threshold,
                    nms_threshold=nms_threshold,
                    input_size=input_size,
                    preprocess=True
                )
            ]

        # YOLOv8 detector
        self.yolov8_detector = None
        if use_yolov8:
            self._init_yolov8()

    def _init_ensemble(self):
        """Initialize multiple detectors for ensemble"""
        # Use YOLOv3 and YOLOv4 for voting
        models = ['yolov3', 'yolov4']

        for model in models:
            try:
                detector = EnhancedAnimalDetector(
                    model=model,
                    confidence_threshold=self.confidence_threshold * 0.8,  # Lower threshold for ensemble
                    nms_threshold=self.nms_threshold,
                    input_size=self.input_size,
                    preprocess=True
                )
                self.detectors.append(detector)
                print(f"✓ Loaded {model} for ensemble")
            except Exception as e:
                print(f"⚠ Could not load {model}: {e}")

    def _init_yolov8(self):
        """Initialize YOLOv8 detector if available"""
        try:
            from ultralytics import YOLO
            print("Loading YOLOv8 (state-of-the-art)...")
            # Use YOLOv8 medium model for best balance
            self.yolov8_detector = YOLO('yolov8m.pt')
            print("✓ YOLOv8 loaded successfully")
        except ImportError:
            print("⚠ YOLOv8 not available. Install with: pip install ultralytics torch")
            self.use_yolov8 = False
        except Exception as e:
            print(f"⚠ Could not load YOLOv8: {e}")
            self.use_yolov8 = False

    def preprocess_advanced(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced image preprocessing for maximum quality

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        # Convert to LAB color space for better contrast
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge channels
        lab = cv2.merge([l, a, b])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Denoise while preserving edges
        image = cv2.bilateralFilter(image, 9, 75, 75)

        # Sharpen
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        image = cv2.filter2D(image, -1, kernel)

        return image

    def augment_image(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Create augmented versions for test-time augmentation

        Args:
            image: Input image

        Returns:
            List of augmented images
        """
        augmented = [image]  # Original

        # Horizontal flip
        augmented.append(cv2.flip(image, 1))

        # Brightness adjustments
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Brighter version
        hsv_bright = hsv.copy()
        hsv_bright[:, :, 2] = np.clip(hsv_bright[:, :, 2] * 1.2, 0, 255)
        augmented.append(cv2.cvtColor(hsv_bright, cv2.COLOR_HSV2BGR))

        # Darker version
        hsv_dark = hsv.copy()
        hsv_dark[:, :, 2] = np.clip(hsv_dark[:, :, 2] * 0.8, 0, 255)
        augmented.append(cv2.cvtColor(hsv_dark, cv2.COLOR_HSV2BGR))

        return augmented

    def merge_detections(
        self,
        all_detections: List[List[Dict]],
        image_width: int,
        image_height: int
    ) -> List[Dict]:
        """
        Merge detections from multiple models/augmentations using voting

        Args:
            all_detections: List of detection lists from different sources
            image_width: Image width
            image_height: Image height

        Returns:
            Merged detections
        """
        if not all_detections:
            return []

        # Flatten all detections
        flat_detections = []
        for detections in all_detections:
            flat_detections.extend(detections)

        if not flat_detections:
            return []

        # Group similar detections using spatial proximity
        merged = []
        used = set()

        for i, det1 in enumerate(flat_detections):
            if i in used:
                continue

            # Find all detections similar to this one
            similar = [det1]
            box1 = det1['box']

            for j, det2 in enumerate(flat_detections):
                if j <= i or j in used:
                    continue

                box2 = det2['box']

                # Check if boxes overlap significantly
                iou = self._calculate_iou(box1, box2)

                # Same class and significant overlap
                if det1['class'] == det2['class'] and iou > 0.3:
                    similar.append(det2)
                    used.add(j)

            # Merge similar detections
            if len(similar) >= 2:  # At least 2 models agree
                merged_det = self._merge_similar_detections(similar)
                merged.append(merged_det)
            elif len(similar) == 1 and similar[0]['confidence'] > self.confidence_threshold:
                # Single high-confidence detection
                merged.append(similar[0])

            used.add(i)

        return merged

    def _calculate_iou(self, box1: Dict, box2: Dict) -> float:
        """Calculate Intersection over Union between two boxes"""
        x1 = max(box1['x'], box2['x'])
        y1 = max(box1['y'], box2['y'])
        x2 = min(box1['x'] + box1['width'], box2['x'] + box2['width'])
        y2 = min(box1['y'] + box1['height'], box2['y'] + box2['height'])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)

        area1 = box1['width'] * box1['height']
        area2 = box2['width'] * box2['height']
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0

    def _merge_similar_detections(self, detections: List[Dict]) -> Dict:
        """Merge similar detections by averaging"""
        # Average confidence (weighted)
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections)

        # Average box coordinates
        avg_x = int(sum(d['box']['x'] for d in detections) / len(detections))
        avg_y = int(sum(d['box']['y'] for d in detections) / len(detections))
        avg_w = int(sum(d['box']['width'] for d in detections) / len(detections))
        avg_h = int(sum(d['box']['height'] for d in detections) / len(detections))

        # Boost confidence based on agreement
        confidence_boost = min(0.2, len(detections) * 0.05)
        final_confidence = min(1.0, avg_confidence + confidence_boost)

        return {
            'class': detections[0]['class'],
            'confidence': final_confidence,
            'box': {'x': avg_x, 'y': avg_y, 'width': avg_w, 'height': avg_h},
            'votes': len(detections)
        }

    def detect_with_yolov8(self, image_path: str) -> List[Dict]:
        """Detect using YOLOv8"""
        if not self.yolov8_detector:
            return []

        results = self.yolov8_detector(image_path, conf=self.confidence_threshold)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.yolov8_detector.names[class_id]

                # Filter for animals
                if class_name not in self.CORE_ANIMALS:
                    continue

                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append({
                    'class': class_name,
                    'confidence': confidence,
                    'box': {
                        'x': int(x1),
                        'y': int(y1),
                        'width': int(x2 - x1),
                        'height': int(y2 - y1)
                    }
                })

        return detections

    def detect_animals(
        self,
        image_path: str,
        save_visualizations: bool = False
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect animals with maximum accuracy

        Args:
            image_path: Path to image
            save_visualizations: Save intermediate results

        Returns:
            Tuple of (annotated_image, detections)
        """
        print("\n" + "=" * 60)
        print("ULTRA-ACCURATE DETECTION")
        print("=" * 60)
        print(f"Ensemble: {self.use_ensemble}")
        print(f"Test-time augmentation: {self.use_augmentation}")
        print(f"YOLOv8: {self.use_yolov8}")
        print("=" * 60 + "\n")

        # Load original image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError(f"Could not load image: {image_path}")

        height, width = original_image.shape[:2]

        # Preprocess
        print("Preprocessing image...")
        processed_image = self.preprocess_advanced(original_image)

        # Save preprocessed image
        if save_visualizations:
            cv2.imwrite('debug_preprocessed.jpg', processed_image)

        all_detections = []

        # YOLOv8 detection
        if self.use_yolov8:
            print("Running YOLOv8 detection...")
            yolov8_dets = self.detect_with_yolov8(image_path)
            all_detections.append(yolov8_dets)
            print(f"  YOLOv8: {len(yolov8_dets)} detections")

        # Ensemble detection
        print(f"Running ensemble with {len(self.detectors)} models...")
        for i, detector in enumerate(self.detectors):
            print(f"  Model {i+1}/{len(self.detectors)}...", end=' ')

            # Save to temporary file
            temp_path = 'temp_detection.jpg'
            cv2.imwrite(temp_path, processed_image)

            try:
                _, detections = detector.detect_animals(
                    temp_path,
                    draw_boxes=False,
                    filter_animals_only=True
                )
                all_detections.append(detections)
                print(f"{len(detections)} detections")
            except Exception as e:
                print(f"Failed: {e}")

        # Test-time augmentation
        if self.use_augmentation:
            print("Applying test-time augmentation...")
            augmented_images = self.augment_image(processed_image)

            for aug_idx, aug_image in enumerate(augmented_images[1:], 1):  # Skip original
                temp_path = f'temp_aug_{aug_idx}.jpg'
                cv2.imwrite(temp_path, aug_image)

                # Use primary detector on augmented images
                try:
                    _, aug_dets = self.detectors[0].detect_animals(
                        temp_path,
                        draw_boxes=False,
                        filter_animals_only=True
                    )

                    # Flip back detections if needed (for horizontal flip)
                    if aug_idx == 1:  # Horizontal flip
                        for det in aug_dets:
                            det['box']['x'] = width - det['box']['x'] - det['box']['width']

                    all_detections.append(aug_dets)
                except Exception as e:
                    print(f"  Augmentation {aug_idx} failed: {e}")

        # Merge all detections
        print("\nMerging detections from all sources...")
        final_detections = self.merge_detections(all_detections, width, height)

        print(f"✓ Final: {len(final_detections)} high-confidence detections")

        # Draw on original image
        result_image = original_image.copy()
        colors = np.random.uniform(0, 255, size=(10, 3))

        for det in final_detections:
            box = det['box']
            color = colors[hash(det['class']) % 10].tolist()

            # Draw box
            cv2.rectangle(
                result_image,
                (box['x'], box['y']),
                (box['x'] + box['width'], box['y'] + box['height']),
                color,
                3
            )

            # Draw label
            label = f"{det['class']}: {det['confidence']:.2%}"
            if 'votes' in det:
                label += f" ({det['votes']} votes)"

            # Background for text
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                result_image,
                (box['x'], box['y'] - text_height - 10),
                (box['x'] + text_width, box['y']),
                color,
                -1
            )
            cv2.putText(
                result_image,
                label,
                (box['x'], box['y'] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )

        return result_image, final_detections

    def get_detection_summary(self, detections: List[Dict]) -> str:
        """Generate detection summary"""
        if not detections:
            return "No animals detected."

        animal_counts = {}
        for det in detections:
            animal = det['class']
            animal_counts[animal] = animal_counts.get(animal, 0) + 1

        summary_parts = []
        for animal, count in animal_counts.items():
            summary_parts.append(f"{count} {animal}{'s' if count > 1 else ''}")

        avg_confidence = sum(d['confidence'] for d in detections) / len(detections)

        summary = f"Detected: {', '.join(summary_parts)}"
        summary += f"\nAverage confidence: {avg_confidence:.2%}"

        # Show voting info if available
        if any('votes' in d for d in detections):
            avg_votes = sum(d.get('votes', 1) for d in detections) / len(detections)
            summary += f"\nAverage model agreement: {avg_votes:.1f} models"

        return summary
