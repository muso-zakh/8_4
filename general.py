from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

basic_router = Router()

@basic_router.message(CommandStart())
async def start_handler(message: Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kategoriya qo‘shish", callback_data="add_category")],
        [InlineKeyboardButton(text="➕ Maxsulot qo‘shish", callback_data="add_product")],
        [InlineKeyboardButton(text="📂 Kategoriyalar", callback_data="list_categories")],
        [InlineKeyboardButton(text="📦 Maxsulotlar", callback_data="list_products")],
        [InlineKeyboardButton(text="🔍 Qidiruv", callback_data="search_product")]
    ])
    await message.answer("🛍 <b>Nima qilmoqchisiz?</b>", reply_markup=markup)
