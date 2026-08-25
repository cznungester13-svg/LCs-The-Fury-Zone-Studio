"""Backend API tests for LC Multi-Dept Resale Marketplace."""
import os
import time
import uuid

import pytest
import requests
from dotenv import dotenv_values

frontend_env = dotenv_values("/app/frontend/.env")
base_url = os.environ.get("REACT_APP_BACKEND_URL") or frontend_env.get("REACT_APP_BACKEND_URL")
if not base_url:
    raise RuntimeError("REACT_APP_BACKEND_URL missing")
BASE_URL = base_url.rstrip("/")
API = f"{BASE_URL}/api"

ADMIN = {"email": "admin@lcfury.com", "password": "admin123"}


@pytest.fixture(scope="session")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def auth_client():
    """Session logged in as a freshly registered user."""
    s = requests.Session()
    email = f"TEST_{uuid.uuid4().hex[:10]}@example.com"
    r = s.post(f"{API}/auth/register", json={"name": "TEST User", "email": email, "password": "test1234"})
    if r.status_code != 200:
        pytest.fail(f"register failed {r.status_code}: {r.text[:300]}")
    s.email = email
    return s


# ---------------------------------------------------------------- Health & seed
class TestHealthSeed:
    def test_health(self, client):
        r = client.get(f"{API}/health")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "healthy"
        assert d["products"] == 300, f"expected 300 products got {d['products']}"

    def test_departments(self, client):
        r = client.get(f"{API}/departments")
        assert r.status_code == 200
        deps = r.json()
        assert len(deps) == 6
        slugs = {d["slug"] for d in deps}
        assert slugs == {"fashion", "electronics", "home", "books", "sports", "toys"}
        for d in deps:
            assert d["count"] == 50, f"{d['slug']} has {d['count']} items"
            assert d["image"].startswith("http")
            assert d["name"] and d["tagline"]


# ---------------------------------------------------------------- Products
class TestProducts:
    def test_default_listing(self, client):
        r = client.get(f"{API}/products")
        assert r.status_code == 200
        d = r.json()
        assert d["total"] == 300
        assert len(d["items"]) == 24
        assert d["pages"] == 13
        p = d["items"][0]
        for k in ("id", "name", "price", "image", "department", "category", "rating"):
            assert k in p, f"missing field {k}"
        assert p["image"].startswith("http")

    @pytest.mark.parametrize("dept", ["fashion", "electronics", "home", "books", "sports", "toys"])
    def test_department_filter(self, client, dept):
        r = client.get(f"{API}/products", params={"department": dept, "limit": 50})
        assert r.status_code == 200
        d = r.json()
        assert d["total"] == 50
        assert len(d["items"]) == 50
        assert all(i["department"] == dept for i in d["items"])
        # every product must have a non-empty image url
        assert all(i.get("image", "").startswith("http") for i in d["items"])

    def test_low_prices(self, client):
        r = client.get(f"{API}/products", params={"limit": 300})
        items = r.json()["items"]
        assert len(items) == 300
        assert all(i["price"] > 0 for i in items)
        assert max(i["price"] for i in items) < 100, "prices should be 'super low' (<100)"

    def test_search(self, client):
        listing = client.get(f"{API}/products", params={"limit": 1}).json()["items"][0]
        term = listing["name"].split()[0]
        r = client.get(f"{API}/products", params={"search": term})
        assert r.status_code == 200
        d = r.json()
        assert d["total"] >= 1
        assert all(term.lower() in i["name"].lower() for i in d["items"])

    def test_search_no_match(self, client):
        r = client.get(f"{API}/products", params={"search": "zzzznotarealproduct"})
        assert r.status_code == 200
        assert r.json()["total"] == 0
        assert r.json()["items"] == []

    def test_sort_price_asc(self, client):
        items = client.get(f"{API}/products", params={"sort": "price_asc", "limit": 30}).json()["items"]
        prices = [i["price"] for i in items]
        assert prices == sorted(prices)

    def test_sort_price_desc(self, client):
        items = client.get(f"{API}/products", params={"sort": "price_desc", "limit": 30}).json()["items"]
        prices = [i["price"] for i in items]
        assert prices == sorted(prices, reverse=True)

    def test_sort_rating(self, client):
        items = client.get(f"{API}/products", params={"sort": "rating", "limit": 30}).json()["items"]
        ratings = [i["rating"] for i in items]
        assert ratings == sorted(ratings, reverse=True)

    def test_pagination(self, client):
        p1 = client.get(f"{API}/products", params={"page": 1, "limit": 10}).json()
        p2 = client.get(f"{API}/products", params={"page": 2, "limit": 10}).json()
        assert p1["total"] == p2["total"] == 300
        assert p1["pages"] == 30
        assert len(p1["items"]) == len(p2["items"]) == 10
        ids1 = {i["id"] for i in p1["items"]}
        ids2 = {i["id"] for i in p2["items"]}
        assert not ids1 & ids2, "pages overlap"

    def test_product_detail_and_related(self, client):
        pid = client.get(f"{API}/products", params={"limit": 1}).json()["items"][0]["id"]
        r = client.get(f"{API}/products/{pid}")
        assert r.status_code == 200
        d = r.json()
        assert d["product"]["id"] == pid
        assert len(d["related"]) == 4
        assert all(x["id"] != pid for x in d["related"])
        assert all(x["department"] == d["product"]["department"] for x in d["related"])

    def test_product_detail_404(self, client):
        r = client.get(f"{API}/products/does-not-exist-123")
        assert r.status_code == 404

    def test_deals(self, client):
        r = client.get(f"{API}/products/deals")
        assert r.status_code == 200
        deals = r.json()
        assert len(deals) == 8
        prices = [d["price"] for d in deals]
        assert prices == sorted(prices)
        cheapest_overall = client.get(
            f"{API}/products", params={"sort": "price_asc", "limit": 8}
        ).json()["items"]
        assert prices == [c["price"] for c in cheapest_overall]


