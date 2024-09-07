from django.http import HttpResponse
from .models import Customers, Distributors, Publications, WithHold, Summary, Subscript
from .serializers import CustomersSerializer, DistributorsSerializer, PublicationsSerializer, WithHoldSerializer, SummarySerializer
from .serializers import EditCustomersSerializer, EditPubicationSerializer, AllocationSerializer, DistributorPaymentSerializer
from .serializers import CustomerBillsSerializer, PaymentReceiptSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import permissions
from django.contrib.auth import get_user_model,authenticate,login
from django.contrib.auth.decorators import login_required
from django.views.static import serve
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import get_template

import numpy as np
import pickle
from django.db.models import Count
from .functions import partition_list
from datetime import datetime
import pandas as pd
import fpdf
import json
import calendar

def index(request):
    return render(request, 'home.html')



class AddCustomer(generics.CreateAPIView):
    queryset = Customers.objects.all()
    serializer_class = CustomersSerializer

class EditCustomerSubscription(generics.CreateAPIView):
    serializer_class = EditCustomersSerializer

def create(self, request, *args, **kargs):
    serializer = EditCustomersSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    serializer1 = EditCustomersSerializer(Subscript.objects.get(phone=request.data['phone']))
    h = serializer1.data['subscription']
    Subscript.objects.all().delete()
    t = Customers.objects.get(phone=request.data['phone'])
    t.subscription.set(h)
    t.save()
    return Response("update successful")

class AddPublication(generics.CreateAPIView):
    queryset = Publications.objects.all()
    serializer_class = PublicationsSerializer

class EditPublication(generics.CreateAPIView):
    serializer_class = EditPubicationSerializer

    def create(self, request, *args, **kargs):
        Publications.objects.filter(paper_name=request.data['paper_name']). update(price=request.data['price'])
        return Response("update successful")

class AddDistributor(generics.CreateAPIView):
    queryset = Distributors.objects.all()
    serializer_class = DistributorsSerializer

class WithHoldCustomer(generics.CreateAPIView):
    serializer_class = WithHoldSerializer
    def create(self, request, *args, **kargs):
        withH = WithHold(from_date=request.data['from_date'],
    to_date=request.data['to_date'])
        withH.customer_id_id = Customers.objects.get(phone=request.data['phone']).id
        withH.save()
        return Response("update")

class AllocateArea(generics.CreateAPIView):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer
    def create(self, request, *args, **kargs):
        p = Customers.objects.values('pincode').order_by('pincode').annotate(count=Count('pincode'))
        count_list = list()
        pincode_list = list()
        for i in p:
            count_list.append(int(i['count']))
            pincode_list.append(i['pincode'])
        d_count = Distributors.objects.all().count()
        sol = partition_list(count_list, d_count)
        
        distributor = Distributors.objects.all()
        index = 0
        pin_no = 0
        for d in distributor:
            for i in range(len(sol[index])):
                ctms = Customers.objects.filter(pincode=pincode_list[pin_no])
                for c in ctms:
                    hold = WithHold.objects.filter(customer_id_id=c.id)
                    if hold:
                        for date in hold:
                            t_date = pd.to_datetime(request.data['date']).date()
                            s_date = date.from_date
                            e_date = date.to_date
                            if s_date <= t_date <= e_date:
                                None
                            else:
                                summ = Summary(distributor_id_id=d.id, customer_id_id=c.id,date=request.data['date'])
                                summ.save()
                        else:
                            summ = Summary(distributor_id_id=d.id, customer_id_id=c.id, date=request.data['date'])
                            summ.save()
                    pin_no = pin_no + 1
                index = index + 1
        return Response("areas allocated")

class DistributorAllocation(generics.CreateAPIView):
    queryset = Customers.objects.all()
    serializer_class = AllocationSerializer

    def post(self, request, *args, **kargs):
        d_id = Distributors.objects.get(distributor_name=request.data['distributor_name']).id
        ctms = Summary.objects.filter(distributor_id_id=d_id).filter(date=request.data['date'])
        c_list = list()
        for c in ctms:
            customer = CustomersSerializer(Customers.objects.get(id=c.customer_id_id))
            cus = dict()
            cus['customer_name'] = customer.data['customer_name']
            cus['address'] = customer.data['address']
            cus['pincode'] = customer.data['pincode']
            cus['phone'] = customer.data['phone']
            cus['subscriptions'] = list()
            for i in range(len(customer.data['subscription'])):
                cus['subscriptions'].append(Publications.objects.get(id=customer.data['subscription'][i]).paper_name)
            c_list.append(cus)
        return Response(c_list)

class DistributorPayment(generics.CreateAPIView):
    queryset = Customers.objects.all()
    serializer_class = DistributorPaymentSerializer

    def post(self, request, *args, **kargs):
        s_date = pd.to_datetime(request.data['year'] + '-' + request.data['month'] + '-1' ).date()
        e_date = pd.to_datetime(request.data['year'] + '-' + request.data['month'] + '-30').date()
        i = Distributors.objects.get(distributor_name=request.data['distributor_name']).id
        s = Summary.objects.filter(distributor_id_id=i).filter(date__range=(s_date, e_date))
        payment = 0
        for c in s:
            customer = CustomersSerializer(Customers.objects.get(id=c.customer_id_id))
            for i in range(len(customer.data['subscription'])):
                payment = payment + Publications.objects.get(id=customer.data['subscription'][i]).price
        return Response(payment/4)

