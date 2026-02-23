from telegram import Update
from models.bot_steps import Step
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from handlers.foundation_scenario.foundation_scenario import FoundationScenario
from handlers.extra_work_scenario.extra_work_scenario import ExtraWorkScenario
from handlers.conclusion_scenario.conclusion_scenario import ConclusionScenario

foundation = FoundationScenario()
extra_work = ExtraWorkScenario()
conclusion = ConclusionScenario()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Расчёт отменён.")
    return ConversationHandler.END


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("calculate", foundation.ask_project_name)],
    states={
        Step.ASK_PROJECT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, foundation.project_name_selected)
        ],
        Step.ASK_ELEVATOR_TYPE: [
            CallbackQueryHandler(foundation.elevator_type_selected)
        ],
        Step.ASK_LOAD_CAPACITY: [
            CallbackQueryHandler(foundation.load_capacity_selected)
        ],
        Step.ASK_ELEVATOR_STOP_COUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, foundation.elevator_stop_count_selected)
        ],
        Step.ASK_HEIGHT_TYPE: [
            CallbackQueryHandler(foundation.height_type_selected)
        ],
        Step.ASK_CUSTOM_HEIGHT_VALUE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, foundation.ask_custom_height_value)
        ],
        Step.ASK_NEED_EXTRA_WORK: [
            CallbackQueryHandler(extra_work.extra_work_selected)
        ],
        Step.ASK_NEED_DEMOUNTING: [
            CallbackQueryHandler(extra_work.demounting_option_selected)
        ],
        Step.ASK_NEED_FLOOR_REINFORCEMENT: [
            CallbackQueryHandler(extra_work.floor_reinforcement_option_selected)
        ],
        Step.ASK_NEED_SEPARATION_BEAMS: [
            CallbackQueryHandler(extra_work.separation_beams_option_selected)
        ],
        Step.ASK_ELEVATOR_COUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, conclusion.elevator_count_selected)
        ],
        Step.ASK_NEED_TO_ADD_ELEVATOR_NEW_CONFIG: [
            CallbackQueryHandler(conclusion.add_new_elevator_config_option_selected)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
