from dataclasses import dataclass, field



@dataclass
class Product:
    _id: str
    title: str
    prices: list = field(default_factory=list)
    rating: int = 0
    specification: str = None
    description: str = None
    img: str = None
    keywords: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)


@dataclass
class User:
    _id: str
    email: str
    password: str
    favorites: list[str] = field(default_factory=list)
    cart: list[str] = field(default_factory=list)