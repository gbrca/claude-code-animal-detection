#!/usr/bin/env python3
"""
Compare different YOLO models on the same image
Helps you choose the best model for your needs
"""

import sys
from pathlib import Path
import cv2
import time

sys.path.insert(0, str(Path(__file__).parent / "src"))

from detector_enhanced import EnhancedAnimalDetector


def compare_models(image_path: str):
    """Compare all available models on the same image"""

    if not Path(image_path).exists():
        print(f"Error: Image not found: {image_path}")
        return

    print("=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)
    print(f"Image: {image_path}\n")

    models = ['yolov3-tiny', 'yolov3', 'yolov4-tiny', 'yolov4']
    results = []

    for model_name in models:
        print(f"\n{'=' * 80}")
        print(f"Testing: {model_name.upper()}")
        print(f"{'=' * 80}")

        try:
            # Initialize detector
            detector = EnhancedAnimalDetector(
                model=model_name,
                confidence_threshold=0.5,
                nms_threshold=0.4,
                input_size=416
            )

            # Time the detection
            start_time = time.time()
            result_image, detections = detector.detect_animals(image_path)
            elapsed_time = time.time() - start_time

            # Calculate metrics
            num_detections = len(detections)
            avg_confidence = sum(d['confidence'] for d in detections) / num_detections if detections else 0

            # Store results
            results.append({
                'model': model_name,
                'detections': num_detections,
                'avg_confidence': avg_confidence,
                'time': elapsed_time,
                'animals': [d['class'] for d in detections]
            })

            # Print results
            print(f"\n✓ Completed in {elapsed_time:.2f} seconds")
            print(f"Detections: {num_detections}")
            if detections:
                print(f"Average confidence: {avg_confidence:.2%}")
                print(f"Animals found: {', '.join(set(d['class'] for d in detections))}")

                print("\nDetailed detections:")
                for i, det in enumerate(detections, 1):
                    print(f"  {i}. {det['class'].capitalize()} - {det['confidence']:.2%}")

            # Save result
            output_path = Path(image_path).parent / f"{Path(image_path).stem}_{model_name}.jpg"
            cv2.imwrite(str(output_path), result_image)
            print(f"Result saved: {output_path}")

        except KeyboardInterrupt:
            print("\n\nComparison cancelled by user.")
            break
        except Exception as e:
            print(f"✗ Failed: {e}")
            results.append({
                'model': model_name,
                'error': str(e)
            })

    # Print comparison summary
    print("\n\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"{'Model':<20} {'Detections':<15} {'Avg Confidence':<20} {'Time':<10}")
    print("-" * 80)

    for result in results:
        if 'error' not in result:
            print(f"{result['model']:<20} {result['detections']:<15} "
                  f"{result['avg_confidence']:<20.2%} {result['time']:<10.2f}s")
        else:
            print(f"{result['model']:<20} {'ERROR':<15} {'-':<20} {'-':<10}")

    print("=" * 80)

    # Recommendations
    print("\n📊 RECOMMENDATIONS:\n")

    if results:
        # Best accuracy
        best_accuracy = max(
            [r for r in results if 'error' not in r],
            key=lambda x: x['avg_confidence']
        )
        print(f"Best Accuracy: {best_accuracy['model']} "
              f"({best_accuracy['avg_confidence']:.2%} avg confidence)")

        # Fastest
        fastest = min(
            [r for r in results if 'error' not in r],
            key=lambda x: x['time']
        )
        print(f"Fastest: {fastest['model']} ({fastest['time']:.2f}s)")

        # Most detections
        most_detections = max(
            [r for r in results if 'error' not in r],
            key=lambda x: x['detections']
        )
        print(f"Most Detections: {most_detections['model']} "
              f"({most_detections['detections']} animals)")

        # Best balance
        balanced = sorted(
            [r for r in results if 'error' not in r],
            key=lambda x: (x['avg_confidence'] * x['detections']) / x['time'],
            reverse=True
        )[0]
        print(f"Best Balance: {balanced['model']}")

    print("\n" + "=" * 80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python compare_models.py <image_path>")
        print("\nThis script will test all available YOLO models on your image")
        print("and help you choose the best one for your needs.")
        sys.exit(1)

    image_path = sys.argv[1]
    compare_models(image_path)


if __name__ == '__main__':
    main()