# ---------------------------------------------------------------- Auth
class TestAuth:
    def test_register_sets_cookies(self, client):
        email = f"TEST_{uuid.uuid4().hex[:10]}@example.com"
        r = requests.post(f"{API}/auth/register",
                          json={"name": "TEST Reg", "email": email, "password": "test1234"})
        assert r.status_code == 200
        d = r.json()
        assert d["email"] == email.lower()
        assert d["role"] == "user"
        assert "id" in d and "_id" not in d
        assert "password_hash" not in d
        cookie_hdrs = r.headers.get("set-cookie", "")
        assert "access_token" in cookie_hdrs and "refresh_token" in cookie_hdrs
        assert "HttpOnly" in cookie_hdrs

    def test_register_duplicate(self, client):
        r = requests.post(f"{API}/auth/register",
                          json={"name": "Dup", "email": ADMIN["email"], "password": "whatever1"})
        assert r.status_code == 400

    def test_register_short_password(self, client):
        r = requests.post(f"{API}/auth/register",
                          json={"name": "X", "email": f"TEST_{uuid.uuid4().hex[:6]}@e.com", "password": "12"})
        assert r.status_code == 422

    def test_register_bad_email(self, client):
        r = requests.post(f"{API}/auth/register",
                          json={"name": "X", "email": "not-an-email", "password": "test1234"})
        assert r.status_code == 422

    def test_login_admin(self):
        s = requests.Session()
        r = s.post(f"{API}/auth/login", json=ADMIN)
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        assert d["email"] == ADMIN["email"]
        assert d["role"] == "admin"
        assert "access_token" in s.cookies
        me = s.get(f"{API}/auth/me")
        assert me.status_code == 200
        assert me.json()["email"] == ADMIN["email"]

    def test_login_wrong_password(self, client):
        r = requests.post(f"{API}/auth/login",
                          json={"email": ADMIN["email"], "password": "wrongpass"})
        assert r.status_code == 401

    def test_login_unknown_user(self, client):
        r = requests.post(f"{API}/auth/login",
                          json={"email": "nobody_xyz@example.com", "password": "wrongpass"})
        assert r.status_code == 401

    def test_me_unauthenticated(self, client):
        r = requests.get(f"{API}/auth/me")
        assert r.status_code == 401

    def test_me_invalid_token(self, client):
        r = requests.get(f"{API}/auth/me", headers={"Authorization": "Bearer garbage.token.here"})
        assert r.status_code == 401

    def test_refresh_and_logout(self):
        s = requests.Session()
        s.post(f"{API}/auth/login", json=ADMIN)
        r = s.post(f"{API}/auth/refresh")
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN["email"]
        out = s.post(f"{API}/auth/logout")
        assert out.status_code == 200
        assert not s.cookies.get("access_token")
        assert s.get(f"{API}/auth/me").status_code == 401

    def test_refresh_without_cookie(self):
        r = requests.post(f"{API}/auth/refresh")
        assert r.status_code == 401

    def test_bcrypt_hash_format(self):
        """Password hashes must be bcrypt $2b$ format."""
        from pymongo import MongoClient
        mc = MongoClient(os.environ.get("MONGO_URL", dotenv_values("/app/backend/.env").get("MONGO_URL")))
        dbn = os.environ.get("DB_NAME", dotenv_values("/app/backend/.env").get("DB_NAME"))
        u = mc[dbn].users.find_one({"email": ADMIN["email"]})
        assert u is not None
        assert u["password_hash"].startswith("$2b$"), u["password_hash"][:10]
        mc.close()

    def test_brute_force_lockout(self):
        """Playbook requirement: lockout after 5 failed attempts."""
        email = f"TEST_bf_{uuid.uuid4().hex[:8]}@example.com"
        requests.post(f"{API}/auth/register", json={"name": "BF", "email": email, "password": "test1234"})
        codes = []
        for _ in range(6):
            codes.append(requests.post(f"{API}/auth/login",
                                       json={"email": email, "password": "badpass"}).status_code)
        assert 423 in codes or 429 in codes, f"no lockout after 6 failed logins, codes={codes}"


