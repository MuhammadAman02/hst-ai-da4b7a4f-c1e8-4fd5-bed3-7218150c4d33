"""
Main application setup and page routing for H&M-style clothing store
"""

from nicegui import ui
from app.core.config import settings
from app.core.assets import AssetManager
from app.frontend.pages import (
    home_page,
    products_page,
    product_detail_page,
    cart_page,
    checkout_page,
    profile_page,
    admin_page
)
from app.frontend.components.layout import create_header, create_footer
from app.core.auth import AuthManager

# Initialize managers
asset_manager = AssetManager()
auth_manager = AuthManager()

def setup_application():
    """Set up the main application with all routes and components"""
    
    # Load CSS
    ui.add_head_html(f'<link rel="stylesheet" href="/static/css/main.css">')
    ui.add_head_html('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">')
    ui.add_head_html('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">')
    
    # Home page
    @ui.page('/')
    async def index():
        await home_page()
    
    # Products pages
    @ui.page('/products')
    async def products():
        await products_page()
    
    @ui.page('/products/{category}')
    async def products_by_category(category: str):
        await products_page(category=category)
    
    @ui.page('/product/{product_id}')
    async def product_detail(product_id: int):
        await product_detail_page(product_id)
    
    # Shopping cart and checkout
    @ui.page('/cart')
    async def cart():
        await cart_page()
    
    @ui.page('/checkout')
    async def checkout():
        await checkout_page()
    
    # User pages
    @ui.page('/profile')
    async def profile():
        await profile_page()
    
    # Admin pages
    @ui.page('/admin')
    async def admin():
        await admin_page()
    
    # Static file serving
    ui.add_static_files('/static', 'app/static')