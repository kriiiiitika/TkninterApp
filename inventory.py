import tkinter as tk
from tkinter import messagebox, ttk


class InventoryManagementApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Product Inventory Management System - Batch 1")
    self.root.geometry("920x560")
    self.root.resizable(False, False)

    # Bring window to front on macOS
    self.root.lift()
    self.root.attributes("-topmost", True)
    self.root.after_idle(self.root.attributes, "-topmost", False)

    # Apply native macOS aqua theme
    style = ttk.Style()
    style.theme_use("aqua")

    self.inventory = {}

    self.var_id = tk.StringVar()
    self.var_name = tk.StringVar()
    self.var_qty = tk.StringVar()
    self.var_price = tk.StringVar()
    self.var_category = tk.StringVar(value="Electronics")
    self.var_in_stock = tk.BooleanVar(value=True)

    self.setup_ui()

  def setup_ui(self):
    # Top Header Section (Batch & Team Allocation Details)
    header = ttk.Frame(self.root, padding=(20, 15, 20, 10))
    header.pack(fill="x")

    ttk.Label(
        header,
        text="Product Inventory Management System",
        font=("Helvetica Neue", 18, "bold"),
    ).pack(anchor="w")

    ttk.Label(
        header,
        text=(
            "Batch 1  |  RA2511003010191 KRITIKA KUMARI  •  RA2511003010192"
            " TANVI GUPTA  •  RA2511003010193 SRIYA SAHU"
        ),
        font=("Helvetica Neue", 11),
    ).pack(anchor="w", pady=(4, 0))

    ttk.Separator(self.root, orient="horizontal").pack(
        fill="x", padx=20, pady=5
    )

    # Main 2-Column Content Area
    main_frame = ttk.Frame(self.root, padding=20)
    main_frame.pack(fill="both", expand=True)
    main_frame.columnconfigure(0, weight=0, minsize=380)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # ---------------- LEFT PANEL: PRODUCT FORM & OPERATIONS ----------------
    form_frame = ttk.LabelFrame(
        main_frame, text=" Product Details & Operations ", padding=15
    )
    form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
    form_frame.columnconfigure(1, weight=1)

    # Product ID
    ttk.Label(form_frame, text="Product ID *:").grid(
        row=0, column=0, sticky="w", pady=8, padx=(0, 10)
    )
    ttk.Entry(form_frame, textvariable=self.var_id).grid(
        row=0, column=1, sticky="ew", pady=8
    )

    # Product Name
    ttk.Label(form_frame, text="Product Name *:").grid(
        row=1, column=0, sticky="w", pady=8, padx=(0, 10)
    )
    ttk.Entry(form_frame, textvariable=self.var_name).grid(
        row=1, column=1, sticky="ew", pady=8
    )

    # Category (OptionMenu)
    ttk.Label(form_frame, text="Category:").grid(
        row=2, column=0, sticky="w", pady=8, padx=(0, 10)
    )
    categories = [
        "Electronics",
        "Groceries",
        "Apparel",
        "Stationery",
        "Furniture",
        "Other",
    ]
    cat_menu = ttk.OptionMenu(
        form_frame, self.var_category, categories[0], *categories
    )
    cat_menu.grid(row=2, column=1, sticky="ew", pady=8)

    # Quantity
    ttk.Label(form_frame, text="Quantity *:").grid(
        row=3, column=0, sticky="w", pady=8, padx=(0, 10)
    )
    ttk.Entry(form_frame, textvariable=self.var_qty).grid(
        row=3, column=1, sticky="ew", pady=8
    )

    # Unit Price
    ttk.Label(form_frame, text="Unit Price (₹) *:").grid(
        row=4, column=0, sticky="w", pady=8, padx=(0, 10)
    )
    ttk.Entry(form_frame, textvariable=self.var_price).grid(
        row=4, column=1, sticky="ew", pady=8
    )

    # Stock Availability (Checkbutton)
    ttk.Checkbutton(
        form_frame,
        text="Available in Stock",
        variable=self.var_in_stock,
    ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 15))

    # Operation Buttons
    btn_frame = ttk.Frame(form_frame)
    btn_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
    btn_frame.columnconfigure(0, weight=1, uniform="btn")
    btn_frame.columnconfigure(1, weight=1, uniform="btn")

    ttk.Button(btn_frame, text="Add Product", command=self.add_product).grid(
        row=0, column=0, sticky="ew", padx=(0, 5), pady=4
    )
    ttk.Button(
        btn_frame, text="Search by ID", command=self.search_product
    ).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=4)
    ttk.Button(
        btn_frame, text="Update Qty/Price", command=self.update_product
    ).grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=4)
    ttk.Button(
        btn_frame, text="Delete Product", command=self.delete_product
    ).grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=4)
    ttk.Button(btn_frame, text="Clear Fields", command=self.clear_fields).grid(
        row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0)
    )

    # ---------------- RIGHT PANEL: INVENTORY LISTBOX ----------------
    list_frame = ttk.LabelFrame(
        main_frame,
        text=" Product Inventory (Click any item to load) ",
        padding=12,
    )
    list_frame.grid(row=0, column=1, sticky="nsew")
    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
    scrollbar.grid(row=0, column=1, sticky="ns")

    self.listbox = tk.Listbox(
        list_frame,
        font=("Menlo", 11),
        yscrollcommand=scrollbar.set,
    )
    self.listbox.grid(row=0, column=0, sticky="nsew")
    self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)
    scrollbar.config(command=self.listbox.yview)

  def validate_inputs(self, check_name=True):
    pid = self.var_id.get().strip()
    name = self.var_name.get().strip()
    qty_str = self.var_qty.get().strip()
    price_str = self.var_price.get().strip()

    if not pid:
      messagebox.showerror("Validation Error", "Product ID is mandatory.")
      return None

    if check_name and not name:
      messagebox.showerror("Validation Error", "Product Name is mandatory.")
      return None

    try:
      qty = int(qty_str)
      if qty < 0:
        raise ValueError
    except ValueError:
      messagebox.showerror(
          "Validation Error",
          "Quantity must be a non-negative integer (0 or more).",
      )
      return None

    try:
      price = float(price_str)
      if price <= 0:
        raise ValueError
    except ValueError:
      messagebox.showerror(
          "Validation Error", "Unit Price must be a positive number (> 0)."
      )
      return None

    return pid, name, qty, price

  def add_product(self):
    validated = self.validate_inputs(check_name=True)
    if not validated:
      return

    pid, name, qty, price = validated

    if pid in self.inventory:
      messagebox.showwarning(
          "Duplicate ID",
          f"Product ID '{pid}' already exists. Use 'Update Qty/Price' instead.",
      )
      return

    self.inventory[pid] = {
        "name": name,
        "category": self.var_category.get(),
        "qty": qty,
        "price": price,
        "in_stock": self.var_in_stock.get(),
    }

    self.refresh_listbox()
    self.clear_fields()
    messagebox.showinfo("Success", f"Product '{name}' added successfully.")

  def search_product(self):
    pid = self.var_id.get().strip()
    if not pid:
      messagebox.showwarning(
          "Input Required", "Enter a Product ID to search."
      )
      return

    if pid in self.inventory:
      item = self.inventory[pid]
      self.var_name.set(item["name"])
      self.var_category.set(item["category"])
      self.var_qty.set(str(item["qty"]))
      self.var_price.set(str(item["price"]))
      self.var_in_stock.set(item["in_stock"])
    else:
      messagebox.showinfo("Not Found", f"No product found with ID '{pid}'.")

  def update_product(self):
    pid = self.var_id.get().strip()
    if not pid:
      messagebox.showwarning(
          "Input Required", "Enter the Product ID to update."
      )
      return

    if pid not in self.inventory:
      messagebox.showerror("Not Found", f"Product ID '{pid}' does not exist.")
      return

    validated = self.validate_inputs(check_name=False)
    if not validated:
      return

    _, _, qty, price = validated

    self.inventory[pid]["qty"] = qty
    self.inventory[pid]["price"] = price
    self.inventory[pid]["in_stock"] = self.var_in_stock.get()

    self.refresh_listbox()
    messagebox.showinfo("Updated", f"Quantity and price updated for '{pid}'.")

  def delete_product(self):
    pid = self.var_id.get().strip()
    if not pid:
      messagebox.showwarning(
          "Input Required", "Enter or select a Product ID to delete."
      )
      return

    if pid in self.inventory:
      confirm = messagebox.askyesno(
          "Confirm Delete", f"Delete product '{pid}'?"
      )
      if confirm:
        del self.inventory[pid]
        self.refresh_listbox()
        self.clear_fields()
        messagebox.showinfo("Deleted", f"Product '{pid}' removed.")
    else:
      messagebox.showerror("Not Found", f"Product ID '{pid}' does not exist.")

  def refresh_listbox(self):
    self.listbox.delete(0, tk.END)
    for pid, data in self.inventory.items():
      status = "In Stock" if data["in_stock"] else "Out of Stock"
      entry = (
          f"{pid:<6} | {data['name']:<14} | {data['category']:<11} | Qty:"
          f" {data['qty']:<4} | ₹{data['price']:<8.2f} | {status}"
      )
      self.listbox.insert(tk.END, entry)

  def on_listbox_select(self, event):
    selection = self.listbox.curselection()
    if not selection:
      return
    selected_text = self.listbox.get(selection[0])
    pid = selected_text.split("|")[0].strip()
    if pid in self.inventory:
      self.var_id.set(pid)
      self.search_product()

  def clear_fields(self):
    self.var_id.set("")
    self.var_name.set("")
    self.var_qty.set("")
    self.var_price.set("")
    self.var_category.set("Electronics")
    self.var_in_stock.set(True)


if __name__ == "__main__":
  root = tk.Tk()
  app = InventoryManagementApp(root)
  root.mainloop()