from django.db import models
from config.g_model import TimeStampMixin


# Create your models here.
class Variant(TimeStampMixin):
    title = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Product(TimeStampMixin):
    title = models.CharField(max_length=255)
    sku = models.SlugField(max_length=255, unique=True)
    description = models.TextField()

    @property
    def get_product_variants(self):
        """ return product variants """
        variants = self.productvariant_set.all()
        return variants

    def __str__(self):
        return self.title


def photo_upload_path(instance, filename):
    """Custom file 'upload_to' directory returned from formatted string"""
    return f'products/{instance.pk}/{filename}'


class ProductImage(TimeStampMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    thumbnail = models.ImageField(
        upload_to=photo_upload_path, null=True, blank=False
    )


class ProductVariant(TimeStampMixin):
    variant_title = models.CharField(max_length=255)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(default=0.00)
    stock = models.IntegerField(default=1)


class ProductVariantPrice(TimeStampMixin):
    product_variant_one = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True,
        related_name='product_variant_one'
    )
    product_variant_two = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True,
        related_name='product_variant_two'
    )
    product_variant_three = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True,
        related_name='product_variant_three'
    )
    price = models.FloatField()
    stock = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
