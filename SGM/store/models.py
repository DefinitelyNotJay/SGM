from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20)
    join_date = models.DateTimeField(auto_now_add=True)
    class GenderChoices(models.Choices):
        MALE = 'M'
        FEMALE = 'F'
        OTHERS = 'O'
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.username + " " + self.nickname


class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
def product_image_path(instance, filename):
    # กำหนดเส้นทางที่ต้องการใน S3
    return f'products/{instance.id}/{filename}'

class Product(models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    add_date = models.DateTimeField(default=datetime.now())
    categories = models.ManyToManyField(Category)
    image_url = models.URLField(null=True, blank=True)
    daily_restock_quantity = models.IntegerField(default=50)
    def __str__(self):
        return self.name

class Order(models.Model):
    class StatusChoices(models.Choices):
        PAID = "P"
        UNPAID = "U"
        
    class PaymentMethodChoices(models.TextChoices):
        POMPAL = "QR Code(pompal)", "QR Code (Pompal)"
        CASH = "Cash", "เงินสด"
        
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField()
    date = models.DateTimeField(default=datetime.now())
    status = models.CharField(max_length=16, choices=StatusChoices.choices, default=StatusChoices.UNPAID)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices, default=PaymentMethodChoices.CASH)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

class LoyaltyPoints(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)