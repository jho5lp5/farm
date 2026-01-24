from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.users.models import CustomUser

UNIT_CHOICES = (
    ('KG', 'Kilograms'), ('L', 'Liters'), ('G', 'Grams'), ('ML', 'Milliliters'), ('BAG', 'Bag'), ('SACK', 'Sack'),
    ('CONTAINER', 'Container'), ('HOUR', 'Hour'), ('DAY', 'Day'), ('SERVICE', 'Service'),
)


class Product(models.Model):

    # -----------------------------
    # TIPOS
    # -----------------------------
    PRODUCT = 'PRODUCT'
    SERVICE = 'SERVICE'

    PRODUCT_TYPE_CHOICES = [
        (PRODUCT, 'Product'),
        (SERVICE, 'Service'),
    ]

    # -----------------------------
    # CATEGORÍAS DE PRODUCTO
    # -----------------------------
    AGROCHEMICAL = 'AGROQUÍMICO'
    FERTILIZER = 'FERTILIZANTE'

    PRODUCT_CATEGORY_CHOICES = [
        (AGROCHEMICAL, 'Agrochemical'),
        (FERTILIZER, 'Fertilizer'),
    ]

    # -----------------------------
    # CAMPOS
    # -----------------------------
    name = models.CharField(max_length=200)

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default=PRODUCT
    )

    # SOLO PARA PRODUCTOS
    product_category = models.CharField(
        max_length=20,
        choices=PRODUCT_CATEGORY_CHOICES,
        null=True,
        blank=True
    )

    brand = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    expiration_date = models.DateField(
        null=True,
        blank=True
    )

    # SOLO PARA SERVICIOS
    service_type = models.ForeignKey(
        'ServiceType',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    # COMÚN
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='KG'
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    observations = models.TextField(
        null=True,
        blank=True
    )

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_inventory(self):
        """
        Check if the product can have inventory transactions.
        Only PRODUCT type with category (AGROCHEMICAL or FERTILIZER) can have inventory.
        Services cannot have inventory.
        """
        return self.product_type == self.PRODUCT and self.product_category is not None

    def __str__(self):
        return self.name


class ServiceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Plot(models.Model):
    """
    Model to represent a plot or farm of the user
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField('Name', max_length=200)
    area_hectares = models.DecimalField('Area in Hectares', max_digits=10, decimal_places=4,
                                        validators=[MinValueValidator(Decimal('0.0001'))])
    location = models.CharField('Location', max_length=300, null=True, blank=True)
    subsidiary = models.ForeignKey('hrm.Subsidiary', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    coordinates = models.CharField('Coordinates (Lat, Long)', max_length=100, null=True, blank=True)
    active = models.BooleanField('Active', default=True)
    observations = models.TextField('Observations', null=True, blank=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.area_hectares} ha)"
    
    class Meta:
        verbose_name = 'Plot'
        verbose_name_plural = 'Plots'
        ordering = ['name']


class CropType(models.Model):
    """
    Model to represent different types of crops
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Crop Type'
        verbose_name_plural = 'Crop Types'
        ordering = ['name']


class Crop(models.Model):
    """
    Model to represent a crop (sembrío) in a plot
    """
    STATUS_CHOICES = (
        ('PREPARATION', 'Preparation'),
        ('PLANTING', 'Planting'),
        ('GROWTH', 'Growth'),
        ('FLOWERING', 'Flowering'),
        ('FRUITING', 'Fruiting'),
        ('HARVEST', 'Harvest'),
        ('FINISHED', 'Finished'),
    )
    
    id = models.AutoField(primary_key=True)
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='crops',  null=True, blank=True,
                             verbose_name='Plot')
    crop_type = models.CharField('Crop Type', max_length=200,
                                 help_text='Type of crop (e.g., Corn, Grape, Wheat, etc.)')
    crop_name = models.CharField('Crop Name', max_length=200, null=True, blank=True,
                                 help_text='Specific name or variety of the crop')
    planting_date = models.DateField('Planting Date')
    estimated_harvest_date = models.DateField('Estimated Harvest Date', null=True, blank=True)
    actual_harvest_date = models.DateField('Actual Harvest Date', null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PLANTING')
    planted_area = models.DecimalField('Planted Area (ha)', max_digits=10, decimal_places=4,
                                       validators=[MinValueValidator(Decimal('0.0001'))],
                                       help_text='Specific area planted within the hectare')
    expected_yield = models.DecimalField('Expected Yield (kg/ha)', max_digits=10,
                                         decimal_places=2, null=True, blank=True,
                                         validators=[MinValueValidator(Decimal('0.00'))])
    actual_yield = models.DecimalField('Actual Yield (kg/ha)', max_digits=10,
                                       decimal_places=2, null=True, blank=True,
                                       validators=[MinValueValidator(Decimal('0.00'))])
    description = models.TextField('Description', null=True, blank=True)
    observations = models.TextField('Observations', null=True, blank=True)
    active = models.BooleanField('Active', default=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    def __str__(self):
        crop_display = self.crop_name if self.crop_name else self.crop_type
        return f"{crop_display} - {self.plot.name} ({self.planting_date})"
    
    class Meta:
        verbose_name = 'Crop'
        verbose_name_plural = 'Crops'
        ordering = ['-planting_date', 'plot']


class CropCycleCost(models.Model):
    """
    Model to record the application of products (agrochemicals/fertilizers) to crops
    """
    id = models.AutoField(primary_key=True)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='crop_cycle_costs',
                             verbose_name='Crop')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='crop_cycle_costs',
                                verbose_name='Product')
    application_date = models.DateField('Application Date')
    quantity = models.DecimalField('Quantity', max_digits=10, decimal_places=4,
                                   validators=[MinValueValidator(Decimal('0.0001'))])
    unit = models.CharField('Unit', max_length=20, help_text='Unit in which the quantity was applied')
    application_method = models.CharField('Application Method', max_length=100, null=True, blank=True,
                                          help_text='E.g., Foliar, Irrigation, Direct application, etc.')
    dosage = models.CharField('Dosage', max_length=100, null=True, blank=True,
                              help_text='E.g., 2 liters per hectare, 500g per 100L of water, etc.')
    responsible = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='crop_cycle_costs_made', verbose_name='Responsible')
    weather_conditions = models.CharField('Weather Conditions', max_length=200, null=True, blank=True,
                                          help_text='E.g., Sunny, Cloudy, Moderate wind, etc.')
    observations = models.TextField('Observations', null=True, blank=True)
    application_cost = models.DecimalField('Application Cost', max_digits=10, decimal_places=2,
                                           null=True, blank=True, validators=[MinValueValidator(Decimal('0.00'))])
    total_cost = models.DecimalField('Total Cost', max_digits=12, decimal_places=2, null=True, blank=True,
                                     validators=[MinValueValidator(Decimal('0.00'))],
                                     help_text='Total cost invested in this application')
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    def get_category(self):
        """Get cost category based on product"""
        if self.product.product_category:
            if self.product.product_category == Product.AGROCHEMICAL:
                return 'AGROQUIMICOS'
            elif self.product.product_category == Product.FERTILIZER:
                return 'FERTILIZANTES'
        elif self.product.product_type == Product.SERVICE:
            product_name_upper = self.product.name.upper()
            if 'TRACTOR' in product_name_upper:
                return 'TRACTOR'
            elif 'ALQUILER' in product_name_upper or 'RENT' in product_name_upper:
                return 'ALQUILER'
            elif 'JORNAL' in product_name_upper or 'LABOR' in product_name_upper or 'MANO DE OBRA' in product_name_upper:
                return 'JORNALES'
            elif 'COSECHA' in product_name_upper or 'HARVEST' in product_name_upper:
                return 'COSECHA'
            elif 'ELECTROSTATIC' in product_name_upper or 'ELECTROSTATICA' in product_name_upper:
                return 'ELECTROSTATICA'
        return 'OTROS'
    
    def __str__(self):
        return f"{self.product.name} - {self.crop} ({self.application_date})"
    
    class Meta:
        verbose_name = 'Crop Cycle Cost'
        verbose_name_plural = 'Crop Cycle Costs'
        ordering = ['-application_date', 'crop']
        indexes = [
            models.Index(fields=['crop', 'application_date']),
            models.Index(fields=['product', 'application_date']),
        ]


