import pytz
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class ShopUser(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatars', blank=True, verbose_name='Avatar')
    age = models.PositiveSmallIntegerField(verbose_name='Age', default=18)

    activate_key = models.CharField(max_length=128, verbose_name='Ключ активации', blank=True, null=True)
    activate_key_expired = models.DateTimeField(blank=True, null=True)

    def is_activate_key_expired(self):
        if datetime.now(pytz.timezone(settings.TIME_ZONE)) > self.activate_key_expired + timedelta(hours=48):
            return True
        else:
            return False

    def activate_user(self):
        self.is_active = True
        self.activate_key = None
        self.activate_key_expired = None
        self.save()


class ShopUserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'W'
    OTHERS = 'O'

    GENDERS = (
        (MALE, 'М'),
        (FEMALE, 'Ж'),
        (OTHERS, 'И'),
    )

    user = models.OneToOneField(ShopUser, unique=True, null=False, db_index=True, on_delete=models.CASCADE)
    tagline = models.CharField(verbose_name='теги', max_length=128, blank=True)
    about_me = models.TextField(verbose_name='о себе')
    gender = models.CharField(verbose_name='пол', choices=GENDERS, default=OTHERS, max_length=1)

    @receiver(post_save, sender=ShopUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            ShopUserProfile.objects.create(user=instance)

    @receiver(post_save, sender=ShopUser)
    def update_user_profile(sender, instance, **kwargs):
        instance.shopuserprofile.save()