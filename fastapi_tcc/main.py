from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any


app = FastAPI()

# dict_item = {
#     'key1': 'item 1',
#     'key2': 'item 2',
# }

# @app.get("/items/{item_id}")
# async def show_item(item_id: str):
#     return {'results': dict_item[item_id]}


users: Dict[int, Any] = {}
purchases: Dict[int, Any] = {}
payments: Dict[int, Any] = {}

class User(BaseModel):
    user: str
    password: str


class Purchase(BaseModel):
    user_id: int
    purchase: str
    price: float


class Payment(BaseModel):
    purchase_id: int
    # amount: float


@app.post("/users/", response_model=Dict[str, Any])
def register_user(user: User):
    user_id = len(users) + 1
    users[user_id] = user.dict()
    return {"message": "User registered successfully", "user_id": user_id}


@app.get("/users/{user_id}", response_model=Any)
def get_user(user_id: int):
    user = users.get(user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/purchases/", response_model=Dict[str, Any])
def register_purchase(purchase: Purchase):
    if purchase.user_id not in users:
        raise HTTPException(status_code=400, detail="Invalid or missing user_id")

    purchase_id = len(purchases) + 1
    purchases[purchase_id] = purchase.dict()
    return {"message": "Purchase registered successfully", "purchase_id": purchase_id}


@app.get("/purchases/{purchase_id}", response_model=Any)
def get_purchase(purchase_id: int):
    purchase = purchases.get(purchase_id)
    if purchase:
        return purchase
    else:
        raise HTTPException(status_code=404, detail="Purchase not found")


@app.post("/payments/", response_model=Dict[str, Any])
def register_payment(payment: Payment):
    if payment.purchase_id not in purchases:
        raise HTTPException(status_code=400, detail="Invalid or missing purchase_id")

    payment_id = len(payments) + 1
    payments[payment_id] = payment.dict()
    purchases[payment.purchase_id]['paid'] = True  # Marca a compra como paga
    return {"message": "Payment registered successfully", "payment_id": payment_id}


@app.get("/payments/{payment_id}", response_model=Any)
def get_payment(payment_id: int):
    payment = payments.get(payment_id)
    if payment:
        return payment
    else:
        raise HTTPException(status_code=404, detail="Payment not found")


@app.get("/paid_purchases/", response_model=Dict[str, int])
def get_paid_purchases():
    paid_purchases_count = sum(1 for purchase in purchases.values() if purchase.get('paid'))
    return {"paid_purchases_count": paid_purchases_count}
