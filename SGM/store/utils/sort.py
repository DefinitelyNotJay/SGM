from store.models import *
from django.db.models import *


def sort_products(categories, sort_filter):
        context = {}
        products = []

        product_categories = Category.objects.all()
        if not categories and not sort_filter:
            products = Product.objects.all().order_by('quantity_in_stock')
            categories = Category.objects.all()

        # หากมีการเลือก filter หริอ category filter
        else:
            products = Product.objects.all()

            # มี sort_filter
            if sort_filter:
                if sort_filter == 'sales-asc':
                    products = Product.objects.annotate(total_sold=Sum('orderitem__amount')).order_by('total_sold')
                elif sort_filter == 'sales-desc':
                    products = Product.objects.annotate(total_sold=Sum('orderitem__amount')).order_by('-total_sold')
                elif sort_filter == 'quantity-asc':
                    products = Product.objects.order_by('quantity_in_stock')
                elif sort_filter == 'quantity-desc':
                    products = Product.objects.order_by('-quantity_in_stock')

            # มี categories
            if categories:
                products = products.filter(categories__name__in=categories)
    
        context = {'products': products, 'categories': product_categories}
        return context
