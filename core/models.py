from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    price: int = 0
    description: str = ""
    stock: int = 0
    image_url: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "stock": self.stock,
            "image_url": self.image_url,
        }

@dataclass
class CartItem:
    product_id: int
    quantity: int
    product_name: str = ""
    product_price: int = 0

@dataclass
class Order:
    id: Optional[int] = None
    user_id: int = 0
    items: List[Dict[str, Any]] = None
    total: int = 0
    status: str = "новый"
    name: str = ""
    phone: str = ""
    address: str = ""
    created_at: str = ""