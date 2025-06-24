from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uvicorn

app = FastAPI(title="User API", version="1.0.0")

# In-memory database for demonstration purposes
users_db = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "username": "johndoe"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "username": "janesmith"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "username": "bobjohnson"},
]

# In-memory posts database for demonstration
posts_db = [
    {"id": 1, "userId": 1, "title": "First Post", "body": "This is my first post"},
    {"id": 2, "userId": 1, "title": "Second Post", "body": "This is my second post"},
    {"id": 3, "userId": 2, "title": "Jane's Post", "body": "Hello from Jane"},
]

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    username: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    username: str

class PostResponse(BaseModel):
    id: int
    userId: int
    title: str
    body: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get user by ID"""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[UserResponse])
async def get_users(_limit: Optional[int] = Query(10, alias="_limit")):
    """Get a list of users, optionally limited by the _limit query parameter"""
    return users_db[:_limit]

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user"""
    # Simple validation for required fields
    if not user.name.strip():
        raise HTTPException(status_code=422, detail={
            "error": "Validation failed",
            "details": ["Name is required"]
        })
    
    new_id = max(u["id"] for u in users_db) + 1
    new_user = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
        "username": user.username
    }
    users_db.append(new_user)
    return new_user

@app.get("/posts", response_model=List[PostResponse])
async def get_posts(userId: Optional[int] = Query(None)):
    """Get posts, optionally filtered by userId"""
    if userId:
        return [p for p in posts_db if p["userId"] == userId]
    return posts_db

# Provider state management for Pact verification
@app.get("/_pact/provider_states")
async def get_provider_states():
    """Available provider states for Pact verification"""
    return {
        "states": [
            "user 1 exists",
            "user 999 does not exist", 
            "users exist",
            "user creation is allowed",
            "user 1 has posts",
            "user creation validation is enabled"
        ]
    }

@app.post("/_pact/provider_states")
async def setup_provider_state(state: dict):
    """Setup provider state for Pact verification"""
    global users_db
    state_name = state.get("state")
    
    if state_name == "user 1 exists":
        # Ensure user 1 exists in database
        if not any(u["id"] == 1 for u in users_db):
            users_db.append({
                "id": 1, 
                "name": "John Doe", 
                "email": "john@example.com", 
                "username": "johndoe"
            })
    
    elif state_name == "user 999 does not exist":
        # Ensure user 999 doesn't exist
        users_db = [u for u in users_db if u["id"] != 999]
    
    elif state_name == "users exist":
        # Ensure we have users in the database
        if len(users_db) == 0:
            users_db.extend([
                {"id": 1, "name": "John Doe", "email": "john@example.com", "username": "johndoe"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "username": "janesmith"}
            ])
    
    elif state_name == "user 1 has posts":
        # Ensure user 1 has posts
        if not any(p["userId"] == 1 for p in posts_db):
            posts_db.append({
                "id": 1, 
                "userId": 1, 
                "title": "Sample Post Title", 
                "body": "Sample post body content"
            })
    
    return {"result": f"Provider state '{state_name}' has been set"}

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 