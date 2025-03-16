import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from .models import House
from .models import Resident
from .models import ResidentialUnit

User = get_user_model()


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class DashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = "residential_units/residential-units.html"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ResidentialUnit.objects.all()
        return ResidentialUnit.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context["total_units"] = queryset.count()
        context["pending_units"] = queryset.filter(status="pending").count()
        context["approved_units"] = queryset.filter(status="approved").count()
        context["rejected_units"] = queryset.filter(status="rejected").count()

        context["total_houses"] = sum(unit.houses.count() for unit in queryset)
        context["total_residents"] = sum(
            house.residents.count() for unit in queryset for house in unit.houses.all()
        )

        recent_units = queryset.order_by("-created_at")[:10]
        for unit in recent_units:
            unit.total_houses = unit.houses.count()
            unit.total_residents = sum(
                house.residents.count() for house in unit.houses.all()
            )

        context["recent_units"] = recent_units
        return context


class ResidentialUnitListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ResidentialUnit
    template_name = "residential_units/list.html"
    context_object_name = "units"
    paginate_by = 10  # Lista completa con paginación
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)

        # Aquí podrías añadir filtros adicionales para la lista
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Obtener el queryset ordenado
        queryset = queryset.order_by(*self.ordering)

        # Agregar contadores a cada unidad residencial
        for unit in queryset:
            unit.total_houses = unit.houses.count()
            unit.total_residents = sum(
                house.residents.count() for house in unit.houses.all()
            )

        return queryset


class ResidentialUnitCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ResidentialUnit
    template_name = "residential_units/form.html"
    fields = [
        "name",
        "address",
        "photo",
        "map_url",
        "property_type",
        "phone",
        "email",
        "description",
    ]
    success_url = reverse_lazy("residential_units:dashboard")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ResidentialUnitUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ResidentialUnit
    template_name = "residential_units/form.html"
    success_url = reverse_lazy("residential_units:dashboard")

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

    def get_form_class(self):
        from django.forms import ModelForm

        if self.request.user.is_superuser:
            form_fields = [
                "name",
                "address",
                "photo",
                "map_url",
                "property_type",
                "status",
                "phone",
                "email",
                "description",
            ]
        else:
            form_fields = [
                "name",
                "address",
                "photo",
                "map_url",
                "property_type",
                "phone",
                "email",
                "description",
            ]

        class CustomResidentialUnitForm(ModelForm):
            class Meta:
                model = ResidentialUnit
                fields = form_fields

        return CustomResidentialUnitForm


class ResidentialUnitDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = ResidentialUnit
    template_name = "residential_units/detail.html"
    context_object_name = "unit"

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset


