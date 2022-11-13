from django.db.models import Q  # noqa
from django_filters import (  # noqa
    FilterSet, OrderingFilter, CharFilter, filters,
    ModelChoiceFilter, ChoiceFilter, DateFilter, DateRangeFilter,  # noqa
    DateFromToRangeFilter, RangeFilter
)
from django_filters.widgets import RangeWidget
from django.forms import (  # noqa
    forms, ModelForm, CharField, TextInput, Textarea, BooleanField,  # noqa
    CheckboxInput  # noqa
)
from django.forms.models import modelformset_factory
from product.models import (  # noqa
    Variant, Product, ProductVariant, ProductVariantPrice, ProductImage
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
    ProductVariant, form=ProductVariantForm, extra=0, can_delete=True,
    min_num=1, max_num=20
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
                'class': 'form-control'
            }
        )
    )
    price = RangeFilter(
        field_name='price',
        widget=RangeWidget(
            attrs={
                'type': 'text',
                'class': 'form-control'
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
        price_min = float(value.stop)
        price_max = float(value.start)
        product_variants = ProductVariant.objects.filter(
            price__range=[price_max, price_min]
        )
        product_ids = [obj.product.pk for obj in product_variants]
        return queryset.filter(pk__in=product_ids)


class ProductImageForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = ('thumbnail', )
        labels = {
           'thumbnail': '',
        }


ProductImageFormFormSet = modelformset_factory(
    ProductImage, form=ProductImageForm, extra=1, can_delete=True, max_num=10
)
