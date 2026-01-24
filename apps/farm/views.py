from datetime import datetime
from http import HTTPStatus
from decimal import Decimal
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Sum, Q
from .models import Product, ServiceType, InventoryTransaction, Crop, CropType, Plot, CropCycleCost, UNIT_CHOICES
from apps.users.models import CustomUser


def get_product_list(request):
    if request.method == 'GET':
        product_set = Product.objects.all().order_by('id')
        return render(request, 'farm/product_list.html', {
            'product_set': product_set,
        })


def modal_product_create(request):
    if request.method == 'GET':
        from .models import UNIT_CHOICES
        service_type_set = ServiceType.objects.filter(active=True).order_by('name')
        t = loader.get_template('farm/product_create.html')
        return JsonResponse({
            'form': t.render({
                'product_type_set': Product.PRODUCT_TYPE_CHOICES,
                'product_category_set': Product.PRODUCT_CATEGORY_CHOICES,
                'unit_set': UNIT_CHOICES,
                'service_type_set': service_type_set,
            }, request),
        })


@csrf_exempt
def create_product(request):
    if request.method == 'POST':
        try:
            # Get form data
            _name = request.POST.get('name', '')
            _product_type = request.POST.get('product-type', Product.PRODUCT)
            _product_category = request.POST.get('product-category', '')
            _unit = request.POST.get('unit', 'KG')
            _unit_price = request.POST.get('unit-price', '')
            _brand = request.POST.get('brand', '')
            _expiration_date = request.POST.get('expiration-date', '')
            _active = request.POST.get('active', 'true')
            _observations = request.POST.get('observations', '')
            
            # Validate required fields
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _unit_price:
                return JsonResponse({
                    'success': False,
                    'message': 'El precio unitario es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate product_category if product_type is PRODUCT
            if _product_type == Product.PRODUCT and not _product_category:
                return JsonResponse({
                    'success': False,
                    'message': 'La categoría del producto es requerida cuando el tipo es Producto'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate service_type if product_type is SERVICE
            _service_type_id = request.POST.get('service-type', '')
            if _product_type == Product.SERVICE and not _service_type_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El tipo de servicio es requerido cuando el tipo es Servicio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate and process unit price
            try:
                unit_price_val = float(_unit_price)
                if unit_price_val < 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'El precio unitario no puede ser negativo'
                    }, status=HTTPStatus.BAD_REQUEST)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'El precio unitario debe ser un número válido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Create Product object
            product_obj = Product(
                name=_name,
                product_type=_product_type,
                product_category=_product_category if _product_type == Product.PRODUCT and _product_category else None,
                unit=_unit,
                unit_price=unit_price_val,
                brand=_brand if _brand else None,
                service_type_id=int(_service_type_id) if _product_type == Product.SERVICE and _service_type_id else None,
                observations=_observations if _observations else None,
                active=(_active == 'true'),
            )
            
            # Process expiration date
            if _expiration_date:
                try:
                    product_obj.expiration_date = datetime.strptime(_expiration_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            product_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Product created successfully'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating product: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_product_update(request):
    if request.method == 'GET':
        product_id = request.GET.get('pk', '')
        if product_id:
            from .models import UNIT_CHOICES
            product_obj = Product.objects.get(id=int(product_id))
            service_type_set = ServiceType.objects.filter(active=True).order_by('name')
            t = loader.get_template('farm/product_update.html')
            return JsonResponse({
                'form': t.render({
                    'product_obj': product_obj,
                    'product_type_set': Product.PRODUCT_TYPE_CHOICES,
                    'product_category_set': Product.PRODUCT_CATEGORY_CHOICES,
                    'unit_set': UNIT_CHOICES,
                    'service_type_set': service_type_set,
                }, request),
            })


@csrf_exempt
def update_product(request):
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id', '')
            _name = request.POST.get('name', '')
            _product_type = request.POST.get('product-type', Product.PRODUCT)
            _product_category = request.POST.get('product-category', '')
            _unit = request.POST.get('unit', 'KG')
            _unit_price = request.POST.get('unit-price', '')
            _brand = request.POST.get('brand', '')
            _expiration_date = request.POST.get('expiration-date', '')
            _active = request.POST.get('active', 'true')
            _observations = request.POST.get('observations', '')
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El ID del producto es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _unit_price:
                return JsonResponse({
                    'success': False,
                    'message': 'El precio unitario es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate product_category if product_type is PRODUCT
            if _product_type == Product.PRODUCT and not _product_category:
                return JsonResponse({
                    'success': False,
                    'message': 'La categoría del producto es requerida cuando el tipo es Producto'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate service_type if product_type is SERVICE
            _service_type_id = request.POST.get('service-type', '')
            if _product_type == Product.SERVICE and not _service_type_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El tipo de servicio es requerido cuando el tipo es Servicio'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate and process unit price
            try:
                unit_price_val = float(_unit_price)
                if unit_price_val < 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'El precio unitario no puede ser negativo'
                    }, status=HTTPStatus.BAD_REQUEST)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'El precio unitario debe ser un número válido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            product_obj = Product.objects.get(id=int(product_id))
            product_obj.name = _name
            product_obj.product_type = _product_type
            # Set product_category only if product_type is PRODUCT, otherwise set to None
            product_obj.product_category = _product_category if _product_type == Product.PRODUCT and _product_category else None
            product_obj.service_type_id = int(_service_type_id) if _product_type == Product.SERVICE and _service_type_id else None
            product_obj.unit = _unit
            product_obj.unit_price = unit_price_val
            product_obj.brand = _brand if _brand else None
            product_obj.observations = _observations if _observations else None
            product_obj.active = (_active == 'true')
            
            # Process expiration date
            if _expiration_date:
                try:
                    product_obj.expiration_date = datetime.strptime(_expiration_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                product_obj.expiration_date = None
            
            product_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Product updated successfully'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating product: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def get_inventory_transaction_list(request):
    if request.method == 'GET':
        # Only show products that can have inventory (PRODUCT type with category)
        product_set = Product.objects.filter(
            active=True,
            product_type=Product.PRODUCT,
            product_category__isnull=False
        ).order_by('name')
        product_id = request.GET.get('product_id', '')
        selected_product = None
        transaction_set = None
        
        if product_id:
            try:
                selected_product = Product.objects.get(
                    id=int(product_id),
                    active=True,
                    product_type=Product.PRODUCT,
                    product_category__isnull=False
                )
                transaction_set = InventoryTransaction.objects.filter(product_id=int(product_id)).order_by('created_at', 'id')
            except Product.DoesNotExist:
                pass
        
        return render(request, 'farm/inventory_transaction_list.html', {
            'transaction_set': transaction_set,
            'product_set': product_set,
            'product_id': product_id,
            'selected_product': selected_product,
        })


def get_inventory_transaction_grid(request):
    """Get inventory transactions grid for AJAX loading"""
    if request.method == 'GET':
        product_id = request.GET.get('product_id', '')
        transaction_set = None
        
        if product_id:
            try:
                transaction_set = InventoryTransaction.objects.filter(product_id=int(product_id)).order_by('created_at', 'id')
            except ValueError:
                pass
        
        return render(request, 'farm/inventory_transaction_grid_list.html', {
            'transaction_set': transaction_set,
        })


def modal_product_selection(request):
    """Modal to select product before creating entry or exit"""
    if request.method == 'GET':
        transaction_type = request.GET.get('type', '')  # 'entry' or 'exit'
        # Only show products that can have inventory (PRODUCT type with category)
        product_set = Product.objects.filter(
            active=True,
            product_type=Product.PRODUCT,
            product_category__isnull=False
        ).order_by('name')
        t = loader.get_template('farm/product_selection.html')
        return JsonResponse({
            'form': t.render({
                'product_set': product_set,
                'transaction_type': transaction_type,
            }, request),
        })


def modal_inventory_entry_create(request):
    """Modal to create inventory entry"""
    if request.method == 'GET':
        product_id = request.GET.get('product_id', '')
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID is required'
            }, status=HTTPStatus.BAD_REQUEST)
        
        try:
            product = Product.objects.get(
                id=int(product_id),
                active=True,
                product_type=Product.PRODUCT,
                product_category__isnull=False
            )
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found or product cannot have inventory'
            }, status=HTTPStatus.NOT_FOUND)
        
        t = loader.get_template('farm/inventory_entry_create.html')
        return JsonResponse({
            'form': t.render({
                'product': product,
            }, request),
        })


def modal_inventory_exit_create(request):
    """Modal to create inventory exit"""
    if request.method == 'GET':
        product_id = request.GET.get('product_id', '')
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Product ID is required'
            }, status=HTTPStatus.BAD_REQUEST)
        
        try:
            product = Product.objects.get(
                id=int(product_id),
                active=True,
                product_type=Product.PRODUCT,
                product_category__isnull=False
            )
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Product not found or product cannot have inventory'
            }, status=HTTPStatus.NOT_FOUND)
        
        crop_set = Crop.objects.filter(active=True).order_by('crop_name', 'crop_type')
        t = loader.get_template('farm/inventory_exit_create.html')
        return JsonResponse({
            'form': t.render({
                'product': product,
                'crop_set': crop_set,
            }, request),
        })


