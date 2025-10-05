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