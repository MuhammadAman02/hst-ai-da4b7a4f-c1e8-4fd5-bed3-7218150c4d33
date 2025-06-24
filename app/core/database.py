"""Database models and connection management"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional
import json

from app.core.config import settings
from app.core.logger import app_logger

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables for many-to-many relationships
product_categories = Table(
    'product_categories',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    products = relationship("Product", secondary=product_categories, back_populates="categories")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    sale_price = Column(Float)
    sku = Column(String(100), unique=True)
    stock_quantity = Column(Integer, default=0)
    images = Column(Text)  # JSON string of image URLs
    sizes = Column(Text)   # JSON string of available sizes
    colors = Column(Text)  # JSON string of available colors
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    categories = relationship("Category", secondary=product_categories, back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    
    @property
    def image_list(self) -> List[str]:
        return json.loads(self.images) if self.images else []
    
    @property
    def size_list(self) -> List[str]:
        return json.loads(self.sizes) if self.sizes else []
    
    @property
    def color_list(self) -> List[str]:
        return json.loads(self.colors) if self.colors else []
    
    @property
    def current_price(self) -> float:
        return self.sale_price if self.sale_price else self.price

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    size = Column(String(10))
    color = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="pending")  # pending, confirmed, shipped, delivered, cancelled
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(Text)
    billing_address = Column(Text)
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="pending")
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Price at time of order
    size = Column(String(10))
    color = Column(String(50))
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

# Database session dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_database():
    """Initialize database with sample data"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Add sample data
        db = SessionLocal()
        
        # Check if data already exists
        if db.query(Category).count() == 0:
            await create_sample_data(db)
        
        db.close()
        app_logger.info("Database initialized successfully")
        
    except Exception as e:
        app_logger.error(f"Database initialization failed: {e}")
        raise

async def create_sample_data(db: Session):
    """Create sample categories and products"""
    
    # Categories
    categories_data = [
        {"name": "Women", "slug": "women", "description": "Women's fashion and clothing"},
        {"name": "Men", "slug": "men", "description": "Men's fashion and clothing"},
        {"name": "Kids", "slug": "kids", "description": "Children's clothing and accessories"},
        {"name": "Accessories", "slug": "accessories", "description": "Fashion accessories and jewelry"},
        {"name": "Shoes", "slug": "shoes", "description": "Footwear for all occasions"},
        {"name": "Sale", "slug": "sale", "description": "Discounted items and special offers"}
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
        categories.append(category)
    
    db.commit()
    
    # Sample products
    products_data = [
        {
            "name": "Classic White T-Shirt",
            "slug": "classic-white-tshirt",
            "description": "Essential white cotton t-shirt with comfortable fit",
            "price": 19.99,
            "sku": "WTS001",
            "stock_quantity": 100,
            "sizes": '["XS", "S", "M", "L", "XL"]',
            "colors": '["White", "Black", "Gray"]',
            "is_featured": True
        },
        {
            "name": "Denim Skinny Jeans",
            "slug": "denim-skinny-jeans",
            "description": "Comfortable skinny fit jeans in classic blue denim",
            "price": 49.99,
            "sale_price": 39.99,
            "sku": "WJ001",
            "stock_quantity": 75,
            "sizes": '["26", "28", "30", "32", "34"]',
            "colors": '["Blue", "Black", "Light Blue"]',
            "is_featured": True
        },
        {
            "name": "Casual Button-Down Shirt",
            "slug": "casual-button-down-shirt",
            "description": "Versatile button-down shirt perfect for any occasion",
            "price": 34.99,
            "sku": "MS001",
            "stock_quantity": 60,
            "sizes": '["S", "M", "L", "XL", "XXL"]',
            "colors": '["White", "Blue", "Navy", "Gray"]'
        },
        {
            "name": "Summer Floral Dress",
            "slug": "summer-floral-dress",
            "description": "Light and breezy floral dress perfect for summer",
            "price": 59.99,
            "sku": "WD001",
            "stock_quantity": 40,
            "sizes": '["XS", "S", "M", "L"]',
            "colors": '["Floral Pink", "Floral Blue", "Floral Yellow"]',
            "is_featured": True
        },
        {
            "name": "Kids Rainbow Hoodie",
            "slug": "kids-rainbow-hoodie",
            "description": "Colorful hoodie that kids will love",
            "price": 29.99,
            "sku": "KH001",
            "stock_quantity": 50,
            "sizes": '["4T", "5T", "6", "8", "10", "12"]',
            "colors": '["Rainbow", "Pink", "Blue"]'
        },
        {
            "name": "Leather Crossbody Bag",
            "slug": "leather-crossbody-bag",
            "description": "Stylish leather crossbody bag for everyday use",
            "price": 79.99,
            "sku": "AB001",
            "stock_quantity": 25,
            "colors": '["Black", "Brown", "Tan"]'
        }
    ]
    
    for product_data in products_data:
        product = Product(**product_data)
        db.add(product)
        
        # Assign categories based on product type
        if "women" in product.name.lower() or "dress" in product.name.lower():
            product.categories.append(categories[0])  # Women
        elif "men" in product.name.lower() or "shirt" in product.name.lower():
            product.categories.append(categories[1])  # Men
        elif "kids" in product.name.lower():
            product.categories.append(categories[2])  # Kids
        elif "bag" in product.name.lower():
            product.categories.append(categories[3])  # Accessories
        
        if product.sale_price:
            product.categories.append(categories[5])  # Sale
    
    db.commit()
    app_logger.info("Sample data created successfully")