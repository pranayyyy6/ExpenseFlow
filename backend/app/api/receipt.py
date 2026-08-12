from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem
from app.models.user import User

from app.core.dependencies import get_current_user

from app.schemas.receipt import (
    ReceiptCreate,
    ReceiptUpdate,
    ReceiptResponse,
    ReceiptItemResponse,
)

from app.utils.file_handler import save_uploaded_file

from app.services.ocr_service import ocr_service
from app.services.receipt_parser import receipt_parser
from pathlib import Path


router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"],
)


# ============================================================
# CREATE RECEIPT MANUALLY
# ============================================================

@router.post(
    "/",
    response_model=ReceiptResponse,
)
def create_receipt(
    receipt: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_receipt = Receipt(
        user_id=current_user.id,
        store_name=receipt.store_name,
        receipt_date=receipt.receipt_date,
        total_amount=receipt.total_amount,
        image_path=receipt.image_path,
    )

    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)

    return new_receipt


# ============================================================
# GET ALL RECEIPTS
# ============================================================

@router.get(
    "/",
    response_model=list[ReceiptResponse],
)
def get_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Receipt)
        .filter(
            Receipt.user_id == current_user.id
        )
        .order_by(Receipt.id.desc())
        .all()
    )

# ============================================================
# GET RECEIPT ITEMS
# ============================================================

@router.get(
    "/{receipt_id}/items",
    response_model=list[ReceiptItemResponse],
)
def get_receipt_items(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == current_user.id,
        )
        .first()
    )

    if receipt is None:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )

    return receipt.items
# ============================================================
# GET RECEIPT BY ID
# ============================================================

@router.get(
    "/{receipt_id}",
    response_model=ReceiptResponse,
)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == current_user.id,
        )
        .first()
    )

    if receipt is None:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )

    return receipt


# ============================================================
# UPDATE RECEIPT
# ============================================================

@router.put(
    "/{receipt_id}",
    response_model=ReceiptResponse,
)
def update_receipt(
    receipt_id: int,
    updated: ReceiptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == current_user.id,
        )
        .first()
    )

    if receipt is None:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )

    update_data = updated.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            receipt,
            key,
            value,
        )

    db.commit()
    db.refresh(receipt)

    return receipt


# ============================================================
# DELETE RECEIPT
# ============================================================

@router.delete(
    "/{receipt_id}",
)
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receipt = (
        db.query(Receipt)
        .filter(
            Receipt.id == receipt_id,
            Receipt.user_id == current_user.id,
        )
        .first()
    )

    if receipt is None:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )

    db.delete(receipt)
    db.commit()

    return {
        "message": "Receipt deleted successfully",
        "receipt_id": receipt_id,
    }


# ============================================================
# UPLOAD + OCR + PARSE + VALIDATE + SAVE
# ============================================================

@router.post(
    "/upload",
)
def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = None

    try:

        # ----------------------------------------------------
        # 1. Validate + save image
        # ----------------------------------------------------

        file_path = save_uploaded_file(file)

        # ----------------------------------------------------
        # 2. OCR
        # ----------------------------------------------------

        ocr_result = ocr_service.extract_text(
            file_path
        )

        # ----------------------------------------------------
        # 3. Parse
        # ----------------------------------------------------

        parsed_receipt = receipt_parser.parse(
            ocr_result
        )

        # ----------------------------------------------------
        # 4. Validate
        # ----------------------------------------------------

        validation = parsed_receipt.get(
            "validation",
            {}
        )

        if validation.get("status") != "VALID":
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Receipt validation failed",
                    "validation": validation,
                },
            )

        # ----------------------------------------------------
        # 5. Create receipt
        # ----------------------------------------------------

        new_receipt = Receipt(
            user_id=current_user.id,
            store_name=parsed_receipt.get(
                "store_name",
                "Unknown Store",
            ),
            receipt_date=parsed_receipt.get(
                "receipt_date"
            ),
            total_amount=parsed_receipt.get(
                "total_amount"
            ),
            image_path=file_path,
        )

        db.add(new_receipt)

        db.flush()

        # ----------------------------------------------------
        # 6. Receipt items
        # ----------------------------------------------------

        items = parsed_receipt.get(
            "items",
            []
        )

        for item in items:

            receipt_item = ReceiptItem(
                receipt_id=new_receipt.id,
                item_name=item.get(
                    "item_name",
                    "Unknown Item",
                ),
                quantity=item.get(
                    "quantity",
                    1,
                ),
                price=item.get(
                    "price",
                    0,
                ),
                category=item.get(
                    "category",
                    "Uncategorized",
                ),
            )

            db.add(receipt_item)

        # ----------------------------------------------------
        # 7. Commit everything
        # ----------------------------------------------------

        db.commit()

        db.refresh(new_receipt)

        return {
            "message": "Receipt uploaded and saved successfully",
            "receipt_id": new_receipt.id,
            "file_path": file_path,
            "parsed_receipt": parsed_receipt,
        }

    except HTTPException:

        db.rollback()

        if file_path:
            path = Path(file_path)

            if path.exists():
                path.unlink()

        raise

    except Exception:

        db.rollback()

        if file_path:
            path = Path(file_path)

            if path.exists():
                path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to process receipt",
        )