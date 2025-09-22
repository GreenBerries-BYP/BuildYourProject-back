from django.utils import timezone
from ..models import Project, Task, UserProject, TaskAssignee

def calcular_metricas_projeto(projeto_id):
    """
    Calcula métricas em tempo real para o projeto
    """
    try:
        projeto = Project.objects.get(id=projeto_id)
        tarefas = Task.objects.filter(project_phase__project=projeto)
        
        # Tarefas atrasadas (pendentes e com prazo vencido)
        tarefas_atrasadas = tarefas.filter(
            is_completed=False, 
            due_date__lt=timezone.now()
        ).count()
        
        # Taxa de conclusão
        total_tarefas = tarefas.count()
        tarefas_concluidas = tarefas.filter(is_completed=True).count()
        taxa_conclusao = (tarefas_concluidas / total_tarefas) if total_tarefas > 0 else 0
        
        # Complexidade média (versão simplificada sem models.Avg)
        tarefas_com_complexidade = tarefas.exclude(complexidade__isnull=True)
        if tarefas_com_complexidade.exists():
            soma_complexidade = sum(t.complexidade for t in tarefas_com_complexidade)
            media_complexidade = soma_complexidade / tarefas_com_complexidade.count()
        else:
            media_complexidade = 3.0  # Valor padrão
        
        # Dias restantes
        dias_restantes = (projeto.end_date - timezone.now()).days
        
        # Carga por usuário
        carga_usuarios = {}
        usuarios_projeto = UserProject.objects.filter(project=projeto)
        
        for up in usuarios_projeto:
            tarefas_pendentes = Task.objects.filter(
                project_phase__project=projeto,
                is_completed=False,
                taskassignee__user=up.user
            ).count()
            carga_usuarios[up.user.email] = tarefas_pendentes
        
        return {
            'total_tarefas': total_tarefas,
            'tarefas_concluidas': tarefas_concluidas,
            'tarefas_atrasadas': tarefas_atrasadas,
            'taxa_conclusao': round(taxa_conclusao * 100, 2),
            'media_complexidade': round(media_complexidade, 2),
            'dias_restantes': max(0, dias_restantes),
            'carga_usuarios': carga_usuarios
        }
        
    except Project.DoesNotExist:
        return None