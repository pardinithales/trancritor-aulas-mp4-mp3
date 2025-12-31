# Sistema de Transcrição e Tradução de Aulas

Sistema automatizado para transcrever e traduzir aulas em áudio/vídeo para português brasileiro usando OpenAI Whisper e Google Gemini Flash 3.0.

## Recursos

- ✅ Suporte para MP3 e MP4
- ✅ Conversão automática de MP4 para MP3
- ✅ Divisão automática de arquivos grandes (>20MB)
- ✅ Transcrição com OpenAI Whisper-1
- ✅ Tradução integral para PT-BR com Gemini Flash 3.0
- ✅ Cache inteligente (não repete processamentos)
- ✅ Limpeza automática de arquivos temporários
- ✅ Logs detalhados com timestamp

## Requisitos

- Python 3.8+
- FFmpeg instalado
- Conta OpenAI (para Whisper)
- Conta Google AI (para Gemini)

## Instalação

```bash
pip install openai python-dotenv google-generativeai
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_aqui
GEMINI_API_KEY=sua_chave_aqui
```

## Uso

1. Coloque seus arquivos MP3 ou MP4 na pasta `aulas/`
2. Execute o script:

```bash
python transcribe_chunked.py
```

## Estrutura de Pastas

```
transcription-videoaulas/
├── aulas/              # Coloque seus arquivos aqui
├── aulas_mp3/          # MP3 convertidos de MP4
├── transcricoes/       # Resultados finais
│   ├── *_original.txt  # Transcrição em inglês
│   └── *_PT-BR.txt     # Tradução em português
├── chunks/             # Temporário (auto-removido)
└── .env                # Suas API keys
```

## Fluxo de Processamento

1. **Detecção**: Busca arquivos MP3/MP4 em `aulas/`
2. **Conversão**: MP4 → MP3 (se necessário)
3. **Divisão**: Chunks de 10 minutos (se arquivo >20MB)
4. **Transcrição**: OpenAI Whisper-1
5. **Tradução**: Gemini Flash 3.0 para PT-BR
6. **Limpeza**: Remove chunks temporários

## Importante

- Não commite arquivos `.env` ou API keys
- Arquivos de áudio são ignorados pelo git (.gitignore)
- O sistema mantém cache para evitar reprocessamento
- Todo o conteúdo original é preservado na tradução

## Testes

Para testar o Gemini:
```bash
python test_gemini.py
```
