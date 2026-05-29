from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.views.generic import ListView

from .models import Category, ProductProxy


class ProductListView(ListView):
    model = ProductProxy
    template_name = 'shop/products.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = ['title']


def search_products(request):
    query = request.GET.get('q') or request.GET.get('query')
    products = ProductProxy.objects.none()
    if query:
        products = ProductProxy.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query)
        )
    context = {'products': products, 'query': query}
    return render(request, 'shop/products.html', context)

def products_view(request):
    products = ProductProxy.objects.all()
    return render(request, 'shop/products.html', {'products': products})

def products_detail_view(request, slug):
    product = get_object_or_404(ProductProxy, slug=slug)
    return render(request, 'shop/product_detail.html', {'product': product})

def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = ProductProxy.objects.select_related('category').filter(category=category)
    context = {'category': category, 'products': products}
    return render(request, 'shop/category_list.html', context)