# Perfect Elevators — Telegram-бот для расчёта КП

Telegram-бот для формирования коммерческих предложений на монтаж лифтов. Собирает параметры лифтов от пользователя и генерирует PDF с расчётом стоимости.

## Требования

- Python 3.11+
- Токен бота от [@BotFather](https://t.me/BotFather)

## Виртуальное окружение

```bash
# Создать виртуальное окружение
python -m venv .venv

# Активация
# macOS / Linux:
source .venv/bin/activate

# Windows (cmd):
.venv\Scripts\activate.bat

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt
```

## Переменные окружения

Создайте файл `.env` в корне проекта (можно скопировать из `.env.example`):

```env
BOT_TOKEN=ваш_токен_от_BotFather
```

Или задайте переменную в окружении:

```bash
export BOT_TOKEN=ваш_токен_от_BotFather
```

> ⚠️ Файл `.env` не должен попадать в репозиторий (уже добавлен в `.gitignore`).

## Запуск

```bash
python bot.py
```

Команды бота:

- `/start` — приветствие и краткая инструкция
- `/calculate` — начать расчёт коммерческого предложения
- `/cancel` — отменить текущий расчёт

---

## Структура проекта

```
perfectElevators/
├── bot.py                 # Точка входа, регистрация обработчиков
├── handlers/
│   ├── start.py           # Обработка /start
│   ├── conversation.py    # Главный ConversationHandler, сценарий диалога
│   ├── foundation_scenario/   # Этап 1: базовые параметры лифта
│   │   └── foundation_scenario.py
│   ├── extra_work_scenario/      # Этап 2: доп. работы
│   │   └── extra_work_scenario.py
│   └── conclusion_scenario/      # Этап 3: кол-во, итог, генерация PDF
│       └── conclusion_scenario.py
├── models/
│   ├── bot_steps.py       # Состояния диалога (enum Step)
│   ├── elevator.py        # Модель Elevator, агрегация конфигураций
│   └── elevator_config.py # ElevatorConfig, типы лифтов, нагрузки, цены
├── utils/
│   ├── keyboards.py       # Inline-клавиатуры
│   └── pdf_builder.py     # Генерация PDF коммерческого предложения
├── assets/
│   └── logo.jpg           # Логотип для PDF (опционально)
├── .env                   # Переменные окружения (не в git)
├── .env.example           # Шаблон .env
├── requirements.txt
└── README.md
```

---

## Архитектура

### Сценарии диалога

Расчёт разбит на три сценария, выполняемых последовательно:

1. **Foundation** — базовые параметры:
   - Название проекта
   - Тип лифта (грузовой / пассажирский)
   - Грузоподъёмность (630–1150 кг)
   - Количество остановок
   - Тип высоты (стандартная / пользовательская)

2. **Extra Work** — дополнительные работы:
   - Дополнительные работы
   - Демонтаж старого лифта
   - Усиление шахты
   - Разгрузочные балки

3. **Conclusion** — подведение итогов:
   - Количество лифтов с текущей конфигурацией
   - Возможность добавить ещё одну конфигурацию (возврат к выбору типа)
   - Генерация PDF и отправка пользователю

### Хранение данных

- **`context.user_data`** — данные диалога и экземпляр `Elevator` для текущего пользователя
- **`Elevator`** — накапливает конфигурации лифтов и формирует данные для PDF
- Изоляция между пользователями достигается за счёт `user_data` в python-telegram-bot

### Генерация PDF

- `utils/pdf_builder.py` — модуль генерации PDF (reportlab)
- `ProposalPDFGenerator` — формирует коммерческое предложение
- Данные подготавливаются в `Elevator.to_pdf_data()`
