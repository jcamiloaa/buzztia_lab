from django.urls import path

from . import views

app_name = "residential_units"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("create/", views.ResidentialUnitCreateView.as_view(), name="create"),
    path("list/", views.ResidentialUnitListView.as_view(), name="list"),
    path("<int:pk>/", views.ResidentialUnitDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ResidentialUnitUpdateView.as_view(), name="edit"),
    path("approve/<int:pk>/", views.approve_unit, name="approve"),
    path("reject/<int:pk>/", views.reject_unit, name="reject"),
    path("<int:unit_id>/houses/add/", views.add_house, name="add_house"),
    path(
        "<int:unit_id>/houses/<int:house_id>/edit/",
        views.edit_house,
        name="edit_house",
    ),
    path(
        "<int:unit_id>/houses/<int:house_id>/delete/",
        views.delete_house,
        name="delete_house",
    ),
    path(
        "<int:unit_id>/houses/bulk_add/",
        views.bulk_add_houses,
        name="bulk_add_houses",
    ),
    path(
        "house/<int:house_id>/link-resident/",
        views.link_resident,
        name="link_resident",
    ),
    path(
        "house/<int:house_id>/manage-residents/",
        views.manage_residents,
        name="manage_residents",
    ),
    path(
        "resident/<int:resident_id>/update/",
        views.update_resident,
        name="update_resident",
    ),
    path(
        "resident/<int:resident_id>/delete/",
        views.delete_resident,
        name="delete_resident",
    ),
]
