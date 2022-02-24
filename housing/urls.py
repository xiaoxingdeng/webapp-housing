from django.urls import path, include
from housing import views

urlpatterns = [
    path('', views.mainpage_action, name='home'),
    path('mainpage', views.mainpage_action, name='mainpage'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('profile', views.profile_action, name='profile'),
    path('other_profile/<int:user_id>', views.other_profile_action, name='other_profile'),
    path('add_item', views.addItem_action, name='add_item'),
    path('delete_item/<int:item_id>', views.delete_action, name='delete_item'),
    path('add_img/<int:id>', views.add_img, name='add_img'),
    path('message', views.message_action, name='message'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('send-msg/<int:msg_box_id>',views.send_msg_action, name='send-msg'),
    path('send-msg-house/<int:user_id>',views.send_msg2house_action, name='send-msg-house'),
    path('get-msg',views.get_msg, name='get-msg'),
    path('get-msg-from-box/<int:box_id>',views.get_msg_from_box, name='get-msg-from-box'),
    path('img/<int:id>', views.get_img, name='img'),
    path('house_infor/<int:id>', views.get_houseinformation, name='house_infor'),
    path('filter', views.filter, name = 'filter'),
    path('get_image/<int:id>', views.get_image, name='get_image'),
    path('post_images/<int:id>', views.get_innerphoto, name='innerphoto'),
]

