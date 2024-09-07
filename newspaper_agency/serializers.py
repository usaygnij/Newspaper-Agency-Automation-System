from rest_framework import serializers, fields
from django import forms
from .models import Customers, Distributors, Publications, WithHold, Summary, Subscript
from django.contrib.auth.models import User
from rest_framework import permissions
from django.contrib.auth import get_user_model

class CustomersSerializer(serializers.ModelSerializer):
# subscription = fields.MultipleChoiceField(choices=CHOICES)
    class Meta:
        model = Customers
        fields = ('id', 'customer_name', 'address', 'pincode','phone', 'subscription')

class EditCustomersSerializer(serializers.ModelSerializer):
# subscription = fields.MultipleChoiceField(choices=CHOICES)
    class Meta:
        model = Subscript
        fields = ('id','phone', 'subscription')

class EditPubicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publications
        fields = ('id','paper_name', 'price')

class DistributorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributors
        fields = ('id','distributor_name', 'address', 'd_phone')

class PublicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publications
        fields = ('id','paper_name', 'language', 'description', 'price')

class WithHoldSerializer(serializers.ModelSerializer):
    phone = serializers.IntegerField()
    class Meta:
        model = WithHold
        fields = ('id','phone', 'from_date', 'to_date')

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ('id', 'date')

class AllocationSerializer(serializers.ModelSerializer):
    distributor_name = serializers.CharField(max_length=200)
    class Meta:
        model = Summary
        fields = ('id', 'distributor_name', 'date')

class DistributorPaymentSerializer(serializers.ModelSerializer):
    month = serializers.IntegerField(default=1)
    year = serializers.IntegerField(default=2018)
    class Meta:
        model = Distributors
        fields = ('id', 'distributor_name', 'month', 'year')

class CustomerBillsSerializer(serializers.ModelSerializer):
    month = serializers.IntegerField(default=1)
    year = serializers.IntegerField(default=2018)
    class Meta:
        model = Customers
        fields = ('id', 'month', 'year')

class PaymentReceiptSerializer(serializers.ModelSerializer):
    month = serializers.IntegerField(default=1)
    year = serializers.IntegerField(default=2018)
    amount = serializers.IntegerField(default=0)
    class Meta:
        model = Customers
        fields = ('id', 'phone', 'month', 'year','amount')
