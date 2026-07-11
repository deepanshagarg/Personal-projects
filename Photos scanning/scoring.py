# scoring.py

import cv2
import numpy as np


class PhotoScorer:

    # =====================================================
    # SHARPNESS SCORE
    # =====================================================

    @staticmethod
    def sharpness_score(image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        score = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        return float(score)

    # =====================================================
    # BRIGHTNESS SCORE
    # =====================================================

    @staticmethod
    def brightness_score(image):

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        brightness = hsv[:, :, 2].mean()

        return float(brightness)

    # =====================================================
    # CONTRAST SCORE
    # =====================================================

    @staticmethod
    def contrast_score(image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        contrast = gray.std()

        return float(contrast)

    # =====================================================
    # FACE SIZE SCORE
    # =====================================================

    @staticmethod
    def face_size_score(face_boxes, image_shape):

        if len(face_boxes) == 0:
            return 0.0

        h, w = image_shape[:2]

        total_image_area = h * w

        total_face_area = 0

        for box in face_boxes:

            x1, y1, x2, y2 = box

            face_area = max(0, (x2 - x1)) * max(0, (y2 - y1))

            total_face_area += face_area

        normalized_score = total_face_area / total_image_area

        return float(normalized_score)

    # =====================================================
    # CENTERING SCORE
    # =====================================================

    @staticmethod
    def centering_score(face_boxes, image_shape):

        if len(face_boxes) == 0:
            return 0.0

        h, w = image_shape[:2]

        image_center_x = w / 2
        image_center_y = h / 2

        scores = []

        for box in face_boxes:

            x1, y1, x2, y2 = box

            face_center_x = (x1 + x2) / 2
            face_center_y = (y1 + y2) / 2

            distance = np.sqrt(
                (face_center_x - image_center_x) ** 2 +
                (face_center_y - image_center_y) ** 2
            )

            max_distance = np.sqrt(
                image_center_x ** 2 +
                image_center_y ** 2
            )

            normalized = 1 - (distance / max_distance)

            scores.append(normalized)

        return float(np.mean(scores))

    # =====================================================
    # EYE OPENNESS ESTIMATION
    # =====================================================

    @staticmethod
    def eye_openness_score(landmarks):

        """
        Approximation using eye landmark geometry.

        InsightFace gives 5-point landmarks:
        [left_eye, right_eye, nose, left_mouth, right_mouth]
        """

        if landmarks is None:
            return 0.5

        try:

            left_eye = landmarks[0]
            right_eye = landmarks[1]

            eye_distance = np.linalg.norm(
                np.array(left_eye) - np.array(right_eye)
            )

            return min(1.0, eye_distance / 100)

        except:
            return 0.5

    # =====================================================
    # FACE VISIBILITY SCORE
    # =====================================================

    @staticmethod
    def visibility_score(face_boxes, image_shape):

        if len(face_boxes) == 0:
            return 0.0

        h, w = image_shape[:2]

        score = 0

        for box in face_boxes:

            x1, y1, x2, y2 = box

            margin = 20

            visible = (
                x1 > margin and
                y1 > margin and
                x2 < (w - margin) and
                y2 < (h - margin)
            )

            if visible:
                score += 1

        return score / len(face_boxes)

    # =====================================================
    # MAIN QUALITY SCORE
    # =====================================================

    def overall_score(
        self,
        image,
        face_boxes,
        landmarks_list=None
    ):

        if landmarks_list is None:
            landmarks_list = []

        sharpness = self.sharpness_score(image)

        brightness = self.brightness_score(image)

        contrast = self.contrast_score(image)

        face_size = self.face_size_score(
            face_boxes,
            image.shape
        )

        centering = self.centering_score(
            face_boxes,
            image.shape
        )

        visibility = self.visibility_score(
            face_boxes,
            image.shape
        )

        eye_scores = []

        for lm in landmarks_list:
            eye_scores.append(
                self.eye_openness_score(lm)
            )

        if len(eye_scores) > 0:
            eye_score = np.mean(eye_scores)
        else:
            eye_score = 0.5

        # =================================================
        # NORMALIZATION
        # =================================================

        sharpness_norm = min(sharpness / 1000, 1.0)

        brightness_norm = min(brightness / 255, 1.0)

        contrast_norm = min(contrast / 100, 1.0)

        face_size_norm = min(face_size * 20, 1.0)

        # =================================================
        # FINAL WEIGHTED SCORE
        # =================================================

        final_score = (
            0.30 * sharpness_norm +
            0.10 * brightness_norm +
            0.10 * contrast_norm +
            0.20 * face_size_norm +
            0.10 * centering +
            0.10 * visibility +
            0.10 * eye_score
        )

        return {
            'sharpness': sharpness,
            'brightness': brightness,
            'contrast': contrast,
            'face_size': face_size,
            'centering': centering,
            'visibility': visibility,
            'eye_score': eye_score,
            'final_score': float(final_score)
        }


# =========================================================
# TESTING
# =========================================================

if __name__ == "__main__":

    image = cv2.imread("test.jpg")

    scorer = PhotoScorer()

    dummy_boxes = [
        [100, 100, 300, 300]
    ]

    result = scorer.overall_score(
        image=image,
        face_boxes=dummy_boxes
    )

    print(result)