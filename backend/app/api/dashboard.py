from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
)

from app.db.dependencies import get_db

from app.models.user import User

from app.repositories.dashboard_repository import (
    DashboardRepository,
)

from app.repositories.analytics_repository import (
    AnalyticsRepository,
)

from app.repositories.budget_repository import (
    BudgetRepository,
)

from app.repositories.receipt_analytics_repository import (
    ReceiptAnalyticsRepository,
)

from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# SERVICE DEPENDENCY
# ============================================================

def get_dashboard_service(
    db: Session = Depends(get_db),
):

    dashboard_repository = (
        DashboardRepository(db)
    )

    analytics_repository = (
        AnalyticsRepository(db)
    )

    budget_repository = (
        BudgetRepository(db)
    )

    receipt_analytics_repository = (
        ReceiptAnalyticsRepository(db)
    )

    return DashboardService(
        repository=dashboard_repository,
        analytics_repository=analytics_repository,
        budget_repository=budget_repository,
        receipt_analytics_repository=(
            receipt_analytics_repository
        ),
    )


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/")
def get_dashboard(
    service: DashboardService = Depends(
        get_dashboard_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_dashboard(
        user_id=current_user.id
    )