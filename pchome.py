#!/usr/bin/env python

from PIL import Image
import subprocess
import argparse
import os

THRESHOLD = 150


def getval(p):
    return (p[0] + p[1] + p[2]) / 3


def main():
    parser = argparse.ArgumentParser(description='Read pchome.com.tw login '
                                                 'captcha')
    parser.add_argument(dest='input_image', type=str)
    options = parser.parse_args()

    input_image_filename = options.input_image
    output_image_filename = os.path.splitext(input_image_filename)[0] + \
        "-processed.png"

    orig_img = Image.open(input_image_filename).convert("RGB")
    w, h = orig_img.width, orig_img.height
    new_img = Image.new('L', (orig_img.width, orig_img.height))

    # Set new image border white
    for x in range(0, w):
        new_img.putpixel((x, 0), 255)
        new_img.putpixel((x, h - 1), 255)
    for y in range(1, h - 1):
        new_img.putpixel((0, y), 255)
        new_img.putpixel((w - 1, y), 255)

    # Clean noise
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            weight = getval(orig_img.getpixel((x, y)))
            weight += getval(orig_img.getpixel((x - 1, y)))
            weight += getval(orig_img.getpixel((x + 1, y)))
            weight += getval(orig_img.getpixel((x, y - 1)))
            weight += getval(orig_img.getpixel((x, y + 1)))

            if (weight / 5) < THRESHOLD:
                new_img.putpixel((x, y), 0)
            else:
                new_img.putpixel((x, y), 255)

    new_img.save(output_image_filename)
    print("Save processed image to %s" % output_image_filename)
    proc = subprocess.Popen(["tesseract", output_image_filename, "stdout"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    output, errorlog = proc.communicate()
    if proc.returncode == 0:
        print("OCR Result: %s" % output.decode("ascii").strip())
    else:
        print("OCR Error: %s" % errorlog)


if __name__ == "__main__":
    main()
