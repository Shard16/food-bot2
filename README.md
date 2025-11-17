# FoodieBot (Telegram Food Delivery Bot)

A small Telegram bot built with pyTelegramBotAPI (`telebot`) that shows a menu, lets users add items to a cart, checkout, and submit orders. This README explains how to set up the project on Windows (PowerShell), configure the bot, and run it locally.

## Contents
- `bot.py` — main entrypoint
- `handlers/` — handler modules (`start.py`, `menu.py`, `cart.py`, `order.py`)
- `data/` — `menu.json` (menu) and `orders.json` (optional)
- `init_db.py` — recreate or initialize the SQLite `data/orders.db` schema
- `handlers/menu.py` uses an in-memory cart stored in `user_carts`

## Prerequisites
- Python 3.8+ installed
- Git (optional)
- A Telegram bot token (get one from @BotFather)

## Recommended workflow (Windows PowerShell)
Open PowerShell in the project root (where `bot.py` is located).

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv venv
# Activate the venv in PowerShell
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install pyTelegramBotAPI
# Optionally: pip install -r requirements.txt (if you add one)
```

3. Create a `.env` file in the project root with these variables:

```
BOT_TOKEN=123456:ABCDEF...   # your bot token
ADMIN_CHAT_ID=987654321     # (optional) Telegram chat id to receive new orders
PAYMENT_ACCOUNT=Acct: 000111222333 (Bank XYZ)
```

(If you don't set `ADMIN_CHAT_ID` the bot will still work but won't forward orders to an admin.)

4. Initialize (or recreate) the orders database (optional but recommended):

```powershell
python init_db.py
```

Note: `init_db.py` in this repository creates the `data/orders.db` table structure. If you change the schema, edit `init_db.py` accordingly.

5. Run the bot:

```powershell
python bot.py
```

You should see a startup message like:

```
🤖 Bot is running...
```

Now open Telegram, message your bot, and send `/start`.

## Typical flow (what to test)
- /start → press "🍽️ View Menu" → press an item to add to cart
- Press "🛒 View Cart" → verify items and subtotals
- Press "✅ Checkout" → choose Dine-in or Delivery → follow prompts for name and table/address
- After confirming, you should receive:
  - an order summary
  - a thank-you/payment instruction with the `PAYMENT_ACCOUNT` displayed
  - a "Back to Menu" button
  - if `ADMIN_CHAT_ID` is set, admin receives order details

## Where data is stored
- `data/menu.json` — contains the menu items (id, name, price, etc.)
- `data/orders.db` — SQLite DB storing individual order rows
- `handlers/menu.py` keeps an in-memory `user_carts` structure while the bot runs; this is not persisted across restarts.

## Troubleshooting
- Buttons show "Connecting" and nothing happens:
  - Ensure `bot.py` is running with the same Python interpreter and virtualenv where `pyTelegramBotAPI` is installed.
  - Check that `BOT_TOKEN` is correct and `bot.infinity_polling()` is running.
  - If using VS Code, make sure the selected interpreter matches the activated venv.

- `ModuleNotFoundError: No module named 'menu'`:
  - Use the project root as the working directory and run `python bot.py` from there. Handlers use `handlers.menu` or `from handlers import menu`.

- Database NOT NULL constraint errors (e.g. `orders.total`):
  - The schema expects `total`; ensure `init_db.py` or migration script matches the insert columns in `handlers/menu.py`'s `save_order`.

- If numbers/prices include a `$` sign in `data/menu.json`, the code strips `$` when computing totals. If your menu stores prices as strings with currency symbols, keep that consistent.

## Next improvements you might want
- Persist `user_carts` and `user_data` to disk or DB so bot restarts don't lose user carts and partial orders.
- Add tests for handlers and DB functions.
- Improve admin notification (include Telegram username, contact, or forward receipt images automatically).
- Add logging instead of print statements for easier debugging.

## Contributing
Open a PR or edit files directly if you're working locally. Please run the bot and test the flow before pushing changes.

## License
This repository doesn't include a license file — add one if you want to share the code publicly.
