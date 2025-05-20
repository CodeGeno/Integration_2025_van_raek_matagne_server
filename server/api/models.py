from rest_framework.response import Response
from rest_framework import status

class ApiResponseClass:
    @staticmethod
    def success(message, data=None):
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        return Response(response, status=status.HTTP_200_OK)

    @staticmethod
    def created(message, data=None):
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        return Response(response, status=status.HTTP_201_CREATED)

    @staticmethod
    def error(message, status_code=status.HTTP_400_BAD_REQUEST):
        response = {
            "success": False,
            "message": message
        }

        if isinstance(status_code, int):
            return Response(response, status=status_code)
        else:
            # Si pas un entier, code 400 par défaut
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def unauthorized(message="Accès non autorisé"):
        response = {
            "success": False,
            "message": message
        }
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def succesOverview(message,data=None,current_page=None,total_pages=None):
        response = {
            "success": True,
            "message": message,
            "data": data,
            "current_page": current_page,
            "total_pages": total_pages
        }
        return Response(response, status=status.HTTP_200_OK)