#!/usr/bin/env python3
"""
Enhanced Animal Detection CLI
Use multiple YOLO models with configurable accuracy settings
"""

import argparse
import sys
from pathlib import Path
import cv2

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from detector_enhanced import EnhancedAnimalDetector


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Animal Detection with multiple models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings
  python detect_enhanced.py image.jpg

  # Use full YOLOv3 for better accuracy
  python detect_enhanced.py image.jpg --model yolov3

  # Maximum accuracy mode
  python detect_enhanced.py image.jpg --model yolov4 --confidence 0.7 --size 608

  # Fast detection
  python detect_enhanced.py image.jpg --model yolov4-tiny --confidence 0.4

  # With preprocessing for difficult images
  python detect_enhanced.py image.jpg --preprocess

  # List available models
  python detect_enhanced.py --list-models
        """
    )

    parser.add_argument(
        'image',
        type=str,
        nargs='?',
        help='Path to the input image'
    )

    parser.add_argument(
        '-m', '--model',
        type=str,
        choices=['yolov3-tiny', 'yolov3', 'yolov4-tiny', 'yolov4'],
        default='yolov3-tiny',
        help='YOLO model to use (default: yolov3-tiny)'
    )

    parser.add_argument(
        '-c', '--confidence',
        type=float,
        help='Confidence threshold (0.0-1.0)',
        default=0.5
    )

    parser.add_argument(
        '-n', '--nms',
        type=float,
        help='NMS threshold (0.0-1.0)',
        default=0.4
    )

    parser.add_argument(
        '-s', '--size',
        type=int,
        choices=[320, 416, 512, 608, 832],
        help='Input size (default: 416)',
        default=416
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Path to save the output image',
        default=None
    )

    parser.add_argument(
        '-p', '--preprocess',
        action='store_true',
        help='Apply image preprocessing for better accuracy'
    )

    parser.add_argument(
        '--show',
        action='store_true',
        help='Display the result in a window'
    )

    parser.add_argument(
        '--no-filter',
        action='store_true',
        help='Detect all objects, not just animals'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show detection statistics'
    )

    parser.add_argument(
        '--list-models',
        action='store_true',
        help='List available models and exit'
    )

    parser.add_argument(
        '--profile',
        type=str,
        choices=['max_accuracy', 'balanced', 'fast', 'raspberry_pi'],
        help='Use a predefined performance profile'
    )

    args = parser.parse_args()

    # List models and exit
    if args.list_models:
        EnhancedAnimalDetector.list_models()
        print("\nRecommendations:")
        print("  Raspberry Pi: yolov3-tiny or yolov4-tiny")
        print("  Desktop (balanced): yolov3")
        print("  Desktop (accuracy): yolov4")
        return

    # Require image if not listing models
    if not args.image:
        parser.print_help()
        return

    # Validate input image
    if not Path(args.image).exists():
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)

    # Apply profile if specified
    if args.profile:
        profiles = {
            'max_accuracy': {'model': 'yolov4', 'confidence': 0.7, 'nms': 0.3, 'size': 608, 'preprocess': True},
            'balanced': {'model': 'yolov3', 'confidence': 0.5, 'nms': 0.4, 'size': 416, 'preprocess': False},
            'fast': {'model': 'yolov3-tiny', 'confidence': 0.4, 'nms': 0.5, 'size': 416, 'preprocess': False},
            'raspberry_pi': {'model': 'yolov3-tiny', 'confidence': 0.5, 'nms': 0.4, 'size': 416, 'preprocess': False}
        }
        profile = profiles[args.profile]
        args.model = profile['model']
        args.confidence = profile['confidence']
        args.nms = profile['nms']
        args.size = profile['size']
        args.preprocess = profile['preprocess']
        print(f"Using profile: {args.profile}")

    # Initialize detector
    print("=" * 60)
    print("Enhanced Animal Detection")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Confidence: {args.confidence}")
    print(f"NMS: {args.nms}")
    print(f"Input size: {args.size}x{args.size}")
    print(f"Preprocessing: {'Enabled' if args.preprocess else 'Disabled'}")
    print("=" * 60)

    detector = EnhancedAnimalDetector(
        model=args.model,
        confidence_threshold=args.confidence,
        nms_threshold=args.nms,
        input_size=args.size,
        preprocess=args.preprocess
    )

    try:
        # Detect animals
        print(f"\nProcessing image: {args.image}")
        result_image, detections = detector.detect_animals(
            args.image,
            draw_boxes=True,
            filter_animals_only=not args.no_filter
        )

        # Print results
        print("\n" + "=" * 60)
        summary = detector.get_detection_summary(detections)
        print(summary)
        print("=" * 60)

        if detections:
            print(f"\nDetailed results ({len(detections)} detection(s)):")
            for i, det in enumerate(detections, 1):
                print(f"  {i}. {det['class'].capitalize()}")
                print(f"     Confidence: {det['confidence']:.2%}")
                print(f"     Position: ({det['box']['x']}, {det['box']['y']})")
                print(f"     Size: {det['box']['width']}x{det['box']['height']}px")

        # Show statistics if requested
        if args.stats:
            detector.print_statistics()

        # Save output image
        if args.output:
            cv2.imwrite(args.output, result_image)
            print(f"\n✓ Output saved to: {args.output}")
        else:
            # Default output name
            input_path = Path(args.image)
            output_path = input_path.parent / f"{input_path.stem}_detected{input_path.suffix}"
            cv2.imwrite(str(output_path), result_image)
            print(f"\n✓ Output saved to: {output_path}")

        # Show result window
        if args.show:
            print("\nDisplaying result... (Press any key to close)")
            cv2.imshow('Enhanced Animal Detection', result_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
