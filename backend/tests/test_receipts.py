def register_user(client, email):

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword123!",
            "full_name": "Receipt User",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_receipt(client, token):

    response = client.post(
        "/receipts/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "store_name": "DMart",
            "receipt_date": "2026-08-12",
            "total_amount": 1250,
            "image_path": None,
        },
    )

    return response


# ============================================================
# CREATE
# ============================================================

def test_create_receipt(client):

    token = register_user(
        client,
        "receipt-create@example.com",
    )

    response = create_receipt(
        client,
        token,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["store_name"] == "DMart"
    assert data["total_amount"] == 1250
    assert data["receipt_date"] == "2026-08-12"


# ============================================================
# GET ALL
# ============================================================

def test_get_receipts(client):

    token = register_user(
        client,
        "receipt-list@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    response = client.get(
        "/receipts/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["store_name"] == "DMart"


# ============================================================
# AUTHENTICATION
# ============================================================

def test_receipts_require_authentication(client):

    response = client.get(
        "/receipts/"
    )

    assert response.status_code in (
        401,
        403,
    )


# ============================================================
# GET BY ID
# ============================================================

def test_get_receipt_by_id(client):

    token = register_user(
        client,
        "receipt-id@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    receipt_id = (
        create_response.json()["id"]
    )

    response = client.get(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == receipt_id
    assert data["store_name"] == "DMart"

    # Receipt response should expose items.
    assert "items" in data
    assert isinstance(
        data["items"],
        list,
    )


# ============================================================
# USER ISOLATION
# ============================================================

def test_user_cannot_access_another_users_receipt(
    client,
):

    # --------------------------------------------------------
    # USER A
    # --------------------------------------------------------

    user_a_token = register_user(
        client,
        "receipt-user-a@example.com",
    )

    create_response = create_receipt(
        client,
        user_a_token,
    )

    assert create_response.status_code == 200

    receipt_id = (
        create_response.json()["id"]
    )

    # --------------------------------------------------------
    # USER B
    # --------------------------------------------------------

    user_b_token = register_user(
        client,
        "receipt-user-b@example.com",
    )

    response = client.get(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": (
                f"Bearer {user_b_token}"
            ),
        },
    )

    # User B must not be able to see
    # User A's receipt.

    assert response.status_code == 404


# ============================================================
# DELETE
# ============================================================

def test_delete_receipt(client):

    token = register_user(
        client,
        "receipt-delete@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    receipt_id = (
        create_response.json()["id"]
    )

    response = client.delete(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    # Verify it no longer exists.

    get_response = client.get(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert get_response.status_code == 404

# ============================================================
# GET RECEIPT ITEMS
# ============================================================

def test_get_receipt_items(client):

    token = register_user(
        client,
        "receipt-items@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    receipt_id = create_response.json()["id"]

    response = client.get(
        f"/receipts/{receipt_id}/items",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0

# ============================================================
# GET NONEXISTENT RECEIPT
# ============================================================

def test_get_nonexistent_receipt(client):

    token = register_user(
        client,
        "receipt-not-found@example.com",
    )

    response = client.get(
        "/receipts/999999",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404

# ============================================================
# GET ITEMS - NOT FOUND
# ============================================================

def test_get_items_for_nonexistent_receipt(client):

    token = register_user(
        client,
        "receipt-items-not-found@example.com",
    )

    response = client.get(
        "/receipts/999999/items",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404

# ============================================================
# UPDATE
# ============================================================

def test_update_receipt(client):

    token = register_user(
        client,
        "receipt-update@example.com",
    )

    create_response = create_receipt(
        client,
        token,
    )

    assert create_response.status_code == 200

    receipt_id = create_response.json()["id"]

    response = client.put(
        f"/receipts/{receipt_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "store_name": "Reliance Fresh",
            "total_amount": 1500,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == receipt_id
    assert data["store_name"] == "Reliance Fresh"
    assert data["total_amount"] == 1500


# ============================================================
# UPDATE - NOT FOUND
# ============================================================

def test_update_nonexistent_receipt(client):

    token = register_user(
        client,
        "receipt-update-not-found@example.com",
    )

    response = client.put(
        "/receipts/999999",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "store_name": "Test Store",
        },
    )

    assert response.status_code == 404

# ============================================================
# DELETE - NOT FOUND
# ============================================================

def test_delete_nonexistent_receipt(client):

    token = register_user(
        client,
        "receipt-delete-not-found@example.com",
    )

    response = client.delete(
        "/receipts/999999",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404

# ============================================================
# ITEMS USER ISOLATION
# ============================================================

def test_user_cannot_access_another_users_receipt_items(
    client,
):

    user_a_token = register_user(
        client,
        "receipt-items-user-a@example.com",
    )

    create_response = create_receipt(
        client,
        user_a_token,
    )

    assert create_response.status_code == 200

    receipt_id = create_response.json()["id"]

    user_b_token = register_user(
        client,
        "receipt-items-user-b@example.com",
    )

    response = client.get(
        f"/receipts/{receipt_id}/items",
        headers={
            "Authorization": f"Bearer {user_b_token}",
        },
    )

    assert response.status_code == 404

# ============================================================
# UPLOAD RECEIPT - SUCCESS
# ============================================================

def test_upload_receipt_success(
    client,
    monkeypatch,
):

    token = register_user(
        client,
        "receipt-upload-success@example.com",
    )

    # Mock file saving
    monkeypatch.setattr(
        "app.api.receipt.save_uploaded_file",
        lambda file: "uploads/test-receipt.jpg",
    )

    # Mock OCR
    monkeypatch.setattr(
        "app.api.receipt.ocr_service.extract_text",
        lambda file_path: [
            {
                "text": "DMart",
                "confidence": 0.99,
            }
        ],
    )

    # Mock parser
    monkeypatch.setattr(
        "app.api.receipt.receipt_parser.parse",
        lambda ocr_result: {
            "store_name": "DMart",
            "receipt_date": "2026-08-12",
            "total_amount": 1250,
            "items": [
                {
                    "item_name": "Rice",
                    "quantity": 2,
                    "price": 500,
                    "category": "Groceries",
                },
                {
                    "item_name": "Milk",
                    "quantity": 1,
                    "price": 250,
                    "category": "Dairy",
                },
            ],
            "validation": {
                "status": "VALID",
            },
        },
    )

    response = client.post(
        "/receipts/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "receipt.jpg",
                b"fake image data",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["message"]
        == "Receipt uploaded and saved successfully"
    )

    assert data["receipt_id"] is not None

    assert (
        data["file_path"]
        == "uploads/test-receipt.jpg"
    )

    assert (
        data["parsed_receipt"]["store_name"]
        == "DMart"
    )

    assert (
        data["parsed_receipt"]["total_amount"]
        == 1250
    )

    assert len(
        data["parsed_receipt"]["items"]
    ) == 2

# ============================================================
# UPLOAD RECEIPT - SUCCESS
# ============================================================

def test_upload_receipt_success(
    client,
    monkeypatch,
):

    token = register_user(
        client,
        "receipt-upload-success@example.com",
    )

    # Mock file saving
    monkeypatch.setattr(
        "app.api.receipt.save_uploaded_file",
        lambda file: "uploads/test-receipt.jpg",
    )

    # Mock OCR
    monkeypatch.setattr(
        "app.api.receipt.ocr_service.extract_text",
        lambda file_path: [
            {
                "text": "DMart",
                "confidence": 0.99,
            }
        ],
    )

    # Mock parser
    monkeypatch.setattr(
        "app.api.receipt.receipt_parser.parse",
        lambda ocr_result: {
            "store_name": "DMart",
            "receipt_date": "2026-08-12",
            "total_amount": 1250,
            "items": [
                {
                    "item_name": "Rice",
                    "quantity": 2,
                    "price": 500,
                    "category": "Groceries",
                },
                {
                    "item_name": "Milk",
                    "quantity": 1,
                    "price": 250,
                    "category": "Dairy",
                },
            ],
            "validation": {
                "status": "VALID",
            },
        },
    )

    response = client.post(
        "/receipts/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "receipt.jpg",
                b"fake image data",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["message"]
        == "Receipt uploaded and saved successfully"
    )

    assert data["receipt_id"] is not None

    assert (
        data["file_path"]
        == "uploads/test-receipt.jpg"
    )

    assert (
        data["parsed_receipt"]["store_name"]
        == "DMart"
    )

    assert (
        data["parsed_receipt"]["total_amount"]
        == 1250
    )

    assert len(
        data["parsed_receipt"]["items"]
    ) == 2

# ============================================================
# UPLOAD - NO ITEMS
# ============================================================

def test_upload_receipt_without_items(
    client,
    monkeypatch,
):

    token = register_user(
        client,
        "receipt-upload-no-items@example.com",
    )

    monkeypatch.setattr(
        "app.api.receipt.save_uploaded_file",
        lambda file: "uploads/no-items.jpg",
    )

    monkeypatch.setattr(
        "app.api.receipt.ocr_service.extract_text",
        lambda file_path: [],
    )

    monkeypatch.setattr(
        "app.api.receipt.receipt_parser.parse",
        lambda ocr_result: {
            "store_name": "Unknown Store",
            "receipt_date": "2026-08-12",
            "total_amount": 500,
            "validation": {
                "status": "VALID",
            },
        },
    )

    response = client.post(
        "/receipts/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "receipt.jpg",
                b"fake image data",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["receipt_id"] is not None

    assert (
        data["parsed_receipt"]["store_name"]
        == "Unknown Store"
    )

# ============================================================
# UPLOAD - NO ITEMS
# ============================================================

def test_upload_receipt_without_items(
    client,
    monkeypatch,
):

    token = register_user(
        client,
        "receipt-upload-no-items@example.com",
    )

    monkeypatch.setattr(
        "app.api.receipt.save_uploaded_file",
        lambda file: "uploads/no-items.jpg",
    )

    monkeypatch.setattr(
        "app.api.receipt.ocr_service.extract_text",
        lambda file_path: [],
    )

    monkeypatch.setattr(
        "app.api.receipt.receipt_parser.parse",
        lambda ocr_result: {
            "store_name": "Unknown Store",
            "receipt_date": "2026-08-12",
            "total_amount": 500,
            "validation": {
                "status": "VALID",
            },
        },
    )

    response = client.post(
        "/receipts/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "receipt.jpg",
                b"fake image data",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["receipt_id"] is not None

    assert (
        data["parsed_receipt"]["store_name"]
        == "Unknown Store"
    )

# ============================================================
# UPLOAD - INTERNAL ERROR
# ============================================================

def test_upload_receipt_internal_error(
    client,
    monkeypatch,
):

    token = register_user(
        client,
        "receipt-upload-error@example.com",
    )

    monkeypatch.setattr(
        "app.api.receipt.save_uploaded_file",
        lambda file: "uploads/error.jpg",
    )

    def raise_error(file_path):
        raise RuntimeError(
            "OCR failed"
        )

    monkeypatch.setattr(
        "app.api.receipt.ocr_service.extract_text",
        raise_error,
    )

    response = client.post(
        "/receipts/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "receipt.jpg",
                b"fake image data",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 500

    data = response.json()

    assert (
        data["detail"]
        == "Failed to process receipt"
    )

# ============================================================
# UPLOAD - CLEANUP AFTER ERROR
# ============================================================

def test_upload_receipt_cleanup_after_error(
    client,
    monkeypatch,
    tmp_path,
):

    token = register_user(
        client,
        "receipt-upload-cleanup@example.com",
    )

    test_file = (
        tmp_path
        / "uploaded-receipt.jpg"
    )

    test_file.write_bytes(
        b"fake image"
    )

    monkeypatch.setattr(
        "app.api.receipt.save_uploaded_file",
        lambda file: str(test_file),
    )

    def raise_error(file_path):
        raise RuntimeError(
            "OCR failed"
        )

    monkeypatch.setattr(
        "app.api.receipt.ocr_service.extract_text",
        raise_error,
    )

    response = client.post(
        "/receipts/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "receipt.jpg",
                b"fake image data",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 500

    assert not test_file.exists()

# ============================================================
# UPLOAD - HTTP EXCEPTION CLEANUP
# ============================================================

def test_upload_receipt_http_exception_cleans_up_file(
    client,
    monkeypatch,
    tmp_path,
):

    token = register_user(
        client,
        "receipt-http-cleanup@example.com",
    )

    # Create a real temporary file.
    uploaded_file = (
        tmp_path / "receipt.jpg"
    )

    uploaded_file.write_bytes(
        b"fake receipt image"
    )

    # Make save_uploaded_file return
    # the existing temporary file.
    monkeypatch.setattr(
        "app.api.receipt.save_uploaded_file",
        lambda file: str(uploaded_file),
    )

    # OCR can return anything because the parser
    # will cause validation to fail.
    monkeypatch.setattr(
        "app.api.receipt.ocr_service.extract_text",
        lambda file_path: [],
    )

    # Force an HTTPException from validation.
    monkeypatch.setattr(
        "app.api.receipt.receipt_parser.parse",
        lambda ocr_result: {
            "validation": {
                "status": "INVALID",
                "reason": "Invalid receipt",
            },
        },
    )

    response = client.post(
        "/receipts/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "receipt.jpg",
                b"fake image data",
                "image/jpeg",
            ),
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert (
        data["detail"]["message"]
        == "Receipt validation failed"
    )

    # The HTTPException handler should delete
    # the uploaded file.
    assert not uploaded_file.exists()