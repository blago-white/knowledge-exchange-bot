def edit_subject_title(title_input: str):
    if len(title_input) > 100:
        raise ValueError("Слишком длинное название :(")

    return title_input


def edit_subject_rate(rate_input: str):
    rate_input = int(rate_input)

    if rate_input > 7000:
        raise ValueError("Кажется слишком много :( если что - "
                         "напишите в поддерджку")

    return rate_input


def edit_subject_description(desc_input: str):
    if len(desc_input) > 500:
        raise ValueError("Это слишком длинное значение")

    return desc_input