@csrf_exempt
def create_inventory_entry(request):
    """Create inventory entry transaction"""
    if request.method == 'POST':
        try:
            # Get form data
            _product_id = request.POST.get('product_id', '')
            _entry_date = request.POST.get('entry_date', '')
            _entry_quantity = request.POST.get('entry_quantity', '')
            _observations = request.POST.get('observations', '')
            
            # Validate required fields
            if not _product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _entry_date:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de ingreso es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _entry_quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad de entrada es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate that the product can have inventory
            try:
                product = Product.objects.get(
                    id=int(_product_id),
                    active=True,
                    product_type=Product.PRODUCT,
                    product_category__isnull=False
                )
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado o no puede tener inventario (solo productos tipo PRODUCT con categoría pueden tener inventario)'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Create InventoryTransaction object
            transaction_obj = InventoryTransaction(
                product_id=int(_product_id),
                observations=_observations if _observations else None,
            )
            
            # Process entry date and quantity
            try:
                transaction_obj.entry_date = datetime.strptime(_entry_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de ingreso inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            try:
                entry_qty = float(_entry_quantity)
                if entry_qty <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'La cantidad debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
                transaction_obj.entry_quantity = entry_qty
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            transaction_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Entrada de inventario registrada exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar entrada: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@csrf_exempt
def create_inventory_exit(request):
    """Create inventory exit transaction"""
    if request.method == 'POST':
        try:
            # Get form data
            _product_id = request.POST.get('product_id', '')
            _exit_date = request.POST.get('exit_date', '')
            _crop_id = request.POST.get('crop_id', '')
            _exit_quantity = request.POST.get('exit_quantity', '')
            _observations = request.POST.get('observations', '')
            
            # Validate required fields
            if not _product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _exit_date:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de salida es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _crop_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Sembrío (razón) es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _exit_quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad de salida es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate that the product can have inventory
            try:
                product = Product.objects.get(
                    id=int(_product_id),
                    active=True,
                    product_type=Product.PRODUCT,
                    product_category__isnull=False
                )
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado o no puede tener inventario (solo productos tipo PRODUCT con categoría pueden tener inventario)'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Create InventoryTransaction object
            transaction_obj = InventoryTransaction(
                product_id=int(_product_id),
                observations=_observations if _observations else None,
            )
            
            # Process exit date, crop and quantity
            try:
                transaction_obj.exit_date = datetime.strptime(_exit_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de salida inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            try:
                transaction_obj.crop_id = int(_crop_id)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Sembrío inválido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            try:
                exit_qty = float(_exit_quantity)
                if exit_qty <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'La cantidad debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
                transaction_obj.exit_quantity = exit_qty
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            transaction_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Salida de inventario registrada exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar salida: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_inventory_transaction_update(request):
    if request.method == 'GET':
        transaction_id = request.GET.get('pk', '')
        if transaction_id:
            transaction_obj = InventoryTransaction.objects.get(id=int(transaction_id))
            crop_set = Crop.objects.filter(active=True).order_by('crop_name', 'crop_type')
            # Only show products that can have inventory (PRODUCT type with category)
            product_set = Product.objects.filter(
                active=True,
                product_type=Product.PRODUCT,
                product_category__isnull=False
            ).order_by('name')
            t = loader.get_template('farm/inventory_transaction_update.html')
            return JsonResponse({
                'form': t.render({
                    'transaction_obj': transaction_obj,
                    'product_set': product_set,
                    'crop_set': crop_set,
                }, request),
            })


@csrf_exempt
def update_inventory_transaction(request):
    if request.method == 'POST':
        try:
            transaction_id = request.POST.get('transaction_id', '')
            _product_id = request.POST.get('product_id', '')
            _entry_date = request.POST.get('entry_date', '')
            _entry_quantity = request.POST.get('entry_quantity', '')
            _exit_date = request.POST.get('exit_date', '')
            _crop_id = request.POST.get('crop_id', '')
            _exit_quantity = request.POST.get('exit_quantity', '')
            _observations = request.POST.get('observations', '')
            
            if not transaction_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Transaction ID is required'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Product is required'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate that the product can have inventory
            try:
                product = Product.objects.get(
                    id=int(_product_id),
                    product_type=Product.PRODUCT,
                    product_category__isnull=False
                )
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Product not found or product cannot have inventory (only PRODUCT type with category can have inventory)'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # At least one of entry or exit must be provided
            if not _entry_quantity and not _exit_quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'Either entry quantity or exit quantity must be provided'
                }, status=HTTPStatus.BAD_REQUEST)
            
            transaction_obj = InventoryTransaction.objects.get(id=int(transaction_id))
            transaction_obj.product_id = int(_product_id)
            transaction_obj.observations = _observations if _observations else None
            
            # Process entry date and quantity
            if _entry_date:
                try:
                    transaction_obj.entry_date = datetime.strptime(_entry_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                transaction_obj.entry_date = None
            
            if _entry_quantity:
                try:
                    transaction_obj.entry_quantity = float(_entry_quantity)
                except ValueError:
                    pass
            else:
                transaction_obj.entry_quantity = None
            
            # Process exit date, crop and quantity
            if _exit_date:
                try:
                    transaction_obj.exit_date = datetime.strptime(_exit_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                transaction_obj.exit_date = None
            
            if _crop_id:
                try:
                    transaction_obj.crop_id = int(_crop_id)
                except ValueError:
                    pass
            else:
                transaction_obj.crop = None
            
            if _exit_quantity:
                try:
                    transaction_obj.exit_quantity = float(_exit_quantity)
                except ValueError:
                    pass
            else:
                transaction_obj.exit_quantity = None
            
            transaction_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Inventory transaction updated successfully'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating inventory transaction: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


# ========== CROP TYPE VIEWS ==========

def get_crop_type_list(request):
    if request.method == 'GET':
        crop_type_set = CropType.objects.all().order_by('name')
        return render(request, 'farm/crop_type_list.html', {
            'crop_type_set': crop_type_set,
        })


def modal_crop_type_create(request):
    if request.method == 'GET':
        t = loader.get_template('farm/crop_type_create.html')
        return JsonResponse({
            'form': t.render({}, request),
        })


@csrf_exempt
def create_crop_type(request):
    if request.method == 'POST':
        try:
            _name = request.POST.get('name', '')
            _description = request.POST.get('description', '')
            _is_active = request.POST.get('is_active', 'true')
            
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            crop_type_obj = CropType(
                name=_name,
                description=_description if _description else '',
                is_active=(_is_active == 'true'),
            )
            crop_type_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Tipo de cultivo creado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear tipo de cultivo: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_crop_type_update(request):
    if request.method == 'GET':
        crop_type_id = request.GET.get('pk', '')
        if crop_type_id:
            crop_type_obj = CropType.objects.get(id=int(crop_type_id))
            t = loader.get_template('farm/crop_type_update.html')
            return JsonResponse({
                'form': t.render({
                    'crop_type_obj': crop_type_obj,
                }, request),
            })


@csrf_exempt
def update_crop_type(request):
    if request.method == 'POST':
        try:
            crop_type_id = request.POST.get('crop_type_id', '')
            _name = request.POST.get('name', '')
            _description = request.POST.get('description', '')
            _is_active = request.POST.get('is_active', 'true')
            
            if not crop_type_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El ID del tipo de cultivo es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            crop_type_obj = CropType.objects.get(id=int(crop_type_id))
            crop_type_obj.name = _name
            crop_type_obj.description = _description if _description else ''
            crop_type_obj.is_active = (_is_active == 'true')
            crop_type_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Tipo de cultivo actualizado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar tipo de cultivo: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


# ========== PLOT VIEWS ==========

def get_plot_list(request):
    if request.method == 'GET':
        plot_set = Plot.objects.all().order_by('name')
        return render(request, 'farm/plot_list.html', {
            'plot_set': plot_set,
        })


def modal_plot_create(request):
    if request.method == 'GET':
        from apps.hrm.models import Subsidiary
        subsidiary_set = Subsidiary.objects.all().order_by('name')
        t = loader.get_template('farm/plot_create.html')
        return JsonResponse({
            'form': t.render({
                'subsidiary_set': subsidiary_set,
            }, request),
        })


@csrf_exempt
def create_plot(request):
    if request.method == 'POST':
        try:
            _name = request.POST.get('name', '')
            _area_hectares = request.POST.get('area_hectares', '')
            _location = request.POST.get('location', '')
            _subsidiary_id = request.POST.get('subsidiary_id', '')
            _description = request.POST.get('description', '')
            _coordinates = request.POST.get('coordinates', '')
            _active = request.POST.get('active', 'true')
            _observations = request.POST.get('observations', '')
            
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _area_hectares:
                return JsonResponse({
                    'success': False,
                    'message': 'El área en hectáreas es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            plot_obj = Plot(
                name=_name,
                location=_location if _location else None,
                description=_description if _description else None,
                coordinates=_coordinates if _coordinates else None,
                observations=_observations if _observations else None,
                active=(_active == 'true'),
            )
            
            try:
                plot_obj.area_hectares = float(_area_hectares)
                if plot_obj.area_hectares <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'El área debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Área inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if _subsidiary_id:
                try:
                    from apps.hrm.models import Subsidiary
                    plot_obj.subsidiary = Subsidiary.objects.get(id=int(_subsidiary_id))
                except:
                    pass
            
            plot_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Parcela creada exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear parcela: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_plot_update(request):
    if request.method == 'GET':
        plot_id = request.GET.get('pk', '')
        if plot_id:
            plot_obj = Plot.objects.get(id=int(plot_id))
            from apps.hrm.models import Subsidiary
            subsidiary_set = Subsidiary.objects.all().order_by('name')
            t = loader.get_template('farm/plot_update.html')
            return JsonResponse({
                'form': t.render({
                    'plot_obj': plot_obj,
                    'subsidiary_set': subsidiary_set,
                }, request),
            })


@csrf_exempt
def update_plot(request):
    if request.method == 'POST':
        try:
            plot_id = request.POST.get('plot_id', '')
            _name = request.POST.get('name', '')
            _area_hectares = request.POST.get('area_hectares', '')
            _location = request.POST.get('location', '')
            _subsidiary_id = request.POST.get('subsidiary_id', '')
            _description = request.POST.get('description', '')
            _coordinates = request.POST.get('coordinates', '')
            _active = request.POST.get('active', 'true')
            _observations = request.POST.get('observations', '')
            
            if not plot_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El ID de la parcela es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _area_hectares:
                return JsonResponse({
                    'success': False,
                    'message': 'El área en hectáreas es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            plot_obj = Plot.objects.get(id=int(plot_id))
            plot_obj.name = _name
            plot_obj.location = _location if _location else None
            plot_obj.description = _description if _description else None
            plot_obj.coordinates = _coordinates if _coordinates else None
            plot_obj.observations = _observations if _observations else None
            plot_obj.active = (_active == 'true')
            
            try:
                plot_obj.area_hectares = float(_area_hectares)
                if plot_obj.area_hectares <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'El área debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Área inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if _subsidiary_id:
                try:
                    from apps.hrm.models import Subsidiary
                    plot_obj.subsidiary = Subsidiary.objects.get(id=int(_subsidiary_id))
                except:
                    plot_obj.subsidiary = None
            else:
                plot_obj.subsidiary = None
            
            plot_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Parcela actualizada exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar parcela: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


# ========== CROP VIEWS ==========

def get_crop_list(request):
    if request.method == 'GET':
        crop_set = Crop.objects.all().order_by('-planting_date', 'plot')
        plot_set = Plot.objects.filter(active=True).order_by('name')
        crop_type_set = CropType.objects.filter(is_active=True).order_by('name')
        return render(request, 'farm/crop_list.html', {
            'crop_set': crop_set,
            'plot_set': plot_set,
            'crop_type_set': crop_type_set,
        })


def modal_crop_create(request):
    if request.method == 'GET':
        plot_set = Plot.objects.filter(active=True).order_by('name')
        crop_type_set = CropType.objects.filter(is_active=True).order_by('name')
        t = loader.get_template('farm/crop_create.html')
        return JsonResponse({
            'form': t.render({
                'plot_set': plot_set,
                'crop_type_set': crop_type_set,
                'status_set': Crop.STATUS_CHOICES,
            }, request),
        })


@csrf_exempt
def create_crop(request):
    if request.method == 'POST':
        try:
            _plot_id = request.POST.get('plot_id', '')
            _crop_type = request.POST.get('crop_type', '')
            _crop_name = request.POST.get('crop_name', '')
            _planting_date = request.POST.get('planting_date', '')
            _estimated_harvest_date = request.POST.get('estimated_harvest_date', '')
            _actual_harvest_date = request.POST.get('actual_harvest_date', '')
            _status = request.POST.get('status', 'PLANTING')
            _planted_area = request.POST.get('planted_area', '')
            _expected_yield = request.POST.get('expected_yield', '')
            _actual_yield = request.POST.get('actual_yield', '')
            _description = request.POST.get('description', '')
            _observations = request.POST.get('observations', '')
            _active = request.POST.get('active', 'true')
            
            if not _crop_type:
                return JsonResponse({
                    'success': False,
                    'message': 'El tipo de cultivo es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _planting_date:
                return JsonResponse({
                    'success': False,
                    'message': 'La fecha de siembra es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _planted_area:
                return JsonResponse({
                    'success': False,
                    'message': 'El área sembrada es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            crop_obj = Crop(
                crop_type=_crop_type,
                crop_name=_crop_name if _crop_name else None,
                status=_status,
                description=_description if _description else None,
                observations=_observations if _observations else None,
                active=(_active == 'true'),
            )
            
            if _plot_id:
                try:
                    crop_obj.plot = Plot.objects.get(id=int(_plot_id), active=True)
                except Plot.DoesNotExist:
                    pass
            
            try:
                crop_obj.planting_date = datetime.strptime(_planting_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de siembra inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if _estimated_harvest_date:
                try:
                    crop_obj.estimated_harvest_date = datetime.strptime(_estimated_harvest_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            if _actual_harvest_date:
                try:
                    crop_obj.actual_harvest_date = datetime.strptime(_actual_harvest_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            try:
                crop_obj.planted_area = float(_planted_area)
                if crop_obj.planted_area <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'El área sembrada debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Área sembrada inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if _expected_yield:
                try:
                    crop_obj.expected_yield = float(_expected_yield)
                    if crop_obj.expected_yield < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El rendimiento esperado no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                except ValueError:
                    pass
            
            if _actual_yield:
                try:
                    crop_obj.actual_yield = float(_actual_yield)
                    if crop_obj.actual_yield < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El rendimiento actual no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                except ValueError:
                    pass
            
            crop_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cultivo creado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear cultivo: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_crop_update(request):
    if request.method == 'GET':
        crop_id = request.GET.get('pk', '')
        if crop_id:
            crop_obj = Crop.objects.get(id=int(crop_id))
            plot_set = Plot.objects.filter(active=True).order_by('name')
            crop_type_set = CropType.objects.filter(is_active=True).order_by('name')
            t = loader.get_template('farm/crop_update.html')
            return JsonResponse({
                'form': t.render({
                    'crop_obj': crop_obj,
                    'plot_set': plot_set,
                    'crop_type_set': crop_type_set,
                    'status_set': Crop.STATUS_CHOICES,
                }, request),
            })


@csrf_exempt
def update_crop(request):
    if request.method == 'POST':
        try:
            crop_id = request.POST.get('crop_id', '')
            _plot_id = request.POST.get('plot_id', '')
            _crop_type = request.POST.get('crop_type', '')
            _crop_name = request.POST.get('crop_name', '')
            _planting_date = request.POST.get('planting_date', '')
            _estimated_harvest_date = request.POST.get('estimated_harvest_date', '')
            _actual_harvest_date = request.POST.get('actual_harvest_date', '')
            _status = request.POST.get('status', 'PLANTING')
            _planted_area = request.POST.get('planted_area', '')
            _expected_yield = request.POST.get('expected_yield', '')
            _actual_yield = request.POST.get('actual_yield', '')
            _description = request.POST.get('description', '')
            _observations = request.POST.get('observations', '')
            _active = request.POST.get('active', 'true')
            
            if not crop_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El ID del cultivo es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _crop_type:
                return JsonResponse({
                    'success': False,
                    'message': 'El tipo de cultivo es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _planting_date:
                return JsonResponse({
                    'success': False,
                    'message': 'La fecha de siembra es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _planted_area:
                return JsonResponse({
                    'success': False,
                    'message': 'El área sembrada es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            crop_obj = Crop.objects.get(id=int(crop_id))
            crop_obj.crop_type = _crop_type
            crop_obj.crop_name = _crop_name if _crop_name else None
            crop_obj.status = _status
            crop_obj.description = _description if _description else None
            crop_obj.observations = _observations if _observations else None
            crop_obj.active = (_active == 'true')
            
            if _plot_id:
                try:
                    crop_obj.plot = Plot.objects.get(id=int(_plot_id), active=True)
                except Plot.DoesNotExist:
                    crop_obj.plot = None
            else:
                crop_obj.plot = None
            
            try:
                crop_obj.planting_date = datetime.strptime(_planting_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de siembra inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if _estimated_harvest_date:
                try:
                    crop_obj.estimated_harvest_date = datetime.strptime(_estimated_harvest_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                crop_obj.estimated_harvest_date = None
            
            if _actual_harvest_date:
                try:
                    crop_obj.actual_harvest_date = datetime.strptime(_actual_harvest_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                crop_obj.actual_harvest_date = None
            
            try:
                crop_obj.planted_area = float(_planted_area)
                if crop_obj.planted_area <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'El área sembrada debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Área sembrada inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if _expected_yield:
                try:
                    crop_obj.expected_yield = float(_expected_yield)
                    if crop_obj.expected_yield < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El rendimiento esperado no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                except ValueError:
                    pass
            else:
                crop_obj.expected_yield = None
            
            if _actual_yield:
                try:
                    crop_obj.actual_yield = float(_actual_yield)
                    if crop_obj.actual_yield < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El rendimiento actual no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                except ValueError:
                    pass
            else:
                crop_obj.actual_yield = None
            
            crop_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cultivo actualizado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar cultivo: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


# ========== CROP CYCLE COST VIEWS ==========

def get_crop_cycle_cost_list(request):
    """List view for crop cycle costs, filtered by crop"""
    if request.method == 'GET':
        crop_set = Crop.objects.filter(active=True).order_by('-planting_date', 'plot')
        crop_id = request.GET.get('crop_id', '')
        selected_crop = None
        cost_set = None
        total_accumulated = Decimal('0.00')
        category_totals = {
            'JORNALES': Decimal('0.00'),
            'AGROQUIMICOS': Decimal('0.00'),
            'ALQUILER': Decimal('0.00'),
            'TRACTOR': Decimal('0.00'),
            'ELECTROSTATICA': Decimal('0.00'),
            'COSECHA': Decimal('0.00'),
        }
        
        # Separate cost sets: agrochemicals & services together, and fertilizers separately
        cost_set_agrochemicals_services = None
        cost_set_fertilizers = None
        total_accumulated_agrochemicals_services = Decimal('0.00')
        total_accumulated_fertilizers = Decimal('0.00')
        
        if crop_id:
            try:
                selected_crop = Crop.objects.get(id=int(crop_id), active=True)
                all_costs = CropCycleCost.objects.filter(crop_id=int(crop_id)).order_by('-application_date', 'id')
                
                # Filter costs: fertilizers (PRODUCT with FERTILIZER category)
                cost_set_fertilizers = all_costs.filter(
                    product__product_type=Product.PRODUCT,
                    product__product_category=Product.FERTILIZER
                ).order_by('application_date', 'product__name')
                
                # Prepare fertilizer table data: group by date and fertilizer
                fertilizer_table_data = []
                fertilizer_dates = []
                fertilizer_date_totals = []
                
                if cost_set_fertilizers:
                    # Get unique dates
                    dates_set = sorted(set(cost.application_date for cost in cost_set_fertilizers))
                    fertilizer_dates = dates_set
                    
                    # Get unique products
                    products_dict = {}
                    for cost in cost_set_fertilizers:
                        product_id = cost.product.id
                        if product_id not in products_dict:
                            products_dict[product_id] = {
                                'id': product_id,
                                'name': cost.product.name,
                                'unit': cost.unit,
                                'quantities_list': [],  # List of quantities in date order
                                'total_quantity': Decimal('0.00')
                            }
                        products_dict[product_id]['total_quantity'] += cost.quantity
                    
                    # Build quantities_list for each product in date order
                    for product_id, product_data in products_dict.items():
                        product_data['quantities_list'] = []
                        for date in fertilizer_dates:
                            # Find quantity for this date
                            quantity = None
                            for cost in cost_set_fertilizers:
                                if cost.product.id == product_id and cost.application_date == date:
                                    quantity = cost.quantity
                                    break
                            product_data['quantities_list'].append(quantity)
                    
                    # Convert to list sorted by name
                    fertilizer_table_data = sorted(products_dict.values(), key=lambda x: x['name'])
                    
                    # Calculate totals by date as list of (date, total) tuples
                    for date in fertilizer_dates:
                        date_costs = cost_set_fertilizers.filter(application_date=date)
                        date_total = date_costs.aggregate(total=Sum('total_cost'))
                        fertilizer_date_totals.append((date, date_total['total'] or Decimal('0.00')))
                
                # Filter costs: agrochemicals (PRODUCT with AGROCHEMICAL category) and services (SERVICE type) together
                cost_set_agrochemicals_services = all_costs.filter(
                    Q(product__product_type=Product.PRODUCT, product__product_category=Product.AGROCHEMICAL) |
                    Q(product__product_type=Product.SERVICE)
                )
                
                # Calculate totals for each type
                fertilizers_result = cost_set_fertilizers.aggregate(total=Sum('total_cost'))
                if fertilizers_result['total']:
                    total_accumulated_fertilizers = fertilizers_result['total']
                
                agrochemicals_services_result = cost_set_agrochemicals_services.aggregate(total=Sum('total_cost'))
                if agrochemicals_services_result['total']:
                    total_accumulated_agrochemicals_services = agrochemicals_services_result['total']
                
                # For backward compatibility, keep cost_set as all non-fertilizer costs
                cost_set = all_costs.exclude(
                    product__product_type=Product.PRODUCT,
                    product__product_category=Product.FERTILIZER
                )
                
                # Calculate total accumulated (excluding fertilizers)
                total_result = cost_set.aggregate(total=Sum('total_cost'))
                if total_result['total']:
                    total_accumulated = total_result['total']
                
                # Calculate totals by category (only agrochemicals and services, exclude fertilizers)
                for cost in cost_set:
                    if cost.total_cost:
                        category = cost.get_category()
                        # Skip fertilizers - they will have a separate report
                        if category == 'FERTILIZANTES':
                            continue
                        # Handle 'OTROS' category or add to existing
                        if category not in category_totals:
                            category_totals[category] = Decimal('0.00')
                        category_totals[category] += cost.total_cost
            except Crop.DoesNotExist:
                pass
        
        # Filter categories with values > 0 and create ordered list
        # Order: JORNALES, AGROQUIMICOS, ALQUILER, TRACTOR, ELECTROSTATICA, COSECHA, OTROS
        # Note: FERTILIZANTES excluded - they will have a separate report
        category_order = ['JORNALES', 'AGROQUIMICOS', 'ALQUILER', 'TRACTOR', 'ELECTROSTATICA', 'COSECHA', 'OTROS']
        category_list = []
        if crop_id:
            for cat in category_order:
                if cat in category_totals and category_totals[cat] > 0:
                    category_list.append((cat, category_totals[cat]))
            
            # Add any other categories not in the predefined order
            for cat, amount in category_totals.items():
                if cat not in category_order and amount > 0:
                    category_list.append((cat, amount))
        
        # Get active products (both agrochemicals and fertilizers) and services separately for global use
        # Include all products for the create modal (will be filtered by category in the frontend)
        product_set = Product.objects.filter(active=True, product_type=Product.PRODUCT).order_by('product_category', 'name')
        service_set = Product.objects.filter(active=True, product_type=Product.SERVICE).order_by('name')
        now_date = datetime.now()

        return render(request, 'farm/crop_cycle_cost_list.html', {
            'cost_set': cost_set,
            'cost_set_agrochemicals_services': cost_set_agrochemicals_services,
            'cost_set_fertilizers': cost_set_fertilizers,
            'total_accumulated_agrochemicals_services': total_accumulated_agrochemicals_services,
            'total_accumulated_fertilizers': total_accumulated_fertilizers,
            'fertilizer_table_data': fertilizer_table_data if 'fertilizer_table_data' in locals() else [],
            'fertilizer_dates': fertilizer_dates if 'fertilizer_dates' in locals() else [],
            'fertilizer_date_totals': fertilizer_date_totals if 'fertilizer_date_totals' in locals() else {},
            'crop_set': crop_set,
            'crop_id': crop_id,
            'selected_crop': selected_crop,
            'total_accumulated': total_accumulated,
            'category_totals': category_totals,
            'category_list': category_list,
            'product_set': product_set,
            'service_set': service_set,
            'unit_set': UNIT_CHOICES,
            'product_type_choices': Product.PRODUCT_TYPE_CHOICES,
            'last_update': now_date
        })


def get_crop_cycle_cost_grid(request):
    """Get crop cycle costs grid for AJAX loading"""
    if request.method == 'GET':
        crop_id = request.GET.get('crop_id', '')
        cost_set = None
        total_accumulated = Decimal('0.00')
        category_totals = {
            'JORNALES': Decimal('0.00'),
            'AGROQUIMICOS': Decimal('0.00'),
            'ALQUILER': Decimal('0.00'),
            'TRACTOR': Decimal('0.00'),
            'ELECTROSTATICA': Decimal('0.00'),
            'COSECHA': Decimal('0.00'),
        }
        
        if crop_id:
            try:
                cost_set = CropCycleCost.objects.filter(crop_id=int(crop_id)).order_by('-application_date', 'id')
                # Calculate total accumulated
                total_result = cost_set.aggregate(total=Sum('total_cost'))
                if total_result['total']:
                    total_accumulated = total_result['total']
                
                # Calculate totals by category (only agrochemicals and services, exclude fertilizers)
                for cost in cost_set:
                    if cost.total_cost:
                        category = cost.get_category()
                        # Skip fertilizers - they will have a separate report
                        if category == 'FERTILIZANTES':
                            continue
                        if category in category_totals:
                            category_totals[category] += cost.total_cost
                        else:
                            category_totals[category] = cost.total_cost
            except ValueError:
                pass
        
        return render(request, 'farm/crop_cycle_cost_grid_list.html', {
            'cost_set': cost_set,
            'total_accumulated': total_accumulated,
            'category_totals': category_totals,
        })


def modal_crop_cycle_cost_create(request):
    """Modal to create crop cycle cost"""
    if request.method == 'GET':
        crop_id = request.GET.get('crop_id', '')
        if not crop_id:
            return JsonResponse({
                'success': False,
                'message': 'Crop ID is required'
            }, status=HTTPStatus.BAD_REQUEST)
        
        try:
            crop = Crop.objects.get(id=int(crop_id), active=True)
        except Crop.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Crop not found'
            }, status=HTTPStatus.NOT_FOUND)
        
        # Get active products (both agrochemicals and fertilizers) and services separately
        product_set = Product.objects.filter(active=True, product_type=Product.PRODUCT).order_by('product_category', 'name')
        service_set = Product.objects.filter(active=True, product_type=Product.SERVICE).order_by('name')
        user_set = CustomUser.objects.filter(is_active=True).order_by('username')
        
        t = loader.get_template('farm/crop_cycle_cost_create.html')
        return JsonResponse({
            'form': t.render({
                'crop': crop,
                'product_set': product_set,
                'service_set': service_set,
                'user_set': user_set,
                'unit_set': UNIT_CHOICES,
                'product_type_choices': Product.PRODUCT_TYPE_CHOICES,
                'product_category_choices': Product.PRODUCT_CATEGORY_CHOICES,
                'current_user': request.user,
            }, request),
        })


@csrf_exempt
def create_crop_cycle_cost(request):
    """Create crop cycle cost"""
    if request.method == 'POST':
        try:
            # Get form data
            _crop_id = request.POST.get('crop_id', '')
            _product_id = request.POST.get('product_id', '')
            _application_date = request.POST.get('application_date', '')
            _quantity = request.POST.get('quantity', '')
            _unit = request.POST.get('unit', '')
            _application_method = request.POST.get('application_method', '')
            _dosage = request.POST.get('dosage', '')
            _responsible_id = request.POST.get('responsible_id', '')
            _weather_conditions = request.POST.get('weather_conditions', '')
            _observations = request.POST.get('observations', '')
            _application_cost = request.POST.get('application_cost', '')
            _total_cost = request.POST.get('total_cost', '')
            
            # Validate required fields
            if not _crop_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Cultivo es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _application_date:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de aplicación es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _unit:
                return JsonResponse({
                    'success': False,
                    'message': 'Unidad es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate crop exists
            try:
                crop = Crop.objects.get(id=int(_crop_id), active=True)
            except Crop.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Cultivo no encontrado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Validate product exists
            try:
                product = Product.objects.get(id=int(_product_id), active=True)
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Create CropCycleCost object
            cost_obj = CropCycleCost(
                crop_id=int(_crop_id),
                product_id=int(_product_id),
                application_method=_application_method if _application_method else None,
                dosage=_dosage if _dosage else None,
                weather_conditions=_weather_conditions if _weather_conditions else None,
                observations=_observations if _observations else None,
            )
            
            # Process application date
            try:
                cost_obj.application_date = datetime.strptime(_application_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de aplicación inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Process quantity
            try:
                quantity_val = float(_quantity)
                if quantity_val <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'La cantidad debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
                cost_obj.quantity = quantity_val
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cost_obj.unit = _unit
            
            # Process responsible
            if _responsible_id:
                try:
                    cost_obj.responsible_id = int(_responsible_id)
                except ValueError:
                    pass
            
            # Process application cost
            if _application_cost:
                try:
                    app_cost = float(_application_cost)
                    if app_cost < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El costo de aplicación no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                    cost_obj.application_cost = app_cost
                except ValueError:
                    pass
            
            # Process total cost
            if _total_cost:
                try:
                    total_cost_val = float(_total_cost)
                    if total_cost_val < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El costo total no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                    cost_obj.total_cost = total_cost_val
                except ValueError:
                    pass
            
            cost_obj.save()
            
            # Create inventory transaction automatically if product has inventory (PRODUCT type with category)
            # Register as exit (consumption) when a PRODUCT type is used in crop cycle cost
            if product.product_type == Product.PRODUCT and product.has_inventory():
                exit_quantity_liters = None
                
                # Convert quantity to liters based on unit
                if _unit == 'L':
                    # Direct liters
                    exit_quantity_liters = Decimal(str(quantity_val))
                elif _unit == 'ML':
                    # Convert milliliters to liters (divide by 1000)
                    exit_quantity_liters = Decimal(str(quantity_val)) / Decimal('1000')
                elif _unit in ['KG', 'G', 'BAG', 'SACK', 'CONTAINER']:
                    # These units cannot be automatically converted to liters without density information
                    # For now, we skip auto-registration but could be improved in the future
                    # If product unit is L or ML, use that as a hint
                    if product.unit == 'L':
                        # If product's default unit is liters, assume the quantity is in liters
                        exit_quantity_liters = Decimal(str(quantity_val))
                    elif product.unit == 'ML':
                        # If product's default unit is milliliters, convert
                        exit_quantity_liters = Decimal(str(quantity_val)) / Decimal('1000')
                    # Otherwise, skip automatic registration (user can register manually)
                
                # Create inventory exit transaction if we have a valid quantity in liters
                if exit_quantity_liters is not None and exit_quantity_liters > 0:
                    try:
                        # Build observations text
                        obs_text = f'Aplicación automática desde costo de ciclo de cultivo'
                        if cost_obj.application_method:
                            obs_text += f' - Método: {cost_obj.application_method}'
                        if cost_obj.observations:
                            obs_text += f' - Observaciones: {cost_obj.observations}'
                        
                        inventory_transaction = InventoryTransaction(
                            product=product,
                            exit_date=cost_obj.application_date,
                            exit_quantity=exit_quantity_liters,
                            crop=crop,
                            observations=obs_text
                        )
                        inventory_transaction.save()
                    except Exception as inv_error:
                        # Log error but don't fail the crop cycle cost creation
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Error creating inventory transaction for crop cycle cost {cost_obj.id}: {str(inv_error)}')
            
            return JsonResponse({
                'success': True,
                'message': 'Costo de ciclo de cultivo registrado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar costo: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_crop_cycle_cost_update(request):
    """Modal to update crop cycle cost"""
    if request.method == 'GET':
        cost_id = request.GET.get('pk', '')
        if cost_id:
            try:
                cost_obj = CropCycleCost.objects.get(id=int(cost_id))
            except CropCycleCost.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Costo no encontrado'
                }, status=HTTPStatus.NOT_FOUND)
            
            # Get active products (only agrochemicals) and services separately
            # Exclude fertilizers - they will have a separate report
            product_set = Product.objects.filter(active=True, product_type=Product.PRODUCT, product_category=Product.AGROCHEMICAL).order_by('name')
            service_set = Product.objects.filter(active=True, product_type=Product.SERVICE).order_by('name')
            user_set = CustomUser.objects.filter(is_active=True).order_by('username')
            
            t = loader.get_template('farm/crop_cycle_cost_update.html')
            return JsonResponse({
                'form': t.render({
                    'cost_obj': cost_obj,
                    'product_set': product_set,
                    'service_set': service_set,
                    'user_set': user_set,
                    'unit_set': UNIT_CHOICES,
                    'product_type_choices': Product.PRODUCT_TYPE_CHOICES,
                }, request),
            })


@csrf_exempt
def update_crop_cycle_cost(request):
    """Update crop cycle cost"""
    if request.method == 'POST':
        try:
            cost_id = request.POST.get('cost_id', '')
            _crop_id = request.POST.get('crop_id', '')
            _product_id = request.POST.get('product_id', '')
            _application_date = request.POST.get('application_date', '')
            _quantity = request.POST.get('quantity', '')
            _unit = request.POST.get('unit', '')
            _application_method = request.POST.get('application_method', '')
            _dosage = request.POST.get('dosage', '')
            _responsible_id = request.POST.get('responsible_id', '')
            _weather_conditions = request.POST.get('weather_conditions', '')
            _observations = request.POST.get('observations', '')
            _application_cost = request.POST.get('application_cost', '')
            _total_cost = request.POST.get('total_cost', '')
            
            if not cost_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID de costo es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _crop_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Cultivo es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _application_date:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de aplicación es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _unit:
                return JsonResponse({
                    'success': False,
                    'message': 'Unidad es requerida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cost_obj = CropCycleCost.objects.get(id=int(cost_id))
            
            # Get old values before updating (for inventory transaction matching)
            old_product_id = cost_obj.product_id
            old_crop_id = cost_obj.crop_id
            old_quantity = cost_obj.quantity
            old_unit = cost_obj.unit
            old_date = cost_obj.application_date
            
            cost_obj.crop_id = int(_crop_id)
            cost_obj.product_id = int(_product_id)
            cost_obj.unit = _unit
            cost_obj.application_method = _application_method if _application_method else None
            cost_obj.dosage = _dosage if _dosage else None
            cost_obj.weather_conditions = _weather_conditions if _weather_conditions else None
            cost_obj.observations = _observations if _observations else None
            
            # Process application date
            try:
                cost_obj.application_date = datetime.strptime(_application_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Fecha de aplicación inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Process quantity
            try:
                quantity_val = float(_quantity)
                if quantity_val <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'La cantidad debe ser mayor a cero'
                    }, status=HTTPStatus.BAD_REQUEST)
                cost_obj.quantity = quantity_val
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Cantidad inválida'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Process responsible
            if _responsible_id:
                try:
                    cost_obj.responsible_id = int(_responsible_id)
                except ValueError:
                    pass
            else:
                cost_obj.responsible = None
            
            # Process application cost
            if _application_cost:
                try:
                    app_cost = float(_application_cost)
                    if app_cost < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El costo de aplicación no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                    cost_obj.application_cost = app_cost
                except ValueError:
                    pass
            else:
                cost_obj.application_cost = None
            
            # Process total cost
            if _total_cost:
                try:
                    total_cost_val = float(_total_cost)
                    if total_cost_val < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'El costo total no puede ser negativo'
                        }, status=HTTPStatus.BAD_REQUEST)
                    cost_obj.total_cost = total_cost_val
                except ValueError:
                    pass
            else:
                cost_obj.total_cost = None
            
            # Validate product exists before saving
            try:
                updated_product = Product.objects.get(id=int(_product_id), active=True)
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado'
                }, status=HTTPStatus.BAD_REQUEST)
            
            cost_obj.save()
            
            # Update or create inventory transaction if product is PRODUCT type with inventory
            if updated_product.product_type == Product.PRODUCT and updated_product.has_inventory():
                exit_quantity_liters = None
                
                # Convert quantity to liters based on unit
                if _unit == 'L':
                    exit_quantity_liters = Decimal(str(quantity_val))
                elif _unit == 'ML':
                    exit_quantity_liters = Decimal(str(quantity_val)) / Decimal('1000')
                elif _unit in ['KG', 'G', 'BAG', 'SACK', 'CONTAINER']:
                    # Use product's default unit as hint
                    if updated_product.unit == 'L':
                        exit_quantity_liters = Decimal(str(quantity_val))
                    elif updated_product.unit == 'ML':
                        exit_quantity_liters = Decimal(str(quantity_val)) / Decimal('1000')
                
                if exit_quantity_liters is not None and exit_quantity_liters > 0:
                    try:
                        # Try to find existing inventory transaction related to this cost
                        # Look for transaction with same product, crop, and date from the old values
                        related_transaction = None
                        if old_product_id and old_crop_id and old_date:
                            try:
                                old_product_obj = Product.objects.get(id=old_product_id)
                                old_crop_obj = Crop.objects.get(id=old_crop_id)
                                
                                # Search for transaction with old product, old crop, and old date
                                related_transaction = InventoryTransaction.objects.filter(
                                    product_id=old_product_id,
                                    crop_id=old_crop_id,
                                    exit_date=old_date,
                                    exit_quantity__isnull=False,
                                    observations__icontains='Aplicación automática desde costo de ciclo'
                                ).order_by('-created_at').first()
                            except (Product.DoesNotExist, Crop.DoesNotExist):
                                pass
                        
                        # Build observations text
                        obs_text = f'Aplicación automática desde costo de ciclo de cultivo'
                        if cost_obj.application_method:
                            obs_text += f' - Método: {cost_obj.application_method}'
                        if cost_obj.observations:
                            obs_text += f' - Observaciones: {cost_obj.observations}'
                        
                        if related_transaction and 'Aplicación automática desde costo de ciclo' in (related_transaction.observations or ''):
                            # Update existing transaction
                            related_transaction.product = updated_product
                            related_transaction.exit_date = cost_obj.application_date
                            related_transaction.exit_quantity = exit_quantity_liters
                            related_transaction.crop = cost_obj.crop
                            related_transaction.observations = obs_text
                            related_transaction.save()
                        else:
                            # Create new transaction
                            inventory_transaction = InventoryTransaction(
                                product=updated_product,
                                exit_date=cost_obj.application_date,
                                exit_quantity=exit_quantity_liters,
                                crop=cost_obj.crop,
                                observations=obs_text
                            )
                            inventory_transaction.save()
                    except Exception as inv_error:
                        # Log error but don't fail the cost update
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Error updating inventory transaction for crop cycle cost {cost_obj.id}: {str(inv_error)}')
            
            return JsonResponse({
                'success': True,
                'message': 'Costo de ciclo de cultivo actualizado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar costo: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


# ========== SERVICE TYPE VIEWS ==========

def modal_service_type_create(request):
    """Modal to manage service types (list, create, update)"""
    if request.method == 'GET':
        action = request.GET.get('action', 'list')  # 'list', 'create', or 'update'
        
        if action == 'create':
            t = loader.get_template('farm/service_type_create.html')
            return JsonResponse({
                'form': t.render({}, request),
            })
        else:
            # Show list
            service_type_set = ServiceType.objects.all().order_by('name')
            t = loader.get_template('farm/service_type_manage.html')
            return JsonResponse({
                'form': t.render({
                    'service_type_set': service_type_set,
                }, request),
            })


@csrf_exempt
def create_service_type(request):
    """Create service type"""
    if request.method == 'POST':
        try:
            _name = request.POST.get('name', '')
            _description = request.POST.get('description', '')
            _active = request.POST.get('active', 'true')
            
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            # Check if name already exists
            if ServiceType.objects.filter(name=_name).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe un tipo de servicio con ese nombre'
                }, status=HTTPStatus.BAD_REQUEST)
            
            service_type_obj = ServiceType(
                name=_name,
                description=_description if _description else '',
                active=(_active == 'true'),
            )
            service_type_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Tipo de servicio creado exitosamente'
            }, status=HTTPStatus.OK)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear tipo de servicio: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def modal_service_type_update(request):
    """Modal to update service type"""
    if request.method == 'GET':
        service_type_id = request.GET.get('pk', '')
        if service_type_id:
            service_type_obj = ServiceType.objects.get(id=int(service_type_id))
            t = loader.get_template('farm/service_type_update.html')
            return JsonResponse({
                'form': t.render({
                    'service_type_obj': service_type_obj,
                }, request),
            })


@csrf_exempt
def update_service_type(request):
    """Update service type"""
    if request.method == 'POST':
        try:
            service_type_id = request.POST.get('service_type_id', '')
            _name = request.POST.get('name', '')
            _description = request.POST.get('description', '')
            _active = request.POST.get('active', 'true')
            
            if not service_type_id:
                return JsonResponse({
                    'success': False,
                    'message': 'El ID del tipo de servicio es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            if not _name:
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre es requerido'
                }, status=HTTPStatus.BAD_REQUEST)
            
            service_type_obj = ServiceType.objects.get(id=int(service_type_id))
            
            # Check if name already exists (excluding current record)
            if ServiceType.objects.filter(name=_name).exclude(id=service_type_obj.id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe otro tipo de servicio con ese nombre'
                }, status=HTTPStatus.BAD_REQUEST)
            
            service_type_obj.name = _name
            service_type_obj.description = _description if _description else ''
            service_type_obj.active = (_active == 'true')
            service_type_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Tipo de servicio actualizado exitosamente'
            }, status=HTTPStatus.OK)
            
        except ServiceType.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Tipo de servicio no encontrado'
            }, status=HTTPStatus.NOT_FOUND)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar tipo de servicio: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@csrf_exempt
def get_service_types(request):
    """Get all active service types for AJAX"""
    if request.method == 'GET':
        try:
            service_types = ServiceType.objects.filter(active=True).order_by('name')
            service_types_list = [{'id': st.id, 'name': st.name} for st in service_types]
            return JsonResponse({
                'success': True,
                'service_types': service_types_list
            }, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener tipos de servicio: {str(e)}'
            }, status=HTTPStatus.INTERNAL_SERVER_ERROR)
