from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Any, List


app = FastAPI()

# Models
class UserBase(BaseModel):
    email: str


class User(UserBase):
    password: str


class UserResponse(UserBase):
    user_id: int
    message: str


class PurchaseBase(BaseModel):
    user_id: int
    item_name: str
    price: float


class Purchase(PurchaseBase):
    paid: bool = False


class PurchaseResponse(Purchase):
    purchase_id: int
    message: str


class Payment(BaseModel):
    user_id: int
    purchase_id: int
    

class PaymentResponse(Payment):
    payment_id: int
    message: str


class PaidPurchaseResponse(BaseModel):
    paid_purchases_count: int

# "Database"
users: Dict[int, User] = {}
purchases: Dict[int, Purchase] = {}
payments: Dict[int, Payment] = {}


def get_valid_user(user_id):
    user = users.get(user_id)
    if user:
        return user
    
    raise HTTPException(status_code=404, detail='User not found')


# Users
@app.post('/users', response_model=UserResponse, tags=['Users'])
def register_user(user: User):
    if any(existing_user.email == user.email for existing_user in users.values()):
        raise HTTPException(status_code=400, detail="User already registered")
    
    user_id = len(users) + 1
    users[user_id] = user
    return UserResponse(
        user_id=user_id,
        email=user.email,
        message='User registered successfully'
    )


@app.get('/users/{user_id}', response_model=User, tags=['Users'])
def get_user(user_id: int):
    return get_valid_user(user_id)


# Purchases
@app.post('/purchases', response_model=PurchaseResponse, tags=['Purchases'])
def register_purchase(purchase: PurchaseBase):
    if purchase.user_id not in users:
        raise HTTPException(status_code=400, detail='Invalid or missing user_id')

    purchase_id = len(purchases) + 1
    purchases[purchase_id] = Purchase.model_validate(purchase.model_dump())
    return PurchaseResponse(
        purchase_id=purchase_id,
        message='Purchase registered successfully',
        user_id=purchase.user_id,
        item_name=purchase.item_name,
        price=purchase.price,
    )


@app.get('/purchases/{purchase_id}', response_model=Purchase, tags=['Purchases'])
def get_purchase(purchase_id: int,  x_user_id: int = Header()):
    _ = get_valid_user(x_user_id)
    purchase = purchases.get(purchase_id)
    if purchase and purchase.user_id == x_user_id:
        return purchase
    
    raise HTTPException(status_code=404, detail='Purchase not found')


@app.get("/all-purchases", response_model=Dict[int, Purchase], tags=['Purchases'])
def get_all_purchases(x_user_id: int = Header()):
    _ = get_valid_user(x_user_id)
    user_purchases = {pid: p for pid, p in purchases.items() if p.user_id == x_user_id}
    if user_purchases:
        return user_purchases

    raise HTTPException(status_code=404, detail="No purchases found")


# Payments
@app.post('/payments', response_model=PaymentResponse, tags=['Payments'])
def register_payment(payment: Payment):
    if payment.purchase_id not in purchases:
        raise HTTPException(status_code=400, detail='Invalid or missing purchase_id')

    existing_payment = any(p.purchase_id == payment.purchase_id for p in payments.values())
    if existing_payment:
        raise HTTPException(status_code=400, detail='Payment already exists for this purchase')

    payment_id = len(payments) + 1
    payments[payment_id] = payment
    purchases[payment.purchase_id].paid = True
    return PaymentResponse(
        payment_id=payment_id,
        user_id=payment.user_id,
        purchase_id=payment.purchase_id,
        message='Payment registered successfully'
    )


@app.get('/payments/{payment_id}', response_model=Payment, tags=['Payments'])
def get_payment(payment_id: int, x_user_id: int = Header()):
    _ = get_valid_user(x_user_id)
    payment = payments.get(payment_id)
    if payment and payment.user_id == x_user_id:
        return payment
    
    raise HTTPException(status_code=404, detail='Payment not found')


@app.get("/all-payments", response_model=Dict[int, Payment], tags=['Payments'])
def get_all_payments(x_user_id: int = Header()):
    _ = get_valid_user(x_user_id)
    user_payments = {pid: p for pid, p in payments.items() if p.user_id == x_user_id}
    if user_payments:
        return user_payments
    
    raise HTTPException(status_code=404, detail="No payments found")


# Admin
@app.get("/admin/users", response_model=Dict[int, User], tags=['Admin'])
def get_all_users():
    return users


@app.get('/admin/paid_purchases', response_model=PaidPurchaseResponse, tags=['Admin'])
def get_paid_purchases():
    paid_purchases_count = sum(1 for purchase in purchases.values() if purchase.paid)
    return PaidPurchaseResponse(paid_purchases_count=paid_purchases_count)
