from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import RiderRequestForm
from .models import RiderRequest, CommentRiderRequest, JoinRequestTrip
from riders.models import Rider
from main.models import City, Neighborhood, Day




# Create your views here.

#Create new rider request
@login_required
def create_rider_request(request:HttpRequest):

    try:
        rider = Rider.objects.get(user=request.user)
    except Rider.DoesNotExist:
        return render(request, "403.html", status=403)  # ⭐


    if request.method == "POST":
        rider_request_form = RiderRequestForm(request.POST)
        if rider_request_form.is_valid():
            rider_request = rider_request_form.save(commit=False)
            rider_request.rider = rider
            rider_request.save()
            rider_request_form.save_m2m()
            messages.success(request, "Created rider request add successfully", "alert-success")
            return redirect('rider_request:list_rider_request')
        else:
            messages.error(request, "Please correct the errors below", "alert-danger")
    else:
        rider_request_form = RiderRequestForm()
        
        context = { 'cities':City.objects.all(), 'neighborhoods':Neighborhood.objects.all(), 
                   'days':Day.objects.all(),"rider_request_form":rider_request_form, "status":RiderRequest.Status.choices}

    return render(request, "rider_request/rider_request_form.html",context)


#Showing the list of rider request ads
def list_rider_request(request:HttpRequest):

    rider_requests = RiderRequest.objects.all().order_by('-id') 

    page_number = request.GET.get("page",1)
    paginator = Paginator(rider_requests, 6)
    rider_requests_page =paginator.get_page(page_number)
    
    return render(request, "rider_request/rider_request_ads_list.html", {'rider_requests': rider_requests_page})


   # Showing the details of rider request ads
def detail_rider_request(request:HttpRequest, rider_request_id):

    rider_request = RiderRequest.objects.filter(id=rider_request_id).first()
    if not rider_request:
        return render(request, "404.html", status=404)  # ⭐
    
    rider = rider_request.rider
    comments = rider_request.comments.filter(parent__isnull=True).order_by('-created_at')
    

    join_requests = rider_request.all_join_requests.filter(rider_status='PENDING')


    approved_requests = rider_request.all_join_requests.filter(rider_status='APPROVED')

    # حساب عدد الركاب المقبولين 
    approved_count = approved_requests.count()
    
    # حساب عدد المقاعد المتبقية
    remaining_seats = max(0, rider_request.total_riders - approved_count)

    has_joined = False
    user_status = None

    if request.user.is_authenticated and hasattr(request.user, 'rider'):
        join_req = JoinRequestTrip.objects.filter(
            rider_request=rider_request, 
            rider=request.user.rider
        ).first()
        
        if join_req:
            has_joined = True
            user_status = join_req.get_rider_status_display()

    is_driver_user = hasattr(request.user, "driver")

   
    return render(request, "rider_request/rider_request_detail.html", {
        'rider_request': rider_request, 
        'rider': rider,
        'comments': comments, 
        'is_driver_user': is_driver_user, 
        'has_joined': has_joined, 
        'user_status': user_status, 
        'join_requests': join_requests, 
        'approved_requests': approved_requests, 
        'remaining_seats': remaining_seats 
    })

#Allowing driver to change the request status
@login_required   # ⭐
def accept_rider_request(request, rider_request_id):

    rider_request = RiderRequest.objects.filter(id=rider_request_id).first()
    if not rider_request:
        return render(request, "404.html", status=404)  

    if not hasattr(request.user, "driver"):
        return render(request, "403.html", status=403)  

    rider_request.status = RiderRequest.Status.A
    rider_request.driver = request.user.driver
    rider_request.save()

    return redirect(
        'rider_request:detail_rider_request',
        rider_request_id=rider_request_id
    )


#طلب_انضمام
@login_required
def join_trip_action(request, rider_request_id):

    # ⭐ جلب الإعلان
    rider_req_ad = RiderRequest.objects.filter(id=rider_request_id).first()
    if not rider_req_ad:
        return render(request, "404.html", status=404)  # ⭐ إعلان غير موجود

    # ⭐ هنا بالضبط نحط شرط الراكب
    if not hasattr(request.user, "rider"):
        return render(request, "403.html", status=403)  # ⭐ مو راكب

    # ⭐ الراكب ما يقدر ينضم لإعلانه نفسه
    if rider_req_ad.rider == request.user.rider:
        return render(request, "403.html", status=403)  # ⭐ صلاحيات

    # ⭐ إنشاء طلب الانضمام
    JoinRequestTrip.objects.get_or_create(
        rider=request.user.rider,
        rider_request=rider_req_ad,
        defaults={'rider_status': 'PENDING'}
    )

    return redirect(
        'rider_request:detail_rider_request',
        rider_request_id=rider_request_id
    )


#تحديث_حالة_الطلب_من _قبل_المعلن
@login_required
def update_request_status(request, join_id, status):

    join_req = JoinRequestTrip.objects.filter(id=join_id).first()
    if not join_req:
        return render(request, "404.html", status=404)  # ⭐ صفحة 404 الخاصة

    if not hasattr(request.user, "rider"):
        return render(request, "403.html", status=403)  # ⭐ مو راكب

    if join_req.rider_request.rider != request.user.rider:
        return render(request, "403.html", status=403)  # ⭐ مو صاحب الإعلان

    if status not in ['APPROVED', 'REJECTED']:
        return render(request, "403.html", status=403)  # ⭐ أكشن غير مسموح

    join_req.rider_status = status
    join_req.save()

    return redirect(
        'rider_request:detail_rider_request',
        rider_request_id=join_req.rider_request.id
    )

