from django.utils import timezone
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
)
from django.db import IntegrityError, transaction
from product.models import Variant, Product, ProductVariant, ProductImage
from product.forms import (
    ProductFilterSet, ProductForm, VariantForm, ProductVariantForm,
    ProductVariantFormFormSet, ProductImageFormFormSet
)
from django.shortcuts import redirect


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


class ProductCreateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.CreateView
):
    """ Copyright first part create view """
    model = Product
    paginate_by = 10
    template_name = 'products/create.html'
    permission_required = "product.add_product"
    success_message = "Product has been created successfully"
    form_class = ProductForm

    def test_func(self):
        return self.request.user.is_active

    def get_success_url(self):
        messages.success(
            self.request, self.success_message
        )
        return redirect("product:list.product")

    def get_context_data(self, **kwargs):
        ''' *** return all form errors '''
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            for key in list(context.keys()):
                if hasattr(context[key], 'errors'):
                    print(f'{key} form error is {context[key].errors}\n\n')
        return context

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        variant_formset = ProductVariantFormFormSet(
            queryset=ProductVariant.objects.none()
        )
        image_formset = ProductImageFormFormSet(
            queryset=ProductImage.objects.none(),
            prefix="product_image"
        )
        return self.render_to_response(
            self.get_context_data(
                form=form, variant_formset=variant_formset,
                image_formset=image_formset
            )
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        variant_formset = ProductVariantFormFormSet(request.POST)
        image_formset = ProductImageFormFormSet(
            request.POST, request.FILES,
            queryset=ProductImage.objects.none()
        )

        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():  # noqa
            return self.form_valid(
                form, variant_formset, image_formset
            )
        else:
            return self.form_invalid(
                form, variant_formset, image_formset
            )

    def form_valid(self, form, variant_formset, image_formset):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        # variant formset
        variant_forms = variant_formset.save(commit=False)
        for variant_form in variant_forms:
            if variant_form != {}:
                variant_form.product = self.object
                variant_form.save()

        # image formset
        images_forms = image_formset.save(commit=False)
        for image_form in images_forms:
            if image_form != {}:
                image_form.product = self.object
                image_form.save()

        return self.get_success_url()

    def form_invalid(self, form, variant_formset, image_formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(
                form=form,
                variant_formset=variant_formset,
                image_formset=image_formset
            )
        )


class ProductUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView
):
    """ Copyright first part create view """
    model = Product
    paginate_by = 10
    template_name = 'products/create.html'
    permission_required = "product.add_product"
    success_message = "Product was updated successfully"
    form_class = ProductForm

    def test_func(self):
        return self.request.user.is_active

    def get_success_url(self):
        messages.success(
            self.request, self.success_message
        )
        return redirect("product:list.product")

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        variant_formset = ProductVariantFormFormSet(
            queryset=ProductVariant.objects.filter(product=self.object)
        )
        image_formset = ProductImageFormFormSet(
            queryset=ProductImage.objects.filter(product=self.object),
            prefix="product_image"
        )
        return self.render_to_response(
            self.get_context_data(
                form=form, variant_formset=variant_formset,
                image_formset=image_formset
            )
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        variant_formset = ProductVariantFormFormSet(
            self.request.POST,
            queryset=ProductVariant.objects.filter(product=self.object)
        )
        image_formset = ProductImageFormFormSet(
            request.POST, request.FILES,
            queryset=ProductImage.objects.filter(product=self.object),
            prefix="product_image"
        )

        if form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():  # noqa
            return self.form_valid(
                form, variant_formset, image_formset
            )
        else:
            return self.form_invalid(
                form, variant_formset, image_formset
            )

    def form_valid(self, form, variant_formset, image_formset):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        # partners formset
        variant_forms = variant_formset.save(commit=False)
        for variant_form in variant_forms:
            if variant_form != {}:
                variant_form.product = self.object
                variant_form.save()

        # image formset
        images_forms = image_formset.save(commit=False)
        for image_form in images_forms:
            if image_form != {}:
                image_form.product = self.object
                image_form.save()

        return self.get_success_url()

    def form_invalid(self, form, variant_formset, image_formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(
                form=form,
                variant_formset=variant_formset,
                image_formset=image_formset
            )
        )
