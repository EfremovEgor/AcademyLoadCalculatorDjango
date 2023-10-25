import datetime
import io
import textwrap
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

style_heading = ParagraphStyle(
    name="Normal",
    fontName="Russian",
    fontSize=24,
    alignment=1,
    spaceAfter=40,
    spaceBefore=40,
)
style_main_text = ParagraphStyle(
    name="Normal", fontName="Russian", fontSize=16, spaceAfter=10
)


def create_person_pdf(info: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("Russian", "./static/fonts/Calibri Light.ttf"))
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=20,
        bottomMargin=18,
        title=info["full_name"],
    )
    flowables = []
    flowables.append(Paragraph(info["full_name"], style=style_heading))
    flowables.append(
        Paragraph(
            f"Дата рождения: {info['birth_date'].strftime('%d.%m.%Y') if info['birth_date'] != datetime.date.min else 'Нет' }",
            style=style_main_text,
        )
    )
    flowables.append(
        Paragraph(
            f"Номер телефона: {info['phone_number']}",
            style=style_main_text,
        )
    )
    flowables.append(
        Paragraph(f"Ученая степень: {info['degree']}", style=style_main_text)
    )
    flowables.append(
        Paragraph(f"Ученое звание: {info['academic_title']}", style=style_main_text)
    )
    flowables.append(Paragraph(f"Должность: {info['position']}", style=style_main_text))
    flowables.append(Paragraph(f"Ставка: {info['rate']}", style=style_main_text))
    flowables.append(
        Paragraph(
            f"Нагрузка по ставке в год(час): {info['yearly_load']}",
            style=style_main_text,
        )
    )
    flowables.append(
        Paragraph(
            f"Оклад по ставке в месяц(руб.): {info['salary']}",
            style=style_main_text,
        )
    )
    flowables.append(Paragraph("Краткая информация по нагрузке", style=style_heading))
    data = [
        [
            "Нагрузка в\nбакалавриате",
            "",
            "Нагрузка в\nмагистратуре",
            "",
            "По ставке",
            "Фактическая",
        ],
        [
            "Нечетные семестры",
            "Четные семестры",
            "Нечетные семестры",
            "Четные семестры",
        ],
        [
            info["bachelor_odd"],
            info["bachelor_even"],
            info["magistrate_odd"],
            info["magistrate_even"],
            info["yearly_load"],
            sum(
                [
                    info["bachelor_odd"],
                    info["bachelor_even"],
                    info["magistrate_odd"],
                    info["magistrate_even"],
                ]
            ),
        ],
    ]
    style_table_load = TableStyle(
        [
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("FONTNAME", (0, 0), (-1, -1), "Russian"),
            ("SPAN", (0, 0), (1, 0)),
            ("SPAN", (2, 0), (3, 0)),
            ("SPAN", (4, 0), (4, 1)),
            ("SPAN", (5, 0), (5, 1)),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]
    )

    tbl = Table(data)
    tbl.setStyle(style_table_load)
    flowables.append(tbl)
    if info["subjects"]:
        flowables.append(Paragraph("Информация по предметам", style=style_heading))

        style_table_subjects_params = [
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("FONTNAME", (0, 0), (-1, -1), "Russian"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]
        data = [
            [
                "Уровень обучения",
                "Предмет",
                "Тип\nзанятия",
                "Направление",
                "Группа\nСеместр",
                "Нагрузка",
            ]
        ]
        text_width = 15
        subjects = info["subjects"]
        offset = 1
        for study_level, subject_names in subjects.items():
            for subject_name, holding_types in subject_names.items():
                for holding_type, directions in holding_types.items():
                    for direction, groups in directions.items():
                        data.append(
                            [
                                study_level,
                                textwrap.fill(subject_name, text_width),
                                textwrap.fill(holding_type, text_width),
                                textwrap.fill(direction, 25),
                                "\n".join(groups),
                                list(groups.values())[0],
                            ]
                        )
            offset += len(groups)
        data_ = list(data)

        current = 0
        for i, item in enumerate(data_[1:], 1):
            if (
                item[2] == data[current][2]
                and item[1] == data_[current][1]
                and item[0] == data_[current][0]
            ):
                item[2] = ""
            else:
                style_table_subjects_params.append(("SPAN", (2, current), (2, i - 1)))
                current = i
        style_table_subjects_params.append(("SPAN", (2, current), (2, i)))

        current = 0
        for i, item in enumerate(data_[1:], 1):
            if item[1] == data_[current][1] and item[0] == data_[current][0]:
                item[1] = ""
            else:
                style_table_subjects_params.append(("SPAN", (1, current), (1, i - 1)))
                current = i
        style_table_subjects_params.append(("SPAN", (1, current), (1, i)))

        current = 0
        for i, item in enumerate(data_[1:], 1):
            if item[0] == data_[current][0]:
                item[0] = ""
            else:
                style_table_subjects_params.append(("SPAN", (0, current), (0, i - 1)))
                current = i
        style_table_subjects_params.append(("SPAN", (0, current), (0, i)))

        data = data_
        subjects_table = Table(data)
        style_table_subjects = TableStyle(style_table_subjects_params)
        subjects_table.setStyle(style_table_subjects)
        flowables.append(subjects_table)

    doc.build(flowables)

    return buffer


def create_overview_pdf(info: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("Russian", "./static/fonts/Calibri Light.ttf"))
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1,
        leftMargin=1,
        topMargin=5,
        bottomMargin=5,
        title="Общая информация",
    )

    flowables = []

    data = [
        [
            "ФИО",
            "Дата\nрождения",
            "Телефон",
            "Ученая\nстепень",
            "Ученое\nзвание",
            "Должность",
            "Ставка",
            "Нагрузка\nпо ставке\nв год,\nчас",
            "Оклад\nпоставке в\nмесяц,\nруб.",
            "Нагрузка в\nбакалавриате",
            "",
            "Нагрузка в\nмагистратуре",
            "",
        ],
        [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Нечетные семестры",
            "Четные семестры",
            "Нечетные семестры",
            "Четные семестры",
        ],
    ]
    for item in info:
        values = list(item.values())
        values[1] = values[1].replace(" ", "\n")
        values[2] = (
            values[2].strftime("%d.%m.%Y") if values[2] != datetime.date.min else "Нет"
        )
        values[3] = "Нет" if not values[3] else values[3]
        data.append(values[1:8] + values[9:])

    style_table_overview = TableStyle(
        [
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (-1, -1), "Russian"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("SPAN", (0, 0), (0, 1)),
            ("SPAN", (1, 0), (1, 1)),
            ("SPAN", (2, 0), (2, 1)),
            ("SPAN", (3, 0), (3, 1)),
            ("SPAN", (4, 0), (4, 1)),
            ("SPAN", (5, 0), (5, 1)),
            ("SPAN", (6, 0), (6, 1)),
            ("SPAN", (7, 0), (7, 1)),
            ("SPAN", (8, 0), (8, 1)),
            ("SPAN", (9, 0), (10, 0)),
            ("SPAN", (11, 0), (12, 0)),
        ]
    )
    tbl = Table(data)
    tbl.setStyle(style_table_overview)
    flowables.append(tbl)

    doc.build(flowables)
    return buffer


