from ..utils.metricas_projeto import calcular_metricas_projeto
from ..models import UserProject, Task, TaskAssignee
from django.utils import timezone

class SistemaSugestoes:
    """
    SISTEMA DE SUGESTÕES INTELIGENTES BASEADO EM MÉTRICAS EVM
    
    Base: PMBOK Guide 7th Edition, NASA EVM Handbook, ANSI/EIA-748
    """
    
    @staticmethod
    def gerar_sugestoes(projeto):
        """
        Gera sugestões contextuais baseadas em análise EVM do projeto
        """
        sugestoes = []
        metricas = calcular_metricas_projeto(projeto.id)
        
        if not metricas:
            return sugestoes
        
        # PROJETO CONCLUÍDO - SEM SUGESTÕES
        if metricas['taxa_conclusao'] == 100:
            return []
        
        spi = metricas['spi']
        tcpi = metricas['tcpi']
        vac = metricas['vac']
        tarefas_atrasadas = metricas['tarefas_atrasadas']
        dias_restantes = metricas['dias_restantes']
        total_tarefas = metricas['total_tarefas']
        taxa_conclusao = metricas['taxa_conclusao']
        dias_atraso = max(0, -vac)
        tarefas_pendentes = total_tarefas - metricas['tarefas_concluidas']

        # SUGESTÃO 1: CARGA DESPROPORCIONAL - TAREFAS vs DIAS
        carga_desproporcional = SistemaSugestoes._verificar_carga_desproporcional(
            tarefas_pendentes, dias_restantes, projeto
        )
        if carga_desproporcional['desproporcional']:
            descricao = f"Carga de trabalho intensa: {tarefas_pendentes} tarefas para {dias_restantes} dias. "
            descricao += f"Média de {carga_desproporcional['tarefas_por_dia']:.1f} tarefas/dia necessárias. "
            descricao += "Considere: alocar mais recursos, estender prazos ou priorizar tarefas críticas."
            
            sugestoes.append({
                'id': 'otimizar_carga',
                'titulo': 'Otimizar Carga de Trabalho',
                'descricao': descricao,
                'acao': 'otimizar_carga',
                'prioridade': 'alta' if carga_desproporcional['tarefas_por_dia'] > 5 else 'media'
            })

        # SUGESTÃO 2: PROJETO ATRASADO (SPI BAIXO) - SÓ SE TIVER +1 TAREFA
        if spi < 0.9 and total_tarefas > 1 and tarefas_atrasadas > 0:
            descricao = f"Priorize as {tarefas_atrasadas} tarefas atrasadas. "
            descricao += "Foque nas atividades críticas do caminho para retomar o cronograma. "
            descricao += f"O projeto está com {dias_atraso} dias de atraso."
            
            sugestoes.append({
                'id': 'priorizar_atrasadas',
                'titulo': 'Priorizar Tarefas Atrasadas',
                'descricao': descricao,
                'acao': 'priorizar_atrasadas',
                'prioridade': 'alta' if spi < 0.7 else 'media'
            })
        
        # SUGESTÃO 3: PERFORMANCE INSUSTENTÁVEL (TCPI ALTO)
        if tcpi > 1.2:
            descricao = f"TCPI de {tcpi:.2f} indica necessidade de performance muito acima do planejado. "
            descricao += "Considere revisar escopo, alocar mais recursos ou renegociar prazos."
            
            sugestoes.append({
                'id': 'revisar_metas',
                'titulo': 'Revisar Metas do Projeto',
                'descricao': descricao,
                'acao': 'revisar_metas',
                'prioridade': 'alta'
            })
        
        # SUGESTÃO 4: PREVISÃO DE ATRASO (VAC NEGATIVO)
        if vac < -7:
            descricao = f"Previsão de {abs(vac):.0f} dias de atraso no término. "
            descricao += f"Restam {dias_restantes} dias. Avalie extensão de prazo ou redução de escopo."
            
            sugestoes.append({
                'id': 'ajustar_prazos',
                'titulo': 'Ajustar Prazos Finais',
                'descricao': descricao,
                'acao': 'ajustar_prazos', 
                'prioridade': 'alta' if vac < -14 else 'media'
            })
        
        # SUGESTÃO 5: CARGA DESBALANCEADA - SÓ SE TIVER +1 MEMBRO
        carga_desequilibrada = SistemaSugestoes._verificar_carga_desequilibrada(projeto)
        if carga_desequilibrada['desequilibrio'] and carga_desequilibrada['total_usuarios'] > 1:
            descricao = f"Distribua melhor as tarefas. Diferença de {carga_desequilibrada['diferenca']} tarefas entre membros. "
            descricao += f"Membro mais sobrecarregado: {carga_desequilibrada['maior_carga']} tarefas. "
            descricao += f"Membro menos carregado: {carga_desequilibrada['menor_carga']} tarefas."
            
            sugestoes.append({
                'id': 'balancear_carga',
                'titulo': 'Balancear Carga de Trabalho',
                'descricao': descricao,
                'acao': 'balancear_carga',
                'prioridade': 'media'
            })
        
        # SUGESTÃO 6: BAIXA TAXA DE CONCLUSÃO COM PRAZO CURTO
        if taxa_conclusao < 50 and dias_restantes < 7:
            descricao = f"Apenas {taxa_conclusao}% concluído com {dias_restantes} dias restantes. "
            descricao += "Foque nas tarefas críticas e considere trabalho extra para cumprir o prazo."
            
            sugestoes.append({
                'id': 'acelerar_conclusao',
                'titulo': 'Acelerar Conclusão',
                'descricao': descricao,
                'acao': 'acelerar_conclusao',
                'prioridade': 'alta'
            })
        
        # SUGESTÃO 7: PROJETO SAUDÁVEL
        if spi >= 1.0 and tcpi <= 1.1 and vac >= 0 and taxa_conclusao > 70:
            sugestoes.append({
                'id': 'manter_ritmo',
                'titulo': 'Manter Ritmo Atual',
                'descricao': 'Projeto está no caminho certo! Continue com o bom trabalho e mantenha o foco na conclusão.',
                'acao': 'manter_ritmo',
                'prioridade': 'baixa'
            })
        
        return sorted(sugestoes, key=lambda x: {'alta': 3, 'media': 2, 'baixa': 1}[x['prioridade']], reverse=True)
    
    @staticmethod
    def _verificar_carga_desproporcional(tarefas_pendentes, dias_restantes, projeto):
        """Verifica se a carga de trabalho é desproporcional aos dias restantes"""
        if dias_restantes <= 0 or tarefas_pendentes <= 0:
            return {'desproporcional': False, 'tarefas_por_dia': 0}
        
        # Calcular tarefas por dia necessárias
        tarefas_por_dia = tarefas_pendentes / dias_restantes
        
        # Verificar desbalanceamento entre membros
        carga_equipe = SistemaSugestoes._verificar_carga_desequilibrada(projeto)
        desbalanceamento_equipe = carga_equipe['desequilibrio']
        
        # Considerar desproporcional se:
        # - Mais de 3 tarefas por dia necessárias OU
        # - Mais de 2 tarefas por dia E há desbalanceamento na equipe
        desproporcional = (tarefas_por_dia > 3) or (tarefas_por_dia > 2 and desbalanceamento_equipe)
        
        return {
            'desproporcional': desproporcional,
            'tarefas_por_dia': tarefas_por_dia,
            'desbalanceamento_equipe': desbalanceamento_equipe
        }
    
    @staticmethod
    def _verificar_carga_desequilibrada(projeto):
        """Verifica desbalanceamento na carga de trabalho da equipe"""
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
            return {'desequilibrio': False, 'diferenca': 0, 'total_usuarios': 0}
        
        diferenca = max(cargas) - min(cargas)
        return {
            'desequilibrio': diferenca > 3,
            'diferenca': diferenca,
            'maior_carga': max(cargas),
            'menor_carga': min(cargas),
            'total_usuarios': len(cargas)
        }
