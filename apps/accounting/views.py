import itertools

from django.shortcuts import render
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views.generic import TemplateView, View, CreateView, UpdateView
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView
from http import HTTPStatus
import re
import locale
import decimal
import calendar

from .models import *
import pytz
from django.contrib.auth.models import User
import json
import requests
import decimal
import math
import random
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.template import loader
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import DatabaseError, IntegrityError
from django.core import serializers
from django.db.models import Min, Sum, Max, Q, Prefetch, Subquery, OuterRef, Value, IntegerField, Case, ExpressionWrapper, DecimalField, Count
from django.db.models.functions import ExtractYear
from farm import settings
import os
from decimal import Decimal
from django.db.models import F

from ..users.models import CustomUser
from ..hrm.models import Subsidiary


# =============================================================================
# VISTAS PARA GESTIÓN DE CUENTAS/CAJAS
# =============================================================================

def cash_list(request):
    """Vista principal del listado de cuentas/cajas"""
    if request.method == 'GET':
        subsidiary_set = Subsidiary.objects.all()
        currency_types = Cash.CURRENCY_TYPE_CHOICES
        
        return render(request, 'accounting/cash_list.html', {
            'subsidiary_set': subsidiary_set,
            'currency_types': currency_types,
        })
    elif request.method == 'POST':
        try:
            # Filtrar cuentas según parámetros
            subsidiary_id = request.POST.get('subsidiary')
            currency_type = request.POST.get('currency_type')
            
            cash_accounts = Cash.objects.all()
        
            if subsidiary_id and subsidiary_id != '0':
                cash_accounts = cash_accounts.filter(subsidiary_id=subsidiary_id)
            if currency_type and currency_type != '0':
                cash_accounts = cash_accounts.filter(currency_type=currency_type)

            cash_accounts = cash_accounts.select_related('subsidiary').order_by('name')

            tpl = loader.get_template('accounting/cash_list_grid.html')
            context = {
                'cash_accounts': cash_accounts,
            }

            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK)
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al cargar las cuentas: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def cash_create(request):
    """Vista para crear nueva cuenta/caja"""
    if request.method == 'GET':
        subsidiary_set = Subsidiary.objects.all()
        currency_types = Cash.CURRENCY_TYPE_CHOICES
        
        return render(request, 'accounting/cash_create.html', {
            'subsidiary_set': subsidiary_set,
            'currency_types': currency_types,
        })


