#!/usr/bin/env python3
"""
Ultra-Accurate Animal Detection CLI
Maximum accuracy using ensemble detection and advanced techniques
"""

import argparse
import sys
from pathlib import Path
import cv2

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from detector_ultra import UltraAccurateDetector


def main():
    parser = argparse.ArgumentParser(
        description='Ultra-accurate animal detection with ensemble and advanced techniques',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Maximum Accuracy Modes:

1. ENSEMBLE MODE (Recommended - Best Accuracy)
   Uses multiple YOLO models that vote on detections
   python detect_ultra.py image.jpg

2. ENSEMBLE + AUGMENTATION (Maximum Accuracy)
   Tests image with different transformations
   python detect_ultra.py image.jpg --augment

3. YOLOV8 MODE (State-of-the-art)
   Uses latest YOLOv8 model (requires: pip install ultralytics torch)
   python detect_ultra.py image.jpg --yolov8

4. FULL POWER (Everything Enabled)
   Ensemble + Augmentation + YOLOv8
   python detect_ultra.py image.jpg --augment --yolov8

Examples:
  # Maximum accuracy with ensemble
  python detect_ultra.py wildlife.jpg

  # Maximum accuracy with all techniques
  python detect_ultra.py wildlife.jpg --augment --yolov8

  # Single model (faster)
  python detect_ultra.py wildlife.jpg --no-ensemble

  # Debug mode (save intermediate results)
  python detect_ultra.py wildlife.jpg --debug
        """
    )

    parser.add_argument(
        'image',
        type=str,
        help='Path to the input image'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Path to save the output image',
        default=None
    )

    parser.add_argument(
        '--no-ensemble',
        action='store_true',
        help='Disable ensemble detection (use single best model)'
    )

    parser.add_argument(
        '--augment',
        action='store_true',
        help='Enable test-time augmentation for maximum accuracy'
    )

    parser.add_argument(
        '--yolov8',
        action='store_true',
        help='Use YOLOv8 (requires: pip install ultralytics torch)'
    )

    parser.add_argument(
        '-c', '--confidence',
        type=float,
        default=0.5,
        help='Confidence threshold (default: 0.5)'
    )

    parser.add_argument(
        '-n', '--nms',
        type=float,
        default=0.3,
        help='NMS threshold (default: 0.3)'
    )

    parser.add_argument(
        '-s', '--size',
        type=int,
        default=608,
        help='Input size (default: 608 for best accuracy)'
    )

    parser.add_argument(
        '--show',
        action='store_true',
        help='Display result in window'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Save debug visualizations'
    )

    args = parser.parse_args()

    # Validate input
    if not Path(args.image).exists():
        print(f"❌ Error: Image not found: {args.image}")
        sys.exit(1)

    # Check YOLOv8 requirements
    if args.yolov8:
        try:
            import torch
            import ultralytics
        except ImportError:
            print("❌ YOLOv8 requires additional packages.")
            print("Install with: pip install ultralytics torch torchvision")
            print("\nContinuing without YOLOv8...")
            args.yolov8 = False

    # Display configuration
    print("\n" + "=" * 70)
    print("🎯 ULTRA-ACCURATE ANIMAL DETECTION")
    print("=" * 70)
    print(f"Image: {args.image}")
    print(f"Ensemble: {'✓ Enabled' if not args.no_ensemble else '✗ Disabled'}")
    print(f"Test-time augmentation: {'✓ Enabled' if args.augment else '✗ Disabled'}")
    print(f"YOLOv8: {'✓ Enabled' if args.yolov8 else '✗ Disabled (install with: pip install ultralytics torch)'}")
    print(f"Confidence threshold: {args.confidence}")
    print(f"NMS threshold: {args.nms}")
    print(f"Input size: {args.size}x{args.size}")
    print("=" * 70)

    if not args.no_ensemble or args.augment:
        print("\n⏱️  Note: Ultra-accurate mode is slower but significantly more accurate")
        print("Expected processing time: 30-120 seconds depending on enabled features\n")

    try:
        # Initialize detector
        detector = UltraAccurateDetector(
            use_ensemble=not args.no_ensemble,
            use_augmentation=args.augment,
            use_yolov8=args.yolov8,
            confidence_threshold=args.confidence,
            nms_threshold=args.nms,
            input_size=args.size
        )

        # Detect animals
        result_image, detections = detector.detect_animals(
            args.image,
            save_visualizations=args.debug
        )

        # Display results
        print("\n" + "=" * 70)
        summary = detector.get_detection_summary(detections)
        print(summary)
        print("=" * 70)

        if detections:
            print(f"\n📊 Detailed Results ({len(detections)} detection(s)):\n")
            for i, det in enumerate(detections, 1):
                print(f"{i}. {det['class'].upper()}")
                print(f"   Confidence: {det['confidence']:.2%}")
                if 'votes' in det:
                    print(f"   Model agreement: {det['votes']} models")
                print(f"   Position: ({det['box']['x']}, {det['box']['y']})")
                print(f"   Size: {det['box']['width']}x{det['box']['height']}px")
                print()

        # Save output
        if args.output:
            output_path = args.output
        else:
            input_path = Path(args.image)
            output_path = input_path.parent / f"{input_path.stem}_ultra_detected{input_path.suffix}"

        cv2.imwrite(str(output_path), result_image)
        print(f"✓ Result saved to: {output_path}")

        if args.debug:
            print("✓ Debug visualizations saved")

        # Show result
        if args.show:
            print("\nDisplaying result... (Press any key to close)")
            cv2.imshow('Ultra-Accurate Detection', result_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        print("\n" + "=" * 70)
        print("✓ Detection complete!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Detection cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
