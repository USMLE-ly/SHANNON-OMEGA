---
name: sharp
description: High-performance image processing powered by libvips. Resize, convert, rotate, blur, and pipeline JPEG, PNG, WebP, AVIF, and TIFF images. Use when uploaded images need resizing, format conversion, or processing before analysis.
---

# sharp

High-performance image processing. Uses Node.js sharp (libvips) for fastest image operations.

## Usage

```bash
cd /root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free
source .venv/bin/activate

sharp-tool info photo.jpg                           # Get image info
sharp-tool convert photo.png photo.webp             # Convert format
sharp-tool resize photo.jpg thumb.jpg 200 200       # Resize to exact dimensions
sharp-tool resize photo.jpg wide.jpg 800            # Resize width, keep aspect
sharp-tool rotate photo.jpg rotated.jpg 90          # Rotate 90°
sharp-tool blur photo.jpg blurred.jpg 5             # Gaussian blur (sigma=5)
sharp-tool pipeline input.jpg output.webp --width 800 --quality 90  # Full pipeline
```

## Parameters

| Arg | Type | Default | Description |
|-----|------|---------|-------------|
| input | str | required | Input image path |
| output | str | required | Output image path |
| width | int | - | Target width in pixels |
| height | int | - | Target height in pixels |
| quality | int | 85 | Output quality (1-100) |
| degrees | int | 90 | Rotation degrees |
| sigma | float | 3 | Blur sigma value |
