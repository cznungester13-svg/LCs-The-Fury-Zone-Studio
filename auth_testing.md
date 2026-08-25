## Auth Testing Playbook (LC Marketplace)

Base URL local: http://localhost:8001

Admin: admin@lcfury.com / admin123

Endpoints:
- POST /api/auth/register {name,email,password}
- POST /api/auth/login {email,password}
- POST /api/auth/logout
- GET  /api/auth/me
- POST /api/auth/refresh

Cookie flow (httpOnly, secure, samesite=none):
```
curl -c c.txt -X POST http://localhost:8001/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@lcfury.com","password":"admin123"}'
curl -b c.txt http://localhost:8001/api/auth/me
```
Frontend sends cookies via axios withCredentials:true. Bearer header fallback also supported.
