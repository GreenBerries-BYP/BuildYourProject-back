from django.utils import timezone
from ..models import Project, Task, UserProject, TaskAssignee

def calcular_metricas_projeto(projeto_id):
    """
    Calcula métricas de desempenho do projeto usando Earned Value Management
    
    Métricas calculadas:
    - SPI (Schedule Performance Index)
    - SV (Schedule Variance) 
    - TCPI (To Complete Performance Index)
    - EAC (Estimate at Completion)
    - VAC (Variance at Completion)
    """
    try:
        projeto = Project.objects.get(id=projeto_id)
        tarefas = Task.objects.filter(project_phase__project=projeto)
        
        # Métricas básicas
        total_tarefas = tarefas.count()
        tarefas_concluidas = tarefas.filter(is_completed=True).count()
        tarefas_atrasadas = tarefas.filter(is_completed=False, due_date__lt=timezone.now()).count()
        
        taxa_conclusao = (tarefas_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0
        dias_restantes = max(0, (projeto.end_date - timezone.now()).days)
        
        # Cálculo EVM
        total_dias = (projeto.end_date - projeto.start_date).days
        dias_decorridos = (timezone.now() - projeto.start_date).days
        
        ev = tarefas_concluidas / total_tarefas if total_tarefas > 0 else 0
        pv = dias_decorridos / total_dias if total_dias > 0 else 0
        
        spi = ev / pv if pv > 0 else 1.0
        sv = ev - pv
        eac = total_dias / spi if spi > 0 else total_dias
        vac = total_dias - eac
        
        # TCPI adaptado para tempo
        trabalho_restante = 1 - ev
        tempo_restante_planejado = max(1, total_dias - dias_decorridos)
        tcpi = trabalho_restante / (dias_restantes / tempo_restante_planejado) if dias_restantes > 0 else 1.0
        
        return {
            'spi': round(spi, 3),
            'sv': round(sv, 3),
            'tcpi': round(tcpi, 3),
            'eac': round(eac, 1),
            'vac': round(vac, 1),
            'dias_restantes': dias_restantes,
            'tarefas_atrasadas': tarefas_atrasadas,
            'taxa_conclusao': round(taxa_conclusao, 2),
            'total_tarefas': total_tarefas,
            'tarefas_concluidas': tarefas_concluidas
        }
        
    except Project.DoesNotExist:
        return None