@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_unit(request, pk):
    unit = get_object_or_404(ResidentialUnit, pk=pk)
    unit.status = "approved"
    unit.approved_by = request.user
    unit.save()
    return JsonResponse(
        {
            "status": "success",
            "message": _("Unit has been approved successfully."),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def reject_unit(request, pk):
    unit = get_object_or_404(ResidentialUnit, pk=pk)
    unit.status = "rejected"
    unit.save()
    return JsonResponse(
        {
            "status": "success",
            "message": _("Unit has been rejected successfully."),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_house(request, unit_id):
    unit = get_object_or_404(ResidentialUnit, id=unit_id)

    if request.method == "POST":
        number = request.POST.get("number")
        tower_label = request.POST.get("tower_label")
        floor = request.POST.get("floor")

        house = House.objects.create(
            residential_unit=unit,
            number=number,
            tower_label=tower_label,
            floor=floor if floor else None,
        )

        return JsonResponse(
            {
                "status": "success",
                "message": _("House/Apartment added successfully."),
                "house": {
                    "id": house.id,
                    "number": house.number,
                    "tower_label": house.tower_label,
                    "floor": house.floor,
                },
            },
        )

    context = {
        "unit": unit,
    }

    if request.GET.get("modal"):
        return render(request, "residential_units/house_form.html", context)
    return JsonResponse({"status": "error", "message": _("Invalid request method.")})


@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_house(request, unit_id, house_id):
    unit = get_object_or_404(ResidentialUnit, id=unit_id)
    house = get_object_or_404(House, id=house_id, residential_unit=unit)

    if request.method == "POST":
        house.number = request.POST.get("number")
        house.tower_label = request.POST.get("tower_label")
        house.floor = request.POST.get("floor") if request.POST.get("floor") else None
        house.save()

        return JsonResponse(
            {
                "status": "success",
                "message": _("House/Apartment updated successfully."),
            },
        )

    context = {
        "unit": unit,
        "house": house,
    }

    if request.GET.get("modal"):
        return render(request, "residential_units/house_form.html", context)
    return JsonResponse({"status": "error", "message": _("Invalid request method.")})


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_house(request, unit_id, house_id):
    if request.method == "POST":
        unit = get_object_or_404(ResidentialUnit, id=unit_id)
        house = get_object_or_404(House, id=house_id, residential_unit=unit)
        house.delete()

        return JsonResponse(
            {
                "status": "success",
                "message": _("House/Apartment deleted successfully."),
            },
        )

    return JsonResponse(
        {
            "status": "error",
            "message": _("Invalid request method."),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def bulk_add_houses(request, unit_id):
    unit = get_object_or_404(ResidentialUnit, id=unit_id)
    limit_houses = 500

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "error",
                "message": _("Invalid JSON data."),
            },
        )

    items = data.get("items", [])
    if not items:
        return JsonResponse(
            {
                "status": "error",
                "message": _("No items to create."),
            },
        )

    if len(items) > limit_houses:
        return JsonResponse(
            {
                "status": "error",
                "message": _("Too many items. Maximum allowed is 500."),
            },
        )

    # Get existing combinations using unique_together fields
    existing_combinations = set(
        House.objects.filter(residential_unit=unit).values_list(
            "tower_label",
            "number",
            "floor",
        ),
    )

    duplicates = []
    created_count = 0

    for item in items:
        number = item.get("number")
        tower_label = item.get("tower_label", "")  # Default to empty string if None
        floor = item.get("floor")  # Can be None

        # Create tuple for comparison with existing combinations
        combination = (tower_label, number, floor)

        if combination in existing_combinations:
            duplicates.append(
                {
                    "number": number,
                    "tower": tower_label,
                    "floor": floor,
                },
            )
            continue

        House.objects.create(
            residential_unit=unit,
            number=number,
            tower_label=tower_label,
            floor=floor,
        )
        existing_combinations.add(combination)
        created_count += 1

    if duplicates:
        duplicate_details = [
            f"{d['number']} ({d['tower']}, Floor {d['floor']})" for d in duplicates
        ]
        if created_count > 0:
            message = _("Created {} houses/apartments. Skipped duplicates: {}").format(
                created_count,
                ", ".join(duplicate_details),
            )
        else:
            message = _("No houses/apartments created. All were duplicates: {}").format(
                ", ".join(duplicate_details),
            )
        return JsonResponse(
            {
                "status": "warning",
                "message": message,
                "duplicates": duplicates,
            },
        )

    return JsonResponse(
        {
            "status": "success",
            "message": _("Successfully created {} houses/apartments.").format(
                created_count,
            ),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def link_resident(request, house_id):
    house = get_object_or_404(House, id=house_id)

    if request.method == "POST":
        user_id = request.POST.get("user")
        is_owner = request.POST.get("is_owner") == "on"
        relationship = request.POST.get("relationship")

        if not is_owner and not relationship:
            return JsonResponse(
                {
                    "status": "error",
                    "message": _(
                        "Relationship is required when resident is not the owner.",
                    ),
                },
            )

        try:
            user = User.objects.get(id=user_id)
            resident = Resident.objects.create(
                house=house,
                user=user,
                is_owner=is_owner,
                relationship=relationship if not is_owner else "",
                approved=request.user.is_staff,
                approved_by=request.user if request.user.is_staff else None,
            )

            return JsonResponse(
                {
                    "status": "success",
                    "message": _("Resident linked successfully."),
                    "resident": {
                        "id": resident.id,
                        "name": resident.user.name,
                        "is_owner": resident.is_owner,
                    },
                },
            )
        except User.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": _("Selected user does not exist."),
                },
            )
        except (ValueError, ValidationError) as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": str(e),
                },
            )

    # Para solicitudes GET, devolver el formulario
    users = User.objects.filter(is_active=True).exclude(
        id__in=house.residents.values_list("user_id", flat=True),
    )

    context = {
        "house": house,
        "users": users,
    }

    if request.GET.get("modal"):
        return render(request, "residential_units/resident_form.html", context)

    return JsonResponse(
        {
            "status": "error",
            "message": _("Invalid request method."),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_residents(request, house_id):
    house = get_object_or_404(House, id=house_id)

    # Verificar que el usuario tenga acceso a esta unidad residencial
    if (
        not request.user.is_superuser
        and house.residential_unit.created_by != request.user
    ):
        raise PermissionDenied

    context = {
        "house": house,
    }
    return render(request, "residential_units/manage_residents.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def update_resident(request, resident_id):
    if request.method == "POST":
        resident = get_object_or_404(Resident, id=resident_id)
        is_owner = request.POST.get("is_owner") == "on"
        relationship = request.POST.get("relationship", "")
        approved = request.POST.get("approved") == "on"

        if not is_owner and not relationship:
            return JsonResponse(
                {
                    "status": "error",
                    "message": _(
                        "Relationship is required when resident is not the owner.",
                    ),
                },
            )

        resident.is_owner = is_owner
        resident.relationship = relationship if not is_owner else ""

        if request.user.is_staff and resident.approved != approved:
            resident.approved = approved
            resident.approved_by = request.user if approved else None

        resident.save()

        return JsonResponse(
            {
                "status": "success",
                "message": _("Resident updated successfully."),
            },
        )

    return JsonResponse(
        {
            "status": "error",
            "message": _("Invalid request method."),
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_resident(request, resident_id):
    if request.method == "POST":
        resident = get_object_or_404(Resident, id=resident_id)
        resident.delete()

        return JsonResponse(
            {
                "status": "success",
                "message": _("Resident removed successfully."),
            },
        )

    return JsonResponse(
        {
            "status": "error",
            "message": _("Invalid request method."),
        },
    )
