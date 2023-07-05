from dataclasses import dataclass, field



@dataclass
class Product:
    _id: str
    title: str
    prices: list = field(default_factory=list)
    rating: dict = field(default_factory=dict)
    description: str = None
    img: str = None
    keywords: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)


@dataclass
class User:
    _id: str
    username: str
    email: str
    password: str
    favorites: list[str] = field(default_factory=list)
    cart: dict = field(default_factory=dict)