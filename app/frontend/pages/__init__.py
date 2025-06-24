"""Page definitions for the e-commerce store"""

from .home import home_page
from .products import products_page, product_detail_page
from .cart import cart_page
from .checkout import checkout_page
from .profile import profile_page
from .admin import admin_page

__all__ = [
    "home_page",
    "products_page", 
    "product_detail_page",
    "cart_page",
    "checkout_page", 
    "profile_page",
    "admin_page"
]