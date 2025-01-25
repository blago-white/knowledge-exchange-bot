def get_week_borders() -> tuple[int, int]:
    today = datetime.datetime.today()
    start = today - datetime.timedelta(days=today.weekday())

    return (
        start.timestamp(),
        (start + datetime.timedelta(days=6)).timestamp()
    )
