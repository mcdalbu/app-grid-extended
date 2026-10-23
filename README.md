# App Grid Soft

Repositório: [mcdalbu/app-grid-soft](https://github.com/mcdalbu/app-grid-soft).

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

Baixe o pacote `app-grid-soft@local_v2.zip` na
[versão v2](https://github.com/mcdalbu/app-grid-soft/releases/tag/v2).
Na pasta do arquivo baixado:

```bash
gnome-extensions install app-grid-soft@local_v2.zip
```

Encerre a sessão e entre novamente para o GNOME reconhecer a extensão nova.
Depois ative:

```bash
gnome-extensions enable app-grid-soft@local
```

Para desativar:

```bash
gnome-extensions disable app-grid-soft@local
```

## Ajustes

Abra as preferências pelo aplicativo **Extensões** ou execute:

```bash
gnome-extensions prefs app-grid-soft@local
```

Os quatro controles são aplicados imediatamente e salvos entre sessões.
O botão **Restaurar** recupera os valores padrão do Dash to Dock Soft.
Valores negativos deslocam a sombra para a esquerda ou para cima; desfoque zero
produz uma sombra nítida. Opacidade zero deixa a sombra invisível.

Para gerar novamente o pacote, execute `make`. Para atualizar a versão 1, use:

```bash
gnome-extensions install --force app-grid-soft@local_v2.zip
```

Encerre e reabra a sessão para carregar a nova versão. Os ajustes seguintes nas
preferências não exigem reiniciar a sessão nem reativar a extensão.

A extensão é independente do Dash to Dock Soft; mudanças futuras nas preferências
do dock não são sincronizadas. Seu CSS se limita às grades de aplicativos.
A folha de estilo temporária é atualizada quando os parâmetros ou o tema mudam e
removida ao desativar a extensão. Não há timers, efeitos de blur ou alterações em
métodos do Shell. As configurações usam o schema próprio
`org.gnome.shell.extensions.app-grid-soft`.

Compatibilidade declarada: GNOME Shell 45–50 (módulos ESM). Validação local no
GNOME Shell 50.6; outras versões precisam de verificação nas respectivas sessões.

## Validação

Para gerar o pacote a partir do código-fonte, execute `make`. O empacotamento
requer `make`, `zip` e `glib-compile-schemas`.

```bash
make
/usr/bin/python3 tests/headless.py
```

A verificação de integração usa GNOME Shell 50 numa sessão Wayland e D-Bus
isolada, com configurações temporárias. Confere alterações ao vivo, limites,
escala, troca de tema, persistência, remoção do efeito e vínculos das preferências.
Resultados em `validation/gnome50-results.json`. O helper que permite avaliar
código existe apenas na sessão de teste e não é incluído no ZIP.

Licença: GPL-2.0-or-later; veja `COPYING`.
