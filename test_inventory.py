import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import inventory


class FakeVariable:
  def __init__(self, value=""):
    self.value = value

  def get(self):
    return self.value

  def set(self, value):
    self.value = value

  def trace_add(self, *_args):
    return None


class FakeListbox:
  def __init__(self):
    self.items = []
    self.colors = {}
    self.selection = ()

  def delete(self, _first, _last=None):
    self.items.clear()
    self.colors.clear()

  def insert(self, _index, value):
    self.items.append(value)

  def itemconfigure(self, index, **options):
    self.colors[index] = options

  def curselection(self):
    return self.selection


class InventoryLogicTests(unittest.TestCase):
  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp_dir.cleanup)
    self.app = inventory.InventoryManagementApp.__new__(inventory.InventoryManagementApp)
    self.app.data_file = Path(self.temp_dir.name) / "inventory.json"
    self.app.storage_writable = True
    self.app.startup_warning = None
    self.app.inventory = {}
    self.app.var_id = FakeVariable()
    self.app.var_name = FakeVariable()
    self.app.var_qty = FakeVariable()
    self.app.var_price = FakeVariable()
    self.app.var_category = FakeVariable("Electronics")
    self.app.var_in_stock = FakeVariable(True)
    self.app.var_name_filter = FakeVariable()
    self.app.var_category_filter = FakeVariable("All Categories")
    self.app.summary_vars = {key: FakeVariable() for key in ("products", "value", "low", "out")}
    self.app.visible_product_ids = []
    self.app.listbox = FakeListbox()
    self.dialogs = patch.multiple(
        inventory.messagebox,
        showerror=lambda *args, **kwargs: None,
        showwarning=lambda *args, **kwargs: None,
        showinfo=lambda *args, **kwargs: None,
        askyesno=lambda *args, **kwargs: True,
    )
    self.dialogs.start()
    self.addCleanup(self.dialogs.stop)

  def fill_form(self, pid="A-1", name="Keyboard", qty="8", price="1250.50"):
    self.app.var_id.set(pid)
    self.app.var_name.set(name)
    self.app.var_qty.set(qty)
    self.app.var_price.set(price)

  def test_add_product_persists_and_updates_summary(self):
    self.fill_form()
    self.app.add_product()
    self.assertEqual(self.app.inventory["A-1"]["name"], "Keyboard")
    self.assertTrue(self.app.data_file.exists())
    self.assertEqual(self.app.summary_vars["products"].get(), "1")
    self.assertEqual(self.app.summary_vars["value"].get(), "₹10,004.00")

  def test_duplicate_id_is_rejected(self):
    self.app.inventory["A-1"] = self.record()
    self.fill_form()
    self.app.add_product()
    self.assertEqual(len(self.app.inventory), 1)
    self.assertFalse(self.app.data_file.exists())

  def test_empty_id_and_name_are_rejected(self):
    for pid, name in (("", "Keyboard"), ("A-1", "   ")):
      with self.subTest(pid=pid, name=name):
        self.fill_form(pid, name)
        self.assertIsNone(self.app.validate_inputs())

  def test_invalid_quantities_are_rejected(self):
    for quantity in ("", "-1", "1.5", "1e2", "abc"):
      with self.subTest(quantity=quantity):
        self.fill_form(qty=quantity)
        self.assertIsNone(self.app.validate_inputs())

  def test_invalid_prices_are_rejected(self):
    for price in ("", "0", "-1", "nan", "inf", "-inf", "abc"):
      with self.subTest(price=price):
        self.fill_form(price=price)
        self.assertIsNone(self.app.validate_inputs())

  def test_search_valid_and_invalid_id(self):
    self.app.inventory["SKU | 7"] = self.record()
    self.app.var_id.set("SKU | 7")
    self.app.search_product()
    self.assertEqual(self.app.var_name.get(), "Keyboard")
    self.assertEqual(self.app.var_qty.get(), "3")
    self.app.var_id.set("missing")
    with patch.object(inventory.messagebox, "showinfo") as showinfo:
      self.app.search_product()
      showinfo.assert_called_once()

  def test_update_changes_quantity_price_and_availability(self):
    self.app.inventory["A-1"] = self.record()
    self.fill_form(name="Edited name", qty="2", price="1600")
    self.app.var_in_stock.set(False)
    self.app.update_product()
    saved = self.app.inventory["A-1"]
    self.assertEqual(saved["name"], "Keyboard")
    self.assertEqual(saved["qty"], 2)
    self.assertEqual(saved["price"], 1600)
    self.assertFalse(saved["in_stock"])
    self.assertEqual(self.app.summary_vars["out"].get(), "1")
    self.assertEqual(self.app.summary_vars["low"].get(), "0")
    self.assertEqual(self.app.listbox.colors[0]["foreground"], self.app.COLORS["danger"])
    self.assertFalse(self.app._load_inventory()["A-1"]["in_stock"])

  def test_update_zero_quantity_overrides_checked_availability(self):
    self.app.inventory["A-1"] = self.record(qty=8)
    self.fill_form(qty="0", price="1600")
    self.app.var_in_stock.set(True)
    self.app.update_product()
    self.assertFalse(self.app.inventory["A-1"]["in_stock"])
    self.assertEqual(self.app.summary_vars["out"].get(), "1")
    self.assertEqual(self.app.listbox.colors[0]["foreground"], self.app.COLORS["danger"])

  def test_update_available_low_stock_refreshes_summary_and_color(self):
    self.app.inventory["A-1"] = self.record(qty=9)
    self.fill_form(qty="3", price="1400")
    self.app.var_in_stock.set(True)
    self.app.update_product()
    self.assertTrue(self.app.inventory["A-1"]["in_stock"])
    self.assertEqual(self.app.summary_vars["low"].get(), "1")
    self.assertEqual(self.app.summary_vars["out"].get(), "0")
    self.assertEqual(self.app.listbox.colors[0]["foreground"], self.app.COLORS["warning"])

  def test_search_loads_saved_unavailable_state_into_checkbox(self):
    self.app.inventory["A-1"] = self.record(qty=4, in_stock=False)
    self.app.var_id.set("A-1")
    self.app.search_product()
    self.assertFalse(self.app.var_in_stock.get())

  def test_delete_requires_confirmation_and_persists(self):
    self.app.inventory["A-1"] = self.record()
    self.fill_form()
    with patch.object(inventory.messagebox, "askyesno", return_value=False):
      self.app.delete_product()
    self.assertIn("A-1", self.app.inventory)
    with patch.object(inventory.messagebox, "askyesno", return_value=True):
      self.app.delete_product()
    self.assertNotIn("A-1", self.app.inventory)
    self.assertEqual(self.app.summary_vars["products"].get(), "0")

  def test_listbox_mapping_handles_delimiters_in_product_id(self):
    pid = "SKU | special id"
    self.app.inventory[pid] = self.record()
    self.app.refresh_listbox()
    self.app.listbox.selection = (0,)
    self.app.on_listbox_select()
    self.assertEqual(self.app.var_id.get(), pid)

  def test_name_and_category_filters_do_not_modify_inventory(self):
    self.app.inventory = {
        "A": self.record(name="Blue keyboard", category="Electronics"),
        "B": self.record(name="Blue pen", category="Stationery"),
    }
    self.app.var_name_filter.set("KEYBOARD")
    self.app.var_category_filter.set("Electronics")
    self.app.refresh_listbox()
    self.assertEqual(self.app.visible_product_ids, ["A"])
    self.assertEqual(len(self.app.inventory), 2)
    self.app.show_all_products()
    self.assertEqual(self.app.visible_product_ids, ["A", "B"])

  def test_summary_and_stock_status_are_consistent(self):
    self.app.inventory = {
        "zero": self.record(qty=0, in_stock=True),
        "low": self.record(qty=4),
        "unavailable": self.record(qty=10, in_stock=False),
        "normal": self.record(qty=9),
    }
    self.app.refresh_listbox()
    self.assertEqual(self.app.summary_vars["products"].get(), "4")
    self.assertEqual(self.app.summary_vars["low"].get(), "1")
    self.assertEqual(self.app.summary_vars["out"].get(), "2")
    self.assertIn("Out of Stock", self.app.listbox.items[0])
    self.assertEqual(self.app.listbox.colors[0]["foreground"], self.app.COLORS["danger"])
    self.assertEqual(self.app.listbox.colors[1]["foreground"], self.app.COLORS["warning"])
    self.assertEqual(self.app.listbox.colors[3]["foreground"], self.app.COLORS["success"])

  def test_json_saves_and_reloads(self):
    expected = {"A-1": self.record()}
    self.assertTrue(self.app._save_inventory(expected))
    self.app.inventory = self.app._load_inventory()
    self.assertEqual(self.app.inventory, expected)

  def test_missing_json_starts_empty_and_writable(self):
    self.assertEqual(self.app._load_inventory(), {})
    self.assertTrue(self.app.storage_writable)

  def test_corrupt_json_is_preserved_and_saving_disabled(self):
    self.app.data_file.write_text("{broken", encoding="utf-8")
    original = self.app.data_file.read_text(encoding="utf-8")
    self.assertEqual(self.app._load_inventory(), {})
    self.assertFalse(self.app.storage_writable)
    self.assertFalse(self.app._save_inventory({"new": self.record()}))
    self.assertEqual(self.app.data_file.read_text(encoding="utf-8"), original)
    self.assertIn("preserved", self.app.startup_warning)

  def test_failed_save_does_not_change_live_inventory(self):
    self.fill_form()
    with patch.object(self.app, "_save_inventory", return_value=False):
      self.app.add_product()
    self.assertEqual(self.app.inventory, {})

  def test_theme_selects_a_portable_available_theme(self):
    class FakeStyle:
      def __init__(self):
        self.used = None

      def theme_names(self):
        return ("default", "clam")

      def theme_use(self, theme):
        self.used = theme

      def configure(self, *_args, **_kwargs):
        return None

      def map(self, *_args, **_kwargs):
        return None

    style = FakeStyle()
    app = inventory.InventoryManagementApp.__new__(inventory.InventoryManagementApp)
    app.root = object()
    with patch.object(inventory.ttk, "Style", return_value=style):
      app._configure_theme()
    self.assertEqual(style.used, "clam")

  @staticmethod
  def record(name="Keyboard", category="Electronics", qty=3, price=1250.50, in_stock=True):
    return {"name": name, "category": category, "qty": qty, "price": price, "in_stock": in_stock}


if __name__ == "__main__":
  unittest.main()
