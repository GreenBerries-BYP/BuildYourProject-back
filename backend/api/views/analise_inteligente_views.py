from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from api.analytics.analisador_desempenho import AnalisadorDesempenho
from api.analytics.sistema_sugestoes import SistemaSugestoes
from api.models import Project, Task, UserProject, TaskAssignee
from django.utils import timezone

@method_decorator(csrf_exempt, name='dispatch')
class AnalisarProjetoView(View):
    """
    View para análise de desempenho do projeto usando EVM
    Base: PMBOK Guide 7th Edition, NASA EVM Handbook, ANSI/EIA-748
    """
    
    def post(self, request, project_id):
        try:
            projeto = Project.objects.get(id=project_id)
            analisador = AnalisadorDesempenho()
            sistema_sugestoes = SistemaSugestoes()
            
            # Análise de desempenho EVM
            analise_desempenho = analisador.analisar_situacao_projeto(projeto)
            
            if 'erro' in analise_desempenho:
                return JsonResponse({
                    'sucesso': False,
                    'erro': analise_desempenho['erro']
                }, status=400)
            
            # Gerar sugestões baseadas em métricas
            sugestoes = sistema_sugestoes.gerar_sugestoes(projeto)
            
            # Calcular probabilidade de atraso baseada em múltiplas métricas
            probabilidade_atraso = self._calcular_probabilidade_atraso(analise_desempenho)
            
            resposta = {
                'sucesso': True,
                'status': analise_desempenho['status'],
                'cor': analise_desempenho['cor'],
                'explicacao': analise_desempenho['explicacao'],
                'dias_restantes': analise_desempenho['dias_restantes'],
                'tarefas_atrasadas': analise_desempenho['tarefas_atrasadas'],
                'tarefas_pendentes': analise_desempenho['tarefas_pendentes'],
                'taxa_conclusao': analise_desempenho['taxa_conclusao'],
                'probabilidade_atraso': probabilidade_atraso,
                'sugestoes': sugestoes,
                'projeto_concluido': analise_desempenho['projeto_concluido'],
                'dias_atraso': analise_desempenho['dias_atraso']
            }
            
            return JsonResponse(resposta)
            
        except Project.DoesNotExist:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Projeto não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': f'Erro na análise: {str(e)}'
            }, status=500)
    
    def _calcular_probabilidade_atraso(self, analise_desempenho):
        """Calcular probabilidade de atraso baseada em múltiplas métricas"""
        if analise_desempenho['projeto_concluido']:
            return 0
            
        probabilidade = 0
        spi = analise_desempenho.get('spi_calculado', 1.0)
        tarefas_atrasadas = analise_desempenho['tarefas_atrasadas']
        dias_atraso = analise_desempenho['dias_atraso']
        taxa_conclusao = analise_desempenho['taxa_conclusao']
        dias_restantes = analise_desempenho['dias_restantes']
        tarefas_pendentes = analise_desempenho['tarefas_pendentes']
        
        # Fator SPI (25% do peso)
        if spi < 0.7:
            probabilidade += 25
        elif spi < 0.9:
            probabilidade += 15
        elif spi < 1.0:
            probabilidade += 5
        
        # Fator Tarefas Atrasadas (20% do peso)
        if tarefas_atrasadas > 5:
            probabilidade += 20
        elif tarefas_atrasadas > 2:
            probabilidade += 10
        elif tarefas_atrasadas > 0:
            probabilidade += 5
        
        # Fator Dias de Atraso (20% do peso)
        if dias_atraso > 14:
            probabilidade += 20
        elif dias_atraso > 7:
            probabilidade += 15
        elif dias_atraso > 0:
            probabilidade += 10
        
        # Fator Pressão do Tempo (20% do peso)
        if taxa_conclusao < 50 and dias_restantes < 7:
            probabilidade += 20
        elif taxa_conclusao < 70 and dias_restantes < 14:
            probabilidade += 10
        
        # Fator Carga Desproporcional (15% do peso)
        if dias_restantes > 0 and tarefas_pendentes > 0:
            tarefas_por_dia = tarefas_pendentes / dias_restantes
            if tarefas_por_dia > 3:
                probabilidade += 15
            elif tarefas_por_dia > 2:
                probabilidade += 10
        
        return min(95, probabilidade)

