#!/usr/bin/env python3
"""
Example usage of the Animal Detection API
Demonstrates how to use the detector programmatically
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from detector import AnimalDetector
import cv2


def example_basic_detection():
    """Example 1: Basic animal detection"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Animal Detection")
    print("=" * 60)

    # Initialize detector
    detector = AnimalDetector(confidence_threshold=0.5)

    # Note: You'll need to provide your own test image
    image_path = "test_image.jpg"

    if not Path(image_path).exists():
        print(f"\n⚠️  Image not found: {image_path}")
        print("Please provide a test image to run this example.")
        return

    # Detect animals
    result_image, detections = detector.detect_animals(image_path)

    # Print results
    summary = detector.get_detection_summary(detections)
    print(f"\n{summary}\n")

    if detections:
        print("Detected animals:")
        for i, det in enumerate(detections, 1):
            print(f"  {i}. {det['class'].capitalize()} - "
                  f"Confidence: {det['confidence']:.2%}")

    # Save result
    output_path = "example_result.jpg"
    cv2.imwrite(output_path, result_image)
    print(f"\n✓ Result saved to: {output_path}")


def example_custom_confidence():
    """Example 2: Custom confidence threshold"""
    print("\n" + "=" * 60)
    print("Example 2: Custom Confidence Threshold")
    print("=" * 60)

    # Initialize with higher confidence threshold
    detector = AnimalDetector(confidence_threshold=0.7)

    print(f"\nDetector initialized with confidence threshold: 0.7")
    print("This will only detect animals with >70% confidence")


def example_batch_processing():
    """Example 3: Batch processing multiple images"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Processing")
    print("=" * 60)

    detector = AnimalDetector()

    # Example image list (you'll need to provide actual images)
    image_files = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
    ]

    results = []

    for image_path in image_files:
        if Path(image_path).exists():
            print(f"\nProcessing: {image_path}")
            result_image, detections = detector.detect_animals(image_path)
            summary = detector.get_detection_summary(detections)
            print(f"  {summary}")

            results.append({
                'image': image_path,
                'detections': detections
            })
        else:
            print(f"  ⚠️  File not found: {image_path}")

    print(f"\n✓ Processed {len(results)} images")


def example_programmatic_api():
    """Example 4: Using the detector programmatically"""
    print("\n" + "=" * 60)
    print("Example 4: Programmatic API Usage")
    print("=" * 60)

    # Create detector with custom settings
    detector = AnimalDetector(
        confidence_threshold=0.5,
        nms_threshold=0.4
    )

    # Get supported animals
    print("\nSupported animals:")
    for animal in sorted(AnimalDetector.CORE_ANIMALS):
        print(f"  - {animal.capitalize()}")

    print(f"\nTotal: {len(AnimalDetector.CORE_ANIMALS)} animal types")


def example_detection_filtering():
    """Example 5: Filtering detections by animal type"""
    print("\n" + "=" * 60)
    print("Example 5: Filter Detections by Type")
    print("=" * 60)

    detector = AnimalDetector()

    image_path = "test_image.jpg"

    if Path(image_path).exists():
        result_image, detections = detector.detect_animals(image_path)

        # Filter for specific animals (e.g., only dogs and cats)
        target_animals = {'dog', 'cat'}
        filtered = [d for d in detections if d['class'] in target_animals]

        print(f"\nTotal detections: {len(detections)}")
        print(f"Dogs and cats only: {len(filtered)}")

        for det in filtered:
            print(f"  - {det['class'].capitalize()}: {det['confidence']:.2%}")
    else:
        print(f"⚠️  Image not found: {image_path}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "🐾 Animal Detection API Examples" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")

    examples = [
        ("Basic Detection", example_basic_detection),
        ("Custom Confidence", example_custom_confidence),
        ("Batch Processing", example_batch_processing),
        ("Programmatic API", example_programmatic_api),
        ("Detection Filtering", example_detection_filtering),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n  0. Run all examples")
    print()

    try:
        choice = input("Select an example to run (0-5): ").strip()

        if choice == "0":
            # Run all examples
            for name, func in examples:
                func()
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            # Run selected example
            examples[int(choice) - 1][1]()
        else:
            print("Invalid choice.")
            return

        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\nExamples cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
