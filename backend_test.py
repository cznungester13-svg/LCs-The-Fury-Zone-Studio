#!/usr/bin/env python3
"""
Comprehensive backend API test suite for LCs The Fury Zone
Tests all endpoints under /api prefix using real credentials
"""
import requests
import json
import random
import string
from typing import Dict, Optional

# Configuration
BASE_URL = "https://girardot-hub.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@furyzone.com"
ADMIN_PASSWORD = "Admin123!"
CUSTOMER_EMAIL = "customer@furyzone.com"
CUSTOMER_PASSWORD = "Customer123!"

# Test state
admin_token = None
customer_token = None
test_product_id = None
test_listing_id = None
test_session_id = None

def random_email():
    """Generate random email for registration tests"""
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{rand}@furyzone.test"

def make_request(method: str, endpoint: str, token: Optional[str] = None, 
                 json_data: Optional[Dict] = None, params: Optional[Dict] = None):
    """Make HTTP request with optional auth"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=json_data, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=json_data, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return resp
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {method} {endpoint} - {e}")
        return None

def test_auth():
    """Test authentication endpoints"""
    global admin_token, customer_token
    
    print("\n" + "="*60)
    print("TESTING AUTH ENDPOINTS")
    print("="*60)
    
    # Test 1: Register new user
    print("\n1. Testing POST /auth/register...")
    new_email = random_email()
    resp = make_request("POST", "/auth/register", json_data={
        "email": new_email,
        "password": "TestPass123!",
        "full_name": "Test User"
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if "token" in data and "user" in data:
            print(f"✅ Register successful: {data['user']['email']}")
            if "password_hash" in data["user"]:
                print("❌ SECURITY ISSUE: password_hash exposed in response")
        else:
            print(f"❌ Register response missing fields: {data}")
    else:
        print(f"❌ Register failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Login with admin
    print("\n2. Testing POST /auth/login (admin)...")
    resp = make_request("POST", "/auth/login", json_data={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if "token" in data and "access_token" in data and "user" in data:
            admin_token = data["token"]
            print(f"✅ Admin login successful: {data['user']['email']}")
            print(f"   Roles: {data['user'].get('roles', [])}")
        else:
            print(f"❌ Login response missing fields: {data}")
    else:
        print(f"❌ Admin login failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 3: Login with customer
    print("\n3. Testing POST /auth/login (customer)...")
    resp = make_request("POST", "/auth/login", json_data={
        "email": CUSTOMER_EMAIL,
        "password": CUSTOMER_PASSWORD
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        customer_token = data["token"]
        print(f"✅ Customer login successful: {data['user']['email']}")
    else:
        print(f"❌ Customer login failed: {resp.status_code if resp else 'No response'}")
    
    # Test 4: Invalid login
    print("\n4. Testing POST /auth/login (invalid credentials)...")
    resp = make_request("POST", "/auth/login", json_data={
        "email": "invalid@test.com",
        "password": "wrongpass"
    })
    
    if resp and resp.status_code == 401:
        print("✅ Invalid login correctly rejected with 401")
    else:
        print(f"❌ Invalid login should return 401, got: {resp.status_code if resp else 'No response'}")
    
    # Test 5: Get current user
    print("\n5. Testing GET /auth/me...")
    resp = make_request("GET", "/auth/me", token=admin_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if "password_hash" in data:
            print("❌ SECURITY ISSUE: password_hash exposed in /me endpoint")
        elif "id" in data and "email" in data and "roles" in data:
            print(f"✅ /auth/me successful: {data['email']}")
        else:
            print(f"❌ /auth/me missing required fields: {data}")
    else:
        print(f"❌ /auth/me failed: {resp.status_code if resp else 'No response'}")
    
    return True

def test_catalog():
    """Test catalog endpoints"""
    global test_product_id
    
    print("\n" + "="*60)
    print("TESTING CATALOG ENDPOINTS")
    print("="*60)
    
    # Test 1: Get all products
    print("\n1. Testing GET /products...")
    resp = make_request("GET", "/products")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            product = data[0]
            required_fields = ["id", "title", "name", "image", "price", "rating"]
            missing = [f for f in required_fields if f not in product]
            if missing:
                print(f"❌ Product missing fields: {missing}")
            else:
                test_product_id = product["id"]
                print(f"✅ Products list successful: {len(data)} products")
                print(f"   Sample: {product['title']} - ${product['price']}")
        else:
            print(f"❌ Products list empty or invalid: {data}")
    else:
        print(f"❌ Products list failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Get featured products
    print("\n2. Testing GET /products?featured=true&limit=4...")
    resp = make_request("GET", "/products", params={"featured": "true", "limit": 4})
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            print(f"✅ Featured products: {len(data)} items")
        else:
            print(f"❌ Featured products invalid: {data}")
    else:
        print(f"❌ Featured products failed: {resp.status_code if resp else 'No response'}")
    
    # Test 3: Search products
    print("\n3. Testing GET /products?search=...")
    resp = make_request("GET", "/products", params={"search": "fury"})
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Product search successful: {len(data)} results")
    else:
        print(f"❌ Product search failed: {resp.status_code if resp else 'No response'}")
    
    # Test 4: Sort by price
    print("\n4. Testing GET /products?sort=price_asc...")
    resp = make_request("GET", "/products", params={"sort": "price_asc"})
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if len(data) >= 2:
            if data[0]["price"] <= data[1]["price"]:
                print(f"✅ Price sort working: ${data[0]['price']} <= ${data[1]['price']}")
            else:
                print(f"❌ Price sort broken: ${data[0]['price']} > ${data[1]['price']}")
        else:
            print(f"✅ Price sort returned {len(data)} products")
    else:
        print(f"❌ Price sort failed: {resp.status_code if resp else 'No response'}")
    
    # Test 5: Get single product
    if test_product_id:
        print(f"\n5. Testing GET /products/{test_product_id}...")
        resp = make_request("GET", f"/products/{test_product_id}")
        
        if resp and resp.status_code == 200:
            data = resp.json()
            required_fields = ["id", "title", "name", "image", "price", "rating"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"❌ Product detail missing fields: {missing}")
            else:
                print(f"✅ Product detail successful: {data['title']}")
        else:
            print(f"❌ Product detail failed: {resp.status_code if resp else 'No response'}")
    
    # Test 6: Get departments
    print("\n6. Testing GET /departments...")
    resp = make_request("GET", "/departments")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Departments list: {len(data)} items")
    else:
        print(f"❌ Departments failed: {resp.status_code if resp else 'No response'}")
    
    # Test 7: Get categories
    print("\n7. Testing GET /categories...")
    resp = make_request("GET", "/categories")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Categories list: {len(data)} items")
    else:
        print(f"❌ Categories failed: {resp.status_code if resp else 'No response'}")
    
    # Test 8: Get brands
    print("\n8. Testing GET /brands...")
    resp = make_request("GET", "/brands")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Brands list: {len(data)} items")
    else:
        print(f"❌ Brands failed: {resp.status_code if resp else 'No response'}")
    
    # Test 9: Create review
    if test_product_id and customer_token:
        print(f"\n9. Testing POST /reviews...")
        resp = make_request("POST", "/reviews", token=customer_token, json_data={
            "target_id": test_product_id,
            "target_type": "product",
            "rating": 5,
            "comment": "Great product! Love it."
        })
        
        if resp and resp.status_code == 200:
            data = resp.json()
            print(f"✅ Review created: {data.get('rating')} stars")
        else:
            print(f"❌ Review creation failed: {resp.status_code if resp else 'No response'}")
        
        # Test 10: Get reviews
        print(f"\n10. Testing GET /reviews?target_id={test_product_id}...")
        resp = make_request("GET", "/reviews", params={"target_id": test_product_id})
        
        if resp and resp.status_code == 200:
            data = resp.json()
            print(f"✅ Reviews list: {len(data)} reviews")
        else:
            print(f"❌ Reviews list failed: {resp.status_code if resp else 'No response'}")

def test_cart():
    """Test cart endpoints"""
    print("\n" + "="*60)
    print("TESTING CART ENDPOINTS")
    print("="*60)
    
    if not customer_token or not test_product_id:
        print("❌ Skipping cart tests: missing token or product_id")
        return
    
    # Test 1: Get cart
    print("\n1. Testing GET /cart...")
    resp = make_request("GET", "/cart", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Cart retrieved: {len(data.get('items', []))} items")
    else:
        print(f"❌ Cart retrieval failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Add to cart
    print(f"\n2. Testing POST /cart/add...")
    resp = make_request("POST", "/cart/add", token=customer_token, json_data={
        "item_type": "product",
        "item_id": test_product_id,
        "quantity": 2
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        if items:
            item = items[-1]
            required_fields = ["item_id", "title", "price", "quantity"]
            missing = [f for f in required_fields if f not in item]
            if missing:
                print(f"❌ Cart item missing fields: {missing}")
            else:
                print(f"✅ Added to cart: {item['title']} x{item['quantity']}")
        else:
            print(f"❌ Cart add returned no items")
    else:
        print(f"❌ Cart add failed: {resp.status_code if resp else 'No response'}")
    
    # Test 3: Update cart
    print(f"\n3. Testing POST /cart/update...")
    resp = make_request("POST", "/cart/update", token=customer_token, json_data={
        "item_id": test_product_id,
        "quantity": 3
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        updated_item = next((i for i in items if i.get("item_id") == test_product_id), None)
        if updated_item and updated_item.get("quantity") == 3:
            print(f"✅ Cart updated: quantity now {updated_item['quantity']}")
        else:
            print(f"❌ Cart update failed: quantity not updated correctly")
    else:
        print(f"❌ Cart update failed: {resp.status_code if resp else 'No response'}")
    
    # Test 4: Delete from cart (we'll add it back for checkout tests)
    print(f"\n4. Testing DELETE /cart/item/{test_product_id}...")
    resp = make_request("DELETE", f"/cart/item/{test_product_id}", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        if not any(i.get("item_id") == test_product_id for i in items):
            print(f"✅ Item removed from cart")
        else:
            print(f"❌ Item still in cart after delete")
    else:
        print(f"❌ Cart delete failed: {resp.status_code if resp else 'No response'}")
    
    # Re-add item for checkout tests
    make_request("POST", "/cart/add", token=customer_token, json_data={
        "item_type": "product",
        "item_id": test_product_id,
        "quantity": 2
    })

def test_coupons():
    """Test coupon validation"""
    print("\n" + "="*60)
    print("TESTING COUPON ENDPOINTS")
    print("="*60)
    
    # Test 1: Valid coupon FURY10
    print("\n1. Testing POST /coupons/validate (FURY10)...")
    resp = make_request("POST", "/coupons/validate", json_data={"code": "FURY10"})
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if data.get("code") == "FURY10" and data.get("percent_off") == 10:
            print(f"✅ Coupon FURY10 valid: {data['percent_off']}% off")
        else:
            print(f"❌ Coupon data incorrect: {data}")
    else:
        print(f"❌ Coupon validation failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Valid coupon ZONE20
    print("\n2. Testing POST /coupons/validate (ZONE20)...")
    resp = make_request("POST", "/coupons/validate", json_data={"code": "ZONE20"})
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if data.get("code") == "ZONE20" and data.get("percent_off") == 20:
            print(f"✅ Coupon ZONE20 valid: {data['percent_off']}% off")
        else:
            print(f"❌ Coupon data incorrect: {data}")
    else:
        print(f"❌ Coupon validation failed: {resp.status_code if resp else 'No response'}")
    
    # Test 3: Invalid coupon
    print("\n3. Testing POST /coupons/validate (invalid)...")
    resp = make_request("POST", "/coupons/validate", json_data={"code": "INVALID"})
    
    if resp and resp.status_code == 404:
        print("✅ Invalid coupon correctly rejected with 404")
    else:
        print(f"❌ Invalid coupon should return 404, got: {resp.status_code if resp else 'No response'}")

def test_addresses():
    """Test address endpoints"""
    print("\n" + "="*60)
    print("TESTING ADDRESS ENDPOINTS")
    print("="*60)
    
    if not customer_token:
        print("❌ Skipping address tests: missing token")
        return
    
    # Test 1: Add address
    print("\n1. Testing POST /addresses...")
    resp = make_request("POST", "/addresses", token=customer_token, json_data={
        "label": "Home",
        "full_name": "John Doe",
        "line1": "123 Fury Street",
        "city": "Los Angeles",
        "state": "CA",
        "postal_code": "90001",
        "country": "US"
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Address created: {data.get('label')} - {data.get('city')}")
    else:
        print(f"❌ Address creation failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Get addresses
    print("\n2. Testing GET /addresses...")
    resp = make_request("GET", "/addresses", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Addresses retrieved: {len(data)} addresses")
    else:
        print(f"❌ Addresses retrieval failed: {resp.status_code if resp else 'No response'}")

def test_checkout():
    """Test Stripe checkout endpoints"""
    global test_session_id
    
    print("\n" + "="*60)
    print("TESTING STRIPE CHECKOUT ENDPOINTS")
    print("="*60)
    
    if not customer_token or not test_product_id:
        print("❌ Skipping checkout tests: missing token or product_id")
        return
    
    # Ensure cart has items
    make_request("POST", "/cart/add", token=customer_token, json_data={
        "item_type": "product",
        "item_id": test_product_id,
        "quantity": 1
    })
    
    # Test 1: Create checkout session
    print("\n1. Testing POST /checkout/session...")
    resp = make_request("POST", "/checkout/session", token=customer_token, json_data={
        "origin_url": "http://localhost:3000",
        "coupon_code": "FURY10"
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if "url" in data and "session_id" in data:
            if "checkout.stripe.com" in data["url"]:
                test_session_id = data["session_id"]
                print(f"✅ Checkout session created")
                print(f"   Session ID: {test_session_id}")
                print(f"   URL contains: checkout.stripe.com")
            else:
                print(f"❌ Checkout URL doesn't contain checkout.stripe.com: {data['url']}")
        else:
            print(f"❌ Checkout response missing fields: {data}")
    else:
        print(f"❌ Checkout session failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Check session status
    if test_session_id:
        print(f"\n2. Testing GET /checkout/status/{test_session_id}...")
        resp = make_request("GET", f"/checkout/status/{test_session_id}", token=customer_token)
        
        if resp and resp.status_code == 200:
            data = resp.json()
            required_fields = ["session_id", "status", "payment_status", "order_id"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"❌ Status response missing fields: {missing}")
            else:
                if data["payment_status"] == "pending" and data["order_id"] is None:
                    print(f"✅ Checkout status correct: payment pending, no order yet")
                else:
                    print(f"⚠️  Checkout status: {data['payment_status']}, order: {data['order_id']}")
        else:
            print(f"❌ Checkout status failed: {resp.status_code if resp else 'No response'}")
        
        # Test 3: Verify payment_transactions record exists
        print(f"\n3. Testing GET /checkout/status/bogus_session_id...")
        resp = make_request("GET", "/checkout/status/bogus_session_id_12345", token=customer_token)
        
        if resp and resp.status_code == 404:
            print("✅ Bogus session ID correctly returns 404")
        else:
            print(f"❌ Bogus session should return 404, got: {resp.status_code if resp else 'No response'}")
    
    # Test 4: Empty cart checkout
    print("\n4. Testing POST /checkout/session (empty cart)...")
    # Clear cart first
    resp = make_request("GET", "/cart", token=customer_token)
    if resp and resp.status_code == 200:
        cart = resp.json()
        for item in cart.get("items", []):
            make_request("DELETE", f"/cart/item/{item['item_id']}", token=customer_token)
    
    resp = make_request("POST", "/checkout/session", token=customer_token, json_data={
        "origin_url": "http://localhost:3000"
    })
    
    if resp and resp.status_code == 400:
        print("✅ Empty cart checkout correctly rejected with 400")
    else:
        print(f"❌ Empty cart should return 400, got: {resp.status_code if resp else 'No response'}")

def test_orders():
    """Test orders endpoint"""
    print("\n" + "="*60)
    print("TESTING ORDERS ENDPOINTS")
    print("="*60)
    
    if not customer_token:
        print("❌ Skipping orders tests: missing token")
        return
    
    print("\n1. Testing GET /orders...")
    resp = make_request("GET", "/orders", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Orders retrieved: {len(data)} orders")
    else:
        print(f"❌ Orders retrieval failed: {resp.status_code if resp else 'No response'}")

def test_wishlist():
    """Test wishlist endpoints"""
    print("\n" + "="*60)
    print("TESTING WISHLIST ENDPOINTS")
    print("="*60)
    
    if not customer_token or not test_product_id:
        print("❌ Skipping wishlist tests: missing token or product_id")
        return
    
    # Test 1: Check wishlist (should be false initially)
    print(f"\n1. Testing GET /wishlist/check/{test_product_id}...")
    resp = make_request("GET", f"/wishlist/check/{test_product_id}", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if "in_wishlist" in data:
            print(f"✅ Wishlist check: in_wishlist={data['in_wishlist']}")
        else:
            print(f"❌ Wishlist check missing in_wishlist field")
    else:
        print(f"❌ Wishlist check failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Add to wishlist
    print(f"\n2. Testing POST /wishlist...")
    resp = make_request("POST", "/wishlist", token=customer_token, json_data={
        "product_id": test_product_id,
        "item_type": "product"
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if data.get("in_wishlist") == True:
            required_fields = ["title", "image", "price"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"❌ Wishlist item missing fields: {missing}")
            else:
                print(f"✅ Added to wishlist: {data['title']}")
        else:
            print(f"❌ Wishlist add failed: in_wishlist not true")
    else:
        print(f"❌ Wishlist add failed: {resp.status_code if resp else 'No response'}")
    
    # Test 3: Get wishlist
    print(f"\n3. Testing GET /wishlist...")
    resp = make_request("GET", "/wishlist", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            if data:
                item = data[0]
                required_fields = ["item_id", "item_type", "title", "image", "price"]
                missing = [f for f in required_fields if f not in item]
                if missing:
                    print(f"❌ Wishlist item missing fields: {missing}")
                else:
                    print(f"✅ Wishlist retrieved: {len(data)} items")
            else:
                print(f"✅ Wishlist retrieved: 0 items")
        else:
            print(f"❌ Wishlist should be a list: {type(data)}")
    else:
        print(f"❌ Wishlist retrieval failed: {resp.status_code if resp else 'No response'}")
    
    # Test 4: Toggle wishlist (remove)
    print(f"\n4. Testing POST /wishlist/toggle...")
    resp = make_request("POST", "/wishlist/toggle", token=customer_token, json_data={
        "item_type": "product",
        "item_id": test_product_id
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if data.get("in_wishlist") == False:
            print(f"✅ Toggled off wishlist: in_wishlist=false")
        else:
            print(f"❌ Toggle failed: in_wishlist should be false")
    else:
        print(f"❌ Wishlist toggle failed: {resp.status_code if resp else 'No response'}")
    
    # Add back for delete test
    make_request("POST", "/wishlist", token=customer_token, json_data={
        "product_id": test_product_id,
        "item_type": "product"
    })
    
    # Test 5: Delete from wishlist
    print(f"\n5. Testing DELETE /wishlist/{test_product_id}...")
    resp = make_request("DELETE", f"/wishlist/{test_product_id}", token=customer_token)
    
    if resp and resp.status_code == 200:
        print(f"✅ Deleted from wishlist")
    else:
        print(f"❌ Wishlist delete failed: {resp.status_code if resp else 'No response'}")

def test_resale():
    """Test resale/marketplace endpoints"""
    global test_listing_id
    
    print("\n" + "="*60)
    print("TESTING RESALE ENDPOINTS")
    print("="*60)
    
    if not customer_token:
        print("❌ Skipping resale tests: missing token")
        return
    
    # Test 1: Create listing
    print("\n1. Testing POST /listings...")
    resp = make_request("POST", "/listings", token=customer_token, json_data={
        "title": "Test Resale Item",
        "price": 49.99,
        "condition": "good",
        "description": "A great pre-owned item for testing"
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        test_listing_id = data.get("id")
        print(f"✅ Listing created: {data.get('title')} - ${data.get('price')}")
    else:
        print(f"❌ Listing creation failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Get all listings
    print("\n2. Testing GET /listings...")
    resp = make_request("GET", "/listings")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            if data:
                listing = data[0]
                required_fields = ["id", "name", "image"]
                missing = [f for f in required_fields if f not in listing]
                if missing:
                    print(f"❌ Listing missing alias fields: {missing}")
                else:
                    print(f"✅ Listings retrieved: {len(data)} listings")
            else:
                print(f"✅ Listings retrieved: 0 listings")
        else:
            print(f"❌ Listings should be a list")
    else:
        print(f"❌ Listings retrieval failed: {resp.status_code if resp else 'No response'}")
    
    # Test 3: Get single listing
    if test_listing_id:
        print(f"\n3. Testing GET /listings/{test_listing_id}...")
        resp = make_request("GET", f"/listings/{test_listing_id}")
        
        if resp and resp.status_code == 200:
            data = resp.json()
            required_fields = ["id", "name", "image"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"❌ Listing detail missing alias fields: {missing}")
            else:
                print(f"✅ Listing detail: {data.get('title')}")
        else:
            print(f"❌ Listing detail failed: {resp.status_code if resp else 'No response'}")
    
    # Test 4: Get my listings
    print("\n4. Testing GET /my/listings...")
    resp = make_request("GET", "/my/listings", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ My listings: {len(data)} listings")
    else:
        print(f"❌ My listings failed: {resp.status_code if resp else 'No response'}")
    
    # Test 5: Get seller stats
    print("\n5. Testing GET /seller/stats...")
    resp = make_request("GET", "/seller/stats", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Seller stats: {data}")
    else:
        print(f"❌ Seller stats failed: {resp.status_code if resp else 'No response'}")
    
    # Test 6: Get seller profile
    print("\n6. Testing GET /seller/profile...")
    resp = make_request("GET", "/seller/profile", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Seller profile: {data.get('store_name')}")
    else:
        print(f"❌ Seller profile failed: {resp.status_code if resp else 'No response'}")
    
    # Test 7: Get seller balance
    print("\n7. Testing GET /seller/balance...")
    resp = make_request("GET", "/seller/balance", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Seller balance: ${data.get('available', 0)}")
    else:
        print(f"❌ Seller balance failed: {resp.status_code if resp else 'No response'}")

def test_raffle():
    """Test raffle endpoints"""
    print("\n" + "="*60)
    print("TESTING RAFFLE ENDPOINTS")
    print("="*60)
    
    # Test 1: Get current raffle
    print("\n1. Testing GET /raffle/current...")
    resp = make_request("GET", "/raffle/current")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if "entry_count" in data:
            print(f"✅ Current raffle: {data.get('name')} - {data['entry_count']} entries")
        else:
            print(f"❌ Raffle missing entry_count field")
    else:
        print(f"❌ Current raffle failed: {resp.status_code if resp else 'No response'}")
    
    if not customer_token:
        print("⚠️  Skipping raffle entry tests: missing token")
        return
    
    # Test 2: Enter raffle
    print("\n2. Testing POST /raffle/enter...")
    resp = make_request("POST", "/raffle/enter", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if data.get("entered") == True:
            print(f"✅ Raffle entry: entered=true, already_entered={data.get('already_entered')}")
        else:
            print(f"❌ Raffle entry failed: entered not true")
    else:
        print(f"❌ Raffle entry failed: {resp.status_code if resp else 'No response'}")
    
    # Test 3: Enter again (should return already_entered)
    print("\n3. Testing POST /raffle/enter (second time)...")
    resp = make_request("POST", "/raffle/enter", token=customer_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if data.get("already_entered") == True:
            print(f"✅ Second entry: already_entered=true")
        else:
            print(f"❌ Second entry should have already_entered=true")
    else:
        print(f"❌ Second raffle entry failed: {resp.status_code if resp else 'No response'}")

def test_chat():
    """Test chat endpoints"""
    print("\n" + "="*60)
    print("TESTING CHAT ENDPOINTS")
    print("="*60)
    
    # Test 1: Get messages
    print("\n1. Testing GET /chat/messages...")
    resp = make_request("GET", "/chat/messages")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Chat messages: {len(data)} messages")
    else:
        print(f"❌ Chat messages failed: {resp.status_code if resp else 'No response'}")
    
    if not customer_token:
        print("⚠️  Skipping chat post test: missing token")
        return
    
    # Test 2: Post message
    print("\n2. Testing POST /chat/messages...")
    resp = make_request("POST", "/chat/messages", token=customer_token, json_data={
        "text": "Hello from the test suite!"
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Message posted: {data.get('text')}")
    else:
        print(f"❌ Message post failed: {resp.status_code if resp else 'No response'}")

def test_newsletter():
    """Test newsletter endpoint"""
    print("\n" + "="*60)
    print("TESTING NEWSLETTER ENDPOINTS")
    print("="*60)
    
    print("\n1. Testing POST /newsletter...")
    resp = make_request("POST", "/newsletter", json_data={
        "email": random_email()
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        print(f"✅ Newsletter subscription: {data.get('message')}")
    else:
        print(f"❌ Newsletter subscription failed: {resp.status_code if resp else 'No response'}")

def test_admin():
    """Test admin endpoints"""
    print("\n" + "="*60)
    print("TESTING ADMIN ENDPOINTS")
    print("="*60)
    
    if not admin_token or not customer_token:
        print("❌ Skipping admin tests: missing tokens")
        return
    
    # Test 1: Admin metrics with admin token
    print("\n1. Testing GET /admin/metrics (as admin)...")
    resp = make_request("GET", "/admin/metrics", token=admin_token)
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if "revenue" in data and "commissions" in data:
            print(f"✅ Admin metrics: revenue=${data['revenue']}, commissions=${data['commissions']}")
        else:
            print(f"❌ Admin metrics missing fields: {data}")
    else:
        print(f"❌ Admin metrics failed: {resp.status_code if resp else 'No response'}")
    
    # Test 2: Admin metrics with customer token (should fail)
    print("\n2. Testing GET /admin/metrics (as customer)...")
    resp = make_request("GET", "/admin/metrics", token=customer_token)
    
    if resp and resp.status_code == 403:
        print("✅ Customer correctly denied access with 403")
    else:
        print(f"❌ Customer should be denied with 403, got: {resp.status_code if resp else 'No response'}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LCs THE FURY ZONE - BACKEND API TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print(f"Customer: {CUSTOMER_EMAIL}")
    
    # Run tests in order
    if not test_auth():
        print("\n❌ Auth tests failed, cannot continue")
        return
    
    test_catalog()
    test_cart()
    test_coupons()
    test_addresses()
    test_checkout()
    test_orders()
    test_wishlist()
    test_resale()
    test_raffle()
    test_chat()
    test_newsletter()
    test_admin()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