@method_decorator(csrf_exempt, name='dispatch')
class AplicarSugestaoView(View):
    """
    View para aplicar sugestões automáticas no projeto
    Base: PMBOK Guide, NASA EVM Handbook, APM Guidelines
    """
    
    def post(self, request, project_id):
        try:
            data = json.loads(request.body)
            sugestao_id = data.get('sugestao_id')
            acao = data.get('acao')
            
            projeto = Project.objects.get(id=project_id)
            
            # Aplicar ações baseadas no tipo
            if acao == 'priorizar_atrasadas':
                resultado = self._aplicar_priorizacao_atrasadas(projeto)
            elif acao == 'revisar_metas':
                resultado = self._aplicar_revisao_metas(projeto)
            elif acao == 'ajustar_prazos':
                resultado = self._aplicar_ajuste_prazos(projeto)
            elif acao == 'balancear_carga':
                resultado = self._aplicar_balanceamento_carga(projeto)
            elif acao == 'acelerar_conclusao':
                resultado = self._aplicar_acelerar_conclusao(projeto)
            elif acao == 'otimizar_carga':
                resultado = self._aplicar_otimizar_carga(projeto)
            else:
                return JsonResponse({
                    'sucesso': False,
                    'erro': 'Ação não reconhecida'
                }, status=400)
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': resultado['mensagem'],
                'acao_aplicada': acao,
                'detalhes': resultado.get('detalhes', {})
            })
            
        except Project.DoesNotExist:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Projeto não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': f'Erro ao aplicar sugestão: {str(e)}'
            }, status=500)
    
    def _aplicar_priorizacao_atrasadas(self, projeto):
        """Priorizar tarefas atrasadas - Base: PMBOK Guide Gerenciamento de Tempo"""
        tarefas_atrasadas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            due_date__lt=timezone.now()
        ).order_by('due_date')
        
        tarefas_atualizadas = 0
        for tarefa in tarefas_atrasadas:
            if hasattr(tarefa, 'priority'):
                tarefa.priority = min(tarefa.priority + 1, 3)
                tarefa.save()
                tarefas_atualizadas += 1
        
        return {
            'mensagem': f'Prioridade aumentada para {tarefas_atualizadas} tarefas atrasadas',
            'detalhes': {
                'tarefas_afetadas': tarefas_atualizadas
            }
        }
    
    def _aplicar_revisao_metas(self, projeto):
        """Revisar metas do projeto - Base: ANSI/EIA-748"""
        from ..utils.metricas_projeto import calcular_metricas_projeto
        
        metricas = calcular_metricas_projeto(projeto.id)
        dias_extensao = 7
        
        if metricas and metricas['tcpi'] > 1.2:
            dias_extensao = max(7, int((metricas['tcpi'] - 1.0) * 10))
        
        return {
            'mensagem': f'Metas revisadas - Sugerida extensão de {dias_extensao} dias',
            'detalhes': {
                'dias_extensao_sugeridos': dias_extensao
            }
        }
    
    def _aplicar_ajuste_prazos(self, projeto):
        """Ajustar prazos finais - Base: NASA EVM Handbook"""
        from ..utils.metricas_projeto import calcular_metricas_projeto
        
        metricas = calcular_metricas_projeto(projeto.id)
        
        if metricas and metricas['vac'] < -7:
            dias_necessarios = abs(int(metricas['vac']))
            
            return {
                'mensagem': f'Ajuste de prazos - {dias_necessarios} dias adicionais necessários',
                'detalhes': {
                    'dias_necessarios': dias_necessarios
                }
            }
        
        return {
            'mensagem': 'Prazos mantidos - Não há necessidade de ajuste significativo',
            'detalhes': {}
        }
    
    def _aplicar_balanceamento_carga(self, projeto):
        """Balancear carga de trabalho - Base: APM Guidelines"""
        usuarios = UserProject.objects.filter(project=projeto)
        cargas = []
        
        for up in usuarios:
            tarefas_pendentes = Task.objects.filter(
                project_phase__project=projeto,
                is_completed=False,
                taskassignee__user=up.user
            ).count()
            cargas.append(tarefas_pendentes)
        
        if cargas and (max(cargas) - min(cargas) > 3):
            return {
                'mensagem': f'Balanceamento sugerido - Diferença de {max(cargas) - min(cargas)} tarefas entre membros',
                'detalhes': {
                    'diferenca': max(cargas) - min(cargas)
                }
            }
        
        return {
            'mensagem': 'Carga balanceada - Distribuição adequada',
            'detalhes': {}
        }
    
    def _aplicar_acelerar_conclusao(self, projeto):
        """Acelerar conclusão de tarefas críticas"""
        tarefas_criticas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            due_date__lte=timezone.now() + timezone.timedelta(days=3)
        )
        
        tarefas_afetadas = tarefas_criticas.count()
        
        return {
            'mensagem': f'Foco em {tarefas_afetadas} tarefas críticas com prazo próximo',
            'detalhes': {
                'tarefas_criticas': tarefas_afetadas
            }
        }
    
    def _aplicar_otimizar_carga(self, projeto):
        """Otimizar carga de trabalho desproporcional"""
        from ..utils.metricas_projeto import calcular_metricas_projeto
        from ..analytics.sistema_sugestoes import SistemaSugestoes
        
        metricas = calcular_metricas_projeto(projeto.id)
        if not metricas:
            return {
                'mensagem': 'Não foi possível analisar a carga de trabalho',
                'detalhes': {}
            }
        
        tarefas_pendentes = metricas['total_tarefas'] - metricas['tarefas_concluidas']
        dias_restantes = metricas['dias_restantes']
        
        if dias_restantes > 0:
            tarefas_por_dia = tarefas_pendentes / dias_restantes
            return {
                'mensagem': f'Otimização sugerida - {tarefas_por_dia:.1f} tarefas/dia necessárias. Considere redistribuir carga.',
                'detalhes': {
                    'tarefas_por_dia': round(tarefas_por_dia, 1),
                    'tarefas_pendentes': tarefas_pendentes,
                    'dias_restantes': dias_restantes
                }
            }
        
        return {
            'mensagem': 'Análise de carga concluída',
            'detalhes': {}
        }
