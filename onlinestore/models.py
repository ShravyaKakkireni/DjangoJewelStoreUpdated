from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
import uuid

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=191)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='products_images/', blank=True)
    products_count = models.IntegerField()

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        user = self.model(
            username=username,
            email=email,
            password=password
        )
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    #last_login = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'address']
    
    objects = UserManager()

    def __str__(self):
        return self.username


class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return "{}:{}".format(self.product.name, self.id)

    def update_quantity(self, quantity):
        self.quantity = self.quantity + quantity
        self.save()

    def total_cost(self):
        return self.quantity * self.price


class Order(models.Model):
    name = models.CharField(max_length=191)
    email = models.EmailField()
    #postal_code = models.IntegerField()
    address = models.CharField(max_length=191)
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cancellation_token = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return "{}:{}".format(self.id, self.email)

    def total_cost(self):
        return sum([ li.cost() for li in self.lineitem_set.all() ] )


class LineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}:{}".format(self.product.name, self.id)

    def cost(self):
        return self.price * self.quantity

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
