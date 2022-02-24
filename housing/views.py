from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, Http404

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from django.utils import timezone
import json
import numpy as np

from housing.forms import *
from housing.models import *

@login_required
def mainpage_action(request):
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')

    hprofiles_list = HProfile.objects.all()
    houseNumInPage = 15
    paginator = Paginator(hprofiles_list, houseNumInPage) # Show 25 contacts per page
    page = request.GET.get('page')
    hprofiles_pages = paginator.get_page(page)
    ## filter housing for current page

    context = {'hprofiles': hprofiles_list,
                'form': HProfileForm(),
                'hprofiles_pages':hprofiles_pages
                }
    if(request.method == 'GET'):
        return render(request, 'housing/mainpage.html', context)
    
    return render(request, 'housing/mainpage.html', context)

@login_required
def addItem_action(request):
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')
    
    if request.method == 'GET':
        c = HProfileForm()
        context = { 'form': c}
        return render(request, 'housing/add_item.html', context)

    entry = HProfile()
    entry.posted_by=request.user
    create_form = HProfileForm(request.POST, request.FILES, instance=entry)
    images=request.FILES.getlist('images')
    if not create_form.is_valid():
        context = { 'form': create_form}
        print("form failure")
        return render(request, 'housing/add_item.html', context)   
    create_form.save()
    print(entry.address)
    for image in images:
        photo = Images(hprofile = entry, image =image)
        photo.save()
    message = 'New house posted'
    edit_form = ProfileForm(instance=entry)
    context = { 'message': message, 'form': edit_form }
    return render(request, 'housing/add_item.html', context)

@login_required
def delete_action(request, item_id):
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')

    context = { 'items': HProfile.objects.all() }

#    if request.method != 'POST':
#        context['error'] = 'Deletes must be done using the POST method'
#        return render(request, 'housing/profile.html', context)

    # Deletes the item if present in the database.
    try:
        item_to_delete = HProfile.objects.get(id=item_id)
        if request.user.username != item_to_delete.posted_by.username:
            context['error'] = 'You can only delete items you have created.'
            return render(request, 'housing/profile.html', context)

        item_to_delete.delete()
        return redirect('profile')
    except ObjectDoesNotExist:
        context['error'] = 'The item did not exist.'
        return render(request, 'housing/profile.html', context)

def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'housing/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'housing/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':

        context['form'] = RegisterForm()
        return render(request, 'housing/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'housing/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
    ## add a Profile when a user register
    new_profile = Profile(user=new_user)
    new_profile.save()
    return redirect(reverse('home'))

@login_required
def profile_action(request) :
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')
    context = {}
    if  not Profile.objects.filter(user = request.user.id).exists():
        new_profile = Profile(user=request.user)
        new_profile.save()
    profile_item = Profile.objects.get(user=request.user)
    cur_user = Profile.objects.get(user=request.user)
    # TODO: add filter in html to get the houses info of this profile user
    houses = HProfile.objects.filter(posted_by=request.user)
    context['houses'] = houses
    #cur_user = request.user
    context['profile_item'] = profile_item

    if request.method == 'GET':
        context['form'] = ProfileForm(initial={'description':profile_item.description})
        return render(request, 'housing/profile.html', context)

    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'housing/profile.html', context)

    # click submit to update the profile content
    if request.method == 'POST':
        ## click submit
        profile_item.description = form.cleaned_data['description']
        if form.cleaned_data['profile_picture']:
            profile_item.profile_picture = form.cleaned_data['profile_picture']
            profile_item.content_type = form.cleaned_data['profile_picture'].content_type
        profile_item.save()
        context['profile_item'] = profile_item
        context['form'] = form
        #context['form'] = ProfileForm(initial={'description':profile_item.description})
    return render(request, 'housing/profile.html', context)

@login_required
def other_profile_action(request, user_id) :
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')
    other_user = User.objects.get(id = user_id)
    profile_item = Profile.objects.get(user_id = user_id)
    cur_user_profile = Profile.objects.get(user_id = request.user.id)
    context = {}
    context['profile_item'] = profile_item
    context['profile_user'] = other_user
    houses = HProfile.objects.filter(posted_by=other_user)
    context['houses'] = houses
    
    return render(request, 'housing/otherprofile.html', context)


