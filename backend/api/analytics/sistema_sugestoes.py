from ..utils.metricas_projeto import calcular_metricas_projeto
from ..models import UserProject, Task, TaskAssignee

class SistemaSugestoes:
    """
    SISTEMA DE SUGESTÕES INTELIGENTES CORRIGIDO
    """
    
    @staticmethod
    def gerar_sugestoes(projeto):
        """
        Gera sugestões contextuais baseadas em análise realista do projeto
        """
        sugestoes = []
        metricas = calcular_metricas_projeto(projeto.id)
        
        if not metricas:
            return sugestoes
        
        # ✅ VERIFICAR SE PROJETO ESTÁ FINALIZADO
        if metricas['taxa_conclusao'] >= 99.9:
            return []  # Retorna array vazio = sem sugestões
        
        spi = metricas['spi']
        tcpi = metricas['tcpi']
        vac = metricas['vac']
        tarefas_atrasadas = metricas['tarefas_atrasadas']
        tarefas_pendentes = metricas['tarefas_pendentes']
        dias_restantes = metricas['dias_restantes']
        taxa_conclusao = metricas['taxa_conclusao']
        projeto_atrasado = metricas['projeto_atrasado']
        
        # 🔴 SUGESTÃO 1: PROJETO ATRASADO (TAREFAS ATRASADAS) - COM INFO ESPECÍFICA
        if tarefas_atrasadas > 0:
            sugestoes.append({
                'id': 'priorizar_atrasadas',
                'titulo': '🎯 Priorizar Tarefas Atrasadas',
                'descricao': f'Existem {tarefas_atrasadas} tarefas com prazo vencido que precisam de atenção imediata',
                'acao': 'priorizar_atrasadas',
                'prioridade': 'alta'
            })
        
        # 🔴 SUGESTÃO 2: PROJETO CRÍTICO - DATA FINAL JÁ PASSOU
        if projeto_atrasado and tarefas_pendentes > 0:
            sugestoes.append({
                'id': 'revisao_urgente',
                'titulo': '🚨 Revisão Urgente do Projeto',
                'descricao': f'O projeto está {abs(metricas["dias_restantes"])} dias atrasado com {tarefas_pendentes} tarefas pendentes',
                'acao': 'revisao_urgente',
                'prioridade': 'alta'
            })
        
        # 🔴 SUGESTÃO 3: PERFORMANCE INSUSTENTÁVEL
        if tcpi > 1.5:
            sugestoes.append({
                'id': 'revisar_metas',
                'titulo': '📈 Revisar Metas Realistas',
                'descricao': f'O ritmo necessário (TCPI: {tcpi:.2f}) é muito alto. Considere replanejar',
                'acao': 'revisar_metas',
                'prioridade': 'alta'
            })
        
        # 🔴 SUGESTÃO 4: OTIMIZAR PROCESSOS (SUBSTITUI AJUSTE DE PRAZO)
        if vac < -7:
            sugestoes.append({
                'id': 'otimizar_processos',
                'titulo': '⚡ Otimizar Processos',
                'descricao': f'Identificamos oportunidades para ganhar eficiência e recuperar {abs(round(vac))} dias',
                'acao': 'otimizar_processos',
                'prioridade': 'alta' if vac < -14 else 'media'
            })
        
        # 🔴 SUGESTÃO 5: CARGA DESBALANCEADA
        carga_desequilibrada = SistemaSugestoes._verificar_carga_desequilibrada(projeto)
        if carga_desequilibrada['desequilibrio']:
            sugestoes.append({
                'id': 'balancear_carga',
                'titulo': '⚖️ Balancear Carga de Trabalho',
                'descricao': f"Distribuição desigual: {carga_desequilibrada['maior_carga']} vs {carga_desequilibrada['menor_carga']} tarefas por pessoa",
                'acao': 'balancear_carga',
                'prioridade': 'media'
            })
        
        # 🔴 SUGESTÃO 6: BAIXA TAXA DE CONCLUSÃO COM PRAZO CURTO
        if taxa_conclusao < 50 and dias_restantes < (metricas['total_dias'] * 0.2):
            sugestoes.append({
                'id': 'foco_conclusao',
                'titulo': '🚀 Foco na Conclusão',
                'descricao': f'Apenas {taxa_conclusao}% concluído com prazo próximo. Priorize tarefas essenciais',
                'acao': 'foco_conclusao',
                'prioridade': 'alta'
            })
        
        # 🔵 SUGESTÃO 7: PROJETO SAUDÁVEL
        if spi >= 1.0 and tcpi <= 1.1 and vac >= 0 and tarefas_atrasadas == 0:
            sugestoes.append({
                'id': 'manter_ritmo',
                'titulo': '✅ Manter Ritmo Atual',
                'descricao': 'Projeto está no caminho certo! Continue com o bom trabalho',
                'acao': 'manter_ritmo',
                'prioridade': 'baixa'
            })
        
        return sorted(sugestoes, key=lambda x: {'alta': 3, 'media': 2, 'baixa': 1}[x['prioridade']], reverse=True)
    
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
            return {'desequilibrio': False, 'diferenca': 0}
        
        diferenca = max(cargas) - min(cargas)
        return {
            'desequilibrio': diferenca > 3,
            'diferenca': diferenca,
            'maior_carga': max(cargas),
            'menor_carga': min(cargas)
        }
