#!/usr/bin/env python3
"""Convert photos to grayscale and stack them vertically into one image.

Each photo is converted to grayscale, optionally gamma corrected, and then
placed in a canvas whose width equals the widest photo. Narrower photos are
centered horizontally, and the unfilled pixels are padded with a given value.
Photos are ordered alphabetically by file name.

Requirements
------------
numpy, pillow, jsonargparse, loguru

Examples
--------
Use every image in a directory::

    python stack_gray.py --inputs photos/ --output stacked --output_format png

Use an explicit list of files with per-photo gamma (gamma values are matched
to the sorted photo order)::

    python stack_gray.py --inputs '[a.jpg, b.png, c.tif]' \\
        --gamma '[1.0, 2.2, 0.8]' --pad_value 255 --output out.jpg
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Literal, Optional, Sequence, Tuple

import numpy as np
from jsonargparse import CLI
from loguru import logger
from PIL import Image, ImageOps

#: File extensions treated as images when a directory is given.
IMAGE_EXTENSIONS: frozenset = frozenset(
    {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif", ".webp"}
)

#: Supported output formats mapped to (valid extensions, Pillow format name, default extension).
OUTPUT_FORMATS: Dict[str, Tuple[Tuple[str, ...], str, str]] = {
    "jpeg": ((".jpg", ".jpeg"), "JPEG", ".jpg"),
    "png": ((".png",), "PNG", ".png"),
    "tiff": ((".tif", ".tiff"), "TIFF", ".tif"),
    "bmp": ((".bmp",), "BMP", ".bmp"),
}


def collect_paths(inputs: Sequence[str]) -> List[Path]:
    """Expand the input arguments into a sorted list of image file paths.

    Parameters
    ----------
    inputs : Sequence[str]
        File names and/or directory names. Directories are scanned
        (non-recursively) for files with a known image extension.

    Returns
    -------
    List[Path]
        Unique image paths sorted alphabetically by file name
        (case-insensitive, with the full path as a tie-breaker).
    """
    found: List[Path] = []
    for item in inputs:
        path = Path(item).expanduser()
        if path.is_dir():
            matches = sorted(
                p
                for p in path.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
            )
            logger.info("Directory '{}' contributes {} image(s)", path, len(matches))
            found.extend(matches)
        elif path.is_file():
            found.append(path)
        else:
            logger.warning("Input does not exist, skipping: {}", path)

    unique = list(dict.fromkeys(found))
    return sorted(unique, key=lambda p: (p.name.casefold(), str(p)))


def load_grayscale(path: Path) -> Optional[np.ndarray]:
    """Read an image file and convert it to an 8-bit grayscale array.

    EXIF orientation is applied so that rotated phone photos are upright.

    Parameters
    ----------
    path : Path
        Path to the image file.

    Returns
    -------
    numpy.ndarray or None
        Array of shape (height, width) with dtype ``uint8``, or ``None`` if the
        file could not be read or converted (a warning is logged).
    """
    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            gray = img.convert("L")
            return np.asarray(gray, dtype=np.uint8).copy()
    except Exception as exc:  # noqa: BLE001 - any read/convert failure means skip
        logger.warning("Could not read or convert '{}', skipping: {}", path, exc)
        return None


def build_gamma_lut(gamma: float) -> np.ndarray:
    """Build a lookup table implementing gamma correction for 8-bit values.

    The mapping is ``out = 255 * (in / 255) ** (1 / gamma)``, so a gamma
    greater than 1 brightens midtones and a gamma less than 1 darkens them.

    Parameters
    ----------
    gamma : float
        Gamma value. Must be strictly positive.

    Returns
    -------
    numpy.ndarray
        Array of shape (256,) with dtype ``uint8`` mapping input to output levels.
    """
    levels = np.arange(256, dtype=np.float64) / 255.0
    return np.round(255.0 * np.power(levels, 1.0 / gamma)).astype(np.uint8)


def apply_gamma(image: np.ndarray, gamma: float) -> np.ndarray:
    """Apply gamma correction to a grayscale image.

    Parameters
    ----------
    image : numpy.ndarray
        Grayscale image with dtype ``uint8``.
    gamma : float
        Gamma value. A value of 1.0 returns the image unchanged.

    Returns
    -------
    numpy.ndarray
        Gamma-corrected image with the same shape and dtype.
    """
    if gamma == 1.0:
        return image
    return build_gamma_lut(gamma)[image]


def stack_centered(images: Sequence[np.ndarray], pad_value: int = 0) -> np.ndarray:
    """Stack grayscale images vertically, centering each one horizontally.

    The canvas width equals the widest image. Narrower images are centered,
    and the remaining pixels are filled with ``pad_value``.

    Parameters
    ----------
    images : Sequence[numpy.ndarray]
        Grayscale images of shape (height, width) with dtype ``uint8``.
        Must contain at least one image.
    pad_value : int, optional
        Gray level (0-255) used for unfilled pixels. Default is 0 (black).

    Returns
    -------
    numpy.ndarray
        Combined image of shape (sum of heights, max width) with dtype ``uint8``.

    Raises
    ------
    ValueError
        If ``images`` is empty.
    """
    if not images:
        raise ValueError("At least one image is required to stack.")

    width = max(img.shape[1] for img in images)
    height = sum(img.shape[0] for img in images)
    canvas = np.full((height, width), pad_value, dtype=np.uint8)

    row = 0
    for img in images:
        h, w = img.shape
        col = (width - w) // 2
        canvas[row : row + h, col : col + w] = img
        row += h
    return canvas


def resolve_output_path(output: str, output_format: str) -> Path:
    """Make sure the output file name has an extension matching the format.

    If the name has no recognized image extension, the default extension for
    the format is appended. If it has a different recognized extension, that
    extension is replaced.

    Parameters
    ----------
    output : str
        Requested output file name or path.
    output_format : str
        One of the keys of :data:`OUTPUT_FORMATS`.

    Returns
    -------
    Path
        Output path with an extension consistent with ``output_format``.
    """
    valid_exts, _, default_ext = OUTPUT_FORMATS[output_format]
    path = Path(output).expanduser()
    if path.suffix.lower() in valid_exts:
        return path

    known = {ext for exts, _, _ in OUTPUT_FORMATS.values() for ext in exts}
    if path.suffix.lower() in known:
        new_path = path.with_suffix(default_ext)
    else:
        new_path = path.with_name(path.name + default_ext)
    logger.warning("Output '{}' does not match format '{}'; writing to '{}'", path, output_format, new_path)
    return new_path


def resolve_gammas(gamma: Optional[List[float]], count: int) -> List[float]:
    """Expand the gamma argument into one value per photo.

    Parameters
    ----------
    gamma : List[float] or None
        ``None`` means no correction. A single value applies to every photo.
        Otherwise there must be exactly one value per photo, in sorted order.
    count : int
        Number of photos that will be processed.

    Returns
    -------
    List[float]
        Gamma value for each photo, in sorted photo order.

    Raises
    ------
    ValueError
        If the number of gamma values is invalid or any value is not positive.
    """
    if gamma is None:
        values = [1.0]
    else:
        values = list(gamma)

    if any(g <= 0 for g in values):
        raise ValueError(f"Gamma values must be positive, got {values}.")

    if len(values) == 1:
        return values * count
    if len(values) == count:
        return values
    raise ValueError(
        f"Got {len(values)} gamma value(s) for {count} photo(s). "
        "Provide one value (applied to all) or one per photo."
    )


def main(
    inputs: List[str],
    output: str = "stacked_photos",
    output_format: Literal["jpeg", "png", "tiff", "bmp"] = "jpeg",
    gamma: Optional[List[float]] = None,
    pad_value: int = 0,
) -> str:
    """Convert photos to grayscale and stack them vertically.

    Parameters
    ----------
    inputs : List[str]
        Either a single directory, or a list of image file names. Photos are
        processed in alphabetical order by file name.
    output : str, optional
        Name of the output file. An extension matching ``output_format`` is
        added or corrected if needed. Default is ``stacked_photos``.
    output_format : {"jpeg", "png", "tiff", "bmp"}, optional
        Output image format. Default is ``jpeg``.
    gamma : List[float] or None, optional
        Gamma correction value(s). Pass one value to apply it to all photos, or
        one value per photo in sorted order. Values must be positive, and 1.0
        means no correction. Default is None (no correction).
    pad_value : int, optional
        Gray level (0-255) used to fill pixels outside each photo. Default is 0.

    Returns
    -------
    str
        Path of the written output file.

    Raises
    ------
    SystemExit
        If no usable photos are found or the inputs are invalid.
    """
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<level>{level: <8}</level> | {message}")

    if not 0 <= pad_value <= 255:
        raise ValueError(f"pad_value must be between 0 and 255, got {pad_value}.")

    paths = collect_paths(inputs)
    if not paths:
        logger.error("No input images found.")
        raise SystemExit(1)

    gammas = resolve_gammas(gamma, len(paths))

    images: List[np.ndarray] = []
    for path, g in zip(paths, gammas):
        arr = load_grayscale(path)
        if arr is None:
            continue
        images.append(apply_gamma(arr, g))
        logger.info("Loaded '{}' ({}x{}, gamma={})", path.name, arr.shape[1], arr.shape[0], g)

    if not images:
        logger.error("None of the input photos could be read.")
        raise SystemExit(1)

    canvas = stack_centered(images, pad_value=pad_value)
    out_path = resolve_output_path(output, output_format)
    _, pil_format, _ = OUTPUT_FORMATS[output_format]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(canvas, mode="L").save(out_path, format=pil_format)
    logger.success(
        "Wrote {} photo(s) as {}x{} {} to '{}'",
        len(images), canvas.shape[1], canvas.shape[0], output_format, out_path,
    )
    return str(out_path)


if __name__ == "__main__":
    CLI(main)
