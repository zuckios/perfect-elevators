from telegram import Update, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes
from models.bot_steps import Step
from models.elevator import Elevator
from models.elevator_config import ElevatorType, LoadCapacity, HeightType
from utils.keyboards import Keyboards
from enum import Enum
from handlers.extra_work_scenario.extra_work_scenario import ExtraWorkScenario


class FoundationScenario:
    class __Messages(Enum):
        ask_project_name = "Введите название объекта"
        ask_select_elevator_type = "Выберите тип лифта"
        ask_select_load_capacity = "Выберите грузоподъёмность лифта"
        ask_elevator_stop_count = "Выберите количество остановок"
        ask_select_height_type = "Выберите тип высоты"
        standart_height_selected = "Выбрана стандартная высота"
        enter_custom_height = "Выбрана нестандартная высота, введите нужную высоту"

    __extra_work = ExtraWorkScenario()

    async def ask_project_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sent_message = await update.message.reply_text(self.__Messages.ask_project_name.value)
        return Step.ASK_PROJECT_NAME

    async def project_name_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        project_name = update.message.text
        context.user_data["project_name"] = project_name
        context.user_data["elevator"] = Elevator()
        return await self.ask_elevator_type(update.message, context)

    async def ask_elevator_type(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.elevator_type_keyboard)
        await message.reply_text(self.__Messages.ask_select_elevator_type.value, reply_markup=reply_markup)
        return Step.ASK_ELEVATOR_TYPE

    async def elevator_type_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        elevator_type = ElevatorType(query.data)
        context.user_data["elevator_type"] = elevator_type
        await query.edit_message_text(f"Тип лифта выбран как {elevator_type.value}")
        return await self.ask_load_capacity(query.message, context)

    async def ask_load_capacity(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.load_capacity_keyboard)
        await message.reply_text(self.__Messages.ask_select_load_capacity.value, reply_markup=reply_markup)
        return Step.ASK_LOAD_CAPACITY

    async def load_capacity_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        load_capacity = LoadCapacity(int(query.data))
        context.user_data["load_capacity"] = load_capacity
        await query.edit_message_text(f"Грузоподъёмность лифта выбрана как {load_capacity.value} кг")
        return await self.ask_elevator_stop_count(query.message, context)

    async def ask_elevator_stop_count(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        await message.reply_text(self.__Messages.ask_elevator_stop_count.value)
        return Step.ASK_ELEVATOR_STOP_COUNT

    async def elevator_stop_count_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["elevator_stop_count"] = int(update.message.text)
        return await self.ask_height_type(update.message, context)

    async def ask_height_type(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.height_type_keyboard)
        await message.reply_text(self.__Messages.ask_select_height_type.value, reply_markup=reply_markup)
        return Step.ASK_HEIGHT_TYPE

    async def height_type_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == HeightType.standart.value:
            context.user_data["height"] = None
            await query.edit_message_text(self.__Messages.standart_height_selected.value)
            return await self.__extra_work.ask_extra_work(query.message, context)
        else:
            await query.edit_message_text(self.__Messages.enter_custom_height.value)
            return Step.ASK_CUSTOM_HEIGHT_VALUE

    async def ask_custom_height_value(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["height"] = int(update.message.text)
        height = context.user_data["height"]
        await update.message.reply_text(f"Принята высота: {height} м")
        return await self.__extra_work.ask_extra_work(update.message, context)
