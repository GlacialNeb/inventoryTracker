from pathlib import Path
from datetime import datetime
import json
import curses
import atexit

# https://stackoverflow.com/questions/39488788/how-to-make-a-menu-in-python-navigable-with-arrow-keys
# really cool forum post about interactive menus using curses in python, curses carried this app

# ---------------------------- INFO ----------------------------
# data files are stored in the same directory as the app file,
# they're json files because txt probably isn't the best idea.
# data gets saved as soon as the user exits the app.
# baskets are calculated by using min on the quantities of all
# items that are labeled as basket items. as for the top/bottom 5
# basket items, they use a lambda function to sort the items by
# quantity and then slice the first 5 items from the sorted list.
# ties are broken by sorting the items alphabetically.
# everything else is fairly organized and self-explanatory.

inventory_path = Path(__file__).with_name("inventory.json")
transactions_path = Path(__file__).with_name("transactions.json")

# hard-coded
default_inventory = {
    "Frozen Ham": {"Quantity": 0, "Value": 50, "Basket": True},
    "Frozen Turkey": {"Quantity": 0, "Value": 50, "Basket": True},
    "Canned Yams": {"Quantity": 0, "Value": 5, "Basket": True},
    "Canned Corn": {"Quantity": 0, "Value": 5, "Basket": True},
    "Canned Green Beans": {"Quantity": 0, "Value": 5, "Basket": True},
    "Canned Carrots": {"Quantity": 0, "Value": 5, "Basket": True},
    "Canned Peas": {"Quantity": 0, "Value": 5, "Basket": True},
    "Canned Fruit": {"Quantity": 0, "Value": 5, "Basket": True},
    "Canned Pumpkin": {"Quantity": 0, "Value": 5, "Basket": True},
    "Canned Milk": {"Quantity": 0, "Value": 5, "Basket": True},
    "Instant Mashed Potatoes": {"Quantity": 0, "Value": 8, "Basket": True},
    "Potatoes": {"Quantity": 0, "Value": 5, "Basket": True},
    "Sugar": {"Quantity": 0, "Value": 15, "Basket": True},
    "Flour": {"Quantity": 0, "Value": 10, "Basket": True},
    "Cranberry Sauce": {"Quantity": 0, "Value": 5, "Basket": True},
    "Pie Crust": {"Quantity": 0, "Value": 8, "Basket": True},
    "Pie Filling": {"Quantity": 0, "Value": 5, "Basket": True},
    "Stuffing Mix": {"Quantity": 0, "Value": 10, "Basket": True},
    "Gravy Mix": {"Quantity": 0, "Value": 1, "Basket": True},
    "Bread Mix": {"Quantity": 0, "Value": 5, "Basket": True},
    "Cookie Mix": {"Quantity": 0, "Value": 5, "Basket": True},
    "Cake Mix and Icing": {"Quantity": 0, "Value": 5, "Basket": True},
    "Cooking Oil": {"Quantity": 0, "Value": 8, "Basket": True},
    "Mac n Cheese": {"Quantity": 0, "Value": 2, "Basket": True},
    "Canned Meats": {"Quantity": 0, "Value": 10, "Basket": False},
    "Peanut Butter": {"Quantity": 0, "Value": 8, "Basket": False},
    "Boxed Meal Kits": {"Quantity": 0, "Value": 5, "Basket": False},
    "Canned Soup": {"Quantity": 0, "Value": 5, "Basket": False},
    "Quick Meals": {"Quantity": 0, "Value": 1, "Basket": False}
}

# load inventory
try:
    if inventory_path.is_file():
        inventory = json.loads(inventory_path.read_text())
    else:
        inventory = default_inventory.copy()
except (json.JSONDecodeError, OSError):
    inventory = default_inventory.copy()
    
# load transactions
try:
    if transactions_path.is_file():
        transactions = json.loads(transactions_path.read_text())
    else:
        transactions = []
except (json.JSONDecodeError, OSError):
    transactions = []

# primary functions
def on_exit():
    inventory_path.write_text(json.dumps(inventory))
    transactions_path.write_text(json.dumps(transactions))
    
def get_input(stdscr):
    characters = []
    while True:
        key = stdscr.getch()
        if key == 27:
            return None
        if key in (curses.KEY_ENTER, 10, 13):
            return ''.join(characters)
        if key in (curses.KEY_BACKSPACE, 8, 127):
            if characters:
                characters.pop()
                stdscr.addstr("\b \b")
        elif 32 <= key <= 126:
            characters.append(chr(key))
            stdscr.addch(key)

def transaction(message):
    date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    transactions.append("{} | {}\n".format(date, message))

def show_message(stdscr, message=None):
    if message is not None:
        stdscr.addstr("\n" + message)
    stdscr.addstr("\nPress any key to return.")
    stdscr.refresh()
    stdscr.getch()