# ---------------------------------------------------------------- Cart
class TestCart:
    def test_cart_requires_auth(self):
        assert requests.get(f"{API}/cart").status_code == 401
        assert requests.post(f"{API}/cart", json={"product_id": "x", "quantity": 1}).status_code == 401
        assert requests.put(f"{API}/cart", json={"product_id": "x", "quantity": 1}).status_code == 401
        assert requests.delete(f"{API}/cart/x").status_code == 401

    def test_cart_flow(self, auth_client, client):
        items = client.get(f"{API}/products", params={"limit": 2}).json()["items"]
        p1, p2 = items[0], items[1]

        # empty initially
        r = auth_client.get(f"{API}/cart")
        assert r.status_code == 200
        assert r.json()["items"] == []
        assert r.json()["total"] == 0

        # add p1
        r = auth_client.post(f"{API}/cart", json={"product_id": p1["id"], "quantity": 2})
        assert r.status_code == 200
        d = r.json()
        assert len(d["items"]) == 1
        assert d["items"][0]["quantity"] == 2
        assert d["items"][0]["line_total"] == round(p1["price"] * 2, 2)
        assert d["total"] == round(p1["price"] * 2, 2)

        # add p1 again -> quantity merges
        d = auth_client.post(f"{API}/cart", json={"product_id": p1["id"], "quantity": 1}).json()
        assert len(d["items"]) == 1 and d["items"][0]["quantity"] == 3

        # add p2
        d = auth_client.post(f"{API}/cart", json={"product_id": p2["id"], "quantity": 1}).json()
        assert len(d["items"]) == 2
        expected = round(p1["price"] * 3 + p2["price"], 2)
        assert abs(d["total"] - expected) < 0.02

        # GET persists
        g = auth_client.get(f"{API}/cart").json()
        assert len(g["items"]) == 2
        assert abs(g["total"] - expected) < 0.02

        # update quantity
        d = auth_client.put(f"{API}/cart", json={"product_id": p1["id"], "quantity": 1}).json()
        qty = {i["product"]["id"]: i["quantity"] for i in d["items"]}
        assert qty[p1["id"]] == 1

        # delete p2
        d = auth_client.delete(f"{API}/cart/{p2['id']}").json()
        ids = [i["product"]["id"] for i in d["items"]]
        assert p2["id"] not in ids and p1["id"] in ids

        # verify persisted
        g = auth_client.get(f"{API}/cart").json()
        assert len(g["items"]) == 1

    def test_add_invalid_product(self, auth_client):
        r = auth_client.post(f"{API}/cart", json={"product_id": "nope-123", "quantity": 1})
        assert r.status_code == 404

    def test_add_invalid_quantity(self, auth_client, client):
        pid = client.get(f"{API}/products", params={"limit": 1}).json()["items"][0]["id"]
        r = auth_client.post(f"{API}/cart", json={"product_id": pid, "quantity": 0})
        assert r.status_code == 422


