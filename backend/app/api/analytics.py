from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.repositories.analytics_repository import (
    AnalyticsRepository,
)

from app.services.analytics_service import (
    AnalyticsService,
)

from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ============================================================
# ANALYTICS SERVICE DEPENDENCY
# ============================================================

def get_analytics_service(
    db: Session = Depends(get_db),
):
    repository = AnalyticsRepository(db)

    return AnalyticsService(repository)


# ============================================================
# BALANCE
# ============================================================

@router.get("/balance")
def get_balance(
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
    current_user: User = Depends(get_current_user),
):
    return service.get_balance(
        current_user.id
    )


# ============================================================
# EXPENSE BY CATEGORY
# ============================================================

@router.get("/by-category")
def get_expense_by_category(
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
    current_user: User = Depends(get_current_user),
):
    return service.get_expense_by_category(
        current_user.id
    )


# ============================================================
# EXPENSE BY PAYMENT METHOD
# ============================================================

@router.get("/by-payment-method")
def get_expense_by_payment_method(
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
    current_user: User = Depends(get_current_user),
):
    return service.get_expense_by_payment_method(
        current_user.id
    )


# ============================================================
# PROJECTED CASH FLOW
# ============================================================

@router.get("/projected-cash-flow")
def get_projected_cash_flow(
    days: int = 30,
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
    current_user: User = Depends(get_current_user),
):
    return service.get_projected_cash_flow(
        days,
        current_user.id,
    )
# ============================================================
# MONTHLY ANALYTICS
# ============================================================

@router.get("/monthly")
def get_monthly_analytics(
    month: str,
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_monthly_analytics(
        user_id=current_user.id,
        month=month,
    )
@router.get("/trends")
def get_spending_trends(
    months: int = 6,
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_spending_trends(
        user_id=current_user.id,
        months=months,
    )
# ============================================================
# FINANCIAL SUMMARY
# ============================================================

@router.get("/summary")
def get_financial_summary(
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_financial_summary(
        user_id=current_user.id,
    )