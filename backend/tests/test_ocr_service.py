from unittest.mock import Mock

import numpy as np
from PIL import Image

from app.services.ocr_service import OCRService


def create_service():
    """
    Create OCRService without loading the real EasyOCR model.
    """

    service = OCRService.__new__(
        OCRService
    )

    service.reader = Mock()

    return service


def test_preprocess_image(tmp_path):

    image_path = (
        tmp_path / "receipt.png"
    )

    image = Image.new(
        "RGB",
        (100, 50),
        "white",
    )

    image.save(image_path)

    service = create_service()

    processed = service.preprocess_image(
        str(image_path)
    )

    # RGB -> grayscale
    assert processed.mode == "L"

    # Original: 100 x 50
    # Upscaled: 200 x 100
    assert processed.size == (
        200,
        100,
    )


def test_extract_text_filters_low_confidence(
    tmp_path,
):

    image_path = (
        tmp_path / "receipt.png"
    )

    image = Image.new(
        "RGB",
        (100, 50),
        "white",
    )

    image.save(image_path)

    service = create_service()

    service.reader.readtext.return_value = [

        (
            [[0, 0], [10, 0], [10, 10], [0, 10]],
            "High confidence",
            0.95,
        ),

        (
            [[0, 0], [10, 0], [10, 10], [0, 10]],
            "Low confidence",
            0.10,
        ),

        (
            [[0, 0], [10, 0], [10, 10], [0, 10]],
            "Boundary confidence",
            0.25,
        ),
    ]

    result = service.extract_text(
        str(image_path)
    )

    assert result == [
        {
            "text": "High confidence",
            "confidence": 0.95,
        },
        {
            "text": "Boundary confidence",
            "confidence": 0.25,
        },
    ]

    service.reader.readtext.assert_called_once()

    args, kwargs = (
        service.reader.readtext.call_args
    )

    assert isinstance(
        args[0],
        np.ndarray,
    )

    assert kwargs["detail"] == 1

    assert kwargs["paragraph"] is False


def test_extract_text_empty_result(
    tmp_path,
):

    image_path = (
        tmp_path / "receipt.png"
    )

    image = Image.new(
        "RGB",
        (50, 50),
        "white",
    )

    image.save(image_path)

    service = create_service()

    service.reader.readtext.return_value = []

    result = service.extract_text(
        str(image_path)
    )

    assert result == []

    service.reader.readtext.assert_called_once()