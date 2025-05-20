import jwt
from decouple import config
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from .models import Account
from api.models import ApiResponseClass
from rest_framework import status
from .entities.accountTypeEnum import AccountRoleEnum

SECRET_KEY=config('SECRET_KEY',default='')
def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Trouver l'objet request dans les arguments
        request = None
        for arg in args:
            if hasattr(arg, 'headers'):
                request = arg
                break
                
        if request is None:
            return ApiResponseClass.error("Objet request introuvable", status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        try:
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
                    request.user = Account.objects.get(id=payload['accountId'])
                except Account.DoesNotExist:
                    return ApiResponseClass.error("Compte non trouvé", status.HTTP_401_UNAUTHORIZED)

                if 'userType' in payload:
                    request.user_type = payload['userType']
                if 'role' in payload:
                    request.user_role = payload['role']

            except jwt.ExpiredSignatureError:
                return ApiResponseClass.error("Token expiré", status.HTTP_401_UNAUTHORIZED)
            except jwt.InvalidTokenError as e:
                return ApiResponseClass.error("Token invalide", status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return ApiResponseClass.error(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return view_func(*args, **kwargs)
    return wrapper


def checkRoleToken(allowed_roles=[AccountRoleEnum.ADMINISTRATOR]):
    """
    Décorateur qui vérifie si le compte a un rôle autorisé.
    L'administrateur a toujours accès, quel que soit le rôle requis.
    
    Args:
        allowed_roles: Liste des rôles autorisés (optionnel)
    """
    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            # Identifier l'objet request et self
            self = None
            request = None
            
            # Cas spécial: si le 1er argument est Request directement (fonction interne)
            if args and args[0].__class__.__name__ == 'Request':
                request = args[0]
            # Pour les vues de classe, le premier argument est self
            elif args and hasattr(args[0], '__class__'):
                self = args[0]
                class_name = self.__class__.__name__
                
                # Si c'est une vue Django REST Framework, la requête est le 2ème argument
                if len(args) > 1 and hasattr(args[1], 'headers'):
                    request = args[1]
                # Sinon, elle peut être un attribut de l'objet self
                elif hasattr(self, 'request'):
                    request = self.request
            else:
                # Chercher la requête dans les arguments
                for arg in args:
                    if hasattr(arg, 'headers'):
                        request = arg
                        break
            
            # Si on n'a pas trouvé de requête, la fonction peut être 
            # une fonction interne qui prend directement le request
            # comme premier argument, et d'autres paramètres ensuite
            if request is None and 'request' in kwargs:
                request = kwargs['request']
            
            if request is None:
                error_msg = "Objet request introuvable dans les arguments"
                return ApiResponseClass.error(error_msg, status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            try:
                # Authentification JWT
                token = request.headers.get("Authorization")
                
                if not token:
                    return ApiResponseClass.error("Token manquant", status.HTTP_401_UNAUTHORIZED)
                    
                parts = token.split()
                if len(parts) != 2 or parts[0].lower() != "bearer":
                    return ApiResponseClass.error("Format du token invalide", status.HTTP_401_UNAUTHORIZED)
                
                token = parts[1]
                
                try:
                    # Décoder le token
                    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                    
                    if not payload.get('accountId'):
                        return ApiResponseClass.error("Token invalide - ID manquant", status.HTTP_401_UNAUTHORIZED)

                    accountId = payload['accountId']
                    
                    try:
                        # Récupérer le compte
                        account = Account.objects.get(id=accountId)
                        
                        # Stocker l'utilisateur dans la requête pour un accès ultérieur
                        request.user = account
                        
                        # L'administrateur a toujours accès
                        if account.role == AccountRoleEnum.ADMINISTRATOR.name:
                            return func(*args, **kwargs)
                        
                        # Pour les autres rôles, vérifier s'ils sont autorisés
                        account_role = account.role
                        
                        # Convertir la liste des rôles autorisés en noms d'énumération
                        if allowed_roles:
                            allowed_roles_names = [role.name if hasattr(role, 'name') else role for role in allowed_roles]
                            if account_role not in allowed_roles_names:
                                return ApiResponseClass.error("Accès non autorisé pour ce rôle", status.HTTP_403_FORBIDDEN)
                        
                        return func(*args, **kwargs)
                    
                    except Account.DoesNotExist:
                        return ApiResponseClass.error("Compte non trouvé", status.HTTP_401_UNAUTHORIZED)
                
                except jwt.ExpiredSignatureError:
                    return ApiResponseClass.error("Token expiré", status.HTTP_401_UNAUTHORIZED)
                except jwt.InvalidTokenError as e:
                    return ApiResponseClass.error("Token invalide", status.HTTP_401_UNAUTHORIZED)
                
            except Exception as e:
                return ApiResponseClass.error(f"Erreur d'authentification: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return wrapped_func
    return decorator

