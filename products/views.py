import re
import time
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.contrib.postgres.search import TrigramWordSimilarity
from django.db.models.functions import Least
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
        context["products"] = query
        context["categories"] = Category.objects.all()
        context["tags"] = Tag.objects.all()

        context["searched_description"] = description
        context["searched_category"] = category
        context["searched_tags"] = tags

        context["query_execution_time"] = end - start
        return context
