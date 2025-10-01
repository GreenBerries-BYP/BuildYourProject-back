from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from api.models import Project, UserProject, ProjectRole, Task, TaskAssignee, AnaliseProjeto

# Import Analytics (novo nome)
try:
    from api.analytics.analisador_desempenho import AnalisadorDesempenho
    from api.analytics.sistema_sugestoes import SistemaSugestoes
    ANALYTICS_DISPONIVEL = True
except ImportError:
    ANALYTICS_DISPONIVEL = False

class AnaliseProjetoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, project_id):
        """
        Analisa o projeto usando Earned Value Management
        URL: POST /api/projetos/{id}/analisar
        """
        if not ANALYTICS_DISPONIVEL:
            return Response({
                'sucesso': False,
                'error': 'Módulo de análise não disponível'
            }, status=503)
            
        projeto = get_object_or_404(Project, id=project_id)
        
        if not UserProject.objects.filter(user=request.user, project=projeto).exists():
            return Response({"error": "Você não tem acesso a este projeto"}, status=403)
        
        try:
            # Usar o novo AnalisadorDesempenho
            analisador = AnalisadorDesempenho()
            analise_completa = analisador.analisar_situacao_projeto(projeto)
            
            # Gerar sugestões com o novo sistema
            sugestoes = SistemaSugestoes.gerar_sugestoes(projeto)
            
            # Calcular probabilidade baseada no SPI (mantendo compatibilidade)
            spi = analise_completa['spi']
            probabilidade_atraso = (1 - spi) * 100 if spi < 1 else 10
            
            # Salvar análise no histórico
            analise = AnaliseProjeto.objects.create(
                projeto=projeto,
                probabilidade_atraso=probabilidade_atraso,
                sugestoes_geradas=sugestoes
            )
            
            # Atualizar projeto
            projeto.probabilidade_atraso = probabilidade_atraso
            projeto.alerta_atraso = spi < 0.9  # Alerta se SPI < 0.9
            projeto.data_ultima_analise = timezone.now()
            projeto.save()
            
            return Response({
                'sucesso': True,
                'analise': analise_completa,
                'sugestoes': sugestoes,
                'probabilidade_atraso': probabilidade_atraso,
                'alerta_atraso': projeto.alerta_atraso,
                'data_analise': analise.data_analise,
                'mensagem': 'Análise concluída com sucesso'
            })
            
        except Exception as e:
            return Response({
                'sucesso': False,
                'error': f'Erro na análise: {str(e)}'
            }, status=500)

class AplicarSugestaoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, project_id):
        """
        Aplica uma sugestão específica no projeto
        URL: POST /api/projetos/{id}/aplicar-sugestao
        """
        projeto = get_object_or_404(Project, id=project_id)
        sugestao_id = request.data.get('sugestao_id')
        acao = request.data.get('acao')
        
        user_project = UserProject.objects.filter(
            user=request.user, 
            project=projeto
        ).first()
        
        if not user_project or user_project.role != ProjectRole.LEADER:
            return Response({"error": "Apenas o líder do projeto pode aplicar sugestões"}, status=403)
        
        try:
            # Mapear ações para os novos métodos
            if acao == 'priorizar_atrasadas':
                resultado = self._priorizar_tarefas_atrasadas(projeto)
            elif acao == 'revisar_metas':
                resultado = self._revisar_metas_projeto(projeto)
            elif acao == 'ajustar_prazos':
                resultado = self._ajustar_prazos_criticos(projeto)
            elif acao == 'balancear_carga':
                resultado = self._balancear_carga_trabalho(projeto)
            elif acao == 'manter_ritmo':
                resultado = self._manter_ritmo_atual(projeto)
            elif acao == 'revisar_escopo':
                resultado = self._revisar_escopo_projeto(projeto)
            else:
                return Response({"error": "Ação não reconhecida"}, status=400)
            
            # Registrar no histórico
            analise = AnaliseProjeto.objects.filter(projeto=projeto).last()
            if analise:
                analise.acoes_aplicadas.append({
                    'sugestao_id': sugestao_id,
                    'acao': acao,
                    'data_aplicacao': timezone.now().isoformat(),
                    'resultado': resultado,
                    'aplicado_por': request.user.email
                })
                analise.save()
            
            return Response({
                'sucesso': True,
                'acao_aplicada': acao,
                'resultado': resultado,
                'mensagem': 'Sugestão aplicada com sucesso'
            })
            
        except Exception as e:
            return Response({
                'sucesso': False,
                'error': f'Erro ao aplicar sugestão: {str(e)}'
            }, status=500)
    
    def _priorizar_tarefas_atrasadas(self, projeto):
        """Prioriza tarefas com prazo vencido"""
        tarefas_atrasadas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            due_date__lt=timezone.now()
        ).order_by('due_date')  # Mais antigas primeiro
        
        # Mover para o topo da lista (reagendar com prazos próximos)
        data_base = timezone.now() + timedelta(days=1)
        tarefas_priorizadas = 0
        
        for i, tarefa in enumerate(tarefas_atrasadas):
            novo_prazo = data_base + timedelta(days=i)
            tarefa.due_date = novo_prazo
            tarefa.save()
            tarefas_priorizadas += 1
        
        return f"Priorizadas {tarefas_priorizadas} tarefas atrasadas"
    
    def _revisar_metas_projeto(self, projeto):
        """Sugere revisão das metas do projeto"""
        # Esta ação é mais sobre notificação - o líder precisa revisar manualmente
        return "Sugerida revisão das metas do projeto para o líder"
    
    def _ajustar_prazos_criticos(self, projeto):
        """Ajusta prazos de tarefas críticas"""
        tarefas_criticas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            due_date__lt=timezone.now() + timedelta(days=3)
        )
        
        tarefas_ajustadas = 0
        
        for tarefa in tarefas_criticas:
            # Adicionar 7 dias ou até o prazo do projeto
            novo_prazo = tarefa.due_date + timedelta(days=7)
            if novo_prazo > projeto.end_date:
                novo_prazo = projeto.end_date
                
            tarefa.due_date = novo_prazo
            tarefa.save()
            tarefas_ajustadas += 1
        
        return f"Ajustados prazos de {tarefas_ajustadas} tarefas críticas"
    
    def _balancear_carga_trabalho(self, projeto):
        """Distribui tarefas não atribuídas de forma equilibrada"""
        usuarios = list(UserProject.objects.filter(project=projeto))
        if not usuarios:
            return "Nenhum usuário no projeto para redistribuir"
            
        tarefas_nao_atribuidas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            taskassignee__isnull=True
        )
        
        tarefas_distribuidas = 0
        
        for i, tarefa in enumerate(tarefas_nao_atribuidas):
            usuario = usuarios[i % len(usuarios)].user
            TaskAssignee.objects.create(task=tarefa, user=usuario)
            tarefas_distribuidas += 1
        
        return f"Distribuídas {tarefas_distribuidas} tarefas entre {len(usuarios)} membros"
    
    def _manter_ritmo_atual(self, projeto):
        """Ação positiva - projeto está bem"""
        # Pode enviar notificação de reconhecimento para a equipe
        return "Reconhecimento: projeto está com bom desempenho"
    
    def _revisar_escopo_projeto(self, projeto):
        """Sugere revisão do escopo do projeto"""
        # Esta ação requer intervenção manual do líder
        return "Sugerida revisão do escopo do projeto para o líder"

# View adicional para buscar apenas sugestões
class SugestoesProjetoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, project_id):
        """
        Retorna apenas as sugestões para o projeto
        URL: GET /api/projetos/{id}/sugestoes/
        """
        if not ANALYTICS_DISPONIVEL:
            return Response({
                'sucesso': False,
                'error': 'Módulo de análise não disponível'
            }, status=503)
            
        projeto = get_object_or_404(Project, id=project_id)
        
        if not UserProject.objects.filter(user=request.user, project=projeto).exists():
            return Response({"error": "Você não tem acesso a este projeto"}, status=403)
        
        try:
            sugestoes = SistemaSugestoes.gerar_sugestoes(projeto)
            
            return Response({
                'sucesso': True,
                'sugestoes': sugestoes,
                'total_sugestoes': len(sugestoes)
            })
            
        except Exception as e:
            return Response({
                'sucesso': False,
                'error': f'Erro ao gerar sugestões: {str(e)}'
            }, status=500)