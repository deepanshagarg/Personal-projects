# exporter.py

import os
import shutil
import json
import pandas as pd
from collections import defaultdict


class Exporter:

    def __init__(self):

        pass

    # =====================================================
    # CREATE OUTPUT STRUCTURE
    # =====================================================

    @staticmethod
    def create_output_folders(output_dir):

        folders = [
            "selected_photos",
            "person_clusters",
            "reports",
            "debug"
        ]

        for folder in folders:

            os.makedirs(
                os.path.join(output_dir, folder),
                exist_ok=True
            )

    # =====================================================
    # EXPORT FINAL SELECTED PHOTOS
    # =====================================================

    def export_selected(
        self,
        selected_photos,
        output_dir
    ):

        selected_dir = os.path.join(
            output_dir,
            "selected_photos"
        )

        os.makedirs(selected_dir, exist_ok=True)

        for idx, photo in enumerate(selected_photos):

            source = photo['path']

            filename = os.path.basename(source)

            destination = os.path.join(
                selected_dir,
                filename
            )

            try:

                shutil.copy2(source, destination)

            except Exception as e:

                print(f"Error copying {source}")
                print(str(e))

        print(f"\nExported {len(selected_photos)} selected photos")

    # =====================================================
    # EXPORT PERSON CLUSTER FOLDERS
    # =====================================================

    def export_person_folders(
        self,
        photo_database,
        output_dir
    ):

        base_dir = os.path.join(
            output_dir,
            "person_clusters"
        )

        os.makedirs(base_dir, exist_ok=True)

        person_map = defaultdict(list)

        for photo in photo_database:

            for person_id in photo['people_ids']:

                person_map[person_id].append(photo)

        for person_id, photos in person_map.items():

            person_dir = os.path.join(
                base_dir,
                f"person_{person_id}"
            )

            os.makedirs(person_dir, exist_ok=True)

            copied = set()

            for photo in photos:

                src = photo['path']

                filename = os.path.basename(src)

                if filename in copied:
                    continue

                copied.add(filename)

                dst = os.path.join(
                    person_dir,
                    filename
                )

                try:

                    shutil.copy2(src, dst)

                except Exception as e:

                    print(f"Error copying {src}")
                    print(str(e))

        print(
            f"\nExported {len(person_map)} person folders"
        )

    # =====================================================
    # EXPORT EXCEL REPORT
    # =====================================================

    def export_excel(
        self,
        photo_database,
        output_dir
    ):

        rows = []

        for photo in photo_database:

            rows.append({

                'photo_path':
                    photo['path'],

                'filename':
                    os.path.basename(photo['path']),

                'people_count':
                    len(photo['people_ids']),

                'people_ids':
                    ", ".join(
                        map(str, photo['people_ids'])
                    ),

                'quality_score':
                    photo['quality']['final_score'],

                'sharpness':
                    photo['quality']['sharpness'],

                'brightness':
                    photo['quality']['brightness'],

                'contrast':
                    photo['quality']['contrast']
            })

        df = pd.DataFrame(rows)

        reports_dir = os.path.join(
            output_dir,
            "reports"
        )

        os.makedirs(reports_dir, exist_ok=True)

        excel_path = os.path.join(
            reports_dir,
            "photo_report.xlsx"
        )

        df.to_excel(
            excel_path,
            index=False
        )

        print(f"\nExcel report saved:")
        print(excel_path)

    # =====================================================
    # EXPORT PERSON SUMMARY EXCEL
    # =====================================================

    def export_person_summary(
        self,
        photo_database,
        output_dir
    ):

        person_map = defaultdict(set)

        for photo in photo_database:

            filename = os.path.basename(
                photo['path']
            )

            for pid in photo['people_ids']:

                person_map[pid].add(filename)

        rows = []

        for pid, photos in person_map.items():

            rows.append({

                'person_id': pid,

                'photo_count': len(photos),

                'photos':
                    ", ".join(sorted(photos))
            })

        df = pd.DataFrame(rows)

        reports_dir = os.path.join(
            output_dir,
            "reports"
        )

        os.makedirs(reports_dir, exist_ok=True)

        excel_path = os.path.join(
            reports_dir,
            "person_summary.xlsx"
        )

        df.to_excel(
            excel_path,
            index=False
        )

        print(f"\nPerson summary saved:")
        print(excel_path)

    # =====================================================
    # EXPORT JSON DATABASE
    # =====================================================

    def export_json(
        self,
        photo_database,
        output_dir
    ):

        exportable = []

        for photo in photo_database:

            exportable.append({

                'path':
                    photo['path'],

                'people_ids':
                    photo['people_ids'],

                'quality':
                    photo['quality']
            })

        reports_dir = os.path.join(
            output_dir,
            "reports"
        )

        os.makedirs(reports_dir, exist_ok=True)

        json_path = os.path.join(
            reports_dir,
            "photo_database.json"
        )

        with open(json_path, 'w') as f:

            json.dump(
                exportable,
                f,
                indent=4
            )

        print(f"\nJSON database saved:")
        print(json_path)

    # =====================================================
    # EXPORT DEBUG INFORMATION
    # =====================================================

    def export_debug_stats(
        self,
        photo_database,
        selected_photos,
        output_dir
    ):

        stats = {

            'total_photos':
                len(photo_database),

            'selected_photos':
                len(selected_photos),

            'compression_ratio':
                (
                    len(selected_photos) /
                    len(photo_database)
                )
                if len(photo_database) > 0 else 0,

            'unique_people':
                len(set(
                    pid
                    for photo in photo_database
                    for pid in photo['people_ids']
                ))
        }

        debug_dir = os.path.join(
            output_dir,
            "debug"
        )

        os.makedirs(debug_dir, exist_ok=True)

        stats_path = os.path.join(
            debug_dir,
            "stats.json"
        )

        with open(stats_path, 'w') as f:

            json.dump(
                stats,
                f,
                indent=4
            )

        print(f"\nDebug stats saved:")
        print(stats_path)


# =========================================================
# TESTING
# =========================================================

if __name__ == "__main__":

    exporter = Exporter()

    exporter.create_output_folders("output")

    print("Exporter initialized")