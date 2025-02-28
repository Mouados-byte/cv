#!/bin/bash

# Check if wkhtmltopdf is installed
if ! command -v wkhtmltopdf &> /dev/null
then
    echo "Error: wkhtmltopdf is not installed."
    echo "Install it with:"
    echo "  Debian/Ubuntu: sudo apt install wkhtmltopdf"
    echo "  Fedora: sudo dnf install wkhtmltopdf"
    echo "  Arch: sudo pacman -S wkhtmltopdf"
    exit 1
fi

# Input and output filenames
INPUT_HTML="cv.html"
OUTPUT_PDF="cv.pdf"

# Check if input HTML file exists
if [ ! -f "$INPUT_HTML" ]; then
    echo "Error: Input file $INPUT_HTML not found!"
    exit 1
fi

# Conversion command with formatting options
wkhtmltopdf \
    --page-size A4 \
    --margin-top 0mm \
    --margin-bottom 0mm \
    --margin-left 0mm \
    --margin-right 0mm \
    --disable-smart-shrinking \
    "$INPUT_HTML" \
    "$OUTPUT_PDF"

echo "Conversion complete! PDF saved as $OUTPUT_PDF"