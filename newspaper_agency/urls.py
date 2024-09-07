from django.contrib import admin
from django.urls import path
from rest_framework.authtoken import views as tokenview
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *
from django.urls import include
from django.contrib.auth.decorators import login_required
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    
    path('addCustomer/', AddCustomer.as_view(),name='addCustomer'),
    path('editCustomer/', EditCustomerSubscription.as_view(),name='editCustomer'),
    path('addDistributor/', AddDistributor.as_view(),name='addDistributor'),
    path('addPublication/', AddPublication.as_view(),name='addPublication'),
    path('editPublication/', EditPublication.as_view(),name='editPublication'),
    path('withHold/', WithHoldCustomer.as_view(),name='withHold'),
    path('allocateArea/', AllocateArea.as_view(),name='allocateArea'),
    path('distributorCheck/', DistributorAllocation.as_view(),name='distributorCheck'),
    path('distributorPayment/', DistributorPayment.as_view(),name='distributorPayment'),
    path('customerBills/', CustomersBills.as_view(),name='customerBills'),
    path('viewSummary/', ViewSummary.as_view(),name='viewSummary'),
    path('paymentReceipts/', PaymentReceipts.as_view(),name='paymentReceipts'),
    path('admin/', admin.site.urls),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
