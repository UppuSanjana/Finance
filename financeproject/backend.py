# backend.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="FinPlanBot API", version="1.0.0")

# In-memory storage
users = []
expenses = []
goals = []
budgets = []

# Models
class User(BaseModel):
    id: int
    name: str
    age: int
    email: Optional[str] = None

class Expense(BaseModel):
    user_id: int
    date: str
    category: str
    subcategory: str
    amount: float
    description: Optional[str] = ""

class Goal(BaseModel):
    user_id: int
    goal_name: str
    target: float
    months: int

class Budget(BaseModel):
    user_id: int
    monthly_budget: float

# Routes
@app.post("/add_user/")
def add_user(user: User):
    users.append(user.dict())
    return {"message": f"User {user.name} added!", "user_id": user.id}

@app.get("/users/")
def get_users():
    return {"users": users}

@app.post("/add_expense/")
def add_expense(expense: Expense):
    if not any(u["id"] == expense.user_id for u in users):
        raise HTTPException(status_code=404, detail="User not found")
    expenses.append(expense.dict())
    return {"message": "Expense added"}

@app.get("/expenses/{user_id}")
def get_expenses(user_id: int):
    user_expenses = [e for e in expenses if e["user_id"] == user_id]
    return {"expenses": user_expenses[-10:]}

@app.post("/add_goal/")
def add_goal(goal: Goal):
    if not any(u["id"] == goal.user_id for u in users):
        raise HTTPException(status_code=404, detail="User not found")
    goals.append(goal.dict())
    return {"message": f"Goal '{goal.goal_name}' added"}

@app.get("/goals/{user_id}")
def get_goals(user_id: int):
    user_goals = [g for g in goals if g["user_id"] == user_id]
    return {"goals": user_goals}

@app.post("/set_budget/")
def set_budget(budget: Budget):
    if not any(u["id"] == budget.user_id for u in users):
        raise HTTPException(status_code=404, detail="User not found")
    budgets.append(budget.dict())
    return {"message": f"Budget of {budget.monthly_budget} set for user {budget.user_id}"}

@app.get("/check_budget/{user_id}")
def check_budget(user_id: int):
    user_budget = next((b for b in budgets if b["user_id"] == user_id), None)
    if not user_budget:
        raise HTTPException(status_code=404, detail="No budget set")
    total_spent = sum(e["amount"] for e in expenses if e["user_id"] == user_id)
    if total_spent > user_budget["monthly_budget"]:
        return {"alert": f"⚠️ Budget exceeded! Spent {total_spent} out of {user_budget['monthly_budget']}"}
    return {"status": f"✅ Within budget: Spent {total_spent} of {user_budget['monthly_budget']}"}
