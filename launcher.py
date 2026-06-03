import os
import re
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox


def _safe(text):
    return re.sub(r'[^\w\-]', '_', str(text or '').replace('/', '-'))


def run_generation(xlsx_path, log_cb, done_cb):
    try:
        from excel_reader import read_invoices
        from invoice_renderer import build_invoice_pdf

        output_dir = xlsx_path.parent / 'invoices'
        output_dir.mkdir(exist_ok=True)

        log_cb(f"Reading: {xlsx_path.name}\n")
        invoices, warnings, skipped_n = read_invoices(xlsx_path)

        for w in warnings:
            log_cb(f"  Warning: {w}\n")

        generated = 0
        errors = 0
        for data in invoices:
            invoice_no = _safe(data['Invoice No.'])
            payee = _safe(data['Payee Name'])
            filename = f"{invoice_no}_{payee}.pdf"
            output_path = output_dir / filename
            try:
                build_invoice_pdf(data, output_path)
                log_cb(f"  Generated: {filename}\n")
                generated += 1
            except Exception as e:
                log_cb(f"  Error ({filename}): {e}\n")
                errors += 1

        summary = (
            f"\nDone!\n"
            f"  Generated : {generated}\n"
            f"  Errors    : {errors}\n"
            f"  Skipped (Generate?≠Y) : {skipped_n}\n"
            f"  Skipped (missing data): {len(warnings)}\n"
        )
        if generated:
            summary += f"\nPDFs saved to:\n{output_dir}"

        done_cb(True, summary, str(output_dir) if generated else None)

    except Exception as e:
        done_cb(False, str(e), None)


class App:
    def __init__(self, root):
        self.root = root
        root.title("KQ Invoice Generator")
        root.geometry("540x420")
        root.resizable(False, False)
        root.configure(bg="#ffffff")

        # Title
        tk.Label(
            root, text="KQ Invoice Generator",
            font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#1F497D"
        ).pack(pady=(24, 4))

        tk.Label(
            root, text="Select your Excel file to generate PDF invoices",
            font=("Segoe UI", 10), bg="#ffffff", fg="#555555"
        ).pack()

        # Select button
        self.btn = tk.Button(
            root, text="  Select Excel File  ",
            font=("Segoe UI", 11, "bold"),
            bg="#0078D4", fg="white",
            activebackground="#005fa3", activeforeground="white",
            relief="flat", cursor="hand2", padx=16, pady=8,
            command=self.select_file,
        )
        self.btn.pack(pady=20)

        # Selected file label
        self.file_label = tk.Label(
            root, text="No file selected",
            font=("Segoe UI", 9), bg="#ffffff", fg="#999999"
        )
        self.file_label.pack()

        # Log box
        frame = tk.Frame(root, bg="#f0f4f8", relief="flat")
        frame.pack(padx=24, pady=(12, 4), fill="both", expand=True)

        self.log = tk.Text(
            frame, font=("Consolas", 9), bg="#f0f4f8", fg="#333333",
            relief="flat", state="disabled", wrap="word",
            highlightthickness=0, borderwidth=0,
        )
        self.log.pack(padx=8, pady=8, fill="both", expand=True)

        # Footer
        tk.Label(
            root, text="PDFs will be saved in an 'invoices' folder next to your Excel file.",
            font=("Segoe UI", 8), bg="#ffffff", fg="#aaaaaa"
        ).pack(pady=(0, 10))

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select Invoice Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if not path:
            return
        self.xlsx_path = Path(path)
        self.file_label.config(text=self.xlsx_path.name, fg="#333333")
        self._start_generation()

    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg)
        self.log.see("end")
        self.log.config(state="disabled")
        self.root.update_idletasks()

    def _start_generation(self):
        self.btn.config(state="disabled", text="  Generating...  ")
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

        t = threading.Thread(
            target=run_generation,
            args=(self.xlsx_path, self._log, self._on_done),
            daemon=True,
        )
        t.start()

    def _on_done(self, success, message, output_dir):
        self.btn.config(state="normal", text="  Select Excel File  ")
        if success:
            messagebox.showinfo("Done", message)
            if output_dir and os.path.isdir(output_dir):
                os.startfile(output_dir)
        else:
            messagebox.showerror("Error", f"Something went wrong:\n\n{message}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
