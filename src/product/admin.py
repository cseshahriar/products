# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    Variant, Product, ProductImage, ProductVariant, ProductVariantPrice
)


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'title',
        'description',
        'active',
    )
    list_filter = ('created_at', 'updated_at', 'active')
    date_hierarchy = 'created_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'title',
        'sku',
        'description',
    )
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'product', 'file_path')
    list_filter = ('created_at', 'updated_at', 'product')
    date_hierarchy = 'created_at'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'variant_title',
        'variant',
        'product',
    )
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(ProductVariantPrice)
class ProductVariantPriceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'updated_at',
        'product_variant_one',
        'product_variant_two',
        'product_variant_three',
        'price',
        'stock',
        'product',
    )
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
