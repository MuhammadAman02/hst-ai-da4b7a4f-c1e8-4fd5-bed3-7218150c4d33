"""User profile and order history page"""

from nicegui import ui
from sqlalchemy.orm import Session
from app.core.database import get_db, Order, User
from app.core.auth import AuthManager
from app.frontend.components.layout import create_header, create_footer

auth_manager = AuthManager()

async def profile_page():
    """User profile page with order history"""
    
    if not auth_manager.is_authenticated():
        with ui.column().classes('w-full min-h-screen bg-gray-50'):
            create_header()
            with ui.column().classes('w-full max-w-4xl mx-auto px-4 py-12 text-center'):
                ui.label('Please log in to view your profile').classes('text-2xl mb-4')
                ui.button('Login', on_click=lambda: show_login_dialog()).classes('bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded')
            create_footer()
        return
    
    db = next(get_db())
    user = auth_manager.current_user
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        create_header()
        
        # Profile Content
        with ui.row().classes('w-full max-w-6xl mx-auto px-4 py-8 gap-8'):
            # Sidebar
            with ui.column().classes('w-64'):
                with ui.card().classes('w-full'):
                    with ui.card_section():
                        ui.label('My Account').classes('text-xl font-bold mb-4')
                        
                        with ui.column().classes('space-y-2'):
                            ui.button('Profile', on_click=lambda: show_profile_tab()).classes('w-full text-left justify-start')
                            ui.button('Orders', on_click=lambda: show_orders_tab()).classes('w-full text-left justify-start')
                            ui.button('Addresses', on_click=lambda: show_addresses_tab()).classes('w-full text-left justify-start')
                            ui.button('Logout', on_click=lambda: logout()).classes('w-full text-left justify-start text-red-600')
            
            # Main Content
            with ui.column().classes('flex-1'):
                # Profile Information
                profile_container = ui.column().classes('w-full')
                
                with profile_container:
                    ui.label('Profile Information').classes('text-3xl font-bold mb-6')
                    
                    with ui.card().classes('w-full'):
                        with ui.card_section():
                            with ui.row().classes('gap-4 mb-4'):
                                username_input = ui.input('Username', value=user.username).classes('flex-1')
                                email_input = ui.input('Email', value=user.email).classes('flex-1')
                            
                            full_name_input = ui.input('Full Name', value=user.full_name or '').classes('w-full mb-4')
                            
                            ui.button('Update Profile', 
                                    on_click=lambda: update_profile(username_input.value, email_input.value, full_name_input.value)).classes('bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded')
                
                # Order History
                orders_container = ui.column().classes('w-full')
                
                with orders_container:
                    ui.label('Order History').classes('text-3xl font-bold mb-6')
                    
                    if not orders:
                        ui.label('No orders found').classes('text-gray-500 text-center py-8')
                    else:
                        for order in orders:
                            with ui.card().classes('w-full mb-4'):
                                with ui.card_section():
                                    with ui.row().classes('w-full justify-between items-start'):
                                        with ui.column():
                                            ui.label(f'Order #{order.order_number}').classes('font-bold text-lg')
                                            ui.label(f'Date: {order.created_at.strftime("%B %d, %Y")}').classes('text-gray-600')
                                            ui.label(f'Status: {order.status.title()}').classes('text-green-600 font-semibold')
                                        
                                        with ui.column().classes('text-right'):
                                            ui.label(f'${order.total_amount:.2f}').classes('font-bold text-lg')
                                            ui.button('View Details', 
                                                    on_click=lambda o=order: show_order_details(o)).classes('text-blue-600 hover:text-blue-800')
                                    
                                    # Order items summary
                                    if order.order_items:
                                        ui.label(f'{len(order.order_items)} items').classes('text-gray-600 mt-2')
        
        # Footer
        create_footer()
    
    db.close()

def show_login_dialog():
    """Show login dialog"""
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Login').classes('text-xl font-bold mb-4')
        
        username_input = ui.input('Username').classes('w-full mb-4')
        password_input = ui.input('Password', password=True).classes('w-full mb-4')
        
        with ui.row().classes('w-full justify-end gap-2'):
            ui.button('Cancel', on_click=dialog.close).classes('text-gray-600')
            ui.button('Login', on_click=lambda: login(username_input.value, password_input.value, dialog)).classes('bg-blue-600 hover:bg-blue-700 text-white')
    
    dialog.open()

def login(username: str, password: str, dialog):
    """Handle login"""
    if username == "demo" and password == "password":
        # Create demo user
        from app.core.database import User
        demo_user = User(
            id=1,
            username="demo",
            email="demo@example.com",
            full_name="Demo User",
            hashed_password="hashed_password",
            is_active=True
        )
        auth_manager.login(demo_user)
        dialog.close()
        ui.notify('Logged in successfully!', type='positive')
        ui.navigate.to('/profile')
    else:
        ui.notify('Invalid credentials', type='negative')

def logout():
    """Handle logout"""
    auth_manager.logout()
    ui.notify('Logged out successfully', type='positive')
    ui.navigate.to('/')

def update_profile(username: str, email: str, full_name: str):
    """Update user profile"""
    # This would update the database
    ui.notify('Profile updated successfully!', type='positive')

def show_profile_tab():
    """Show profile tab"""
    pass

def show_orders_tab():
    """Show orders tab"""
    pass

def show_addresses_tab():
    """Show addresses tab"""
    pass

def show_order_details(order: Order):
    """Show order details dialog"""
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label(f'Order #{order.order_number}').classes('text-xl font-bold mb-4')
        
        ui.label(f'Date: {order.created_at.strftime("%B %d, %Y")}')
        ui.label(f'Status: {order.status.title()}')
        ui.label(f'Total: ${order.total_amount:.2f}')
        
        if order.shipping_address:
            ui.label('Shipping Address:').classes('font-semibold mt-4')
            ui.label(order.shipping_address)
        
        ui.button('Close', on_click=dialog.close).classes('mt-4')
    
    dialog.open()