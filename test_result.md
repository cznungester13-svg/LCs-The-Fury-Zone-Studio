#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================
user_problem_statement: "Make LCs The Fury Zone fully functional: wire up all backend routers, build missing endpoints, seed data, real register/login, real Stripe payments (Flow A claimable sandbox), so customers can register/login, browse products, and pay for real."

backend:
  - task: "Auth (register/login/me) with JWT + bcrypt"
    implemented: true
    working: true
    file: "auth.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Added /auth/me, register now auto-logins returning {token,user}, login returns token+access_token+user. Demo users seeded: admin@furyzone.com/Admin123!, customer@furyzone.com/Customer123!"
        - working: true
          agent: "testing"
          comment: "✅ All auth endpoints working correctly. POST /auth/register creates user and returns {token,access_token,user} without password_hash. POST /auth/login works for both admin and customer, returns correct token+user. Invalid login correctly returns 401. GET /auth/me returns user data without password_hash. Tested with credentials from test_credentials.md."
  - task: "Router wiring under /api prefix"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "All routers (auth, catalog, shop, resale, raffle, chat, engage, storage, admin) now mounted under /api. Added now_iso/NO_ID to database.py which were missing and broke imports."
        - working: true
          agent: "testing"
          comment: "✅ All routers correctly mounted under /api prefix. Tested all endpoints and they respond correctly at https://girardot-hub.preview.emergentagent.com/api/*"
  - task: "Catalog products + reviews (with name/image aliases)"
    implemented: true
    working: true
    file: "catalog.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Products list/detail return frontend aliases name/image/item_id. 28 products seeded, 12 featured."
        - working: true
          agent: "testing"
          comment: "✅ Catalog fully functional. GET /products returns 28 products with all required fields (id,title,name,image,price,rating). Featured products filter works (?featured=true&limit=4 returns 4 items). Search and sort (price_asc) working correctly. GET /products/{id} returns single product with aliases. Departments (6), categories (6), brands (5) all return data. Reviews POST and GET working - created 5-star review and retrieved it successfully."
  - task: "Cart (item_type/item_id schema) + coupons + addresses + orders"
    implemented: true
    working: true
    file: "shop.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Cart reworked to item_type/item_id, supports products and listings. /orders, /coupons/validate (FURY10=10, ZONE20=20), /addresses GET+POST added."
        - working: true
          agent: "testing"
          comment: "✅ Cart operations fully working. GET /cart retrieves cart. POST /cart/add adds items with correct item_id/title/price/quantity fields. POST /cart/update correctly updates quantities. DELETE /cart/item/{id} removes items. Coupons: FURY10 (10% off) and ZONE20 (20% off) validate correctly, invalid coupon returns 404. Addresses: POST creates address, GET retrieves list. GET /orders returns order list (empty for new user)."
  - task: "Stripe checkout (Flow A sandbox) + status polling + webhook + order creation"
    implemented: true
    working: true
    file: "shop.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "POST /checkout/session builds real Stripe session from SERVER-SIDE cart, inserts payment_transactions. GET /checkout/status/{sid} polls Stripe inline + creates order idempotently on paid. Webhook at /api/stripe/webhook. Verified: real checkout.stripe.com URL returned."
        - working: true
          agent: "testing"
          comment: "✅ Stripe checkout fully functional. POST /checkout/session with cart items returns real Stripe URL (checkout.stripe.com) and session_id. Coupon code FURY10 applied correctly. GET /checkout/status/{session_id} returns correct structure with payment_status:pending and order_id:null before payment. Bogus session_id correctly returns 404. Empty cart checkout correctly rejected with 400. Payment_transactions record created successfully."
  - task: "Resale listings + seller dashboard"
    implemented: true
    working: true
    file: "resale.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Fixed ensure_seller_profile (optional store_name + creates seller_balances). Listing decoration adds name/image aliases."
        - working: true
          agent: "testing"
          comment: "✅ Resale marketplace fully working. POST /listings creates listing and auto-promotes user to seller role. GET /listings returns listings with name/image aliases. GET /listings/{id} returns single listing with aliases. GET /my/listings returns user's listings. Seller dashboard endpoints all working: GET /seller/stats returns active/sold counts and balance, GET /seller/profile returns store info, GET /seller/balance returns financial data."
  - task: "Engage: wishlist (item_type/item_id) + notifications + newsletter"
    implemented: true
    working: true
    file: "engage.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Wishlist reworked to item_type/item_id with GET/POST/toggle/check/delete. Newsletter subscribe added."
        - working: true
          agent: "testing"
          comment: "✅ Wishlist and newsletter fully functional. GET /wishlist/check/{id} returns {in_wishlist:false/true}. POST /wishlist adds item and returns {in_wishlist:true} with title/image/price. GET /wishlist returns list with all required fields (item_id,item_type,title,image,price). POST /wishlist/toggle correctly toggles on/off. DELETE /wishlist/{id} removes item. POST /newsletter accepts email and returns success message."
  - task: "Raffle + chat + admin metrics"
    implemented: true
    working: true
    file: "raffle.py, chat.py, admin_routes.py"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Fixed _id serialization on first raffle/cart creation. Admin metrics at /api/admin/metrics."
        - working: true
          agent: "testing"
          comment: "✅ All features working. Raffle: GET /raffle/current returns raffle with entry_count. POST /raffle/enter successfully enters user, second entry returns already_entered:true. Chat: GET /chat/messages returns messages list. POST /chat/messages posts message successfully (FIXED: removed _id from response to prevent ObjectId serialization error). Admin: GET /admin/metrics returns revenue/commissions for admin, correctly returns 403 for customer."

frontend:
  - task: "Cards.jsx (ProductCard/ListingCard) created; cart/wishlist contract aligned"
    implemented: true
    working: "NA"
    file: "components/Cards.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Cards.jsx was empty (Home/Marketplace crashed). Recreated with brand styling. Not yet tested."

metadata:
  created_by: "main_agent"
  version: "2.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus: []
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "Full backend rebuild done. Please test all backend endpoints. Use credentials admin@furyzone.com/Admin123! and customer@furyzone.com/Customer123!. Coupons FURY10 (10%) and ZONE20 (20%). For Stripe, verify /checkout/session returns a Stripe URL and payment_transactions is created; /checkout/status/{sid} should return pending before payment (do NOT attempt real card payment). Focus on high priority tasks first."
    - agent: "testing"
      message: "Comprehensive backend testing complete. All 8 backend tasks are now working correctly. Fixed one bug in chat.py (ObjectId serialization). All endpoints tested: Auth (register/login/me), Catalog (products/reviews/taxonomy), Cart (CRUD operations), Coupons (FURY10/ZONE20), Addresses, Stripe Checkout (real checkout.stripe.com URLs), Orders, Wishlist (full CRUD), Resale (listings/seller dashboard), Raffle (enter/check), Chat (messages), Newsletter, Admin (metrics with role-based access). Ready for main agent to summarize and finish."
