# middleware/cors.py
class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Adiciona headers CORS para todos os métodos
        response["Access-Control-Allow-Origin"] = "https://buildyourproject-front.onrender.com"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRFToken"
        response["Access-Control-Allow-Credentials"] = "true"
        
        return response
