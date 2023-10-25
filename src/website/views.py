import json
import datetime
from django.forms.models import model_to_dict
from django.http import FileResponse, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from transliterate import translit
from .pdf_converter import (
    create_overview_pdf,
    create_person_pdf,
    create_study_level_pdf,
)
from .forms import DataFileForm, LoginForm
from .models import Group, Person, Position, Subject, Degree, AcademicTitle
from .utils import calculate_employee_load
from django.contrib.auth import authenticate, login, logout


@login_required(login_url="login")
def overview(request):
    to_render = list()
    for item in Person.objects.all():
        load = calculate_employee_load(item)
        serialized_item = model_to_dict(item)
        position = Position.objects.filter(id=serialized_item["position"])[0]
        serialized_item["academic_title"] = item.academic_title.name
        serialized_item["degree"] = item.degree.name
        serialized_item["birth_date"] = (
            serialized_item["birth_date"].strftime("%d.%m.%Y")
            if serialized_item["birth_date"] != datetime.date.min
            else "Нет"
        )
        serialized_item["position"] = position.position_name
        serialized_item["yearly_load"] = round(
            position.load * serialized_item["rate"], 2
        )
        serialized_item["salary"] = round(position.salary * serialized_item["rate"], 2)

        serialized_item.update(
            {
                "bachelor_odd": load[0],
                "bachelor_even": load[1],
                "magistrate_odd": load[2],
                "magistrate_even": load[3],
            }
        )
        to_render.append(serialized_item)
    to_render.sort(key=lambda a: a["full_name"])
    return render(request, "overview.html", {"employees": to_render})


@login_required(login_url="login")
def data(request):
    if request.method == "POST":
        form = DataFileForm(request.POST, request.FILES)
        if form.is_valid():
            model_to_override = {
                "Предметы": Subject,
                "Группы": Group,
                "Должности": Position,
            }

            model_name = request.POST["model"]
            data = json.load(request.FILES["file"])
            to_create = list()
            model_to_override[model_name].objects.all().delete()
            if model_name == "Предметы":
                for item in data:
                    cipher = item["cipher"]
                    groups = Group.objects.all().filter(
                        cipher=cipher,
                    )
                    for group in groups.all():
                        if not (
                            item["course"]
                            == relativedelta(
                                datetime.date.today(),
                                datetime.date(
                                    datetime.datetime.now().year // 100 * 100
                                    + int(group.name.split("-")[-1]),
                                    8,
                                    1,
                                ),
                            ).years
                            + 1
                        ):
                            continue
                        if item["semester_duration"] is None:
                            item["semester_duration"] = 0
                        if item["subject_type"] is None:
                            item["subject_type"] = "Неизвестно"
                        if item["holding_type"] is None:
                            item["holding_type"] = item["subject_type"]
                        if item["holding_type"].lower().strip() == "семинар":
                            item["holding_type"] = "Практическое занятие"
                        subject = Subject(**item, groups=group)

                        to_create.append(subject)
            else:
                to_create = [model_to_override[model_name](**item) for item in data]
            model_to_override[model_name].objects.bulk_create(to_create)

    else:
        form = DataFileForm()
    return render(request, "data.html", {"form": form})


def save_person(request):
    data = json.loads(request.body)
    person = Person(
        full_name=data.get("name"),
        birth_date=data.get("birth_date")
        if data.get("birth_date") is not None
        else datetime.datetime.min,
        phone_number=data.get("phone_number"),
        degree=Degree.objects.filter(name=data.get("degree")).first(),
        academic_title=AcademicTitle.objects.filter(
            name=data.get("academic_title")
        ).first(),
        position=Position.objects.filter(position_name=data.get("position")).first(),
        rate=float(data.get("rate")),
    )
    person.save()
    for item in data.get("subjects"):
        subject = Subject.objects.filter(
            semester=int(item["semester"]),
            holding_type=item["holding_type"],
            groups__name=item["groups"],
            study_level=item["study_level"],
            name=item["name"],
        ).first()
        if subject not in person.subjects.all():
            person.subjects.add(subject)
    return JsonResponse(
        {
            "message": {"status": "ok"},
        },
        content_type="application/json",
    )


def get_positions(request):
    return JsonResponse(
        {
            "message": {"status": "ok"},
            "data": {
                "positions": [item.position_name for item in Position.objects.all()],
            },
        },
        content_type="application/json",
    )


