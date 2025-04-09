from flask import Flask,make_response,jsonify,request
from models import db, Product, Category, CartItem, WishlistItem
from flask_migrate import Migrate
from flask_restful import Api,Resource
from flask_cors import CORS
from werkzeug.exceptions import NotFound, InternalServerError,BadRequest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///electronics.db'   
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
db.init_app(app)
api = Api(app)
migrate = Migrate(app, db)
cors= CORS(app)

# Product resource for all and one product
class ProductResource(Resource):
    def get(self, id=None):
        try:
            if id:
                # Getting single product
                product = Product.query.get(id)
                if not product:
                    raise NotFound("Product not found")
                return make_response(product.to_dict(rules = ('-cart_items','-wishlist_items','categories')), 200)
            else:
                # Getting all products
                products = Product.query.all()
                return make_response([product.to_dict(rules = ('-cart_items','-wishlist_items','categories')) for product in products], 200)
                
        except NotFound as e:
            return make_response({"error": str(e)}, 404)
        except Exception as e:
            return make_response({"error": "Internal server error"}, 500)

api.add_resource(ProductResource, '/products','/products/<int:id>')
    
# category resource for both all and one category
class CategoryResource(Resource):
    def get(self, category_id=None):
        try:
            if category_id:
                category = Category.query.get_or_404(category_id)
                return make_response(category.to_dict(rules = ('-products.cart_items','products.wishlist_items',)),200)
            return make_response([category.to_dict(rules = ('-products.cart_items','products.wishlist_items',)) for category in Category.query.all()])
        except NotFound:
            return {'error': 'Category not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500
api.add_resource(CategoryResource, '/categories','/categories/<int:category_id>')

class CartItemResource(Resource):
    # GET: List all cart items 
    def get(self):
        try:
            cart_items = CartItem.query.all()  
            return jsonify([item.to_dict() for item in cart_items])
        except Exception as e:
            return {'error': str(e)}, 500

    #Adding a new item to cart
    def post(self):
        try:
            data = request.get_json()
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)

            if not product_id:
                return {'error': 'Product ID is required'}, 400
            
            product = Product.query.get_or_404(product_id)

        
            cart_item = CartItem.query.filter_by(product_id=product_id).first()
            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = CartItem(product_id=product_id, quantity=quantity)
                db.session.add(cart_item)

            db.session.commit()
            return jsonify(cart_item.to_dict()), 201

        except NotFound:
            return {'error': 'Product not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500


api.add_resource(CartItemResource, '/cart')

class CartItemResourceByID(Resource):
    def get(self, item_id):
        try:
            cart_item = CartItem.query.get_or_404(item_id)
            return jsonify(cart_item.to_dict())
        except Exception as e:
            return {'error': str(e)}, 500
        
    def patch(self, item_id):
        try:
            data = request.get_json()
            quantity = data.get('quantity')

            if not quantity or quantity < 1:
                return {'error': 'Valid quantity is required'}, 400

            cart_item = CartItem.query.get_or_404(item_id)
            cart_item.quantity = quantity
            db.session.commit()
            return jsonify(cart_item.to_dict())

        except NotFound:
            return {'error': 'Cart item not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def delete(self, item_id):
        try:
            cart_item = CartItem.query.get_or_404(item_id)
            db.session.delete(cart_item)
            db.session.commit()
            return {'message': 'Item removed from cart'}, 200

        except NotFound:
            return {'error': 'Cart item not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

api.add_resource(CartItemResourceByID, '/cart/<int:item_id>')

class WishlistResource(Resource):
    # Get all wishlist items
    def get(self):
        try:
            wishlist_items = WishlistItem.query.all()  # Add user_id filter if needed
            return jsonify([item.to_dict() for item in wishlist_items])
        except Exception as e:
            return {'error': str(e)}, 500

    # Add product to wishlist
    def post(self):
        try:
            data = request.get_json()
            product_id = data.get('product_id')

            if not product_id:
                return {'error': 'Product ID is required'}, 400
            
            Product.query.get_or_404(product_id)

            existing = WishlistItem.query.filter_by(product_id=product_id).first()
            if existing:
                return {'error': 'Product already in wishlist'}, 409

            new_item = WishlistItem(product_id=product_id)
            db.session.add(new_item)
            db.session.commit()
            return jsonify(new_item.to_dict()), 201

        except NotFound:
            return {'error': 'Product not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
        
api.add_resource(WishlistResource, '/wishlist')

class WishlistItemResource(Resource):
    # Remove from wishlist
    def delete(self, item_id):
        try:
            item = WishlistItem.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return {'message': 'Item removed from wishlist'}, 200
        except NotFound:
            return {'error': 'Wishlist item not found'}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500


api.add_resource(WishlistItemResource, '/wishlist/items/<int:item_id>')

if __name__ == '__main__':
    app.run(debug=True,port=5555)