from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from trips.models import JoinTrip
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
    rider_html = render_to_string("main/mail/subscribes_rider.html", {"rider":join_trip.rider, "trip":trip, "start_date": join_trip.start_date, "end_date": join_trip.end_date,
        "days": days_count, "price": total_price})   
    email_to_rider=EmailMessage("تم الاشتراك في الباقة", rider_html,settings.EMAIL_HOST_USER,[join_trip.rider.user.email] )
    email_to_rider.content_subtype="html"
    email_to_rider.send()

    #ارسال رسالة للسائق انه في مشترك جديد
    driver_html = render_to_string("main/mail/new_subscription_driver.html", {"driver": trip.driver, "rider": join_trip.rider, "trip": trip,
        "start_date": join_trip.start_date, "end_date": join_trip.end_date})   
    email_to_driver=EmailMessage("متدرب جديد اشترك معك", driver_html,settings.EMAIL_HOST_USER,[trip.driver.user.email] )
    email_to_driver.content_subtype="html"
    email_to_driver.send()

    
    messages.success(request, "You have successfully subscribed to the trip.", "alert-success")
    return redirect("trips:trip_detail", trip_id=trip.id)

@login_required
def payment_trip_cancel(request:HttpRequest):
    messages.warning(request, "The payment process has been cancelled.", "alert-warning")
    return redirect(request.META.get('HTTP_REFERER') or "/")
   