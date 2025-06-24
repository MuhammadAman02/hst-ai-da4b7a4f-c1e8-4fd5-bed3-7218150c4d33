"""Homepage with hero section, featured products, and categories"""

from nicegui import ui
from sqlalchemy.orm import Session
from app.core.database import get_db, Product, Category
from app.core.assets import AssetManager
from app.frontend.components.layout import create_header, create_footer
from app.frontend.components.product_card import create_product_card

asset_manager = AssetManager()

async def home_page():
    """Create the homepage with hero section and featured products"""
    
    # Get database session
    db = next(get_db())
    
    # Get featured products and categories
    featured_products = db.query(Product).filter(Product.is_featured == True).limit(8).all()
    categories = db.query(Category).filter(Category.is_active == True).limit(6).all()
    
    # Get hero images
    hero_images = asset_manager.get_hero_images(3)
    
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        create_header()
        
        # Hero Section
        with ui.row().classes('w-full'):
            with ui.carousel(animated=True, arrows=True, navigation=True).classes('w-full h-96 rounded-lg shadow-lg'):
                for i, hero_img in enumerate(hero_images):
                    with ui.carousel_slide(name=str(i)):
                        with ui.card().classes('w-full h-full relative overflow-hidden'):
                            ui.image(hero_img['primary']).classes('w-full h-full object-cover')
                            with ui.column().classes('absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center text-white text-center'):
                                ui.label('Discover Your Style').classes('text-4xl font-bold mb-4')
                                ui.label('Fashion that speaks to you').classes('text-xl mb-6')
                                ui.button('Shop Now', on_click=lambda: ui.navigate.to('/products')).classes('bg-white text-black px-8 py-3 rounded-lg font-semibold hover:bg-gray-100')
        
        # Categories Section
        with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-12'):
            ui.label('Shop by Category').classes('text-3xl font-bold text-center mb-8')
            
            with ui.row().classes('w-full grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6'):
                for category in categories:
                    category_img = asset_manager.get_category_image(category.name)
                    
                    with ui.card().classes('cursor-pointer hover:shadow-lg transition-all duration-300').on('click', lambda cat=category: ui.navigate.to(f'/products/{cat.slug}')):
                        ui.image(category_img['primary']).classes('w-full h-32 object-cover category-image')
                        with ui.card_section():
                            ui.label(category.name).classes('text-center font-semibold')
        
        # Featured Products Section
        if featured_products:
            with ui.column().classes('w-full max-w-7xl mx-auto px-4 py-12'):
                ui.label('Featured Products').classes('text-3xl font-bold text-center mb-8')
                
                with ui.row().classes('w-full product-gallery'):
                    for product in featured_products:
                        create_product_card(product)
        
        # Newsletter Section
        with ui.column().classes('w-full bg-gray-900 text-white py-16'):
            with ui.column().classes('max-w-4xl mx-auto text-center px-4'):
                ui.label('Stay in Style').classes('text-3xl font-bold mb-4')
                ui.label('Subscribe to our newsletter for the latest fashion trends and exclusive offers').classes('text-lg mb-8')
                
                with ui.row().classes('w-full max-w-md mx-auto gap-4'):
                    email_input = ui.input('Enter your email').classes('flex-1')
                    ui.button('Subscribe', on_click=lambda: subscribe_newsletter(email_input.value)).classes('bg-blue-600 hover:bg-blue-700 px-6 py-2')
        
        # Footer
        create_footer()
    
    db.close()

def subscribe_newsletter(email: str):
    """Handle newsletter subscription"""
    if email:
        ui.notify(f'Thank you for subscribing with {email}!', type='positive')
    else:
        ui.notify('Please enter a valid email address', type='negative')