from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()
        return user
        
    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='profile_pictures/default.jpg')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Required for createsuperuser
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'soundscore_user'


