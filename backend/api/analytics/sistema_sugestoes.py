from ..utils.metricas_projeto import calcular_metricas_projeto
from ..models import UserProject, Task, TaskAssignee

class SistemaSugestoes:
    """
    SISTEMA DE SUGESTÕES INTELIGENTES BASEADO EM MÉTRICAS EVM
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
        
        # ✅ VERIFICAR SE PROJETO ESTÁ FINALIZADO
        if metricas['taxa_conclusao'] >= 99.9:
            return []  # Retorna array vazio = sem sugestões
        
        spi = metricas['spi']
        tcpi = metricas['tcpi']
        vac = metricas['vac']
        tarefas_atrasadas = metricas['tarefas_atrasadas']
        dias_restantes = metricas['dias_restantes']
        taxa_conclusao = metricas['taxa_conclusao']
        
        # 🔴 SUGESTÃO 1: PROJETO ATRASADO (TAREFAS ATRASADAS)
        if tarefas_atrasadas > 0:
            sugestoes.append({
                'id': 'priorizar_atrasadas',
                'titulo': '🎯 Priorizar Tarefas Atrasadas',
                'descricao': f'{tarefas_atrasadas} tarefas estão com prazo vencido',
                'acao': 'priorizar_atrasadas',
                'prioridade': 'alta' if tarefas_atrasadas > 5 else 'media'
            })
        
        # 🔴 SUGESTÃO 2: PERFORMANCE INSUSTENTÁVEL
        if tcpi > 1.2:
            sugestoes.append({
                'id': 'revisar_metas',
                'titulo': '📈 Revisar Metas do Projeto',
                'descricao': 'O ritmo atual não é suficiente para cumprir os prazos',
                'acao': 'revisar_metas',
                'prioridade': 'alta'
            })
        
        # 🔴 SUGESTÃO 3: OTIMIZAR PROCESSOS (SUBSTITUI AJUSTE DE PRAZO)
        if vac < -7:
            sugestoes.append({
                'id': 'otimizar_processos',
                'titulo': '⚡ Otimizar Processos',
                'descricao': f'Identificamos oportunidades para ganhar eficiência e recuperar {abs(round(vac))} dias',
                'acao': 'otimizar_processos',
                'prioridade': 'alta' if vac < -14 else 'media'
            })
        
        # 🔴 SUGESTÃO 4: CARGA DESBALANCEADA
        carga_desequilibrada = SistemaSugestoes._verificar_carga_desequilibrada(projeto)
        if carga_desequilibrada['desequilibrio']:
            sugestoes.append({
                'id': 'balancear_carga',
                'titulo': '⚖️ Balancear Carga de Trabalho',
                'descricao': f"Distribuição desigual de tarefas entre a equipe",
                'acao': 'balancear_carga',
                'prioridade': 'media'
            })
        
        # 🔴 SUGESTÃO 5: BAIXA TAXA DE CONCLUSÃO
        if taxa_conclusao < 30 and dias_restantes < 7:
            sugestoes.append({
                'id': 'acelerar_conclusao',
                'titulo': '🚀 Acelerar Conclusão',
                'descricao': f'Progresso insuficiente com prazo próximo',
                'acao': 'acelerar_conclusao',
                'prioridade': 'alta'
            })
        
        # 🔵 SUGESTÃO 6: PROJETO SAUDÁVEL
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
