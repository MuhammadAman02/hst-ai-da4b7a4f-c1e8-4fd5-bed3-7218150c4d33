"""
H&M-Style Clothing E-commerce Store
✓ Complete product catalog with fashion categories and image galleries
✓ Shopping cart and checkout functionality with real-time updates
✓ User authentication and profile management system
✓ Order processing and management system
✓ Admin panel for product and inventory management
✓ Professional fashion imagery integration with fallbacks
✓ Modern responsive design optimized for fashion retail
✓ Zero-configuration deployment readiness
"""

import os
import sys
from dotenv import load_dotenv
from nicegui import ui, app
import asyncio
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Import the main application
try:
    from app.main import setup_application
    from app.core.config import settings
    from app.core.database import init_database
    from app.core.logger import app_logger
except ImportError as e:
    print(f"Error importing application modules: {e}")
    sys.exit(1)

@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager"""
    # Startup
    app_logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    await init_database()
    yield
    # Shutdown
    app_logger.info("Shutting down application")

if __name__ in {"__main__", "__mp_main__"}:
    try:
        # Set up the application
        setup_application()
        
        # Configure FastAPI app
        app.add_middleware(
            "fastapi.middleware.cors.CORSMiddleware",
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Run the application
        ui.run(
            host=settings.HOST,
            port=settings.PORT,
            title=settings.APP_NAME,
            favicon="🛍️",
            reload=settings.DEBUG,
            show=False,
            storage_secret=settings.SECRET_KEY,
        )
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)