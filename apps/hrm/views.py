import decimal
from datetime import datetime, timedelta, time
from http import HTTPStatus
import json
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Max, Q, F, Sum
from django.db.models.functions import Coalesce
from django.template import loader
from django.core import serializers
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from django.utils import timezone

# Create your views here.
from apps.hrm.models import Subsidiary, FunctionArea, FunctionCharge, Charge, Area
from django.http import JsonResponse
from django.shortcuts import render

from apps.users.models import CustomUser
from farm import settings
from apps.accounting.models import CashFlow, Cash


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        pk = self.request.user.id
        user_obj = CustomUser.objects.get(id=int(pk))
        subsidiary_obj = user_obj.subsidiary
        current_date = datetime.now()

        context = {
            'current': current_date,
            'subsidiary_obj': subsidiary_obj,
        }
        return context


def get_subsidiary_list(request):
    if request.method == 'GET':
        subsidiary_set = Subsidiary.objects.all().order_by('id')
        return render(request, 'hrm/subsidiary_list.html', {
            'subsidiary_set': subsidiary_set,
        })


def modal_subsidiary_create(request):
    if request.method == 'GET':
        t = loader.get_template('hrm/subsidiary_create.html')
        return JsonResponse({
            'form': t.render({}, request),
        })


@csrf_exempt
def create_subsidiary(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            _serial = request.POST.get('serial', '')
            _name = request.POST.get('name', '')
            _phone = request.POST.get('phone', '')
            _email = request.POST.get('email', '')
            _ruc = request.POST.get('ruc', '')
            _address = request.POST.get('address', '')
            _business = request.POST.get('business-name', '')
            _representative_dni = request.POST.get('representative-dni', '')
            _representative_name = request.POST.get('representative-name', '')
            _observation = request.POST.get('observation-input', '')
            
            # Validar campos requeridos
            if not _name or not _ruc or not _business:
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos Nombre, RUC y Razón Social son obligatorios'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Obtener descripción textual
            _text_description = request.POST.get('text-description', '')
            
            # Crear objeto Subsidiary con los campos del modelo
            subsidiary_obj = Subsidiary(
                name=_name,
                serial=_serial,
                phone=_phone,
                address=_address,
                ruc=_ruc,
                email=_email,
                business_name=_business,
                representative_dni=_representative_dni,
                representative_name=_representative_name,
                observation=_observation,
                text_description=_text_description,
            )
            subsidiary_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Sucursal creada exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear la sucursal: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_subsidiary_update(request):
    if request.method == 'GET':
        subsidiary_id = request.GET.get('pk', '')
        if subsidiary_id:
            subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
            t = loader.get_template('hrm/subsidiary_update.html')
            return JsonResponse({
                'form': t.render({
                    'subsidiary_obj': subsidiary_obj,
                }, request),
            })


@csrf_exempt
def update_subsidiary(request):
    if request.method == 'POST':
        try:
            subsidiary_id = request.POST.get('subsidiary_id', '')
            _serial = request.POST.get('serial', '')
            _name = request.POST.get('name', '')
            _phone = request.POST.get('phone', '')
            _email = request.POST.get('email', '')
            _ruc = request.POST.get('ruc', '')
            _address = request.POST.get('address', '')
            _business = request.POST.get('business-name', '')
            _representative_dni = request.POST.get('representative-dni', '')
            _representative_name = request.POST.get('representative-name', '')
            _observation = request.POST.get('observation-input', '')
            _text_description = request.POST.get('text-description', '')
            
            if not subsidiary_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de sucursal es obligatorio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            subsidiary_obj = Subsidiary.objects.get(id=int(subsidiary_id))
            subsidiary_obj.serial = _serial
            subsidiary_obj.name = _name
            subsidiary_obj.phone = _phone
            subsidiary_obj.email = _email
            subsidiary_obj.ruc = _ruc
            subsidiary_obj.address = _address
            subsidiary_obj.business_name = _business
            subsidiary_obj.representative_dni = _representative_dni
            subsidiary_obj.representative_name = _representative_name
            subsidiary_obj.observation = _observation
            subsidiary_obj.text_description = _text_description
            subsidiary_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Sucursal actualizada exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar la sucursal: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_employee_list(request):
    if request.method == 'GET':
        user_set = CustomUser.objects.filter(is_superuser=False).order_by('id')
        return render(request, 'hrm/employee_list.html', {
            'user_set': user_set,
        })


def modal_user_create(request):
    if request.method == 'GET':
        my_date = datetime.now()
        date_now = my_date.strftime("%Y-%m-%d")
        t = loader.get_template('hrm/user_create.html')
        return JsonResponse({
            'form': t.render({
                'date_now': date_now,
                'gender_set': CustomUser._meta.get_field('gender').choices,
                'nationality_set': CustomUser._meta.get_field('nationality').choices,
                'education_set': CustomUser._meta.get_field('education').choices,
                'marital_status_set': CustomUser._meta.get_field('marital_status').choices,
                'type_employee_set': CustomUser._meta.get_field('type_employee').choices,
                'subsidiary_set': Subsidiary.objects.all(),
            }, request),
        })


@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            _username = request.POST.get('username', '')
            _password = request.POST.get('password', '')
            _first_name = request.POST.get('first_name', '')
            _last_name = request.POST.get('last_name', '')
            _email = request.POST.get('email', '')
            _subsidiary_id = request.POST.get('subsidiary', '')
            _is_active = request.POST.get('is_active', 'false')
            _is_staff = request.POST.get('is_staff', 'false')
            
            if not _username or not _password or not _first_name or not _last_name:
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos Usuario, Contraseña, Nombre y Apellido son obligatorios'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Verificar si el usuario ya existe
            if CustomUser.objects.filter(username=_username).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre de usuario ya existe'
                }, status=HTTPStatus.BAD_REQUEST)
            
            subsidiary_obj = None
            if _subsidiary_id:
                subsidiary_obj = Subsidiary.objects.get(id=int(_subsidiary_id))
            
            user_obj = CustomUser(
                username=_username,
                first_name=_first_name,
                last_name=_last_name,
                email=_email,
                subsidiary=subsidiary_obj,
                is_active=(_is_active == 'true'),
                is_staff=(_is_staff == 'true'),
            )
            user_obj.set_password(_password)
            user_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Usuario creado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear el usuario: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_user_update(request):
    if request.method == 'GET':
        user_id = request.GET.get('pk', '')
        if user_id:
            user_obj = CustomUser.objects.get(id=int(user_id))
            subsidiary_set = Subsidiary.objects.all()
            t = loader.get_template('hrm/user_update.html')
            return JsonResponse({
                'form': t.render({
                    'user_obj': user_obj,
                    'subsidiary_set': subsidiary_set,
                    'type_employee_set': CustomUser._meta.get_field('type_employee').choices,
                    'gender_set': CustomUser._meta.get_field('gender').choices,
                    'nationality_set': CustomUser._meta.get_field('nationality').choices,
                    'education_set': CustomUser._meta.get_field('education').choices,
                    'marital_status_set': CustomUser._meta.get_field('marital_status').choices,
                }, request),
            })


def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


@csrf_exempt
def update_user(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id', '')

            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'No se identificó al usuario'
                }, status=HTTPStatus.BAD_REQUEST)

            user_obj = CustomUser.objects.get(id=int(user_id))
            if not user_obj:
                return JsonResponse({
                    'success': False,
                    'message': 'Problemas al obtener el usuario'
                }, status=HTTPStatus.BAD_REQUEST)

            # Obtener datos del formulario
            _document = request.POST.get('document', '')
            _first_name = request.POST.get('first-name', '')
            _last_name = request.POST.get('last-name', '')
            _phone = request.POST.get('phone', '')
            _gender = request.POST.get('gender', '')
            _subsidiary = request.POST.get('subsidiary', '')
            _education = request.POST.get('education', '')
            _type_employee = request.POST.get('type-employee', '')
            _nationality = request.POST.get('nationality', '')
            _marital_status = request.POST.get('marital-status', '')
            _reference = request.POST.get('reference', '')
            _observations = request.POST.get('observations', '')
            _cellphone = request.POST.get('cellphone', '')
            _address = request.POST.get('address', '')
            _email = request.POST.get('email', '')
            _user = request.POST.get('user', '')
            _password = request.POST.get('password', '')

            # Checkboxes de permisos (nombres actualizados para edición)
            _check_active = request.POST.get('editCheckActive', False)
            _check_access = request.POST.get('editCheckboxAccess', False)
            _check_sales = request.POST.get('editCheckboxSales', False)
            _check_hrm = request.POST.get('editCheckboxHrm', False)
            _check_finances = request.POST.get('editCheckboxFinances', False)
            _check_report = request.POST.get('editCheckboxReport', False)
            _check_admin = request.POST.get('editCheckboxAdmin', False)

            # Convertir checkboxes a boolean
            if _check_active == 'on':
                _check_active = True
            if _check_access == 'on':
                _check_access = True
            if _check_sales == 'on':
                _check_sales = True
            if _check_hrm == 'on':
                _check_hrm = True
            if _check_finances == 'on':
                _check_finances = True
            if _check_report == 'on':
                _check_report = True
            if _check_admin == 'on':
                _check_admin = True

            # Validar campos requeridos
            if not _first_name or not _last_name or not _email:
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos Nombres, Apellidos y Email son obligatorios'
                }, status=HTTPStatus.BAD_REQUEST)

            # Validar sucursal
            if _subsidiary == '0' or not _subsidiary:
                return JsonResponse({
                    'success': False,
                    'message': 'Seleccione una sucursal'
                }, status=HTTPStatus.BAD_REQUEST)

            # Obtener objeto sucursal
            _subsidiary_obj = Subsidiary.objects.get(id=int(_subsidiary))

            # Procesar fecha de nacimiento
            _birth_date = None
            if request.POST.get('birth-date', '') != '':
                _birth_date = datetime.strptime(request.POST.get('birth-date', ''), '%Y-%m-%d')

            # Verificar si el username ya existe (si cambió)
            if _user and _user != user_obj.username:
                try:
                    existing_user = CustomUser.objects.get(username=_user)
                    if existing_user.id != user_obj.id:
                        return JsonResponse({
                            'success': False,
                            'message': 'El nombre de usuario ya existe'
                        }, status=HTTPStatus.BAD_REQUEST)
                except CustomUser.DoesNotExist:
                    pass

            # Verificar si el email ya existe (si cambió)
            if _email != user_obj.email:
                try:
                    existing_user = CustomUser.objects.get(email=_email)
                    if existing_user.id != user_obj.id:
                        return JsonResponse({
                            'success': False,
                            'message': 'El correo electrónico ya existe'
                        }, status=HTTPStatus.BAD_REQUEST)
                except CustomUser.DoesNotExist:
                    pass

            # Procesar foto
            _photo = request.FILES.get('exampleInputFile', False)

            # Actualizar campos del usuario
            user_obj.first_name = _first_name
            user_obj.last_name = _last_name
            user_obj.email = _email
            user_obj.username = _user
            user_obj.is_active = _check_active
            user_obj.document = _document
            user_obj.birth_date = _birth_date
            user_obj.type_employee = _type_employee
            user_obj.gender = _gender
            user_obj.phone = _phone
            user_obj.subsidiary = _subsidiary_obj
            user_obj.address = _address
            user_obj.education = _education
            user_obj.nationality = _nationality
            user_obj.marital_status = _marital_status
            user_obj.reference = _reference
            user_obj.cellphone = _cellphone
            user_obj.observations = _observations
            user_obj.has_access_system = _check_access
            user_obj.has_access_to_sales = _check_sales
            user_obj.has_access_to_hrm = _check_hrm
            user_obj.has_access_to_finances = _check_finances
            user_obj.has_access_to_report = _check_report
            user_obj.has_access_to_all = _check_admin

            # Actualizar foto si se proporcionó una nueva
            if _photo:
                user_obj.photo = _photo

            # Actualizar contraseña si se proporcionó una nueva
            if _password:
                user_obj.set_password(_password)

            # Guardar cambios
            user_obj.save()

            return JsonResponse({
                'success': True,
                'message': 'Colaborador actualizado con éxito'
            }, status=HTTPStatus.OK)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar el colaborador: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
