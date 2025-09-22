# tests.py
import os
import django
import sys
from datetime import timedelta

# Configura o Django
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importações Django
from django.utils import timezone

# Importações dos seus models
from api.models import Project, User, UserProject, ProjectRole, Phase, ProjectPhase, Task, TaskAssignee

# Importações do ML
from api.ml.predictor import PredictorAtraso
from api.ml.sugestoes import GeradorSugestoes
from api.utils.ml_metrics import calcular_metricas_projeto

def testar_projeto_problematico():
    """Testa um projeto cheio de problemas para gerar sugestões"""
    print("\n" + "🚨" * 20)
    print("🚨 TESTANDO PROJETO PROBLEMÁTICO")
    print("🚨" * 20)
    
    try:
        # Criar usuário se não existir
        user, created = User.objects.get_or_create(
            email="problema@test.com",
            defaults={
                'username': 'userproblema',
                'password': 'testpass123', 
                'full_name': 'Usuário Problema'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        # Criar projeto SUPER PROBLEMÁTICO
        projeto = Project.objects.create(
            name="🚨 PROJETO EM CRISE",
            description="Projeto com todos os problemas possíveis",
            start_date=timezone.now() - timedelta(days=60),  # 2 meses atrás
            end_date=timezone.now() + timedelta(days=3)      # Só 3 dias restantes!
        )
        
        # Adicionar usuários (para testar distribuição de carga)
        UserProject.objects.create(user=user, project=projeto, role=ProjectRole.LEADER)
        
        # Criar outro usuário para ter carga desbalanceada
        user2, _ = User.objects.get_or_create(
            email="user2@test.com",
            defaults={
                'username': 'user2',
                'password': 'testpass123',
                'full_name': 'Usuário Dois'
            }
        )
        UserProject.objects.create(user=user2, project=projeto, role=ProjectRole.MEMBER)
        
        # Criar fases
        fase1 = Phase.objects.create(name="Fase Atrasada")
        fase2 = Phase.objects.create(name="Fase Crítica")
        
        pp1 = ProjectPhase.objects.create(project=projeto, phase=fase1)
        pp2 = ProjectPhase.objects.create(project=projeto, phase=fase2)
        
        print("📋 Criando tarefas problemáticas...")
        
        # Tarefas MUITO ATRASADAS (5 tarefas)
        for i in range(5):
            task = Task.objects.create(
                title=f"Tarefa Atrasada {i+1}",
                description=f"Tarefa extremamente atrasada {i+1}",
                is_completed=False,
                due_date=timezone.now() - timedelta(days=20),  # 20 dias atrasada!
                project_phase=pp1
            )
            # Atribuir todas ao primeiro usuário (sobrecarregar)
            TaskAssignee.objects.create(task=task, user=user)
        
        # Tarefas com prazos ULTRA CURTOS (3 tarefas)
        for i in range(3):
            task = Task.objects.create(
                title=f"Tarefa Urgente {i+1}",
                description=f"Tarefa com prazo curtíssimo {i+1}",
                is_completed=False, 
                due_date=timezone.now() + timedelta(days=1),  # Só 1 dia!
                project_phase=pp2
            )
        
        # Apenas 1 tarefa concluída de 8 (progresso horrível)
        task_concluida = Task.objects.create(
            title="Única tarefa concluída",
            description="Apenas esta foi feita",
            is_completed=True,
            due_date=timezone.now() - timedelta(days=10),
            project_phase=pp1
        )
        
        print("✅ Projeto problemático criado!")
        print(f"   • 8 tarefas criadas (7 pendentes, 1 concluída)")
        print(f"   • 5 tarefas atrasadas em 20 dias")
        print(f"   • 3 tarefas com prazo de 1 dia")
        print(f"   • Apenas 12.5% de progresso")
        print(f"   • 3 dias restantes no projeto")
        
        return projeto
        
    except Exception as e:
        print(f"❌ Erro ao criar projeto problemático: {e}")
        import traceback
        traceback.print_exc()
        return None

def testar_sugestoes_intensivo():
    """Teste focado em gerar sugestões"""
    print("\n" + "💡" * 20)
    print("💡 TESTE INTENSIVO DE SUGESTÕES")
    print("💡" * 20)
    
    # Criar projeto problemático
    projeto = testar_projeto_problematico()
    if not projeto:
        print("❌ Não foi possível criar projeto para teste")
        return
    
    # Calcular métricas
    metricas = calcular_metricas_projeto(projeto.id)
    if not metricas:
        print("❌ Não foi possível calcular métricas")
        return
        
    print(f"\n📊 MÉTRICAS DO DESASTRE:")
    print(f"   • Progresso: {metricas['taxa_conclusao']}% (PÉSSIMO)")
    print(f"   • Tarefas atrasadas: {metricas['tarefas_atrasadas']} (CRÍTICO)")
    print(f"   • Dias restantes: {metricas['dias_restantes']} (EMERGÊNCIA)")
    print(f"   • Carga usuários: {metricas['carga_usuarios']} (DESBALANCEADA)")
    
    # Testar predição
    predictor = PredictorAtraso()
    probabilidade = predictor.prever_probabilidade_atraso(projeto)
    
    print(f"\n🎯 PROBABILIDADE DE ATRASO: {probabilidade}%")
    
    if probabilidade > 70:
        print("🚨 ALERTA VERMELHO: Projeto em risco extremo!")
    elif probabilidade > 40:
        print("⚠️ ALERTA AMARELO: Projeto em risco moderado")
    else:
        print("✅ SITUAÇÃO CONTROLADA")
    
    # Gerar sugestões
    print(f"\n💡 GERANDO SUGESTÕES DE EMERGÊNCIA...")
    sugestoes = GeradorSugestoes.gerar_sugestoes(projeto)
    
    print(f"🎯 SUGESTÕES GERADAS: {len(sugestoes)}")
    
    if sugestoes:
        for i, sug in enumerate(sugestoes, 1):
            print(f"\n{i}. {sug['titulo']}")
            print(f"   📌 Prioridade: {sug['prioridade'].upper()}")
            print(f"   📝 Descrição: {sug['descricao']}")
            print(f"   ⚡ Ação: {sug['acao']}")
            if 'detalhes' in sug:
                print(f"   🔍 Detalhes: {sug['detalhes']}")
    else:
        print("❌ NENHUMA SUGESTÃO GERADA")
        print("💡 Dica: Verifique as regras no GeradorSugestoes")
    
    # Salvar resultados
    projeto.probabilidade_atraso = probabilidade
    projeto.save()
    
    print(f"\n💾 Resultados salvos no projeto '{projeto.name}'")
    print("✅ Teste de sugestões concluído!")

# Função original de teste (opcional)
def testar_sistema_ml():
    print("🚀 INICIANDO TESTE DO SISTEMA DE ML")
    print("=" * 50)
    
    try:
        projetos = Project.objects.all()
        print(f"📁 Projetos encontrados no banco: {projetos.count()}")
        
        if not projetos.exists():
            print("❌ Nenhum projeto encontrado. Criando um de teste...")
            # Você pode adicionar a função criar_projeto_teste() aqui se quiser
            return
        
        for i, projeto in enumerate(projetos, 1):
            print(f"\n🎯 TESTANDO PROJETO {i}: {projeto.name}")
            print("-" * 30)
            
            metricas = calcular_metricas_projeto(projeto.id)
            if metricas:
                print(f"   • Total tarefas: {metricas['total_tarefas']}")
                print(f"   • Tarefas concluídas: {metricas['tarefas_concluidas']}")
                print(f"   • Tarefas atrasadas: {metricas['tarefas_atrasadas']}")
                print(f"   • Taxa conclusão: {metricas['taxa_conclusao']}%")
                print(f"   • Dias restantes: {metricas['dias_restantes']}")
            
            predictor = PredictorAtraso()
            probabilidade = predictor.prever_probabilidade_atraso(projeto)
            print(f"   • Probabilidade de atraso: {probabilidade}%")
            
            sugestoes = GeradorSugestoes.gerar_sugestoes(projeto)
            print(f"   • Sugestões geradas: {len(sugestoes)}")
            
            projeto.probabilidade_atraso = probabilidade
            projeto.save()
            
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Escolha qual teste executar:
    
    # Teste normal dos projetos existentes
    # testar_sistema_ml()
    
    # Teste INTENSIVO de sugestões (RECOMENDADO)
    testar_sugestoes_intensivo()