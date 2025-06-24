"""Products listing and detail pages"""

from nicegui import ui
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.core.database import get_db, Product, Category
from app.core.assets import AssetManager
from app.frontend.components.layout import create_header, create_footer
from app.frontend.components.product_card import create_product_card

asset_manager = AssetManager()

async def products_page(category: Optional[str] = None):
    """Products listing page with filtering and search"""
    
    db = next(get_db())
    
    # Get categories for filter
    categories = db.query(Category).filter(Category.is_active == True).all()
    
    # Build query
    query = db.query(Product).filter(Product.is_active == True)
    
    # Filter by category if specified
    current_category = None
    if category:
        current_category = db.query(Category).filter(Category.slug == category).first()
        if current_category:
            query = query.filter(Product.categories.contains(current_category))
    
    products = query.all()
    
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        create_header()
        
        # Page Header
        with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-8'):
            if current_category:
                ui.label(f'{current_category.name} Collection').classes('text-4xl font-bold mb-2')
                if current_category.description:
                    ui.label(current_category.description).classes('text-lg text-gray-600')
            else:
                ui.label('All Products').classes('text-4xl font-bold mb-2')
                ui.label('Discover our complete fashion collection').classes('text-lg text-gray-600')
        
        # Filters and Search
        with ui.row().classes('w-full max-w-7xl mx-auto px-4 mb-8 gap-4'):
            # Search
            search_input = ui.input('Search products...').classes('flex-1')
            search_input.on('input', lambda: filter_products(search_input.value, products))
            
            # Category filter
            category_options = ['All'] + [cat.name for cat in categories]
            category_select = ui.select(category_options, value='All').classes('w-48')
            category_select.on('change', lambda: filter_by_category(category_select.value, categories))
            
            # Sort options
            sort_options = ['Name A-Z', 'Name Z-A', 'Price Low-High', 'Price High-Low']
            sort_select = ui.select(sort_options, value='Name A-Z').classes('w-48')
        
        # Products Grid
        with ui.column().classes('w-full max-w-7xl mx-auto px-4'):
            products_container = ui.row().classes('w-full product-gallery')
            
            # Display products
            display_products(products_container, products)
        
        # Footer
        create_footer()
    
    db.close()

def display_products(container, products):
    """Display products in the container"""
    container.clear()
    
    if not products:
        with container:
            ui.label('No products found').classes('text-center text-gray-500 w-full py-12')
        return
    
    with container:
        for product in products:
            create_product_card(product)

def filter_products(search_term: str, all_products):
    """Filter products by search term"""
    if not search_term:
        filtered = all_products
    else:
        filtered = [p for p in all_products if search_term.lower() in p.name.lower() or 
                   (p.description and search_term.lower() in p.description.lower())]
    
    # Update display (this would need to be connected to the UI)
    ui.notify(f'Found {len(filtered)} products')

def filter_by_category(category_name: str, categories):
    """Filter products by category"""
    if category_name == 'All':
        ui.navigate.to('/products')
    else:
        category = next((cat for cat in categories if cat.name == category_name), None)
        if category:
            ui.navigate.to(f'/products/{category.slug}')

async def product_detail_page(product_id: int):
    """Product detail page with images, description, and purchase options"""
    
    db = next(get_db())
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        with ui.column().classes('w-full min-h-screen bg-gray-50'):
            create_header()
            ui.label('Product not found').classes('text-center text-2xl py-12')
            create_footer()
        db.close()
        return
    
    # Get product images
    product_images = asset_manager.get_product_images(product.name, count=4)
    
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        create_header()
        
        # Product Detail
        with ui.row().classes('w-full max-w-7xl mx-auto px-4 py-8 gap-8'):
            # Product Images
            with ui.column().classes('flex-1'):
                # Main image
                main_image = ui.image(product_images[0]['primary']).classes('w-full h-96 object-cover rounded-lg mb-4')
                
                # Thumbnail images
                with ui.row().classes('gap-2'):
                    for i, img in enumerate(product_images):
                        ui.image(img['primary']).classes('w-20 h-20 object-cover rounded cursor-pointer').on('click', 
                            lambda src=img['primary']: setattr(main_image, 'source', src))
            
            # Product Info
            with ui.column().classes('flex-1 space-y-6'):
                ui.label(product.name).classes('text-3xl font-bold')
                
                # Price
                with ui.row().classes('items-center gap-4'):
                    if product.sale_price:
                        ui.label(f'${product.sale_price:.2f}').classes('text-2xl font-bold text-red-600')
                        ui.label(f'${product.price:.2f}').classes('text-lg text-gray-500 line-through')
                    else:
                        ui.label(f'${product.price:.2f}').classes('text-2xl font-bold')
                
                # Description
                if product.description:
                    ui.label(product.description).classes('text-gray-700')
                
                # Size selection
                if product.size_list:
                    ui.label('Size:').classes('font-semibold')
                    size_select = ui.select(product.size_list).classes('w-32')
                
                # Color selection
                if product.color_list:
                    ui.label('Color:').classes('font-semibold')
                    color_select = ui.select(product.color_list).classes('w-32')
                
                # Quantity
                ui.label('Quantity:').classes('font-semibold')
                quantity_input = ui.number('Quantity', value=1, min=1, max=product.stock_quantity).classes('w-24')
                
                # Stock status
                if product.stock_quantity > 0:
                    ui.label(f'{product.stock_quantity} in stock').classes('text-green-600')
                else:
                    ui.label('Out of stock').classes('text-red-600')
                
                # Add to cart button
                with ui.row().classes('gap-4 mt-6'):
                    if product.stock_quantity > 0:
                        ui.button('Add to Cart', 
                                on_click=lambda: add_to_cart(product, quantity_input.value)).classes('bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg')
                        ui.button('Buy Now', 
                                on_click=lambda: buy_now(product)).classes('bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg')
                    else:
                        ui.button('Out of Stock').classes('bg-gray-400 text-white px-8 py-3 rounded-lg').props('disabled')
        
        # Footer
        create_footer()
    
    db.close()

def add_to_cart(product: Product, quantity: int):
    """Add product to cart"""
    # This would integrate with cart management system
    ui.notify(f'Added {quantity} x {product.name} to cart!', type='positive')

def buy_now(product: Product):
    """Direct purchase"""
    ui.navigate.to('/checkout')