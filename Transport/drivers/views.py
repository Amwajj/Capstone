from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from .models import Driver, Car
from .forms import CarForm
from django.contrib import messages

# Create your views here.



@login_required
def driver_car_view(request: HttpRequest) -> HttpResponse:
    # جلب السائق الحالي
    driver = Driver.objects.filter(user=request.user).first()

    if not driver:
        messages.error(request, "No driver profile found. Please contact admin.")
        return redirect("accounts:profile_driver",driver_id=driver.id)

    # جلب السيارة المرتبطة بالسائق إذا وجدت
    car = getattr(driver, 'car', None)

    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            car = form.save()        # حفظ السيارة
            driver.car = car         # ربط السيارة بالسائق
            driver.save()
            messages.success(request, "Car information updated successfully.")
            return redirect("accounts:profile_driver",driver_id=driver.id)
    else:
        form = CarForm(instance=car)

    return render(request, "drivers/driver_car.html", {
        "form": form,
        "car": car
    })
