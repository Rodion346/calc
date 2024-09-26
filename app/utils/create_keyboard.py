from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CreateKeyboard:
    def __init__(self):
        pass

    async def create_keyboard(self, buttons, columns=2):
        keyboard_buttons = []
        for i in range(0, len(buttons), columns):
            row = [
                types.KeyboardButton(text=button) for button in buttons[i : i + columns]
            ]
            keyboard_buttons.append(row)
        return types.ReplyKeyboardMarkup(
            keyboard=keyboard_buttons, resize_keyboard=True
        )

    async def create_kb_folders(self, folders, row=1):
        k_b = InlineKeyboardBuilder()
        for i in range(0, len(folders), row):
            row_buttons = [
                InlineKeyboardButton(
                    text=folder.title,
                    callback_data=f"kb_{folder.title}",
                )
                for folder in folders[i : i + row]
            ]
            k_b.row(*row_buttons)
        return k_b.as_markup()
