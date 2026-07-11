# optimizer.py

import numpy as np


class CoverageOptimizer:

    def __init__(
        self,
        quality_weight=1.0,
        coverage_weight=2.0,
        diversity_weight=0.5
    ):

        self.quality_weight = quality_weight
        self.coverage_weight = coverage_weight
        self.diversity_weight = diversity_weight

    # =====================================================
    # GET ALL UNIQUE PEOPLE
    # =====================================================

    @staticmethod
    def get_all_people(photo_database):

        people = set()

        for photo in photo_database:

            for pid in photo['people_ids']:
                people.add(pid)

        return people

    # =====================================================
    # COMPUTE PHOTO UTILITY
    # =====================================================

    def compute_utility(
        self,
        photo,
        uncovered_people,
        selected_people_frequency
    ):

        photo_people = set(photo['people_ids'])

        newly_covered = (
            photo_people.intersection(uncovered_people)
        )

        # ---------------------------------------------
        # COVERAGE SCORE
        # ---------------------------------------------

        coverage_score = len(newly_covered)

        # ---------------------------------------------
        # QUALITY SCORE
        # ---------------------------------------------

        quality_score = (
            photo['quality']['final_score']
        )

        # ---------------------------------------------
        # DIVERSITY SCORE
        # Penalize over-represented people
        # ---------------------------------------------

        diversity_bonus = 0

        for pid in photo_people:

            frequency = selected_people_frequency.get(pid, 0)

            diversity_bonus += 1 / (1 + frequency)

        # ---------------------------------------------
        # FINAL SCORE
        # ---------------------------------------------

        utility = (

            self.coverage_weight *
            coverage_score

            +

            self.quality_weight *
            quality_score

            +

            self.diversity_weight *
            diversity_bonus
        )

        return utility

    # =====================================================
    # MAIN OPTIMIZATION
    # =====================================================

    def select_best_photos(
        self,
        photo_database
    ):

        if len(photo_database) == 0:
            return []

        all_people = self.get_all_people(
            photo_database
        )

        uncovered_people = set(all_people)

        selected_photos = []

        used_photo_paths = set()

        selected_people_frequency = {}

        iteration = 0

        print("\n" + "=" * 50)
        print("STARTING COVERAGE OPTIMIZATION")
        print("=" * 50)

        print(f"Unique people: {len(all_people)}")

        while uncovered_people:

            best_photo = None
            best_utility = -1

            iteration += 1

            for photo in photo_database:

                photo_path = photo['path']

                if photo_path in used_photo_paths:
                    continue

                if len(photo['people_ids']) == 0:
                    continue

                utility = self.compute_utility(
                    photo,
                    uncovered_people,
                    selected_people_frequency
                )

                if utility > best_utility:

                    best_utility = utility
                    best_photo = photo

            if best_photo is None:
                break

            selected_photos.append(best_photo)

            used_photo_paths.add(
                best_photo['path']
            )

            # -----------------------------------------
            # UPDATE COVERAGE
            # -----------------------------------------

            for pid in best_photo['people_ids']:

                if pid in uncovered_people:
                    uncovered_people.remove(pid)

                selected_people_frequency[pid] = (
                    selected_people_frequency.get(pid, 0) + 1
                )

            print(
                f"Iteration {iteration} | "
                f"Selected: {best_photo['path']} | "
                f"Remaining people: {len(uncovered_people)}"
            )

        print("\nOptimization complete")

        return selected_photos

    # =====================================================
    # OPTIONAL SECOND PASS
    # Improve overall quality
    # =====================================================

    def improve_quality_pass(
        self,
        selected_photos,
        photo_database,
        max_extra_photos=20
    ):

        selected_paths = set(
            photo['path']
            for photo in selected_photos
        )

        remaining = []

        for photo in photo_database:

            if photo['path'] not in selected_paths:
                remaining.append(photo)

        remaining = sorted(
            remaining,
            key=lambda x: x['quality']['final_score'],
            reverse=True
        )

        extra = remaining[:max_extra_photos]

        final_output = (
            selected_photos + extra
        )

        return final_output

    # =====================================================
    # PRINT SELECTION SUMMARY
    # =====================================================

    @staticmethod
    def print_summary(
        original_count,
        selected_photos
    ):

        selected_count = len(selected_photos)

        reduction_ratio = (
            selected_count / original_count
        ) if original_count > 0 else 0

        print("\n" + "=" * 50)
        print("OPTIMIZATION SUMMARY")
        print("=" * 50)

        print(f"Original photos : {original_count}")
        print(f"Selected photos : {selected_count}")

        print(
            f"Compression ratio : "
            f"{reduction_ratio:.2f}"
        )

    # =====================================================
    # ANALYZE PERSON COVERAGE
    # =====================================================

    @staticmethod
    def analyze_coverage(
        selected_photos
    ):

        person_count = {}

        for photo in selected_photos:

            for pid in photo['people_ids']:

                person_count[pid] = (
                    person_count.get(pid, 0) + 1
                )

        print("\n" + "=" * 50)
        print("PERSON COVERAGE")
        print("=" * 50)

        for pid, count in sorted(person_count.items()):

            print(
                f"Person {pid}: "
                f"{count} selected photos"
            )

        return person_count

    # =====================================================
    # IMPORTANT PEOPLE BOOST
    # =====================================================

    def apply_importance_weights(
        self,
        photo_database,
        important_people
    ):

        """
        important_people:

        {
            person_id: weight
        }

        Example:

        {
            0: 5,  # bride
            1: 5,  # groom
            2: 3   # parent
        }
        """

        for photo in photo_database:

            boost = 0

            for pid in photo['people_ids']:

                boost += important_people.get(pid, 0)

            photo['quality']['final_score'] += (
                boost * 0.1
            )

        return photo_database


# =========================================================
# TESTING
# =========================================================

if __name__ == "__main__":

    optimizer = CoverageOptimizer()

    dummy_database = [

        {
            'path': 'img1.jpg',
            'people_ids': [1, 2],
            'quality': {
                'final_score': 0.9
            }
        },

        {
            'path': 'img2.jpg',
            'people_ids': [2, 3],
            'quality': {
                'final_score': 0.7
            }
        },

        {
            'path': 'img3.jpg',
            'people_ids': [4],
            'quality': {
                'final_score': 0.95
            }
        }
    ]

    selected = optimizer.select_best_photos(
        dummy_database
    )

    optimizer.print_summary(
        len(dummy_database),
        selected
    )

    optimizer.analyze_coverage(selected)