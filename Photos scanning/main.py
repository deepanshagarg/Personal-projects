# main.py

import os
import numpy as np
from tqdm import tqdm

from detector import FaceDetector
from scoring import PhotoScorer
from clustering import FaceClusterer
from duplicates import DuplicateRemover
from optimizer import CoverageOptimizer
from exporter import Exporter
from utils import get_all_images


# =========================================================
# CONFIG
# =========================================================

INPUT_DIR = "input_photos"
OUTPUT_DIR = "output"

USE_GPU = True


# =========================================================
# LOAD MODULES
# =========================================================

print("=" * 60)
print("LOADING MODELS")
print("=" * 60)

detector = FaceDetector(
    model_name='buffalo_l',
    gpu=USE_GPU
)

scorer = PhotoScorer()

clusterer = FaceClusterer()

duplicate_remover = DuplicateRemover()

optimizer = CoverageOptimizer()

exporter = Exporter()


# =========================================================
# LOAD IMAGES
# =========================================================

print("\nScanning image folders...")

image_paths = get_all_images(INPUT_DIR)

print(f"Found {len(image_paths)} images")


# =========================================================
# DATABASES
# =========================================================

photo_database = []

all_embeddings = []

face_reference_map = []


# =========================================================
# STAGE 1 — FACE DETECTION
# =========================================================

print("\n" + "=" * 60)
print("STAGE 1 — FACE DETECTION")
print("=" * 60)

for image_path in tqdm(image_paths):

    try:

        result = detector.detect(image_path)

        if result is None:
            continue

        image = result['image']
        faces = result['faces']

        photo_entry = {
            'path': image_path,
            'faces': [],
            'people_ids': [],
            'quality': None
        }

        face_boxes = []

        for face_index, face in enumerate(faces):

            embedding = face['embedding']
            bbox = face['bbox']

            face_boxes.append(bbox)

            photo_entry['faces'].append({
                'face_index': face_index,
                'bbox': bbox,
                'embedding': embedding
            })

            all_embeddings.append(embedding)

            face_reference_map.append({
                'photo_index': len(photo_database),
                'face_index': face_index
            })

        quality = scorer.overall_score(
            image=image,
            face_boxes=face_boxes
        )

        photo_entry['quality'] = quality

        photo_database.append(photo_entry)

    except Exception as e:
        print(f"\nERROR processing {image_path}")
        print(str(e))


print(f"\nProcessed {len(photo_database)} photos")


# =========================================================
# STAGE 2 — FACE CLUSTERING
# =========================================================

print("\n" + "=" * 60)
print("STAGE 2 — FACE CLUSTERING")
print("=" * 60)

if len(all_embeddings) == 0:
    print("No faces detected.")
    exit()

embeddings_array = np.array(all_embeddings)

labels = clusterer.cluster(embeddings_array)

print(f"Generated {len(set(labels))} clusters")


# =========================================================
# STAGE 3 — ASSIGN PERSON IDs
# =========================================================

print("\n" + "=" * 60)
print("STAGE 3 — ASSIGN PERSON IDs")
print("=" * 60)

for label, ref in zip(labels, face_reference_map):

    if label == -1:
        continue

    photo_index = ref['photo_index']
    face_index = ref['face_index']

    photo_database[photo_index]['faces'][face_index]['person_id'] = int(label)


# =========================================================
# STAGE 4 — BUILD PHOTO PERSON MAP
# =========================================================

print("\n" + "=" * 60)
print("STAGE 4 — BUILD PHOTO PERSON MAP")
print("=" * 60)

for photo in photo_database:

    people_ids = []

    for face in photo['faces']:

        if 'person_id' in face:
            people_ids.append(face['person_id'])

    photo['people_ids'] = list(set(people_ids))


# =========================================================
# STAGE 5 — REMOVE DUPLICATE PHOTOS
# =========================================================

print("\n" + "=" * 60)
print("STAGE 5 — REMOVE DUPLICATES")
print("=" * 60)

before_count = len(photo_database)

photo_database = duplicate_remover.remove_duplicates(
    photo_database,
    threshold=5
)

after_count = len(photo_database)

print(f"Removed {before_count - after_count} duplicates")


# =========================================================
# STAGE 6 — COVERAGE OPTIMIZATION
# =========================================================

print("\n" + "=" * 60)
print("STAGE 6 — COVERAGE OPTIMIZATION")
print("=" * 60)

selected_photos = optimizer.select_best_photos(
    photo_database
)

print(f"Selected {len(selected_photos)} final photos")


# =========================================================
# STAGE 7 — EXPORT RESULTS
# =========================================================

print("\n" + "=" * 60)
print("STAGE 7 — EXPORTING")
print("=" * 60)

exporter.export_selected(
    selected_photos,
    OUTPUT_DIR
)

exporter.export_person_folders(
    photo_database,
    OUTPUT_DIR
)

exporter.export_excel(
    photo_database,
    OUTPUT_DIR
)

print("\nDONE")
print("=" * 60)

print(f"Final selected photos: {len(selected_photos)}")
print(f"Output folder: {OUTPUT_DIR}")