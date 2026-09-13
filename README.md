# 🚗 My Summer Car - Smart Auto Mod Installer

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Compatibility](https://img.shields.io/badge/MSCLoader-Ready-brightgreen.svg)](https://www.nexusmods.com/mysummercar/mods/147)
[![Automation](https://img.shields.io/badge/Modo-100%25%20Automático-orange.svg)](#como-funciona)
[![Tests](https://img.shields.io/badge/Testes-27%2F27%20Passando-success.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Instalador e gerenciador inteligente, autônomo e de alta performance de mods para **My Summer Car** (compatível com **MSCLoader**). 

Projetado com uma filosofia **100% autônoma e sem menus interativos**: você simplesmente baixa os arquivos `.zip` e `.rar` dos mods diretamente para a pasta **Downloads**, executa o instalador com um único clique e ele analisa, classifica, resolve caminhos, cria backups, instala e valida a integridade física de tudo automaticamente.

---

## 🌟 Principais Recursos

- **🚀 100% Automático e Sem Menus**: Zero perguntas repetitivas, zero menus `[1]`, `[2]`, `[3]`. Executa do início ao fim em segundos.
- **🧠 Banco de Memória Persistente Local (`installed_mods.json`)**:
  - Salva o estado de cada mod instalado (nome original, hash SHA-256 do arquivo baixado, hashes dos arquivos em `Mods/`, versões e histórico).
  - **Fast-Path**: Na próxima execução, verifica a integridade em microssegundos e ignora arquivos já instalados sem tocar no disco ou descompactar nada.
  - **Auto-Reparo**: Se você apagar ou modificar manualmente um arquivo em `Mods/`, o instalador detecta a divergência e restaura automaticamente.
  - **Recuperação com Backup Automático**: Mantém cópia espelho em `installed_mods.json.bak` com substituição atômica contra quedas de energia ou corrupção.
- **📦 Resolução Inteligente e Conservadora de Estrutura**:
  - Elimina pastas de container redundantes (como `Mods/`, `NomeDoMod/Mods/`) sem alterar estruturas legítimas.
  - Roteamento dinâmico de pacotes de assets/texturas que omitem a pasta `Assets/` na raiz.
  - Vinculação inteligente de texturas e modelos soltos na raiz diretamente à pasta de assets correspondente (`Mods/Assets/<ModName>/`).
- **🛡️ Isolamento Seguro de Conflitos (`Cross-Mod Collision Isolation`)**:
  - Rastreamento de propriedade de arquivos instalados (`file_ownership`).
  - Bibliotecas idênticas compartilhadas (ex.: `RaycastCore.dll` com mesmo hash) são aproveitadas sem sobrescritas.
  - Conflitos de arquivos divergentes entre mods distintos são isolados: o arquivo existente é preservado, um aviso é registrado e os demais componentes do mod são instalados com sucesso.
- **🔒 Segurança e Transacionalidade**:
  - **Proteção contra Zip Slip / Path Traversal**: Impede que arquivos maliciosos com `../../` alcancem pastas fora do diretório `Mods`.
  - **Quarentena de Executáveis**: Bloqueia a extração de scripts ou executáveis suspeitos (`.exe`, `.bat`, `.cmd`, `.ps1`, `.vbs`, etc.).
  - **Backups Automáticos com Timestamp**: Todo arquivo sobrescrito recebe uma cópia prévia em `Mods/_Backups/`.
  - **Rollback Atômico**: Se ocorrer erro durante a extração ou falha de integridade, todas as alterações são revertidas e os backups restaurados.
- **📁 Suporte Unificado a ZIP e RAR**:
  - Suporta arquivos `.zip` nativamente e `.rar` via biblioteca `rarfile` ou diretamente por executáveis de linha de comando (`UnRAR.exe` do WinRAR ou `7z.exe` do 7-Zip).
- **📝 Gestão Limpa de READMEs**:
  - Converte documentações (`README.txt`, `leiame.txt`, etc.) para Markdown padronizado com cabeçalho: `readme(NomeDoMod).md`, `readme(NomeDoMod_2).md`, sem poluição visual.

---

## 📋 Estrutura de Pastas Suportadas

O instalador é **100% generalista** (não possui regras hardcoded para nomes de mods específicos). Ele analisa a estrutura real de cada arquivo:

| Estrutura Interna do Arquivo Compactado | Ação Realizada pelo Instalador | Local de Instalação em `Mods/` |
| :--- | :--- | :--- |
| `Mods/arquivo.dll` | Remove o container redundante `Mods/`. | `Mods/arquivo.dll` |
| `NomeDoMod/Mods/arquivo.dll` | Remove o prefixo até o container `Mods/`. | `Mods/arquivo.dll` |
| `arquivo.dll` (raiz do ZIP/RAR) | Instala diretamente na pasta raiz de Mods. | `Mods/arquivo.dll` |
| `Assets/Mod/modelo.unity3d` | Preserva a estrutura padrão de assets. | `Mods/Assets/Mod/modelo.unity3d` |
| `Mod/textura.png` (pacote sem DLL) | Inspeciona `Mods/Assets/` e ancora sob `Assets/`. | `Mods/Assets/Mod/textura.png` |
| `textura.png` (solto na raiz) | Direciona para a pasta de assets do Mod Principal. | `Mods/Assets/<ModPrincipal>/textura.png` |
| Múltiplas DLLs no mesmo pacote | Extrai e mapeia cada DLL individualmente. | Todas as DLLs em `Mods/` |

---

## 🚀 Como Usar

### Instalação em 1 Clique (Recomendado)

1. Baixe os mods (`.zip` ou `.rar`) do [Nexus Mods](https://www.nexusmods.com/mysummercar) para a sua pasta **Downloads**.
2. Dê um duplo-clique em **`Run_MySummerCarModInstaller.bat`**.
3. O script detectará automaticamente o Python instalado no sistema (incluindo versões do Blender, Python oficial ou py launcher) e executará o instalador:

```text
========================================================
       MY SUMMER CAR SMART AUTO MOD INSTALLER
========================================================

Analisando Downloads...

24 arquivos compactados encontrados.

[1/24] AutoFuel 1.3-1801-1-3-1682251911.zip...
      MAIN FILE | 83% confiança
      ✓ Já instalado — ignorado
[2/24] Better Graphics-4103-2-0-1761421573.zip...
      MAIN FILE | 83% confiança
      → Novo mod detectado → Instalando...
      ✓ Instalado com sucesso!
...
========================================================
                    CONCLUÍDO
========================================================
Mods analisados  : 24
Novos instalados : 1
Atualizados      : 0
Já instalados    : 23
Ignorados        : 0
Conflitos        : 0
Erros            : 0

Tempo total      : 5.45s
========================================================
```

---

### Execução via Linha de Comando (CLI)

Você também pode executar diretamente via terminal e personalizar as pastas de origem e destino:

```bash
# Execução padrão (detecta ~/Downloads e o Steam automaticamente)
python MySummerCarModInstaller.py

# Especificando caminhos personalizados
python MySummerCarModInstaller.py --downloads "D:\MeusModsMSC" --mods "D:\SteamLibrary\steamapps\common\My Summer Car\Mods"
```

---

## 🧪 Suíte de Testes Automatizados (27 Testes)

O repositório inclui uma suíte exaustiva de testes automatizados com cobertura completa:

1. **Testes de Integração e Segurança** (`tests/test_integration.py` - 10 testes):
   - Leitura de ZIP real e RAR real (`Lights On Switches.rar`).
   - Agrupamento inteligente Main + 4K e diferenciação de sequências (`Mod` vs `Mod 2`).
   - Bloqueio rigoroso de Zip Slip / Path Traversal (`../../`).
   - Resolução conservadora de pastas e renomeação de READMEs.
   - Cálculo SHA-256 e backups automáticos.

2. **Testes de Memória e Resiliência** (`tests/test_memory.py` - 12 cenários):
   - Primeira execução e gravação do banco de memória.
   - Fast-path de verificação (pula sem descompactar).
   - Detecção de arquivos renomeados ou atualizados no Downloads.
   - Auto-reparo de arquivos deletados ou modificados externamente.
   - Recuperação automática de banco de dados corrompido via `.bak`.
   - Rollback transacional atômico após erro de instalação.

3. **Testes de Auditoria Generalista** (`tests/test_audit.py` - 5 testes):
   - Subpastas de texturas sem prefixo `Assets/`.
   - Texturas soltas na raiz vinculadas a mod existente.
   - Isolamento de colisão entre mods distintos preservando arquivos existentes.
   - Compartilhamento de dependências idênticas (0 conflitos).
   - Numeração sequencial de READMEs sem colisões.

### Executando os Testes

Dê um duplo clique em **`tests\run_tests.bat`** ou execute via Python:

```bash
python tests/run_all_tests.py
```

---

## 📁 Estrutura do Repositório

```text
MySummerCar-SmartModInstaller/
├── MySummerCarModInstaller.py      # Script principal do instalador
├── Run_MySummerCarModInstaller.bat # Launcher de 1 clique com auto-detecção de Python
├── install_dependencies.bat        # Instalador opcional de dependências
├── requirements.txt                # Dependências opcionais (rarfile)
├── LICENSE                         # Licença MIT
├── README.md                       # Documentação completa do projeto
├── .gitignore                      # Configuração de arquivos ignorados no Git
├── src/
│   ├── __init__.py
│   └── MySummerCarModInstaller.py  # Cópia modular do código-fonte
└── tests/
    ├── __init__.py
    ├── run_all_tests.py            # Executor consolidado dos 27 testes
    ├── run_tests.bat               # Launcher de 1 clique para testes
    ├── test_integration.py         # 10 testes de integração e segurança
    ├── test_memory.py              # 12 testes de memória persistente e automação
    └── test_audit.py               # 5 testes de regras generalistas e colisões
```

---

## ⚙️ Requisitos

- **Sistema Operacional**: Windows 10 ou Windows 11 (64-bit).
- **Python**: Python 3.8 ou superior (funciona perfeitamente com qualquer distribuição Python padrão, py launcher ou Blender Python).
- **Descompactador de RAR (Opcional)**: [WinRAR](https://www.win-rar.com/) (`UnRAR.exe`) ou [7-Zip](https://www.7-zip.org/) (`7z.exe`) caso possua arquivos `.rar` compactados no formato RAR5.

---

## 📄 Licença

Este projeto está licenciado sob os termos da licença [MIT](LICENSE).
Sinta-se livre para usar, modificar e distribuir.
