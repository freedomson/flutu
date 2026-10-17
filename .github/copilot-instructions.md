# Instruções do projeto para o Copilot

## Autenticação obrigatória

- Todas as novas páginas e funcionalidades privadas devem exigir a autenticação comum do projeto.
- A proteção deve ser validada no servidor em cada rota; ocultar links ou proteger apenas no frontend não é suficiente.
- Se não houver sessão válida, redirecione páginas HTML para `/` (login). APIs devem responder `401` em JSON, sem executar a ação protegida.
- Novos links para páginas privadas só devem aparecer depois do login, no dashboard ou na página privada que seja o seu pai.

## Hierarquia de páginas e navegação

- O dashboard (`/dashboard`) é a raiz da área autenticada e o nível 1.
- Páginas acessíveis diretamente a partir do dashboard são nível 2 e devem oferecer navegação de retorno ao dashboard.
- Páginas acessíveis a partir de uma página de nível 2 são nível 3 e devem retornar à página de nível 2 que as abriu. Continue esse padrão para todos os níveis: cada página retorna ao seu pai imediato, nunca automaticamente ao login ou à raiz, exceto quando a página atual já for o dashboard.
- Registre as novas páginas nos links do respetivo pai e nas rotas do servidor, mantendo a hierarquia de navegação visível e previsível.
- Ao criar uma página, identifique o seu pai, implemente o link “Voltar” para esse pai e proteja a rota no servidor usando a sessão comum.
