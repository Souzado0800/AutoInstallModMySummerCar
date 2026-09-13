# AutoInstallModMySummerCar

O **AutoInstallModMySummerCar** é um instalador inteligente e automático de mods para o jogo **My Summer Car** (compatível com MSCLoader e MSCLoader Pro).

Você só precisa colocar seus arquivos `.zip` ou `.rar` dentro da pasta `mods` e dar dois cliques no `run.bat` (ou no `AutoInstallModMySummerCar.exe`). O programa cuida de todo o resto sozinho: analisa os arquivos, descobre onde cada um deve ficar, organiza as pastas e instala tudo no lugar certo.

Sem menus complicados, sem perguntas chatas a cada mod e sem necessidade de instalar o Python no computador.

---

## Como usar

1. Coloque seus arquivos `.zip` ou `.rar` dentro da pasta `mods`.
2. Dê um duplo clique no arquivo `run.bat` (ou execute `AutoInstallModMySummerCar.exe`).
3. Na primeira vez, confirme onde está sua pasta `Mods` do jogo.
4. Pronto! Seus mods foram instalados.

Nas próximas vezes que quiser instalar novos mods, basta colocar os arquivos em `mods` e abrir o `run.bat` novamente. O programa instala os novos e não perde tempo reinstalando o que já foi instalado.

---

## Primeira execução

Na primeira vez que você abrir o programa:

1. **Apoio ao projeto**: Você verá uma mensagem rápida do desenvolvedor. Você pode pressionar `[G]` para abrir o repositório no GitHub e deixar uma estrela (Star ⭐) se o projeto te ajudar, ou apenas pressionar `[ENTER]` para continuar. Deixar a estrela é totalmente opcional e não bloqueia nada!
2. **Localização da pasta Mods**: O programa procura automaticamente sua pasta `Mods` nas 3 localizações padrão do MSCLoader:
   - Pasta do jogo na Steam (`steamapps\common\My Summer Car\Mods`)
   - Meus Documentos (`Documents\My Summer Car\Mods`)
   - AppData LocalLow (`AppData\LocalLow\Amistech\My Summer Car\Mods`)
3. Se ele encontrar sua pasta, basta apertar `[ENTER]` para confirmar. Se você usa uma pasta diferente, basta colar o caminho dela.
4. Esse caminho fica salvo no seu computador. Nas próximas execuções, o programa não pergunta mais nada e vai direto ao ponto.

> **Precisa trocar a pasta de Mods depois?**  
> Basta executar via prompt de comando: `AutoInstallModMySummerCar.exe --reconfigure`

---

## O que o programa faz por baixo dos panos

Você não precisa entender de programação para usar, mas é legal saber como ele funciona:

```text
Lê os mods na pasta "mods"
   ↓
Analisa o conteúdo de cada ZIP/RAR
   ↓
Identifica o tipo de cada arquivo
   ↓
Consulta a memória local
   ↓
Compara com o que já está instalado no jogo
   ↓
Instala somente o que for novo ou alterado
   ↓
Faz backup e confirma que está tudo certo
```

### Detecção inteligente
O programa abre cada arquivo compactado e entende o que ele é:
- **Mod principal** (`.dll`)
- **Pacotes de textura** (incluindo versões 4K e HD)
- **Addons e expansões** de mods existentes
- **Patches e correções**
- **Traduções** e arquivos de configuração
- **Pastas de Assets** (ele sabe exatamente para onde cada pasta de som ou textura deve ir)

Se você baixar, por exemplo, o mod principal e um pacote de texturas 4K separado, ele reconhece que os dois pertencem ao mesmo mod e instala na ordem certa.

### Sistema de memória
O programa guarda uma memória dos arquivos já processados:
- **Não reinstala à toa**: se o mod já está instalado e os arquivos continuam intactos no jogo, ele pula em milissegundos.
- **Atualizações automáticas**: se você baixar uma versão mais nova de um mod, ele percebe a alteração, cria um backup da versão anterior na pasta `_Backups` e atualiza com segurança.
- **Reparo automático**: se algum arquivo do mod foi apagado ou alterado acidentalmente na sua pasta do jogo, ele detecta e restaura automaticamente.

---

## Estrutura do projeto

```text
AutoInstallModMySummerCar/
├── AutoInstallModMySummerCar.exe  # O programa principal compilado (Windows x64)
├── README.md                      # Este guia explicativo
├── requirements.txt               # Informações de dependências
├── run.bat                        # Atalho de 1 clique para iniciar no Windows
└── mods/                          # Pasta onde você coloca seus arquivos .zip e .rar
```

---

## Requisitos

- **Windows 10 ou 11 (64-bit)**
- **MSCLoader** ou **MSCLoader Pro** instalado no My Summer Car
- **Zero configuração**: o programa já vem pré-compilado e pronto para uso, dispensando a instalação de Python ou dependências manuais pelo usuário final.

---

## Apoie o Desenvolvedor

Este é um projeto gratuito e de código aberto desenvolvido por **Souza ([Souzado0800](https://github.com/Souzado0800))**.

Se este instalador economizou seu tempo e te ajudou a jogar My Summer Car com seus mods favoritos, deixe uma estrela no repositório!

⭐ **GitHub**: https://github.com/Souzado0800/AutoInstallModMySummerCar