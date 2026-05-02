import json
import secrets
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Token


def get_user_from_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token_key = auth_header[7:]
    try:
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None


@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'message': 'Invalid JSON'}, status=400)

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return JsonResponse({'message': 'Email and password required'}, status=400)

    user = authenticate(username=email, password=password)
    if not user:
        return JsonResponse({'message': 'Invalid credentials'}, status=401)

    token, _ = Token.objects.get_or_create(user=user)
    if not token.key:
        token.key = secrets.token_urlsafe(32)
        token.save()

    role = 'admin'
    if user.groups.filter(name='Manager').exists():
        role = 'manager'
    elif user.groups.filter(name='Staff').exists():
        role = 'staff'

    return JsonResponse({
        'token': token.key,
        'user': {
            'id': user.id,
            'name': user.first_name and f"{user.first_name} {user.last_name}" or user.email.split('@')[0].title(),
            'email': user.email,
            'role': role,
        }
    })


@csrf_exempt
@require_POST
def logout_view(request):
    user = get_user_from_token(request)
    if user:
        try:
            user.auth_token.delete()
        except Token.DoesNotExist:
            pass
    return JsonResponse({'message': 'Logged out'})


@csrf_exempt
@require_GET
def me_view(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    role = 'admin'
    if user.groups.filter(name='Manager').exists():
        role = 'manager'
    elif user.groups.filter(name='Staff').exists():
        role = 'staff'

    return JsonResponse({
        'user': {
            'id': user.id,
            'name': user.first_name and f"{user.first_name} {user.last_name}" or user.email.split('@')[0].title(),
            'email': user.email,
            'role': role,
        }
    })
