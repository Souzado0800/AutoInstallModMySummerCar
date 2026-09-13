<div align="center">

# 🚗 AutoInstallModMySummerCar

**O instalador automático, inteligente e definitivo de mods para My Summer Car.**  
*Compatível com MSCLoader e MSCLoader Pro.*

[![GitHub Release](https://img.shields.io/badge/Release-v2.0-blue?style=for-the-badge&logo=github)](https://github.com/Souzado0800/AutoInstallModMySummerCar)
[![Platform](https://img.shields.io/badge/Plataforma-Windows%2010%20%2F%2011%20(64--bit)-0078D6?style=for-the-badge&logo=windows)](https://microsoft.com)
[![Status](https://img.shields.io/badge/Instalação-100%25%20Automática-success?style=for-the-badge)]()
[![License](https://img.shields.io/badge/Licença-MIT-yellow?style=for-the-badge)](LICENSE)

<br>

> **Chega de extrair arquivos manualmente e adivinhar onde colocar cada pasta.**  
> Coloque seus arquivos `.zip` e `.rar` na pasta `mods`, dê dois cliques no `run.bat` e pronto!

</div>

---

## ⚡ Como Usar (Super Rápido)

Instalar mods no My Summer Car nunca foi tão simples:

```
 1. COLOQUE OS MODS             2. EXECUTE                     3. PRONTO!
┌───────────────────────┐      ┌───────────────────────┐      ┌───────────────────────┐
│ Coloque seus .zip     │  ──► │ Dê 2 cliques no       │  ──► │ Mods instalados e     │
│ e .rar dentro da      │      │ arquivo:              │      │ organizados no jogo!  │
│ pasta "mods"          │      │   run.bat             │      │ Pode abrir o jogo.    │
└───────────────────────┘      └───────────────────────┘      └───────────────────────┘
```

> 💡 **Nas próximas vezes**: Basta colocar os novos mods na pasta `mods` e abrir o `run.bat` novamente. Ele só instala o que for novo e não perde tempo reinstalando o que já está pronto!

---

## ✨ Principais Vantagens

| Recurso | Como te ajuda |
| :--- | :--- |
| 🚀 **Zero Instalações** | O programa já vem compilado em executável (`.exe`). **Não precisa instalar Python** nem configurar nada no Windows. |
| 🧠 **Organização Inteligente** | Reconhece DLLs, pacotes de textura (incluindo 4K/HD), addons, patches, sons e pastas `Assets/`, colocando cada arquivo no seu devido lugar. |
| ⚡ **Memória Rápida (Fast-Path)** | Lembra de cada mod instalado através de hashes criptográficos. Se o mod já estiver no jogo, ele pula a verificação em frações de segundo. |
| 🔄 **Atualizações Seguras** | Se você baixar uma versão mais recente de um mod, ele atualiza automaticamente e cria um backup da versão anterior na pasta `_Backups`. |
| 🔧 **Reparo Automático** | Se algum arquivo do mod foi apagado por engano da sua pasta do jogo, o instalador detecta a ausência e restaura o arquivo original. |
| 🛡️ **Segurança Integrada** | Bloqueia scripts suspeitos (`.exe`, `.bat`, `.ps1`) dentro dos arquivos de mods e isola conflitos entre mods de autores diferentes. |

---

## 🔍 Como o Programa Funciona por Baixo dos Panos

```text
       Lê os arquivos na pasta "mods" (.zip e .rar)
                           ↓
        Analisa a estrutura interna de cada arquivo
                           ↓
    Identifica o papel (Mod Principal, Textura, Addon...)
                           ↓
             Consulta a memória persistente
                           ↓
        Compara com os arquivos instalados no jogo
         ├── Já instalado e intacto?  ──► Pula instantaneamente
         ├── Arquivo corrompido?     ──► Repara e restaura
         ├── Versão nova detectada?  ──► Cria backup e atualiza
         └── Mod inédito?            ──► Instala no lugar correto
                           ↓
      Grava o relatório de execução no log do sistema
```

---

## 🎮 Primeira Execução & Configuração

Na primeira vez que você abrir o `run.bat`:

1. **Apoio ao Projeto**: Será exibida uma mensagem do desenvolvedor. Você pode apertar `[G]` para abrir a página do GitHub e deixar uma estrela (Star ⭐) se o projeto te ajudar, ou apertar `[ENTER]` para continuar direto (a estrela é opcional!).
2. **Detecção da Pasta Mods**: O instalador verifica automaticamente as 3 localizações oficiais do MSCLoader:
   - 🎮 **Pasta do Jogo (Steam)**: `steamapps\common\My Summer Car\Mods`
   - 📂 **Meus Documentos**: `Documents\My Summer Car\Mods`
   - ⚙️ **AppData LocalLow**: `AppData\LocalLow\Amistech\My Summer Car\Mods`
3. Ele mostra a pasta encontrada na tela. Basta pressionar `[ENTER]` para confirmar.
4. **Pronto!** O caminho é salvo. Nas próximas vezes, o programa não pergunta nada e executa 100% no automático.

> 🔁 **Quer trocar a pasta de Mods no futuro?**  
> Abra o terminal na pasta do programa e execute:  
> `AutoInstallModMySummerCar.exe --reconfigure`

---

## 📁 Estrutura do Projeto

A distribuição é limpa, organizada e sem arquivos desnecessários:

```text
AutoInstallModMySummerCar/
│
├── AutoInstallModMySummerCar.exe   # Aplicativo principal compilado (Windows 64-bit)
├── README.md                       # Este guia de uso rápido
├── requirements.txt                # Informações de distribuição do projeto
├── run.bat                         # Atalho de 1 clique para executar facilmente
└── mods/                           # Pasta onde você coloca seus arquivos .zip e .rar
```

---

## 📋 Requisitos do Sistema

- **Sistema Operacional**: Windows 10 ou Windows 11 (64-bit)
- **Mod Loader**: [MSCLoader](https://www.nexusmods.com/mysummercar/mods/147) ou [MSCLoader Pro](https://www.nexusmods.com/mysummercar/mods/532) instalado no jogo
- **Arquivos Suportados**: Arquivos compactados nos formatos `.zip` e `.rar`

---

## ⭐ Apoie o Projeto

Este é um projeto gratuito e de código aberto desenvolvido por **Souzado0800**.  
Se este instalador facilitou sua jogatina e economizou seu tempo, deixe uma estrela no repositório!

👉 **Repositório Oficial**: [https://github.com/Souzado0800/AutoInstallModMySummerCar](https://github.com/Souzado0800/AutoInstallModMySummerCar)

---

## 📄 Licença

Distribuído sob a licença [MIT](LICENSE). Desenvolvido por **Souzado0800**.