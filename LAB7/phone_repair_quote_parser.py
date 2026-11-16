"""Defensive parsing helpers for phone repair requests.

Invalid inputs return empty results instead of raising an exception. These
helpers parse user input; mask_imei does not validate IMEI length or checksum.
"""

import re


def mask_imei(imei):
    """Remove dashes/whitespace and mask all but the last four ASCII digits.

    Return an empty string for non-string or non-digit input. Inputs of four
    digits or fewer are returned unchanged, following the last-four rule.
    """
    if not isinstance(imei, str):
        return ""
    digits = "".join(char for char in imei if char != "-" and not char.isspace())
    if not digits or not digits.isascii() or not digits.isdigit():
        return ""
    return "*" * max(0, len(digits) - 4) + digits[-4:]

def parse_parts_order(text):
    """
    Parse 'screen x1; battery x2' into a {part: quantity} dictionary.

    Skip malformed entries and non-positive quantities, preserve valid entries,
    and sum repeated parts. Accept x or X and optional whitespace. Non-string
    input returns an empty dictionary. Part names remain case-sensitive.
    """
    order = {}
    if not isinstance(text, str):
        return order
    for item in text.split(';'):
        match = re.fullmatch(r"\s*(.+?)\s*[xX]\s*([0-9]+)\s*", item)
        if match is None:
            continue
        part, quantity_text = match.groups()
        part = part.strip()
        if not part:
            continue
        try:
            quantity = int(quantity_text)
        except ValueError:
            # Python limits integer-string conversion length; huge inputs are invalid.
            continue
        if quantity > 0:
            order[part] = order.get(part, 0) + quantity
    return order

def parse_model(text):
    """
    Split 'Brand Model name' into a (brand, model) tuple using any whitespace.

    Missing fields become empty strings; non-string input returns ('', '').
    """
    if not isinstance(text, str):
        return "", ""
    fields = text.split(None, 1)
    if not fields:
        return "", ""
    return fields[0].title(), fields[1].strip() if len(fields) > 1 else ""

def main():
    print("==== Running mask_imei ====")
    value = input("Enter an IMEI number (e.g. 35-209900-176148-1): ")
    print("Masked IMEI:", mask_imei(value))

    print("\n==== Running parse_parts_order ====")
    value = input("Enter parts and quantities as PART xQTY separated by ; (e.g. screen x1; battery x2): ")
    print("Parts order:", parse_parts_order(value))

    print("\n==== Running parse_model ====")
    value = input("Enter the phone brand and model (e.g. Samsung Galaxy S23): ")
    print("Brand and model:", parse_model(value))

if __name__ == "__main__":
    main()
