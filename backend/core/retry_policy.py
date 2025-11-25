# backend/core/retry_policy.py
import time
from typing import Optional

# Mapeamento de backoff exponencial: Tentativa -> Tempo de espera (em segundos)
# Ex: 1ª tentativa espera 5s, 2ª espera 15s, etc.
BACKOFF_POLICY = {
    1: 5,   # Primeira retentativa
    2: 15,  # Segunda retentativa
    3: 30,  # Terceira retentativa
    4: 60,  # Quarta retentativa (1 minuto)
}

MAX_RETRIES = max(BACKOFF_POLICY.keys())

class RetryPolicy:
    """Implementa a lógica de backoff exponencial para tarefas com falha temporária."""

    @staticmethod
    def get_wait_time(retry_count: int) -> Optional[int]:
        """
        Retorna o tempo de espera em segundos para o dado número de retentativas.
        :param retry_count: O número da tentativa de execução (1, 2, 3...).
        :return: Tempo de espera em segundos ou None se exceder o limite.
        """
        return BACKOFF_POLICY.get(retry_count)

    @staticmethod
    def should_retry(retry_count: int) -> bool:
        """Verifica se a tarefa ainda está dentro do limite máximo de retentativas."""
        return retry_count < MAX_RETRIES

