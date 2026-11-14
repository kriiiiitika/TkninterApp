
# StockFlow – Product Inventory Management System

StockFlow is a desktop-based Product Inventory Management System developed using **Python, Tkinter, and ttk**. It provides a modern, user-friendly interface for managing products, monitoring stock availability, and tracking inventory value.

The application features a responsive light-themed dashboard, persistent JSON storage, and interactive inventory management controls.

## Academic Project Details

**Course:** Advanced Programming Practice (APP)  
**Project:** Tkinter GUI Application  
**Batch:** 1

### Team Members

| Name | Registration Number |
|---|---|
| Kritika Kumari | RA2511003010191 |
| Tanvi Gupta | RA2511003010192 |
| Sriya Sahu | RA2511003010193 |

## Features

### Product Management

- Add products with ID, name, quantity, price, category, and availability.
- Search products using their unique Product ID.
- Update product quantity, unit price, and stock availability.
- Delete products with confirmation.
- Clear input fields.

### Inventory Dashboard

- **Total Products:** Number of products in inventory.
- **Inventory Value:** Total inventory value in Indian Rupees (₹).
- **Low Stock:** Available products with quantities from 1 to 5.
- **Out of Stock:** Products with zero quantity or unavailable status.

### Graphical User Interface

- Modern, responsive light-themed Tkinter dashboard.
- Category selection using `OptionMenu`.
- Stock availability using `Checkbutton`.
- Product display using `Listbox`.
- Search and category filtering.
- Color-coded stock indicators.
- Scrollable inventory records.

### Data Storage and Validation

- Automatic JSON-based data persistence.
- Duplicate Product ID prevention.
- Mandatory Product ID and Product Name.
- Non-negative integer quantity validation.
- Positive, finite unit-price validation.
- Safe handling of missing or corrupted JSON files.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Tkinter | Graphical user interface |
| ttk | Themed GUI components |
| JSON | Persistent inventory storage |
| unittest | Automated testing |

No external Python packages are required.

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/kriiiiitika/TkninterApp.git
```

### 2. Open the project directory

```bash
cd TkninterApp
```

### 3. Verify Tkinter installation (optional)

```bash
python3 -m tkinter
```

### 4. Run the application

```bash
python3 inventory.py
```

The application opens in a desktop window.

The `inventory.json` file is automatically created after the first successful inventory modification.

## Running Tests

Check Python syntax:

```bash
python3 -m py_compile inventory.py
```

Run all automated tests:

```bash
python3 -m unittest discover -v
```

The project has passed **19 automated tests**, covering CRUD operations, validation, JSON persistence, stock availability, and data consistency.

## Project Structure

```text
TkninterApp/
├── inventory.py
├── test_inventory.py
├── README.md
├── .gitignore
└── inventory.json       # Generated automatically
```

## Inventory Rules

- Quantity cannot be negative.
- Unit price must be greater than zero.
- Quantity 0 always means Out of Stock.
- Products with positive quantity can be marked available or unavailable.
- Available products with quantities from 1 to 5 are considered Low Stock.

## Future Enhancements

- Export inventory reports to CSV.
- Product sales and purchase history.
- Barcode scanning.
- Advanced inventory analytics.

---

**StockFlow – Simplifying Product Inventory Management.**