@login_required
def add_img(request, id):
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')
    item = get_object_or_404(Profile, id=id)
    print('Picture #{} fetched from db: {} (type={})'.format(id, item.profile_picture, type(item.profile_picture)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.profile_picture:
        raise Http404

    return HttpResponse(item.profile_picture, content_type=item.content_type)

def message_action(request):
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')
    ## TODO: need to filter the user boxes
    context = {'boxes': MessageBox.objects.all()}
    if(request.method == 'GET'):
        return render(request, 'housing/message.html', context)
    
    return render(request, 'housing/message.html', context)


@login_required
def get_photo(request, id):
    item = get_object_or_404(HProfile, id=id)
    print('Picture #{} fetched from db: {} (type={})'.format(id, item.picture, type(item.picture)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.picture:
        raise Http404
    return HttpResponse(item.picture)

def get_image(request, id):
    item=get_object_or_404(Images, id=id)
    if not item.image:
        raise Http404
    return HttpResponse(item.image)

def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)

def get_innerphoto(request,id):
    item = get_object_or_404(Images, id=id)
    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.image:
        raise Http404
    return HttpResponse(item.image)
    
@login_required
def send_msg_action(request, msg_box_id): 
    print("send_msg action")
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
    
    if not 'csrfmiddlewaretoken' in request.POST or not request.POST['csrfmiddlewaretoken'] or request.POST['csrfmiddlewaretoken'] == 'unknown':
        return _my_json_error_response("You must use csrftocken", status=400)

    if not 'comment_text' in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter.", status=400)


    msgBox = MessageBox.objects.get(id=msg_box_id)
        
    new_item = MessageText(text=request.POST['comment_text'], 
                       texted_by = request.user,
                       comment_date_time = timezone.now(),
                       self_box = msgBox)
    new_item.save()
    return get_msg(request)

@login_required
def get_msg(request):
    print("get-msg")
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    response_boxes = []
    response_texts = []

    for item in MessageBox.objects.all():
        print("box")
        cur_box = {
            'id':item.id,
            'user2_name':item.user2_name,
            'user1_name': item.user1_name
        }
        response_boxes.append(cur_box)

    for item in MessageText.objects.all().order_by('-comment_date_time'):
        print("text")
        cur_text = {
            'id': item.id,
            'text': item.text,
            'texted_by_id': item.texted_by.id,
            'self_box_id':item.self_box.id, 
            'comment_date_time': item.comment_date_time.isoformat()
        }
        response_texts.append(cur_text)
        print(item.text)
    
    response_data = {'response_boxes':response_boxes,'response_texts':response_texts}
    response_json = json.dumps(response_data)

    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

@login_required
def get_msg_from_box(request, box_id):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    response_texts = []

    for item in MessageText.objects.all().order_by('-comment_date_time'):
        if item.self_box.id == box_id:
            cur_text = {
                'id': item.id,
                'text': item.text,
                'texted_by_id': item.texted_by.id,
                'self_box_id':item.self_box.id, 
                'comment_date_time': item.comment_date_time.isoformat()
            }
            response_texts.append(cur_text)
    
    response_data = {'response_texts':response_texts}
    response_json = json.dumps(response_data)

    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response
    
@login_required
def send_msg2house_action(request, user_id):
    if not request.user.email.endswith("@andrew.cmu.edu"):
        return render(request, 'housing/login.html')
    user2 = User.objects.get(id = user_id)
    ## check if there is previous chat
    user_list = [request.user.username, user2.username]
    user_list.sort()
    user1_user2_str_name = "_".join(user_list)
    if  (not MessageBox.objects.filter(user1_user2_str__name=user1_user2_str_name).exists()):
        new_box = MessageBox.objects.create(user1_user2_str_name=user1_user2_str_name, user1_name=user_list[0], user2_name=user_list[1])
        new_box.save()
    
    box_item = MessageBox.objects.get(user1_user2_str__name=user1_user2_str_name)
    context = {}
    context['boxes'] = box_item
    if request.method == 'GET':
        return render(request, 'housing/message.html', context)
    
    context['boxes'] = box_item
    return render(request, 'housing/message.html', context)
    
def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)

def get_similar(id):
    regions={'oakland':0,'squirrel':1,'shadyside':2}
    rommtypes={'studio':0,'2b1b':1,'2b2b':2,'3b1b':3,'3b2b':4,'3b3b':5,'others':6}
    housetypes={'house':0,'apartment':1}
    hprofile = get_object_or_404(HProfile,id=id)
    cur_hou=np.array([regions[hprofile.region],rommtypes[hprofile.room_type],housetypes[hprofile.house_type],hprofile.price/1000,hprofile.area/1000,hprofile.distance2cmu])
    rec=[]


    for house in HProfile.objects.all():
        if house.id==hprofile.id:
            continue
        temp=[]
        temp.append(house.id)
        hou=np.array([regions[house.region],rommtypes[house.room_type],housetypes[house.house_type],house.price/1000,house.area/1000,house.distance2cmu])
        dis=np.linalg.norm(hou-cur_hou)
        temp.append(dis)
        rec.append(temp)
    if len(rec)<3:
        return []
    rec=np.array(rec)
    rec=rec[np.argsort(rec[:,1])]
    return [get_object_or_404(HProfile,id=int(rec[0,0])),get_object_or_404(HProfile,id=int(rec[1,0])),get_object_or_404(HProfile,id=int(rec[2,0]))]

def get_houseinformation(request,id):
    hprofile = get_object_or_404(HProfile,id=id)
    images = Images.objects.filter(hprofile=hprofile)
    simis=get_similar(id)
    context = {}
    context['images']=images
    context['profile']=hprofile
    context['simis']=simis
    return render(request, 'housing/houseinformation.html', context )

@login_required
def get_img(request, id):
    item = get_object_or_404(HProfile, id=id)
    imgs = get_object_or_404(Images, hprofile=item)
    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    return HttpResponse(imgs[0].image.url)

def filter(request):
    if request.is_ajax():
        distance = request.POST.get("Distance")
        Region = request.POST.get("Region")
        Room = request.POST.get("Room")
        Building = request.POST.get("Building")
        Price = request.POST.get("Price")
        Size = request.POST.get("Size")
        response = []
        for housing in HProfile.objects.all():
            if Region:
                if housing.region != Region:
                    continue
            if Room:
                if housing.room_type != Room:
                    continue
            if Building:
                if housing.house_type != Building:
                    continue
            if Price:
                if Price == "0":
                    if housing.price > 500:
                        continue
                elif Price == "500":
                    if housing.price > 1000 or housing.price <= 500:
                        continue
                elif Price == "1000":
                    if housing.price > 1500 or housing.price <= 1000:
                        continue
                elif Price == "1500":
                    if housing.price > 2000 or housing.price <= 1500:
                        continue
                elif Price == "2000":
                    if housing.price <= 2000:
                        continue
            if Size:
                if Size == "0":
                    if housing.area > 500:
                        continue
                elif Size == "500":
                    if housing.area > 1000 or housing.area <= 500:
                        continue
                elif Size == "1000":
                    if housing.area > 1500 or housing.area <= 1000:
                        continue
                elif Size == "1500":
                    if housing.area > 2000 or housing.area <= 1500:
                        continue
                elif Size == "2000":
                    if housing.area <= 2000:
                        continue
            housing_item = {
                'id': housing.id,
                'room_type': housing.room_type,
                'address': housing.address,
                'price' : housing.price,
                'distance' : housing.distance2cmu,
                'latitude' : housing.latitude,
                'longtitude' : housing.longtitude
            }
            response.append(housing_item)
        if distance == "close":
                response.sort(key = myFunc)
        elif distance == "far":
                response.sort(reverse=True, key= myFunc)
        response_json = json.dumps(response)
        response = HttpResponse(response_json, content_type='application/json')
        return response

def myFunc(e):
    return e['distance']
