"""Checkout page with order processing"""

from nicegui import ui
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from app.core.database import get_db, CartItem, Order, OrderItem
from app.core.auth import AuthManager
from app.frontend.components.layout import create_header, create_footer

auth_manager = AuthManager()

async def checkout_page():
    """Checkout page with shipping and payment information"""
    
    if not auth_manager.is_authenticated():
        with ui.column().classes('w-full min-h-screen bg-gray-50'):
            create_header()
            with ui.column().classes('w-full max-w-4xl mx-auto px-4 py-12 text-center'):
                ui.label('Please log in to checkout').classes('text-2xl mb-4')
                ui.button('Login', on_click=lambda: ui.navigate.to('/login')).classes('bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded')
            create_footer()
        return
    
    db = next(get_db())
    cart_items = db.query(CartItem).filter(CartItem.user_id == auth_manager.current_user.id).all()
    
    if not cart_items:
        with ui.column().classes('w-full min-h-screen bg-gray-50'):
            create_header()
            with ui.column().classes('w-full max-w-4xl mx-auto px-4 py-12 text-center'):
                ui.label('Your cart is empty').classes('text-2xl mb-4')
                ui.button('Continue Shopping', on_click=lambda: ui.navigate.to('/products')).classes('bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded')
            create_footer()
        db.close()
        return
    
    # Calculate total
    total = sum(item.product.current_price * item.quantity for item in cart_items)
    
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        create_header()
        
        # Checkout Form
        with ui.row().classes('w-full max-w-6xl mx-auto px-4 py-8 gap-8'):
            # Checkout Form
            with ui.column().classes('flex-2'):
                ui.label('Checkout').classes('text-3xl font-bold mb-8')
                
                # Shipping Information
                with ui.card().classes('w-full mb-6'):
                    with ui.card_section():
                        ui.label('Shipping Information').classes('text-xl font-bold mb-4')
                        
                        with ui.row().classes('gap-4'):
                            first_name = ui.input('First Name').classes('flex-1')
                            last_name = ui.input('Last Name').classes('flex-1')
                        
                        email = ui.input('Email').classes('w-full')
                        phone = ui.input('Phone').classes('w-full')
                        address = ui.input('Address').classes('w-full')
                        
                        with ui.row().classes('gap-4'):
                            city = ui.input('City').classes('flex-1')
                            state = ui.input('State').classes('flex-1')
                            zip_code = ui.input('ZIP Code').classes('flex-1')
                
                # Payment Information
                with ui.card().classes('w-full mb-6'):
                    with ui.card_section():
                        ui.label('Payment Information').classes('text-xl font-bold mb-4')
                        
                        payment_method = ui.select(['Credit Card', 'PayPal', 'Apple Pay'], value='Credit Card').classes('w-full mb-4')
                        
                        # Credit card fields (shown conditionally)
                        card_number = ui.input('Card Number').classes('w-full')
                        
                        with ui.row().classes('gap-4'):
                            expiry = ui.input('MM/YY').classes('flex-1')
                            cvv = ui.input('CVV').classes('flex-1')
                        
                        cardholder_name = ui.input('Cardholder Name').classes('w-full')
            
            # Order Summary
            with ui.column().classes('flex-1'):
                with ui.card().classes('w-full sticky top-4'):
                    with ui.card_section():
                        ui.label('Order Summary').classes('text-xl font-bold mb-4')
                        
                        # Order items
                        for item in cart_items:
                            product = item.product
                            with ui.row().classes('w-full justify-between mb-2'):
                                with ui.column():
                                    ui.label(product.name).classes('font-semibold')
                                    ui.label(f'Qty: {item.quantity}').classes('text-sm text-gray-600')
                                ui.label(f'${product.current_price * item.quantity:.2f}')
                        
                        ui.separator().classes('my-4')
                        
                        # Totals
                        with ui.row().classes('w-full justify-between mb-2'):
                            ui.label('Subtotal:')
                            ui.label(f'${total:.2f}')
                        
                        with ui.row().classes('w-full justify-between mb-2'):
                            ui.label('Shipping:')
                            ui.label('Free').classes('text-green-600')
                        
                        with ui.row().classes('w-full justify-between mb-2'):
                            ui.label('Tax:')
                            ui.label(f'${total * 0.08:.2f}')  # 8% tax
                        
                        ui.separator().classes('my-4')
                        
                        with ui.row().classes('w-full justify-between mb-6'):
                            ui.label('Total:').classes('text-xl font-bold')
                            ui.label(f'${total * 1.08:.2f}').classes('text-xl font-bold')
                        
                        # Place order button
                        ui.button('Place Order', 
                                on_click=lambda: place_order(
                                    first_name.value, last_name.value, email.value,
                                    phone.value, address.value, city.value,
                                    state.value, zip_code.value, payment_method.value,
                                    cart_items, total * 1.08
                                )).classes('w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg')
        
        # Footer
        create_footer()
    
    db.close()

def place_order(first_name: str, last_name: str, email: str, phone: str,
                address: str, city: str, state: str, zip_code: str,
                payment_method: str, cart_items, total: float):
    """Process the order"""
    
    # Validate required fields
    if not all([first_name, last_name, email, address, city, state, zip_code]):
        ui.notify('Please fill in all required fields', type='negative')
        return
    
    try:
        db = next(get_db())
        
        # Create shipping address
        shipping_address = f"{address}, {city}, {state} {zip_code}"
        
        # Create order
        order = Order(
            user_id=auth_manager.current_user.id,
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            status="confirmed",
            total_amount=total,
            shipping_address=shipping_address,
            payment_method=payment_method,
            payment_status="paid"
        )
        
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.current_price,
                size=cart_item.size,
                color=cart_item.color
            )
            db.add(order_item)
        
        # Clear cart
        for cart_item in cart_items:
            db.delete(cart_item)
        
        db.commit()
        
        ui.notify(f'Order {order.order_number} placed successfully!', type='positive')
        ui.navigate.to('/profile')  # Redirect to profile/orders page
        
    except Exception as e:
        db.rollback()
        ui.notify('Error placing order. Please try again.', type='negative')
    finally:
        db.close()