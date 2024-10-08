import json
from fastapi.responses import JSONResponse
from ninja import Router, NinjaAPI
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from pydantic import Json
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.response import Response
from rest_framework import status
from core.models import Role, User
from core.schemas import DetailSchema, LogInSchema, RegisterInSchema, UserSchemaOut
import logging
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

# User model
User = get_user_model()

# Ninja API instance
api = NinjaAPI(
    version="1.0",
    csrf=False,
    title="Valmi App Backend API",
    description="App Backend API Serves the Valmi App Frontend",
)

# Public Router for routes accessible without authentication
public_router = Router()

# Authenticated Router for routes protected by Bearer Token
protected_router = Router()


### PUBLIC ROUTES ###

# Register Route - Anyone can access
@public_router.post("/register/", response={200: dict, 400: DetailSchema})
def register(request, register_schema: RegisterInSchema):
    req = register_schema.dict()
    try:
        if User.objects.filter(username=req["username"]).exists():
            raise Exception("Username already exists")

        user = User(
            username=req["username"], 
            email=req["email"], 
            password=make_password(req["password"])
        )
        user.role = req.get("role") or Role.MEMBER.value
        if user.role not in [Role.LIBRARIAN.value, Role.MEMBER.value]:
            raise Exception(f"Invalid role: {user.role}. Role must be either 'librarian' or 'member'.")
        print(f"Assigning role: {user.role}")
        print(user)
        user.save()
        
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        response = {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
        }
        return response
    except Exception as e:
        return 400, {"detail": str(e)}



# Login Route - Anyone can access
@public_router.post("/login/", response={200: dict, 400: DetailSchema})
def login(request, login_req: LogInSchema):  # Add the request parameter
    req = login_req.dict()

    try:
        user = User.objects.filter(username=req["username"]).first()
        if user and user.check_password(req["password"]):
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            response = {
                'access_token': str(access_token),  # Corrected key name
                'refresh_token': str(refresh_token),  # Ensure token is string
            }
            return response  # Return the response directly
        else:
            raise Exception("Invalid username or password")
    except Exception as e:
        return 400, {"detail": str(e)}


### AUTHENTICATED/PROTECTED ROUTES ###

class AuthBearer:
    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        token_type, token = auth_header.split()
        if token_type.lower() != 'bearer':
            return None
        
        try:
            # Validate the token
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            request.user = user  # Attach user to request
            return token
        except Exception:
            return None


# Protected Route - Requires valid Bearer token
@protected_router.get("/profile/", response=UserSchemaOut)
def get_profile(request):
    user = request.user
    return {
        "username": user.username,
        "email": user.email,
        "role": user.role
    }




# Add Public and Protected Routers to the Main API
api.add_router("/v1/auth", public_router)
api.add_router("/v1/", protected_router, auth=AuthBearer())
