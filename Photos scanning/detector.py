# detector.py

from insightface.app import FaceAnalysis
import cv2
import numpy as np


class FaceDetector:

    def __init__(
        self,
        model_name='buffalo_l',
        gpu=True,
        det_size=(640, 640)
    ):

        ctx_id = 0 if gpu else -1

        self.app = FaceAnalysis(name=model_name)

        self.app.prepare(
            ctx_id=ctx_id,
            det_size=det_size
        )

    def detect(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            return None

        faces = self.app.get(image)

        results = []

        for idx, face in enumerate(faces):

            bbox = face.bbox.astype(int)

            x1, y1, x2, y2 = bbox

            face_crop = image[y1:y2, x1:x2]

            results.append({
                'face_index': idx,
                'bbox': bbox.tolist(),
                'embedding': face.embedding,
                'det_score': float(face.det_score),
                'landmarks': face.kps.tolist(),
                'face_crop': face_crop
            })

        return {
            'image': image,
            'faces': results,
            'face_count': len(results)
        }


if __name__ == "__main__":

    detector = FaceDetector(
        model_name='buffalo_l',
        gpu=True
    )

    result = detector.detect("test.jpg")

    if result is None:
        print("Could not load image")

    else:
        print(f"Faces found: {result['face_count']}")

        for face in result['faces']:
            print(face['bbox'])
            print(face['det_score'])