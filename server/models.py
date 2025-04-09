from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event, CheckConstraint
from werkzeug.exceptions import BadRequest
import re

db = SQLAlchemy()


# Association table
product_category = db.Table(
    'product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True),
    extend_existing=True
)

class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
    )
    
    serialize_rules = ('-cart_items.product', '-wishlist_items.product')
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    
    # Relationships
    categories = db.relationship(
        'Category', 
        secondary=product_category,
        back_populates='products',
        lazy='dynamic'
    )
    category_names = association_proxy('categories', 'name')
    cart_items = db.relationship('CartItem', back_populates='product', lazy=True)
    wishlist_items = db.relationship('WishlistItem', back_populates='product', lazy=True)

    # Validation methods
    def validate_name(self, name):
        if not name or len(name) > 100:
            raise ValueError("Product name must be 1-100 characters")
        return name

    def validate_price(self, price):
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price must be a positive number")
        return float(price)

    def validate_image_url(self, url):
        if url and len(url) > 255:
            raise ValueError("Image URL must be ≤ 255 characters")
        if url and not re.match(r'^https?://', url):
            raise ValueError("Image URL must start with http:// or https://")
        return url

    def __init__(self, **kwargs):
        try:
            self.name = self.validate_name(kwargs.get('name'))
            self.price = self.validate_price(kwargs.get('price'))
            self.description = kwargs.get('description')
            self.image_url = self.validate_image_url(kwargs.get('image_url'))
        except ValueError as e:
            raise BadRequest(str(e))

    def __repr__(self):
        return f'<Product {self.name}>'

class Category(db.Model,SerializerMixin):
    __tablename__ = 'categories'

    serialize_rules = ('-products.categories',)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    products = db.relationship(
        'Product',
        secondary=product_category,
        back_populates='categories',
        lazy='dynamic'
    )
    product_names = association_proxy('products', 'name')

    # Validation methods
    def validate_name(self, name):
        if not name or len(name) > 50:
            raise ValueError("Category name must be 1-50 characters")
        return name

    def validate_slug(self, slug):
        if not slug or len(slug) > 50:
            raise ValueError("Slug must be 1-50 characters")
        if not re.match(r'^[a-z0-9-]+$', slug):
            raise ValueError("Slug can only contain lowercase letters, numbers, and hyphens")
        return slug

    def __init__(self, **kwargs):
        try:
            self.name = self.validate_name(kwargs.get('name'))
            self.slug = self.validate_slug(kwargs.get('slug'))
        except ValueError as e:
            raise BadRequest(str(e))

    def __repr__(self):
        return f'<Category {self.name}>'

class CartItem(db.Model, SerializerMixin):
    __tablename__ = 'cart_items'
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
    
    serialize_rules = ('-product.cart_items', '-product.wishlist_items',)
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    product = db.relationship('Product', back_populates='cart_items')

    # Validation methods
    def validate_quantity(self, quantity):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        return quantity

    def __init__(self, **kwargs):
        try:
            self.product_id = kwargs.get('product_id')
            self.quantity = self.validate_quantity(kwargs.get('quantity', 1))
        except ValueError as e:
            raise BadRequest(str(e))

    def __repr__(self):
        return f'<CartItem {self.product_id}>'

class WishlistItem(db.Model, SerializerMixin):
    __tablename__ = 'wishlist_items'
    
    serialize_rules = ('-product.cart_items', '-product.wishlist_items',)
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    product = db.relationship('Product', back_populates='wishlist_items')

    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')

    def __repr__(self):
        return f'<WishlistItem {self.product_id}>'

# Validation event listeners
@event.listens_for(Product, 'before_update')
def validate_product_before_update(mapper, connection, target):
    if hasattr(target, 'name'):
        target.validate_name(target.name)
    if hasattr(target, 'price'):
        target.validate_price(target.price)
    if hasattr(target, 'image_url'):
        target.validate_image_url(target.image_url)

@event.listens_for(Category, 'before_update')
def validate_category_before_update(mapper, connection, target):
    if hasattr(target, 'name'):
        target.validate_name(target.name)
    if hasattr(target, 'slug'):
        target.validate_slug(target.slug)

@event.listens_for(CartItem, 'before_update')
def validate_cart_item_before_update(mapper, connection, target):
    if hasattr(target, 'quantity'):
        target.validate_quantity(target.quantity)
