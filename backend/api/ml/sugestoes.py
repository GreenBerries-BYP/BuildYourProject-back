from ..utils.ml_metrics import calcular_metricas_projeto
from ..models import UserProject, Task, TaskAssignee

class GeradorSugestoes:
    @staticmethod
    def gerar_sugestoes(projeto):
        """
        Gera sugestões inteligentes baseadas no estado do projeto
        """
        sugestoes = []
        metricas = calcular_metricas_projeto(projeto.id)
        
        if not metricas:
            return sugestoes
        
        # Sugestão 1: Reordenar tarefas complexas
        if metricas['tarefas_atrasadas'] > 2 and metricas['media_complexidade'] > 3.0:
            sugestoes.append({
                'id': 'reordenar_complexas',
                'tipo': 'reordenacao',
                'prioridade': 'alta',
                'titulo': '📊 Reordenar tarefas por complexidade',
                'descricao': 'Mover tarefas mais complexas para o início para evitar acumulo no final',
                'acao': 'reordenar_tarefas_complexas',
                'detalhes': f'{metricas["tarefas_atrasadas"]} tarefas atrasadas detectadas'
            })
        
        # Sugestão 2: Redistribuir carga
        carga_desequilibrada = GeradorSugestoes._verificar_carga_desequilibrada(projeto)
        if carga_desequilibrada:
            sugestoes.append({
                'id': 'redistribuir_carga',
                'tipo': 'distribuicao',
                'prioridade': 'media',
                'titulo': '⚖️ Balancear carga de trabalho',
                'descricao': 'Redistribuir tarefas entre membros da equipe',
                'acao': 'redistribuir_carga',
                'detalhes': 'Carga de trabalho desequilibrada detectada'
            })
        
        # Sugestão 3: Ajustar prazos
        if metricas['taxa_conclusao'] < 40 and metricas['dias_restantes'] < 10:
            sugestoes.append({
                'id': 'ajustar_prazos',
                'tipo': 'prazo',
                'prioridade': 'alta',
                'titulo': '⏰ Revisar prazos críticos',
                'descricao': 'Estender prazos de tarefas próximas ao vencimento',
                'acao': 'ajustar_prazos',
                'detalhes': f'Progresso: {metricas["taxa_conclusao"]}% | Dias restantes: {metricas["dias_restantes"]}'
            })
        
        # Ordenar por prioridade
        prioridade_ordem = {'alta': 3, 'media': 2, 'baixa': 1}
        sugestoes.sort(key=lambda x: prioridade_ordem[x['prioridade']], reverse=True)
        
        return sugestoes
    
    @staticmethod
    def _verificar_carga_desequilibrada(projeto):
        """
        Verifica se há usuários sobrecarregados
        """
        usuarios = UserProject.objects.filter(project=projeto)
        cargas = []
        
        for up in usuarios:
            tarefas_pendentes = Task.objects.filter(
                project_phase__project=projeto,
                is_completed=False,
                taskassignee__user=up.user
            ).count()
            cargas.append(tarefas_pendentes)
        
        if not cargas:
            return False
            
        return max(cargas) - min(cargas) > 3