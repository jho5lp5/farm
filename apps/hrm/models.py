from django.core.validators import MaxLengthValidator
from django.db import models
from apps.users.models import CustomUser
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Adjust


class Subsidiary(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    serial = models.CharField(max_length=4, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=45, null=True, blank=True)
    email = models.EmailField(max_length=45, null=True, blank=True)
    ruc = models.CharField('RUC', max_length=11, null=True, blank=True)
    business_name = models.CharField('Razón social', max_length=100, null=True, blank=True)
    representative_name = models.CharField(max_length=100, null=True, blank=True)
    representative_dni = models.CharField(max_length=45, null=True, blank=True)
    observation = models.CharField(max_length=500, null=True, blank=True)
    url = models.CharField(max_length=500, null=True, blank=True)
    token = models.CharField(max_length=500, null=True, blank=True)
    photo = models.ImageField(upload_to='subsidiary/', default='subsidiary/employee0.jpg', blank=True)
    photo_thumbnail = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1), ResizeToFill(100, 100)], source='photo',
                                     format='JPEG', options={'quality': 90})
    text_description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'


class Area(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'


class FunctionArea(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.description)


class Charge(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    charge = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.charge)


class FunctionCharge(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    charge = models.ForeignKey('Charge', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.charge)


class Department(models.Model):
    id = models.CharField(primary_key=True, max_length=6)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Departameto'
        verbose_name_plural = 'Departametos'


class Province(models.Model):
    id = models.CharField(primary_key=True, max_length=6)
    description = models.CharField(max_length=200, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'


class District(models.Model):
    id = models.CharField(primary_key=True, max_length=6)
    description = models.CharField(max_length=200, null=True, blank=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Distrito'
        verbose_name_plural = 'Distritos'


