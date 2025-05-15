import jwt
import os
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from .models import Account
from api.models import ApiResponseClass
from rest_framework import status
from .entities.accountTypeEnum import AccountRoleEnum
SECRET_KEY = "264acbe227697c2106fec96de2608ffa9696eea8d4bec4234a4d49e099decc7448daafbc7ba2f4d7b127460936a200f9885c220e81c929525e310084a7abea6fc523f0b2a2241bc91899f158f4c437b059141ffc24642dfa2254842ae8acab96460e05a6293aea8a31f44aa860470b8d972d5f4d1adec181bf79d77fe4a2eed0eed7189da484c5601591ca222b11ff0ca56fce663f838cd4f1a5cddcec78f3821ac0da9769b848147238928f24d59849c7bb8dbf12697d214f04d7fbd476f38c3b360895b1e09d9c0d1291fd61452efb0616034baf32492550b3067d0a3adf317a6808da8555f1cffca990c0452e97d48c8becb77ccdda4290146c49b1c5a8b5"


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        try:
            print("=== Début de la vérification JWT ===")
            print("Méthode de la requête:", request.method)
            print("URL de la requête:", request.path)
            
            token = request.headers.get("Authorization")
            if not token:
                print("ERREUR: Token manquant dans les headers")
                return JsonResponse({
                    "error": "Token manquant",
                    "details": "L'en-tête Authorization est requis pour cette requête"
                }, status=401)
                
            parts = token.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                print("ERREUR: Format du token invalide")
                return JsonResponse({
                    "error": "Format du token invalide",
                    "details": "Le token doit être au format 'Bearer <token>'"
                }, status=401)
            
            token = parts[1]
            
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                
                if not payload.get('accountId'):
                    print("ERREUR: Pas d'accountId dans le payload")
                    return JsonResponse({
                        "error": "Token invalide",
                        "details": "Le token ne contient pas d'identifiant de compte"
                    }, status=401)

                try:
                    request.user = Account.objects.get(id=payload['accountId'])
                except Account.DoesNotExist:
                    print("ERREUR: Compte non trouvé pour l'ID:", payload['accountId'])
                    return JsonResponse({
                        "error": "Compte non trouvé",
                        "details": f"Aucun compte trouvé avec l'ID {payload['accountId']}"
                    }, status=401)

                if 'userType' in payload:
                    request.user_type = payload['userType']
                if 'role' in payload:
                    request.user_role = payload['role']

            except jwt.ExpiredSignatureError:
                print("ERREUR: Token expiré")
                return JsonResponse({
                    "error": "Token expiré",
                    "details": "Le token a expiré, veuillez vous reconnecter"
                }, status=401)
            except jwt.InvalidTokenError as e:
                print("ERREUR: Token invalide:", str(e))
                return JsonResponse({
                    "error": "Token invalide",
                    "details": str(e)
                }, status=401)

        except Exception as e:
            print("ERREUR générale:", str(e))
            return JsonResponse({
                "error": "Erreur d'authentification",
                "details": str(e)
            }, status=500)
        
        print("=== Fin de la vérification JWT ===")
        return view_func(self, request, *args, **kwargs)
    return wrapper


def checkRoleToken(allowed_roles=[AccountRoleEnum.ADMINISTRATOR]):
    """
    Décorateur qui vérifie si le compte a un rôle autorisé.
    L'administrateur a toujours accès, quel que soit le rôle requis.
    
    Args:
        allowed_roles: Liste des rôles autorisés (optionnel)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            try:
                # Vérifier l'authentification JWT
                token = request.headers.get("Authorization")
                if not token:
                    return ApiResponseClass.error("Token manquant", status.HTTP_401_UNAUTHORIZED)
                    
                parts = token.split()
                if len(parts) != 2 or parts[0].lower() != "bearer":
                    return ApiResponseClass.error("Format du token invalide", status.HTTP_401_UNAUTHORIZED)
                
                token = parts[1]
                
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                    
                    if not payload.get('accountId'):
                        return ApiResponseClass.error("Token invalide", status.HTTP_401_UNAUTHORIZED)

                    try:
                        account = Account.objects.get(id=payload['accountId'])
                        print(account.role)
                        request.user = account
                        # L'administrateur a toujours accès
                        if account.role == AccountRoleEnum.ADMINISTRATOR.name:
                            return view_func(self, request, *args, **kwargs)
                    

                    
                    except Account.DoesNotExist:
                        return ApiResponseClass.error("Compte non trouvé", status.HTTP_401_UNAUTHORIZED)

                except jwt.ExpiredSignatureError:
                    return ApiResponseClass.error("Token expiré", status.HTTP_401_UNAUTHORIZED)
                except jwt.InvalidTokenError as e:
                    return ApiResponseClass.error("Token invalide", status.HTTP_401_UNAUTHORIZED)

                # Vérification du rôle
                account_role = account.role
                
              
                
                # Vérifier si le rôle est autorisé
                if allowed_roles:
                    allowed_roles_names = [role.name if hasattr(role, 'name') else role for role in allowed_roles]
                    if account_role not in allowed_roles_names:
                        return ApiResponseClass.error("Accès non autorisé pour ce rôle", status.HTTP_403_FORBIDDEN)
                
                return view_func(self, request, *args, **kwargs)
                
            except Exception as e:
                print("ERREUR générale:", str(e))
                return ApiResponseClass.error(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        return wrapper
    return decorator

