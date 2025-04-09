from app import app
from models import db, Product, Category, product_category, CartItem, WishlistItem
from werkzeug.exceptions import BadRequest

def seed_database():
    print("🌱 Seeding database with validation checks...")
    
    try:
        # Clear existing data with proper error handling
        print("Clearing existing data...")
        try:
            db.session.query(product_category).delete()
            Product.query.delete()
            Category.query.delete()
            CartItem.query.delete()
            WishlistItem.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to clear existing data: {str(e)}")

        # Create categories with validation
        print("Creating categories...")
        categories = [
            {"name": "Smartphones", "slug": "smartphones"},
            {"name": "Laptops", "slug": "laptops"},
            {"name": "Audio", "slug": "audio"},
            {"name": "Gaming", "slug": "gaming"},
            {"name": "Accessories", "slug": "accessories"},
            {"name": "Premium", "slug": "premium"}
        ]

        category_objects = []
        for cat_data in categories:
            try:
                category = Category(**cat_data)
                db.session.add(category)
                category_objects.append(category)
            except BadRequest as e:
                print(f"⚠️ Failed to create category {cat_data['name']}: {str(e)}")
                continue

        db.session.commit()

        # Create products with validation
        print("Creating products...")
        products = [
            {
                "name": "iPhone 15 Pro Max",
                "price": 1199.99,
                "description": "6.7\" Super Retina XDR, A17 Pro chip",
                "image_url": "https://example.com/iphone15pm.jpg"
            },
            {
                "name": "Alienware x16",
                "price": 2899.99,
                "description": "16\" QHD+, i9-13900HK, RTX 4080",
                "image_url": "https://example.com/alienware.jpg"
            },
            {
                "name": "Sony WH-1000XM5",
                "price": 399.99,
                "description": "Premium noise-cancelling headphones",
                "image_url": "https://example.com/sonyxm5.jpg"
            },
            {
                "name": "PlayStation 5 Pro",
                "price": 699.99,
                "description": "Enhanced 4K gaming console",
                "image_url": "https://example.com/ps5pro.jpg"
            },
            {
                "name": "SteelSeries Arctis Nova Pro",
                "price": 349.99,
                "description": "Wireless gaming headset",
                "image_url": "https://example.com/arctis.jpg"
            }
        ]

        product_objects = []
        for prod_data in products:
            try:
                product = Product(**prod_data)
                db.session.add(product)
                product_objects.append(product)
            except BadRequest as e:
                print(f"⚠️ Failed to create product {prod_data['name']}: {str(e)}")
                continue

        db.session.commit()

        # Create many-to-many relationships
        print("Creating category relationships...")
        relationships = [
            (0, [0, 5]),   # iPhone: Smartphones, Premium
            (1, [1, 3, 5]), # Alienware: Laptops, Gaming, Premium
            (2, [2, 5]),    # Sony: Audio, Premium
            (3, [3, 5]),    # PS5: Gaming, Premium
            (4, [2, 3, 4])  # SteelSeries: Audio, Gaming, Accessories
        ]

        for prod_idx, cat_indices in relationships:
            try:
                product = product_objects[prod_idx]
                product.categories.extend([category_objects[i] for i in cat_indices])
            except Exception as e:
                print(f"⚠️ Failed to create relationship for {product.name}: {str(e)}")
                continue

        db.session.commit()

        # Create cart items with validation
        print("Creating cart items...")
        cart_items = [
            {"product_id": 1, "quantity": 1},
            {"product_id": 3, "quantity": 2}
        ]

        for item_data in cart_items:
            try:
                cart_item = CartItem(**item_data)
                db.session.add(cart_item)
            except BadRequest as e:
                print(f"⚠️ Failed to create cart item: {str(e)}")
                continue

        # Create wishlist items
        print("Creating wishlist items...")
        wishlist_items = [
            {"product_id": 2},
            {"product_id": 4}
        ]

        for item_data in wishlist_items:
            try:
                wishlist_item = WishlistItem(**item_data)
                db.session.add(wishlist_item)
            except BadRequest as e:
                print(f"⚠️ Failed to create wishlist item: {str(e)}")
                continue

        db.session.commit()

        # Verification
        print("\n✅ Database successfully seeded!")
        print("\nSample data verification:")
        print(f"- Created {len(category_objects)} categories")
        print(f"- Created {len(product_objects)} products")
        print(f"- Created {len(cart_items)} cart items")
        print(f"- Created {len(wishlist_items)} wishlist items")

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Seeding failed: {str(e)}")
        raise

if __name__ == '__main__':
    with app.app_context():
        seed_database()
