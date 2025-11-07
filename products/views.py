import re
import time
from django.views.generic import TemplateView
from django.db.models import Count, Q, Avg, Max, Subquery, F
from django.contrib.postgres.search import TrigramWordSimilarity
from django.db.models.functions import Least
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import JsonResponse
from .models import Category, Tag, Product

class IndexView(TemplateView):
    """
    Index page: /
    """
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        description = self.request.GET.get('description', '')

        # Handle case when category is not a number
        # category is an id instead of name because the database
        # automatically index primary keys -> faster search runtime
        category = 0
        try:
            category = int(self.request.GET.get('category', 0))
        except ValueError:
            category = 0

        # Handle case when a tag is not a number
        # tags are ids instead of names because the database
        # automatically index primary keys -> faster search runtime
        tags = self.request.GET.getlist('tags', [])
        processed_tags = []
        for tag in tags:
            try:
                processed_tags.append(int(tag))
            except ValueError:
                continue
        tags = processed_tags
        
        # Handle case when page is not a number
        page = self.request.GET.get('page', 1)
        try:
            page = int(page)
        except ValueError:
            page = 1

        # Start time counter
        start = time.perf_counter()

        # Initial query
        # Using prefetch_related and select_related to avoid extra database queries on
        # when accessing tag and category's fields later on
        query = Product.objects.prefetch_related('tag').select_related('category')

        # Filters applied
        if description or category or tags:
            if description:
                searched_phrases = re.split(r'\W+', description)
                similarity_query = None

                # Length of search_phrases cannot be 0
                if len(searched_phrases) == 1:
                    similarity_query = TrigramWordSimilarity(searched_phrases[0], "description")
                else:
                    similarity_query = Least(*(TrigramWordSimilarity(phrase, "description") for phrase in searched_phrases))

                query = query.annotate(
                    similarity=similarity_query
                ).filter(
                    similarity__gt=0.3
                ).order_by("-similarity")
                
                # Uncomment this block of code for substring exact search
                # combined_query = Q()
                # for phrase in searched_phrases:
                #     combined_query &= Q(description__icontains=phrase)
                
                # query = query.filter(combined_query)

            if category:
                query = query.filter(category__id=category)

            # Assuming getting all products that have all searched tags
            if tags:
                # Using .annotate to run the queries within the database instead of Python
                # for better resource usage and faster code execution
                query = (
                    query.filter(tag__id__in=tags)
                    .annotate(num_tags=Count("tag", filter=Q(tag__id__in=tags), distinct=True))
                    .filter(num_tags=len(tags))
                )

        # End time counter
        end = time.perf_counter()

        # Context variables used for template
        paginator = Paginator(query, 25)
        context["paginator"] = paginator
        context["product_page"] = paginator.get_page(page)
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()

        context["searched_description"] = description
        context["searched_category"] = category
        context["searched_tags"] = tags

        context["query_execution_time"] = end - start
        return context

def products_under_ten_dollar(request):
    products = Product.objects.select_related("category").prefetch_related("tag")
    products = products.filter(price__lt=10).order_by("price")
    return JsonResponse({
        "products": [product.serialize() for product in products]
    })
    
def products_with_espresso_in_name(request):
    products = Product.objects.select_related("category").prefetch_related("tag")
    products = products.filter(name__icontains="espresso")
    return JsonResponse({
        "products": [product.serialize() for product in products]
    })
    
def products_with_no_category(request):
    products = Product.objects.select_related("category").prefetch_related("tag")
    products = products.filter(category__isnull=True)
    return JsonResponse({
        "products": [product.serialize() for product in products]
    })
    
def products_with_tea_category(request):
    products = Product.objects.select_related("category").prefetch_related("tag")
    products = products.filter(category__name__iexact="tea")
    return JsonResponse({
        "products": [product.serialize() for product in products]
    })

def products_with_caffeinated_tag(request):
    products = Product.objects.select_related("category").prefetch_related("tag")
    products = products.filter(tag__name="caffeinated")
    return JsonResponse({
        "products": [product.serialize() for product in products]
    })

def tags_with_at_least_one_product(request):
    tags = Tag.objects.filter(product__isnull=False).distinct()
    return JsonResponse({
        "tags": [tag.serialize() for tag in tags]
    })
    
