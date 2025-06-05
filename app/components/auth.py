"""
Authentication components
"""
from typing import Optional
from nicegui import ui
from models.schemas import User


class AuthComponent:
    """Authentication and authorization components"""
    
    def __init__(self):
        self.current_user: Optional[User] = None
    
    def create_login_form(self, on_login_success=None):
        """Create login form component"""
        with ui.card().classes('w-96 mx-auto'):
            ui.label('Login to Fraud Detection System').classes('text-xl font-bold mb-4')
            
            email_input = ui.input('Email', placeholder='Enter your email').classes('w-full')
            password_input = ui.input('Password', password=True).classes('w-full')
            
            async def handle_login():
                # Simulate authentication
                if email_input.value and password_input.value:
                    self.current_user = User(
                        id=1,
                        email=email_input.value,
                        full_name="Bank Administrator",
                        role="admin",
                        is_active=True
                    )
                    if on_login_success:
                        await on_login_success(self.current_user)
                else:
                    ui.notification('Please enter valid credentials', type='negative')
            
            ui.button('Login', on_click=handle_login).classes('w-full bg-blue-600 text-white')
    
    def create_user_menu(self):
        """Create user menu component"""
        if not self.current_user:
            return
        
        with ui.row().classes('items-center gap-2'):
            ui.avatar(f'{self.current_user.full_name[0]}', color='blue')
            ui.label(self.current_user.full_name).classes('text-sm')
            
            with ui.menu() as menu:
                ui.menu_item('Profile', lambda: ui.notification('Profile clicked'))
                ui.menu_item('Settings', lambda: ui.notification('Settings clicked'))
                ui.separator()
                ui.menu_item('Logout', lambda: self.logout())
            
            ui.button(icon='more_vert', on_click=menu.open).props('flat round')
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        ui.navigate.to('/login')
        ui.notification('Logged out successfully')
    
    def require_auth(self, required_role: str = None):
        """Decorator to require authentication"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                if not self.current_user:
                    ui.navigate.to('/login')
                    return
                
                if required_role and self.current_user.role != required_role:
                    ui.notification('Insufficient permissions', type='negative')
                    return
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator