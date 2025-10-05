from django.utils import timezone
from ..models import Project, Task

def calcular_metricas_projeto(projeto_id):
    """
    Calcula métricas de desempenho do projeto usando Earned Value Management CORRETO
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
        tarefas_pendentes = total_tarefas - tarefas_concluidas
        
        taxa_conclusao = (tarefas_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0
        
        # 📅 CÁLCULOS DE TEMPO
        total_dias = max(1, (projeto.end_date - projeto.start_date).days)
        dias_decorridos = max(0, (timezone.now() - projeto.start_date).days)
        dias_restantes = max(0, (projeto.end_date - timezone.now()).days)
        
        # ⚠️ VERIFICAÇÃO CRÍTICA: Projeto já está atrasado?
        projeto_atrasado = timezone.now() > projeto.end_date
        
        # 🧮 CÁLCULO EVM CORRETO - CONSIDERANDO PESO DAS TAREFAS
        # Vamos considerar que cada tarefa tem peso igual
        ev = tarefas_concluidas / total_tarefas if total_tarefas > 0 else 0  # Earned Value
        
        # Planned Value: % do tempo que passou deveria ter sido concluído
        pv = min(dias_decorridos / total_dias, 1.0) if total_dias > 0 else 0
        
        # 📈 SPI (Schedule Performance Index) - CORRIGIDO
        spi = ev / pv if pv > 0 else 1.0
        
        # ✅ CORREÇÃO REALISTA: Se há tarefas atrasadas, SPI deve refletir isso
        if tarefas_atrasadas > 0:
            # Reduz o SPI proporcionalmente às tarefas atrasadas
            penalidade_atraso = (tarefas_atrasadas / total_tarefas) * 0.5  # Penalidade de 50% por tarefa atrasada
            spi = max(0.1, spi - penalidade_atraso)
        
        # ✅ CORREÇÃO ADICIONAL: Se projeto já passou da data final
        if projeto_atrasado and tarefas_pendentes > 0:
            spi = 0.3  # SPI crítico para projetos atrasados com tarefas pendentes
        
        # 📉 SV (Schedule Variance)
        sv = ev - pv
        
        # 🎯 EAC (Estimate at Completion) - CORRIGIDO
        eac = total_dias / spi if spi > 0.1 else total_dias * 2  # Limite realista
        
        # ⚠️ VAC (Variance at Completion)
        vac = total_dias - eac
        
        # 🔄 TCPI (To Complete Performance Index) - CORRIGIDO
        trabalho_restante = max(0, 1 - ev)
        tcpi = trabalho_restante / (dias_restantes / total_dias) if dias_restantes > 0 and total_dias > 0 else 2.0
        
        # Se TCPI for muito alto (> 2.0), é praticamente impossível
        if tcpi > 2.0:
            tcpi = 2.0
        
        return {
            'spi': round(spi, 3),
            'sv': round(sv, 3),
            'tcpi': round(tcpi, 3),
            'eac': round(eac, 1),
            'vac': round(vac, 1),
            'dias_restantes': dias_restantes,
            'tarefas_atrasadas': tarefas_atrasadas,
            'tarefas_pendentes': tarefas_pendentes,
            'taxa_conclusao': round(taxa_conclusao, 2),
            'total_tarefas': total_tarefas,
            'tarefas_concluidas': tarefas_concluidas,
            'dias_decorridos': dias_decorridos,
            'total_dias': total_dias,
            'ev': round(ev, 3),
            'pv': round(pv, 3),
            'projeto_atrasado': projeto_atrasado
        }
        
    except Project.DoesNotExist:
        return None
    except Exception as e:
        print(f"Erro ao calcular métricas: {e}")
        return None
