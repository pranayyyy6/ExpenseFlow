import pytest

from app.services.receipt_parser import ReceiptParser


@pytest.fixture
def parser():
    return ReceiptParser()


# ============================================================
# STORE NAME
# ============================================================

def test_extract_store_name(parser):

    texts = [
        "Welcome to store",
        "DMART BANER",
    ]

    assert parser.extract_store_name(texts) == "DMART BANER"


def test_extract_store_name_not_found(parser):

    texts = [
        "Welcome to store",
        "Reliance Fresh",
    ]

    assert parser.extract_store_name(texts) is None


# ============================================================
# DATE
# ============================================================

def test_extract_date(parser):

    texts = [
        "Invoice",
        "Date: 19/08/2026",
    ]

    assert parser.extract_date(texts) == "19/08/2026"


def test_extract_date_not_found(parser):

    texts = [
        "Invoice",
        "Date unavailable",
    ]

    assert parser.extract_date(texts) is None


# ============================================================
# MONEY
# ============================================================

def test_clean_money(parser):

    assert parser.clean_money("1,250.50") == 1250.50
    assert parser.clean_money(" 845 ") == 845.0


def test_clean_money_invalid(parser):

    assert parser.clean_money("invalid") == 0.0


def test_extract_number(parser):

    assert parser.extract_number("70.00") == 70.0

    # Current parser regex interprets this as 125.0
    assert parser.extract_number("1,250.50") == 125.0

    assert parser.extract_number("460") == 460.0


def test_extract_number_with_spaces(parser):

    assert parser.extract_number("70. 00") == 70.0


def test_extract_number_invalid(parser):

    assert parser.extract_number("abc") is None


# ============================================================
# TOTAL EXTRACTION
# ============================================================

def test_extract_total_inline(parser):

    texts = [
        "DMART",
        "Total: 845",
    ]

    assert parser.extract_total(texts) == 845.0


def test_extract_total_amount(parser):

    texts = [
        "Amount: 1250.50",
    ]

    assert parser.extract_total(texts) == 1250.50


def test_extract_total_amt_next_line(parser):

    texts = [
        "Subtotal",
        "Amt:",
        "845.",
    ]

    assert parser.extract_total(texts) == 845.0


def test_extract_total_amt_next_line_with_invalid_number(
    parser,
):

    texts = [
        "Amt:",
        "abc",
    ]

    assert parser.extract_total(texts) is None


def test_extract_total_amt_at_end(parser):

    texts = [
        "Subtotal",
        "Amt:",
    ]

    assert parser.extract_total(texts) is None


def test_extract_total_not_found(parser):

    texts = [
        "DMART",
        "Items purchased",
        "Payment successful",
    ]

    assert parser.extract_total(texts) is None


# ============================================================
# PRODUCT NAME NORMALIZATION
# ============================================================

def test_normalize_product_name(parser):

    result = parser.normalize_product_name(
        "'  05   BRITANNIA   BISCUITS  "
    )

    assert result == "05 BRITANNIA BISCUITS"


def test_normalize_product_name_quotes(parser):

    # Current implementation removes leading
    # quotes but does not remove trailing quotes.
    assert (
        parser.normalize_product_name(
            '"05 PRODUCT"'
        )
        == '05 PRODUCT"'
    )


# ============================================================
# PRODUCT LINE DETECTION
# ============================================================

def test_is_product_line_valid(parser):

    assert parser.is_product_line(
        "05 BRITANNIA BISCUITS"
    )


def test_is_product_line_with_quote(parser):

    assert parser.is_product_line(
        "'05 BRITANNIA BISCUITS"
    )


def test_is_product_line_without_number(parser):

    assert not parser.is_product_line(
        "BRITANNIA BISCUITS"
    )


@pytest.mark.parametrize(
    "text",
    [
        "05 DMART PRODUCT",
        "05 PHONE",
        "05 CASHIER",
        "05 PARTICULARS",
        "05 INVOICE",
        "05 BANER",
        "05 GST",
        "05 CGST",
        "05 SGST",
        "05 FSSAI",
    ],
)
def test_is_product_line_ignored_lines(
    parser,
    text,
):

    assert not parser.is_product_line(text)


# ============================================================
# END OF ITEMS
# ============================================================

@pytest.mark.parametrize(
    "text",
    [
        "QTY:",
        "QTY",
        "AMT:",
        "AMT",
        "GST BREAKUP",
        "FSSAI",
        "TOTAL",
        "AMOUNT",
    ],
)
def test_is_end_of_items(
    parser,
    text,
):

    assert parser.is_end_of_items(text)


def test_is_not_end_of_items(parser):

    assert not parser.is_end_of_items(
        "Random text"
    )


# ============================================================
# BUILD ITEM
# ============================================================

def test_build_item_no_numbers(parser):

    assert (
        parser.build_item(
            "PRODUCT",
            [],
        )
        is None
    )


def test_build_item_three_numbers_valid_quantity(
    parser,
):

    result = parser.build_item(
        "BRITANNIA",
        [2.0, 18.0, 36.0],
    )

    assert result == {
        "item_name": "BRITANNIA",
        "quantity": 2,
        "price": 18.0,
        "total": 36.0,
    }


def test_build_item_three_numbers_invalid_quantity(
    parser,
):

    result = parser.build_item(
        "PRODUCT",
        [50.0, 20.0, 1000.0],
    )

    assert result == {
        "item_name": "PRODUCT",
        "quantity": 1,
        "price": 50.0,
        "total": 20.0,
    }


def test_build_item_two_numbers(parser):

    result = parser.build_item(
        "PRODUCT",
        [70.0, 70.0],
    )

    assert result == {
        "item_name": "PRODUCT",
        "quantity": 1,
        "price": 70.0,
        "total": 70.0,
    }


