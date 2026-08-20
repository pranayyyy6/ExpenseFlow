from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db

from app.models.user import User

from app.repositories.budget_repository import (
    BudgetRepository,
)

from app.services.budget_service import (
    BudgetService,
)

from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
)


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
)


# ============================================================
# SERVICE DEPENDENCY
# ============================================================

def get_budget_service(
    db: Session = Depends(get_db),
):

    repository = BudgetRepository(
        db
    )

    return BudgetService(
        repository
    )


# ============================================================
# CREATE BUDGET
# ============================================================

@router.post(
    "/",
    response_model=BudgetResponse,
)
def create_budget(
    request: BudgetCreate,
    service: BudgetService = Depends(
        get_budget_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.create_budget(
        user_id=current_user.id,
        category=request.category,
        amount=request.amount,
        month=request.month,
    )


# ============================================================
# GET ALL BUDGETS
# ============================================================

@router.get(
    "/",
    response_model=list[BudgetResponse],
)
def get_budgets(
    service: BudgetService = Depends(
        get_budget_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_budgets(
        current_user.id
    )

# ============================================================
# BUDGET OVERVIEW
# ============================================================

@router.get(
    "/overview",
)
def get_budget_overview(
    month: str,
    service: BudgetService = Depends(
        get_budget_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_budget_overview(
        user_id=current_user.id,
        month=month,
    )
# ============================================================
# GET BUDGET BY ID
# ============================================================

@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def get_budget(
    budget_id: int,
    service: BudgetService = Depends(
        get_budget_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_budget(
        budget_id=budget_id,
        user_id=current_user.id,
    )


# ============================================================
# UPDATE BUDGET
# ============================================================

@router.put(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def update_budget(
    budget_id: int,
    request: BudgetUpdate,
    service: BudgetService = Depends(
        get_budget_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    update_data = request.model_dump(
        exclude_unset=True
    )

    return service.update_budget(
        budget_id=budget_id,
        user_id=current_user.id,
        update_data=update_data,
    )


# ============================================================
# DELETE BUDGET
# ============================================================

@router.delete(
    "/{budget_id}",
)
def delete_budget(
    budget_id: int,
    service: BudgetService = Depends(
        get_budget_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.delete_budget(
        budget_id=budget_id,
        user_id=current_user.id,
    )
# ============================================================
# BUDGET STATUS
# ============================================================

@router.get(
    "/{budget_id}/status",
)
def get_budget_status(
    budget_id: int,
    service: BudgetService = Depends(
        get_budget_service
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return service.get_budget_status(
        budget_id=budget_id,
        user_id=current_user.id,
    )
