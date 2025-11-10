# Improving Detection Accuracy

This guide explains various methods to increase the accuracy of animal detection in the app.

## Quick Improvements (Easy)

### 1. Increase Confidence Threshold

**Current default: 0.5 (50%)**

Higher threshold = more accurate but fewer detections:

```bash
# CLI
python main.py image.jpg --confidence 0.7

# Programmatically
detector = AnimalDetector(confidence_threshold=0.7)
```

**Recommended values:**
- `0.3-0.4`: More detections, less accurate (use for difficult/small animals)
- `0.5-0.6`: Balanced (default)
- `0.7-0.8`: High precision, fewer false positives
- `0.9+`: Very strict, only very confident detections

### 2. Use Full YOLOv3 Model (Instead of Tiny)

**YOLOv3-tiny**: Fast but less accurate (~89MB)
**YOLOv3 Full**: Slower but much more accurate (~237MB)

See "Using Better Models" section below for implementation.

### 3. Improve Image Quality

- Use higher resolution images (at least 640x480)
- Ensure good lighting
- Avoid blurry or motion-blurred images
- Center the animal in the frame
- Avoid heavy occlusion

### 4. Adjust NMS Threshold

**Non-Maximum Suppression** removes duplicate detections.

```python
detector = AnimalDetector(
    confidence_threshold=0.5,
    nms_threshold=0.3  # Lower = fewer overlapping boxes
)
```

**Recommended values:**
- `0.2-0.3`: Strict, removes more overlaps
- `0.4`: Balanced (default)
- `0.5-0.6`: Allows more overlapping detections

## Medium Improvements (Moderate Effort)

### 5. Use Full YOLOv3 Model

Edit `src/detector.py` or use the enhanced version:

**Option A: Edit detector.py**
Change these lines in the `download_model_files()` method:

```python
files = {
    'yolov3.weights': 'https://pjreddie.com/media/files/yolov3.weights',
    'yolov3.cfg': 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg',
    'coco.names': 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
}
```

And update the `load_model()` method:
```python
weights_path = self.models_dir / "yolov3.weights"
config_path = self.models_dir / "yolov3.cfg"
```

**Option B: Use the enhanced detector with model selection** (see below)

### 6. Use YOLOv4 (Even Better)

YOLOv4 is more accurate than YOLOv3:

```python
files = {
    'yolov4.weights': 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights',
    'yolov4.cfg': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg',
    'coco.names': 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
}
```

### 7. Pre-process Images

Add image enhancement before detection:

```python
import cv2

# Increase contrast
image = cv2.convertScaleAbs(image, alpha=1.2, beta=10)

# Denoise
image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

# Sharpen
kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
image = cv2.filter2D(image, -1, kernel)
```

### 8. Optimal Input Size

YOLO works best with specific input sizes:

```python
# In detector.py, change blob creation
blob = cv2.dnn.blobFromImage(image, 0.00392, (608, 608), (0, 0, 0), True, crop=False)
```

**Input sizes:**
- `416x416`: Fast, standard
- `608x608`: Better accuracy, slower
- `832x832`: Best accuracy, slowest

## Advanced Improvements (High Effort)

### 9. Fine-tune Model on Custom Dataset

Train YOLO on your specific animal dataset:

1. Collect 1000+ labeled images of your target animals
2. Use Darknet or Ultralytics YOLOv5 to fine-tune
3. Replace the model weights with your custom weights

