from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import DriverForm, CarForm, DriverLicenseUpdateForm
from .models import Driver, Car, Manufacturer


@login_required
def index(request):
    """View function for the home page of the site."""

    num_drivers = Driver.objects.count()
    num_cars = Car.objects.count()
    num_manufacturers = Manufacturer.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_drivers": num_drivers,
        "num_cars": num_cars,
        "num_manufacturers": num_manufacturers,
        "num_visits": num_visits + 1,
    }

    return render(request, "taxi/index.html", context=context)


class ManufacturerListView(LoginRequiredMixin, generic.ListView):
    model = Manufacturer
    context_object_name = "manufacturer_list"
    template_name = "taxi/manufacturer_list.html"
    paginate_by = 5


class ManufacturerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Manufacturer
    success_url = reverse_lazy("taxi:manufacturer-list")


class CarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    paginate_by = 5
    queryset = Car.objects.all().select_related("manufacturer")


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car


class CarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    fields = "__all__"
    success_url = reverse_lazy("taxi:car-list")


class CarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Car
    success_url = reverse_lazy("taxi:car-list")


class DriverListView(LoginRequiredMixin, generic.ListView):
    model = Driver
    paginate_by = 5


class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = Driver
    queryset = Driver.objects.all().prefetch_related("cars__manufacturer")


class DriverCreateView(generic.CreateView):
    model = Driver
    success_url = reverse_lazy("taxi:driver-list")
    form_class = DriverForm


class DriversLicenseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Driver
    form_class = DriverLicenseUpdateForm
    template_name = "taxi/driver-license-update.html"


class DriversDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Driver
    template_name = "taxi/driver-delete-confirm.html"
    success_url = reverse_lazy("taxi:driver-list")


class DriverAssignView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    template_name = "taxi/driver-assign-confirm.html"
    success_url = reverse_lazy("taxi:car-detail", pk=get_user_model().id)
    fields = "__all__"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return render(
            request,
            "taxi/driver-assign-confirm.html",
            context={"driver_id": pk}
        )

    def post(self, request, *args, **kwargs):
        car = Car.objects.get(pk=kwargs.get("pk"))
        user = request.user
        car.drivers.add(user)
        car.save()
        return redirect("taxi:car-detail", pk=kwargs.get("pk"))


class DriverDisassignView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    template_name = "taxi/driver-assign-confirm.html"
    success_url = reverse_lazy("taxi:car-detail", pk=get_user_model().id)
    fields = "__all__"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return render(
            request,
            "taxi/driver-disassign-confirm.html",
            context={"driver_id": pk}
        )

    def post(self, request, *args, **kwargs):
        car = Car.objects.get(pk=kwargs.get("pk"))
        user = request.user
        car.drivers.remove(user)
        car.save()
        return redirect("taxi:car-detail", pk=kwargs.get("pk"))
