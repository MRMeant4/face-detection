import uuid
from pathlib import Path
from typing import Sequence, Tuple

import numpy as np
from cv2 import (
    COLOR_BGR2GRAY,
    CascadeClassifier,
    cvtColor,
    data,
    imread,
    imwrite,
    rectangle,
    typing,
)
from django.conf import settings


class FaceDetector:
    def __init__(self):
        """
        Load the pre-trained face detection model
        using the default Haar Cascade classifier for face detection
        Default has higher recall (more true and false positives) while
        alt_tree has higher precision (less true positives, less false positives).
        """
        face_cascade_path = data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = CascadeClassifier(face_cascade_path)
        self.processed_dir = Path(settings.MEDIA_ROOT) / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_image(
        self, image_path: Path = Path(), unique_id: str = str(uuid.uuid4())
    ) -> Tuple[Path, int]:
        """
        Process the uploaded image by detecting faces, drawing boxes and saving the result.

        Args:
            image_path: path to the image file, defaults to an empty path
            unique_id: unique identifier for the processed image, defaults to a random UUID

        Returns:
            Tuple containing the path to the processed image and the number of faces detected
        """
        try:
            img = imread(str(image_path))
            if img is None:
                raise ValueError(f"Failed to load image from {image_path}")

            faces = self.detect_faces(img)

            for x, y, w, h in faces:
                rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            output_filename = f"faces_{unique_id}.jpg"
            output_path = Path("processed") / output_filename
            full_output_path = self.processed_dir / output_filename
            imwrite(str(full_output_path), img)

            return output_path, len(faces)
        except Exception as e:
            raise RuntimeError(f"Failed to process image: {str(e)}") from e

    def detect_faces(self, image_data: typing.MatLike) -> Sequence[typing.Rect]:
        """
        Detect faces in the given image and return coordinates of bounding boxes.

        Args:
            image_data: image data where faces will be detected

        Returns:
            Sequence of rectangles containing the coordinates of the detected faces
        """
        try:
            # Read the image using OpenCV
            gray = cvtColor(image_data, COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            return faces
        except Exception as e:
            raise ValueError(f"Failed to detect faces: {e}") from e