def edit_item_number(stdscr, item_name, item_content, field):
    stdscr.erase()
    stdscr.addstr("Edit {}\nPress ESC to cancel\n\nEnter new {}: ".format(field, field.lower()))
    stdscr.refresh()
    value_text = get_input(stdscr)
    try:
        value = int(value_text)
        if value < 0:
            raise ValueError
    except ValueError:
        show_message(stdscr, "Please enter a non-negative integer.")
        return
    item_content[field] = value
    transaction("Updated {} for {} to {}".format(field.lower(), item_name, value))
    show_message(stdscr, "{} updated successfully.".format(field))


def edit_item_basket_status(stdscr, item_name, item_content):
    stdscr.erase()
    stdscr.addstr("Edit Basket Status\nPress ESC to cancel\n\nIs this item in baskets? (y/n): ")
    stdscr.refresh()
    answer = get_input(stdscr)
    if answer not in ("y", "n"):
        show_message(stdscr, "Please enter 'y' or 'n'.")
        return
    item_content["Basket"] = answer == "y"
    transaction("Updated basket status for {} to {}".format(item_name, item_content["Basket"]))
    show_message(stdscr, "Basket status updated successfully.")


def delete_item(stdscr, item_name):
    stdscr.erase()
    stdscr.addstr("Delete Item\nPress ESC to cancel\n\nDelete {}? (y/n): ".format(item_name))
    stdscr.refresh()
    answer = get_input(stdscr)
    if answer is None or answer != "y":
        return
    del inventory[item_name]
    transaction("Deleted item: {}".format(item_name))
    show_message(stdscr, "Item deleted successfully.")
    
def item_options(stdscr, item_name, item_content):
    options = [
        "Edit Quantity",
        "Edit Value",
        "Edit Basket Status",
        "Delete Item"
    ]
    selected = 0

    while True:
        stdscr.erase()
        stdscr.addstr("Item Options\n\n")
        stdscr.addstr("Use arrow keys to navigate, Enter to select. ESC to return.\n\n")
        for index, option in enumerate(options):
            attribute = curses.color_pair(2) if index == selected else curses.color_pair(1)
            stdscr.addstr("{}. {}\n".format(index + 1, option), attribute)
        stdscr.refresh()

        key = stdscr.getch()
        if key == 27:
            return
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            if selected == 0:
                edit_item_number(stdscr, item_name, item_content, "Quantity")
            elif selected == 1:
                edit_item_number(stdscr, item_name, item_content, "Value")
            elif selected == 2:
                edit_item_basket_status(stdscr, item_name, item_content)
            else:
                delete_item(stdscr, item_name)
            return

def view_inventory(stdscr):
    list_items(stdscr, inventory, "Food Drive Inventory")

def search_inventory(stdscr):
    stdscr.clear()
    stdscr.addstr("Search Inventory\nPress ESC to cancel\n\nEnter item name to search: ")
    stdscr.refresh()
    search_term = get_input(stdscr)
    if search_term is None:
        return

    found_items = {name: content for name, content in inventory.items() if search_term.lower() in name.lower()}

    stdscr.clear()
    if found_items:
        list_items(stdscr, found_items, "Search Results")
    else:
        stdscr.addstr("Search Results\n\n")
        show_message(stdscr, "No items found.")

def list_items(stdscr, items, title):
    items_to_list = dict(sorted(items.items(), key=lambda x: (-x[1]['Quantity'], x[0])))
    attributes = {}
    
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    attributes['normal'] = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    attributes['highlighted'] = curses.color_pair(2)
    
    c = 0
    option = 0
    first_item = 0
    while c != 10 and c != 27:
        stdscr.erase()
        stdscr.addstr(title + '\n')
        stdscr.addstr("Use arrow keys to navigate, Enter to select. ESC to return.\n\n")
        if title == "Food Drive Inventory":
            stdscr.addstr("Grand total: {} points and {} items\n".format(int(sum(item['Quantity'] * item['Value'] for item in inventory.values())), sum(item['Quantity'] for item in inventory.values())))
        height, width = stdscr.getmaxyx()
        visible_items = max(1, height - 6)
        first_item = min(first_item, max(0, len(items_to_list) - visible_items))
        last_item = min(first_item + visible_items, len(items_to_list))
        for i in range(first_item, last_item):
            item_name, item_content = list(items_to_list.items())[i]
            if i == option:
                attr = attributes['highlighted']
            else:
                attr = attributes['normal']
            line = "{}. {} | Quantity: {} | Value: {} | Total Value: {} | In Basket: {}".format(i + 1, item_name, item_content['Quantity'], item_content['Value'], item_content['Quantity'] * item_content['Value'], "Yes" if item_content['Basket'] else "No")
            stdscr.addnstr(line, max(0, width - 1), attr)
            if i < last_item - 1:
                stdscr.addstr("\n")
        c = stdscr.getch()
        if c == curses.KEY_UP and option > 0:
            option -= 1
            if option < first_item:
                first_item = option
        elif c == curses.KEY_DOWN and option < len(items_to_list) - 1:
            option += 1
            if option >= first_item + visible_items:
                first_item = option - visible_items + 1
    if c != 27 and len(items_to_list) > 0:
        item_name, item_content = list(items_to_list.items())[option]
        item_options(stdscr, item_name, item_content)

