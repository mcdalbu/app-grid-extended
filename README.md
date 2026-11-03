# App Grid Extended

Repositório: [mcdalbu/app-grid-extended](https://github.com/mcdalbu/app-grid-extended).

Extensão simples para adicionar sombra ao desenho dos ícones na página de
aplicativos do GNOME Shell, incluindo as miniaturas das pastas e os aplicativos
dentro delas.

Usa os mesmos valores padrão da sombra dos ícones do **Dash to Dock Soft v20**,
também encontrados na configuração local consultada:

| Parâmetro | Padrão | Intervalo |
| --- | --- | --- |
| Cor | Preto | Fixa |
| Opacidade | 24% | 0–100% |
| Deslocamento horizontal | 0 px | −32 a 32 px |
| Deslocamento vertical | 2 px | −32 a 32 px |
| Desfoque | 4 px | 0–32 px |

Os valores são em pixels lógicos e acompanham a escala do GNOME Shell.
A sombra usa `icon-shadow`, seguindo o contorno do ícone.

## Instalação

Baixe o pacote `app-grid-extended@local_v3.zip` na
[versão v3](https://github.com/mcdalbu/app-grid-extended/releases/tag/v3).
Na pasta do arquivo baixado:

```bash
gnome-extensions install app-grid-extended@local_v3.zip
```

Encerre a sessão e entre novamente para o GNOME reconhecer a extensão nova.
Depois ative:

```bash
gnome-extensions enable app-grid-extended@local
```

Para desativar:

```bash
gnome-extensions disable app-grid-extended@local
```

## Ajustes

Abra as preferências pelo aplicativo **Extensões** ou execute:

```bash
gnome-extensions prefs app-grid-extended@local
```

Os quatro controles são aplicados imediatamente e salvos entre sessões.
O botão **Restaurar** recupera os valores padrão do Dash to Dock Soft.
Valores negativos deslocam a sombra para a esquerda ou para cima; desfoque zero
produz uma sombra nítida. Opacidade zero deixa a sombra invisível.

Para gerar novamente o pacote, execute `make`. Para atualizar uma instalação do App Grid Extended, use:

```bash
gnome-extensions install --force app-grid-extended@local_v3.zip
```

Encerre e reabra a sessão para carregar a nova versão. Os ajustes seguintes nas
preferências não exigem reiniciar a sessão nem reativar a extensão.

A extensão é independente do Dash to Dock Soft; mudanças futuras nas preferências
do dock não são sincronizadas. Seu CSS se limita às grades de aplicativos.
A folha de estilo temporária é atualizada quando os parâmetros ou o tema mudam e
removida ao desativar a extensão. Não há timers, efeitos de blur ou alterações em
métodos do Shell. As configurações usam o schema próprio
`org.gnome.shell.extensions.app-grid-extended`.

Compatibilidade declarada: GNOME Shell 45–51 (módulos ESM). Validação local no
GNOME Shell 51.1; outras versões precisam de verificação nas respectivas sessões.

## Validação

Para gerar o pacote a partir do código-fonte, execute `make`. O empacotamento
requer `make`, `zip` e `glib-compile-schemas`.

```bash
make
/usr/bin/python3 tests/headless.py
```

A verificação de integração usa a versão instalada do GNOME Shell numa sessão Wayland e D-Bus
isolada, com configurações temporárias. Confere alterações ao vivo, limites,
escala, troca de tema, persistência, remoção do efeito e vínculos das preferências.
Resultados em `validation/gnome51-results.json`. O helper que permite avaliar
código existe apenas na sessão de teste e não é incluído no ZIP.

Licença: GPL-2.0-or-later; veja `COPYING`.

## Migração do App Grid Soft

A versão 3 passa a se chamar **App Grid Extended**, com UUID
`app-grid-extended@local`. Antes de ativá-la, desative a instalação antiga:

```bash
gnome-extensions disable app-grid-soft@local
gnome-extensions install app-grid-extended@local_v3.zip
```

Encerre a sessão, entre novamente e ative `app-grid-extended@local`.
O schema passa a ser `org.gnome.shell.extensions.app-grid-extended`, mas mantém
o caminho de armazenamento `/org/gnome/shell/extensions/app-grid-soft/` para
preservar os quatro ajustes existentes. Não ative as duas extensões juntas.

## Versão 3

Renomeia o projeto, o pacote, o UUID e o schema para App Grid Extended.
Inclui suporte declarado ao GNOME Shell 51 e validação de integração no 51.1.
O teste lê a versão e o UUID dos metadados e verifica o pacote que será publicado.
