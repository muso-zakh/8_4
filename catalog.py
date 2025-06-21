from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import sqlite3

catalog_router = Router()

# --- Foydalanuvchi holatlari
class AddCategory(StatesGroup):
    name = State()

class AddProduct(StatesGroup):
    name = State()
    category = State()

class SearchProduct(StatesGroup):
    term = State()

# --- Tugmalarni ushlash
@catalog_router.callback_query(F.data == "list_categories")
async def list_categories(callback: CallbackQuery):
    with sqlite3.connect("shop.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM categories")
        rows = cur.fetchall()
    if not rows:
        await callback.message.answer("❌ Hech qanday kategoriya yo‘q.")
    else:
        text = "\n".join(f"📂 {r[0]}" for r in rows)
        await callback.message.answer(f"📋 Kategoriyalar:\n{text}")
    await callback.answer()

@catalog_router.callback_query(F.data == "list_products")
async def list_products(callback: CallbackQuery):
    with sqlite3.connect("shop.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.name, c.name FROM products p
            JOIN categories c ON p.category_id = c.id
        """)
        rows = cur.fetchall()
    if not rows:
        await callback.message.answer("❌ Maxsulotlar yo‘q.")
    else:
        text = "\n".join(f"📦 {r[0]} ({r[1]})" for r in rows)
        await callback.message.answer(f"🛒 Maxsulotlar:\n{text}")
    await callback.answer()

# --- Kategoriya qo‘shish
@catalog_router.callback_query(F.data == "add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✏️ Kategoriya nomini kiriting:")
    await state.set_state(AddCategory.name)
    await callback.answer()

@catalog_router.message(AddCategory.name)
async def add_category_finish(message: Message, state: FSMContext):
    name = message.text.strip()
    try:
        with sqlite3.connect("shop.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO categories(name) VALUES (?)", (name,))
            conn.commit()
        await message.answer(f"✅ Kategoriya qo‘shildi: {name}")
    except:
        await message.answer("❌ Bu nomli kategoriya allaqachon mavjud.")
    await state.clear()

# --- Maxsulot qo‘shish
@catalog_router.callback_query(F.data == "add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Maxsulot nomini kiriting:")
    await state.set_state(AddProduct.name)
    await callback.answer()

@catalog_router.message(AddProduct.name)
async def get_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("📂 Qaysi kategoriya ostida? (nomini yozing):")
    await state.set_state(AddProduct.category)

@catalog_router.message(AddProduct.category)
async def save_product(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    category_name = message.text.strip()

    with sqlite3.connect("shop.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        row = cur.fetchone()
        if not row:
            await message.answer("❌ Bunday kategoriya topilmadi.")
        else:
            cur.execute("INSERT INTO products(name, category_id) VALUES (?, ?)", (name, row[0]))
            conn.commit()
            await message.answer(f"✅ Maxsulot qo‘shildi: {name} ({category_name})")
    await state.clear()

# --- Qidiruv
@catalog_router.callback_query(F.data == "search_product")
async def search_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔍 Qidirilayotgan maxsulot nomini kiriting:")
    await state.set_state(SearchProduct.term)
    await callback.answer()

@catalog_router.message(SearchProduct.term)
async def search_result(message: Message, state: FSMContext):
    term = message.text.strip()
    with sqlite3.connect("shop.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.name, c.name FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.name LIKE ?
        """, (f"%{term}%",))
        rows = cur.fetchall()
    if not rows:
        await message.answer("❌ Hech nima topilmadi.")
    else:
        text = "\n".join(f"🔍 {r[0]} ({r[1]})" for r in rows)
        await message.answer(f"🔎 Natijalar:\n{text}")
    await state.clear()
