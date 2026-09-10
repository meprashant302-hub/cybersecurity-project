# Image Steganography Tool

A simple Python command-line tool that hides text inside PNG images using **LSB (Least Significant Bit) steganography**.

The tool can:

* Hide a text message inside an image
* Extract the hidden message
* Hide text from a file
* Use a password with XOR-based obfuscation
* Analyze an image for possible hidden data

## Tech Used

* Python
* Pillow
* LSB Steganography
* Basic image and bit manipulation

## How It Works

The tool changes the last bit of the RGB values of pixels to store the message.

For example, if a pixel has:

```text
R = 200 → 11001000
G = 150 → 10010110
B = 90  → 01011010
```

The last bit of these values can be changed to store information. The change is very small, so it is normally not visible when looking at the image.

A special marker is added at the end of the message so that the extraction process knows where the hidden message ends.

## Installation

Install Pillow using:

```bash
pip install Pillow
```

## Usage

### 1. Hide a message

```bash
python stego_tool.py hide -i cover.png -o secret.png -m "Your secret message"
```

### 2. Hide text from a file

```bash
python stego_tool.py hide -i cover.png -o secret.png -f message.txt
```

### 3. Hide a message with a password

```bash
python stego_tool.py hide -i cover.png -o secret.png -m "Top secret" --password "mypass123"
```

### 4. Extract a message

```bash
python stego_tool.py extract -i secret.png
```

If a password was used:

```bash
python stego_tool.py extract -i secret.png --password "mypass123"
```

### 5. Analyze an image

```bash
python stego_tool.py analyze -i secret.png
```

The analyze command checks the distribution of LSBs and also looks for the message marker. It is only a basic check and should not be considered a complete steganalysis tool.

## Example

```text
✓ Message hidden successfully in 'secret.png'
  Message length: 52 characters
  Image capacity used: 0.43%

✓ Hidden message found:

This is a secret cybersecurity project test message!
```

## Important Notes

* Use **PNG images** for this project. JPEG compression can destroy the hidden data.
* Larger images can store more data.
* The password option currently uses a simple **XOR operation**. It is included for learning purposes and is **not secure encryption**.
* The analyze feature is a basic implementation and can produce false positives or miss some hidden data.

## What I Learned

While building this project, I worked with:

* Binary and bit-level operations
* Image processing using Pillow
* Reading and writing image pixels
* Basic steganography concepts
* Simple statistical analysis for detecting possible hidden data
* Command-line argument handling in Python

## Future Improvements

Some improvements I would like to make:

* Add AES encryption before hiding the message
* Support hiding files instead of only text
* Add a simple GUI
* Improve the image analysis/detection method
* Add support for other types of media

## Resume Description

**Image Steganography Tool — Python**

Built a Python-based tool that uses LSB steganography to hide and extract text from PNG images, with password-based XOR obfuscation and a basic LSB analysis feature for detecting possible hidden data.
