# Product Inventory Management System (Tkinter GUI)

**Course:** Advanced Programming Practice (APP) – Tkinter Project  
**Allocation:** Batch 1

## Team Members
| Register Number | Name |
| :--- | :--- |
| `RA2511003010191` | Kritika Kumari |
| `RA2511003010192` | Tanvi Gupta |
| `RA2511003010193` | Sriya Sahu |

## Features & Implementation
- **Form Inputs:** `Entry` widgets for Product ID, Product Name, Quantity, and Unit Price (₹).
- **Selection Widgets:** `OptionMenu` for product category selection and `Checkbutton` for stock availability status.
- **CRUD Operations:**
  - **Add Product:** Adds validated items to the inventory dictionary and updates the display.
  - **Search by ID:** Fetches and populates product details into the form fields.
  - **Update Qty/Price:** Modifies existing product quantity, price, and stock status.
  - **Delete Product:** Removes selected or searched records after confirmation.
  - **Interactive Listbox:** Displays all inventory records; clicking any row loads its details into the form.
- **Input Validation:**
  - Product ID and Product Name are mandatory.
  - Quantity must be a non-negative integer (`>= 0`).
  - Unit Price must be a positive number (`> 0`).

## How to Run
1. Ensure Python 3.x is installed with Tkinter (`python3 -m tkinter` to verify).
2. Clone the repository and run the application:
   ```bash
   git clone <your-repo-url>
   cd product-inventory-system
   python3 inventory.py
