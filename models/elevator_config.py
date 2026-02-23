from dataclasses import dataclass
from typing import Optional
from enum import Enum, IntEnum


class ElevatorType(Enum):
    cargo = "грузовой"
    passenger = "пассажирский"


class LoadCapacity(IntEnum):
    lightweight = 630
    middlewight = 800
    lightheavyweight = 1000
    heavyweight = 1150


class HeightType(Enum):
    standart = "standart"
    custom = "custom"


class BoolType(Enum):
    yes = "yes"
    no = "no"


# Базовые цены за монтаж (без НДС) в сум
BASE_PRICES: dict[LoadCapacity, int] = {
    LoadCapacity.lightweight: 41_000_000,
    LoadCapacity.middlewight: 65_000_000,
    LoadCapacity.lightheavyweight: 82_000_000,
    LoadCapacity.heavyweight: 95_000_000,
}


@dataclass(frozen=True)
class ElevatorConfig:
    elevator_type: ElevatorType
    load_capacity: LoadCapacity
    stop_count: int
    height_value: Optional[int]
    need_extra_work: BoolType
    need_demounting: BoolType
    need_floor_reinforcement: BoolType
    need_separation_beams: BoolType

    def get_unit_price(self) -> int:
        """Возвращает базовую цену за единицу (без НДС)."""
        return BASE_PRICES.get(self.load_capacity, 50_000_000)