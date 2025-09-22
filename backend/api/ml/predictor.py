import numpy as np
from django.utils import timezone
from ..utils.ml_metrics import calcular_metricas_projeto

class PredictorAtraso:
    def __init__(self):
        # Inicialmente usaremos regras simples
        # Depois podemos treinar um modelo com dados reais
        pass
    
    def prever_probabilidade_atraso(self, projeto):
        """
        Prevê probabilidade de atraso usando regras de negócio
        """
        metricas = calcular_metricas_projeto(projeto.id)
        if not metricas:
            return 50.0  # Valor padrão se não conseguir calcular
        
        risco = 0
        
        # Regra 1: Pouco tempo restante
        if metricas['dias_restantes'] < 7:
            risco += 40
        elif metricas['dias_restantes'] < 14:
            risco += 20
        
        # Regra 2: Progresso lento
        if metricas['taxa_conclusao'] < 30:
            risco += 30
        elif metricas['taxa_conclusao'] < 50:
            risco += 15
        
        # Regra 3: Tarefas atrasadas
        if metricas['tarefas_atrasadas'] > 3:
            risco += 25
        elif metricas['tarefas_atrasadas'] > 1:
            risco += 10
        
        # Regra 4: Tarefas complexas
        if metricas['media_complexidade'] > 4.0:
            risco += 20
        elif metricas['media_complexidade'] > 3.0:
            risco += 10
        
        # Limitar entre 0-100%
        return min(100, max(0, risco))