class CustomersBills(generics.CreateAPIView):
    queryset = Customers.objects.all()
    serializer_class = CustomerBillsSerializer

    def post(self, request, *args, **kargs):
        s_date = pd.to_datetime(request.data['year'] + '-' + request.data['month'] + '-1' ).date()
        e_date = pd.to_datetime(request.data['year'] + '-' + request.data['month'] + '-30').date()
        customers = Customers.objects.all()

        for ctmr in customers:
            bill = dict()
            sub = Summary.objects.filter(customer_id_id=ctmr.id).filter(date__range=(s_date, e_date)).count()
            bill['Name'] = ctmr.customer_name
            bill['Month'] = request.data['month'] + '-' + request.data['year']
            bill['Bill'] = dict()
            c = CustomersSerializer(Customers.objects.get(phone=ctmr.phone))
        
            for i in range(len(c.data['subscription'])):
                name = Publications.objects.get(id=c.data['subscription'][i]).paper_name
                price = Publications.objects.get(id=c.data['subscription'][i]).price
                bill['Bill'][name] = price
                amt = 0
                bills = list()
                st = 'Name ' + bill['Name']
                bills.append(st)
                st = 'Month ' + bill['Month']
                bills.append(st)
                bills.append("Bills")
                for key, value in bill['Bill'].items():
                    st = ' ' + key + ' : ' + str(sub) + ' x' + str(value)
                    bills.append(st)
                    amt = amt + sub * value
                due = ctmr.due
                amt = amt + due
                st = 'Due ' + str(due)
                bills.append(st)
                st = 'Total Amount : Rs.' + str(amt)
                bills.append(st)

                Customers.objects.filter(id=ctmr.id).update(due=amt)

                if amt:
                    pdf = fpdf.FPDF(format='letter')
                    pdf.add_page()
                    pdf.image('logo.jpg',0,0,210,45)
                    pdf.set_font("Arial", size=12)
                    pdf.cell(100)
                    pdf.ln(30)
                    pdf.write(bill)

                    for i in bills:
                        pdf.write(5,i)
                        pdf.ln()
                    p = "bills/" + bill['Month'] + "/" + str(ctmr.id) + '_' + ctmr.customer_name + '.pdf'
                    pdf.output(p)
            return Response("Bills saved")

class ViewSummary(generics.CreateAPIView):
    queryset = Summary.objects.all()
    serializer_class = CustomerBillsSerializer

    def post(self, request, *args, **kargs):
        s_date = pd.to_datetime(request.data['year'] + '-' + request.data['month'] + '-1' ).date()
        e_date = pd.to_datetime(request.data['year'] + '-' + request.data['month'] + '-30').date()
        month = "Month : " + request.data['month'] + '-' + request.data['year'] + "\n\n"

        tit = "Customer phone publications received\n"
        customers = Customers.objects.all()
        summ = list()
        paper = dict()
        publica = Publications.objects.all()

        for p in publica:
            paper[p.paper_name] = 0

        for ctmr in customers:
            sub = Summary.objects.filter(customer_id_id=ctmr.id).filter(date__range=(s_date, e_date)).count()
            subscri = ''
            c = CustomersSerializer(Customers.objects.get(phone=ctmr.phone))

            for i in range(len(c.data['subscription'])):
                name = Publications.objects.get(id=c.data['subscription'][i]).paper_name
                paper[name] = paper[name] + sub
                subscri = subscri + ', ' + name + '-' + str(sub)

            st = ctmr.customer_name + "   " + ctmr.phone + " " + subscri
            summ.append(st)

        n = "\n\nDistribution of publications : "
        summ.append(n)
        tot = 0

        for key, value in paper.items():
            n = key + " : \t" + str(value)
            tot = tot + value
            summ.append(n)
        n = "Total publications delivered : \t" + str(tot)
        summ.append(n)
        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.image('logo.jpg',0,0,210,45)
        pdf.set_font("Arial", size=12)
        pdf.cell(100)
        pdf.ln(30)
        pdf.write(5, month)
        pdf.write(5,tit)

        for i in summ:
            pdf.write(5,i)
            pdf.ln()

        month = request.data['month'] + '-' + request.data['year']
        p = "bills/" + month + "/summary.pdf"
        pdf.output(p)
        return Response("Summary pdf saved")

class PaymentReceipts(generics.CreateAPIView):
    queryset = Customers.objects.all()
    serializer_class = PaymentReceiptSerializer

    def post(self, request, *args, **kargs):
        tit = "Payment Receipt\n\n"
        month = "Month " + request.data['month'] + '-' + request.data['year'] + "\n\n"

        customers = Customers.objects.get(phone=request.data['phone'])
        bills = list()
        st = 'Name ' + customers.customer_name
        bills.append(tit)
        bills.append(st)
        bills.append(month)
        due = "Due amount " + str(customers.due)
        bills.append(due)
        due = "Received amount " + str(request.data['amount'])
        bills.append(due)
        due = "Remaining due " + str(int(customers.due) - int(request.data['amount']))
        bills.append(due)

        Customers.objects.filter(id=customers.id).update(due=int(customers.due) - int(request.data['amount']))
        pdf = fpdf.FPDF(format='letter')
        pdf.add_page()
        pdf.image('logo.jpg',0,0,210,45)
        pdf.set_font("Arial", size=12)
        pdf.cell(100)
        pdf.ln(30)

        for i in bills:
            pdf.write(5,i)
            pdf.ln()

        m = request.data['month'] + '-' + request.data['year']
        p = "receipts/" + m + "/" + str(customers.id) + '_' + customers.customer_name + '.pdf'
        pdf.output(p)
        return Response("receipt pdf saved")