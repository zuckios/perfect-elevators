import math
from datetime import datetime

from models.elevator_config import ElevatorConfig
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Elevator:
    project_name: Optional[str] = None
    configurations: Dict[ElevatorConfig, int] = field(default_factory=dict)

    def add_configuration(self, config: ElevatorConfig, count: int = 1):
        if config in self.configurations:
            self.configurations[config] += count
        else:
            self.configurations[config] = count

    def add_project_name(self, name: str):
        if self.project_name is None:
            self.project_name = name

    def print_configurations(self):
        if not self.configurations:
            print("Конфигурации лифтов отсутствуют")
            return

        print(f"Проект: {self.project_name}")
        for idx, (config, count) in enumerate(self.configurations.items(), start=1):
            print(
                f"{idx}. {config.elevator_type.value}, "
                f"грузоподъёмность: {config.load_capacity}, "
                f"этажей: {config.stop_count}, "
                f"нужны доп работы: {config.need_extra_work}, "
                f"нужен демонтаж лифта: {config.need_demounting}, "
                f"нужно усиление шахты: {config.need_floor_reinforcement}, "
                f"нужены разгарадительные балки: {config.need_separation_beams}, "
                f"кол-во: {count}"
            )

    def to_pdf_data(self, subtitle: str = "Стоимость монтажных и пусконаладочных работ") -> dict:
        """Формирует словарь данных для ProposalPDFGenerator."""
        items = []
        for config, count in self.configurations.items():
            unit_price = config.get_unit_price()
            total = unit_price * count
            items.append({
                "name": "Монтаж лифта",
                "size": f"{config.load_capacity} кг",
                "floors": f"{config.stop_count}/{config.stop_count}/{config.stop_count}",
                "qty": count,
                "unit_price": unit_price,
                "total": total,
            })
        without_vat = sum(it["total"] for it in items)
        vat_percent = 12
        vat_amount = math.floor(without_vat * vat_percent / 100)
        with_vat = without_vat + vat_amount
        return {
            "project": self.project_name or "Проект",
            "subtitle": subtitle,
            "date": datetime.today().strftime("%d.%m.%Y"),
            "items": items,
            "totals": {
                "without_vat": without_vat,
                "vat_percent": vat_percent,
                "vat_amount": vat_amount,
                "with_vat": with_vat,
            },
        }
