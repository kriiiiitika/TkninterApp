import json
import math
import os
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


class ColorActionButton(tk.Frame):
  def __init__(self, parent, text, command, background, hover_background):
    self.normal_background = background
    self.hover_background = hover_background
    self.command = command
    super().__init__(
        parent,
        bg=background,
        height=46,
        highlightthickness=2,
        highlightbackground=background,
        highlightcolor="#0F172A",
        bd=0,
        takefocus=True,
        cursor="hand2",
    )
    self.pack_propagate(False)
    self.label = tk.Label(
        self,
        text=text,
        bg=background,
        fg="#FFFFFF",
        font=("Helvetica", 13, "bold"),
        cursor="hand2",
        takefocus=False,
    )
    self.label.pack(fill="both", expand=True)
    for widget in (self, self.label):
      widget.bind("<Enter>", self._on_enter)
      widget.bind("<Leave>", self._on_leave)
      widget.bind("<Button-1>", self._on_click)
    self.bind("<FocusIn>", self._on_focus_in)
    self.bind("<FocusOut>", self._on_focus_out)
    for key in ("<Return>", "<KP_Enter>", "<space>"):
      self.bind(key, self._on_key_activate)

  def _set_surface(self, color):
    self.configure(bg=color)
    self.label.configure(bg=color)

  def _on_enter(self, _event):
    self._set_surface(self.hover_background)

  def _on_leave(self, _event):
    self._set_surface(self.normal_background)

  def _on_focus_in(self, _event):
    self.configure(highlightbackground="#0F172A")

  def _on_focus_out(self, _event):
    self.configure(highlightbackground=self.normal_background)

  def _on_click(self, _event):
    self.focus_set()
    self._set_surface(self.hover_background)
    self.command()
    self.after(120, lambda: self._set_surface(self.normal_background))
    return "break"

  def _on_key_activate(self, _event):
    self._set_surface(self.hover_background)
    self.command()
    self.after(120, lambda: self._set_surface(self.normal_background))
    return "break"


