from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
)

from app.db.dependencies import get_db

from app.models.user import User

from app.repositories.receipt_analytics_repository import (
    ReceiptAnalyticsRepository,
)

from app.services.receipt_analytics_service import (
    ReceiptAnalyticsService,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Receipt Analytics"],
)


# ============================================================
# SERVICE DEPENDENCY
# ============================================================

def get_receipt_analytics_service(
    db: Session = Depends(get_db),
):

    repository = (
        ReceiptAnalyticsRepository(db)
    )

    return ReceiptAnalyticsService(
        repository
    )


# ============================================================
# RECEIPT SPENDING
# ============================================================

@router.get(
    "/receipt-spending",
)
def get_receipt_spending(
    service: ReceiptAnalyticsService = Depends(
        get_receipt_analytics_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return (
        service.get_receipt_spending(
            user_id=current_user.id
        )
    )