def create_study_level_pdf(info: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("Russian", "./static/fonts/Calibri Light.ttf"))
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1,
        leftMargin=1,
        topMargin=5,
        bottomMargin=5,
        title="Общая информация",
    )
    flowables = []

    style_table = TableStyle(
        [
            ("FONTSIZE", (0, 0), (-1, -1), 16),
            ("FONTNAME", (0, 0), (-1, -1), "Russian"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("SPAN", (0, 0), (-1, 0)),
        ]
    )
    style_table_group = TableStyle(
        [
            ("FONTSIZE", (0, 0), (-1, -1), 15),
            ("FONTNAME", (0, 0), (-1, -1), "Russian"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("SPAN", (2, 0), (-1, 0)),
        ]
    )

    table_width = 5 * [2 * inch]
    for _, item_data in info.items():
        for subject_name, subject_data in item_data.items():
            data = list()
            data.append([textwrap.fill(subject_name, 60), "", "", ""])
            tbl = Table(data, colWidths=table_width)
            tbl.setStyle(style_table)
            flowables.append(tbl)
            for group_name, group_data in subject_data.items():
                for semester, semester_data in group_data.items():
                    data = list()
                    data.append(
                        [
                            group_name,
                            f"{semester} Семестр",
                            f"{list(semester_data.items())[0][1]['number_of_students']} Студент(ов)",
                            "",
                        ]
                    )
                    tbl = Table(data, colWidths=table_width)
                    tbl.setStyle(style_table_group)
                    flowables.append(tbl)
                    for holding_type, holding_data in semester_data.items():
                        amount = 1
                        if (
                            holding_type == "Лабораторная работа"
                            and holding_data["number_of_students"] >= 14
                        ):
                            amount = 2
                        for _ in range(amount):
                            style_table_type = TableStyle(
                                [
                                    ("FONTSIZE", (0, 0), (-1, -1), 14),
                                    ("FONTNAME", (0, 0), (-1, -1), "Russian"),
                                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                    ("SPAN", (2, 0), (-1, 0)),
                                ]
                            )
                            data = list()
                            data.append(
                                [
                                    textwrap.fill(holding_type, 20),
                                    f"{holding_data['total_time']} Час(ов)",
                                    textwrap.fill(holding_data["teacher"], 20)
                                    if holding_data["teacher"] is not None
                                    else "Нет",
                                    "",
                                ]
                            )
                            if holding_data["teacher"] is not None:
                                style_table_type.add(
                                    "BACKGROUND", (0, 0), (-1, -1), colors.palegreen
                                )
                            else:
                                style_table_type.add(
                                    "BACKGROUND", (0, 0), (-1, -1), colors.pink
                                )
                            tbl = Table(data, colWidths=table_width)
                            tbl.setStyle(style_table_type)
                            flowables.append(tbl)

    doc.build(flowables)
    return buffer