class InventoryManagementApp:
  CATEGORIES = ("Electronics", "Groceries", "Apparel", "Stationery", "Furniture", "Other")
  COLORS = {
      "background": "#EEF4FF",
      "header": "#1E3A8A",
      "primary": "#2563EB",
      "card": "#FFFFFF",
      "text": "#0F172A",
      "secondary": "#64748B",
      "border": "#E2E8F0",
      "success": "#16A34A",
      "warning": "#F59E0B",
      "danger": "#DC2626",
  }

  def __init__(self, root, data_file=None):
    self.root = root
    self.root.title("StockFlow | Product Inventory Management System")
    screen_width = self.root.winfo_screenwidth()
    screen_height = self.root.winfo_screenheight()
    width = max(500, screen_width - 64)
    height = max(420, screen_height - 112)
    min_width = min(760, max(500, screen_width - 24))
    min_height = min(620, max(420, screen_height - 80))
    self.root.geometry(f"{width}x{height}+32+32")
    self.root.minsize(min_width, min_height)
    self.root.configure(bg=self.COLORS["background"])
    self.data_file = Path(data_file) if data_file else Path(__file__).resolve().with_name("inventory.json")
    self.storage_writable = True
    self.startup_warning = None
    self.inventory = self._load_inventory()

    self.var_id = tk.StringVar()
    self.var_name = tk.StringVar()
    self.var_qty = tk.StringVar()
    self.var_price = tk.StringVar()
    self.var_category = tk.StringVar(value=self.CATEGORIES[0])
    self.var_in_stock = tk.BooleanVar(value=True)
    self.var_name_filter = tk.StringVar()
    self.var_category_filter = tk.StringVar(value="All Categories")
    self.summary_vars = {
        "products": tk.StringVar(value="0"),
        "value": tk.StringVar(value="₹0.00"),
        "low": tk.StringVar(value="0"),
        "out": tk.StringVar(value="0"),
    }
    self.visible_product_ids = []
    self.summary_cards = []
    self._compact_layout = None
    self._scrollbar_visible = False

    self._configure_theme()
    self.setup_ui()
    self.refresh_listbox()
    if self.startup_warning:
      self.root.after(150, lambda: messagebox.showwarning("Inventory data", self.startup_warning))

  def _configure_theme(self):
    style = ttk.Style(self.root)
    themes = style.theme_names()
    if "clam" in themes:
      style.theme_use("clam")
    elif themes:
      style.theme_use(themes[0])
    style.configure("TFrame", background=self.COLORS["background"])
    style.configure("TLabel", background=self.COLORS["background"], foreground=self.COLORS["text"], font=("Helvetica", 12))
    style.configure("Panel.TFrame", background=self.COLORS["card"], relief="solid", borderwidth=1)
    style.configure("Panel.TLabel", background=self.COLORS["card"], foreground=self.COLORS["text"], font=("Helvetica", 12))
    style.configure("Muted.Panel.TLabel", background=self.COLORS["card"], foreground=self.COLORS["secondary"], font=("Helvetica", 11))
    style.configure("Title.Panel.TLabel", background=self.COLORS["card"], foreground=self.COLORS["text"], font=("Helvetica", 17, "bold"))
    style.configure("TEntry", padding=10, fieldbackground=self.COLORS["card"], font=("Helvetica", 13))
    style.configure("TMenubutton", padding=9, font=("Helvetica", 12))
    style.configure("TCheckbutton", background=self.COLORS["card"], foreground=self.COLORS["text"], font=("Helvetica", 12))
    button_styles = {
        "Primary.TButton": (self.COLORS["primary"], "white"),
        "Warning.TButton": (self.COLORS["warning"], "#FFFFFF"),
        "Danger.TButton": (self.COLORS["danger"], "white"),
        "Neutral.TButton": (self.COLORS["card"], self.COLORS["text"]),
    }
    for name, (background, foreground) in button_styles.items():
      style.configure(name, background=background, foreground=foreground, padding=(12, 11), font=("Helvetica", 13, "bold"), borderwidth=0)
      style.map(name, background=[("active", self.COLORS["header"]), ("pressed", self.COLORS["header"])])
    style.map(
      "Warning.TButton",
      background=[("pressed", "#D97706"), ("active", "#D97706")],
      foreground=[("pressed", "#FFFFFF"), ("active", "#FFFFFF")],
    )
    style.configure("TLabelFrame", background=self.COLORS["card"], foreground=self.COLORS["text"])
    style.configure("TLabelFrame.Label", background=self.COLORS["card"], foreground=self.COLORS["text"], font=("Helvetica", 16, "bold"))

  def setup_ui(self):
    self.root.rowconfigure(0, weight=1)
    self.root.columnconfigure(0, weight=1)
    self.page_canvas = tk.Canvas(self.root, bg=self.COLORS["background"], highlightthickness=0)
    self.page_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.page_canvas.yview)
    self.page_canvas.configure(yscrollcommand=self.page_scrollbar.set)
    self.page_canvas.grid(row=0, column=0, sticky="nsew")
    self.page = ttk.Frame(self.page_canvas, padding=(18, 14, 18, 14))
    self.page_window = self.page_canvas.create_window((0, 0), window=self.page, anchor="nw")
    self.page.columnconfigure(0, weight=1)
    self.page.rowconfigure(2, weight=1)
    self.page.bind("<Configure>", self._sync_page_geometry)
    self.page_canvas.bind("<Configure>", self._sync_page_geometry)
    self.root.bind("<MouseWheel>", self._on_mousewheel)
    self.root.bind("<Button-4>", lambda _event: self.page_canvas.yview_scroll(-1, "units"))
    self.root.bind("<Button-5>", lambda _event: self.page_canvas.yview_scroll(1, "units"))

    self._build_header()
    self._build_summary()
    self._build_main()
    self.root.after_idle(self.entry_id.focus_set)

  def _build_header(self):
    header = tk.Frame(self.page, bg=self.COLORS["header"], padx=22, pady=14)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
    brand = tk.Frame(header, bg=self.COLORS["header"])
    brand.pack(anchor="w")
    icon = tk.Canvas(brand, width=38, height=38, bg=self.COLORS["header"], highlightthickness=0)
    icon.pack(side="left", padx=(0, 12))
    icon.create_rectangle(7, 11, 31, 31, outline="#BFDBFE", width=2)
    icon.create_line(7, 16, 19, 22, 31, 16, fill="#BFDBFE", width=2)
    icon.create_line(19, 22, 19, 31, fill="#BFDBFE", width=2)
    title = tk.Frame(brand, bg=self.COLORS["header"])
    title.pack(side="left", anchor="w")
    tk.Label(title, text="StockFlow", bg=self.COLORS["header"], fg="white", font=("Helvetica", 28, "bold")).pack(anchor="w")
    tk.Label(title, text="Product Inventory Management System", bg=self.COLORS["header"], fg="#DBEAFE", font=("Helvetica", 13)).pack(anchor="w", pady=(0, 1))

  def _build_summary(self):
    self.summary_frame = ttk.Frame(self.page)
    self.summary_frame.grid(row=1, column=0, sticky="ew", pady=(0, 14))
    cards = (
        ("Total Products", "products", self.COLORS["primary"]),
        ("Inventory Value", "value", self.COLORS["success"]),
        ("Low Stock (1-5)", "low", self.COLORS["warning"]),
        ("Out of Stock", "out", self.COLORS["danger"]),
    )
    for title, key, accent in cards:
      card = tk.Frame(self.summary_frame, bg=self.COLORS["card"], height=112, highlightthickness=1, highlightbackground=self.COLORS["border"], padx=16, pady=13)
      card.pack_propagate(False)
      tk.Frame(card, bg=accent, width=4).pack(side="left", fill="y", padx=(0, 12))
      details = tk.Frame(card, bg=self.COLORS["card"])
      details.pack(side="left", fill="both", expand=True)
      ttk.Label(details, text=title, style="Muted.Panel.TLabel", font=("Helvetica", 12)).pack(anchor="w")
      ttk.Label(details, textvariable=self.summary_vars[key], style="Title.Panel.TLabel", font=("Helvetica", 25, "bold")).pack(anchor="w", pady=(3, 0))
      self.summary_cards.append(card)

  def _build_main(self):
    self.main_frame = ttk.Frame(self.page)
    self.main_frame.grid(row=2, column=0, sticky="nsew")
    self.main_frame.rowconfigure(0, weight=1)
    self.form_frame = ttk.Frame(self.main_frame, style="Panel.TFrame", padding=18)
    self.inventory_frame = ttk.Frame(self.main_frame, style="Panel.TFrame", padding=18)
    self._build_form()
    self._build_inventory_panel()

  def _build_form(self):
    form = self.form_frame
    form.columnconfigure(1, weight=1)
    ttk.Label(form, text="Product Details", style="Title.Panel.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 3))
    ttk.Label(form, text="Fields marked * are required", style="Muted.Panel.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
    fields = (("Product ID *", self.var_id), ("Product Name *", self.var_name), ("Quantity *", self.var_qty), ("Unit Price (₹) *", self.var_price))
    self.form_entries = []
    for row, (label, variable) in enumerate(fields, start=2):
      ttk.Label(form, text=label, style="Panel.TLabel", font=("Helvetica", 13)).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 12))
      entry = self._create_input_entry(form, variable)
      entry.grid(row=row, column=1, sticky="ew", pady=4, ipady=6)
      self.form_entries.append(entry)
    self.entry_id = self.form_entries[0]
    ttk.Label(form, text="Category", style="Panel.TLabel", font=("Helvetica", 13)).grid(row=6, column=0, sticky="w", pady=4, padx=(0, 12))
    ttk.OptionMenu(form, self.var_category, self.CATEGORIES[0], *self.CATEGORIES).grid(row=6, column=1, sticky="ew", pady=4)
    self._stock_images = {
      False: self._create_stock_indicator(False),
      True: self._create_stock_indicator(True),
    }
    self.stock_checkbutton = tk.Checkbutton(
      form,
      text="Available in stock",
      variable=self.var_in_stock,
      image=self._stock_images[bool(self.var_in_stock.get())],
      compound="left",
      indicatoron=0,
      command=self._sync_stock_indicator,
      anchor="w",
      font=("Helvetica", 12),
      fg=self.COLORS["text"],
      bg=self.COLORS["card"],
      activeforeground=self.COLORS["text"],
      activebackground=self.COLORS["card"],
      selectcolor=self.COLORS["card"],
      relief="flat",
      bd=0,
      padx=0,
      pady=3,
      highlightthickness=1,
      highlightbackground=self.COLORS["card"],
      highlightcolor=self.COLORS["primary"],
      cursor="hand2",
    )
    self.stock_checkbutton.grid(row=7, column=0, columnspan=2, sticky="w", pady=(7, 9))
    self.var_in_stock.trace_add("write", self._sync_stock_indicator)
    buttons = tk.Frame(form, bg=self.COLORS["card"], bd=0, highlightthickness=0)
    buttons.grid(row=8, column=0, columnspan=2, sticky="ew")
    buttons.columnconfigure(0, weight=1, uniform="actions", minsize=120)
    buttons.columnconfigure(1, weight=1, uniform="actions", minsize=120)
    actions = (
        ("Add Product", self.add_product, "#2563EB", "#1D4ED8"),
        ("Search by ID", self.search_product, "#1E40AF", "#3B82F6"),
        ("Update Qty/Price", self.update_product, "#F59E0B", "#D97706"),
        ("Delete Product", self.delete_product, "#DC2626", "#B91C1C"),
    )
    self.action_buttons = []
    for index, (text, command, background, hover_background) in enumerate(actions):
      button = ColorActionButton(buttons, text, command, background, hover_background)
      button.grid(row=index // 2, column=index % 2, sticky="ew", padx=6, pady=6)
      self.action_buttons.append(button)
    clear_button = ColorActionButton(buttons, "Clear Fields", self.clear_fields, "#64748B", "#475569")
    clear_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
    self.action_buttons.append(clear_button)

  def _create_input_entry(self, parent, variable):
    return tk.Entry(
        parent,
        textvariable=variable,
        font=("Helvetica", 13),
        bg=self.COLORS["card"],
        fg=self.COLORS["text"],
        insertwidth=2,
        insertbackground=self.COLORS["text"],
        cursor="xterm",
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=self.COLORS["border"],
        highlightcolor=self.COLORS["primary"],
    )

  def _create_stock_indicator(self, checked):
    size = 22
    image = tk.PhotoImage(master=self.root, width=size, height=size)
    image.put(self.COLORS["card"], to=(0, 0, size, size))
    border = self.COLORS["secondary"]
    for offset in range(size):
      image.put(border, to=(offset, 0))
      image.put(border, to=(offset, size - 1))
      image.put(border, to=(0, offset))
      image.put(border, to=(size - 1, offset))
    if checked:
      self._draw_indicator_line(image, (5, 11), (9, 15))
      self._draw_indicator_line(image, (9, 15), (17, 6))
    return image

  @staticmethod
  def _draw_indicator_line(image, start, end):
    x_start, y_start = start
    x_end, y_end = end
    steps = max(abs(x_end - x_start), abs(y_end - y_start))
    for step in range(steps + 1):
      fraction = step / steps
      x = round(x_start + (x_end - x_start) * fraction)
      y = round(y_start + (y_end - y_start) * fraction)
      for x_offset in (0, 1):
        for y_offset in (0, 1):
          image.put("#1E3A8A", to=(x + x_offset, y + y_offset))

  def _sync_stock_indicator(self, *_args):
    if hasattr(self, "stock_checkbutton"):
      self.stock_checkbutton.configure(image=self._stock_images[bool(self.var_in_stock.get())])

  def _build_inventory_panel(self):
    panel = self.inventory_frame
    panel.columnconfigure(0, weight=1)
    panel.rowconfigure(4, weight=0)
    ttk.Label(panel, text="Inventory", style="Title.Panel.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(panel, text="Select a row to load its product details", style="Muted.Panel.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 10))
    ttk.Label(panel, text="Filter by product name or category", style="Muted.Panel.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 5))
    filters = ttk.Frame(panel, style="Panel.TFrame")
    filters.grid(row=3, column=0, sticky="ew", pady=(0, 8))
    filters.columnconfigure(0, weight=1)
    self.entry_name_filter = self._create_input_entry(filters, self.var_name_filter)
    self.entry_name_filter.grid(row=0, column=0, sticky="ew", padx=(0, 6), ipady=5)
    self.var_name_filter.trace_add("write", lambda *_args: self.refresh_listbox())
    ttk.OptionMenu(filters, self.var_category_filter, "All Categories", "All Categories", *self.CATEGORIES, command=lambda _value: self.refresh_listbox()).grid(row=0, column=1, padx=4)
    ttk.Button(filters, text="Show All", command=self.show_all_products, style="Neutral.TButton").grid(row=0, column=2, padx=(4, 0))
    heading = f"{'PRODUCT ID':<13}{'NAME':<22}{'CATEGORY':<13}{'QUANTITY':>8}  {'PRICE':>13}  {'STATUS':<14}"
    self.column_header = tk.Canvas(panel, height=34, width=1, bg=self.COLORS["card"], highlightthickness=0)
    self.column_header.create_text(8, 7, text=heading, anchor="nw", fill=self.COLORS["secondary"], font=("Menlo", 13, "bold"))
    header_bounds = self.column_header.bbox("all")
    self.column_header.configure(scrollregion=(0, 0, header_bounds[2] + 8, 34))
    self.column_header.grid(row=4, column=0, sticky="ew", pady=(2, 0))
    self.listbox = tk.Listbox(panel, font=("Menlo", 14), bg="white", fg=self.COLORS["text"], selectbackground=self.COLORS["primary"], selectforeground="white", activestyle="none", height=10, width=1, relief="solid", borderwidth=1, highlightthickness=0, exportselection=False)
    self.listbox.grid(row=5, column=0, sticky="nsew")
    self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)
    vertical = ttk.Scrollbar(panel, orient="vertical", command=self.listbox.yview)
    vertical.grid(row=5, column=1, sticky="ns")
    horizontal = ttk.Scrollbar(panel, orient="horizontal", command=self._scroll_inventory_horizontally)
    horizontal.grid(row=6, column=0, sticky="ew")
    self.inventory_horizontal = horizontal
    self.listbox.configure(yscrollcommand=vertical.set, xscrollcommand=self._sync_inventory_header)
    self.empty_state = tk.Label(self.listbox, text="", bg="white", fg=self.COLORS["secondary"], font=("Helvetica", 14), justify="center")
    self.empty_state.place(relx=0.5, rely=0.5, anchor="center")
    panel.rowconfigure(5, weight=1)

  def _scroll_inventory_horizontally(self, *args):
    self.listbox.xview(*args)
    self.column_header.xview(*args)

  def _sync_inventory_header(self, first, last):
    self.inventory_horizontal.set(first, last)
    self.column_header.xview_moveto(first)

  def _sync_page_geometry(self, event=None):
    canvas_width = max(1, self.page_canvas.winfo_width())
    canvas_height = max(1, self.page_canvas.winfo_height())
    self.page_canvas.itemconfigure(self.page_window, width=canvas_width)
    self._apply_responsive_layout(canvas_width)
    self.page.update_idletasks()
    content_height = self.page.winfo_reqheight()
    self.page_canvas.itemconfigure(self.page_window, height=max(canvas_height, content_height))
    self.page_canvas.configure(scrollregion=(0, 0, canvas_width, max(canvas_height, content_height)))
    needs_scroll = content_height > canvas_height + 2
    if needs_scroll != self._scrollbar_visible:
      self._scrollbar_visible = needs_scroll
      if needs_scroll:
        self.page_scrollbar.grid(row=0, column=1, sticky="ns")
      else:
        self.page_scrollbar.grid_remove()

  def _apply_responsive_layout(self, width):
    compact = width < 1040
    if compact == self._compact_layout:
      return
    self._compact_layout = compact
    for card in self.summary_cards:
      card.grid_forget()
    for column in range(4):
      self.summary_frame.columnconfigure(column, weight=0)
    if width >= 1160:
      for column, card in enumerate(self.summary_cards):
        self.summary_frame.columnconfigure(column, weight=1, uniform="summary")
        card.grid(row=0, column=column, sticky="ew", padx=(0, 10) if column < 3 else 0)
    else:
      for column in range(2):
        self.summary_frame.columnconfigure(column, weight=1, uniform="summary")
      for index, card in enumerate(self.summary_cards):
        card.grid(row=index // 2, column=index % 2, sticky="ew", padx=(0, 8) if index % 2 == 0 else 0, pady=(0, 8) if index < 2 else 0)
    self.form_frame.grid_forget()
    self.inventory_frame.grid_forget()
    self.main_frame.columnconfigure(0, weight=0, uniform="")
    self.main_frame.columnconfigure(1, weight=0, uniform="")
    if not compact:
      self.main_frame.columnconfigure(0, weight=4, uniform="panels")
      self.main_frame.columnconfigure(1, weight=6, uniform="panels")
      self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
      self.inventory_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    else:
      self.main_frame.columnconfigure(0, weight=1)
      self.main_frame.rowconfigure(0, weight=0)
      self.main_frame.rowconfigure(1, weight=1)
      self.form_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
      self.inventory_frame.grid(row=1, column=0, sticky="nsew")
    if not compact:
      self.main_frame.rowconfigure(0, weight=1)
      self.main_frame.rowconfigure(1, weight=0)

  def _on_mousewheel(self, event):
    if getattr(event, "delta", 0):
      self.page_canvas.yview_scroll(int(-event.delta / 120), "units")

  def _load_inventory(self):
    if not self.data_file.exists():
      return {}
    try:
      with self.data_file.open("r", encoding="utf-8") as data_file:
        raw_data = json.load(data_file)
      if not isinstance(raw_data, dict):
        raise ValueError("The inventory JSON root must be an object.")
      inventory = {}
      for pid, item in raw_data.items():
        if not isinstance(pid, str) or not pid.strip() or not isinstance(item, dict):
          raise ValueError("An inventory record has an invalid ID or format.")
        name = item["name"]
        category = item["category"]
        qty = item["qty"]
        price = float(item["price"])
        in_stock = item["in_stock"]
        if (not isinstance(name, str) or not name.strip() or category not in self.CATEGORIES
            or isinstance(qty, bool) or not isinstance(qty, int) or qty < 0
            or not math.isfinite(price) or price <= 0 or not isinstance(in_stock, bool)):
          raise ValueError(f"Product '{pid}' contains invalid data.")
        inventory[pid] = {"name": name.strip(), "category": category, "qty": qty, "price": price, "in_stock": in_stock and qty > 0}
      return inventory
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
      self.storage_writable = False
      self.startup_warning = f"Could not load {self.data_file.name}: {error}\nThe file has been preserved, and saving is disabled to protect its contents."
      return {}

  def _save_inventory(self, inventory):
    if not self.storage_writable:
      messagebox.showerror("Save unavailable", "Inventory was not changed because the existing data file could not be loaded safely.")
      return False
    temporary_path = None
    try:
      self.data_file.parent.mkdir(parents=True, exist_ok=True)
      with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.data_file.parent, prefix=f".{self.data_file.name}.", suffix=".tmp", delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)
        json.dump(inventory, temporary_file, ensure_ascii=False, indent=2, allow_nan=False)
        temporary_file.write("\n")
        temporary_file.flush()
        os.fsync(temporary_file.fileno())
      os.replace(temporary_path, self.data_file)
      return True
    except (OSError, TypeError, ValueError) as error:
      messagebox.showerror("Save failed", f"Inventory was not changed because it could not be saved:\n{error}")
      return False
    finally:
      if temporary_path and temporary_path.exists():
        try:
          temporary_path.unlink()
        except OSError:
          pass

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
      if not qty_str or any(character in qty_str for character in ".eE"):
        raise ValueError
      qty = int(qty_str)
      if qty < 0:
        raise ValueError
    except ValueError:
      messagebox.showerror("Validation Error", "Quantity must be a non-negative integer (0 or more).")
      return None
    try:
      price = float(price_str)
      if not math.isfinite(price) or price <= 0:
        raise ValueError
    except ValueError:
      messagebox.showerror("Validation Error", "Unit Price must be a finite number greater than 0.")
      return None
    if self.var_category.get() not in self.CATEGORIES:
      messagebox.showerror("Validation Error", "Select a valid product category.")
      return None
    return pid, name, qty, price

  def add_product(self):
    validated = self.validate_inputs(check_name=True)
    if not validated:
      return
    pid, name, qty, price = validated
    if pid in self.inventory:
      messagebox.showwarning("Duplicate ID", f"Product ID '{pid}' already exists. Use 'Update Qty/Price' instead.")
      return
    candidate = dict(self.inventory)
    candidate[pid] = {"name": name, "category": self.var_category.get(), "qty": qty, "price": price, "in_stock": self.var_in_stock.get() and qty > 0}
    if not self._save_inventory(candidate):
      return
    self.inventory = candidate
    self.refresh_listbox()
    self.clear_fields()
    messagebox.showinfo("Success", f"Product '{name}' added successfully.")

  def search_product(self):
    pid = self.var_id.get().strip()
    if not pid:
      messagebox.showwarning("Input Required", "Enter a Product ID to search.")
      return
    item = self.inventory.get(pid)
    if item is None:
      messagebox.showinfo("Not Found", f"No product found with ID '{pid}'.")
      return
    self._populate_fields(pid, item)

  def _populate_fields(self, pid, item):
    self.var_id.set(pid)
    self.var_name.set(item["name"])
    self.var_category.set(item["category"])
    self.var_qty.set(str(item["qty"]))
    self.var_price.set(str(item["price"]))
    self.var_in_stock.set(item["in_stock"] and item["qty"] > 0)

  def update_product(self):
    pid = self.var_id.get().strip()
    if not pid:
      messagebox.showwarning("Input Required", "Enter the Product ID to update.")
      return
    if pid not in self.inventory:
      messagebox.showerror("Not Found", f"Product ID '{pid}' does not exist.")
      return
    validated = self.validate_inputs(check_name=False)
    if not validated:
      return
    _, _, qty, price = validated
    candidate = dict(self.inventory)
    candidate[pid] = dict(self.inventory[pid], qty=qty, price=price, in_stock=self.var_in_stock.get() and qty > 0)
    if not self._save_inventory(candidate):
      return
    self.inventory = candidate
    self.refresh_listbox()
    messagebox.showinfo("Updated", f"Quantity and price updated for '{pid}'.")

  def delete_product(self):
    pid = self.var_id.get().strip()
    if not pid:
      messagebox.showwarning("Input Required", "Enter or select a Product ID to delete.")
      return
    if pid not in self.inventory:
      messagebox.showerror("Not Found", f"Product ID '{pid}' does not exist.")
      return
    if not messagebox.askyesno("Confirm Delete", f"Delete product '{pid}'?"):
      return
    candidate = dict(self.inventory)
    del candidate[pid]
    if not self._save_inventory(candidate):
      return
    self.inventory = candidate
    self.refresh_listbox()
    self.clear_fields()
    messagebox.showinfo("Deleted", f"Product '{pid}' removed.")

  def refresh_listbox(self):
    self.listbox.delete(0, tk.END)
    self.visible_product_ids = []
    name_filter = self.var_name_filter.get().strip().casefold()
    category_filter = self.var_category_filter.get()
    for pid, data in self.inventory.items():
      if name_filter and name_filter not in data["name"].casefold():
        continue
      if category_filter != "All Categories" and data["category"] != category_filter:
        continue
      status = "In Stock" if data["in_stock"] and data["qty"] > 0 else "Out of Stock"
      entry = self._format_inventory_row(pid, data, status)
      row = len(self.visible_product_ids)
      self.visible_product_ids.append(pid)
      self.listbox.insert(tk.END, entry)
      if status == "Out of Stock":
        color = self.COLORS["danger"]
      elif data["qty"] <= 5:
        color = self.COLORS["warning"]
      else:
        color = self.COLORS["success"]
      self.listbox.itemconfigure(row, foreground=color)
    if hasattr(self, "empty_state"):
      if self.visible_product_ids:
        self.empty_state.place_forget()
      elif self.inventory:
        self.empty_state.configure(text="No matching products found.")
        self.empty_state.place(relx=0.5, rely=0.5, anchor="center")
        self.empty_state.lift()
      else:
        self.empty_state.configure(text="No products yet\nAdd your first product to start managing inventory.")
        self.empty_state.place(relx=0.5, rely=0.5, anchor="center")
        self.empty_state.lift()
    self._update_summary()

  @staticmethod
  def _format_inventory_row(pid, data, status):
    def fit(value, width):
      value = str(value)
      return value if len(value) <= width else value[:width - 1] + "…"

    return (
      f"{fit(pid, 12):<13}{fit(data['name'], 21):<22}"
      f"{fit(data['category'], 12):<13}{data['qty']:>8}  "
      f"₹{data['price']:>12,.2f}  {status:<14}"
    )

  def _update_summary(self):
    total_value = sum(item["qty"] * item["price"] for item in self.inventory.values())
    low_stock = sum(1 for item in self.inventory.values() if item["in_stock"] and 1 <= item["qty"] <= 5)
    out_of_stock = sum(1 for item in self.inventory.values() if item["qty"] == 0 or not item["in_stock"])
    self.summary_vars["products"].set(str(len(self.inventory)))
    self.summary_vars["value"].set(f"₹{total_value:,.2f}")
    self.summary_vars["low"].set(str(low_stock))
    self.summary_vars["out"].set(str(out_of_stock))

  def on_listbox_select(self, event=None):
    selection = self.listbox.curselection()
    if not selection:
      return
    row = selection[0]
    if 0 <= row < len(self.visible_product_ids):
      pid = self.visible_product_ids[row]
      item = self.inventory.get(pid)
      if item:
        self._populate_fields(pid, item)

  def show_all_products(self):
    self.var_name_filter.set("")
    self.var_category_filter.set("All Categories")
    self.refresh_listbox()

  def clear_fields(self):
    self.var_id.set("")
    self.var_name.set("")
    self.var_qty.set("")
    self.var_price.set("")
    self.var_category.set(self.CATEGORIES[0])
    self.var_in_stock.set(True)
    if hasattr(self, "entry_id"):
      self.entry_id.focus_set()


if __name__ == "__main__":
  root = tk.Tk()
  app = InventoryManagementApp(root)
  root.mainloop()