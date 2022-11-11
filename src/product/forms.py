from django.db.models import Q
from django_filters import (  # noqa
    FilterSet, OrderingFilter, CharFilter, filters,
    ModelChoiceFilter, ChoiceFilter, DateFilter, DateRangeFilter,  # noqa
    DateFromToRangeFilter, RangeFilter
)
from django_filters.widgets import RangeWidget
from django.forms import (
    forms, ModelForm, CharField, TextInput, Textarea, BooleanField,
    CheckboxInput
)
from django.forms.models import modelformset_factory
from product.models import (
    Variant, Product, ProductVariant, ProductVariantPrice
)


class VariantForm(ModelForm):
    class Meta:
        model = Variant
        fields = '__all__'
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'active': CheckboxInput(
                attrs={'class': 'form-check-input', 'id': 'active'}
            )
        }


class ProductVariantForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductVariantForm, self).__init__(*args, **kwargs)
        self.fields['variant'].queryset = Variant.objects.filter(
            active=True
        )

    class Meta:
        model = ProductVariant
        fields = ['variant_title', 'variant', 'price', 'stock']

        labels = {
           'variant_title': '',
           'variant': '',
           'price': '',
           'stock': '',
        }


ProductVariantFormFormSet = modelformset_factory(
    ProductVariant, form=ProductVariantForm, extra=1, can_delete=True,
    min_num=1, max_num=3
)


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'sku', 'description']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'active': CheckboxInput(
                attrs={'class': 'form-check-input', 'id': 'active'}
            )
        }


class ProductFilterSet(FilterSet):
    q = CharFilter(label='Search by Title', method='filter_by_q')
    variant = ChoiceFilter(
        choices=(
            [(obj.pk, obj.title) for obj in Variant.objects.all()]
        ),
        field_name='variant',
        empty_label='--Select A Variant--',
        method='filter_by_variant'
    )
    created_at = DateFromToRangeFilter(
        field_name='created_at',
        widget=RangeWidget(
            attrs={
                'type': 'date',
                'class': 'form-control form-control-sm'
            }
        )
    )
    price = RangeFilter(
        field_name='price',
        widget=RangeWidget(
            attrs={
                'type': 'text',
                'class': 'form-control form-control-sm'
            }
        ), method="filter_by_price_range"
    )

    class Meta:
        model = Product
        fields = ['title', ]

    def filter_by_q(self, queryset, name, value):
        return queryset.filter(title__icontains=value)

    def filter_by_variant(self, queryset, name, value):
        product_varients = ProductVariant.objects.filter(variant__pk=value)
        product_ids = set([obj.product.pk for obj in product_varients])
        return queryset.filter(pk__in=product_ids)

    def filter_by_price_range(self, queryset, name, value):
        price = value
        price_min = float(value.stop)
        price_max = float(value.start)
        print('-' * 30, 'price ', price_max, price_max, type(price_min))
        product_variants = ProductVariantPrice.objects.filter(
            price__range=[price_max, price_min]
        )
        product_ids = [obj.product.pk for obj in product_variants]
        return queryset.filter(pk__in=product_ids)
