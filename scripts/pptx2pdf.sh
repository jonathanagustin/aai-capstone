#!/usr/bin/env bash

echo "Converting presentations to PDF..."
for file in *.pptx; do
    if [ -f "$file" ]; then
    echo "Converting $file to PDF..."
    libreoffice --headless --convert-to pdf "$file"
    fi
done
