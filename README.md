# QR Code Generator/Decoder Application

## Overview

This application provides a graphical interface to:
- Encode binary strings (sequences of 0s and 1s) into custom QR codes (5x5 or 7x7 format)
- Decode images of these custom QR codes back to their binary representation

## Features

- **Encoding**:
  - Input any binary string (e.g., "1010101")
  - Choose between 5x5 (9-bit) or 7x7 (25-bit) formats
  - Automatic padding/truncation to fit selected format
  - Preview and save generated QR codes

- **Decoding**:
  - Load QR code images (PNG)
  - Extract the original binary data
  - Display decoded bits

## Requirements

- Python 3.6+
- Required packages:
  ```
  PyQt5
  Pillow
  opencv-python
  numpy
  ```

Install requirements with:
```bash
pip install PyQt5 pillow opencv-python numpy
```

## Installation

1. Clone the repository or download the files:
   ```
   git clone https://github.com/your-repo/custom-qr-app.git
   cd custom-qr-app
   ```

2. The application consists of two main files:
   - `fenetre.py` - The GUI application
   - `qr.py` - Core QR code generation/decoding logic

## Usage

Run the application:
```bash
python fenetre.py
```

### Encoding
1. Enter a binary string (only 0s and 1s)
2. Select format (5x5 or 7x7)
3. Click "Generate QR Code"
4. Save the image using "Save Image" button

### Decoding
1. Click "Load QR Image"
2. Select your QR code image
3. Click "Decode Image"
4. View the decoded binary string

## Technical Details

### QR Code Format
- **5x5 Format**:
  - 9-bit capacity (3x3 center area)
  - Fixed border pattern for orientation

- **7x7 Format**:
  - 25-bit capacity (5x5 center area)
  - Fixed border pattern for orientation

### File Structure
```
custom-qr-app/
├── fenetre.py        # GUI application
├── qr.py          # Core QR code logic
└── README.md      # This file
```

## Troubleshooting

### Common Issues
1. **Wayland-related warnings**:
   - Run with: `QT_QPA_PLATFORM=xcb python fenetre.py`
   - Or set environment variable: `export QT_QPA_PLATFORM=xcb`

2. **Binary string validation**:
   - Only 0s and 1s accepted
   - Automatic truncation/padding occurs if length doesn't match format

3. **Image loading issues**:
   - Supported formats: PNG,
   - Ensure images are clear and properly aligned

## License

This project is licensed under the MIT License.

---

**Note**: This application generates custom QR codes that are not compatible with standard QR code readers. The codes are designed for use with this specific decoder.