**Resources:**
- [Darknet Training Guide](https://github.com/AlexeyAB/darknet#how-to-train-to-detect-your-custom-objects)
- [YOLOv5 Training](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data)

### 10. Use YOLOv8 (State-of-the-art)

Most accurate modern YOLO version:

```bash
pip install ultralytics
```

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # or yolov8s, yolov8m, yolov8l, yolov8x
results = model(image)
```

### 11. Ensemble Multiple Models

Combine predictions from multiple models:

```python
# Use YOLOv3 + YOLOv4 + YOLOv8
# Average confidence scores
# Keep detections with consensus
```

### 12. Test-Time Augmentation

Run detection on multiple versions of the image:

```python
# Original image
# Flipped image
# Different brightness levels
# Different scales
# Combine results
```

## Model Comparison

| Model | Size | Speed (RPi4) | Accuracy | Recommended For |
|-------|------|--------------|----------|-----------------|
| YOLOv3-tiny | 35MB | 2-4s | ★★☆☆☆ | Real-time, low-power |
| YOLOv3 | 237MB | 8-12s | ★★★★☆ | Balanced |
| YOLOv4 | 246MB | 10-15s | ★★★★★ | High accuracy |
| YOLOv4-tiny | 23MB | 1-3s | ★★★☆☆ | Fast detection |
| YOLOv5s | 14MB | 1-2s | ★★★☆☆ | Modern, efficient |
| YOLOv8n | 6MB | 1-2s | ★★★★☆ | Best modern option |

## Practical Configuration Examples

### Example 1: Maximum Accuracy (Slow)
```python
detector = AnimalDetector(
    confidence_threshold=0.7,
    nms_threshold=0.3,
    model='yolov4',  # If implemented
    input_size=608
)
```

### Example 2: Balanced
```python
detector = AnimalDetector(
    confidence_threshold=0.5,
    nms_threshold=0.4,
    model='yolov3',
    input_size=416
)
```

### Example 3: Fast (Real-time)
```python
detector = AnimalDetector(
    confidence_threshold=0.4,
    nms_threshold=0.5,
    model='yolov3-tiny',
    input_size=416
)
```

## Measuring Accuracy

To measure improvements, use this test script:

```python
# test_accuracy.py
import os
from detector import AnimalDetector

# Test images with known animals
test_images = {
    'dog1.jpg': ['dog'],
    'cat1.jpg': ['cat'],
    'zoo.jpg': ['elephant', 'giraffe', 'zebra']
}

detector = AnimalDetector(confidence_threshold=0.5)

correct = 0
total = 0

for image_path, expected_animals in test_images.items():
    _, detections = detector.detect_animals(image_path)
    detected = {d['class'] for d in detections}

    for animal in expected_animals:
        total += 1
        if animal in detected:
            correct += 1
            print(f"✓ {image_path}: Found {animal}")
        else:
            print(f"✗ {image_path}: Missed {animal}")

accuracy = (correct / total) * 100
print(f"\nAccuracy: {accuracy:.1f}%")
```

## Quick Implementation: Enhanced Detector

I can create an enhanced version of the detector with:
- Multiple model support (tiny, full, v4, v8)
- Configurable input sizes
- Image preprocessing options
- Performance metrics

Would you like me to implement this?

## Troubleshooting Low Accuracy

**If you're getting poor results:**

1. **Check image quality**: Is it clear, well-lit, high resolution?
2. **Verify animal is in training data**: COCO dataset has limited animals
3. **Try lower confidence**: Some animals are harder to detect
4. **Use full model**: YOLOv3-tiny trades accuracy for speed
5. **Check distance**: Animals should be reasonably sized in frame
6. **Test with multiple images**: Single failures don't indicate poor accuracy

## Recommended Settings by Use Case

### Wildlife Camera
```python
confidence=0.4, nms=0.4, model='yolov3', size=608
```

### Pet Detection
```python
confidence=0.6, nms=0.3, model='yolov3', size=416
```

### Zoo/Safari Photos
```python
confidence=0.5, nms=0.4, model='yolov4', size=608
```

### Real-time Video
```python
confidence=0.5, nms=0.5, model='yolov3-tiny', size=416
```

## Next Steps

1. Start with adjusting confidence threshold (easiest)
2. Upgrade to full YOLOv3 model (big improvement)
3. Tune NMS threshold for your specific use case
4. Consider YOLOv8 for production (best accuracy)
5. Fine-tune on custom data if targeting specific animals

Let me know if you'd like me to implement any of these improvements!