#update the rider request ads form
@login_required
def update_rider_request(request, pk):
  
    rider_request = RiderRequest.objects.filter(
        pk=pk,
        rider__user=request.user
    ).first()

    if not rider_request:
        return render(request, "404.html", status=404)  # ⭐
    
    if request.method == "POST":
       
        form = RiderRequestForm(request.POST, instance=rider_request)
        if form.is_valid():
            updated_request = form.save()
            messages.success(request, "The rider request ads updated successfully", "alert-success")
            return redirect('rider_request:list_rider_request')
    else:
      
        form = RiderRequestForm(instance=rider_request)

    context = { 'rider_request_form': form,'rider_request': rider_request, 'cities': City.objects.all(),'neighborhoods': Neighborhood.objects.all(),'days': Day.objects.all(),'status': RiderRequest.Status.choices
    }
    return render(request, "rider_request/rider_request_update_form.html", context)

@login_required
def delete_rider_request(request, pk):
   
    rider_request = RiderRequest.objects.filter(
        pk=pk,
        rider__user=request.user
    ).first()

    if not rider_request:
        return render(request, "404.html", status=404)  # ⭐
    
    if request.method == "POST":
        rider_request.delete()
        messages.success(request, "The rider request ads deleted successfully", "alert-success")
        return redirect('rider_request:list_rider_request')
    
    return render(request, "rider_request/rider_request_confirm_delete.html", {'rider_request': rider_request})
 

 
@login_required
def add_comment(request: HttpRequest, rider_request_id):

    if request.method != "POST":
        return render(request, "403.html", status=403)  # ⭐


    rider_request = RiderRequest.objects.filter(id=rider_request_id).first()
    if not rider_request:
        return render(request, "404.html", status=404)  # ⭐
    
    rider_owner = rider_request.rider.user  #  صاحب الإعلان (الراكب)

    content = (request.POST.get("comment") or "").strip()
    if not content:
        messages.error(request, "Comment cannot be empty")
        return redirect("rider_request:detail_rider_request", rider_request_id=rider_request_id)  

    parent_id = request.POST.get("parent_id")
    parent = None

    # helper: نطلع Root Comment لأي رسالة داخل نفس المحادثة
    def get_root(c: CommentRiderRequest) -> CommentRiderRequest:
        while c.parent_id is not None:
            c = c.parent
        return c

    #  helper: نطلع آخر رسالة في السلسلة (Leaf) عشان نخلي الرد دائماً على آخر شي
    def get_last_in_chain(c: CommentRiderRequest) -> CommentRiderRequest:
        # نفترض إن المحادثة خط واحد (بنفرضه بالصلاحيات)
        while c.replies.exists():
            c = c.replies.order_by("created_at").last()
        return c

    if parent_id:
        #  الرد لازم يكون على آخر رسالة في السلسلة (يعني نمنع الرد على رسالة قديمة)
        parent = CommentRiderRequest.objects.filter(
            id=parent_id,
            rider_request=rider_request
        ).first()

        if not parent:
            return render(request, "404.html", status=404)  # ⭐
        root = get_root(parent)  
        thread_driver = root.user  #  السائق اللي بدأ المحادثة

        #  تمنع سائق ثاني يدخل يرد على محادثة مو له
        if request.user != rider_owner and request.user != thread_driver:
            return render(request, "403.html", status=403)  # ⭐

        #  نفرض الرد يكون على آخر رسالة فقط
        last_msg = get_last_in_chain(root)  
        if parent.id != last_msg.id:
            #  إذا حاول يرد على تعليق قديم، نحوله لآخر رسالة
            parent = last_msg

        #  التناوب: إذا آخر رسالة من السائق - اللي يرد الآن لازم الراكب صاحب الإعلان
        # إذا آخر رسالة من الراكب صاحب الإعلان - اللي يرد الآن لازم نفس السائق عشان ما اكثر ردود
        if parent.user == thread_driver:
            # آخر رسالة سائق - الآن لازم الراكب
            if request.user != rider_owner:
                return render(request, "403.html", status=403)  # ⭐

        else:
            # آخر رسالة راكب - الآن لازم نفس السائق
            if request.user != thread_driver:
                return render(request, "403.html", status=403)  # ⭐


        #  أنشئ الرد
        CommentRiderRequest.objects.create(
            user=request.user,
            rider_request=rider_request,
            comment=content,              #  (استخدمنا content بعد strip)
            parent=parent
        )

    else:
        #  Root Comment: فقط السائق يكتب، الراكب (صاحب الإعلان) ممنوع يبدأ
        if request.user == rider_owner:
            return render(request, "403.html", status=403)  # ⭐


        #  أنشئ تعليق رئيسي (بداية محادثة)
        CommentRiderRequest.objects.create(
            user=request.user,
            rider_request=rider_request,
            comment=content,
            parent=None
        )

    return redirect("rider_request:detail_rider_request", rider_request_id=rider_request_id)  
