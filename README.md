# flutu

Projeto inicial criado para servir como base para desenvolvimento.

## Como executar

Configure as credenciais do Google em `.env` (use `.env.example` como modelo) e inicie o servidor:

```bash
bash start_server.sh
```

Acesse http://localhost:8000. O script carrega as variáveis de `.env` antes de iniciar o servidor; não inicie diretamente com `python3 server.py` se quiser usar o Login do Google.
