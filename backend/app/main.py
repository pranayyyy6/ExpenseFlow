from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.db.database import Base, engine
from app.api.transaction import router as transaction_router
from app.models import (
    Receipt,
    ReceiptItem,
    Transaction,
)
from app.api.analytics import router as analytics_router
from app.api.receipt import router as receipt_router
from app.api.recurring_bill import router as recurring_bill_router
from app.api import budget
from app.api import dashboard
from app.api import receipt_analytics
app = FastAPI(
    title="Smart Receipt Expense Tracker",
    description="AI-powered personal expense tracking system",
    version="1.0.0",
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Register routers
app.include_router(receipt_router)
app.include_router(transaction_router)
app.include_router(analytics_router)
app.include_router(recurring_bill_router)
app.include_router(auth_router)
app.include_router(budget.router)
app.include_router(dashboard.router)
app.include_router(
    receipt_analytics.router
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Smart Receipt Expense Tracker"
    }


@app.get("/health")
def health():
    return {
        "status": "OK"
    }