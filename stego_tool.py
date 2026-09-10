#!/usr/bin/env python3
"""
=====================================================================
 Image Steganography Tool (LSB Technique)
 Author: <Your Name>

 Features:
   1. HIDE  — embed a secret text message inside a PNG image using
      Least Significant Bit (LSB) encoding
   2. EXTRACT — recover a hidden message from a steganographic image
   3. ANALYZE — basic statistical check to flag whether an image is
      likely to contain hidden LSB data (detection side of the project)
   4. Optional password-based XOR obfuscation of the message before
      embedding, so extraction without the password gives garbage

 How LSB steganography works:
   Every pixel in an image has Red, Green, Blue values (0-255 each).
   Changing the LAST bit of each value shifts the color by at most 1
   out of 255 — invisible to the human eye. We use these least
   significant bits to store our secret message, bit by bit.

 Usage:
   python stego_tool.py hide   -i cover.png -o secret.png -m "Hidden message"
   python stego_tool.py hide   -i cover.png -o secret.png -f message.txt
   python stego_tool.py extract -i secret.png
   python stego_tool.py analyze -i secret.png
   (add --password "yourpass" to hide/extract for XOR obfuscation)
=====================================================================
"""

import argparse
import sys
from PIL import Image

DELIMITER = "#####END#####"  # marks the end of the hidden message


# ---------------------------------------------------------------
# OPTIONAL XOR OBFUSCATION (simple, educational — not real crypto)
# ---------------------------------------------------------------
def xor_cipher(data: str, password: str) -> str:
    if not password:
        return data
    return "".join(
        chr(ord(char) ^ ord(password[i % len(password)]))
        for i, char in enumerate(data)
    )


# ---------------------------------------------------------------
# TEXT <-> BINARY HELPERS
# ---------------------------------------------------------------
def text_to_binary(text: str) -> str:
    return "".join(format(ord(char), "08b") for char in text)


def binary_to_text(binary: str) -> str:
    chars = [binary[i:i + 8] for i in range(0, len(binary), 8)]
    return "".join(chr(int(b, 2)) for b in chars if len(b) == 8)


# ---------------------------------------------------------------
# HIDE MESSAGE
# ---------------------------------------------------------------
def hide_message(input_path: str, output_path: str, message: str, password: str = ""):
    image = Image.open(input_path)
    image = image.convert("RGB")
    width, height = image.size
    max_bytes = (width * height * 3) // 8

    message = xor_cipher(message, password) if password else message
    full_message = message + DELIMITER
    binary_message = text_to_binary(full_message)

    if len(binary_message) > width * height * 3:
        print(f"Error: Message too large for this image.")
        print(f"  This image can hold ~{max_bytes} characters. "
              f"Your message needs ~{len(full_message)} characters.")
        sys.exit(1)

    pixels = list(image.getdata())
    new_pixels = []
    bit_index = 0
    total_bits = len(binary_message)

    for pixel in pixels:
        r, g, b = pixel
        if bit_index < total_bits:
            r = (r & ~1) | int(binary_message[bit_index]); bit_index += 1
        if bit_index < total_bits:
            g = (g & ~1) | int(binary_message[bit_index]); bit_index += 1
        if bit_index < total_bits:
            b = (b & ~1) | int(binary_message[bit_index]); bit_index += 1
        new_pixels.append((r, g, b))

    stego_image = Image.new("RGB", image.size)
    stego_image.putdata(new_pixels)
    stego_image.save(output_path, "PNG")

    print(f"✓ Message hidden successfully in '{output_path}'")
    print(f"  Message length: {len(message)} characters")
    print(f"  Image capacity used: {round((total_bits / (width*height*3)) * 100, 2)}%")
    if password:
        print("  Note: message was XOR-obfuscated with your password before embedding.")


# ---------------------------------------------------------------
# EXTRACT MESSAGE
# ---------------------------------------------------------------
def extract_message(input_path: str, password: str = "") -> str:
    image = Image.open(input_path)
    image = image.convert("RGB")
    pixels = list(image.getdata())

    bits = []
    for pixel in pixels:
        for channel in pixel:  # r, g, b
            bits.append(str(channel & 1))

    binary_data = "".join(bits)
    decoded = binary_to_text(binary_data)

    if DELIMITER in decoded:
        message = decoded.split(DELIMITER)[0]
    else:
        # Delimiter not found within a reasonable scan window — likely no hidden message
        return None

    if password:
        message = xor_cipher(message, password)

    return message


# ---------------------------------------------------------------
# ANALYZE (basic LSB steganalysis)
# ---------------------------------------------------------------
def analyze_image(input_path: str):
    """
    Basic Chi-Square-style heuristic: in a natural (non-stego) image,
    LSBs tend to correlate loosely with pixel content. After LSB
    steganography, LSBs approach a uniform 50/50 random distribution.
    This is a simplified educational check, not a production-grade
    steganalysis tool.
    """
    image = Image.open(input_path).convert("RGB")
    pixels = list(image.getdata())

    total_bits = 0
    ones = 0
    for pixel in pixels:
        for channel in pixel:
            total_bits += 1
            if channel & 1:
                ones += 1

    ratio = ones / total_bits
    print(f"Analyzing '{input_path}'...")
    print(f"  Total pixel-channel samples: {total_bits}")
    print(f"  LSB '1' ratio: {round(ratio * 100, 2)}%  (natural images typically deviate more from 50%)")

    if 0.48 <= ratio <= 0.52:
        print("  ⚠ LSB distribution is very close to 50/50 — this image MAY contain hidden data.")
    else:
        print("  ✓ LSB distribution looks like a typical natural image (less likely to contain hidden data).")

    # Try a direct extraction attempt too
    result = extract_message(input_path)
    if result:
        print(f"  ⚠ A hidden message delimiter was found! Extracted preview: {result[:50]}...")
    else:
        print("  No readable hidden message delimiter found (message may be password-protected or absent).")


# ---------------------------------------------------------------
# MAIN / CLI
# ---------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Image Steganography Tool (LSB technique)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    hide_parser = subparsers.add_parser("hide", help="Hide a message inside an image")
    hide_parser.add_argument("-i", "--input", required=True, help="Cover image path (PNG recommended)")
    hide_parser.add_argument("-o", "--output", required=True, help="Output stego image path")
    group = hide_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--message", help="Message text to hide")
    group.add_argument("-f", "--file", help="Path to a text file whose contents will be hidden")
    hide_parser.add_argument("--password", default="", help="Optional password to XOR-obfuscate the message")

    extract_parser = subparsers.add_parser("extract", help="Extract a hidden message from an image")
    extract_parser.add_argument("-i", "--input", required=True, help="Stego image path")
    extract_parser.add_argument("--password", default="", help="Password used during hiding, if any")

    analyze_parser = subparsers.add_parser("analyze", help="Check if an image likely contains hidden LSB data")
    analyze_parser.add_argument("-i", "--input", required=True, help="Image path to analyze")

    args = parser.parse_args()

    if args.command == "hide":
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                message = f.read()
        else:
            message = args.message
        hide_message(args.input, args.output, message, args.password)

    elif args.command == "extract":
        result = extract_message(args.input, args.password)
        if result is not None:
            print("✓ Hidden message found:\n")
            print(result)
        else:
            print("No hidden message found in this image (or wrong/missing password).")

    elif args.command == "analyze":
        analyze_image(args.input)


if __name__ == "__main__":
    main()
