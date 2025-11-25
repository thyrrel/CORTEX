from typing import Any, Dict
# Importamos a base de Worker do AgenteManager, pois CERNE lida com Workers
from .agente_manager import AgenteManager, WorkerBase, WorkerSimples 
# Nota: WorkerSimples é importado para uso na função de auto_modulacao,
# garantindo que o CERNE possa criar agentes ad-hoc para simulação.

class CERNE: 
    """
    O Kernel Lógico do C.O.R.T.E.X. (O Núcleo).
    Implementa o Loop de Raciocínio (Análise -> Delegação -> Execução) e a Orquestração de Workers.
    """
    
    def __init__(self, agente_manager: AgenteManager):
        self._manager = agente_manager
        print("CERNE (Kernel Lógico) ativado. Loop de Raciocínio pronto.")

    def auto_modulacao(self, purpose: str = "Teste Simples") -> WorkerBase:
        """
        Função de Auto-Modulação: Cria agentes ad-hoc para testes ou simulações.
        Garante nomenclatura coerente (Agente_*).
        """
        # Nomenclatura ajustada para Agente_Simulacao
        agent_name = f"Agente_{purpose.replace(' ', '_')}" 
        print(f"Auto-Modulação: Criando agente de simulação '{agent_name}'.")
        # Cria um worker simples (WorkerSimples) independentemente do modo principal.
        return WorkerSimples(name=agent_name)

    def processar_tarefa(self, task_desc: str, required_agent: str) -> str:
        """Executa o Loop de Raciocínio simplificado: Análise -> Delegação -> Execução."""
        print(f"\n--- Processando Tarefa em CERNE: '{task_desc}' ---")
        
        # 1. Análise (Simplificada)
        if "simulação" in task_desc.lower():
             worker = self.auto_modulacao(purpose="Simulacao_Teste")
        else:
            # 2. Delegação
            try:
                worker = self._manager.get_agent(required_agent)
            except ValueError as e:
                return f"Erro de Delegação: {e}"
        
        # 3. Execução
        resultado = worker.execute_task(task_data=task_desc)
        return resultado
