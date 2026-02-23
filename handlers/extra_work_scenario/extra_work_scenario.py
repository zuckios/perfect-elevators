from telegram import Update, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes
from models.elevator_config import BoolType
from models.bot_steps import Step
from utils.keyboards import Keyboards
from enum import Enum
from handlers.conclusion_scenario.conclusion_scenario import ConclusionScenario


class ExtraWorkScenario:
    class __Messages(Enum):
        need_extra_work = "Требуются ли дополнительные работы?"
        extra_work_needed = "Нужны дополнительные работы"
        extra_work_noneed = "Дополнительные работы не требуются"
        need_demounting_work = "Требуется ли демонтаж существующего лифта?"
        demounting_work_needed = "Требуется демонтаж существующего лифта"
        demounting_work_noneeded = "Демонтаж существующего лифта не требуется"
        need_mine_reinforcement = "Требуются ли усиление шахты?"
        mine_reinforcement_needed = "Требуются усиление шахты"
        mine_reinforcement_noneeded = "Усиление шахты не требуется"
        need_barrier_beams = "Требуются ли разгарадительные балки?"
        barrier_beams_needed = "Требуются разгарадительные балки"
        barrier_beams_noneeded = "Разгарадительные балки не требуются"

    __conclusion = ConclusionScenario()

    async def ask_extra_work(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.boolKeyboard)
        await message.reply_text(self.__Messages.need_extra_work.value, reply_markup=reply_markup)
        return Step.ASK_NEED_EXTRA_WORK

    async def extra_work_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        context.user_data["need_extra_work"] = BoolType.no
        context.user_data["need_demounting"] = BoolType.no
        context.user_data["need_floor_reinforcement"] = BoolType.no
        context.user_data["need_separation_beams"] = BoolType.no

        if query.data == BoolType.yes.value:
            context.user_data["need_extra_work"] = BoolType.yes
            await query.edit_message_text(self.__Messages.extra_work_needed.value)
            return await self.ask_demounting_work(query.message, context)
        else:
            context.user_data["need_extra_work"] = BoolType.no
            await query.edit_message_text(self.__Messages.extra_work_noneed.value)
            return await self.__conclusion.ask_elevator_count(query.message, context)

    async def ask_demounting_work(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.boolKeyboard)
        await message.reply_text(self.__Messages.need_demounting_work.value, reply_markup=reply_markup)
        return Step.ASK_NEED_DEMOUNTING

    async def demounting_option_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == BoolType.yes.value:
            context.user_data["need_demounting"] = BoolType.yes
            await query.edit_message_text(self.__Messages.demounting_work_needed.value)
        else:
            context.user_data["need_demounting"] = BoolType.no
            await query.edit_message_text(self.__Messages.demounting_work_noneeded.value)
        return await self.ask_floor_reinforcement(query.message, context)

    async def ask_floor_reinforcement(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.boolKeyboard)
        await message.reply_text(self.__Messages.need_mine_reinforcement.value, reply_markup=reply_markup)
        return Step.ASK_NEED_FLOOR_REINFORCEMENT

    async def floor_reinforcement_option_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == BoolType.yes.value:
            context.user_data["need_floor_reinforcement"] = BoolType.yes
            await query.edit_message_text(self.__Messages.mine_reinforcement_needed.value)
        else:
            context.user_data["need_floor_reinforcement"] = BoolType.no
            await query.edit_message_text(self.__Messages.mine_reinforcement_noneeded.value)
        return await self.ask_separation_beams(query.message, context)

    async def ask_separation_beams(self, message: Message, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(Keyboards.boolKeyboard)
        await message.reply_text(self.__Messages.need_barrier_beams.value, reply_markup=reply_markup)
        return Step.ASK_NEED_SEPARATION_BEAMS

    async def separation_beams_option_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == BoolType.yes.value:
            context.user_data["need_separation_beams"] = BoolType.yes
            await query.edit_message_text(self.__Messages.barrier_beams_needed.value)
        else:
            context.user_data["need_separation_beams"] = BoolType.no
            await query.edit_message_text(self.__Messages.barrier_beams_noneeded.value)
        return await self.__conclusion.ask_elevator_count(query.message, context)
