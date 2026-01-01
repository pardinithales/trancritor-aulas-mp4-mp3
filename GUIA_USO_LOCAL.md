# Guia de Uso Local - Sistema de Transcrição de Aulas

## Problema
O ambiente Claude Code tem restrições de proxy que bloqueiam:
- Google Drive (para download de arquivos)
- OpenAI API (para transcrição)
- Google Gemini API (para tradução)

## Solução: Executar Localmente

### 1. Pré-requisitos

```bash
# Instalar Python 3.8+
python --version

# Instalar FFmpeg
# Windows: https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### 2. Clonar o Repositório

```bash
git clone https://github.com/pardinithales/trancritor-aulas-mp4-mp3.git
cd trancritor-aulas-mp4-mp3
```

### 3. Instalar Dependências

```bash
pip install openai python-dotenv google-generativeai gdown
```

### 4. Configurar API Keys

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
GEMINI_API_KEY=sua_chave_gemini_aqui
```

### 5. Baixar Arquivo do Google Drive

**Opção A - Download Manual:**
1. Acesse: https://drive.google.com/file/d/1d8UD5EZA4g_EpzD21Udda1dXKyTg_xzO/view
2. Baixe o arquivo
3. Coloque na pasta `aulas/`

**Opção B - Download Automático com gdown:**
```bash
python download_from_drive.py "https://drive.google.com/file/d/1d8UD5EZA4g_EpzD21Udda1dXKyTg_xzO/view?usp=drivesdk"
```

### 6. Processar a Aula

```bash
python transcribe_chunked.py
```

### 7. Resultados

Os arquivos serão salvos em:
- `transcricoes/[nome]_original.txt` - Transcrição em inglês
- `transcricoes/[nome]_PT-BR.txt` - Tradução em português

## Estrutura do Projeto

```
trancritor-aulas-mp4-mp3/
├── aulas/                    # Coloque seus arquivos aqui
├── transcricoes/             # Resultados finais
│   ├── *_original.txt       # Transcrição original
│   └── *_PT-BR.txt          # Tradução PT-BR
├── chunks/                   # Temporário (auto-removido)
├── download_from_drive.py    # Script de download
├── transcribe_chunked.py     # Script principal
└── .env                      # Suas API keys
```

## Recursos do Sistema

- ✅ Suporte para MP3 e MP4
- ✅ Conversão automática de MP4 para MP3
- ✅ Divisão automática de arquivos grandes (>20MB)
- ✅ Transcrição com OpenAI Whisper-1
- ✅ Tradução integral para PT-BR com Gemini Flash 3.0
- ✅ Cache inteligente (não repete processamentos)
- ✅ Limpeza automática de arquivos temporários
- ✅ Logs detalhados com timestamp

## Custos Aproximados

- **OpenAI Whisper-1:** ~$0.006 por minuto de áudio
- **Google Gemini Flash:** Gratuito até 15 requests/minuto

**Exemplo:** Aula de 60 minutos = ~$0.36

## Troubleshooting

### Erro: FFmpeg não encontrado
```bash
# Instale o FFmpeg seguindo as instruções do passo 1
```

### Erro: API Key inválida
```bash
# Verifique se o arquivo .env está na raiz do projeto
# Confirme que as chaves estão corretas
```

### Arquivo muito grande
- O sistema divide automaticamente em chunks de 10 minutos
- Não há limite de tamanho!

## Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Verifique os logs detalhados no terminal
