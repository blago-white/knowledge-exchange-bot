def get_validated_link(link_input: str):
    link_input = link_input.lstrip().rstrip()

    if not link_input.startswith("http"):
        raise ValueError("Неверный формат, отсутствует `http`")

    return link_input
