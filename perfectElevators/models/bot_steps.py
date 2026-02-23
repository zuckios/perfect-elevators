from enum import Enum, auto


# Состояния диалога
class Step(Enum):
    ASK_PROJECT_NAME = auto()
    ASK_ELEVATOR_TYPE = auto()
    ASK_LOAD_CAPACITY = auto()
    ASK_ELEVATOR_STOP_COUNT = auto()
    ASK_HEIGHT_TYPE = auto()
    ASK_CUSTOM_HEIGHT_VALUE = auto()
    ASK_NEED_EXTRA_WORK = auto()
    ASK_NEED_DEMOUNTING = auto()
    ASK_NEED_FLOOR_REINFORCEMENT = auto()
    ASK_NEED_SEPARATION_BEAMS = auto()
    ASK_ELEVATOR_COUNT = auto()
    ASK_NEED_TO_ADD_ELEVATOR_NEW_CONFIG = auto()