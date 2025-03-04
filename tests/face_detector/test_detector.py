import os
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch
import shutil

import numpy as np
import pytest
from django.conf import settings
from django.test import TestCase, override_settings

from face_detector.detector import FaceDetector


class FaceDetectorTests(TestCase):
    """Test cases for the FaceDetector class."""

    def setUp(self):
        """Set up the test environment."""
        self.test_media_dir = Path(settings.BASE_DIR) / "test_media"
        self.test_media_dir.mkdir(exist_ok=True)
        self.test_processed_dir = self.test_media_dir / "processed"
        self.test_processed_dir.mkdir(exist_ok=True)

        self.test_images_dir = Path(settings.BASE_DIR) / "test_images"
        self.test_images_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""

        if self.test_media_dir.exists():
            shutil.rmtree(self.test_media_dir)
        if self.test_images_dir.exists():
            shutil.rmtree(self.test_images_dir)

    @patch("face_detector.detector.CascadeClassifier")
    def test_init_loads_cascade_classifier(self, mock_cascade):
        """Test that the constructor loads the Haar Cascade classifier."""
        FaceDetector()

        mock_cascade.assert_called_once()
        call_arg = mock_cascade.call_args[0][0]
        self.assertIn("haarcascade_frontalface_default.xml", call_arg)

    @override_settings(MEDIA_ROOT="test_media")
    def test_init_creates_processed_directory(self):
        """Test that the constructor creates the processed directory."""
        processed_dir = Path("test_media") / "processed"
        if processed_dir.exists():
            shutil.rmtree(processed_dir)

        FaceDetector()

        self.assertTrue(processed_dir.exists())

    @patch("face_detector.detector.imread")
    @patch("face_detector.detector.imwrite")
    def test_process_image_image_load_failure(self, mock_imwrite, mock_imread):
        """Test handling of image loading failures."""
        mock_imread.return_value = None

        detector = FaceDetector()
        test_image_path = Path("nonexistent_image.jpg")

        with self.assertRaises(RuntimeError):
            detector.process_image(test_image_path)

        mock_imwrite.assert_not_called()

    @patch("face_detector.detector.imread")
    @patch("face_detector.detector.imwrite")
    def test_process_image_with_no_faces(self, mock_imwrite, mock_imread):
        """Test processing an image with no faces detected."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image

        detector = FaceDetector()
        detector.detect_faces = MagicMock(return_value=[])

        test_image_path = Path("test_image.jpg")
        test_uuid = "test-uuid"
        output_path, face_count = detector.process_image(test_image_path, test_uuid)

        self.assertEqual(face_count, 0)
        self.assertEqual(output_path, Path("processed") / f"faces_{test_uuid}.jpg")
        mock_imwrite.assert_called_once()

    @patch("face_detector.detector.imread")
    @patch("face_detector.detector.imwrite")
    @patch("face_detector.detector.rectangle")
    def test_process_image_with_faces(self, mock_rectangle, mock_imwrite, mock_imread):
        """Test processing an image with faces detected."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image

        detector = FaceDetector()
        faces = [(10, 20, 30, 40), (50, 60, 70, 80)]
        detector.detect_faces = MagicMock(return_value=faces)

        test_image_path = Path("test_image.jpg")
        test_uuid = "test-uuid"
        output_path, face_count = detector.process_image(test_image_path, test_uuid)

        self.assertEqual(face_count, 2)
        self.assertEqual(output_path, Path("processed") / f"faces_{test_uuid}.jpg")
        self.assertEqual(mock_rectangle.call_count, 2)
        mock_imwrite.assert_called_once()
