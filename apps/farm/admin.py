from django.contrib import admin
from .models import Product, ServiceType, Plot, CropType, Crop, CropCycleCost, InventoryTransaction


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'product_category', 'service_type', 'unit', 'unit_price', 'active', 'created_at')
    list_filter = ('product_type', 'product_category', 'service_type', 'unit', 'active', 'created_at')
    search_fields = ('name', 'unit')
    readonly_fields = ('created_at',)
    
    def get_fieldsets(self, request, obj=None):
        """Dynamically adjust fieldsets based on product_type"""
        fieldsets = (
            ('Basic Information', {
                'fields': ('name', 'product_type', 'active')
            }),
            ('Commercial Information', {
                'fields': ('unit', 'unit_price')
            }),
            ('Dates', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )
        
        # Add conditional fields based on product_type
        if obj and obj.product_type == Product.SERVICE:
            # For services, show service_type field
            fieldsets = (
                ('Basic Information', {
                    'fields': ('name', 'product_type', 'service_type', 'active')
                }),
                ('Commercial Information', {
                    'fields': ('unit', 'unit_price')
                }),
                ('Dates', {
                    'fields': ('created_at',),
                    'classes': ('collapse',)
                }),
            )
        elif obj and obj.product_type == Product.PRODUCT:
            # For products, show product_category field
            fieldsets = (
                ('Basic Information', {
                    'fields': ('name', 'product_type', 'product_category', 'active')
                }),
                ('Commercial Information', {
                    'fields': ('unit', 'unit_price')
                }),
                ('Dates', {
                    'fields': ('created_at',),
                    'classes': ('collapse',)
                }),
            )
        else:
            # For new objects, show both fields with description
            fieldsets = (
                ('Basic Information', {
                    'fields': ('name', 'product_type', 'active')
                }),
                ('Type Configuration', {
                    'fields': ('product_category', 'service_type'),
                    'description': 'Select product_category if type is PRODUCT, or service_type if type is SERVICE'
                }),
                ('Commercial Information', {
                    'fields': ('unit', 'unit_price')
                }),
                ('Dates', {
                    'fields': ('created_at',),
                    'classes': ('collapse',)
                }),
            )
        
        return fieldsets


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'description')
    list_filter = ('active',)
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'active')
        }),
    )


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'subsidiary', 'area_hectares', 'location', 'active', 'created_at')
    list_filter = ('active', 'created_at', 'subsidiary')
    search_fields = ('name', 'location', 'subsidiary__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subsidiary', 'area_hectares', 'active')
        }),
        ('Location', {
            'fields': ('location', 'coordinates')
        }),
        ('Additional Information', {
            'fields': ('description', 'observations')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropType)
class CropTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'description')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
    )


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('crop_name', 'crop_type', 'plot', 'planting_date', 'status', 'active', 'created_at')
    list_filter = ('status', 'active', 'planting_date', 'plot')
    search_fields = ('crop_name', 'crop_type', 'plot__name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'planting_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('plot', 'crop_type', 'crop_name', 'status', 'active')
        }),
        ('Dates', {
            'fields': ('planting_date', 'estimated_harvest_date', 'actual_harvest_date')
        }),
        ('Area and Yield', {
            'fields': ('planted_area', 'expected_yield', 'actual_yield')
        }),
        ('Additional Information', {
            'fields': ('description', 'observations')
        }),
        ('System Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropCycleCost)
class CropCycleCostAdmin(admin.ModelAdmin):
    list_display = ('product', 'crop', 'application_date', 'quantity', 'unit', 'application_cost', 'total_cost', 'responsible', 'created_at')
    list_filter = ('application_date', 'product__product_type', 'crop__plot', 'responsible')
    search_fields = ('product__name', 'crop__crop_name', 'crop__crop_type', 'crop__plot__name',
                    'application_method', 'observations')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'application_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('crop', 'product', 'application_date', 'responsible')
        }),
        ('Application', {
            'fields': ('quantity', 'unit', 'dosage', 'application_method')
        }),
        ('Conditions and Costs', {
            'fields': ('weather_conditions', 'application_cost', 'total_cost')
        }),
        ('Additional Information', {
            'fields': ('observations',)
        }),
        ('System Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'entry_date', 'entry_quantity', 'exit_date', 'crop', 'exit_quantity', 'balance', 'created_at')
    list_filter = ('product', 'entry_date', 'exit_date', 'crop', 'created_at')
    search_fields = ('product__name', 'crop__crop_name', 'crop__crop_type', 'observations')
    readonly_fields = ('balance', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Product Information', {
            'fields': ('product',),
            'description': 'Note: Only PRODUCT type with category (AGROCHEMICAL or FERTILIZER) can have inventory. Services cannot have inventory transactions.'
        }),
        ('Entry Information', {
            'fields': ('entry_date', 'entry_quantity')
        }),
        ('Exit Information', {
            'fields': ('exit_date', 'crop', 'exit_quantity')
        }),
        ('Balance', {
            'fields': ('balance',)
        }),
        ('Additional Information', {
            'fields': ('observations',)
        }),
        ('System Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter products to show only those that can have inventory
        (PRODUCT type with category, excluding SERVICES)
        """
        if db_field.name == 'product':
            kwargs['queryset'] = Product.objects.filter(
                product_type=Product.PRODUCT,
                product_category__isnull=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
