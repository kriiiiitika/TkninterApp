# StockFlow Inventory Management System

StockFlow is a desktop product inventory manager built with Python's standard-library Tkinter and ttk widgets. The application opens in a near-screen-sized window, adapts its panels when resized, and keeps its inventory Listbox visible and interactive.

## Academic Team

| Name | Register Number |
| :--- | :--- |
| Kritika Kumari | `RA2511003010191` |
| Tanvi Gupta | `RA2511003010192` |
| Sriya Sahu | `RA2511003010193` |

## Features

- Add, search by ID, update quantity and price, delete with confirmation, and clear form fields.
- Product name and category filters, with a Show All reset.
- Tkinter `OptionMenu`, `Checkbutton`, and `Listbox` controls with scrolling and reliable selection mapping.
- Summary cards for product count, total inventory value, low stock, and out-of-stock products.
- JSON persistence in `inventory.json` beside `inventory.py`, with atomic writes and protection against malformed files.
- Validation for duplicate IDs, required values, non-negative integer quantities, and finite positive prices.
- Responsive light dashboard with larger text, compact empty states, and a scrollable fallback for short windows.

Low stock is an available product with a quantity from 1 through 5. A product with zero quantity is always considered out of stock.

## Run on macOS

Verify Tkinter is available, then run:

```bash
python3 -m tkinter
python3 inventory.py
```

The first successful add, update, or delete creates `inventory.json` in the project directory.

## Tests

Run the unit tests and syntax check from this directory:

```bash
python3 -m py_compile inventory.py
python3 -m unittest discover -v
```
