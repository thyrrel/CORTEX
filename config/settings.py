"""
Gerenciador central de configurações do C.O.R.T.E.X.
Suporta hot-reload e criptografia de valores sensíveis.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class Config:
    """Gerenciador de configurações com hot-reload."""
    
    def __init__(self):
        self.config_path = Path("config/settings.json")
        self.observer = None
        self._config = {}
        
    async def load_config(self):
        """Carrega as configurações do arquivo."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
            else:
                # Configurações padrão
                self._config = self._default_config()
                self.save_config()
                
            # Inicia monitoramento de mudanças
            self._start_watching()
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            raise
            
    def _default_config(self) -> Dict[str, Any]:
        """Retorna configurações padrão."""
        return {
            "version": "1.0.0",
            "debug": False,
            "log_level": "INFO",
            "voice_enabled": True,
            "headless": False,
            "network": {
                "scan_interval": 30,
                "timeout": 5,
                "ports": [22, 80, 443, 8080, 1883, 5683],
                "exclude_ranges": ["127.0.0.0/8", "10.0.0.0/8"]
            },
            "iot": {
                "protocols": ["mqtt", "coap", "http", "websocket"],
                "auto_discovery": True,
                "credentials_path": "config/iot_creds.json"
            },
            "ai": {
                "model_path": "models/",
                "confidence_threshold": 0.8,
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "security": {
                "encryption_key": None,  # Gerado automaticamente
                "rotate_keys_interval": 86400,  # 24 horas
                "max_login_attempts": 5,
                "session_timeout": 3600
            },
            "apis": {
                "openai": None,
                "anthropic": None,
                "google": None,
                "local": "http://localhost:11434"
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any):
        """Define um valor de configuração."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        
    def save_config(self):
        """Salva as configurações no arquivo."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
                
            logger.info("Configurações salvas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            
    def _start_watching(self):
        """Inicia monitoramento de mudanças no arquivo."""
        class ConfigHandler(FileSystemEventHandler):
            def __init__(self, config_instance):
                self.config = config_instance
                
            def on_modified(self, event):
                if event.src_path == str(self.config.config_path):
                    asyncio.create_task(self.config.load_config())
                    
        handler = ConfigHandler(self)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.config_path.parent), recursive=False)
        self.observer.start()
      
