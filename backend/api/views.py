from django.http import JsonResponse

# Na view a gente faz o tratamento do que a url pede. Depende se for get, post, update. 
# Sempre retorne em JSON pro front conseguir tratar bem
def hello_world(request):
    return JsonResponse({"message": "Mensagem vinda do Django!"})
