from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import RegexValidator


class Profile(models.Model):
    description = models.CharField(blank=True, max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    profile_picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    msg_box_list = models.ManyToManyField(User, related_name='msg_box_list')

    def __str__(self):
        return 'id=' + str(self.id) + ',description="' + self.description + '"'

class HProfile(models.Model):
    description = models.TextField(blank=True, max_length=200)
    picture = models.FileField(blank=True, upload_to = "images/")
    posted_by = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    REGION_CHOICES = [
        ('oakland', 'oakland'),
        ('squirrel', 'squirrel'),
        ('shadyside', 'shadyside')
    ]
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    ROOM_TYPE_CHOICES = [
        ('studio', 'studio'),
        ('2b1b', '2b1b'),
        ('2b2b', '2b2b'),
        ('3b1b', '3b1b'),
        ('3b2b', '3b2b'),
        ('3b3b', '3b3b'),
        ('others', 'others'),
    ]
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES)
    HOUSE_TYPE_CHOICES = [
        ('house', 'house'),
        ('apartment', 'apartment'),
    ]
    address= models.CharField(max_length=50)
    house_type = models.CharField(max_length=50, choices=HOUSE_TYPE_CHOICES)
    price = models.IntegerField()
    area = models.IntegerField()
    distance2cmu = models.FloatField()
    latitude = models.FloatField(default=40.4433)
    longtitude = models.FloatField(default=-79.9436)

    def __str__(self):
        return 'id=' + str(self.id) + ',description="' + self.description + '"'

class Msg_str(models.Model):
    name = models.CharField(max_length=200, default=None, unique=True)

class Images(models.Model):
    hprofile = models.ForeignKey(HProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="post_images/")

class MessageBox(models.Model):
    #user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    #user2 = models.ForeignKey(User, default=None, on_delete=models.PROTECT, related_name='user2')
    user1_user2_str = models.ForeignKey(Msg_str, default=None, on_delete=models.PROTECT)
    user1_name = models.CharField(max_length=200, default=None)
    user2_name = models.CharField(max_length=200, default=None)
    #user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    #date_time = models.DateTimeField()

    @property
    def user1_user2_str_name(self):
        return self.user1_user2_str.name
    @user1_user2_str_name.setter
    def user1_user2_str_name(self, value):
        self.user1_user2_str, _ = Msg_str.objects.get_or_create(name=value)
    def __str__(self):
        return 'id=' + str(self.id)

class MessageText(models.Model):
    text = models.CharField(max_length=200)
    texted_by = models.ForeignKey(User, default=None,on_delete=models.PROTECT)
    #comment_profile = models.CharField(blank=True, max_length=200)
    comment_date_time = models.DateTimeField()
    self_box = models.ForeignKey(MessageBox, default=None, on_delete=models.PROTECT)

    def __str__(self):
        return 'id=' + str(self.id) + ',text="' + self.text + '"'
