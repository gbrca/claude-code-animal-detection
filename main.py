#!/usr/bin/env python3
"""
Animal Detection CLI Application
Detect animals in images from the command line
"""

import argparse
import sys
from pathlib import Path
import cv2

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from detector import AnimalDetector


def main():
    parser = argparse.ArgumentParser(
        description='Detect animals in images using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py image.jpg
  python main.py image.jpg --output result.jpg
  python main.py image.jpg --confidence 0.6
  python main.py image.jpg --show
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
        help='Path to save the output image with detections',
        default=None
    )

    parser.add_argument(
        '-c', '--confidence',
        type=float,
        help='Confidence threshold (0.0-1.0, default: 0.5)',
        default=0.5
    )

    parser.add_argument(
        '-s', '--show',
        action='store_true',
        help='Display the result in a window'
    )

    parser.add_argument(
        '--no-download',
        action='store_true',
        help='Skip automatic model download (use existing models)'
    )

    args = parser.parse_args()

    # Validate input image
    if not Path(args.image).exists():
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)

    # Initialize detector
    print("Initializing animal detector...")
    detector = AnimalDetector(confidence_threshold=args.confidence)

    try:
        # Detect animals
        print(f"Processing image: {args.image}")
        result_image, detections = detector.detect_animals(args.image)

        # Print results
        print("\n" + "=" * 50)
        summary = detector.get_detection_summary(detections)
        print(summary)
        print("=" * 50)

        if detections:
            print(f"\nDetailed results ({len(detections)} detection(s)):")
            for i, det in enumerate(detections, 1):
                print(f"  {i}. {det['class'].capitalize()} - "
                      f"Confidence: {det['confidence']:.2%} - "
                      f"Box: ({det['box']['x']}, {det['box']['y']}, "
                      f"{det['box']['width']}x{det['box']['height']})")

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
            cv2.imshow('Animal Detection', result_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
