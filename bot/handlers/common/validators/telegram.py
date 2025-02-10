def get_validated_tid(telegram_id_input: str):
    try:
        telegram_id = int(telegram_id_input.lstrip().rstrip())
    except:
        raise ValueError("Похоже это не id, а нужно значение только из цифр(")

    if telegram_id < 0:
        raise ValueError("Наверняка id не может быть 0<")

    return telegram_id
