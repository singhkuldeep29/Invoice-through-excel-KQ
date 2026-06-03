#!/usr/bin/env python3
import re
import sys
from pathlib import Path

from excel_reader import read_invoices
from invoice_renderer import build_invoice_pdf


def _safe(text):
    """Convert to a filesystem-safe string."""
    return re.sub(r'[^\w\-]', '_', str(text or '').replace('/', '-'))


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_invoices.py <path_to_excel.xlsx>")
        sys.exit(1)

    xlsx_path = Path(sys.argv[1])
    if not xlsx_path.exists():
        print(f"Error: File not found: {xlsx_path}")
        sys.exit(1)

    output_dir = xlsx_path.parent / 'invoices'
    output_dir.mkdir(exist_ok=True)

    print(f"Reading: {xlsx_path.name}")
    try:
        invoices, warnings, skipped_n = read_invoices(xlsx_path)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    for w in warnings:
        print(f"  Warning: {w}")

    generated = 0
    errors = 0
    for data in invoices:
        invoice_no = _safe(data['Invoice No.'])
        payee = _safe(data['Payee Name'])
        filename = f"{invoice_no}_{payee}.pdf"
        output_path = output_dir / filename

        try:
            build_invoice_pdf(data, output_path)
            print(f"  Generated: {filename}")
            generated += 1
        except Exception as e:
            print(f"  Error ({filename}): {e}")
            errors += 1

    print(f"\nDone.")
    print(f"  Generated : {generated}")
    print(f"  Errors    : {errors}")
    print(f"  Skipped (Generate?≠Y) : {skipped_n}")
    print(f"  Skipped (missing data): {len(warnings)}")
    if generated:
        print(f"  Output → {output_dir}/")


if __name__ == '__main__':
    main()
