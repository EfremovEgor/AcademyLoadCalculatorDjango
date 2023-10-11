from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .forms import DataFileForm
from .utils import calculate_employee_load
from .models import Subject, Group, Position, Person
import json
from django.http import QueryDict


def overview(request):
    to_render = list()
    for item in Person.objects.all():
        load = calculate_employee_load(item)
        serialized_item = model_to_dict(item)
        position = Position.objects.filter(id=serialized_item["position"])[0]
        serialized_item["position"] = position.position_name
        serialized_item["yearly_load"] = position.load
        serialized_item["salary"] = position.salary * serialized_item["rate"]

        serialized_item.update(
            {
                "bachelor_odd": load[0],
                "bachelor_even": load[1],
                "magistrate_odd": load[2],
                "magistrate_even": load[3],
            }
        )
        to_render.append(serialized_item)

    return render(request, "overview.html", {"employees": to_render})


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
                    groups = Group.objects.all().filter(cipher=cipher)
                    for group in groups.all():
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
        birth_date=data.get("birth_date"),
        phone_number=data.get("phone_number"),
        degree=data.get("degree"),
        academic_title=data.get("academic_title"),
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
        print(subject not in person.subjects.all())
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
            "subject_names": sorted(
                list(
                    Subject.objects.values("name")
                    .distinct()
                    .values_list("name", flat=True)
                )
            ),
        },
    )


def get_employee(request):
    person = Person.objects.get(pk=request.GET.get("id"))
    data = model_to_dict(
        person,
        fields=[field.name for field in Person._meta.fields],
    )
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
            ", ".join((subject.cipher, subject.department))
            not in data["subjects"][f"{subject.name} | {subject.study_level}"][
                subject.holding_type
            ]["cipher_and_direction"]
        ):
            data["subjects"][f"{subject.name} | {subject.study_level}"][
                subject.holding_type
            ]["cipher_and_direction"].append(
                ", ".join((subject.cipher, subject.department))
            )

        data["subjects"][f"{subject.name} | {subject.study_level}"][
            subject.holding_type
        ]["groups"].append(f"{subject.groups.name} | {str(subject.semester)} Семестр")
    print(data)
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
    person.birth_date = data.get("birth_date")
    person.phone_number = data.get("phone_number")
    person.degree = data.get("degree")
    person.academic_title = data.get("academic_title")
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
                department=direction,
            )
            .only("groups")
            .distinct("groups")
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
                .values("cipher", "department")
                .distinct()
                .values_list("cipher", "department")
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


def bachelor(request):
    subjects = {}
    for subject in (
        Subject.objects.filter(study_level="Бакалавриат").order_by("subject_type").all()
    ):
        subjects[subject.subject_type] = subjects.get(subject.subject_type, dict())
        subjects[subject.subject_type][subject.name] = subjects[
            subject.subject_type
        ].get(subject.name, dict())
        subjects[subject.subject_type][subject.name][subject.groups.name] = subjects[
            subject.subject_type
        ][subject.name].get(subject.groups.name, dict())
        subjects[subject.subject_type][subject.name][subject.groups.name][
            "credit"
        ] = subject.credit
        subjects[subject.subject_type][subject.name][subject.groups.name][
            subject.holding_type
        ] = subjects[subject.subject_type][subject.name][subject.groups.name].get(
            subject.holding_type, dict()
        )
        teacher = Person.objects.filter(subjects__in=[subject.id]).first()
        subjects[subject.subject_type][subject.name][subject.groups.name][
            subject.holding_type
        ]["teacher"] = (teacher.full_name if teacher is not None else None)

    return render(request, "bachelor.html", {"subjects": subjects})


def magistrate(request):
    subjects = {}
    for subject in (
        Subject.objects.filter(study_level="Магистратура")
        .order_by("subject_type")
        .all()
    ):
        subjects[subject.subject_type] = subjects.get(subject.subject_type, dict())
        subjects[subject.subject_type][subject.name] = subjects[
            subject.subject_type
        ].get(subject.name, dict())
        subjects[subject.subject_type][subject.name][subject.groups.name] = subjects[
            subject.subject_type
        ][subject.name].get(subject.groups.name, dict())
        subjects[subject.subject_type][subject.name][subject.groups.name][
            "credit"
        ] = subject.credit
        subjects[subject.subject_type][subject.name][subject.groups.name][
            subject.holding_type
        ] = subjects[subject.subject_type][subject.name][subject.groups.name].get(
            subject.holding_type, dict()
        )
        teacher = Person.objects.filter(subjects__in=[subject.id]).first()
        subjects[subject.subject_type][subject.name][subject.groups.name][
            subject.holding_type
        ]["teacher"] = (teacher.full_name if teacher is not None else None)

    return render(request, "bachelor.html", {"subjects": subjects})
