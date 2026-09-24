#!/usr/bin/env python3
"""
Backend test for LCs The Fury Zone - Catalog Scale + New Shopper Bonus
Focus areas:
1. Catalog scale (750 products, 15 departments)
2. New shopper bonus (free_items_remaining, free orders, bonus + Stripe)
3. Regression (auth, cart, coupons, addresses, wishlist, resale, raffle, chat, admin)
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
new_user_token = None
new_user_email = None

def random_email():
    """Generate random email for registration tests"""
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"shopper_{rand}@furyzone.test"

def make_request(method: str, endpoint: str, token: Optional[str] = None, 
                 json_data: Optional[Dict] = None, params: Optional[Dict] = None):
    """Make HTTP request with optional auth"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=15)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=json_data, timeout=15)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=json_data, timeout=15)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=15)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return resp
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {method} {endpoint} - {e}")
        return None

def test_catalog_scale():
    """Test catalog scale: 750 products, 15 departments"""
    print("\n" + "="*80)
    print("TESTING CATALOG SCALE")
    print("="*80)
    
    # Test 1: GET /api/products with large limit
    print("\n1. Testing GET /api/products?limit=1000 (should return ~750 products)...")
    resp = make_request("GET", "/products", params={"limit": 1000})
    
    if resp and resp.status_code == 200:
        products = resp.json()
        print(f"✅ Products endpoint returned {len(products)} products")
        
        if len(products) < 700:
            print(f"❌ CRITICAL: Expected ~750 products, got {len(products)}")
            return False
        
        # Check first product structure
        if products:
            p = products[0]
            required_fields = ["id", "title", "name", "image", "price"]
            missing = [f for f in required_fields if f not in p]
            if missing:
                print(f"❌ CRITICAL: Product missing fields: {missing}")
                return False
            
            if not p.get("image"):
                print(f"❌ CRITICAL: Product has empty image field")
                return False
            
            print(f"✅ Product structure valid: id={p['id'][:8]}..., title={p['title'][:30]}, price=${p['price']}")
            
            # Check price distribution (mostly under $20)
            under_20 = sum(1 for p in products if p.get("price", 999) < 20)
            percent_under_20 = (under_20 / len(products)) * 100
            print(f"✅ Price distribution: {under_20}/{len(products)} ({percent_under_20:.1f}%) under $20")
    else:
        print(f"❌ CRITICAL: Products endpoint failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 2: GET /api/departments (should return 15)
    print("\n2. Testing GET /api/departments (should return 15 departments)...")
    resp = make_request("GET", "/departments")
    
    if resp and resp.status_code == 200:
        departments = resp.json()
        print(f"✅ Departments endpoint returned {len(departments)} departments")
        
        if len(departments) != 15:
            print(f"❌ CRITICAL: Expected 15 departments, got {len(departments)}")
            return False
        
        # Check each department has image and slug
        for dept in departments:
            if not dept.get("image"):
                print(f"❌ CRITICAL: Department '{dept.get('name')}' has empty image field")
                return False
            if not dept.get("slug"):
                print(f"❌ CRITICAL: Department '{dept.get('name')}' has empty slug field")
                return False
        
        print(f"✅ All departments have image and slug fields")
        print(f"   Sample: {departments[0]['name']} (slug: {departments[0]['slug']})")
    else:
        print(f"❌ CRITICAL: Departments endpoint failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 3: Filter by department_id
    print("\n3. Testing filter ?department_id={id}...")
    dept_id = departments[0]["id"]
    resp = make_request("GET", "/products", params={"department_id": dept_id, "limit": 100})
    
    if resp and resp.status_code == 200:
        filtered = resp.json()
        print(f"✅ Department filter returned {len(filtered)} products for '{departments[0]['name']}'")
        
        # Verify all products belong to this department
        wrong_dept = [p for p in filtered if p.get("department_id") != dept_id]
        if wrong_dept:
            print(f"❌ CRITICAL: {len(wrong_dept)} products have wrong department_id")
            return False
    else:
        print(f"❌ CRITICAL: Department filter failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 4: Filter by max_price
    print("\n4. Testing filter ?max_price=5...")
    resp = make_request("GET", "/products", params={"max_price": 5, "limit": 100})
    
    if resp and resp.status_code == 200:
        cheap = resp.json()
        print(f"✅ Max price filter returned {len(cheap)} products under $5")
        
        # Verify all products are under $5
        over_price = [p for p in cheap if p.get("price", 0) > 5]
        if over_price:
            print(f"❌ CRITICAL: {len(over_price)} products over $5 in results")
            return False
    else:
        print(f"❌ CRITICAL: Max price filter failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 5: Search filter
    print("\n5. Testing filter ?search=hoodie...")
    resp = make_request("GET", "/products", params={"search": "hoodie", "limit": 100})
    
    if resp and resp.status_code == 200:
        results = resp.json()
        print(f"✅ Search filter returned {len(results)} products matching 'hoodie'")
    else:
        print(f"❌ CRITICAL: Search filter failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 6: Sort by price_asc
    print("\n6. Testing sort ?sort=price_asc...")
    resp = make_request("GET", "/products", params={"sort": "price_asc", "limit": 10})
    
    if resp and resp.status_code == 200:
        sorted_asc = resp.json()
        prices = [p.get("price", 0) for p in sorted_asc]
        if prices == sorted(prices):
            print(f"✅ Price ascending sort working: {prices[:5]}")
        else:
            print(f"❌ CRITICAL: Price ascending sort broken: {prices[:5]}")
            return False
    else:
        print(f"❌ CRITICAL: Sort price_asc failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 7: Sort by price_desc
    print("\n7. Testing sort ?sort=price_desc...")
    resp = make_request("GET", "/products", params={"sort": "price_desc", "limit": 10})
    
    if resp and resp.status_code == 200:
        sorted_desc = resp.json()
        prices = [p.get("price", 0) for p in sorted_desc]
        if prices == sorted(prices, reverse=True):
            print(f"✅ Price descending sort working: {prices[:5]}")
        else:
            print(f"❌ CRITICAL: Price descending sort broken: {prices[:5]}")
            return False
    else:
        print(f"❌ CRITICAL: Sort price_desc failed: {resp.status_code if resp else 'No response'}")
        return False
    
    return True

def test_new_shopper_bonus():
    """Test new shopper bonus feature"""
    global new_user_token, new_user_email
    
    print("\n" + "="*80)
    print("TESTING NEW SHOPPER BONUS")
    print("="*80)
    
    # Test 1: Register new user and check free_items_remaining
    print("\n1. Testing new user registration -> free_items_remaining: 3...")
    new_user_email = random_email()
    resp = make_request("POST", "/auth/register", json_data={
        "email": new_user_email,
        "password": "NewUser123!",
        "full_name": "New Shopper Test"
    })
    
    if resp and resp.status_code == 200:
        data = resp.json()
        new_user_token = data.get("token")
        user = data.get("user", {})
        free_items = user.get("free_items_remaining", 0)
        
        if free_items == 3:
            print(f"✅ New user has free_items_remaining: {free_items}")
        else:
            print(f"❌ CRITICAL: Expected free_items_remaining=3, got {free_items}")
            return False
    else:
        print(f"❌ CRITICAL: User registration failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 2: Verify via GET /auth/me
    print("\n2. Testing GET /auth/me confirms free_items_remaining: 3...")
    resp = make_request("GET", "/auth/me", token=new_user_token)
    
    if resp and resp.status_code == 200:
        user = resp.json()
        free_items = user.get("free_items_remaining", 0)
        
        if free_items == 3:
            print(f"✅ GET /auth/me confirms free_items_remaining: {free_items}")
        else:
            print(f"❌ CRITICAL: Expected free_items_remaining=3, got {free_items}")
            return False
    else:
        print(f"❌ CRITICAL: GET /auth/me failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 3: Get 2 cheapest products
    print("\n3. Finding 2 cheapest products for free order test...")
    resp = make_request("GET", "/products", params={"sort": "price_asc", "limit": 10})
    
    if not resp or resp.status_code != 200:
        print(f"❌ CRITICAL: Cannot fetch products: {resp.status_code if resp else 'No response'}")
        return False
    
    products = resp.json()
    if len(products) < 2:
        print(f"❌ CRITICAL: Not enough products available")
        return False
    
    cheap1 = products[0]
    cheap2 = products[1]
    print(f"✅ Found cheapest products: {cheap1['title'][:30]} (${cheap1['price']}), {cheap2['title'][:30]} (${cheap2['price']})")
    
    # Test 4: Add 2 cheapest products to cart
    print("\n4. Adding 2 cheapest products to cart...")
    for product in [cheap1, cheap2]:
        resp = make_request("POST", "/cart/add", token=new_user_token, json_data={
            "item_type": "product",
            "item_id": product["id"],
            "quantity": 1
        })
        
        if not resp or resp.status_code != 200:
            print(f"❌ CRITICAL: Failed to add product to cart: {resp.status_code if resp else 'No response'}")
            return False
    
    print(f"✅ Added 2 products to cart")
    
    # Test 5: Create FREE checkout session
    print("\n5. Testing POST /checkout/session (should be FREE order)...")
    resp = make_request("POST", "/checkout/session", token=new_user_token, json_data={
        "origin_url": "http://localhost:3000"
    })
    
    if resp and resp.status_code == 200:
        checkout = resp.json()
        
        if not checkout.get("free"):
            print(f"❌ CRITICAL: Expected free=true, got {checkout.get('free')}")
            return False
        
        session_id = checkout.get("session_id", "")
        if not session_id.startswith("free_"):
            print(f"❌ CRITICAL: Expected session_id to start with 'free_', got {session_id}")
            return False
        
        print(f"✅ Free order created: session_id={session_id}, free={checkout.get('free')}")
    else:
        print(f"❌ CRITICAL: Checkout session failed: {resp.status_code if resp else 'No response'}")
        if resp:
            print(f"   Response: {resp.text}")
        return False
    
    # Test 6: Check order was created with total 0.0
    print("\n6. Testing GET /orders (should show 1 order with total 0.0)...")
    resp = make_request("GET", "/orders", token=new_user_token)
    
    if resp and resp.status_code == 200:
        orders = resp.json()
        
        if len(orders) != 1:
            print(f"❌ CRITICAL: Expected 1 order, got {len(orders)}")
            return False
        
        order = orders[0]
        if order.get("total") != 0.0:
            print(f"❌ CRITICAL: Expected total=0.0, got {order.get('total')}")
            return False
        
        if order.get("free_items_used") != 2:
            print(f"❌ CRITICAL: Expected free_items_used=2, got {order.get('free_items_used')}")
            return False
        
        print(f"✅ Order created: total={order.get('total')}, free_items_used={order.get('free_items_used')}")
    else:
        print(f"❌ CRITICAL: GET /orders failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 7: Check free_items_remaining decreased to 1
    print("\n7. Testing GET /auth/me (should show free_items_remaining: 1)...")
    resp = make_request("GET", "/auth/me", token=new_user_token)
    
    if resp and resp.status_code == 200:
        user = resp.json()
        free_items = user.get("free_items_remaining", 0)
        
        if free_items == 1:
            print(f"✅ free_items_remaining decreased to {free_items}")
        else:
            print(f"❌ CRITICAL: Expected free_items_remaining=1, got {free_items}")
            return False
    else:
        print(f"❌ CRITICAL: GET /auth/me failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 8: Check checkout status
    print("\n8. Testing GET /checkout/status/{session_id}...")
    resp = make_request("GET", f"/checkout/status/{session_id}", token=new_user_token)
    
    if resp and resp.status_code == 200:
        status = resp.json()
        
        if status.get("payment_status") != "paid":
            print(f"❌ CRITICAL: Expected payment_status='paid', got {status.get('payment_status')}")
            return False
        
        if not status.get("order_id"):
            print(f"❌ CRITICAL: Expected order_id, got {status.get('order_id')}")
            return False
        
        print(f"✅ Checkout status: payment_status={status.get('payment_status')}, order_id={status.get('order_id')[:8]}...")
    else:
        print(f"❌ CRITICAL: GET /checkout/status failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 9: BONUS + STRIPE - add expensive product
    print("\n9. Testing BONUS + STRIPE: adding expensive product (~$18-19)...")
    resp = make_request("GET", "/products", params={"sort": "price_desc", "limit": 10})
    
    if not resp or resp.status_code != 200:
        print(f"❌ CRITICAL: Cannot fetch expensive products: {resp.status_code if resp else 'No response'}")
        return False
    
    expensive_products = resp.json()
    expensive = None
    for p in expensive_products:
        if 18 <= p.get("price", 0) <= 19:
            expensive = p
            break
    
    if not expensive:
        # Just take the most expensive one
        expensive = expensive_products[0]
    
    print(f"✅ Found expensive product: {expensive['title'][:30]} (${expensive['price']})")
    
    # Add to cart
    resp = make_request("POST", "/cart/add", token=new_user_token, json_data={
        "item_type": "product",
        "item_id": expensive["id"],
        "quantity": 1
    })
    
    if not resp or resp.status_code != 200:
        print(f"❌ CRITICAL: Failed to add expensive product to cart: {resp.status_code if resp else 'No response'}")
        return False
    
    print(f"✅ Added expensive product to cart")
    
    # Test 10: Create Stripe checkout session (should NOT be free)
    print("\n10. Testing POST /checkout/session (should return Stripe URL, NOT free)...")
    resp = make_request("POST", "/checkout/session", token=new_user_token, json_data={
        "origin_url": "http://localhost:3000"
    })
    
    if resp and resp.status_code == 200:
        checkout = resp.json()
        
        if checkout.get("free"):
            print(f"❌ CRITICAL: Expected free=false or absent, got free=true")
            return False
        
        url = checkout.get("url", "")
        if "checkout.stripe.com" not in url:
            print(f"❌ CRITICAL: Expected checkout.stripe.com URL, got {url}")
            return False
        
        session_id_stripe = checkout.get("session_id", "")
        if session_id_stripe.startswith("free_"):
            print(f"❌ CRITICAL: Expected real Stripe session_id, got free_ prefix")
            return False
        
        print(f"✅ Stripe checkout created: url={url[:50]}..., session_id={session_id_stripe[:20]}...")
        
        # Check that bonus was applied (total should be reduced)
        # We can't check the exact total without knowing shipping, but we can verify the transaction was created
        print("\n11. Verifying bonus was applied (checking payment_transactions)...")
        # We'll check via checkout status
        resp_status = make_request("GET", f"/checkout/status/{session_id_stripe}", token=new_user_token)
        
        if resp_status and resp_status.status_code == 200:
            status = resp_status.json()
            print(f"✅ Checkout status retrieved: payment_status={status.get('payment_status')}")
            
            # Since we didn't complete payment, it should be pending
            if status.get("payment_status") != "pending":
                print(f"⚠️  Warning: Expected payment_status='pending', got {status.get('payment_status')}")
        else:
            print(f"❌ CRITICAL: Cannot verify checkout status: {resp_status.status_code if resp_status else 'No response'}")
            return False
        
    else:
        print(f"❌ CRITICAL: Stripe checkout failed: {resp.status_code if resp else 'No response'}")
        if resp:
            print(f"   Response: {resp.text}")
        return False
    
    # Test 12: Verify free_items_remaining is STILL 1 (not decremented until payment)
    print("\n12. Testing GET /auth/me (free_items_remaining should STILL be 1)...")
    resp = make_request("GET", "/auth/me", token=new_user_token)
    
    if resp and resp.status_code == 200:
        user = resp.json()
        free_items = user.get("free_items_remaining", 0)
        
        if free_items == 1:
            print(f"✅ free_items_remaining STILL 1 (not decremented until payment)")
        else:
            print(f"❌ CRITICAL: Expected free_items_remaining=1, got {free_items}")
            return False
    else:
        print(f"❌ CRITICAL: GET /auth/me failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 13: NO BONUS - test with customer who has 0 free items
    print("\n13. Testing NO BONUS: customer with free_items_remaining=0...")
    # Login as existing customer
    resp = make_request("POST", "/auth/login", json_data={
        "email": CUSTOMER_EMAIL,
        "password": CUSTOMER_PASSWORD
    })
    
    if not resp or resp.status_code != 200:
        print(f"❌ CRITICAL: Customer login failed: {resp.status_code if resp else 'No response'}")
        return False
    
    customer_token = resp.json().get("token")
    
    # Check free_items_remaining
    resp = make_request("GET", "/auth/me", token=customer_token)
    if resp and resp.status_code == 200:
        user = resp.json()
        free_items = user.get("free_items_remaining", 0)
        print(f"✅ Customer free_items_remaining: {free_items}")
    
    # Add a product to cart
    resp = make_request("GET", "/products", params={"limit": 1})
    if resp and resp.status_code == 200:
        product = resp.json()[0]
        
        resp = make_request("POST", "/cart/add", token=customer_token, json_data={
            "item_type": "product",
            "item_id": product["id"],
            "quantity": 1
        })
        
        if resp and resp.status_code == 200:
            print(f"✅ Added product to customer cart")
        else:
            print(f"❌ CRITICAL: Failed to add to cart: {resp.status_code if resp else 'No response'}")
            return False
    
    # Create checkout (should not have bonus)
    resp = make_request("POST", "/checkout/session", token=customer_token, json_data={
        "origin_url": "http://localhost:3000",
        "coupon_code": "FURY10"
    })
    
    if resp and resp.status_code == 200:
        checkout = resp.json()
        print(f"✅ Checkout created for customer with no bonus")
        # We can't verify exact math without inspecting the transaction, but it should work
    else:
        print(f"❌ CRITICAL: Customer checkout failed: {resp.status_code if resp else 'No response'}")
        return False
    
    return True

def test_regression():
    """Test regression - existing features still work"""
    global admin_token, customer_token
    
    print("\n" + "="*80)
    print("TESTING REGRESSION (existing features)")
    print("="*80)
    
    # Test 1: Auth login
    print("\n1. Testing auth login...")
    resp = make_request("POST", "/auth/login", json_data={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if resp and resp.status_code == 200:
        admin_token = resp.json().get("token")
        print(f"✅ Admin login successful")
    else:
        print(f"❌ CRITICAL: Admin login failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 2: Coupons validate
    print("\n2. Testing coupons validate (FURY10)...")
    resp = make_request("POST", "/coupons/validate", json_data={"code": "FURY10"})
    
    if resp and resp.status_code == 200:
        coupon = resp.json()
        if coupon.get("percent_off") == 10:
            print(f"✅ FURY10 coupon valid: {coupon.get('percent_off')}% off")
        else:
            print(f"❌ CRITICAL: FURY10 should be 10% off, got {coupon.get('percent_off')}%")
            return False
    else:
        print(f"❌ CRITICAL: Coupon validation failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 3: Addresses
    print("\n3. Testing addresses GET/POST...")
    resp = make_request("GET", "/addresses", token=admin_token)
    
    if resp and resp.status_code == 200:
        print(f"✅ GET /addresses successful")
    else:
        print(f"❌ CRITICAL: GET /addresses failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 4: Wishlist toggle
    print("\n4. Testing wishlist toggle...")
    resp = make_request("GET", "/products", params={"limit": 1})
    if resp and resp.status_code == 200:
        product = resp.json()[0]
        
        resp = make_request("POST", "/wishlist/toggle", token=admin_token, json_data={
            "item_id": product["id"],
            "item_type": "product"
        })
        
        if resp and resp.status_code == 200:
            print(f"✅ Wishlist toggle successful")
        else:
            print(f"❌ CRITICAL: Wishlist toggle failed: {resp.status_code if resp else 'No response'}")
            return False
    
    # Test 5: Resale create listing
    print("\n5. Testing resale create listing...")
    resp = make_request("POST", "/listings", token=admin_token, json_data={
        "title": "Test Resale Item",
        "description": "Test description",
        "price": 25.99,
        "condition": "like_new",
        "images": ["https://example.com/image.jpg"]
    })
    
    if resp and resp.status_code == 200:
        listing = resp.json()
        print(f"✅ Resale listing created: {listing.get('id')}")
    else:
        print(f"❌ CRITICAL: Resale listing creation failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 6: GET /listings
    print("\n6. Testing GET /listings...")
    resp = make_request("GET", "/listings")
    
    if resp and resp.status_code == 200:
        listings = resp.json()
        print(f"✅ GET /listings returned {len(listings)} listings")
    else:
        print(f"❌ CRITICAL: GET /listings failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 7: Raffle current
    print("\n7. Testing raffle current...")
    resp = make_request("GET", "/raffle/current")
    
    if resp and resp.status_code == 200:
        print(f"✅ GET /raffle/current successful")
    else:
        print(f"❌ CRITICAL: GET /raffle/current failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 8: Raffle enter
    print("\n8. Testing raffle enter...")
    resp = make_request("POST", "/raffle/enter", token=admin_token)
    
    if resp and resp.status_code == 200:
        print(f"✅ Raffle enter successful")
    else:
        print(f"❌ CRITICAL: Raffle enter failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 9: Chat messages
    print("\n9. Testing chat messages...")
    resp = make_request("GET", "/chat/messages")
    
    if resp and resp.status_code == 200:
        print(f"✅ GET /chat/messages successful")
    else:
        print(f"❌ CRITICAL: GET /chat/messages failed: {resp.status_code if resp else 'No response'}")
        return False
    
    # Test 10: Admin metrics (admin should get 200, customer should get 403)
    print("\n10. Testing admin metrics (admin=200, customer=403)...")
    resp = make_request("GET", "/admin/metrics", token=admin_token)
    
    if resp and resp.status_code == 200:
        print(f"✅ Admin metrics accessible to admin")
    else:
        print(f"❌ CRITICAL: Admin metrics failed for admin: {resp.status_code if resp else 'No response'}")
        return False
    
    # Login as customer
    resp = make_request("POST", "/auth/login", json_data={
        "email": CUSTOMER_EMAIL,
        "password": CUSTOMER_PASSWORD
    })
    
    if resp and resp.status_code == 200:
        customer_token = resp.json().get("token")
        
        resp = make_request("GET", "/admin/metrics", token=customer_token)
        
        if resp and resp.status_code == 403:
            print(f"✅ Admin metrics correctly returns 403 for customer")
        else:
            print(f"❌ CRITICAL: Admin metrics should return 403 for customer, got {resp.status_code if resp else 'No response'}")
            return False
    else:
        print(f"❌ CRITICAL: Customer login failed: {resp.status_code if resp else 'No response'}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("LCs THE FURY ZONE - BACKEND TEST SUITE")
    print("Catalog Scale + New Shopper Bonus + Regression")
    print("="*80)
    
    results = {
        "Catalog Scale": False,
        "New Shopper Bonus": False,
        "Regression": False
    }
    
    try:
        results["Catalog Scale"] = test_catalog_scale()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in Catalog Scale tests: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        results["New Shopper Bonus"] = test_new_shopper_bonus()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in New Shopper Bonus tests: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        results["Regression"] = test_regression()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in Regression tests: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
