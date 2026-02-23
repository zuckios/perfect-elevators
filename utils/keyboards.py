from telegram import InlineKeyboardButton
from models.elevator_config import ElevatorType, LoadCapacity, HeightType, BoolType


class Keyboards:
    boolKeyboard = [
        [InlineKeyboardButton("Да", callback_data=BoolType.yes.value)],
        [InlineKeyboardButton("Нет", callback_data=BoolType.no.value)]
    ]

    elevator_type_keyboard = [
        [InlineKeyboardButton("Грузовой 🚛", callback_data=ElevatorType.cargo.value)],
        [InlineKeyboardButton("Пассажирский 🚶", callback_data=ElevatorType.passenger.value)],
    ]

    load_capacity_keyboard = [
        [InlineKeyboardButton("630 кг", callback_data=LoadCapacity.lightweight.value)],
        [InlineKeyboardButton("800 кг", callback_data=LoadCapacity.middlewight.value)],
        [InlineKeyboardButton("1000 кг", callback_data=LoadCapacity.lightheavyweight.value)],
        [InlineKeyboardButton("1150 кг", callback_data=LoadCapacity.heavyweight.value)]
    ]

    height_type_keyboard = [
        [InlineKeyboardButton("Стандартная высота", callback_data=HeightType.standart.value)],
        [InlineKeyboardButton("Нестандартная высота", callback_data=HeightType.custom.value)]
    ]
