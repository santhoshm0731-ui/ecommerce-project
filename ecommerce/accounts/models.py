from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
from django.db.models import constraints, Q
from django.views.decorators.http import condition

types=[
    ('home','home'),
    ('office','office')
]

class UserManager(BaseUserManager):
      def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        if not phone:
            raise ValueError("Phone is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            phone=phone,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

      def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email=email,
            phone=phone,
            password=password,
            **extra_fields
        )

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    objects = UserManager()

    def __str__(self):
        return self.email

class Address(models.Model):
    customer=models.ForeignKey(User,on_delete=models.CASCADE,related_name="addresses")
    home_no=models.CharField(max_length=4)
    building_name=models.CharField(max_length=100)
    street=models.CharField(max_length=100)
    nearby_landmark=models.CharField(max_length=100)
    zip_code=models.CharField(max_length=10)
    type=models.CharField(max_length=100,choices=types)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    country=models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        constraints=[
            constraints.UniqueConstraint(
            fields=['customer'],
            condition=Q(is_default=True),
            name="one_default_address_per_customer"
             )
        ]

    def __str__(self):
        return self.street