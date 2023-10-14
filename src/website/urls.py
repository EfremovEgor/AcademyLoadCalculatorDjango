from django.urls import path, re_path
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    path("overview", views.overview, name="overview"),
    path("data", views.data, name="data"),
    path("bachelor", views.bachelor, name="bachelor"),
    path("magistrate", views.magistrate, name="magistrate"),
    path("add_employee", views.add_employee, name="add_employee"),
    path("edit_employee", views.edit_employee, name="edit_employee"),
    path("employees/get_employee", views.get_employee, name="get_employee"),
    path("login", views.user_login, name="login"),
    path("logout", views.user_logout, name="logout"),
    path(
        "positions/get_positions",
        views.get_positions,
        name="get_positions",
    ),
    path(
        "subjects/get_subject_study_level_by_name",
        views.get_subject_study_level_by_name,
        name="get_subject_study_level_by_name",
    ),
    path(
        "subjects/get_subject_holding_type_by_study_level_name",
        views.get_subject_holding_type_by_study_level_name,
        name="get_subject_holding_type_by_study_level_name",
    ),
    path(
        "subjects/get_subject_ciphers_and_directions_by_name_level_holding",
        views.get_subject_ciphers_and_directions_by_name_level_holding,
        name="get_subject_ciphers_and_directions_by_name_level_holding",
    ),
    path(
        "subjects/get_subject_groups_by_name_level_holding_cipher_direction",
        views.get_subject_groups_by_name_level_holding_cipher_direction,
        name="get_subject_groups_by_name_level_holding_cipher_direction",
    ),
    path(
        "persons/save_person",
        views.save_person,
        name="save_person",
    ),
    path(
        "persons/delete_person",
        views.delete_person,
        name="delete_person",
    ),
    path(
        "persons/edit_person",
        views.edit_person,
        name="edit_person",
    ),
    path(
        "investigate_subject/<str:subject_name>/<str:group>",
        views.investigate_subject,
        name="investigate_subject",
    ),
    re_path(
        r"^.*$",
        RedirectView.as_view(url="overview", permanent=False),
        name="index",
    ),
]
