"""Shopping cart page"""

from nicegui import ui
from sqlalchemy.orm import Session
from app.core.database import get_db, CartItem, Product
from app.core.auth import AuthManager
from app.frontend.components.layout import create_header, create_footer

auth_manager = AuthManager()

async def cart_page():
    """Shopping cart page with items and checkout"""
    
    if not auth_manager.is_authenticated():
        with ui.column().classes('w-full min-h-screen bg-gray-50'):
            create_header()
            with ui.column().classes('w-full max-w-4xl mx-auto px-4 py-12 text-center'):
                ui.label('Please log in to view your cart').classes('text-2xl mb-4')
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).classes('bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded')
            create_footer()
        return
    
    db = next(get_db())
    
    # Get cart items for current user
    cart_items = db.query(CartItem).filter(CartItem.user_id == auth_manager.current_user.id).all()
    
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        create_header()
        
        # Cart Content
        with ui.column().classes('w-full max-w-4xl mx-auto px-4 py-8'):
            ui.label('Shopping Cart').classes('text-3xl font-bold mb-8')
            
            if not cart_items:
                # Empty cart
                with ui.column().classes('text-center py-12'):
                    ui.label('Your cart is empty').classes('text-xl text-gray-500 mb-4')
                    ui.button('Continue Shopping', on_click=lambda: ui.navigate.to('/products')).classes('bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded')
            else:
                # Cart items
                total = 0
                
                for item in cart_items:
                    product = item.product
                    item_total = product.current_price * item.quantity
                    total += item_total
                    
                    with ui.card().classes('w-full mb-4'):
                        with ui.row().classes('w-full items-center gap-4 p-4'):
                            # Product image placeholder
                            ui.image('https://via.placeholder.com/100x100/f0f0f0/666666?text=Product').classes('w-24 h-24 object-cover rounded')
                            
                            # Product info
                            with ui.column().classes('flex-1'):
                                ui.label(product.name).classes('font-semibold text-lg')
                                if item.size:
                                    ui.label(f'Size: {item.size}').classes('text-gray-600')
                                if item.color:
                                    ui.label(f'Color: {item.color}').classes('text-gray-600')
                                ui.label(f'${product.current_price:.2f}').classes('font-semibold')
                            
                            # Quantity controls
                            with ui.row().classes('items-center gap-2'):
                                ui.button('-', on_click=lambda i=item: update_quantity(i, -1)).classes('w-8 h-8 rounded-full')
                                ui.label(str(item.quantity)).classes('mx-2 font-semibold')
                                ui.button('+', on_click=lambda i=item: update_quantity(i, 1)).classes('w-8 h-8 rounded-full')
                            
                            # Item total and remove
                            with ui.column().classes('text-right'):
                                ui.label(f'${item_total:.2f}').classes('font-semibold text-lg')
                                ui.button('Remove', on_click=lambda i=item: remove_item(i)).classes('text-red-600 hover:text-red-800')
                
                # Cart summary
                with ui.card().classes('w-full mt-8'):
                    with ui.card_section():
                        ui.label('Order Summary').classes('text-xl font-bold mb-4')
                        
                        with ui.row().classes('w-full justify-between mb-2'):
                            ui.label('Subtotal:')
                            ui.label(f'${total:.2f}').classes('font-semibold')
                        
                        with ui.row().classes('w-full justify-between mb-2'):
                            ui.label('Shipping:')
                            ui.label('Free').classes('font-semibold text-green-600')
                        
                        ui.separator()
                        
                        with ui.row().classes('w-full justify-between mt-4'):
                            ui.label('Total:').classes('text-xl font-bold')
                            ui.label(f'${total:.2f}').classes('text-xl font-bold')
                        
                        ui.button('Proceed to Checkout', 
                                on_click=lambda: ui.navigate.to('/checkout')).classes('w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg mt-4')
        
        # Footer
        create_footer()
    
    db.close()

def update_quantity(item: CartItem, change: int):
    """Update item quantity in cart"""
    new_quantity = item.quantity + change
    if new_quantity <= 0:
        remove_item(item)
    else:
        # Update in database
        db = next(get_db())
        db.query(CartItem).filter(CartItem.id == item.id).update({'quantity': new_quantity})
        db.commit()
        db.close()
        ui.notify('Cart updated', type='positive')
        # Refresh page
        ui.navigate.to('/cart')

def remove_item(item: CartItem):
    """Remove item from cart"""
    db = next(get_db())
    db.delete(item)
    db.commit()
    db.close()
    ui.notify('Item removed from cart', type='positive')
    # Refresh page
    ui.navigate.to('/cart')