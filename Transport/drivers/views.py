from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Driver, Car
from .forms import CarForm

# Create your views here.



@login_required
def driver_car_view(request):
    driver = Driver.objects.get(user=request.user)
    car = driver.car  # يا None يا سيارة موجودة

    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            new_car = form.save()
            if not car:
                driver.car = new_car
                driver.save()
            return redirect("drivers:driver_car")
    else:
        #يخلي البيانات تظهر
        form = CarForm(instance=car)

    return render(request, "drivers/driver_car.html", {
        "form": form,
        "car": car
    })

