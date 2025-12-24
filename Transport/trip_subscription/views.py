from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from riders.models import Rider
from trips.models import JoinTrip
from rider_request.models import JoinRequestTrip
from .models import TripSubscription
import stripe
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.

@login_required
def checkout_srtipe_view(request:HttpRequest, join_trip_id):

    stripe.api_key = settings.STRIPE_SECRET_KEY
    #الباقة
    try:
        join_trip =JoinTrip.objects.select_related('trip','rider','trip__driver').get(pk=join_trip_id, rider=request.user.rider)
    except JoinTrip.DoesNotExist:
        messages.error(request,"Requested join does not exit","alert-danger")
        return redirect(request.META.get('HTTP_REFERER'),"/")
    
    
    if join_trip.rider_status != 'APPROVED':
        messages.warning(request, "You cannot proceed with payment until your trip request is approved.","alert-warning")
        return redirect("accounts:profile_rider", rider_id=join_trip.rider.id)
    
    trip = join_trip.trip

    #التحقق من عدد المقاعد
    active_subscriptions =JoinTrip.objects.filter(
        trip=trip,
        rider_status='APPROVED',
        end_date__gte=timezone.now().date()
    ).count()

    remaining_riders =trip.total_riders - active_subscriptions

    if remaining_riders <= 0:
        messages.error(request,"Sorry, all seats for this trip are already booked.", "alert-warning")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    
    #حساب السعر على حسب عدد الايام الي حددها الراكب
    days_count = (join_trip.end_date - join_trip.start_date).days + 1
    total_price = days_count * trip.price

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data":{
                    "currency":"sar",
                    "product_data":{"name":f"Join to Trip with {trip.driver.user.username}"},
                    "unit_amount":int(total_price *100),
                },
                "quantity":1,
            } 
        ],
        metadata={
                "join_trip_id": str(join_trip.id),
                "rider_id": str(join_trip.rider.id),
        },
        success_url=request.build_absolute_uri(reverse("trip_subscription:payment_trip_success"))+ "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("trip_subscription:payment_trip_cancel")),
    )
    return redirect(session.url)


@login_required
def payment_trip_success(request:HttpRequest):
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Invalid payment session.", "alert-danger")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    

    try:
        session =stripe.checkout.Session.retrieve(session_id)
    except Exception:
        messages.error(request,"Unable to verify the payment process.", "alert-danger")
        return redirect(request.META.get('HTTP_REFERER') or"/")
    
    #التأكد من ان عملية الدفع تمت
    if session.payment_status != "paid":
        messages.error(request, "The payment was not completed successfully.", "alert-warning")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    
    join_trip_id = session.metadata.get("join_trip_id")
    rider_id = session.metadata.get("rider_id")

    try:
        join_trip =JoinTrip.objects.select_related('trip','rider').get(pk=join_trip_id, rider_id=rider_id)
    except JoinTrip.DoesNotExist:
        messages.error(request,"","alert-danger")
        return redirect(request.META.get('HTTP_REFERER'),"/")
    
    
    if join_trip.rider_status != 'APPROVED':
        messages.warning(request, "Your trip request is no longer approved.","alert-warning")
        return redirect("/")
    
    trip = join_trip.trip

    #التحقق من عدد المقاعد
    active_subscriptions =JoinTrip.objects.filter(
        trip=trip,
        rider_status='APPROVED',
        end_date__gte=timezone.now().date()
    ).count()

    remaining_riders =trip.total_riders - active_subscriptions

    if remaining_riders <= 0:
        messages.error(request,"Sorry, all seats for this trip are already booked.", "alert-warning")
        return redirect(request.META.get('HTTP_REFERER') or "/")
    
  
    subscription, created = TripSubscription.objects.get_or_create(join_trip=join_trip, rider=join_trip.rider)

    if not created:
        messages.info(request,"You are already subscribed to this trip.","alert-info")
        return redirect("/")
    

    #حساب السعر على حسب عدد الايام الي حددها الراكب
    days_count = (join_trip.end_date - join_trip.start_date).days + 1
    total_price = days_count * trip.price
    
    # إرسال رسالة للراكب اذا اشترك
    rider_html = render_to_string("trip_subscription/subscribes_rider.html", {"driver": trip.driver, "rider":join_trip.rider, "trip":trip, "start_date": join_trip.start_date, "end_date": join_trip.end_date,
        "days": days_count, "price": total_price})   
    email_to_rider=EmailMessage("تم الاشتراك في الباقة", rider_html,settings.EMAIL_HOST_USER,[join_trip.rider.user.email] )
    email_to_rider.content_subtype="html"
    email_to_rider.send()

    #ارسال رسالة للسائق انه في مشترك جديد
    driver_html = render_to_string("trip_subscription/new_subscription_driver.html", {"driver": trip.driver, "rider": join_trip.rider, "trip": trip,
        "start_date": join_trip.start_date, "end_date": join_trip.end_date})   
    email_to_driver=EmailMessage("متدرب جديد اشترك معك", driver_html,settings.EMAIL_HOST_USER,[trip.driver.user.email] )
    email_to_driver.content_subtype="html"
    email_to_driver.send()

    
    messages.success(request, "You have successfully subscribed to the trip.", "alert-success")
    return redirect("trips:trip_detail_view", trip_id=trip.id)