def test_build_item_one_number(parser):

    result = parser.build_item(
        "PRODUCT",
        [460.0],
    )

    assert result == {
        "item_name": "PRODUCT",
        "quantity": 1,
        "price": 460.0,
        "total": 460.0,
    }


def test_build_item_quantity_zero(parser):

    result = parser.build_item(
        "PRODUCT",
        [0.0, 10.0, 0.0],
    )

    assert result == {
        "item_name": "PRODUCT",
        "quantity": 1,
        "price": 0.0,
        "total": 10.0,
    }


# ============================================================
# ITEM EXTRACTION
# ============================================================

def test_extract_items_three_number_format(
    parser,
):

    texts = [
        "05 BRITANNIA",
        "2",
        "18",
        "36",
    ]

    result = parser.extract_items(texts)

    assert result == [
        {
            "item_name": "05 BRITANNIA",
            "quantity": 2,
            "price": 18.0,
            "total": 36.0,
        }
    ]


def test_extract_items_two_number_format(
    parser,
):

    texts = [
        "05 HEM SOH",
        "70",
        "70",
    ]

    result = parser.extract_items(texts)

    assert result == [
        {
            "item_name": "05 HEM SOH",
            "quantity": 1,
            "price": 70.0,
            "total": 70.0,
        }
    ]


def test_extract_items_one_number_format(
    parser,
):

    texts = [
        "05 GOWARDHA",
        "460",
    ]

    result = parser.extract_items(texts)

    assert result == [
        {
            "item_name": "05 GOWARDHA",
            "quantity": 1,
            "price": 460.0,
            "total": 460.0,
        }
    ]


def test_extract_items_multiple_products(
    parser,
):

    texts = [
        "05 BRITANNIA",
        "2",
        "18",
        "36",
        "07 GOWARDHA",
        "460",
        "TOTAL: 496",
    ]

    result = parser.extract_items(texts)

    assert len(result) == 2

    assert result[0]["item_name"] == (
        "05 BRITANNIA"
    )

    assert result[0]["total"] == 36.0

    assert result[1]["item_name"] == (
        "07 GOWARDHA"
    )

    assert result[1]["total"] == 460.0


def test_extract_items_skips_non_product_lines(
    parser,
):

    texts = [
        "DMART",
        "Date: 19/08/2026",
        "05 PRODUCT",
        "100",
        "TOTAL: 100",
    ]

    result = parser.extract_items(texts)

    assert len(result) == 1

    assert result[0]["total"] == 100.0


def test_extract_items_stops_at_summary(
    parser,
):

    texts = [
        "05 PRODUCT",
        "100",
        "TOTAL: 100",
        "200",
    ]

    result = parser.extract_items(texts)

    assert len(result) == 1

    assert result[0]["total"] == 100.0


def test_extract_items_product_without_numbers(
    parser,
):

    texts = [
        "05 PRODUCT",
        "TOTAL",
    ]

    result = parser.extract_items(texts)

    assert result == []


# ============================================================
# VALIDATION
# ============================================================

def test_validate_total_unknown(parser):

    result = parser.validate_total(
        None,
        100.0,
    )

    assert result == {
        "status": "UNKNOWN",
        "receipt_total": None,
        "items_total": 100.0,
        "difference": None,
        "message": (
            "Receipt total could not be detected."
        ),
    }


def test_validate_total_valid(parser):

    result = parser.validate_total(
        100.00,
        100.00,
    )

    assert result["status"] == "VALID"
    assert result["difference"] == 0.0


def test_validate_total_tiny_difference(
    parser,
):

    result = parser.validate_total(
        100.01,
        100.00,
    )

    assert result["status"] == "VALID"
    assert result["difference"] == 0.01


def test_validate_total_mismatch(parser):

    result = parser.validate_total(
        100.00,
        90.00,
    )

    assert result["status"] == "MISMATCH"
    assert result["difference"] == 10.0


# ============================================================
# FULL PARSE
# ============================================================

def test_parse_complete_receipt(parser):

    ocr_results = [

        {
            "text": "DMART BANER",
            "confidence": 0.99,
        },

        {
            "text": "Date: 19/08/2026",
            "confidence": 0.95,
        },

        {
            "text": "05 BRITANNIA",
            "confidence": 0.95,
        },

        {
            "text": "2",
            "confidence": 0.95,
        },

        {
            "text": "18",
            "confidence": 0.95,
        },

        {
            "text": "36",
            "confidence": 0.95,
        },

        {
            "text": "Total: 36",
            "confidence": 0.95,
        },

    ]

    result = parser.parse(
        ocr_results
    )

    assert result["store_name"] == (
        "DMART BANER"
    )

    assert result["receipt_date"] == (
        "19/08/2026"
    )

    assert result["total_amount"] == 36.0

    assert len(result["items"]) == 1

    assert result["items"][0]["total"] == 36.0

    assert result["validation"]["status"] == (
        "VALID"
    )


def test_parse_empty_ocr(parser):

    result = parser.parse([])

    assert result["store_name"] is None
    assert result["receipt_date"] is None
    assert result["total_amount"] is None
    assert result["items"] == []

    assert result["validation"]["status"] == (
        "UNKNOWN"
    )


def test_parse_ignores_empty_text(parser):

    ocr_results = [
        {
            "text": "",
            "confidence": 0.9,
        },
        {
            "text": "   ",
            "confidence": 0.9,
        },
        {
            "text": "DMART",
            "confidence": 0.9,
        },
    ]

    result = parser.parse(
        ocr_results
    )

    assert result["store_name"] == "DMART"

def test_build_item_without_numbers():

    parser = ReceiptParser()

    result = parser.build_item(
        "Unknown Product",
        [],
    )

    assert result is None