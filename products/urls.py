from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("products_under_ten_dollar", views.products_under_ten_dollar, name="products_under_ten_dollar"),
    path("products_with_espresso_in_name", views.products_with_espresso_in_name, name="products_with_espresso_in_name"),
    path("products_with_no_category", views.products_with_no_category, name="products_with_no_category"),
    path("products_with_tea_category", views.products_with_tea_category, name="products_with_tea_category"),
    path("products_with_caffeinated_tag", views.products_with_caffeinated_tag, name="products_with_caffeinated_tag"),
    path("tags_with_at_least_one_product", views.tags_with_at_least_one_product, name="tags_with_at_least_one_product"),
    path("milky_tag_related_products", views.milky_tag_related_products, name="milky_tag_related_products"),
    path("categories_with_product_num", views.categories_with_product_num, name="categories_with_product_num"),
    path("product_avg_price", views.product_avg_price, name="product_avg_price"),
    path("tags_with_avg_price_gt_five", views.tags_with_avg_price_gt_five, name="tags_with_avg_price_gt_five"),
    path("most_expensive_product_per_category", views.most_expensive_product_per_category, name="most_expensive_product_per_category"),
    path("products_with_tag_count", views.products_with_tag_count, name="products_with_tag_count"),
    path("products_with_tag_names", views.products_with_tag_names, name="products_with_tag_names"),
    path("products_with_at_least_one_of_tags", views.products_with_at_least_one_of_tags, name="products_with_at_least_one_of_tags"),
    path("products_with_none_of_tags", views.products_with_none_of_tags, name="products_with_none_of_tags"),
    path("distinct_categories_over_products_span", views.distinct_categories_over_products_span, name="distinct_categories_over_products_span"),
    path("case_insensitive_latte_search", views.case_insensitive_latte_search, name="case_insensitive_latte_search"),
    path("products_above_average_price", views.products_above_average_price, name="products_above_average_price"),
    path("products_in_categories_starting_with_c", views.products_in_categories_starting_with_c, name="products_in_categories_starting_with_c"),
    path("discount_clearance_products", views.discount_clearance_products, name="discount_clearance_products"),
    path("delete_unused_tags", views.delete_unused_tags, name="delete_unused_tags")
]
