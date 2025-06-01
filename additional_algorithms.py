from datetime import datetime

def date_translate(date: str):
    weekdays_ru = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье"
    }

    months_ru = {
        "January": "Января",
        "February": "Февраля",
        "March": "Марта",
        "April": "Апреля",
        "May": "Мая",
        "June": "Июня",
        "July": "Июля",
        "August": "Августа",
        "September": "Сентября",
        "October": "Октября",
        "November": "Ноября",
        "December": "Декабря"
    }

    date_obj = datetime.strptime(date, "%a %b %d %H:%M:%S %Y")

    # Получаем английские названия
    weekday_en = date_obj.strftime("%A")
    month_en = date_obj.strftime("%B")

    # Переводим
    weekday_ru = weekdays_ru.get(weekday_en, weekday_en)
    month_ru = months_ru.get(month_en, month_en)

    # Форматируем вывод
    return f"{weekday_ru}, {date_obj.day} {month_ru} {date_obj.year}"