import re
from typing import Any


class ReceiptParser:

    # ============================================================
    # REGEX
    # ============================================================

    DATE_PATTERN = re.compile(
        r"\b\d{2}/\d{2}/\d{4}\b"
    )

    PRODUCT_PATTERN = re.compile(
        r"^[\'`\"]?\d+\s+[A-Za-z]",
        re.IGNORECASE,
    )

    TOTAL_PATTERN = re.compile(
        r"(?:Amt|Amount|Total)\s*:?\s*"
        r"₹?\s*(\d+(?:[.,]\d{1,2})?)",
        re.IGNORECASE,
    )

    # ============================================================
    # MAIN PARSER
    # ============================================================

    def parse(
        self,
        ocr_results: list[dict[str, Any]],
    ) -> dict:

        texts = [
            item["text"].strip()
            for item in ocr_results
            if item.get("text")
        ]

        store_name = self.extract_store_name(texts)

        receipt_date = self.extract_date(texts)

        total_amount = self.extract_total(texts)

        items = self.extract_items(texts)

        items_total = round(
            sum(item["total"] for item in items),
            2,
        )

        validation = self.validate_total(
            total_amount,
            items_total,
        )

        return {
            "store_name": store_name,
            "receipt_date": receipt_date,
            "total_amount": total_amount,
            "items": items,
            "validation": validation,
        }

    # ============================================================
    # STORE
    # ============================================================

    def extract_store_name(
        self,
        texts: list[str],
    ) -> str | None:

        for text in texts:

            if "DMART" in text.upper():

                return text.strip()

        return None

    # ============================================================
    # DATE
    # ============================================================

    def extract_date(
        self,
        texts: list[str],
    ) -> str | None:

        for text in texts:

            match = self.DATE_PATTERN.search(text)

            if match:

                return match.group(0)

        return None

    # ============================================================
    # TOTAL
    # ============================================================

    def extract_total(
        self,
        texts: list[str],
    ) -> float | None:

        for index, text in enumerate(texts):

            # ----------------------------------------------------
            # Example:
            #
            # Total: 845
            # Amount: 845
            # ----------------------------------------------------

            match = self.TOTAL_PATTERN.search(text)

            if match:

                return self.clean_money(
                    match.group(1)
                )

            # ----------------------------------------------------
            # Example OCR:
            #
            # Amt:
            # 845.
            # ----------------------------------------------------

            if text.lower().startswith("amt"):

                if index + 1 < len(texts):

                    number = self.extract_number(
                        texts[index + 1]
                    )

                    if number is not None:

                        return number

        return None

    # ============================================================
    # ITEM EXTRACTION
    # ============================================================

    def extract_items(
        self,
        texts: list[str],
    ) -> list[dict]:

        items = []

        index = 0

        while index < len(texts):

            raw_text = texts[index].strip()

            # ----------------------------------------------------
            # Normalize OCR garbage
            # ----------------------------------------------------

            product_name = self.normalize_product_name(
                raw_text
            )

            # ----------------------------------------------------
            # Check whether this is a product line
            # ----------------------------------------------------

            if not self.is_product_line(
                raw_text
            ):

                index += 1

                continue

            # ----------------------------------------------------
            # Collect numbers until next product
            # ----------------------------------------------------

            numbers = []

            next_index = index + 1

            while next_index < len(texts):

                next_text = texts[
                    next_index
                ].strip()

                # Stop when another product starts.

                if self.is_product_line(
                    next_text
                ):
                    break

                # Stop at obvious receipt summary.

                if self.is_end_of_items(
                    next_text
                ):
                    break

                number = self.extract_number(
                    next_text
                )

                if number is not None:

                    numbers.append(number)

                next_index += 1

            # ----------------------------------------------------
            # Convert numbers to item
            # ----------------------------------------------------

            item = self.build_item(
                product_name,
                numbers,
            )

            if item is not None:

                items.append(item)

            index = next_index

        return items

    # ============================================================
    # PRODUCT DETECTION
    # ============================================================

    def is_product_line(
        self,
        text: str,
    ) -> bool:

        text = text.strip()

        # Remove OCR punctuation before checking.

        normalized = text.lstrip(
            "'`\" "
        )

        # Product lines generally start with:
        #
        # 307 HEM...
        # 05 GOWARDHA...
        # 05 BRITANNI...
        # 07 EVERFRE...

        if not re.match(
            r"^\d+\s+[A-Za-z]",
            normalized,
            re.IGNORECASE,
        ):

            return False

        upper = normalized.upper()

        # These are not products.

        ignored = [
            "DMART",
            "PHONE",
            "CASHIER",
            "PARTICULARS",
            "INVOICE",
            "BANER",
            "GST",
            "CGST",
            "SGST",
            "FSSAI",
        ]

        for word in ignored:

            if word in upper:

                return False

        return True

    # ============================================================
    # NORMALIZE PRODUCT NAME
    # ============================================================

    @staticmethod
    def normalize_product_name(
        text: str,
    ) -> str:

        text = text.strip()

        # Remove OCR quote characters.

        text = text.lstrip(
            "'`\" "
        )

        # Collapse multiple spaces.

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    # ============================================================
    # END OF ITEM SECTION
    # ============================================================

    @staticmethod
    def is_end_of_items(
        text: str,
    ) -> bool:

        upper = text.upper()

        endings = [
            "QTY:",
            "QTY",
            "AMT:",
            "AMT",
            "GST BREAKUP",
            "FSSAI",
            "TOTAL",
            "AMOUNT",
        ]

        for ending in endings:

            if upper.startswith(ending):

                return True

        return False

    # ============================================================
    # BUILD ITEM
    # ============================================================

    def build_item(
        self,
        product_name: str,
        numbers: list[float],
    ) -> dict | None:

        if not numbers:

            return None

        quantity = 1

        price = None

        total = None

        # --------------------------------------------------------
        # Product
        # Qty
        # Rate
        # Value
        #
        # Example:
        #
        # BRITANNI
        # 2
        # 18
        # 36
        # --------------------------------------------------------

        if len(numbers) >= 3:

            possible_quantity = numbers[0]

            if (
                possible_quantity.is_integer()
                and 1 <= possible_quantity <= 20
            ):

                quantity = int(
                    possible_quantity
                )

                price = numbers[1]

                total = numbers[2]

            else:

                price = numbers[0]

                total = numbers[1]

        # --------------------------------------------------------
        # Product
        # Rate
        # Value
        #
        # Example:
        #
        # HEM SOH
        # 70
        # 70
        # --------------------------------------------------------

        elif len(numbers) == 2:

            price = numbers[0]

            total = numbers[1]

        # --------------------------------------------------------
        # Product
        # Value
        #
        # Example:
        #
        # GOWARDHA
        # 460
        # 460
        # --------------------------------------------------------

        elif len(numbers) == 1:

            price = numbers[0]

            total = (
                price * quantity
            )

        if price is None:

            return None

        return {
            "item_name": product_name,
            "quantity": quantity,
            "price": round(price, 2),
            "total": round(total, 2),
        }

    # ============================================================
    # NUMBER EXTRACTION
    # ============================================================

    @staticmethod
    def extract_number(
        text: str,
    ) -> float | None:

        # Remove spaces so:
        #
        # 70. 00
        #
        # becomes:
        #
        # 70.00

        cleaned = text.replace(
            " ",
            "",
        )

        # OCR sometimes produces:
        #
        # 460.Q0
        # 460_Oc
        #
        # We only need the numeric component.

        match = re.search(
            r"\d+(?:[.,]\d{1,2})?",
            cleaned,
        )

        if not match:

            return None

        try:

            return float(
                match.group(0).replace(
                    ",",
                    "",
                )
            )

        except ValueError:

            return None

    # ============================================================
    # MONEY CLEANER
    # ============================================================

    @staticmethod
    def clean_money(
        value: str,
    ) -> float:

        value = value.replace(
            " ",
            "",
        )

        value = value.replace(
            ",",
            "",
        )

        try:

            return float(value)

        except ValueError:

            return 0.0

    # ============================================================
    # VALIDATION
    # ============================================================

    @staticmethod
    def validate_total(
        receipt_total: float | None,
        items_total: float,
    ) -> dict:

        if receipt_total is None:

            return {
                "status": "UNKNOWN",
                "receipt_total": None,
                "items_total": items_total,
                "difference": None,
                "message": (
                    "Receipt total could not be detected."
                ),
            }

        difference = round(
            receipt_total - items_total,
            2,
        )

        # Allow tiny floating point differences.

        if abs(difference) <= 0.01:

            return {
                "status": "VALID",
                "receipt_total": receipt_total,
                "items_total": items_total,
                "difference": difference,
                "message": (
                    "Receipt total matches "
                    "the sum of item totals."
                ),
            }

        return {
            "status": "MISMATCH",
            "receipt_total": receipt_total,
            "items_total": items_total,
            "difference": difference,
            "message": (
                "Receipt total does not match "
                "the sum of extracted items."
            ),
        }


# ================================================================
# SINGLE PARSER INSTANCE
# ================================================================

receipt_parser = ReceiptParser()

print("🔥 NEW RECEIPT PARSER LOADED")