def add_employee(request):
    return render(
        request,
        "components/add_employee_form.html",
        {
            "positions": [item.position_name for item in Position.objects.all()],
            "titles": [item.name for item in AcademicTitle.objects.all()],
            "degrees": [item.name for item in Degree.objects.all()],
            "subject_names": sorted(
                list(
                    Subject.objects.values("name")
                    .distinct()
                    .values_list("name", flat=True)
                )
            ),
        },
    )


def edit_employee(request):
    return render(
        request,
        "components/edit_employee_form.html",
        {
            "positions": [item.position_name for item in Position.objects.all()],
            "titles": [item.name for item in AcademicTitle.objects.all()],
            "degrees": [item.name for item in Degree.objects.all()],
            "subject_names": sorted(
                list(
                    Subject.objects.values("name")
                    .distinct()
                    .values_list("name", flat=True)
                )
            ),
        },
    )


def get_person_from_db(id):
    person = get_object_or_404(Person, pk=id)
    data = model_to_dict(
        person,
        fields=[field.name for field in Person._meta.fields],
    )
    data["academic_title"] = person.academic_title.name
    data["degree"] = person.degree.name
    data["position"] = person.position.position_name
    data["subjects"] = dict()
    for subject in person.subjects.all():
        if data["subjects"].get(f"{subject.name} | {subject.study_level}") is None:
            data["subjects"][f"{subject.name} | {subject.study_level}"] = {}

        if (
            data["subjects"][f"{subject.name} | {subject.study_level}"].get(
                subject.holding_type
            )
            is None
        ):
            data["subjects"][f"{subject.name} | {subject.study_level}"][
                subject.holding_type
            ] = {"cipher_and_direction": [], "groups": []}

        if (
            ", ".join((subject.cipher, subject.direction))
            not in data["subjects"][f"{subject.name} | {subject.study_level}"][
                subject.holding_type
            ]["cipher_and_direction"]
        ):
            data["subjects"][f"{subject.name} | {subject.study_level}"][
                subject.holding_type
            ]["cipher_and_direction"].append(
                ", ".join((subject.cipher, subject.direction))
            )

        data["subjects"][f"{subject.name} | {subject.study_level}"][
            subject.holding_type
        ]["groups"].append(f"{subject.groups.name} | {str(subject.semester)} Семестр")
    return data


def get_employee(request):
    data = get_person_from_db(request.GET.get("id"))
    return JsonResponse(
        {
            "message": {"status": "ok"},
            "data": data,
        },
        content_type="application/json",
    )


def edit_person(request):
    data = json.loads(request.body)
    person = Person.objects.filter(pk=data.get("id")).first()
    person.full_name = data.get("name")
    person.birth_date = (
        data.get("birth_date") if data.get("birth_date") else datetime.datetime.now
    )
    person.phone_number = data.get("phone_number")
    person.degree = Degree.objects.filter(name=data.get("degree")).first()
    person.academic_title = AcademicTitle.objects.filter(
        name=data.get("academic_title")
    ).first()
    person.position = Position.objects.filter(
        position_name=data.get("position")
    ).first()
    person.rate = float(data.get("rate"))
    person.subjects.clear()

    for item in data.get("subjects"):
        subject = Subject.objects.filter(
            semester=int(item["semester"]),
            holding_type=item["holding_type"],
            groups__name=item["groups"],
            study_level=item["study_level"],
            name=item["name"],
        ).first()
        if subject not in person.subjects.all():
            person.subjects.add(subject)
    person.save()
    return JsonResponse(
        {"message": {"status": "ok"}},
        content_type="application/json",
    )


def delete_person(request):
    Person.objects.filter(id=QueryDict(request.body).get("id")).delete()
    return JsonResponse(
        {"message": {"status": "ok"}},
        content_type="application/json",
    )


def get_subject_study_level_by_name(request):
    if request.method != "GET":
        return HttpResponse({"message": f"Method Not Allowed {request.method}"})

    response_data = sorted(
        list(
            Subject.objects.filter(name=request.GET.get("name"))
            .values("study_level")
            .distinct()
            .values_list("study_level", flat=True)
        )
    )

    return JsonResponse(
        {
            "message": {"status": "ok"},
            "data": response_data,
        },
        content_type="application/json",
    )


def get_subject_holding_type_by_study_level_name(request):
    if request.method != "GET":
        return HttpResponse({"message": f"Method Not Allowed {request.method}"})
    response_data = (
        sorted(
            list(
                Subject.objects.filter(
                    study_level=request.GET.get("study_level"),
                    name=request.GET.get("name"),
                )
                .values("holding_type")
                .distinct()
                .values_list("holding_type", flat=True)
            )
        ),
    )

    return JsonResponse(
        {
            "message": {"status": "ok"},
            "data": response_data,
        },
        content_type="application/json",
    )