@login_required
def checkout_join_request_view(request: HttpRequest, join_request_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    rider = request.user.rider

    try:
        join_request = JoinRequestTrip.objects.select_related(
            'rider_request',
            'rider_request__driver',
            'rider'
        ).get(pk=join_request_id)
    except JoinRequestTrip.DoesNotExist:
        messages.error(request, "Requested join does not exist.")
        return redirect("accounts:profile_rider", rider_id=rider.id)

    # صلاحية الدفع: المنضم أو منشئ الطلب
    if not (
        join_request.rider == rider
        or join_request.rider_request.rider == rider
    ):
        return render(request, "403.html", status=403)

    # لازم يكون الطلب مقبول
    if join_request.rider_status != 'APPROVED':
        messages.warning(request, "You cannot pay until the request is approved.")
        return redirect("accounts:profile_rider", rider_id=rider.id)

    # منع الدفع المكرر لنفس الشخص
    if TripSubscription.objects.filter(
        join_request_trip=join_request,
        rider=rider
    ).exists():
        messages.info(request, "You have already subscribed to this trip.")
        return redirect("accounts:profile_rider", rider_id=rider.id)

    trip = join_request.rider_request

    days_count = (trip.end_date - trip.start_date).days + 1
    total_price = days_count * trip.price

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "sar",
                "product_data": {
                    "name": f"Join Trip with {trip.driver.user.username}"
                },
                "unit_amount": int(total_price * 100),
            },
            "quantity": 1,
        }],
        metadata={
            "join_request_trip_id": str(join_request.id),
            "payer_rider_id": str(rider.id),
        },
        success_url=request.build_absolute_uri(
            reverse("trip_subscription:payment_join_request_success")
        ) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(
            reverse("trip_subscription:payment_trip_cancel")
        ),
    )

    return redirect(session.url)


@login_required
def payment_join_request_success(request: HttpRequest):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Invalid payment session.")
        return redirect("accounts:profile_rider", rider_id=request.user.rider.id)

    session = stripe.checkout.Session.retrieve(session_id)
    join_request_id = session.metadata.get("join_request_trip_id")
    payer_id = session.metadata.get("payer_rider_id")

    if not join_request_id or not payer_id:
        messages.error(request, "Invalid payment data.")
        return redirect("accounts:profile_rider", rider_id=request.user.rider.id)

    payer = get_object_or_404(Rider, id=payer_id)
    join_request = get_object_or_404(
        JoinRequestTrip.objects.select_related('rider_request','rider'),
        pk=join_request_id
    )

    # صلاحية الدفع
    if not (join_request.rider == request.user.rider or join_request.rider_request.rider == request.user.rider):
        return render(request, "403.html", status=403)

    if session.payment_status != "paid":
        messages.error(request, "Payment not completed.")
        return redirect("accounts:profile_rider", rider_id=payer.id)

    if join_request.rider_status != 'APPROVED':
        messages.warning(request, "Your request is no longer approved.")
        return redirect("accounts:profile_rider", rider_id=payer.id)

    # تحقق من الاشتراك مسبقًا لنفس الراكب + الطلب
    subscription_exists = TripSubscription.objects.filter(
        join_request_trip=join_request,
        rider=payer
    ).exists()

    if subscription_exists:
        messages.info(request, "You are already subscribed.")
        return redirect("accounts:profile_rider", rider_id=payer.id)

    # إنشاء الاشتراك باسم الدافع
    TripSubscription.objects.create(
        rider=payer,
        join_request_trip=join_request
    )

    messages.success(request, "Subscription completed successfully.")
    return redirect("accounts:profile_rider", rider_id=payer.id)

@login_required
def payment_trip_cancel(request:HttpRequest):
    messages.warning(request, "The payment process has been cancelled.", "alert-warning")
    return redirect(request.META.get('HTTP_REFERER') or "/")
   