"""Professional visual asset management system for fashion e-commerce"""

import requests
import hashlib
from typing import Dict, List, Optional
from urllib.parse import quote
import json
import os
from pathlib import Path

from app.core.config import settings
from app.core.logger import app_logger

class AssetManager:
    """Advanced professional visual asset management system for fashion e-commerce"""
    
    FASHION_CATEGORIES = {
        "hero": {
            "keywords": ["fashion", "shopping", "style", "clothing", "retail", "boutique"],
            "sizes": ["1920x800", "1200x600", "800x400"]
        },
        "women": {
            "keywords": ["women fashion", "female model", "women clothing", "dress", "blouse"],
            "sizes": ["600x800", "400x600", "300x400"]
        },
        "men": {
            "keywords": ["men fashion", "male model", "men clothing", "shirt", "suit"],
            "sizes": ["600x800", "400x600", "300x400"]
        },
        "kids": {
            "keywords": ["kids fashion", "children clothing", "kids style", "child model"],
            "sizes": ["600x600", "400x400", "300x300"]
        },
        "accessories": {
            "keywords": ["fashion accessories", "jewelry", "bags", "watches", "sunglasses"],
            "sizes": ["600x600", "400x400", "300x300"]
        },
        "shoes": {
            "keywords": ["shoes", "sneakers", "boots", "heels", "footwear"],
            "sizes": ["600x400", "400x300", "300x200"]
        },
        "lifestyle": {
            "keywords": ["lifestyle", "modern living", "fashion lifestyle", "shopping experience"],
            "sizes": ["800x600", "600x400", "400x300"]
        },
        "sale": {
            "keywords": ["sale", "discount", "shopping", "bargain", "special offer"],
            "sizes": ["600x400", "400x300", "300x200"]
        }
    }
    
    def __init__(self):
        self.cache_dir = Path("app/static/cache/images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_fashion_images(self, category: str, count: int = 6) -> List[Dict[str, str]]:
        """Get fashion-specific images for different categories"""
        if category not in self.FASHION_CATEGORIES:
            category = "hero"
        
        category_data = self.FASHION_CATEGORIES[category]
        keywords = category_data["keywords"]
        sizes = category_data["sizes"]
        
        images = []
        for i in range(count):
            keyword = keywords[i % len(keywords)]
            size = sizes[0]  # Use primary size
            
            # Create unique seed for consistent images
            seed = hashlib.md5(f"{category}_{keyword}_{i}".encode()).hexdigest()[:8]
            
            # Multiple image sources for reliability
            primary_url = f"https://source.unsplash.com/{size}/?{quote(keyword)}&sig={seed}"
            fallback_url = f"https://picsum.photos/{size.replace('x', '/')}?random={abs(hash(seed)) % 10000}"
            
            images.append({
                "primary": primary_url,
                "fallback": fallback_url,
                "alt": f"Fashion {keyword} image",
                "category": category,
                "size": size
            })
        
        return images
    
    def get_product_images(self, product_name: str, category: str = "fashion", count: int = 4) -> List[Dict[str, str]]:
        """Get product-specific images"""
        # Determine category from product name
        product_lower = product_name.lower()
        if any(word in product_lower for word in ["dress", "blouse", "skirt", "women"]):
            img_category = "women"
        elif any(word in product_lower for word in ["shirt", "suit", "men", "male"]):
            img_category = "men"
        elif any(word in product_lower for word in ["kids", "child", "children"]):
            img_category = "kids"
        elif any(word in product_lower for word in ["bag", "jewelry", "watch", "accessory"]):
            img_category = "accessories"
        elif any(word in product_lower for word in ["shoe", "sneaker", "boot", "heel"]):
            img_category = "shoes"
        else:
            img_category = category
        
        return self.get_fashion_images(img_category, count)
    
    def get_hero_images(self, count: int = 3) -> List[Dict[str, str]]:
        """Get hero banner images for homepage"""
        return self.get_fashion_images("hero", count)
    
    def get_category_image(self, category_name: str) -> Dict[str, str]:
        """Get a single image for category display"""
        images = self.get_fashion_images(category_name.lower(), 1)
        return images[0] if images else self.get_placeholder_image()
    
    def get_placeholder_image(self, size: str = "400x300") -> Dict[str, str]:
        """Get a placeholder image"""
        return {
            "primary": f"https://via.placeholder.com/{size}/f0f0f0/666666?text=Fashion+Item",
            "fallback": f"https://picsum.photos/{size.replace('x', '/')}?random=1",
            "alt": "Fashion item placeholder",
            "category": "placeholder",
            "size": size
        }
    
    def cache_image(self, url: str, filename: str) -> Optional[str]:
        """Cache an image locally"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                cache_path = self.cache_dir / filename
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                return str(cache_path)
        except Exception as e:
            app_logger.warning(f"Failed to cache image {url}: {e}")
        return None
    
    def get_image_css(self) -> str:
        """Generate CSS for professional image handling"""
        return """
        /* Professional Fashion Image System */
        .hero-image {
            width: 100%;
            height: 500px;
            object-fit: cover;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .hero-image:hover {
            transform: scale(1.02);
        }
        
        .product-image {
            width: 100%;
            height: 300px;
            object-fit: cover;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .product-image:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .category-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 8px;
            filter: brightness(0.8);
            transition: all 0.3s ease;
        }
        
        .category-image:hover {
            filter: brightness(1);
            transform: scale(1.03);
        }
        
        .product-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin: 32px 0;
        }
        
        .product-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .product-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        }
        
        .image-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.7) 100%);
            display: flex;
            align-items: flex-end;
            padding: 20px;
            color: white;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .product-card:hover .image-overlay {
            opacity: 1;
        }
        
        .sale-badge {
            position: absolute;
            top: 12px;
            right: 12px;
            background: #ff4757;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            z-index: 2;
        }
        
        .featured-badge {
            position: absolute;
            top: 12px;
            left: 12px;
            background: #2ed573;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            z-index: 2;
        }
        
        @media (max-width: 768px) {
            .hero-image {
                height: 300px;
            }
            
            .product-gallery {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }
            
            .product-image {
                height: 250px;
            }
        }
        """