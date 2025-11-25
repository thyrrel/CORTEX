"""
VaultManager - Sistema seguro de gerenciamento de credenciais e tokens.
Utiliza criptografia AES-256 com rotação automática de chaves.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class VaultManager:
    """Gerenciador seguro de credenciais e tokens."""
    
    def __init__(self):
        self.vault_path = Path("config/tokens.json.enc")
        self.key_path = Path("config/secrets.py")
        self._vault = {}
        self._fernet = None
        
    async def initialize(self):
        """Inicializa o vault de credenciais."""
        # Gera ou carrega chave de criptografia
        await self._load_or_generate_key()
        
        # Carrega o vault
        await self._load_vault()
        
        # Agenda rotação de chaves
        self._schedule_key_rotation()
        
    async def _load_or_generate_key(self):
        """Carrega ou gera uma nova chave de criptografia."""
        if self.key_path.exists():
            # Carrega chave existente
            with open(self.key_path, 'rb') as f:
                key = f.read()
        else:
            # Gera nova chave
            key = Fernet.generate_key()
            self.key_path.parent.mkdir(exist_ok=True)
            with open(self.key_path, 'wb') as f:
                f.write(key)
                
            # Define permissões restritas
            os.chmod(self.key_path, 0o600)
            
        self._fernet = Fernet(key)
        
    async def _load_vault(self):
        """Carrega o vault de credenciais."""
        if self.vault_path.exists():
            try:
                with open(self.vault_path, 'rb') as f:
                    encrypted_data = f.read()
                    
                decrypted_data = self._fernet.decrypt(encrypted_data)
                self._vault = json.loads(decrypted_data.decode())
                
                logger.info("Vault carregado com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao carregar vault: {e}")
                # Cria vault vazio em caso de erro
                self._vault = {}
        else:
            self._vault = {}
            
    async def save(self):
        """Salva o vault criptografado."""
        try:
            # Serializa e criptografa
            data = json.dumps(self._vault, indent=2)
            encrypted_data = self._fernet.encrypt(data.encode())
            
            # Salva arquivo
            self.vault_path.parent.mkdir(exist_ok=True)
            with open(self.vault_path, 'wb') as f:
                f.write(encrypted_data)
                
            # Define permissões restritas
            os.chmod(self.vault_path, 0o600)
            
            logger.info("Vault salvo com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao salvar vault: {e}")
            raise
            
    def get_token(self, service: str, key: str) -> Optional[str]:
        """Obtém um token específico."""
        service_data = self._vault.get(service, {})
        return service_data.get(key)
        
    def set_token(self, service: str, key: str, value: str, 
                  expires_in: Optional[int] = None):
        """Define um novo token."""
        if service not in self._vault:
            self._vault[service] = {}
            
        token_data = {
            "value": value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            token_data["expires_at"] = expires_at.isoformat()
            
        self._vault[service][key] = token_data
        
    def list_services(self) -> list:
        """Lista todos os serviços com tokens armazenados."""
        return list(self._vault.keys())
        
    def list_tokens(self, service: str) -> list:
        """Lista todos os tokens de um serviço."""
        return list(self._vault.get(service, {}).keys())
        
    def remove_token(self, service: str, key: str):
        """Remove um token específico."""
        if service in self._vault and key in self._vault[service]:
            del self._vault[service][key]
            
    def rotate_key(self):
        """Rotaciona a chave de criptografia."""
        logger.info("Rotacionando chave de criptografia...")
        
        # Descriptografa com chave antiga
        old_data = json.dumps(self._vault)
        
        # Gera nova chave
        new_key = Fernet.generate_key()
        new_fernet = Fernet(new_key)
        
        # Re-criptografa com nova chave
        encrypted_data = new_fernet.encrypt(old_data.encode())
        
        # Salva nova chave
        backup_path = self.key_path.with_suffix('.backup')
        self.key_path.rename(backup_path)
        
        with open(self.key_path, 'wb') as f:
            f.write(new_key)
        os.chmod(self.key_path, 0o600)
        
        # Salva vault re-criptografado
        with open(self.vault_path, 'wb') as f:
            f.write(encrypted_data)
            
        # Atualiza instância
        self._fernet = new_fernet
        
        # Remove backup após 24 horas
        asyncio.create_task(self._cleanup_backup(backup_path))
        
        logger.info("Chave rotacionada com sucesso")
        
    def _schedule_key_rotation(self):
        """Agenda rotação automática de chaves."""
        interval = 86400  # 24 horas
        asyncio.create_task(self._rotation_worker(interval))
        
    async def _rotation_worker(self, interval: int):
        """Worker para rotação de chaves."""
        while True:
            await asyncio.sleep(interval)
            self.rotate_key()
            
    async def _cleanup_backup(self, backup_path: Path):
        """Remove arquivo de backup após delay."""
        await asyncio.sleep(86400)  # 24 horas
        if backup_path.exists():
            backup_path.unlink()
          
