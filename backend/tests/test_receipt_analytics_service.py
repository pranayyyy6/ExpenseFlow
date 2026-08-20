from unittest.mock import Mock

from app.services.receipt_analytics_service import (
    ReceiptAnalyticsService,
)


def create_service():
    repository = Mock()

    service = ReceiptAnalyticsService(
        repository
    )

    return service, repository


def test_get_receipt_spending():

    service, repository = create_service()

    # --------------------------------------------------------
    # Repository results
    # --------------------------------------------------------

    repository.get_total_receipts.return_value = 5

    repository.get_total_items.return_value = 12

    repository.get_total_spending.return_value = 4250.567

    repository.get_average_receipt_value.return_value = 850.113

    repository.get_spending_by_category.return_value = [
        ("Food", 2000),
        ("Shopping", 1500.50),
    ]

    repository.get_top_items.return_value = [
        ("Rice", 1200, 3),
        ("Milk", 600, 4),
    ]

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    result = service.get_receipt_spending(
        user_id=1
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    assert result["total_receipts"] == 5

    assert result["total_items"] == 12

    assert result["total_spending"] == 4250.57

    assert result["average_receipt_value"] == 850.11

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    assert result["categories"] == [
        {
            "category": "Food",
            "total": 2000.0,
        },
        {
            "category": "Shopping",
            "total": 1500.50,
        },
    ]

    # --------------------------------------------------------
    # Top items
    # --------------------------------------------------------

    assert result["top_items"] == [
        {
            "item_name": "Rice",
            "total_spent": 1200.0,
            "purchase_count": 3,
        },
        {
            "item_name": "Milk",
            "total_spent": 600.0,
            "purchase_count": 4,
        },
    ]

    # --------------------------------------------------------
    # Verify repository calls
    # --------------------------------------------------------

    repository.get_total_receipts.assert_called_once_with(1)

    repository.get_total_items.assert_called_once_with(1)

    repository.get_total_spending.assert_called_once_with(1)

    repository.get_average_receipt_value.assert_called_once_with(1)

    repository.get_spending_by_category.assert_called_once_with(1)

    repository.get_top_items.assert_called_once_with(
        user_id=1,
        limit=10,
    )


def test_get_receipt_spending_handles_none_values():

    service, repository = create_service()

    # --------------------------------------------------------
    # Simulate empty database results
    # --------------------------------------------------------

    repository.get_total_receipts.return_value = 0

    repository.get_total_items.return_value = 0

    repository.get_total_spending.return_value = 0

    repository.get_average_receipt_value.return_value = 0

    repository.get_spending_by_category.return_value = [
        (None, None),
    ]

    repository.get_top_items.return_value = [
        (None, None, None),
    ]

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    result = service.get_receipt_spending(
        user_id=1
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    assert result["total_receipts"] == 0

    assert result["total_items"] == 0

    assert result["total_spending"] == 0

    assert result["average_receipt_value"] == 0

    # --------------------------------------------------------
    # None category → Uncategorized
    # --------------------------------------------------------

    assert result["categories"] == [
        {
            "category": "Uncategorized",
            "total": 0.0,
        }
    ]

    # --------------------------------------------------------
    # None item → Unknown Item
    # --------------------------------------------------------

    assert result["top_items"] == [
        {
            "item_name": "Unknown Item",
            "total_spent": 0.0,
            "purchase_count": 0,
        }
    ]

# ============================================================
# API RECEIPT ANALYTICS
# ============================================================

def register_user(client, email):

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Receipt Analytics User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_receipt_spending_api(client):

    token = register_user(
        client,
        "receipt-analytics-api@example.com",
    )

    response = client.get(
        "/analytics/receipt-spending",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_receipts" in data
    assert "total_items" in data
    assert "total_spending" in data
    assert "average_receipt_value" in data
    assert "categories" in data
    assert "top_items" in data