def get_subject_groups_by_name_level_holding_cipher_direction(request):
    if request.method != "GET":
        return HttpResponse({"message": f"Method Not Allowed {request.method}"})
    combined = [
        item.split(", ") for item in request.GET.getlist("ciphers_and_directions[]")
    ]

    response_data = set()
    for cipher, direction in combined:
        data = list(
            Subject.objects.filter(
                study_level=request.GET.get("study_level"),
                name=request.GET.get("name"),
                holding_type=request.GET.get("holding_type"),
                cipher=cipher.strip(),
                direction=direction,
            ).only("groups")
        )

        response_data.update(
            [
                f"{subject.groups.name} | {str(subject.semester)} Семестр"
                for subject in data
            ]
        )
    response_data = sorted(list(response_data))
    return JsonResponse(
        {
            "message": {"status": "ok"},
            "data": response_data,
        },
        content_type="application/json",
    )


def get_subject_ciphers_and_directions_by_name_level_holding(request):
    if request.method != "GET":
        return HttpResponse({"message": f"Method Not Allowed {request.method}"})

    response_data = (
        sorted(
            [
                ", ".join(item)
                for item in Subject.objects.filter(
                    study_level=request.GET.get("study_level"),
                    name=request.GET.get("name"),
                    holding_type=request.GET.get("holding_type"),
                )
                .values("cipher", "direction")
                .distinct()
                .values_list("cipher", "direction")
            ]
        ),
    )

    return JsonResponse(
        {
            "message": {"status": "ok"},
            "data": response_data,
        },
        content_type="application/json",
    )


def create_subjects_from_db(study_level):
    subjects = {}
    items = (
        Subject.objects.values_list("name", "groups__name", "subject_type")
        .filter(study_level=study_level)
        .order_by("subject_type")
        .all()
    )

    for item in items:
        subjects[item[2]] = subjects.get(item[2], dict())
        subjects[item[2]][item[0]] = subjects[item[2]].get(item[0], dict())
        subjects[item[2]][item[0]]["20" + item[1].split("-")[-1]] = subjects[item[2]][
            item[0]
        ].get("20" + item[1].split("-")[-1], list())
        if item[1] not in subjects[item[2]][item[0]]["20" + item[1].split("-")[-1]]:
            subjects[item[2]][item[0]]["20" + item[1].split("-")[-1]].append(item[1])
        subjects[item[2]][item[0]]["20" + item[1].split("-")[-1]].sort()

        for key, value in subjects.items():
            subjects[key] = dict(sorted(value.items()))
    return subjects


@login_required(login_url="login")
def bachelor(request):
    subjects = create_subjects_from_db("Бакалавриат")
    return render(
        request,
        "subjects.html",
        {"subjects": subjects, "study_level": "Бакалавриат"},
    )


@login_required(login_url="login")
def magistrate(request):
    subjects = create_subjects_from_db("Магистратура")
    return render(
        request,
        "subjects.html",
        {"subjects": subjects, "study_level": "Магистратура"},
    )


def investigate_subject(request, subject_name, group):
    info = {}
    for item in Subject.objects.filter(name=subject_name, groups__name=group).all():
        info[
            (
                item.semester,
                item.groups.number_of_students,
            )
        ] = info.get(
            (
                item.semester,
                item.groups.number_of_students,
            ),
            dict(),
        )
        info[
            (
                item.semester,
                item.groups.number_of_students,
            )
        ][item.holding_type] = info[
            (
                item.semester,
                item.groups.number_of_students,
            )
        ].get(
            item.holding_type, None
        )
        teacher = Person.objects.filter(subjects__in=[item.id]).first()
        if teacher is not None:
            info[
                (
                    item.semester,
                    item.groups.number_of_students,
                )
            ][item.holding_type] = teacher.full_name
        info[
            (
                item.semester,
                item.groups.number_of_students,
            )
        ][item.holding_type] = (
            info[
                (
                    item.semester,
                    item.groups.number_of_students,
                )
            ][item.holding_type],
            item.total_time_for_group * item.semester_duration,
        )

    info = dict(sorted(info.items()))

    return render(
        request,
        "components/investigate_subject.html",
        {"naming": f"{subject_name} - {group}", "info": info},
    )


