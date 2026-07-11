# duplicates.py

from PIL import Image
import imagehash
import os
from collections import defaultdict


class DuplicateRemover:

    def __init__(
        self,
        hash_size=16
    ):

        self.hash_size = hash_size

    # =====================================================
    # GENERATE PERCEPTUAL HASH
    # =====================================================

    def get_hash(self, image_path):

        try:

            image = Image.open(image_path).convert("RGB")

            phash = imagehash.phash(
                image,
                hash_size=self.hash_size
            )

            return phash

        except Exception as e:

            print(f"Error hashing {image_path}")
            print(str(e))

            return None

    # =====================================================
    # HAMMING DISTANCE
    # =====================================================

    @staticmethod
    def hash_distance(hash1, hash2):

        return abs(hash1 - hash2)

    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    def is_duplicate(
        self,
        hash1,
        hash2,
        threshold=5
    ):

        distance = self.hash_distance(hash1, hash2)

        return distance <= threshold

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    def remove_duplicates(
        self,
        photo_database,
        threshold=5
    ):

        unique_photos = []

        stored_hashes = []

        duplicate_groups = defaultdict(list)

        for photo in photo_database:

            image_path = photo['path']

            image_hash = self.get_hash(image_path)

            if image_hash is None:
                continue

            is_dup = False

            for idx, existing_hash in enumerate(stored_hashes):

                if self.is_duplicate(
                    image_hash,
                    existing_hash,
                    threshold
                ):

                    is_dup = True

                    duplicate_groups[idx].append(image_path)

                    break

            if not is_dup:

                stored_hashes.append(image_hash)

                unique_photos.append(photo)

        self.print_duplicate_summary(
            photo_database,
            unique_photos
        )

        return unique_photos

    # =====================================================
    # FIND DUPLICATE GROUPS
    # =====================================================

    def find_duplicate_groups(
        self,
        image_paths,
        threshold=5
    ):

        hashes = []

        groups = []

        for image_path in image_paths:

            current_hash = self.get_hash(image_path)

            if current_hash is None:
                continue

            matched = False

            for group in groups:

                representative = group[0]

                rep_hash = representative['hash']

                if self.is_duplicate(
                    current_hash,
                    rep_hash,
                    threshold
                ):

                    group.append({
                        'path': image_path,
                        'hash': current_hash
                    })

                    matched = True
                    break

            if not matched:

                groups.append([
                    {
                        'path': image_path,
                        'hash': current_hash
                    }
                ])

        return groups

    # =====================================================
    # PRINT SUMMARY
    # =====================================================

    @staticmethod
    def print_duplicate_summary(
        original_photos,
        unique_photos
    ):

        original_count = len(original_photos)

        unique_count = len(unique_photos)

        removed = original_count - unique_count

        print("\n" + "=" * 50)
        print("DUPLICATE SUMMARY")
        print("=" * 50)

        print(f"Original photos : {original_count}")
        print(f"Unique photos   : {unique_count}")
        print(f"Duplicates removed : {removed}")

    # =====================================================
    # DEBUG HASHES
    # =====================================================

    def print_hashes(self, image_paths):

        print("\nIMAGE HASHES\n")

        for path in image_paths:

            h = self.get_hash(path)

            if h is not None:
                print(f"{os.path.basename(path)} -> {h}")

    # =====================================================
    # KEEP BEST QUALITY IN DUPLICATE SET
    # =====================================================

    @staticmethod
    def keep_best_quality(
        duplicate_group
    ):

        """
        duplicate_group:
        [
            {
                'path': ...,
                'quality': ...
            }
        ]
        """

        best = None
        best_score = -1

        for photo in duplicate_group:

            score = photo['quality']['final_score']

            if score > best_score:

                best_score = score
                best = photo

        return best


# =========================================================
# TESTING
# =========================================================

if __name__ == "__main__":

    remover = DuplicateRemover()

    image_paths = [
        "img1.jpg",
        "img2.jpg",
        "img3.jpg"
    ]

    remover.print_hashes(image_paths)

    groups = remover.find_duplicate_groups(
        image_paths,
        threshold=5
    )

    print("\nDuplicate Groups:\n")

    for idx, group in enumerate(groups):

        print(f"\nGROUP {idx}")

        for item in group:
            print(item['path'])