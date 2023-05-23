from dataclasses import dataclass, field



@dataclass
class Product:
    _id: str
    title: str
    price: str
    rating: int = 0
    specification: str
    description: str 
    video_link: str 


@dataclass
class User:
    _id: str
    email: str
    password: str
    favorites: list[str] = field(default_factory=list)
    cart: list[str] = field(default_factory=list)