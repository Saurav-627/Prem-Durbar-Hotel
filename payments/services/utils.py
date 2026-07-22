from decimal import ROUND_HALF_UP, Decimal
import re

TWOPLACES = Decimal("0.01")

def decimal_2(value) -> Decimal:
    """
    Normalize value to a Decimal with exactly 2 decimal places.
    """
    return Decimal(str(value or 0)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def to_minor_units(value) -> int:
    """
    Convert major currency amount (e.g. 12.34) to minor units (e.g. 1234).
    """
    return int((decimal_2(value) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def clean_and_split_remarks(remarks2: str, max_len: int = 25, remove_word: str = None, prefix: str = "Buy", suffix: str = "Credits") -> tuple[str, str]:
    remarks1 = prefix
    if remove_word:
        remarks2 = re.sub(r"(?i)\s*" + re.escape(remove_word) + r"\s*", " ", remarks2).strip() or suffix

    if len(remarks2) > max_len:
        excess_len = len(remarks2) - max_len
        split_idx = remarks2.find(" ", excess_len)
        if split_idx == -1:
            split_idx = excess_len

        remarks1 = f"{prefix} {remarks2[:split_idx]}".strip()
        remarks2 = remarks2[split_idx:].strip() or suffix

    return remarks1, remarks2
