import random
import string

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

def rand_slug():
    """
    Generate a random 3-character slug.
    
    Generates a random string of 3 characters consisting of lowercase letters
    and digits. Used as a prefix to ensure uniqueness in auto-generated slugs.
    
    Returns:
        str: A random 3-character string (e.g., 'a1b', '9cd', 'xyz').
    
    Example:
        >>> slug = rand_slug()
        >>> len(slug)
        3
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))


class Category(models.Model):
    """
    Represents a product category with hierarchical structure.
    
    Supports nested categories through self-referencing parent field, allowing
    creation of category trees (e.g., Electronics > Computers > Laptops).
    
    Attributes:
        name (str): Category name (up to 250 characters), indexed for faster lookups.
        parent (ForeignKey): Reference to parent category for hierarchical structure (optional).
        slug (str): URL-friendly identifier (up to 250 characters), unique per parent.
        created_at (datetime): Automatic timestamp when category is created.
    
    Meta:
        unique_together: Ensures slug is unique within each parent (different parents can share same slug).
        verbose_name: 'Категория'
        verbose_name_plural: 'Категории'
    """
    name = models.CharField("Категория", max_length=250, db_index=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='Родительская категория',
        blank=True,
        null=True,
        related_name='children',
        on_delete=models.CASCADE
    )
    slug = models.SlugField('URL', max_length=250, unique=True, null=False, editable=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        unique_together = ('slug', 'parent',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        
    def __str__(self):
        """
        Return the full hierarchical path of the category.
        
        Displays the complete category chain from root to current category
        separated by ' -> ' (e.g., 'Electronics -> Computers -> Laptops').
        
        This method traverses up the parent chain to build the complete path,
        then reverses it to show the hierarchy from top-level to current.
        
        Returns:
            str: Hierarchical category path with parents in correct order.
            
        Example:
            If category 'Laptops' has parent 'Computers' which has parent 'Electronics':
            str(laptops_category) returns: 'Electronics -> Computers -> Laptops'
        """
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])
        
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug if not provided.
        
        If slug is empty, generates a unique slug by combining:
        - A random 3-character prefix (lowercase letters and digits)
        - The literal string 'pickBetter'
        - The category name
        
        Then slugifies the result to ensure it's URL-friendly.
        
        Example:
            If name='Electronics' and rand_slug()='a7x':
            slug becomes: 'a7x-pickbetter-electronics'
        
        Args:
            *args: Positional arguments passed to parent save method.
            **kwargs: Keyword arguments passed to parent save method.
        """
        if not self.slug:
            self.slug = slugify(rand_slug() + '-pickBetter' +self.name)
        super(Category, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("shop:category-list", args=[str(self.slug)])
    
    
class Product(models.Model):
        """
        Represents a product in the e-commerce system.
        
        
        """
        
        category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
        title = models.CharField('Название', max_length=250)
        brand = models.CharField('Бренд', max_length=250)
        description = models.TextField('Описание', blank=True)
        slug = models.SlugField('URL', max_length=250,)
        price = models.DecimalField('Цена', max_digits=7, decimal_places=2, default=99.99)
        image = models.ImageField('Изображение', upload_to='products/%Y/%m/%d', )
        available = models.BooleanField('В наличии', default=True)
        created_at = models.DateTimeField('Дата создания', auto_now_add=True)
        updated_at = models.DateTimeField('Дата изменения', auto_now=True)
        
        class Meta:
            verbose_name = 'Продукт'
            verbose_name_plural = 'Продукты'
            
        def __str__(self):
            return self.title
        
        def get_absolute_url(self):
            return reverse("shop:product-detail", args=[str(self.slug)])



class ProductManager(models.Manager):
    def get_queryset(self):
        """
        Returns a queryset of products that are available.
        
        Returns:
            QuerySet: A queryset of  products that are available.
        """
        
        return super(ProductManager, self).get_queryset().filter(available=True)


class ProductProxy(Product):
    
    objects = ProductManager()

    class Meta:
        proxy = True