
#  double-click → pick Excel → PDFs appear. (through .exe)


# Invoice-through-excel-KQ
Upload your excel sheet with pre filled data to the application and then it will generate and save invoices in PDF format in pre defined format (each row in excel is fields required in one invoice)

---

## Easiest way (Windows users)

1. Keep all the files in this folder as they are.
2. Put your invoice Excel file (`.xlsx`) **inside this same folder**.
3. **Double-click `run.bat`** (or type `run.bat` in the terminal opened in this folder).

That's it. The PDFs appear in an `invoices` folder, which opens automatically.

The first run installs the required components automatically. If Python is not
installed, `run.bat` shows you exactly how to install it (install Python from
https://www.python.org/downloads/ and tick **"Add Python to PATH"**).

> Mac / Linux users can run the same thing with: `python3 run_invoices.py`

---

## For developers

To Run the file 

Usage: python generate_invoices.py <path_to_excel.xlsx>



If you put the excel file inside the same project folder or directory then (having excel file name 'KQ-Invoices.xlsx')

"python3 generate_invoices.py KQ-Invoices.xlsx"

or full path

"python3 generate_invoices.py /Volumes/kuldeep/KQ-Invoices/KQ-Invoices.xlsx"
