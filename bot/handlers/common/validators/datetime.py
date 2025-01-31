import datetime
import string


def get_datetime_validated(input_date: str) -> datetime.datetime:
    input_date = input_date.lstrip().rstrip()

    if len(input_date) <= 5:
        raise ValueError(
            "Слишком мало цифр, исправьте: 1 -> 01 | 5 -> 05 | 12 -> 12 и т.д."
        )

    date_numbers = [i for i in input_date.split(" ")[0] if i.isdigit()]
    time_numbers = [i for i in input_date.split(" ")[-1] if i.isdigit()]

    time_numbers = list("".join(time_numbers).zfill(4))

    mounth, day = int("".join(date_numbers[2:])), int("".join(date_numbers[:2]))
    hour, minute = int("".join(time_numbers[:2])), int("".join(time_numbers[2:]))

    if len(date_numbers) != 4 or len(time_numbers) != 4:
        raise ValueError("Неверное кол-во цифр в дате, нужнен "
                         "формат: `31.12 22:59`")

    if not (0 < day <= 31):
        raise ValueError(
            f"Что то не так с днем месяца: (32>{day=}>0)"
        )

    if not (0 < mounth <= 12):
        raise ValueError(
            f"Что то не так с номером месяца (13>{mounth=}>0)"
        )

    if not ((0 <= minute <= 59) and (0 <= hour <= 24)):
        raise ValueError(
            f"Что то не так со временем урока, ваш ввод: {minute=} {hour=}"
        )

    return datetime.datetime(
        year=datetime.datetime.now().year,
        month=mounth,
        day=day,
        hour=hour,
        minute=minute
    )


def get_validated_duration(duration_input: str):
    try:
        duration_input = int(duration_input.lstrip().rstrip())
    except:
        raise ValueError("Похоже вы ввели не чисто...")

    if duration_input < 15:
        raise ValueError("Слишком короткий урок, минимум 15 минут")

    if duration_input > 60*4:
        raise ValueError("Кажется, >4 часа это многовато...")

    return duration_input