def add_item(stdscr):
    stdscr.clear()
    stdscr.addstr("Add Item\nPress ESC to cancel")
    stdscr.addstr("\n\nEnter item name: ")
    stdscr.refresh()
    item_name = get_input(stdscr)
    if item_name is None:
        return
    
    if item_name in inventory:
        show_message(stdscr, "Item already exists.")
        return

    stdscr.addstr("\nEnter item quantity: ")
    stdscr.refresh()
    try:
        item_quantity_text = get_input(stdscr)
        if item_quantity_text is None:
            return
        item_quantity = int(item_quantity_text)
        if item_quantity < 0:
            raise ValueError
    except ValueError:
        show_message(stdscr, "Invalid quantity. Please enter a non-negative integer.")
        return

    stdscr.addstr("\nEnter item value: ")
    stdscr.refresh()
    try:
        item_value_text = get_input(stdscr)
        if item_value_text is None:
            return
        item_value = int(item_value_text)
        if item_value < 0:
            raise ValueError
    except ValueError:
        show_message(stdscr, "Invalid value. Please enter a non-negative integer.")
        return
    
    stdscr.addstr("\nIs this item in baskets? (y/n): ")
    stdscr.refresh()
    try:
        answer = get_input(stdscr)
        if answer is None:
            return
        answer = answer.lower()
        if answer not in ['y', 'n']:
            raise ValueError
    except ValueError:
        show_message(stdscr, "Invalid input. Please enter 'y' or 'n'.")
        return

    inventory[item_name] = {"Quantity": item_quantity, "Value": item_value, "Basket": answer == 'y'}
    transaction("Created item: {} - Amount: {} - Points Per Item: {} - In Baskets: {}".format(item_name, item_quantity, item_value, answer == 'y'))

def view_transactions(stdscr):
    stdscr.clear()
    stdscr.addstr("View Transactions\n")
    height, width = stdscr.getmaxyx()
    available_rows = max(0, height - 4)
    visible_transactions = transactions[-available_rows:] if available_rows else []
    for index, transaction in enumerate(visible_transactions):
        stdscr.addnstr(transaction.rstrip("\n"), max(0, width - 1))
        if index < len(visible_transactions) - 1:
            stdscr.addstr("\n")
    show_message(stdscr)

def basket_details(stdscr):
    top_five = sorted((item for item in inventory.items() if item[1]['Basket']), key=lambda x: (-x[1]['Quantity'], x[0]))[:5]
    bottom_five = sorted((item for item in inventory.items() if item[1]['Basket']), key=lambda x: (x[1]['Quantity'], x[0]))[:5]
    showing_top = True
    while True:
        stdscr.clear()
        stdscr.addstr("Basket Details\n\nBaskets Possible: {0}\n\n".format(min(item['Quantity'] for item in inventory.values() if item['Basket'])))
        items_to_show = top_five if showing_top else bottom_five
        title = "Top" if showing_top else "Bottom"
        stdscr.addstr("{0} 5 Items by Quantity:\n".format(title))
        for item_name, item_content in items_to_show:
            stdscr.addstr("{0} | Quantity: {1}\n".format(item_name, item_content['Quantity']))
        stdscr.addstr("\nPress Enter to switch views. Press ESC to return.")
        stdscr.refresh()
        key = stdscr.getch()
        if key == 27:
            return
        elif key in (curses.KEY_ENTER, 10, 13):
            showing_top = not showing_top

def clear_transactions(stdscr):
    stdscr.clear()
    stdscr.addstr("Clear Transactions\nPress ESC to cancel\n\nAre you sure you want to clear all transactions? (y/n): ")
    stdscr.refresh()
    answer = get_input(stdscr)
    if answer is None or answer.lower() != 'y':
        return
    transactions.clear()
    transaction("Cleared all transactions.")
    show_message(stdscr, "All transactions cleared.")

def clear_inventory(stdscr):
    stdscr.clear()
    stdscr.addstr("Clear Inventory\nPress ESC to cancel\n\nAre you sure you want to clear the entire inventory? (y/n): ")
    stdscr.refresh()
    answer = get_input(stdscr)
    if answer is None or answer.lower() != 'y':
        return
    inventory.clear()
    transaction("Inventory cleared.")
    show_message(stdscr, "Inventory cleared.")

def main():
    while True:
        print("\nInventory Tracker")
        print("\nUse arrow keys to navigate, Enter to select.")
        
        print("\nCommands")
        print("1. View Inventory")
        print("2. Search Inventory")
        print("3. Add Item")
        print("4. Basket Details")
        print("5. View Transactions")
        print("6. Clear Transactions")
        print("7. Clear Inventory")
        print("0. Exit")

        choice = input("Input selection: ")

        if choice == "1":
            curses.wrapper(view_inventory)
        elif choice == "2":
            curses.wrapper(search_inventory)
        elif choice == "3":
            curses.wrapper(add_item)
        elif choice == "4":
            curses.wrapper(basket_details)
        elif choice == "5":
            curses.wrapper(view_transactions)
        elif choice == "6":
            curses.wrapper(clear_transactions)
        elif choice == "7":
            curses.wrapper(clear_inventory)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

# actual script
atexit.register(on_exit)

if __name__ == "__main__":
    main()