@csrf_exempt
def cash_save(request):
    """Vista para guardar nueva cuenta/caja"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            name = request.POST.get('cash_name', '').strip()
            subsidiary_id = request.POST.get('subsidiary_id', '')
            account_number = request.POST.get('account_number', '').strip()
            currency_type = request.POST.get('currency_type', 'S')
            account_type = request.POST.get('account_type', 'C')
            
            # Validaciones básicas
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre de la cuenta es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not subsidiary_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar una sucursal'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Verificar si ya existe una cuenta con el mismo nombre en la misma sucursal
            if Cash.objects.filter(name__iexact=name, subsidiary_id=subsidiary_id).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Ya existe una cuenta con el nombre "{name}" en esta sucursal'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Crear la cuenta
            subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
            cash_obj = Cash(
                name=name.upper(),
                subsidiary=subsidiary_obj,
                account_number=account_number.upper() if account_number else None,
                currency_type=currency_type,
                account_type=account_type
            )
            cash_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cuenta creada exitosamente',
                'cash_id': cash_obj.id
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear la cuenta: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def cash_edit(request, cash_id):
    """Vista para editar cuenta existente"""
    try:
        cash_obj = Cash.objects.select_related('subsidiary').get(id=cash_id)
        subsidiary_set = Subsidiary.objects.all()
        currency_types = Cash.CURRENCY_TYPE_CHOICES
        
        return render(request, 'accounting/cash_edit.html', {
            'cash': cash_obj,
            'subsidiary_set': subsidiary_set,
            'currency_types': currency_types,
        })
        
    except Cash.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Cuenta no encontrada'
        }, status=HTTPStatus.NOT_FOUND)


@csrf_exempt
def cash_get(request):
    """Vista para obtener datos de una cuenta específica"""
    if request.method == 'POST':
        try:
            cash_id = request.POST.get('cash_id')
            if not cash_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de cuenta no proporcionado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cash_obj = Cash.objects.select_related('subsidiary').get(id=int(cash_id))
            
            # Preparar datos para el formulario
            cash_data = {
                'id': cash_obj.id,
                'name': cash_obj.name,
                'subsidiary_id': cash_obj.subsidiary.id,
                'account_number': cash_obj.account_number,
                'currency_type': cash_obj.currency_type,
                'account_type': cash_obj.account_type,
            }
            
            return JsonResponse({
                'success': True,
                'cash': cash_data
            }, status=HTTPStatus.OK)
            
        except Cash.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cuenta no encontrada'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener los datos de la cuenta: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def cash_update(request):
    """Vista para actualizar cuenta existente"""
    if request.method == 'POST':
        try:
            cash_id = request.POST.get('cash_id')
            if not cash_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de cuenta no proporcionado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cash_obj = Cash.objects.get(id=int(cash_id))
            
            # Obtener datos del formulario
            name = request.POST.get('cash_name', '').strip()
            subsidiary_id = request.POST.get('subsidiary_id', '')
            account_number = request.POST.get('account_number', '').strip()
            currency_type = request.POST.get('currency_type', 'S')
            account_type = request.POST.get('account_type', 'C')
            
            # Validaciones básicas
            if not name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre de la cuenta es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not subsidiary_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar una sucursal'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Verificar si ya existe una cuenta con el mismo nombre en la misma sucursal (excluyendo la actual)
            if Cash.objects.filter(name__iexact=name, subsidiary_id=subsidiary_id).exclude(id=cash_obj.id).exists():
                return JsonResponse({
                    'success': False,
                    'message': f'Ya existe una cuenta con el nombre "{name}" en esta sucursal'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Actualizar la cuenta
            subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
            cash_obj.name = name.upper()
            cash_obj.subsidiary = subsidiary_obj
            cash_obj.account_number = account_number.upper() if account_number else None
            cash_obj.currency_type = currency_type
            cash_obj.account_type = account_type
            cash_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cuenta actualizada correctamente'
            }, status=HTTPStatus.OK)
            
        except Cash.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cuenta no encontrada'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar la cuenta: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def cashflow_get(request):
    """Vista para obtener datos de un gasto específico - Solo para administradores"""
    if request.method == 'POST':
        try:
            # Verificar permisos de administrador
            if not (hasattr(request.user, 'has_access_to_all') and request.user.has_access_to_all):
                return JsonResponse({
                    'success': False,
                    'message': 'No tiene permisos para editar gastos. Solo los administradores pueden realizar esta acción.'
                }, status=HTTPStatus.FORBIDDEN)
            
            cashflow_id = request.POST.get('cashflow_id')
            if not cashflow_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de gasto no proporcionado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cashflow_obj = CashFlow.objects.select_related('cash', 'user').get(id=int(cashflow_id))
            
            # Preparar datos para el formulario
            cashflow_data = {
                'id': cashflow_obj.id,
                'transaction_date': cashflow_obj.transaction_date.strftime('%Y-%m-%d'),
                'type': cashflow_obj.type,
                'cash_id': cashflow_obj.cash.id,
                'type_expense': cashflow_obj.type_expense,
                'user_id': cashflow_obj.user.id,
                'document_type_attached': cashflow_obj.document_type_attached,
                'description': cashflow_obj.description,
                'serial': cashflow_obj.serial,
                'n_receipt': cashflow_obj.n_receipt,
                'operation_code': cashflow_obj.operation_code,
                'subtotal': float(cashflow_obj.subtotal),
                'igv': float(cashflow_obj.igv),
                'total': float(cashflow_obj.total),
                'way_to_pay': cashflow_obj.way_to_pay,
            }
            
            return JsonResponse({
                'success': True,
                'cashflow': cashflow_data
            }, status=HTTPStatus.OK)
            
        except CashFlow.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Gasto no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener los datos del gasto: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


@csrf_exempt
def cashflow_delete(request):
    """Vista para eliminar gasto existente - Solo para administradores"""
    if request.method == 'POST':
        try:
            # Verificar permisos de administrador
            if not (hasattr(request.user, 'has_access_to_all') and request.user.has_access_to_all):
                return JsonResponse({
                    'success': False,
                    'message': 'No tiene permisos para eliminar gastos. Solo los administradores pueden realizar esta acción.'
                }, status=HTTPStatus.FORBIDDEN)
            
            cashflow_id = request.POST.get('cashflow_id')
            if not cashflow_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de gasto no proporcionado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cashflow_obj = CashFlow.objects.get(id=int(cashflow_id))
            
            # Obtener información del gasto para el mensaje
            description = cashflow_obj.description
            amount = cashflow_obj.total
            
            # Eliminar el gasto
            cashflow_obj.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Gasto eliminado exitosamente: {description} - S/ {amount}'
            }, status=HTTPStatus.OK)
            
        except CashFlow.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Gasto no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar el gasto: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


# =============================================================================
# VISTAS PARA GESTIÓN DE GASTOS (CASHFLOW)
# =============================================================================

def cashflow_list(request):
    """Vista principal del listado de gastos"""
    if request.method == 'GET':
        document_types = CashFlow.DOCUMENT_TYPE_ATTACHED_CHOICES
        transaction_types = [('A', 'Apertura'), ('C', 'Cierre'), ('E', 'Entrada'), ('S', 'Salida')]  # Apertura, cierre, entrada y salida
        expense_types = CashFlow.TYPE_EXPENSE
        user_set = CustomUser.objects.filter(is_active=True, is_staff=False)
        subsidiary_set = Subsidiary.objects.all()
        # Fecha actual para los filtros
        peru_tz = pytz.timezone("America/Lima")
        date_now = datetime.now(peru_tz).strftime('%Y-%m-%d')
        
        # Obtener la sucursal del usuario actual
        user_subsidiary = None
        first_cash_account = None

        if hasattr(request.user, 'subsidiary') and request.user.subsidiary:
            user_subsidiary = request.user.subsidiary

        # Verificar si el usuario tiene permisos de administrador
        is_admin = hasattr(request.user, 'has_access_to_all') and request.user.has_access_to_all

        # Filtrar cajas según permisos del usuario
        if is_admin:
            # Usuario admin puede ver todas las cajas
            cash_accounts = Cash.objects.all().order_by('subsidiary_id')
            # Buscar la primera cuenta de tipo 'E' de cualquier sucursal
            first_cash_account = Cash.objects.filter(account_type='E').first()
        else:
            # Usuario normal solo ve cajas de su sucursal
            cash_accounts = Cash.objects.filter(subsidiary=user_subsidiary)
            # Buscar la primera cuenta de tipo 'E' de la sucursal del usuario
            if user_subsidiary:
                first_cash_account = Cash.objects.filter(
                    subsidiary=user_subsidiary,
                    account_type='E'
                ).first()

        # Si no hay cuenta de tipo 'E', buscar cualquier cuenta según permisos
        if not first_cash_account:
            if is_admin:
                first_cash_account = Cash.objects.first()
            elif user_subsidiary:
                first_cash_account = Cash.objects.filter(subsidiary=user_subsidiary).first()
        
        return render(request, 'accounting/cashflow_list.html', {
            'cash_accounts': cash_accounts,
            'document_types': document_types,
            'transaction_types': transaction_types,
            'expense_types': expense_types,
            'subsidiary_set': subsidiary_set,
            'user_set': user_set,
            'date_now': date_now,
            'user_subsidiary': user_subsidiary,
            'first_cash_account': first_cash_account,
            'is_admin': is_admin,
        })
    elif request.method == 'POST':
        try:
            # Filtrar gastos según parámetros
            cash_id = request.POST.get('cash_account')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            expense_type = request.POST.get('expense_type')
            
            cashflows = CashFlow.objects.filter(type__in=['S', 'A'])
        
            # Verificar permisos del usuario
            is_admin = hasattr(request.user, 'has_access_to_all') and request.user.has_access_to_all
            
            # Si no es admin, solo mostrar sus propios gastos
            if not is_admin:
                cashflows = cashflows.filter(user=request.user)
        
            if cash_id and cash_id != '0':
                cashflows = cashflows.filter(cash_id=cash_id)
            
            # Filtro por tipo de gasto (solo para admins)
            if is_admin and expense_type and expense_type != '0':
                cashflows = cashflows.filter(type_expense=expense_type)

            # Filtro por rango de fechas
            # Por defecto, si no se especifica, usar la fecha de hoy
            if not start_date and not end_date:
                # Si no se proporcionan fechas, usar la fecha de hoy
                peru_tz = pytz.timezone("America/Lima")
                today = datetime.now(peru_tz).date()
                cashflows = cashflows.filter(transaction_date=today)
            else:
                # Si se proporciona fecha de inicio, filtrar desde esa fecha
                if start_date:
                    cashflows = cashflows.filter(transaction_date__gte=start_date)
                # Si se proporciona fecha de fin, filtrar hasta esa fecha
                if end_date:
                    cashflows = cashflows.filter(transaction_date__lte=end_date)

            # Ordenar: aperturas primero, luego por id
            cashflows = cashflows.select_related('cash', 'user', 'cash__subsidiary').order_by(
                'type',  # Aperturas (A) aparecerán primero
                'id'
            )

            # Calcular totales
            # Entradas: tipo 'E' (Entrada) + tipo 'A' (Apertura)
            total_income = cashflows.filter(type__in=['E', 'A']).aggregate(total=Sum('total'))['total'] or 0
            # Salidas: tipo 'S' (Salida)
            total_expenses = cashflows.filter(type='S').aggregate(total=Sum('total'))['total'] or 0
            # Balance: Entradas - Salidas
            net_balance = total_income - total_expenses

            # Totales por tipo de gasto
            expense_totals = {}
            for expense_code, expense_name in CashFlow.TYPE_EXPENSE:
                total = cashflows.filter(type__in=['S', 'A'], type_expense=expense_code).aggregate(
                    total=Sum('total')
                )['total'] or 0
                expense_totals[expense_code] = total

            tpl = loader.get_template('accounting/cashflow_list_grid.html')
            context = {
                'cashflows': cashflows,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_balance': net_balance,
                'expense_totals': expense_totals,
                # 'date_now': date_now,
            }

            return JsonResponse({
                'grid': tpl.render(context, request),
            }, status=HTTPStatus.OK)
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al cargar los gastos: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def cashflow_create(request):
    """Vista para crear nuevo gasto"""
    if request.method == 'GET':
        cash_accounts = Cash.objects.all()
        document_types = CashFlow.DOCUMENT_TYPE_ATTACHED_CHOICES
        transaction_types = [('A', 'Apertura'), ('C', 'Cierre'), ('E', 'Entrada'), ('S', 'Salida')]  # Apertura, cierre, entrada y salida
        expense_types = CashFlow.TYPE_EXPENSE
        user_set = CustomUser.objects.filter(is_active=True, is_staff=False)
        
        # Fecha actual
        date_now = datetime.now().strftime('%Y-%m-%d')
        
        return render(request, 'accounting/cashflow_create.html', {
            'cash_accounts': cash_accounts,
            'document_types': document_types,
            'transaction_types': transaction_types,
            'expense_types': expense_types,
            'user_set': user_set,
            'date_now': date_now,
        })


@csrf_exempt
def cashflow_save(request):
    """Vista para guardar nuevo gasto"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            transaction_date = request.POST.get('transaction_date')
            description = request.POST.get('description', '').strip()
            serial = request.POST.get('serial', '').strip()
            n_receipt = request.POST.get('n_receipt', '0')
            document_type = request.POST.get('document_type', 'O')
            transaction_type = request.POST.get('transaction_type', 'S')
            subtotal = request.POST.get('subtotal', '0.00')
            total = request.POST.get('total', '0.00')
            igv = request.POST.get('igv', '0.00')
            cash_id = request.POST.get('cash_id')
            operation_code = request.POST.get('operation_code', '').strip()
            expense_type = request.POST.get('expense_type', 'O')
            payment_type = request.POST.get('payment_type', 'E')
            user_id = request.POST.get('user_id')
            
            # Validaciones básicas
            if not transaction_date:
                return JsonResponse({
                    'success': False,
                    'message': 'La fecha de transacción es obligatoria'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not description:
                return JsonResponse({
                    'success': False,
                    'message': 'La descripción es obligatoria'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not cash_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar una cuenta/caja'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar un usuario'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Obtener objetos relacionados
            cash_obj = Cash.objects.get(id=int(cash_id))
            user_obj = CustomUser.objects.get(id=int(user_id))
            
            # Crear el gasto
            cashflow_obj = CashFlow(
                transaction_date=transaction_date,
                description=description.upper(),
                serial=serial.upper() if serial else None,
                n_receipt=int(n_receipt) if n_receipt else 0,
                document_type_attached=document_type,
                type=transaction_type,
                subtotal=Decimal(str(subtotal)),
                total=Decimal(str(total)),
                igv=Decimal(str(igv)),
                cash=cash_obj,
                operation_code=operation_code.upper() if operation_code else None,
                type_expense=expense_type,
                way_to_pay=payment_type,
                user=user_obj,
                subsidiary=cash_obj.subsidiary
            )
            cashflow_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{cashflow_obj.get_type_display()} registrado exitosamente',
                'cashflow_id': cashflow_obj.id
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar el gasto: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def cashflow_edit(request, cashflow_id):
    """Vista para editar gasto existente"""
    try:
        cashflow_obj = CashFlow.objects.select_related('cash', 'user', 'cash__subsidiary').get(id=cashflow_id)
        cash_accounts = Cash.objects.all()
        document_types = CashFlow.DOCUMENT_TYPE_ATTACHED_CHOICES
        transaction_types = [('A', 'Apertura'), ('C', 'Cierre'), ('E', 'Entrada'), ('S', 'Salida')]  # Apertura, cierre, entrada y salida
        expense_types = CashFlow.TYPE_EXPENSE
        user_set = CustomUser.objects.filter(is_active=True, is_staff=False)
        
        return render(request, 'accounting/cashflow_edit.html', {
            'cashflow': cashflow_obj,
            'cash_accounts': cash_accounts,
            'document_types': document_types,
            'transaction_types': transaction_types,
            'expense_types': expense_types,
            'user_set': user_set,
        })
        
    except CashFlow.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Gasto no encontrado'
        }, status=HTTPStatus.NOT_FOUND)


@csrf_exempt
def cashflow_update(request):
    """Vista para actualizar gasto existente"""
    if request.method == 'POST':
        try:
            cashflow_id = request.POST.get('cashflow_id')
            if not cashflow_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de gasto no proporcionado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cashflow_obj = CashFlow.objects.get(id=int(cashflow_id))
            
            # Obtener datos del formulario
            transaction_date = request.POST.get('transaction_date')
            description = request.POST.get('description', '').strip()
            serial = request.POST.get('serial', '').strip()
            n_receipt = request.POST.get('n_receipt', '0')
            document_type = request.POST.get('document_type', 'O')
            transaction_type = request.POST.get('transaction_type', 'S')
            subtotal = request.POST.get('subtotal', '0.00')
            total = request.POST.get('total', '0.00')
            igv = request.POST.get('igv', '0.00')
            cash_id = request.POST.get('cash_id')
            operation_code = request.POST.get('operation_code', '').strip()
            expense_type = request.POST.get('expense_type', 'O')
            payment_type = request.POST.get('payment_type', 'E')
            user_id = request.POST.get('user_id')
            
            # Validaciones básicas
            if not transaction_date:
                return JsonResponse({
                    'success': False,
                    'message': 'La fecha de transacción es obligatoria'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not description:
                return JsonResponse({
                    'success': False,
                    'message': 'La descripción es obligatoria'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not cash_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar una cuenta/caja'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar un usuario'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Obtener objetos relacionados
            cash_obj = Cash.objects.get(id=int(cash_id))
            user_obj = CustomUser.objects.get(id=int(user_id))
            
            # Actualizar el gasto
            cashflow_obj.transaction_date = transaction_date
            cashflow_obj.description = description.upper()
            cashflow_obj.serial = serial.upper() if serial else None
            cashflow_obj.n_receipt = int(n_receipt) if n_receipt else 0
            cashflow_obj.document_type_attached = document_type
            cashflow_obj.type = transaction_type
            cashflow_obj.subtotal = Decimal(str(subtotal))
            cashflow_obj.total = Decimal(str(total))
            cashflow_obj.igv = Decimal(str(igv))
            cashflow_obj.cash = cash_obj
            cashflow_obj.operation_code = operation_code.upper() if operation_code else None
            cashflow_obj.type_expense = expense_type
            cashflow_obj.way_to_pay = payment_type
            cashflow_obj.user = user_obj
            cashflow_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Gasto actualizado correctamente'
            }, status=HTTPStatus.OK)
            
        except CashFlow.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Gasto no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar el gasto: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


def get_cash_accounts_by_subsidiary(request):
    """Vista para obtener cuentas por sucursal"""
    if request.method == 'GET':
        subsidiary_id = request.GET.get('subsidiary', '')
        if subsidiary_id:
            try:
                cash_accounts = Cash.objects.filter(subsidiary_id=int(subsidiary_id)).order_by('name')
                accounts_list = []
                
                for account in cash_accounts:
                    accounts_list.append({
                        'id': account.id,
                        'name': account.name,
                        'currency': account.get_currency_type_display(),
                        'account_type': account.account_type,
                        # 'balance': float(account.initial)
                    })
                
                return JsonResponse({
                    'success': True,
                    'accounts': accounts_list
                }, status=HTTPStatus.OK)
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error al obtener las cuentas: {str(e)}'
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
        
        return JsonResponse({
            'success': False,
            'message': 'ID de sucursal no proporcionado'
        }, status=HTTPStatus.BAD_REQUEST)
    
    return JsonResponse({'message': 'Error de petición.'}, status=HTTPStatus.BAD_REQUEST)


# =============================================================================
# VISTAS PARA REPORTES
# =============================================================================
def _format_time_slot(start_time, end_time, age_desc=None):
    """Formatea un turno para mostrar en gráficos"""
    from datetime import time as dt_time
    if isinstance(start_time, dt_time):
        start_str = start_time.strftime('%H:%M')
    elif isinstance(start_time, str):
        start_str = start_time[:5] if len(start_time) >= 5 else start_time
    else:
        start_str = str(start_time)
    
    if isinstance(end_time, dt_time):
        end_str = end_time.strftime('%H:%M')
    elif isinstance(end_time, str):
        end_str = end_time[:5] if len(end_time) >= 5 else end_time
    else:
        end_str = str(end_time)
    
    label = f"{start_str} - {end_str}"
    if age_desc:
        label += f" ({age_desc})"
    return label


@csrf_exempt
def monthly_report(request):
    """Vista para reporte mensual de academia de basketball con gráficos profesionales"""
    from ..students.models import Enrollment, Student, Cycle, TrainingSchedule, TimeSlot
    
    if request.method == 'GET':
        subsidiary_set = Subsidiary.objects.all()
        
        # Obtener la sucursal del usuario actual
        user_subsidiary = None
        if hasattr(request.user, 'subsidiary') and request.user.subsidiary:
            user_subsidiary = request.user.subsidiary
        
        # Fecha actual para el filtro
        current_date = datetime.now()
        current_month = current_date.strftime('%Y-%m')
        
        return render(request, 'accounting/monthly_report.html', {
            'subsidiary_set': subsidiary_set,
            'user_subsidiary': user_subsidiary,
            'current_month': current_month,
        })
    elif request.method == 'POST':
        try:
            # Obtener parámetros del filtro
            report_month = request.POST.get('report_month')
            subsidiary_id = request.POST.get('subsidiary')
            
            if not report_month:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe seleccionar un mes'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Convertir mes a rango de fechas
            year, month = report_month.split('-')
            start_date = datetime(int(year), int(month), 1).date()
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1).date()
            else:
                end_date = datetime(int(year), int(month) + 1, 1).date()
            
            # Filtrar datos por sucursal si se especifica
            subsidiary_obj = None
            enrollments_filter = {}
            cashflows_filter = {}
            
            if subsidiary_id and subsidiary_id != '0':
                subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
                enrollments_filter = {'subsidiary_id': subsidiary_id}
                cashflows_filter = {'cash__subsidiary_id': subsidiary_id}
            
            # 1. INSCRIPCIONES DEL MES
            enrollments_month = Enrollment.objects.filter(
                enrollment_date__gte=start_date,
                enrollment_date__lt=end_date,
                **enrollments_filter
            ).select_related('student', 'cycle', 'schedule', 'time_slot', 'time_slot__teacher', 'subsidiary')
            
            # 2. INSCRIPCIONES ACTIVAS (con pagos completos)
            active_enrollments = enrollments_month.filter(
                status='A',
                remaining=0
            )
            
            # 3. INSCRIPCIONES CON PAGOS PENDIENTES
            pending_enrollments = enrollments_month.filter(
                remaining__gt=0
            )
            
            # 4. INSCRIPCIONES POR CICLO
            enrollments_by_cycle = enrollments_month.values('cycle__name').annotate(
                count=Count('id'),
                total=Sum('price'),
                advance_total=Sum('advance'),
                remaining_total=Sum('remaining')
            ).order_by('-count')
            
            # 5. INSCRIPCIONES POR HORARIO
            enrollments_by_schedule = enrollments_month.values('schedule__name').annotate(
                count=Count('id'),
                total=Sum('price')
            ).order_by('-count')
            
            # 6. INSCRIPCIONES POR TURNO
            enrollments_by_timeslot = enrollments_month.values(
                'time_slot__start_time', 'time_slot__end_time', 'time_slot__age_description'
            ).annotate(
                count=Count('id'),
                total=Sum('price')
            ).order_by('time_slot__start_time')
            
            # 7. INSCRIPCIONES POR PROFESOR
            enrollments_by_teacher = enrollments_month.filter(
                time_slot__teacher__isnull=False
            ).values('time_slot__teacher__first_name', 'time_slot__teacher__last_name').annotate(
                count=Count('id'),
                total=Sum('price')
            ).order_by('-count')
            
            # 8. INSCRIPCIONES POR SEDE
            enrollments_by_subsidiary = enrollments_month.values('subsidiary__name').annotate(
                count=Count('id'),
                total=Sum('price'),
                advance_total=Sum('advance'),
                remaining_total=Sum('remaining')
            ).order_by('-count')
            
            # 9. INGRESOS DEL MES (de inscripciones)
            income_from_enrollments = enrollments_month.aggregate(
                total_advance=Sum('advance')
            )['total_advance'] or Decimal('0')
            
            # 10. PAGOS PENDIENTES TOTALES
            total_pending = pending_enrollments.aggregate(
                total=Sum('remaining')
            )['total'] or Decimal('0')
            
            # 11. INGRESOS GENERALES DEL MES (CashFlow tipo 'E')
            monthly_income = CashFlow.objects.filter(
                transaction_date__gte=start_date,
                transaction_date__lt=end_date,
                type='E',
                **cashflows_filter
            ).select_related('cash', 'cash__subsidiary')
            
            monthly_income_total = monthly_income.aggregate(Sum('total'))['total__sum'] or Decimal('0')
            
            # 12. GASTOS DEL MES
            monthly_expenses = CashFlow.objects.filter(
                transaction_date__gte=start_date,
                transaction_date__lt=end_date,
                type='S',
                **cashflows_filter
            ).select_related('cash', 'cash__subsidiary')
            
            monthly_expenses_total = monthly_expenses.aggregate(Sum('total'))['total__sum'] or Decimal('0')
            
            # 13. INSCRIPCIONES POR DÍA DEL MES
            daily_enrollments = enrollments_month.extra(
                select={'day': 'DATE(enrollment_date)'}
            ).values('day').annotate(
                count=Count('id'),
                total=Sum('price')
            ).order_by('day')
            
            # 14. DEPORTISTAS NUEVOS VS REGULARES
            # Convertir start_date a datetime para comparar con creation_date (DateTimeField)
            start_datetime = datetime.combine(start_date, datetime.min.time())
            new_students = enrollments_month.filter(
                student__creation_date__gte=start_datetime
            ).values('student_id').distinct().count()
            
            regular_students = enrollments_month.exclude(
                student__creation_date__gte=start_datetime
            ).values('student_id').distinct().count()
            
            # Calcular estadísticas
            stats = {
                'total_enrollments': enrollments_month.count(),
                'active_enrollments': active_enrollments.count(),
                'pending_enrollments': pending_enrollments.count(),
                'total_pending': float(total_pending),
                'income_from_enrollments': float(income_from_enrollments),
                'monthly_income_total': float(monthly_income_total),
                'monthly_expenses_total': float(monthly_expenses_total),
                'monthly_profit_total': float(monthly_income_total - monthly_expenses_total),
                'new_students': new_students,
                'regular_students': regular_students,
                'total_students': new_students + regular_students,
            }
            
            # Datos para gráficos
            chart_data = {
                'enrollments_by_cycle': list(enrollments_by_cycle),
                'enrollments_by_schedule': list(enrollments_by_schedule),
                'enrollments_by_timeslot': [
                    {
                        'label': _format_time_slot(item['time_slot__start_time'], item['time_slot__end_time'], item.get('time_slot__age_description')),
                        'count': item['count'],
                        'total': float(item['total']),
                        'age': item.get('time_slot__age_description') or 'Todas'
                    }
                    for item in enrollments_by_timeslot
                ],
                'enrollments_by_teacher': [
                    {
                        'label': f"{item['time_slot__teacher__first_name'] or ''} {item['time_slot__teacher__last_name'] or ''}".strip() or 'Sin nombre',
                        'count': item['count'],
                        'total': float(item['total'])
                    }
                    for item in enrollments_by_teacher
                ],
                'enrollments_by_subsidiary': list(enrollments_by_subsidiary),
                'daily_enrollments': [
                    {
                        'day': item['day'].strftime('%Y-%m-%d') if hasattr(item['day'], 'strftime') else str(item['day']),
                        'count': item['count'],
                        'total': float(item['total'])
                    }
                    for item in daily_enrollments
                ],
                'income_by_subsidiary': list(
                    monthly_income.values('cash__subsidiary__name')
                    .annotate(total=Sum('total'))
                    .order_by('-total')
                ),
                'expenses_by_subsidiary': list(
                    monthly_expenses.values('cash__subsidiary__name')
                    .annotate(total=Sum('total'))
                    .order_by('-total')
                ),
            }
            
            return JsonResponse({
                'success': True,
                'stats': stats,
                'chart_data': chart_data,
                'subsidiary': subsidiary_obj.name if subsidiary_obj else 'Todas las sucursales',
                'month_name': start_date.strftime('%B %Y').capitalize()
            })
            
        except Exception as e:
            import traceback
            import sys
            error_traceback = traceback.format_exc()
            # Log del error para debugging
            print(f"ERROR EN MONTHLY_REPORT: {str(e)}")
            print(error_traceback)
            return JsonResponse({
                'success': False,
                'message': f'Error al generar reporte mensual: {str(e)}',
                'error_detail': str(e),
                'traceback': error_traceback
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)




