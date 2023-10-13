from .models import Person


def calculate_employee_load(
    person: Person,
) -> tuple[float, float, float, float]:
    actual_load_masters = list([0, 0])
    actual_load_bachelor = list([0, 0])
    to_calculate = list()

    for subject in person.subjects.all():
        for item in to_calculate:
            if (
                item.name.lower().strip() == subject.name.lower().strip()
                and item.semester % 2 == subject.semester % 2
                and item.holding_type == "Лекция"
                and subject.holding_type == "Лекция"
                and item.study_level == subject.study_level
                and item.total_time_for_group == subject.total_time_for_group
            ):
                break
        else:
            to_calculate.append(subject)

    for subject in to_calculate:
        if subject.study_level == "Бакалавриат":
            actual_load_bachelor[not (subject.semester % 2)] += (
                subject.total_time_for_group * subject.semester_duration
            )

        if subject.study_level == "Магистратура":
            actual_load_masters[not (subject.semester % 2)] += (
                subject.total_time_for_group * subject.semester_duration
            )

    actual_load_bachelor.extend(actual_load_masters)
    return tuple(actual_load_bachelor)
