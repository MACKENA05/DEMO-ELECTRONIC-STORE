from flask import Flask, request, jsonify
from flask_restful import Resource
from extensions import db, api, cors, migrate
import os
from werkzeug.exceptions import BadRequest, NotFound
from sqlalchemy.exc import IntegrityError
from models import Product, Category, CartItem, WishlistItem

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    cors.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    
    return app

app = create_app()


class ProductResource(Resource):
    def get(self, product_id=None):
        try:
            if product_id:
                product = Product.query.get_or_404(product_id)
                return product.to_dict()
            return [p.to_dict() for p in Product.query.all()]
        except NotFound:
            return {'error': 'Product not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        try:
            data = request.get_json()
            product = Product(**data)
            db.session.add(product)
            db.session.commit()
            return product.to_dict(), 201
        except BadRequest as e:
            return {'error': str(e)}, 400
        except IntegrityError:
            return {'error': 'Product already exists'}, 409
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def put(self, product_id):
        try:
            product = Product.query.get_or_404(product_id)
            data = request.get_json()
            for key, value in data.items():
                setattr(product, key, value)
            db.session.commit()
            return product.to_dict()
        except NotFound:
            return {'error': 'Product not found'}, 404
        except BadRequest as e:
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, product_id):
        try:
            product = Product.query.get_or_404(product_id)
            db.session.delete(product)
            db.session.commit()
            return '', 204
        except NotFound:
            return {'error': 'Product not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class CategoryResource(Resource):
    def get(self, category_id=None):
        try:
            if category_id:
                category = Category.query.get_or_404(category_id)
                return category.to_dict()
            return [c.to_dict() for c in Category.query.all()]
        except NotFound:
            return {'error': 'Category not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        try:
            data = request.get_json()
            category = Category(**data)
            db.session.add(category)
            db.session.commit()
            return category.to_dict(), 201
        except BadRequest as e:
            return {'error': str(e)}, 400
        except IntegrityError:
            return {'error': 'Category already exists'}, 409
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def put(self, category_id):
        try:
            category = Category.query.get_or_404(category_id)
            data = request.get_json()
            for key, value in data.items():
                setattr(category, key, value)
            db.session.commit()
            return category.to_dict()
        except NotFound:
            return {'error': 'Category not found'}, 404
        except BadRequest as e:
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, category_id):
        try:
            category = Category.query.get_or_404(category_id)
            db.session.delete(category)
            db.session.commit()
            return '', 204
        except NotFound:
            return {'error': 'Category not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class CartItemResource(Resource):
    def get(self, cart_item_id=None):
        try:
            if cart_item_id:
                item = CartItem.query.get_or_404(cart_item_id)
                return item.to_dict()
            return [i.to_dict() for i in CartItem.query.all()]
        except NotFound:
            return {'error': 'Cart item not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        try:
            data = request.get_json()
            item = CartItem(**data)
            db.session.add(item)
            db.session.commit()
            return item.to_dict(), 201
        except BadRequest as e:
            return {'error': str(e)}, 400
        except IntegrityError:
            return {'error': 'Invalid product reference'}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def put(self, cart_item_id):
        try:
            item = CartItem.query.get_or_404(cart_item_id)
            data = request.get_json()
            for key, value in data.items():
                setattr(item, key, value)
            db.session.commit()
            return item.to_dict()
        except NotFound:
            return {'error': 'Cart item not found'}, 404
        except BadRequest as e:
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, cart_item_id):
        try:
            item = CartItem.query.get_or_404(cart_item_id)
            db.session.delete(item)
            db.session.commit()
            return '', 204
        except NotFound:
            return {'error': 'Cart item not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

class WishlistItemResource(Resource):
    def get(self, wishlist_item_id=None):
        try:
            if wishlist_item_id:
                item = WishlistItem.query.get_or_404(wishlist_item_id)
                return item.to_dict()
            return [i.to_dict() for i in WishlistItem.query.all()]
        except NotFound:
            return {'error': 'Wishlist item not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        try:
            data = request.get_json()
            item = WishlistItem(**data)
            db.session.add(item)
            db.session.commit()
            return item.to_dict(), 201
        except BadRequest as e:
            return {'error': str(e)}, 400
        except IntegrityError:
            return {'error': 'Invalid product reference'}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, wishlist_item_id):
        try:
            item = WishlistItem.query.get_or_404(wishlist_item_id)
            db.session.delete(item)
            db.session.commit()
            return '', 204
        except NotFound:
            return {'error': 'Wishlist item not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

# Register all resources with their routes
api.add_resource(ProductResource, 
    '/api/products', 
    '/api/products/<int:product_id>'
)
api.add_resource(CategoryResource, 
    '/api/categories', 
    '/api/categories/<int:category_id>'
)
api.add_resource(CartItemResource, 
    '/api/cart', 
    '/api/cart/<int:cart_item_id>'
)
api.add_resource(WishlistItemResource, 
    '/api/wishlist', 
    '/api/wishlist/<int:wishlist_item_id>'
)

@app.route('/')
def health_check():
    return {
        'status': 'healthy',
        'routes': {
            'products': '/api/products',
            'categories': '/api/categories',
            'cart': '/api/cart', 
            'wishlist': '/api/wishlist'
        }
    }

# Error handlers
@app.errorhandler(400)
def handle_bad_request(e):
    return {'error': str(e)}, 400

@app.errorhandler(404)
def handle_not_found(e):
    return {'error': 'Resource not found'}, 404

@app.errorhandler(500)
def handle_server_error(e):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
