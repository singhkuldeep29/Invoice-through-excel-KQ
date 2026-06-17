#!/usr/bin/env python3
"""
Auto-finds the Excel file in this folder and generates all invoice PDFs.

Picks the single .xlsx file in the current folder. If there are several,
it asks which one to use. PDFs are written to an 'invoices' subfolder.
"""
import sys
from pathlib import Path

from excel_reader import read_invoices
from generate_invoices import _safe
from invoice_renderer import build_invoice_pdf


def find_excel(folder):
    candidates = [
        p for p in folder.glob('*.xlsx')
        if not p.name.startswith('~$')  # skip temp files Excel leaves open
    ]
    if not candidates:
        print("ERROR: No Excel (.xlsx) file found in this folder.")
        print(f"Put your invoice Excel file in:\n  {folder}")
        return None
    if len(candidates) == 1:
        return candidates[0]

    print("Multiple Excel files found:")
    for i, p in enumerate(candidates, 1):
        print(f"  {i}) {p.name}")
    while True:
        choice = input("Which one? Enter a number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice) - 1]
        print("Invalid choice, try again.")


def main():
    folder = Path(__file__).resolve().parent
    xlsx_path = find_excel(folder)
    if xlsx_path is None:
        sys.exit(1)

    output_dir = folder / 'invoices'
    output_dir.mkdir(exist_ok=True)

    print(f"Reading: {xlsx_path.name}")
    try:
        invoices, warnings, skipped_n = read_invoices(xlsx_path)
    except ValueError as e:
        print(f"ERROR: {e}")
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

    print("\nDone.")
    print(f"  Generated : {generated}")
    print(f"  Errors    : {errors}")
    print(f"  Skipped (Generate?!=Y) : {skipped_n}")
    print(f"  Skipped (missing data) : {len(warnings)}")
    if generated:
        print(f"\nPDFs saved to: {output_dir}")


if __name__ == '__main__':
    main()
