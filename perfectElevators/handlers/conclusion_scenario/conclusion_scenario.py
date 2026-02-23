import tempfile
from pathlib import Path

from telegram import Update, InlineKeyboardMarkup, Message
from telegram.ext import ConversationHandler, ContextTypes
from models.bot_steps import Step
from models.elevator_config import BoolType, ElevatorConfig
from utils.keyboards import Keyboards
from utils.pdf_builder import ProposalPDFGenerator, Layout
from enum import Enum


class ConclusionScenario:

    class __Messages(Enum):
        ask_elevator_count = "Количество лифтов с выбранной выше конфигурацией"
        ask_add_new_config_elevator = "Добавить ещё одну конфигурацию лифта?"
        ask_select_elevator_type = "Начинаем ввод новой конфигурации лифта. Выберите тип лифта"
        input_finished = "Новая конфигурация не требуется. Все введеные параметры приняты ✅. Начинаю формировать коммерческое предложение"

    async def ask_elevator_count(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        await message.reply_text(self.__Messages.ask_elevator_count.value)
        return Step.ASK_ELEVATOR_COUNT

    async def elevator_count_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["elevator_count"] = int(update.message.text)
        await self.saveConfig(context)
        return await self.ask_add_new_elevator_config(update.message, context)

    async def saveConfig(self, context: ContextTypes.DEFAULT_TYPE):
        config = ElevatorConfig(
            elevator_type=context.user_data["elevator_type"],
            load_capacity=context.user_data["load_capacity"],
            stop_count=context.user_data["elevator_stop_count"],
            height_value=context.user_data["height"],
            need_extra_work=context.user_data["need_extra_work"],
            need_demounting=context.user_data["need_demounting"],
            need_floor_reinforcement=context.user_data["need_floor_reinforcement"],
            need_separation_beams=context.user_data["need_separation_beams"]
        )

        count = context.user_data["elevator_count"]
        project_name = context.user_data["project_name"]
        elevator = context.user_data["elevator"]
        elevator.add_project_name(project_name)
        elevator.add_configuration(config, count)



    async def ask_add_new_elevator_config(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.boolKeyboard)
        await message.reply_text(self.__Messages.ask_add_new_config_elevator.value, reply_markup=reply_markup)
        return Step.ASK_NEED_TO_ADD_ELEVATOR_NEW_CONFIG

    async def add_new_elevator_config_option_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == BoolType.yes.value:
            reply_markup = InlineKeyboardMarkup(Keyboards.elevator_type_keyboard)
            await query.edit_message_text(self.__Messages.ask_select_elevator_type.value, reply_markup=reply_markup)
            return Step.ASK_ELEVATOR_TYPE
        else:
            await query.edit_message_text(self.__Messages.input_finished.value)
            elevator = context.user_data["elevator"]
            elevator.print_configurations()

            ## Формирование пдф из данных в elevator
            pdf_data = elevator.to_pdf_data()
            generator = ProposalPDFGenerator()
            output_path = tempfile.mktemp(suffix=".pdf")
            generator.generate(pdf_data, output=output_path, logo_path=Layout.DEFAULT_LOGO)
            try:
                with open(output_path, "rb") as doc:
                    await query.message.reply_document(document=doc, filename="commercial_proposal.pdf")
            finally:
                Path(output_path).unlink(missing_ok=True)

            return ConversationHandler.END
