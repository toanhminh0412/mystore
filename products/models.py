from django.db import models

# NOTES:
# - null=False, blank=False are by default but I want to be specific
class Category(models.Model):
    """
    Product categories
    Assuming one product falls into one category only
    """
    name = models.CharField(max_length=200, null=False, blank=False)

    def __repr__(self) -> str:
        return str(self.name)

    def __str__(self) -> str:
        return repr(self)

class Tag(models.Model):
    """
    Product tags
    Assuming one product can have multiple tags and one tag
    can belong to multiple products
    """
    name = models.CharField(max_length=200, null=False, blank=False)

    def __repr__(self) -> str:
        return str(self.name)

    def __str__(self) -> str:
        return repr(self)
    
    def serialize(self):
        return {
            "name": self.name,
            # "products": [product.name for product in self.product_set.all()]
        }

class Product(models.Model):
    """
    Individual products
    """
    # NOTES:
    # - Products should include images but exempted here as it's not mentioned
    # in the assignment description
    name = models.CharField(max_length=200, null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag)

    def __repr__(self) -> str:
        return str(self.name)

    def __str__(self) -> str:
        return repr(self)

    def render_tags(self) -> str:
        """
        Return tags as comma-separated list string
        Used in HTML and print statements
        """
        return ', '.join(self.tag.values_list('name', flat=True))
    
    def serialize(self):
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "category": self.category.name,
            "tags": [tag.name for tag in self.tag.all()]
        }
