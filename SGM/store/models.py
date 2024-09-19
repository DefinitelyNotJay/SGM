from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class Customer(models.Model):
    username = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=20)
    join_date = models.DateTimeField(auto_now_add=True)
    class GenderChoices(models.Choices):
        MALE = 'M'
        FEMALE = 'F'
        OTHERS = 'O'
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Category(models.Model):
    name = models.CharField(max_length=50)

class Product(models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.IntegerField()
    add_date = models.DateTimeField(default=datetime.now())
    categories = models.ManyToManyField(Category)

class Order(models.Model):
    class StatusChoices(models.Choices):
        PAID = "P"
        UNPAID = "U"
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    date = models.DateTimeField(default=datetime.now())
    status = models.CharField(max_length=16, choices=StatusChoices.choices)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

class LoyaltyPoints(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    points = models.IntegerField()
