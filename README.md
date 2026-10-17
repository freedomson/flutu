# flutu

Projeto inicial criado para servir como base para desenvolvimento.

## Como executar

Configure as credenciais do Google em `.env` (use `.env.example` como modelo) e inicie o servidor:

```bash
bash start_server.sh
```

Acesse http://localhost:8000. O script carrega as variáveis de `.env` antes de iniciar o servidor; não inicie diretamente com `python3 server.py` se quiser usar o Login do Google.

Depois de entrar, o dashboard mostra o link **Escolher um caminho**. A página e sua API exigem a autenticação comum. Cada toque em **Escolher por mim** pede uma nova permutação aleatória à ANU. A página mostra apenas a direção escolhida, sem exibir o conjunto.

## Verificar o último número de um conjunto

A interface de demonstração fica em http://localhost:8000/permutation-checker. A API recebe um array `set` e retorna o booleano JSON `true` quando o último valor é maior que 1, ou `false` caso contrário:

```http
POST /api/check-last-number
Content-Type: application/json

{"set": [1, 2]}
```

A página de decisão usa `POST /api/decision`, que consulta uma nova permutação aleatória a cada chamada e retorna `{"go_right": true}` ou `{"go_right": false}`.

## Reinício automático pelo Copilot

O hook `.github/hooks/restart-app.json` reinicia o servidor após alterações do agente em `server.py`, `decision.html`, `permutation-checker.html` ou `start_server.sh`. Ele compara hashes para não reiniciar após operações que não alteraram esses arquivos. O processo é iniciado em segundo plano com as configurações de `.env`; consulte o log em `/tmp/flutu-server.log` se o servidor não iniciar.