def user_login(request):
    if request.user.is_authenticated:
        return redirect("overview")
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.GET.get("next") is not None:
                    return redirect(request.GET.get("next"))
                return redirect("overview")
    return render(request, "login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("login")


def get_person_pdf(request, id):
    person = get_object_or_404(Person, pk=id)
    data = model_to_dict(person)
    data["degree"] = person.degree.name
    data["academic_title"] = person.academic_title.name
    data["position"] = person.position.position_name
    data["yearly_load"] = round(person.position.load * person.rate, 2)
    data["salary"] = round(person.position.salary * person.rate, 2)
    load = calculate_employee_load(person)

    data.update(
        {
            "bachelor_odd": load[0],
            "bachelor_even": load[1],
            "magistrate_odd": load[2],
            "magistrate_even": load[3],
        }
    )
    data["subjects"] = dict()
    for subject in person.subjects.all():
        if data["subjects"].get(subject.study_level) is None:
            data["subjects"][subject.study_level] = {}
        if data["subjects"][subject.study_level].get(subject.name) is None:
            data["subjects"][subject.study_level][subject.name] = {}
        if (
            data["subjects"][subject.study_level][subject.name].get(
                subject.holding_type
            )
            is None
        ):
            data["subjects"][subject.study_level][subject.name][
                subject.holding_type
            ] = {}
        if (
            data["subjects"][subject.study_level][subject.name][
                subject.holding_type
            ].get(subject.direction)
            is None
        ):
            data["subjects"][subject.study_level][subject.name][subject.holding_type][
                subject.direction
            ] = {}
        if (
            data["subjects"][subject.study_level][subject.name][subject.holding_type][
                subject.direction
            ].get(f"{subject.groups.name}|{subject.semester} сем")
            is None
        ):
            data["subjects"][subject.study_level][subject.name][subject.holding_type][
                subject.direction
            ][f"{subject.groups.name}|{subject.semester} сем."] = (
                subject.total_time_for_group * subject.semester_duration
            )

    buffer = create_person_pdf(data)

    buffer.seek(0)
    response = FileResponse(
        buffer,
        as_attachment=False,
        filename=f"{person.full_name}.pdf",
        content_type="application/pdf",
    )
    response[
        "Content-Disposition"
    ] = f"inline; filename={translit(person.full_name,'ru',reversed=True)}.pdf"
    return response


def get_overview_pdf(request):
    data = list()
    persons = Person.objects.all()
    for person in persons:
        info = {}
        info = model_to_dict(person)
        info["degree"] = person.degree.name
        info["academic_title"] = person.academic_title.name
        info["position"] = person.position.position_name
        info["yearly_load"] = round(person.position.load * person.rate, 2)
        info["salary"] = round(person.position.salary * person.rate, 2)
        load = calculate_employee_load(person)
        info.update(
            {
                "bachelor_odd": load[0],
                "bachelor_even": load[1],
                "magistrate_odd": load[2],
                "magistrate_even": load[3],
            }
        )
        data.append(info)

    buffer = create_overview_pdf(data)
    buffer.seek(0)
    response = FileResponse(
        buffer,
        as_attachment=False,
        filename="overview.pdf",
        content_type="application/pdf",
    )
    response["Content-Disposition"] = "inline; filename=overview.pdf"
    return response


def get_study_level_pdf(request, study_level):
    subjects = {}
    items = (
        Subject.objects.filter(study_level=study_level)
        .order_by("study_level", "subject_type", "name", "semester")
        .all()
    )
    persons = Person.objects.exclude(subjects=None)
    for item in items:
        subjects[item.study_level] = subjects.get(item.study_level, dict())

        subjects[item.study_level][item.name] = subjects[item.study_level].get(
            item.name, dict()
        )
        subjects[item.study_level][item.name][item.groups.name] = subjects[
            item.study_level
        ][item.name].get(item.groups.name, dict())
        subjects[item.study_level][item.name][item.groups.name][
            item.semester
        ] = subjects[item.study_level][item.name][item.groups.name].get(
            item.semester, dict()
        )
        teacher = persons.filter(subjects__in=[item.id]).first()
        if teacher is not None:
            teacher = teacher.full_name
        subjects[item.study_level][item.name][item.groups.name][item.semester][
            item.holding_type
        ] = {
            "total_time": item.total_time_for_group * item.semester_duration,
            "teacher": teacher,
            "number_of_students": item.groups.number_of_students,
        }
        subjects[item.study_level][item.name] = dict(
            sorted(subjects[item.study_level][item.name].items())
        )
    buffer = create_study_level_pdf(subjects)
    buffer.seek(0)
    response = FileResponse(
        buffer,
        as_attachment=False,
        filename=f"{translit(study_level,'ru',reversed=True)}.pdf",
        content_type="application/pdf",
    )

    response[
        "Content-Disposition"
    ] = f"inline; filename={translit(study_level,'ru',reversed=True)}.pdf"

    return response
