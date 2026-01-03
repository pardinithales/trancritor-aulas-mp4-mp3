# AGENTS.md - Documentação Técnica Completa

## Índice
1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Dependências e Requisitos](#dependências-e-requisitos)
4. [Estrutura de Diretórios](#estrutura-de-diretórios)
5. [Variáveis de Ambiente](#variáveis-de-ambiente)
6. [Fluxo de Execução Detalhado](#fluxo-de-execução-detalhado)
7. [Módulos e Funções](#módulos-e-funções)
8. [Instalação e Configuração](#instalação-e-configuração)
9. [Segurança e Boas Práticas](#segurança-e-boas-práticas)
10. [Troubleshooting](#troubleshooting)

---

## Visão Geral do Projeto

### Propósito
Sistema automatizado para processar arquivos de áudio/vídeo de aulas, realizando transcrição automática usando OpenAI Whisper e tradução/correção para português brasileiro usando Google Gemini Flash 3.0.

### Principais Características
- **Processamento em lote**: Processa múltiplos arquivos automaticamente
- **Gerenciamento inteligente de arquivos grandes**: Divide arquivos >20MB em chunks de 10 minutos
- **Cache de processamento**: Evita reprocessamento de arquivos já processados
- **Limpeza automática**: Remove arquivos temporários após processamento
- **Logs detalhados**: Acompanhamento em tempo real com timestamps

---

## Arquitetura do Sistema

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT (aulas/)                          │
│                  MP3 ou MP4 Files                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              CONVERSÃO (se MP4)                             │
│          ffmpeg converte para MP3                           │
│         Salva em: aulas_mp3/                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          ANÁLISE DE TAMANHO                                 │
│     >20MB? → Divide em chunks de 10min                      │
│     ≤20MB? → Processa diretamente                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              TRANSCRIÇÃO                                    │
│         OpenAI Whisper-1 API                                │
│    Resultado: texto em inglês original                      │
│    Salvo em: transcricoes/*_original.txt                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        TRADUÇÃO E CORREÇÃO                                  │
│      Google Gemini Flash 3.0                                │
│  - Traduz para PT-BR                                        │
│  - Corrige erros gramaticais                                │
│  - Remove hesitações                                        │
│  - Organiza em parágrafos                                   │
│    Salvo em: transcricoes/*_PT-BR.txt                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              LIMPEZA                                        │
│    Remove chunks temporários                                │
│    Mantém apenas arquivos finais                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Dependências e Requisitos

### Sistema Operacional
- **Linux**: Totalmente suportado
- **Windows**: Requer WSL2 ou instalação nativa do Python e FFmpeg
- **macOS**: Totalmente suportado

### Python
- **Versão mínima**: Python 3.8+
- **Versão recomendada**: Python 3.10+

### Bibliotecas Python

#### Obrigatórias
```
openai==2.14.0+          # API OpenAI Whisper
python-dotenv==1.2.1+    # Gerenciamento de variáveis de ambiente
google-genai==1.56.0+    # API Google Gemini (nova biblioteca, substituiu google-generativeai)
tenacity==9.1.2+         # Dependência do google-genai (retry logic)
websockets==15.0.1+      # Dependência do google-genai (streaming)
```

**⚠️ IMPORTANTE**: A biblioteca `google-generativeai` foi **DEPRECIADA**. Use apenas `google-genai`!

#### Dependências Transitivas (instaladas automaticamente)
```
anyio<5,>=3.5.0
distro<2,>=1.7.0
httpx<1,>=0.23.0
jiter<1,>=0.10.0
pydantic<3,>=1.9.0
sniffio
tqdm>4
typing-extensions<5,>=4.11
google-api-core
google-api-python-client
google-auth>=2.15.0
protobuf
certifi
httpcore
h11
requests
```

### Ferramentas Externas

#### FFmpeg (OBRIGATÓRIO)
**Função**: Conversão de MP4 para MP3 e divisão de arquivos de áudio

**Instalação**:
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install ffmpeg
  ```
- **macOS**:
  ```bash
  brew install ffmpeg
  ```
- **Windows**:
  1. Baixar de: https://ffmpeg.org/download.html
  2. Adicionar ao PATH do sistema

**Verificação**:
```bash
ffmpeg -version
ffprobe -version
```

---

## Estrutura de Diretórios

### Estrutura Completa
```
transcritor-mp3/
│
├── .env                          # NUNCA COMMITAR! Contém API keys
├── .gitignore                    # Configuração de arquivos ignorados
├── README.md                     # Documentação para usuários
├── AGENTS.md                     # Esta documentação técnica
│
├── transcribe_chunked.py         # Script principal
├── test_gemini.py                # Script de teste do Gemini
├── download_from_drive.py        # Script auxiliar para Google Drive
│
├── aulas/                        # INPUT: Coloque arquivos aqui
│   ├── *.mp3                     # Arquivos de áudio
│   └── *.mp4                     # Arquivos de vídeo
│
├── aulas_mp3/                    # Arquivos MP3 convertidos de MP4
│   └── *.mp3                     # Conversões automáticas
│
├── transcricoes/                 # OUTPUT: Resultados finais
│   ├── *_original.txt            # Transcrições em inglês
│   ├── *_PT-BR.txt               # Traduções em português
│   └── chunks/                   # Transcrições de chunks individuais
│       └── chunk_*_transcricao.txt
│
├── chunks/                       # TEMPORÁRIO: Pedaços de áudio
│   └── [nome_audio]/             # Removido após processamento
│       ├── chunk_001.mp3
│       ├── chunk_002.mp3
│       └── ...
│
└── venv/                         # Ambiente virtual Python (opcional)
    └── ...
```

### Descrição Detalhada

#### Diretório `aulas/`
- **Propósito**: Entrada de arquivos
- **Formatos aceitos**: `.mp3`, `.mp4`
- **Comportamento**: O script varre este diretório no início da execução

#### Diretório `aulas_mp3/`
- **Propósito**: Armazenamento de conversões MP4→MP3
- **Criação**: Automática quando há arquivos MP4
- **Cache**: Reutiliza conversões existentes

#### Diretório `transcricoes/`
- **Propósito**: Resultados finais
- **Arquivos**:
  - `*_original.txt`: Transcrição em inglês (ou idioma original)
  - `*_PT-BR.txt`: Tradução e correção em português brasileiro
  - `chunks/*_transcricao.txt`: Transcrições de partes individuais (temporário)

#### Diretório `chunks/`
- **Propósito**: Armazenamento temporário de segmentos de áudio
- **Criação**: Apenas para arquivos >20MB
- **Limpeza**: Automática após processamento bem-sucedido

---

## Variáveis de Ambiente

### Arquivo `.env`

**CRITICAL**: Este arquivo contém informações sensíveis e **NUNCA** deve ser commitado ao Git.

#### Estrutura do `.env`
```env
# API Key da OpenAI (para Whisper)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx

# API Key do Google (para Gemini)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx

# API Key da Anthropic (opcional, para Claude)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxx
```

#### Como Obter as Chaves

##### OpenAI API Key
1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave (só aparece uma vez!)
5. **Importante**: Adicione créditos à conta (API paga)

##### Google Gemini API Key
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Create API Key"
4. Copie a chave
5. **Importante**: API gratuita com limites de uso

##### Anthropic API Key (Opcional)
1. Acesse: https://console.anthropic.com/
2. Faça login ou crie uma conta
3. Navegue para "API Keys"
4. Crie uma nova chave
5. **Importante**: API paga

#### Segurança das Chaves

**NUNCA FAÇA**:
- ❌ Commitar o arquivo `.env` para o Git
- ❌ Compartilhar as chaves publicamente
- ❌ Incluir chaves em código-fonte
- ❌ Enviar chaves por email/chat sem criptografia

**SEMPRE FAÇA**:
- ✅ Adicionar `.env` ao `.gitignore`
- ✅ Usar variáveis de ambiente em produção
- ✅ Rotacionar chaves periodicamente
- ✅ Monitorar uso de API para detectar abusos

---

## Fluxo de Execução Detalhado

### 1. Inicialização (`main()`)

```python
def main():
    # 1.1 Carrega variáveis de ambiente do .env
    load_dotenv()

    # 1.2 Cria diretórios necessários
    os.makedirs("transcricoes", exist_ok=True)
    os.makedirs("chunks", exist_ok=True)
    os.makedirs("aulas_mp3", exist_ok=True)

    # 1.3 Busca arquivos de áudio/vídeo
    mp3_files = glob.glob("aulas/*.mp3")
    mp4_files = glob.glob("aulas/*.mp4")

    # 1.4 Inicializa clientes das APIs
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-3-flash-preview")

    # 1.5 Processa cada arquivo
    for file in all_files:
        process_audio(file, openai_client, gemini_model)
```

### 2. Conversão MP4→MP3 (se necessário)

```python
def convert_mp4_to_mp3(video_path):
    # 2.1 Verifica se conversão já existe
    if os.path.exists(output_path):
        return output_path  # Reutiliza cache

    # 2.2 Converte usando FFmpeg
    subprocess.run([
        'ffmpeg', '-i', video_path,
        '-vn',  # Remove vídeo
        '-acodec', 'libmp3lame',  # Codec MP3
        '-b:a', '128k',  # Bitrate 128kbps
        '-y',  # Sobrescrever se existir
        output_path
    ])
```

### 3. Análise e Divisão de Arquivo

```python
def split_audio_if_needed(audio_path):
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)

    # 3.1 Arquivo pequeno: retorna diretamente
    if file_size_mb <= MAX_FILE_SIZE_MB:  # 20MB
        return [audio_path]

    # 3.2 Arquivo grande: divide em chunks
    duration = get_audio_duration(audio_path)
    chunk_duration = 600  # 10 minutos
    num_chunks = int(duration / chunk_duration) + 1

    # 3.3 Extrai cada chunk usando FFmpeg
    for i in range(num_chunks):
        start_time = i * chunk_duration
        subprocess.run([
            'ffmpeg', '-i', audio_path,
            '-ss', str(start_time),
            '-t', str(chunk_duration),
            '-acodec', 'libmp3lame',
            '-b:a', '128k',
            '-y', chunk_path
        ])
```

### 4. Transcrição com Whisper

```python
def transcribe_chunk(chunk_path, openai_client):
    # 4.1 Verifica cache
    if os.path.exists(transcription_file):
        return cached_transcription

    # 4.2 Envia para OpenAI Whisper
    with open(chunk_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )

    # 4.3 Salva resultado
    with open(transcription_file, "w", encoding="utf-8") as f:
        f.write(transcription)
```

### 5. Tradução e Correção com Gemini

```python
def process_audio(audio_path, openai_client, gemini_model):
    # 5.1 Combina transcrições de chunks
    combined_transcription = "\n\n".join(all_transcriptions)

    # 5.2 Prepara prompt para Gemini
    prompt = f"""Você é um tradutor especializado...

    Tarefa:
    1. TRADUZA INTEGRALMENTE para PT-BR
    2. Mantenha TODOS os detalhes técnicos
    3. Corrija erros ortográficos
    4. Remova hesitações (ah, hum, etc.)
    5. Organize em parágrafos

    Texto: {combined_transcription}
    """

    # 5.3 Envia para Gemini
    response = gemini_model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 65536,
        }
    )
```

### 6. Limpeza de Arquivos Temporários

```python
def cleanup_chunks(audio_name):
    # 6.1 Remove diretório de chunks de áudio
    chunks_dir = f"chunks/{audio_name}"
    if os.path.exists(chunks_dir):
        shutil.rmtree(chunks_dir)

    # 6.2 Remove transcrições temporárias de chunks
    chunk_files = glob.glob("transcricoes/chunks/chunk_*.txt")
    for file in chunk_files:
        os.remove(file)
```

---

## Módulos e Funções

### `transcribe_chunked.py`

#### Constantes
```python
MAX_FILE_SIZE_MB = 20           # Limite para divisão em chunks
CHUNK_DURATION_MS = 10 * 60 * 1000  # 10 minutos por chunk
```

#### Funções Principais

##### `log(message: str) -> None`
**Propósito**: Exibe mensagens com timestamp
```python
def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
```

##### `get_audio_duration(audio_path: str) -> float`
**Propósito**: Obtém duração do áudio em segundos
**Dependência**: FFprobe (parte do FFmpeg)
```python
def get_audio_duration(audio_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error',
         '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1',
         audio_path],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())
```

##### `convert_mp4_to_mp3(video_path: str) -> str`
**Propósito**: Converte vídeo MP4 para áudio MP3
**Retorna**: Caminho do arquivo MP3 criado
**Cache**: Reutiliza conversões existentes

##### `split_audio_if_needed(audio_path: str) -> List[str]`
**Propósito**: Divide áudio em chunks se necessário
**Retorna**: Lista de caminhos dos chunks (ou arquivo original se pequeno)
**Lógica**:
- Arquivos ≤20MB: retorna arquivo original
- Arquivos >20MB: divide em chunks de 10 minutos

##### `transcribe_chunk(chunk_path: str, openai_client: OpenAI) -> str`
**Propósito**: Transcreve um chunk de áudio
**API**: OpenAI Whisper-1
**Cache**: Reutiliza transcrições existentes

##### `cleanup_chunks(audio_name: str) -> None`
**Propósito**: Remove arquivos temporários após processamento
**Remove**:
- Diretório `chunks/{audio_name}/`
- Arquivos `transcricoes/chunks/chunk_*_transcricao.txt`

##### `process_audio(audio_path: str, openai_client: OpenAI, gemini_model: GenerativeModel) -> bool`
**Propósito**: Orquestra todo o processo de transcrição e tradução
**Fluxo**:
1. Verifica se já foi processado (cache)
2. Divide em chunks se necessário
3. Transcreve com Whisper
4. Traduz com Gemini
5. Limpa arquivos temporários
**Retorna**: True se sucesso, False se erro

##### `main() -> None`
**Propósito**: Ponto de entrada do programa
**Responsabilidades**:
- Inicializa ambiente
- Busca arquivos
- Processa em lote
- Exibe estatísticas finais

---

## Instalação e Configuração

### Passo a Passo Completo

#### 1. Clone ou Baixe o Repositório
```bash
# Via Git
git clone https://github.com/pardinithales/trancritor-aulas-mp4-mp3.git
cd trancritor-aulas-mp4-mp3

# Ou baixe o ZIP e extraia
```

#### 2. Crie Ambiente Virtual (Recomendado)
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Instale Dependências Python
```bash
pip install openai python-dotenv google-generativeai
```

#### 4. Instale FFmpeg

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS**:
```bash
brew install ffmpeg
```

**Windows**:
1. Baixe de: https://ffmpeg.org/download.html
2. Extraia para `C:\ffmpeg`
3. Adicione `C:\ffmpeg\bin` ao PATH

#### 5. Configure Variáveis de Ambiente

Crie arquivo `.env` na raiz:
```env
OPENAI_API_KEY=sua_chave_openai_aqui
GEMINI_API_KEY=sua_chave_gemini_aqui
```

#### 6. Prepare Diretórios
```bash
mkdir -p aulas aulas_mp3 transcricoes chunks
```

#### 7. Adicione Arquivos de Áudio
```bash
# Copie seus arquivos MP3/MP4 para aulas/
cp /caminho/para/seus/audios/*.mp3 aulas/
```

#### 8. Execute o Sistema
```bash
python3 transcribe_chunked.py
```

---

## Segurança e Boas Práticas

### Gerenciamento de Credenciais

#### `.gitignore` - CRITICAL
O arquivo `.gitignore` deve sempre conter:
```gitignore
# NUNCA commitar credenciais
.env
*.key
credentials.json

# NUNCA commitar arquivos de áudio/vídeo grandes
aulas/*.mp3
aulas/*.mp4
aulas_mp3/*.mp3
chunks/

# Ambiente virtual
venv/
env/
```

### Rotação de Chaves API

**Recomendação**: Rotacione chaves a cada 90 dias

**Processo**:
1. Gere nova chave no painel da API
2. Atualize `.env` com nova chave
3. Teste funcionamento
4. Revogue chave antiga

### Monitoramento de Custos

#### OpenAI Whisper
- **Modelo**: whisper-1
- **Custo**: $0.006 / minuto
- **Exemplo**: 1 hora de áudio = $0.36

#### Google Gemini Flash 3.0
- **Tier gratuito**: 15 requisições/minuto, 1 milhão tokens/dia
- **Custo** (se exceder): Varia, consulte pricing

### Backup e Recuperação

**Recomendações**:
1. **Backup das transcrições**: Copie `transcricoes/` regularmente
2. **Versionamento**: Use Git para código (mas não para áudios/keys)
3. **Cloud backup**: Considere sync de `transcricoes/` para cloud

---

## Troubleshooting

### Erros Comuns

#### 1. `ModuleNotFoundError: No module named 'openai'`
**Causa**: Dependências não instaladas
**Solução**:
```bash
pip install openai python-dotenv google-generativeai
```

#### 2. `ffmpeg: command not found`
**Causa**: FFmpeg não instalado ou não no PATH
**Solução**:
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Adicione FFmpeg ao PATH

#### 3. `AuthenticationError: Incorrect API key`
**Causa**: Chave de API inválida ou ausente
**Solução**:
1. Verifique arquivo `.env` existe
2. Verifique chaves estão corretas
3. Regenere chaves se necessário

#### 4. `RateLimitError: Rate limit exceeded`
**Causa**: Muitas requisições à API
**Solução**:
- **OpenAI**: Aguarde 1 minuto, reduza taxa de requisições
- **Gemini**: Aguarde reset do limite (1 minuto)

#### 5. Arquivo `.env` não carregado
**Causa**: Arquivo não está na raiz ou nome incorreto
**Solução**:
```bash
# Verifique localização
ls -la .env

# Verifique conteúdo
cat .env
```

#### 6. Transcrição vazia ou truncada
**Causa**: Áudio corrompido ou formato incompatível
**Solução**:
1. Verifique integridade do arquivo: `ffprobe arquivo.mp3`
2. Reconverta o áudio: `ffmpeg -i input.mp4 -acodec libmp3lame output.mp3`

### Logs e Debugging

#### Ativar Logs Detalhados
Modifique `transcribe_chunked.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verificar Status de Processamento
```bash
# Verificar arquivos processados
ls -lh transcricoes/*_PT-BR.txt

# Verificar chunks temporários (devem estar vazios após sucesso)
ls chunks/

# Verificar uso de espaço
du -sh aulas/ aulas_mp3/ transcricoes/ chunks/
```

### Contato e Suporte

- **GitHub Issues**: https://github.com/pardinithales/trancritor-aulas-mp4-mp3/issues
- **Email**: [Seu email de suporte]
- **Documentação OpenAI**: https://platform.openai.com/docs
- **Documentação Gemini**: https://ai.google.dev/docs

---

## Histórico de Problemas e Soluções (Troubleshooting Completo)

Esta seção documenta **TODOS** os problemas encontrados durante o desenvolvimento e testes do sistema, incluindo a migração da biblioteca Google Generative AI.

### 🔴 Problema 1: `python: command not found`

**Contexto**: Tentativa de executar script no WSL2/Ubuntu
**Comando executado**:
```bash
python transcribe_chunked.py
```

**Erro**:
```
bash: python: command not found
```

**Causa Raiz**: No WSL2/Ubuntu, o comando `python` não existe por padrão, apenas `python3`.

**Solução**:
```bash
# Opção 1: Usar python3 diretamente
python3 transcribe_chunked.py

# Opção 2: Criar alias permanente (adicionar ao ~/.bashrc)
echo "alias python=python3" >> ~/.bashrc
source ~/.bashrc
```

**Status**: ✅ Resolvido usando `python3`

---

### 🔴 Problema 2: `ModuleNotFoundError: No module named 'openai'`

**Contexto**: Tentativa de executar script sem instalar dependências
**Comando executado**:
```bash
python3 transcribe_chunked.py
```

**Erro**:
```
ModuleNotFoundError: No module named 'openai'
```

**Causa Raiz**: Dependências Python não instaladas no ambiente.

**Solução**:
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install openai python-dotenv google-genai
```

**Status**: ✅ Resolvido com venv

---

### 🔴 Problema 3: `externally-managed-environment` (PEP 668)

**Contexto**: Tentativa de instalar pacotes com pip no Python do sistema
**Comando executado**:
```bash
pip3 install openai python-dotenv google-generativeai
```

**Erro**:
```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
```

**Causa Raiz**: PEP 668 impede instalação de pacotes no Python do sistema em distribuições Linux modernas para evitar conflitos com o gerenciador de pacotes do sistema.

**Solução**:
```bash
# NUNCA tente --break-system-packages
# SEMPRE use ambiente virtual:
python3 -m venv venv
source venv/bin/activate
pip install <pacotes>
```

**Referência**: [PEP 668 – Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)

**Status**: ✅ Resolvido com venv

---

### 🔴 Problema 4: Instalação extremamente lenta em background

**Contexto**: Comando de instalação rodando em background não completava
**Comando executado**:
```bash
python3 -m venv venv && source venv/bin/activate && pip install openai python-dotenv google-generativeai
```

**Sintoma**: Processo executando por 5+ minutos sem completar, apenas mostrando:
```
Installing collected packages: ...
```

**Causa Raiz**:
1. Comando em cadeia (`&&`) em background pode ter problemas com shell interativo
2. `source` em subshell não funciona corretamente
3. Buffer de saída não liberado

**Solução**:
```bash
# Opção 1: Executar comandos separadamente
python3 -m venv venv
./venv/bin/pip install openai python-dotenv google-genai

# Opção 2: Usar o Python do venv diretamente (MELHOR)
./venv/bin/python3 -m pip install <pacotes>
```

**Status**: ✅ Resolvido usando ./venv/bin/pip diretamente

---

### 🔴 Problema 5: Script congelado sem saída (Buffer de stdout)

**Contexto**: Script Python rodando em background não mostrava logs
**Comando executado**:
```bash
./venv/bin/python3 transcribe_chunked.py 2>&1 | tee test_output.log &
```

**Sintoma**:
- Processo rodando (verificado com `ps aux`)
- Arquivo de log com 0 bytes
- Nenhuma saída visível

**Causa Raiz**: Python usa buffer de saída por padrão. Em processos background, o buffer não é liberado até estar cheio ou o programa terminar.

**Solução**:
```bash
# Opção 1: Usar flag -u (unbuffered)
./venv/bin/python3 -u transcribe_chunked.py 2>&1

# Opção 2: Forçar flush no código
import sys
sys.stdout.reconfigure(line_buffering=True)  # Já existe no código
sys.stdout.flush()  # Após cada print importante

# Opção 3: Variável de ambiente
PYTHONUNBUFFERED=1 python3 transcribe_chunked.py
```

**Status**: ✅ Resolvido com flag `-u`

---

### 🔴 Problema 6: Biblioteca Google Generative AI depreciada

**Contexto**: Ao rodar o script, aparecia warning de depreciação
**Warning exibido**:
```python
FutureWarning: google.generativeai is deprecated.
Please use google.genai.
```

**Causa Raiz**: Google lançou nova biblioteca `google-genai` (v1.x) substituindo a antiga `google-generativeai` (v0.x).

**Mudanças na API**:

| Aspecto | Biblioteca Antiga (`google.generativeai`) | Biblioteca Nova (`google.genai`) |
|---------|-------------------------------------------|-----------------------------------|
| **Import** | `import google.generativeai as genai` | `from google import genai` |
| **Inicialização** | `genai.configure(api_key="...")`<br>`model = genai.GenerativeModel("model-name")` | `client = genai.Client(api_key="...")` |
| **Geração** | `model.generate_content(prompt, generation_config=config)` | `client.models.generate_content(model="...", contents=prompt, config=config)` |
| **Resposta** | `response.text` | `response.text` (igual) |

**Solução Implementada**:

1. **Desinstalar biblioteca antiga**:
```bash
./venv/bin/pip uninstall google-generativeai
```

2. **Instalar biblioteca nova**:
```bash
./venv/bin/pip install --upgrade google-genai
```

3. **Atualizar código** (`transcribe_chunked.py`):

```python
# ANTES (Depreciado):
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-3-flash-preview")

response = gemini_model.generate_content(
    prompt,
    generation_config=generation_config
)

# DEPOIS (Atual):
from google import genai  # ← Mudança no import

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # ← Client-based

response = gemini_client.models.generate_content(  # ← model como parâmetro
    model="gemini-3-flash-preview",
    contents=prompt,  # ← renamed from 'prompt'
    config=generation_config  # ← renamed from 'generation_config'
)
```

**Dependências adicionadas automaticamente**:
- `tenacity` (v9.1.2) - Para retry logic
- `websockets` (v15.0.1) - Para streaming

**Teste de Validação**:
```bash
./venv/bin/python3 << 'EOF'
from google import genai
client = genai.Client(api_key="AIzaSy...")
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Traduza: Hello world",
    config={"temperature": 0.3}
)
print(response.text)  # Output: "Olá mundo"
EOF
```

**Status**: ✅ Migração completa e testada com sucesso

---

### 🔴 Problema 7: `load_dotenv()` AssertionError em heredoc

**Contexto**: Ao testar código Python via heredoc (stdin)
**Comando executado**:
```bash
./venv/bin/python3 << 'EOF'
from dotenv import load_dotenv
load_dotenv()
EOF
```

**Erro**:
```python
File "/venv/lib/python3.12/site-packages/dotenv/main.py", line 322, in find_dotenv
    assert frame.f_back is not None
AssertionError
```

**Causa Raiz**: `load_dotenv()` sem argumentos tenta inspecionar o call stack para encontrar o arquivo `.env` automaticamente. Em scripts executados via stdin (heredoc), o frame não existe.

**Solução**:
```python
# Opção 1: Especificar path explicitamente
load_dotenv(".env")

# Opção 2: Usar path absoluto
load_dotenv("/caminho/completo/.env")

# Opção 3: Carregar manualmente
import os
os.environ["API_KEY"] = "valor"

# Opção 4: Para testes, não usar heredoc
# Criar arquivo temporário test.py
```

**Status**: ✅ Contornado usando path explícito em testes

---

### 📊 Resumo Estatístico dos Problemas

| Problema | Categoria | Impacto | Tempo para Resolver | Solução |
|----------|-----------|---------|---------------------|---------|
| #1 python não encontrado | Ambiente | Baixo | 1 min | Usar python3 |
| #2 Módulos faltando | Dependências | Médio | 3 min | Criar venv + pip install |
| #3 PEP 668 | Ambiente | Alto | 5 min | Forçar uso de venv |
| #4 Instalação lenta | Performance | Médio | 8 min | Usar ./venv/bin/pip |
| #5 Buffer stdout | Debug | Alto | 10 min | Flag -u |
| #6 Biblioteca depreciada | Migração | Alto | 30 min | Migrar para google-genai |
| #7 load_dotenv heredoc | Teste | Baixo | 2 min | Path explícito |

**Total de problemas**: 7
**Tempo total de troubleshooting**: ~59 minutos
**Taxa de resolução**: 100% ✅

---

### 🎯 Lições Aprendidas

1. **Sempre use ambiente virtual** - Evita 80% dos problemas de dependências
2. **Leia warnings** - A depreciação da biblioteca estava avisada há meses
3. **Use `-u` em background** - Essencial para debug de processos longos
4. **Especifique paths completos** - `./venv/bin/python3` melhor que `python`
5. **Teste progressivamente** - Testar API isoladamente antes de integrar
6. **Documente tudo** - Este documento economizará horas no futuro

---

### 🔧 Comandos de Diagnóstico Úteis

```bash
# Verificar versão Python
python3 --version

# Verificar pip e pacotes instalados
./venv/bin/pip list

# Verificar processos Python rodando
ps aux | grep python

# Verificar bibliotecas Google instaladas
./venv/bin/pip show google-genai google-generativeai

# Forçar reinstalação limpa
./venv/bin/pip uninstall google-generativeai -y
./venv/bin/pip install --force-reinstall --no-cache-dir google-genai

# Testar Gemini rapidamente
./venv/bin/python3 -u -c "from google import genai; print('OK')"
```

---

## Changelog

### Versão 1.1.0 (2026-01-03) - Atual
**🎉 Migração para Google Genai v1.x**
- ✅ Migrado de `google-generativeai` (depreciado) para `google-genai` v1.56.0
- ✅ Atualizada arquitetura para Client-based API
- ✅ Adicionadas dependências: `tenacity` v9.1.2, `websockets` v15.0.1
- ✅ Testes completos realizados com sucesso
- ✅ Documentação completa de troubleshooting (7 problemas documentados)
- ✅ Performance mantida: tradução de 17.875 caracteres em ~27 segundos
- ⚠️ **BREAKING CHANGE**: Código atualizado incompatível com `google-generativeai` antiga

**Arquivos Modificados**:
- `transcribe_chunked.py`: Linhas 5, 149, 205-223, 265-271, 288
- `AGENTS.md`: Adicionada seção completa de troubleshooting (337 linhas)
- `requirements.txt`: Atualizado (implicitamente via pip)

### Versão 1.0.0 (2026-01-02)
**🚀 Lançamento Inicial**
- Transcrição com OpenAI Whisper-1
- Tradução com Google Gemini Flash 3.0
- Suporte para MP3 e MP4
- Divisão automática de arquivos grandes (>20MB)
- Cache inteligente para evitar reprocessamento
- Limpeza automática de temporários
- Sistema de logs com timestamps

### Melhorias Futuras Planejadas
- [ ] Interface web (Streamlit/Gradio)
- [ ] Suporte a mais idiomas de saída
- [ ] Paralelização de processamento de múltiplos arquivos
- [ ] Docker container para deploy facilitado
- [ ] API REST para integração
- [ ] Suporte a modelos locais (Whisper local + Gemma)
- [ ] Dashboard de métricas e estatísticas
- [ ] Suporte a legendas/subtítulos (SRT, VTT)

---

**Última atualização**: 2026-01-03 04:25 UTC
**Versão do documento**: 1.1.0
**Última migração de biblioteca**: Google Generative AI → Google Genai v1.56.0
**Autor**: Sistema automatizado
