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
            
            # Calcular probabilidade de atraso baseada no SPI
            spi = analise_desempenho['spi']
            probabilidade_atraso = self._calcular_probabilidade_atraso(spi)
            
            resposta = {
                'sucesso': True,
                'status': analise_desempenho['status'],
                'cor': analise_desempenho['cor'],
                'explicacao': analise_desempenho['explicacao'],
                'spi': analise_desempenho['spi'],
                'sv': analise_desempenho['sv'],
                'tcpi': analise_desempenho['tcpi'],
                'eac': analise_desempenho['eac'],
                'vac': analise_desempenho['vac'],
                'dias_restantes': analise_desempenho['dias_restantes'],
                'tarefas_atrasadas': analise_desempenho['tarefas_atrasadas'],
                'taxa_conclusao': analise_desempenho['taxa_conclusao'],
                'probabilidade_atraso': probabilidade_atraso,
                'sugestoes': sugestoes
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
    
    def _calcular_probabilidade_atraso(self, spi):
        """Calcular probabilidade de atraso baseada no SPI"""
        if spi >= 1.0:
            return 10
        elif spi >= 0.9:
            return 25
        elif spi >= 0.7:
            return 60
        else:
            return 85

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