def milky_tag_related_products(request):
    (tag, _created) = Tag.objects.get_or_create(name="milky")
    products = tag.product_set.all().prefetch_related("tag")
    return JsonResponse({
        "products": [product.serialize() for product in products]
    })

def categories_with_product_num(request):
    categories = Category.objects.annotate(
        product_num=Count('product')
    ).order_by("-product_num")
    return JsonResponse({
        "categories": [{
            "name": cat.name,
            "product_num": cat.product_num    
        } for cat in categories]
    })

def product_avg_price(request):
    avg_price = Product.objects.aggregate(
        Avg("price", default=0)
    )["price__avg"]
    return JsonResponse({
        "Avg price": avg_price
    })

def tags_with_avg_price_gt_five(request):
    tags = Tag.objects.annotate(
        avg_product_price=Avg('product__price', default=0)
    ).filter(avg_product_price__gt=5)
    
    return JsonResponse({
        "tags": [
            {
                "name": tag.name,
                "avg_price": float(tag.avg_product_price)
            } for tag in tags
        ]
    })
    
def most_expensive_product_per_category(request):
    categories = Category.objects.annotate(
        max_price=Max('product__price', default=0)
    ).values_list("id", "max_price")
    
    return JsonResponse({
        "categories": list(categories)
    })
    
def products_with_tag_count(request):
    products = Product.objects.annotate(
        tag_count=Count("tag", distinct=True)
    ).order_by("-tag_count")
    return JsonResponse({
        "products": [
            {
                "name": product.name,
                "tag_count": product.tag_count
            } for product in products
        ]
    })
    
def products_with_tag_names(request):
    tags = ["hot", "contains-dairy"]
    products = Product.objects.annotate(
        matched_tag_count=Count('tag', filter=Q(tag__name__in=tags), distinct=True)
    ).filter(matched_tag_count=len(tags)).prefetch_related("tag")

    return JsonResponse({
        "products": [
            {
                "name": product.name,
                "tags": [tag.name for tag in product.tag.all()]
            } for product in products
        ]
    })

def products_with_at_least_one_of_tags(request):
    tags = ["cold", "something"]
    products = Product.objects.filter(tag__name__in=tags).prefetch_related("tag").distinct()
    
    return JsonResponse({
        "products": [
            {
                "name": product.name,
                "tags": [tag.name for tag in product.tag.all()]
            } for product in products
        ]
    })
    
def products_with_none_of_tags(request):
    tags = ["cold", "hot"]
    # products = Product.objects.filter(
    #     ~Q(tag__name__in=tags)
    # ).prefetch_related("tag").distinct()
    
    products = Product.objects.exclude(tag__name__in=tags).prefetch_related("tag").distinct()
    
    return JsonResponse({
        "products": [
            {
                "name": product.name,
                "tags": [tag.name for tag in product.tag.all()]
            } for product in products
        ]
    })
    
def distinct_categories_over_products_span(request):
    tags = Tag.objects.annotate(
        cat_num=Count("product__category__name", distinct=True)
    ).distinct()
    
    return JsonResponse({
        "tags": [
            {
                "name": tag.name,
                "cat_num": tag.cat_num
            } for tag in tags
        ]
    })

def case_insensitive_latte_search(request):
    products = Product.objects.select_related("category").prefetch_related("tag")
    products = products.filter(Q(name__icontains="latte") | Q(description__icontains="latte"))
    return JsonResponse({
        "products": [product.serialize() for product in products] if products else []
    })

def products_above_average_price(request):
    avg_price = Product.objects.aggregate(avg_price=Avg("price", default=0))["avg_price"]
    products = Product.objects.filter(price__gt=avg_price)
    
    return JsonResponse({
        "products": [product.serialize() for product in products] if products else []
    })

def products_in_categories_starting_with_c(request):
    products = Product.objects.filter(category__name__istartswith="c")
    return JsonResponse({
        "products": [product.serialize() for product in products] if products else []
    })

def discount_clearance_products(request):
    products = Product.objects.filter(category__name="Coffee").update(price=F("price") * 0.9)

    updated_count = 0
    return JsonResponse({
        "updated_count": updated_count,
        "message": f"Applied 10% discount to {updated_count} products in Clearance category"
    })

def delete_unused_tags(request):
    deleted_count = 0
    return JsonResponse({
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} unused tags"
    })