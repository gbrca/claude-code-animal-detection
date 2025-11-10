# 🐾 AI Animal Detection App

A powerful and easy-to-use animal detection application using deep learning. Detect animals in images using state-of-the-art YOLO (You Only Look Once) AI model. Optimized for Raspberry Pi and other edge devices.

## Features

- **Real-time Animal Detection**: Detect 10+ types of animals including cats, dogs, birds, horses, and more
- **Multiple Interfaces**: Both CLI and web-based interfaces available
- **High Accuracy**: Uses YOLOv3-tiny pre-trained model with COCO dataset
- **Raspberry Pi Optimized**: Lightweight and efficient for edge computing
- **Easy to Use**: Simple drag-and-drop web interface or command-line tool
- **Automatic Model Download**: Models are downloaded automatically on first run

## Supported Animals

- 🐦 Bird
- 🐱 Cat
- 🐕 Dog
- 🐴 Horse
- 🐑 Sheep
- 🐄 Cow
- 🐘 Elephant
- 🐻 Bear
- 🦓 Zebra
- 🦒 Giraffe

## Installation

### Prerequisites

- **Python 3.11 or 3.12** (recommended) or Python 3.8-3.13
- pip package manager
- 2GB+ free disk space (for models)
- Internet connection (for initial model download)

> **Windows Users**: If you encounter installation errors, see [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for detailed troubleshooting.

### Quick Setup

#### Windows (Easy Way)

1. **Double-click** `setup_windows.bat`
2. Follow the prompts
3. Done!

Or manually:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src\app.py
```

#### Linux/Mac/Raspberry Pi

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/claude-code-animal-detection.git
cd claude-code-animal-detection
```

2. **Run quick setup script**
```bash
chmod +x quickstart.sh
./quickstart.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **First run** - Models will be downloaded automatically
The YOLO models (~35MB) will be downloaded on first use.

## Usage

### Web Interface (Recommended)

1. **Start the web server**
```bash
python src/app.py
```

2. **Open your browser**
Navigate to: `http://localhost:5000`

3. **Upload and detect**
- Drag and drop an image, or click to browse
- Wait for the AI to analyze the image
- View detected animals with bounding boxes

### Command Line Interface

**Basic usage:**
```bash
python main.py path/to/image.jpg
```

**With options:**
```bash
# Save output to specific file
python main.py image.jpg --output result.jpg

# Adjust confidence threshold
python main.py image.jpg --confidence 0.6

# Display result in a window
python main.py image.jpg --show

# Combine options
python main.py image.jpg -o result.jpg -c 0.7 -s
```

**CLI Options:**
- `-o, --output`: Path to save the output image (default: `<filename>_detected.jpg`)
- `-c, --confidence`: Confidence threshold 0.0-1.0 (default: 0.5)
- `-s, --show`: Display result in a window
- `--no-download`: Skip automatic model download

## Examples

### Example 1: Basic Detection
```bash
python main.py test_images/cat.jpg
```

Output:
```
Initializing animal detector...
Processing image: test_images/cat.jpg

==================================================
Detected: 1 cat
==================================================

Detailed results (1 detection(s)):
  1. Cat - Confidence: 98.50% - Box: (120, 80, 200x180)

✓ Output saved to: test_images/cat_detected.jpg
```

### Example 2: Web Interface

1. Start server: `python src/app.py`
2. Upload an image through the browser
3. View real-time detection results with visual bounding boxes

## Project Structure

```
claude-code-animal-detection/
├── src/
│   ├── detector.py      # Core detection module
│   └── app.py           # Flask web application
├── models/              # YOLO model files (auto-downloaded)
├── uploads/             # Uploaded images (web interface)
├── static/              # Web assets
│   ├── css/
│   └── js/
├── templates/           # HTML templates
├── main.py             # CLI interface
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Endpoints

The web server provides several endpoints:

- `GET /` - Main web interface
- `POST /upload` - Upload image for detection
- `GET /uploads/<filename>` - Serve uploaded/result images
- `GET /health` - Health check endpoint
- `GET /api/info` - API information

## Configuration

### Detector Settings

Edit `src/detector.py` to modify:

```python
detector = AnimalDetector(
    confidence_threshold=0.5,  # Detection confidence (0.0-1.0)
    nms_threshold=0.4         # Non-maximum suppression threshold
)
```

### Web Server Settings

Edit `src/app.py` to modify:

```python
MAX_FILE_SIZE = 16 * 1024 * 1024  # Maximum upload size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
```

## Performance

### Raspberry Pi 4 (4GB)
- Processing time: 2-4 seconds per image
- Memory usage: ~500MB
- Model: YOLOv3-tiny (optimized)

### Desktop/Laptop
- Processing time: <1 second per image
- Memory usage: ~400MB

## Troubleshooting

### Models not downloading
If automatic download fails:
```bash
cd models
wget https://pjreddie.com/media/files/yolov3-tiny.weights
wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg
wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
```

### OpenCV display issues (Linux)
Install additional packages:
```bash
sudo apt-get install python3-opencv
sudo apt-get install libgl1-mesa-glx
```

### Memory issues on Raspberry Pi
Reduce image size before processing or increase swap space.

## Technical Details

- **Model**: YOLOv3-tiny
- **Framework**: OpenCV DNN module
- **Dataset**: COCO (Common Objects in Context)
- **Backend**: Flask web server
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## Requirements

```
opencv-python==4.8.1.78
numpy==1.24.3
flask==3.0.0
werkzeug==3.0.1
pillow==10.1.0
requests==2.31.0
```

## License

MIT License - Feel free to use and modify for your projects.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- YOLO (You Only Look Once) by Joseph Redmon
- COCO Dataset
- OpenCV community
- Flask framework

## Future Enhancements

- [ ] Add video detection support
- [ ] Real-time webcam detection
- [ ] Mobile app version
- [ ] Additional animal species
- [ ] Batch processing support
- [ ] REST API with authentication
- [ ] Docker containerization
- [ ] GPU acceleration support

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Made with ❤️ for animal lovers and AI enthusiasts
