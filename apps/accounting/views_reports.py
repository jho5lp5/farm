"""
Vistas para reportes de texto/tablas de la academia
"""
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from http import HTTPStatus
from datetime import datetime
from decimal import Decimal

from .models import CashFlow
from ..hrm.models import Subsidiary


def reports_list(request):
    """Vista principal para reportes de texto/tablas"""
    if request.method == 'GET':
        subsidiary_set = Subsidiary.objects.all()
        
        # Obtener la sucursal del usuario actual
        user_subsidiary = None
        if hasattr(request.user, 'subsidiary') and request.user.subsidiary:
            user_subsidiary = request.user.subsidiary
        
        # Fecha actual para el filtro
        current_date = datetime.now()
        current_month = current_date.strftime('%Y-%m')
        
        return render(request, 'accounting/reports_list.html', {
            'subsidiary_set': subsidiary_set,
            'user_subsidiary': user_subsidiary,
            'current_month': current_month,
        })
