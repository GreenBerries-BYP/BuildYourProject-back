from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from api.analytics.analisador_desempenho import AnalisadorDesempenho
from api.analytics.sistema_sugestoes import SistemaSugestoes
from api.models import Project

@method_decorator(csrf_exempt, name='dispatch')
class AnalisarProjetoView(View):
    """
    View para análise de desempenho do projeto usando EVM
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
            
            # Gerar sugestões
            sugestoes = sistema_sugestoes.gerar_sugestoes(projeto)
            
            # Calcular probabilidade de atraso
            probabilidade_atraso = self._calcular_probabilidade_atraso(analise_desempenho)
            
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
                'tarefas_pendentes': analise_desempenho['tarefas_pendentes'],  # ✅ ADICIONADO
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
    
    def _calcular_probabilidade_atraso(self, analise_desempenho):
        """Calcular probabilidade de atraso baseada em métricas EXISTENTES"""
        if analise_desempenho.get('status') == "CONCLUÍDO":
            return 0
            
        probabilidade = 0
        spi = analise_desempenho['spi']
        tarefas_atrasadas = analise_desempenho['tarefas_atrasadas']
        taxa_conclusao = analise_desempenho['taxa_conclusao']
        dias_restantes = analise_desempenho['dias_restantes']
        tarefas_pendentes = analise_desempenho['tarefas_pendentes']  # ✅ AGORA EXISTE
        
        # Baseado no SPI (50% do peso)
        if spi < 0.7:
            probabilidade += 50
        elif spi < 0.9:
            probabilidade += 30
        elif spi < 1.0:
            probabilidade += 10
        
        # Baseado em tarefas atrasadas (30% do peso)
        if tarefas_atrasadas > 5:
            probabilidade += 30
        elif tarefas_atrasadas > 2:
            probabilidade += 20
        elif tarefas_atrasadas > 0:
            probabilidade += 10
        
        # Baseado em pressão de tempo (20% do peso)
        if taxa_conclusao < 50 and dias_restantes < 7:
            probabilidade += 20
        
        return min(95, probabilidade)


@method_decorator(csrf_exempt, name='dispatch')
class AplicarSugestaoView(View):
    """
    View para aplicar sugestões automáticas no projeto
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
            elif acao == 'manter_ritmo':
                resultado = self._aplicar_manter_ritmo(projeto)
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
        """Priorizar tarefas atrasadas"""
        from api.models import Task
        from django.utils import timezone
        
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
        """Revisar metas do projeto"""
        from ..utils.metricas_projeto import calcular_metricas_projeto
        
        metricas = calcular_metricas_projeto(projeto.id)
        dias_extensao = 7
        
        if metricas and metricas.get('tcpi', 1.0) > 1.2:
            dias_extensao = max(7, int((metricas['tcpi'] - 1.0) * 10))
        
        return {
            'mensagem': f'Metas revisadas - Sugerida extensão de {dias_extensao} dias',
            'detalhes': {
                'dias_extensao_sugeridos': dias_extensao
            }
        }
    
    def _aplicar_ajuste_prazos(self, projeto):
        """Ajustar prazos finais"""
        from ..utils.metricas_projeto import calcular_metricas_projeto
        
        metricas = calcular_metricas_projeto(projeto.id)
        
        if metricas and metricas.get('vac', 0) < -7:
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
        """Balancear carga de trabalho"""
        from api.models import UserProject, Task, TaskAssignee
        
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
        from api.models import Task
        from django.utils import timezone
        
        tarefas_criticas = Task.objects.filter(
            project_phase__project=projeto,
            is_completed=False,
            due_date__lte=timezone.now() + timezone.timedelta(days=3)
        )
        
        tarefas_afetadas = tarefas_criticas.count()
        
        return {
            'mensagem': f'Foco em {tarefas_afetadas} tarefas com prazo próximo',
            'detalhes': {
                'tarefas_criticas': tarefas_afetadas
            }
        }
    
    def _aplicar_manter_ritmo(self, projeto):
        """Manter ritmo atual - Ação positiva"""
        return {
            'mensagem': 'Ritmo mantido - Continue com o excelente trabalho!',
            'detalhes': {
                'status': 'positivo'
            }
        }