class InventoryTransaction(models.Model):
    """
    Model to record inventory entries and exits (physical kardex)
    Only products of type PRODUCT with category (AGROCHEMICAL or FERTILIZER) can have inventory transactions.
    Services (SERVICE type) cannot have inventory.
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_transactions',
                                verbose_name='Product')
    entry_date = models.DateField('Entry Date', null=True, blank=True)
    entry_quantity = models.DecimalField('Entry Quantity (L)', max_digits=10, decimal_places=2,
                                         null=True, blank=True,
                                         validators=[MinValueValidator(Decimal('0.00'))],
                                         help_text='Quantity in liters')
    exit_date = models.DateField('Exit Date', null=True, blank=True)
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='inventory_transactions', verbose_name='Crop',
                             help_text='Crop where the product was used (reason for exit)')
    exit_quantity = models.DecimalField('Exit Quantity (L)', max_digits=10, decimal_places=2, null=True, blank=True,
                                        validators=[MinValueValidator(Decimal('0.00'))],
                                        help_text='Quantity in liters')
    balance = models.DecimalField('Balance', max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                  validators=[MinValueValidator(Decimal('0.00'))])
    observations = models.TextField('Observations', null=True, blank=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    
    def save(self, *args, **kwargs):
        """
        Calculate balance automatically based on previous transactions for the same product
        Recalculates all balances for the product to ensure consistency
        Only products (not services) can have inventory transactions
        """
        # Validate that the product is not a service
        if not self.product.has_inventory():
            raise ValueError(f"Product '{self.product.name}' is a service and cannot have inventory transactions. Only PRODUCT type with category can have inventory.")
        
        # Save first to get the ID if it's a new transaction
        is_new = self.id is None
        super().save(*args, **kwargs)
        
        # Recalculate all balances for this product from scratch
        # This ensures consistency even when transactions are updated
        all_transactions = InventoryTransaction.objects.filter(
            product=self.product
        ).order_by('created_at', 'id')
        
        current_balance = Decimal('0.00')
        transactions_to_update = []
        
        for transaction in all_transactions:
            if transaction.entry_quantity:
                current_balance += transaction.entry_quantity
            if transaction.exit_quantity:
                current_balance -= transaction.exit_quantity
            
            # Only update if balance changed
            if transaction.balance != current_balance:
                transaction.balance = current_balance
                transactions_to_update.append(transaction)
        
        # Bulk update all transactions that need balance updates
        if transactions_to_update:
            InventoryTransaction.objects.bulk_update(transactions_to_update, ['balance'])
    
    def __str__(self):
        if self.entry_quantity:
            return f"{self.product.name} - Entry: {self.entry_quantity}L on {self.entry_date}"
        elif self.exit_quantity:
            crop_name = self.crop.__str__() if self.crop else "N/A"
            return f"{self.product.name} - Exit: {self.exit_quantity}L to {crop_name} on {self.exit_date}"
        return f"{self.product.name} - Transaction #{self.id}"
    
    class Meta:
        verbose_name = 'Inventory Transaction'
        verbose_name_plural = 'Inventory Transactions'
        ordering = ['product', 'created_at', 'id']
        indexes = [
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['crop']),
        ]