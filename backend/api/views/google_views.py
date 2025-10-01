from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

class GoogleCalendarSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        token = user.google_access_token
        if not token:
            return Response({"error": "Usuário não conectado ao Google"}, status=400)

        try:
            creds = Credentials(token)
            service = build('calendar', 'v3', credentials=creds)

            events_result = service.events().list(
                calendarId='primary', 
                maxResults=10, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            service.close()
            
            return Response(events)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def post(self, request):
        user = request.user
        access_token = getattr(user, "google_access_token", None)
        if not access_token:
            return Response({"error": "Usuário não tem Google conectado."}, status=400)

        event = {
            "summary": "Nova tarefa do projeto",
            "description": "Descrição da tarefa",
            "start": {
                "dateTime": "2025-09-17T10:00:00-03:00",
                "timeZone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": "2025-09-17T11:00:00-03:00",
                "timeZone": "America/Sao_Paulo",
            },
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                json=event,
            )

            if response.status_code == 200 or response.status_code == 201:
                return Response({"message": "Evento criado com sucesso!", "event": response.json()})
            else:
                return Response({"error": "Falha ao criar evento", "details": response.json()}, status=response.status_code)
        except Exception as e:
            return Response({"error": f"Erro na requisição: {str(e)}"}, status=500)