import time
import random
from typing import Any, Dict, Optional
from ..utilities.logger import CORTEX_LOGGER
from ..core.protocol import AgentMessage, AgentResponse # Dependência do protocolo

class NetworkSimulator:
    """
    Simula latência, falha e erros de I/O de rede para testar a resiliência do CERNE e dos Agentes.
    """
    
    def __init__(self, base_latency_ms: int = 50, failure_rate: float = 0.05):
        """
        Inicializa o simulador com parâmetros padrão.
        :param base_latency_ms: Latência mínima garantida em milissegundos.
        :param failure_rate: Probabilidade de falha da conexão (0.0 a 1.0).
        """
        self.base_latency = base_latency_ms
        self.failure_rate = failure_rate
        self.max_additional_latency = 200 # Latência máxima adicional (em ms)
        CORTEX_LOGGER.info(
            f"NetworkSimulator ativo. Latência base: {base_latency_ms}ms, Falha: {failure_rate*100:.1f}%.",
            extra_data={'latency_ms': base_latency_ms, 'failure_rate': failure_rate}
        )
        
    def _simulate_delay(self):
        """Adiciona latência aleatória ao tempo de execução."""
        delay_ms = self.base_latency + random.randint(0, self.max_additional_latency)
        delay_s = delay_ms / 1000.0
        time.sleep(delay_s)
        return delay_ms

    def simulate_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Simula uma requisição de rede e aplica latência/falha.
        :returns: Dicionário simulando uma resposta de dados.
        :raises ConnectionError: Se a falha for disparada.
        """
        delay = self._simulate_delay()
        
        # 1. Simulação de Falha
        if random.random() < self.failure_rate:
            CORTEX_LOGGER.error(f"Simulação de Falha de Rede no endpoint: {endpoint}.", 
                                extra_data={'latency': delay, 'endpoint': endpoint})
            raise ConnectionError(f"Simulação: Falha de conexão ao {endpoint}.")
        
        # 2. Simulação de Resposta de Sucesso
        CORTEX_LOGGER.info(f"Requisição simulada com sucesso.", 
                           extra_data={'latency': delay, 'endpoint': endpoint})
                           
        # Retorna um payload de resposta simulada
        return {
            "status": "OK",
            "message": f"Dados recebidos do {endpoint}",
            "processed_delay_ms": delay,
            "original_data_hash": hash(str(data))
        }

# --- Instância Singleton para Acesso ---

NETWORK_SIMULATOR = NetworkSimulator()
