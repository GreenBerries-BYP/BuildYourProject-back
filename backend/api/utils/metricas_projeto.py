from django.utils import timezone
from ..models import Project, Task

def calcular_metricas_projeto(projeto_id):
    """
    Calcula métricas de desempenho do projeto usando Earned Value Management
    """
    try:
        projeto = Project.objects.get(id=projeto_id)
        tarefas = Task.objects.filter(project_phase__project=projeto)
        
        # 📊 MÉTRICAS BÁSICAS
        total_tarefas = tarefas.count()
        if total_tarefas == 0:
            return None
            
        tarefas_concluidas = tarefas.filter(is_completed=True).count()
        tarefas_atrasadas = tarefas.filter(is_completed=False, due_date__lt=timezone.now()).count()
        
        taxa_conclusao = (tarefas_concluidas / total_tarefas * 100)
        dias_restantes = max(0, (projeto.end_date - timezone.now()).days)
        
        # 🧮 CÁLCULO EVM - EARNED VALUE MANAGEMENT
        total_dias = max(1, (projeto.end_date - projeto.start_date).days)
        dias_decorridos = max(0, (timezone.now() - projeto.start_date).days)
        
        # EV (Earned Value) = Percentual de trabalho REALIZADO
        ev = tarefas_concluidas / total_tarefas
        
        # PV (Planned Value) = Percentual de trabalho PLANEJADO
        pv = min(dias_decorridos / total_dias, 1.0)
        
        # 📈 SPI (Schedule Performance Index)
        spi = ev / pv if pv > 0 else 1.0
        
        # ✅ CORREÇÃO: Se tem tarefas atrasadas, ajusta SPI para refletir realidade
        if tarefas_atrasadas > 0 and spi >= 1.0:
            spi = max(0.7, spi * 0.8)  # Reduz SPI se há atrasos
        
        # 📉 SV (Schedule Variance)
        sv = ev - pv
        
        # 🎯 EAC (Estimate at Completion) - Nova estimativa de término
        eac = total_dias / spi if spi > 0 else total_dias
        
        # ⚠️ VAC (Variance at Completion) - Variação no término
        vac = total_dias - eac
        
        # 🔄 TCPI (To Complete Performance Index) - Performance necessária
        trabalho_restante = max(0, 1 - ev)
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
            'tarefas_concluidas': tarefas_concluidas,
            'dias_decorridos': dias_decorridos,
            'total_dias': total_dias,
            'ev': round(ev, 3),
            'pv': round(pv, 3)
        }
        
    except Project.DoesNotExist:
        return None
    except Exception as e:
        print(f"Erro ao calcular métricas: {e}")
        return None