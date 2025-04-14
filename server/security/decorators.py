import jwt
import os
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from .models import Account
SECRET_KEY = "264acbe227697c2106fec96de2608ffa9696eea8d4bec4234a4d49e099decc7448daafbc7ba2f4d7b127460936a200f9885c220e81c929525e310084a7abea6fc523f0b2a2241bc91899f158f4c437b059141ffc24642dfa2254842ae8acab96460e05a6293aea8a31f44aa860470b8d972d5f4d1adec181bf79d77fe4a2eed0eed7189da484c5601591ca222b11ff0ca56fce663f838cd4f1a5cddcec78f3821ac0da9769b848147238928f24d59849c7bb8dbf12697d214f04d7fbd476f38c3b360895b1e09d9c0d1291fd61452efb0616034baf32492550b3067d0a3adf317a6808da8555f1cffca990c0452e97d48c8becb77ccdda4290146c49b1c5a8b5"



def jwt_required(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):  # Ajout du paramètre self pour les méthodes de classe
        token = request.headers.get("Authorization")
        if not token:
                return JsonResponse({"error": "Token manquant"}, status=401)
            
        parts = token.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JsonResponse({"error": "Format du token invalide"}, status=401)
        
        token = parts[1]        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload['account_id']:
                request.user = Account.objects.get(account_id=payload['account_id'])

        except Exception as e:
                    return JsonResponse({"error": str(e)}, status=401)
        
        return func(self, request, *args, **kwargs)  # Passage de self à la fonction d'origine
    return wrapper

def has_employee_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        @jwt_required
        def wrapper(self, request, *args, **kwargs):
            try:
                user = request.user
                print(user.employee_role)
                allowed_roles_values = [role.value if hasattr(role, 'value') else role for role in allowed_roles]
                if user.employee_role not in allowed_roles_values:
                    return JsonResponse({
                        "error": "Accès non autorisé pour ce rôle",
                        "role_requis": allowed_roles_values,                
                        "votre_role": user.employee_role
                    }, status=403)
                
                return func(self, request, *args, **kwargs)
                
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=401)              
        return wrapper
    return decorator
