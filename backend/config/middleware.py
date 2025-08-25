# config/middleware.py
from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Permite mais flexibilidade para autenticação OAuth
        response["Cross-Origin-Opener-Policy"] = "unsafe-none"
        response["Cross-Origin-Embedder-Policy"] = "unsafe-none"
        return response