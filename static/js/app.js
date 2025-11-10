// Animal Detection Web App JavaScript

const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const error = document.getElementById('error');
const uploadSection = document.querySelector('.upload-section');

// Drag and drop functionality
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#764ba2';
    uploadBox.style.background = '#e9ecef';
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.style.borderColor = '#667eea';
    uploadBox.style.background = '#f8f9fa';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#667eea';
    uploadBox.style.background = '#f8f9fa';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Handle file upload
async function handleFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file type. Please upload a valid image file (JPG, PNG, GIF, BMP).');
        return;
    }

    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File too large. Maximum size is 16MB.');
        return;
    }

    // Show loading
    uploadSection.style.display = 'none';
    loading.style.display = 'block';
    results.style.display = 'none';
    error.style.display = 'none';

    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload and process
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showResults(data);
        } else {
            showError(data.error || 'An error occurred during processing.');
        }
    } catch (err) {
        showError('Failed to connect to the server. Please try again.');
        console.error('Upload error:', err);
    }
}

// Show results
function showResults(data) {
    loading.style.display = 'none';
    results.style.display = 'block';

    // Set summary
    document.getElementById('summary').textContent = data.summary;

    // Set images
    document.getElementById('originalImage').src = data.original_image;
    document.getElementById('resultImage').src = data.result_image;

    // Display detections list
    const detectionsList = document.getElementById('detectionsList');
    if (data.detections && data.detections.length > 0) {
        let html = '<h3>Detailed Detections</h3>';
        data.detections.forEach((det, index) => {
            const confidence = (det.confidence * 100).toFixed(1);
            html += `
                <div class="detection-item">
                    <strong>${index + 1}. ${capitalizeFirst(det.class)}</strong><br>
                    Confidence: ${confidence}%<br>
                    Position: (${det.box.x}, ${det.box.y}), Size: ${det.box.width}x${det.box.height}
                </div>
            `;
        });
        detectionsList.innerHTML = html;
    } else {
        detectionsList.innerHTML = '';
    }
}

// Show error
function showError(message) {
    loading.style.display = 'none';
    uploadSection.style.display = 'none';
    results.style.display = 'none';
    error.style.display = 'block';

    document.getElementById('errorMessage').textContent = message;
}

// Reset app
function resetApp() {
    uploadSection.style.display = 'block';
    loading.style.display = 'none';
    results.style.display = 'none';
    error.style.display = 'none';
    fileInput.value = '';
}

// Utility function
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Page load
console.log('🐾 Animal Detection App loaded successfully');
console.log('Ready to detect animals in images!');
