from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import *

from .views_pdf import export_sales_report_pdf

urlpatterns = [
    # URLs para gestión de cuentas/cajas
    path('cash/', login_required(cash_list), name='cash_list'),
    path('cash/create/', login_required(cash_create), name='cash_create'),
    path('cash/save/', login_required(cash_save), name='cash_save'),
    path('cash/get/', login_required(cash_get), name='cash_get'),
    path('cash/<int:cash_id>/edit/', login_required(cash_edit), name='cash_edit'),
    path('cash/update/', login_required(cash_update), name='cash_update'),
    
    # URLs para gestión de gastos (cashflow)
    path('cashflow/', login_required(cashflow_list), name='cashflow_list'),
    path('cashflow/create/', login_required(cashflow_create), name='cashflow_create'),
    path('cashflow/save/', login_required(cashflow_save), name='cashflow_save'),
    path('cashflow/get/', login_required(cashflow_get), name='cashflow_get'),
    path('cashflow/<int:cashflow_id>/edit/', login_required(cashflow_edit), name='cashflow_edit'),
    path('cashflow/update/', login_required(cashflow_update), name='cashflow_update'),
    path('cashflow/delete/', login_required(cashflow_delete), name='cashflow_delete'),
    
    # URLs auxiliares
    path('get-cash-accounts/', login_required(get_cash_accounts_by_subsidiary), name='get_cash_accounts_by_subsidiary'),

]
