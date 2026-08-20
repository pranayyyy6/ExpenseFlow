import io

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image

from app.utils.file_handler import (
    MAX_FILE_SIZE,
    UPLOAD_DIR,
    save_uploaded_file,
)


# ============================================================
# HELPERS
# ============================================================


def make_upload(
    filename,
    content,
):
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
    )


def make_image(
    image_format,
):
    buffer = io.BytesIO()

    image = Image.new(
        "RGB",
        (10, 10),
        "white",
    )

    image.save(
        buffer,
        format=image_format,
    )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# MISSING FILENAME
# ============================================================


def test_missing_filename():

    upload = make_upload(
        None,
        b"test",
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 400

    assert exc.value.detail == (
        "Filename is missing"
    )


# ============================================================
# INVALID EXTENSION
# ============================================================


def test_unsupported_extension():

    upload = make_upload(
        "receipt.txt",
        b"some content",
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 400

    assert (
        "Unsupported image format"
        in exc.value.detail
    )


# ============================================================
# EMPTY FILE
# ============================================================


def test_empty_file():

    upload = make_upload(
        "receipt.jpg",
        b"",
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 400

    assert exc.value.detail == (
        "Uploaded file is empty"
    )


# ============================================================
# FILE TOO LARGE
# ============================================================


def test_file_too_large():

    oversized_data = (
        b"x" * (MAX_FILE_SIZE + 1)
    )

    upload = make_upload(
        "large.jpg",
        oversized_data,
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 413

    assert exc.value.detail == (
        "File too large. Maximum size is 10 MB."
    )


# ============================================================
# INVALID IMAGE CONTENT
# ============================================================


def test_invalid_image_content():

    upload = make_upload(
        "receipt.jpg",
        b"this is not an image",
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 400

    assert exc.value.detail == (
        "Uploaded file is not a valid image"
    )


# ============================================================
# ACTUAL FORMAT DOES NOT MATCH ALLOWED FORMATS
# ============================================================


def test_unsupported_actual_image_format(
    monkeypatch,
):

    class FakeImage:

        format = "GIF"

        def verify(self):
            pass

    monkeypatch.setattr(
        "app.utils.file_handler.Image.open",
        lambda _: FakeImage(),
    )

    upload = make_upload(
        "receipt.jpg",
        b"fake-image-data",
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 400

    assert exc.value.detail == (
        "Unsupported image format"
    )


# ============================================================
# VALID JPEG
# ============================================================


def test_save_valid_jpeg(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.utils.file_handler.UPLOAD_DIR",
        tmp_path,
    )

    image_data = make_image("JPEG")

    upload = make_upload(
        "receipt.jpeg",
        image_data,
    )

    result = save_uploaded_file(upload)

    filepath = tmp_path / result.split("\\")[-1]

    assert filepath.exists()

    assert filepath.suffix == ".jpg"

    assert filepath.read_bytes() == image_data


# ============================================================
# VALID PNG
# ============================================================


def test_save_valid_png(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.utils.file_handler.UPLOAD_DIR",
        tmp_path,
    )

    image_data = make_image("PNG")

    upload = make_upload(
        "receipt.png",
        image_data,
    )

    result = save_uploaded_file(upload)

    filepath = tmp_path / result.split("\\")[-1]

    assert filepath.exists()

    assert filepath.suffix == ".png"

    assert filepath.read_bytes() == image_data


# ============================================================
# VALID WEBP
# ============================================================


def test_save_valid_webp(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.utils.file_handler.UPLOAD_DIR",
        tmp_path,
    )

    image_data = make_image("WEBP")

    upload = make_upload(
        "receipt.webp",
        image_data,
    )

    result = save_uploaded_file(upload)

    filepath = tmp_path / result.split("\\")[-1]

    assert filepath.exists()

    assert filepath.suffix == ".webp"

    assert filepath.read_bytes() == image_data


# ============================================================
# SAVE FAILURE
# ============================================================


def test_save_failure(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.utils.file_handler.UPLOAD_DIR",
        tmp_path,
    )

    image_data = make_image("JPEG")

    upload = make_upload(
        "receipt.jpg",
        image_data,
    )

    def failing_open(
        *args,
        **kwargs,
    ):
        raise OSError("disk failure")

    monkeypatch.setattr(
        "builtins.open",
        failing_open,
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 500

    assert exc.value.detail == (
        "Failed to save uploaded file"
    )


# ============================================================
# SAVE FAILURE + CLEANUP
# ============================================================


def test_save_failure_removes_partial_file(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.utils.file_handler.UPLOAD_DIR",
        tmp_path,
    )

    image_data = make_image("JPEG")

    upload = make_upload(
        "receipt.jpg",
        image_data,
    )

    original_open = open

    def failing_open(
        filepath,
        mode,
        *args,
        **kwargs,
    ):

        if mode == "wb":

            # Create a partial file first.
            partial = original_open(
                filepath,
                "wb",
            )

            partial.write(
                b"partial data"
            )

            partial.close()

            raise OSError(
                "disk failure"
            )

        return original_open(
            filepath,
            mode,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        "builtins.open",
        failing_open,
    )

    with pytest.raises(HTTPException) as exc:

        save_uploaded_file(upload)

    assert exc.value.status_code == 500

    # The handler should remove the
    # partially-created file.
    assert list(tmp_path.iterdir()) == []