import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# SAVE + VALIDATE UPLOAD
# ============================================================

def save_uploaded_file(
    file: UploadFile,
) -> str:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Allowed formats: JPG, JPEG, PNG, WEBP"
            ),
        )

    # --------------------------------------------------------
    # Read upload in chunks
    # --------------------------------------------------------

    chunks = []
    total_size = 0

    while True:

        chunk = file.file.read(
            1024 * 1024
        )

        if not chunk:
            break

        total_size += len(chunk)

        if total_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 10 MB.",
            )

        chunks.append(chunk)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    file_data = b"".join(chunks)

    # --------------------------------------------------------
    # Validate actual image content
    # --------------------------------------------------------

    try:

        from io import BytesIO

        image = Image.open(
            BytesIO(file_data)
        )

        image.verify()

        actual_format = image.format

    except (
        UnidentifiedImageError,
        OSError,
    ):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image",
        )

    if actual_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format",
        )

    # --------------------------------------------------------
    # Generate server-side filename
    # --------------------------------------------------------

    safe_extension = ALLOWED_FORMATS[
        actual_format
    ]

    filename = (
        f"{uuid.uuid4().hex}"
        f"{safe_extension}"
    )

    filepath = UPLOAD_DIR / filename

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    try:

        with open(
            filepath,
            "wb",
        ) as buffer:

            buffer.write(file_data)

    except OSError:

        if filepath.exists():
            filepath.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file",
        )

    return str(filepath)