# ---------------------------------------------------------------- Orders
class TestOrders:
    def test_orders_require_auth(self):
        assert requests.get(f"{API}/orders").status_code == 401
        assert requests.post(f"{API}/orders", json={"full_name": "a", "address": "b", "city": "c"}).status_code == 401

    def test_checkout_flow(self, client):
        s = requests.Session()
        email = f"TEST_{uuid.uuid4().hex[:10]}@example.com"
        assert s.post(f"{API}/auth/register",
                      json={"name": "TEST Order", "email": email, "password": "test1234"}).status_code == 200

        # empty cart checkout -> 400
        r = s.post(f"{API}/orders", json={"full_name": "A B", "address": "1 St", "city": "NY"})
        assert r.status_code == 400

        p = client.get(f"{API}/products", params={"limit": 1}).json()["items"][0]
        s.post(f"{API}/cart", json={"product_id": p["id"], "quantity": 2})

        r = s.post(f"{API}/orders", json={"full_name": "A B", "address": "1 St", "city": "NY"})
        assert r.status_code == 200, r.text[:300]
        o = r.json()
        assert "_id" not in o
        assert o["status"] == "confirmed"
        assert o["total"] == round(p["price"] * 2, 2)
        assert o["items"][0]["product_id"] == p["id"]
        assert o["shipping"]["city"] == "NY"

        # cart emptied
        assert s.get(f"{API}/cart").json()["items"] == []

        # order listed
        lst = s.get(f"{API}/orders")
        assert lst.status_code == 200
        orders = lst.json()
        assert any(x["id"] == o["id"] for x in orders)
        assert all("_id" not in x for x in orders)

    def test_checkout_validation(self, auth_client):
        r = auth_client.post(f"{API}/orders", json={"full_name": "", "address": "", "city": ""})
        assert r.status_code == 422

    def test_orders_isolated_per_user(self, client):
        s = requests.Session()
        email = f"TEST_{uuid.uuid4().hex[:10]}@example.com"
        s.post(f"{API}/auth/register", json={"name": "Iso", "email": email, "password": "test1234"})
        assert s.get(f"{API}/orders").json() == []


# ---------------------------------------------------------------- CORS
class TestCORS:
    def test_cors_credentials(self):
        origin = BASE_URL
        r = requests.options(f"{API}/auth/login", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        assert r.status_code in (200, 204), r.status_code
        acao = r.headers.get("access-control-allow-origin")
        assert r.headers.get("access-control-allow-credentials") == "true"
        assert acao == origin, f"ACAO must echo origin (not '*') when credentials allowed, got {acao}"


def teardown_module(module):
    """Remove TEST_ data."""
    try:
        from pymongo import MongoClient
        env = dotenv_values("/app/backend/.env")
        mc = MongoClient(os.environ.get("MONGO_URL", env.get("MONGO_URL")))
        d = mc[os.environ.get("DB_NAME", env.get("DB_NAME"))]
        users = list(d.users.find({"email": {"$regex": "^test_", "$options": "i"}}, {"_id": 1}))
        ids = [str(u["_id"]) for u in users]
        d.carts.delete_many({"user_id": {"$in": ids}})
        d.orders.delete_many({"user_id": {"$in": ids}})
        d.users.delete_many({"email": {"$regex": "^test_", "$options": "i"}})
        mc.close()
    except Exception as e:  # noqa
        print(f"cleanup skipped: {e}")
