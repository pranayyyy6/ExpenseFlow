from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.recurring_bill import RecurringBill
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.recurring_bill import (
    RecurringBillCreate,
    RecurringBillUpdate,
    RecurringBillResponse,
)


router = APIRouter(
    prefix="/recurring-bills",
    tags=["Recurring Bills"],
)


# ============================================================
# CREATE RECURRING BILL
# ============================================================

@router.post(
    "/",
    response_model=RecurringBillResponse,
)
def create_recurring_bill(
    bill: RecurringBillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_bill = RecurringBill(
        # Ownership comes from the authenticated JWT.
        user_id=current_user.id,

        name=bill.name,
        amount=bill.amount,
        frequency=bill.frequency,
        next_due_date=bill.next_due_date,
        category=bill.category,
        payment_method=bill.payment_method,
        auto_pay=bill.auto_pay,
    )

    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)

    return new_bill


# ============================================================
# GET ALL RECURRING BILLS
# ============================================================

@router.get(
    "/",
    response_model=list[RecurringBillResponse],
)
def get_recurring_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(RecurringBill)
        .filter(
            RecurringBill.user_id == current_user.id
        )
        .order_by(RecurringBill.next_due_date)
        .all()
    )


# ============================================================
# UPCOMING BILLS
# ============================================================

@router.get("/upcoming")
def get_upcoming_bills(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    end_date = today + timedelta(days=days)

    # IMPORTANT:
    # Only retrieve bills belonging to the authenticated user.
    bills = (
        db.query(RecurringBill)
        .filter(
            RecurringBill.user_id == current_user.id,
            RecurringBill.is_active == True,
        )
        .all()
    )

    upcoming = []

    for bill in bills:

        try:
            due_date = datetime.strptime(
                bill.next_due_date,
                "%Y-%m-%d",
            ).date()

        except (ValueError, TypeError):
            continue

        if today <= due_date <= end_date:

            days_remaining = (
                due_date - today
            ).days

            upcoming.append(
                {
                    "id": bill.id,
                    "name": bill.name,
                    "amount": bill.amount,
                    "due_date": bill.next_due_date,
                    "days_remaining": days_remaining,
                    "category": bill.category,
                    "auto_pay": bill.auto_pay,
                }
            )

    upcoming.sort(
        key=lambda x: x["days_remaining"]
    )

    total = sum(
        bill["amount"]
        for bill in upcoming
    )

    return {
        "days": days,
        "upcoming_bills": upcoming,
        "total_upcoming": total,
        "count": len(upcoming),
    }


# ============================================================
# GET RECURRING BILL BY ID
# ============================================================

@router.get(
    "/{bill_id}",
    response_model=RecurringBillResponse,
)
def get_recurring_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = (
        db.query(RecurringBill)
        .filter(
            RecurringBill.id == bill_id,
            RecurringBill.user_id == current_user.id,
        )
        .first()
    )

    if bill is None:
        raise HTTPException(
            status_code=404,
            detail="Recurring bill not found",
        )

    return bill


# ============================================================
# UPDATE RECURRING BILL
# ============================================================

@router.put(
    "/{bill_id}",
    response_model=RecurringBillResponse,
)
def update_recurring_bill(
    bill_id: int,
    updated: RecurringBillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = (
        db.query(RecurringBill)
        .filter(
            RecurringBill.id == bill_id,
            RecurringBill.user_id == current_user.id,
        )
        .first()
    )

    if bill is None:
        raise HTTPException(
            status_code=404,
            detail="Recurring bill not found",
        )

    update_data = updated.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(bill, key, value)

    db.commit()
    db.refresh(bill)

    return bill


# ============================================================
# DELETE RECURRING BILL
# ============================================================

@router.delete(
    "/{bill_id}",
)
def delete_recurring_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = (
        db.query(RecurringBill)
        .filter(
            RecurringBill.id == bill_id,
            RecurringBill.user_id == current_user.id,
        )
        .first()
    )

    if bill is None:
        raise HTTPException(
            status_code=404,
            detail="Recurring bill not found",
        )

    db.delete(bill)
    db.commit()

    return {
        "message": "Recurring bill deleted successfully",
        "bill_id": bill_id,
    }