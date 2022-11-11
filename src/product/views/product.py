from django.views import generic
from django.contrib.auth.mixins import (
    UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
)
from product.models import Variant, Product
from product.forms import ProductFilterSet


class ProductListView(
    LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin,
    generic.ListView
):
    model = Product
    paginate_by = 10
    filterset_class = ProductFilterSet
    template_name = 'products/list.html'
    permission_required = "product.view_product"

    def test_func(self):
        """Tests if the user is active"""
        return self.request.user.is_active

    def get_queryset(self):
        queryset = self.model.objects.all().order_by('-created_at')
        self.filterset = self.filterset_class(
            self.request.GET, queryset=queryset
        )
        return self.filterset.qs

    def get_context_data(self, *, object_list=None, **kwargs):
        """Override get_context_data to include forms"""
        kwargs['filter_form'] = self.filterset.form
        return super().get_context_data(**kwargs)


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
