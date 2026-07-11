# utils.py

import os
import cv2
from PIL import Image
from datetime import datetime


# =========================================================
# VALID IMAGE EXTENSIONS
# =========================================================

VALID_EXTENSIONS = {
    '.jpg',
    '.jpeg',
    '.png',
    '.webp',
    '.bmp',
    '.tiff'
}


# =========================================================
# GET ALL IMAGE PATHS
# =========================================================

def get_all_images(folder_path):

    image_paths = []

    for root, dirs, files in os.walk(folder_path):

        for file in files:

            ext = os.path.splitext(file)[1].lower()

            if ext in VALID_EXTENSIONS:

                full_path = os.path.join(root, file)

                image_paths.append(full_path)

    image_paths.sort()

    return image_paths


# =========================================================
# SAFE IMAGE LOADER
# =========================================================

def load_image(image_path):

    try:

        image = cv2.imread(image_path)

        if image is None:
            return None

        return image

    except Exception as e:

        print(f"Error loading image: {image_path}")
        print(str(e))

        return None


# =========================================================
# IMAGE DIMENSIONS
# =========================================================

def get_image_dimensions(image_path):

    try:

        image = Image.open(image_path)

        width, height = image.size

        return width, height

    except:

        return None, None


# =========================================================
# FILE SIZE
# =========================================================

def get_file_size_mb(image_path):

    try:

        size_bytes = os.path.getsize(image_path)

        size_mb = size_bytes / (1024 * 1024)

        return round(size_mb, 2)

    except:

        return 0


# =========================================================
# FORMAT TIMESTAMP
# =========================================================

def format_timestamp(timestamp):

    return datetime.fromtimestamp(
        timestamp
    ).strftime("%Y-%m-%d %H:%M:%S")


# =========================================================
# IMAGE METADATA
# =========================================================

def get_image_metadata(image_path):

    try:

        stat = os.stat(image_path)

        width, height = get_image_dimensions(
            image_path
        )

        metadata = {

            'path':
                image_path,

            'filename':
                os.path.basename(image_path),

            'width':
                width,

            'height':
                height,

            'size_mb':
                get_file_size_mb(image_path),

            'created':
                format_timestamp(stat.st_ctime),

            'modified':
                format_timestamp(stat.st_mtime)
        }

        return metadata

    except Exception as e:

        print(f"Metadata error: {image_path}")
        print(str(e))

        return None


# =========================================================
# CHECK IMAGE VALIDITY
# =========================================================

def is_valid_image(image_path):

    try:

        image = Image.open(image_path)

        image.verify()

        return True

    except:

        return False


# =========================================================
# REMOVE CORRUPT IMAGES
# =========================================================

def filter_valid_images(image_paths):

    valid = []

    invalid = []

    for path in image_paths:

        if is_valid_image(path):
            valid.append(path)

        else:
            invalid.append(path)

    print("\n" + "=" * 50)
    print("IMAGE VALIDATION")
    print("=" * 50)

    print(f"Valid images   : {len(valid)}")
    print(f"Invalid images : {len(invalid)}")

    return valid


# =========================================================
# CREATE DIRECTORY
# =========================================================

def ensure_directory(path):

    os.makedirs(path, exist_ok=True)


# =========================================================
# PRINT HEADER
# =========================================================

def print_header(title):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# =========================================================
# PRINT PROGRESS
# =========================================================

def print_progress(current, total):

    percent = (current / total) * 100

    print(
        f"\rProgress: "
        f"{current}/{total} "
        f"({percent:.2f}%)",
        end=""
    )


# =========================================================
# HUMAN READABLE COUNT
# =========================================================

def human_readable_number(number):

    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"

    if number >= 1_000:
        return f"{number / 1_000:.1f}K"

    return str(number)


# =========================================================
# DEBUG PHOTO DATABASE
# =========================================================

def debug_photo_database(photo_database):

    print("\n" + "=" * 60)
    print("PHOTO DATABASE DEBUG")
    print("=" * 60)

    print(f"Total photos: {len(photo_database)}")

    total_faces = 0

    for photo in photo_database:

        total_faces += len(photo['faces'])

    print(f"Total faces: {total_faces}")

    unique_people = set()

    for photo in photo_database:

        for pid in photo['people_ids']:
            unique_people.add(pid)

    print(f"Unique people: {len(unique_people)}")


# =========================================================
# SORT BY QUALITY
# =========================================================

def sort_by_quality(photo_database):

    return sorted(
        photo_database,
        key=lambda x: x['quality']['final_score'],
        reverse=True
    )


# =========================================================
# TESTING
# =========================================================

if __name__ == "__main__":

    folder = "input_photos"

    images = get_all_images(folder)

    print(f"Found {len(images)} images")

    images = filter_valid_images(images)

    if len(images) > 0:

        metadata = get_image_metadata(
            images[0]
        )

        print("\nSample Metadata:\n")

        print(metadata)