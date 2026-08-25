# LC Multi-Dept Resale Marketplace — PRD

## Original Problem
Two disconnected repos (CRA frontend + Express/Postgres backend) that never deployed. User chose to **rebuild fresh** on the house stack: React + FastAPI + MongoDB. Hard requirements: every department has exactly 50 items, super-low resale prices, product images displayed correctly and matching the items.

## Stack
- Frontend: React (CRA/CRACO) + Tailwind, neo-brutalist "Eclectic Thrift Bazaar" theme (Anton/Archivo/Space Mono)
- Backend: FastAPI + Motor (MongoDB)
- Auth: JWT in httpOnly cookies (bcrypt), brute-force lockout, Bearer fallback

## Personas
- Shopper: browses departments, adds to cart, checks out, views orders
- Admin: seeded account (admin@lcfury.com)

## Core Requirements (static)
- 6 departments (fashion, electronics, home, books, sports, toys), exactly 50 items each = 300
- Prices $0.99–$19.99; discount vs realistic original price
- Real photos per department, images match item type

## Implemented (2026-06 / Aug run)
- Backend: /api/health, /api/departments, /api/products (filter/search/sort/pagination), /api/products/deals, /api/products/{id} (+related)
- Auth: register/login/logout/me/refresh; bcrypt; brute-force lockout (5→15min); admin + shopper@test.com seeded; self-healing product seed (reseeds unless exactly 300)
- Cart (auth): GET/POST/PUT(in-place)/DELETE
- Orders (auth): POST checkout (empties cart), GET list
- Frontend: Home (hero bento + dept cards + deals), Shop/Department (sort + pagination), Product detail (+related), Cart, Checkout (success), Orders, Login, Register; sonner toasts; responsive nav
- Tested: backend 39/41 pytest + full E2E purchase flow passed; the 2 gaps (brute-force, CORS) were fixed after.

## Backlog / Next
- P1: real payment (Stripe/Razorpay) at checkout
- P1: decrement stock on order + out-of-stock handling
- P2: admin product management UI
- P2: subcategory filtering within departments
- P2: wishlist / recently viewed
- Deferred: consolidate old repos / deploy backend to Render (user's original phases 3-5) — superseded by fresh rebuild

## Credentials
- Admin: admin@lcfury.com / admin123
- Test user: shopper@test.com / test123
