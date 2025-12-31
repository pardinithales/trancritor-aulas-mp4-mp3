import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
import glob
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

MAX_FILE_SIZE_MB = 20
CHUNK_DURATION_MS = 10 * 60 * 1000

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_audio_duration(audio_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())
    except:
        return None

def convert_mp4_to_mp3(video_path):
    video_name = Path(video_path).stem
    output_path = f"aulas_mp3/{video_name}.mp3"
    
    os.makedirs("aulas_mp3", exist_ok=True)
    
    if os.path.exists(output_path):
        log(f"[CACHE] MP3 ja existe: {output_path}")
        return output_path
    
    log(f"[CONVERSAO] Convertendo MP4 para MP3: {video_name}")
    
    try:
        subprocess.run([
            'ffmpeg', '-i', video_path, '-vn', '-acodec', 'libmp3lame',
            '-b:a', '128k', '-y', output_path
        ], capture_output=True, check=True)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        log(f"[OK] MP3 criado: {output_path} ({file_size:.2f} MB)")
        return output_path
    except Exception as e:
        log(f"[ERRO] Falha na conversao: {str(e)}")
        return None

def split_audio_if_needed(audio_path):
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    
    if file_size_mb <= MAX_FILE_SIZE_MB:
        log(f"[OK] Arquivo pequeno ({file_size_mb:.2f} MB), nao precisa dividir")
        return [audio_path]
    
    log(f"[INFO] Arquivo grande ({file_size_mb:.2f} MB), dividindo em chunks...")
    
    audio_name = Path(audio_path).stem
    chunks_dir = f"chunks/{audio_name}"
    os.makedirs(chunks_dir, exist_ok=True)
    
    existing_chunks = glob.glob(f"{chunks_dir}/*.mp3")
    if existing_chunks:
        log(f"[OK] {len(existing_chunks)} chunks ja existem, reutilizando...")
        return sorted(existing_chunks)
    
    duration = get_audio_duration(audio_path)
    if not duration:
        log("[ERRO] Nao foi possivel determinar duracao do audio. Instale ffmpeg.")
        return [audio_path]
    
    log(f"Duracao total: {duration/60:.2f} minutos")
    
    chunk_duration = 600
    num_chunks = int(duration / chunk_duration) + 1
    
    chunks = []
    for i in range(num_chunks):
        start_time = i * chunk_duration
        chunk_path = f"{chunks_dir}/chunk_{i+1:03d}.mp3"
        
        log(f"Extraindo chunk {i+1}/{num_chunks}: {start_time/60:.1f}min - {(start_time+chunk_duration)/60:.1f}min")
        
        subprocess.run([
            'ffmpeg', '-i', audio_path, '-ss', str(start_time), 
            '-t', str(chunk_duration), '-acodec', 'libmp3lame', 
            '-b:a', '128k', '-y', chunk_path
        ], capture_output=True, check=True)
        
        if os.path.exists(chunk_path):
            chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)
            log(f"[SALVO] {chunk_path} ({chunk_size:.2f} MB)")
            chunks.append(chunk_path)
    
    log(f"[OK] Audio dividido em {len(chunks)} chunks")
    return chunks

def transcribe_chunk(chunk_path, openai_client):
    chunk_name = Path(chunk_path).stem
    transcription_file = f"transcricoes/chunks/{chunk_name}_transcricao.txt"
    
    os.makedirs("transcricoes/chunks", exist_ok=True)
    
    if os.path.exists(transcription_file):
        log(f"[CACHE] Usando transcricao existente: {chunk_name}")
        with open(transcription_file, "r", encoding="utf-8") as f:
            return f.read()
    
    log(f"[TRANSCREVENDO] {chunk_name}...")
    
    with open(chunk_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    
    transcription_text = transcription
    
    with open(transcription_file, "w", encoding="utf-8") as f:
        f.write(transcription_text)
    
    log(f"[OK] {len(transcription_text)} caracteres transcritos")
    return transcription_text

def cleanup_chunks(audio_name):
    chunks_dir = f"chunks/{audio_name}"
    chunks_transcriptions = "transcricoes/chunks"
    
    if os.path.exists(chunks_dir):
        import shutil
        shutil.rmtree(chunks_dir)
        log(f"[LIMPEZA] Chunks de audio removidos: {chunks_dir}")
    
    if os.path.exists(chunks_transcriptions):
        chunk_files = glob.glob(f"{chunks_transcriptions}/*{audio_name}*")
        for file in chunk_files:
            os.remove(file)
        log(f"[LIMPEZA] Transcricoes temporarias removidas")

def process_audio(audio_path, openai_client, gemini_model):
    audio_name = Path(audio_path).stem
    final_file = f"transcricoes/{audio_name}_PT-BR.txt"
    
    log(f"\n{'='*60}")
    log(f"PROCESSANDO: {audio_name}")
    log(f"{'='*60}")
    
    if os.path.exists(final_file):
        log(f"[AVISO] Transcricao final ja existe: {final_file}")
        log("[OK] Arquivo ja processado!")
        cleanup_chunks(audio_name)
        return True
    
    chunks = split_audio_if_needed(audio_path)
    needs_cleanup = len(chunks) > 1
    
    log(f"\n[ETAPA 1] TRANSCRICAO COM OPENAI WHISPER-1")
    log("-" * 60)
    
    all_transcriptions = []
    for i, chunk in enumerate(chunks, 1):
        log(f"\nProcessando chunk {i}/{len(chunks)}...")
        transcription = transcribe_chunk(chunk, openai_client)
        all_transcriptions.append(transcription)
    
    combined_transcription = "\n\n".join(all_transcriptions)
    log(f"\n[OK] Transcricao completa: {len(combined_transcription)} caracteres")
    
    original_file = f"transcricoes/{audio_name}_original.txt"
    with open(original_file, "w", encoding="utf-8") as f:
        f.write(combined_transcription)
    log(f"[SALVO] {original_file}")
    
    log(f"\n[ETAPA 2] TRADUCAO E CORRECAO COM GEMINI FLASH 3.0")
    log("-" * 60)
    
    prompt = f"""Voce e um tradutor e revisor especializado em transcricoes de aulas e palestras medicas.

IMPORTANTE: Esta e uma transcricao de uma aula sobre enxaqueca/cefaleia. Mantenha TODA a informacao medica, cientifica e tecnica.

Tarefa:
1. TRADUZA INTEGRALMENTE para Portugues do Brasil (PT-BR)
2. Mantenha TODOS os detalhes, nomes de medicamentos, estudos, porcentagens, dados cientificos
3. Corrija erros ortograficos e gramaticais
4. Remova hesitacoes e sons de preenchimento (ah, hum, ne, etc.)
5. Organize em paragrafos logicos para facilitar leitura
6. Mantenha linguagem natural e fluida
7. NAO OMITA NENHUMA INFORMACAO - mantenha 100% do conteudo original
8. Preserve todos os termos tecnicos e nomes proprios corretamente

Transcricao original em ingles:
{combined_transcription}

Retorne APENAS a transcricao traduzida e corrigida em PT-BR, sem comentarios adicionais."""
    
    log("Enviando para o Gemini processar traducao...")
    
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 65536,
    }
    
    response = gemini_model.generate_content(
        prompt,
        generation_config=generation_config
    )
    
    translated_text = response.text
    log(f"[OK] Traducao concluida ({len(translated_text)} caracteres)")
    
    with open(final_file, "w", encoding="utf-8") as f:
        f.write(translated_text)
    
    log(f"[SALVO] {final_file}")
    
    if needs_cleanup:
        log(f"\n[ETAPA 3] LIMPEZA DE ARQUIVOS TEMPORARIOS")
        log("-" * 60)
        cleanup_chunks(audio_name)
    
    log(f"\n[CONCLUIDO] {audio_name}")
    log(f"Original (EN): {original_file}")
    log(f"Final (PT-BR): {final_file}")
    return True

def main():
    log("="*60)
    log("SISTEMA DE TRANSCRICAO COM SUPORTE MP3/MP4")
    log("="*60)
    
    load_dotenv()
    
    os.makedirs("transcricoes", exist_ok=True)
    os.makedirs("chunks", exist_ok=True)
    os.makedirs("aulas_mp3", exist_ok=True)
    log("[OK] Diretorios verificados/criados")
    
    log("\nBuscando arquivos de audio/video na pasta 'aulas'...")
    mp3_files = glob.glob("aulas/*.mp3")
    mp4_files = glob.glob("aulas/*.mp4")
    
    all_files = mp3_files + mp4_files
    
    if not all_files:
        log("[ERRO] Nenhum arquivo MP3/MP4 encontrado na pasta 'aulas'")
        return
    
    log(f"[OK] Encontrados {len(mp3_files)} MP3 e {len(mp4_files)} MP4")
    for i, file in enumerate(all_files, 1):
        file_size = os.path.getsize(file) / (1024 * 1024)
        file_type = Path(file).suffix.upper()
        log(f"  {i}. {Path(file).name} ({file_size:.2f} MB) [{file_type}]")
    
    log("\nInicializando APIs...")
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    log("[OK] OpenAI conectado")
    
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-3-flash-preview")
    log("[OK] Gemini Flash 3.0 inicializado")
    
    success_count = 0
    for file in all_files:
        try:
            file_ext = Path(file).suffix.lower()
            
            if file_ext == ".mp4":
                log(f"\n[MP4] Detectado video, convertendo para MP3 primeiro...")
                mp3_file = convert_mp4_to_mp3(file)
                if not mp3_file:
                    log(f"[ERRO] Falha ao converter {file}")
                    continue
                audio_file = mp3_file
            else:
                audio_file = file
            
            if process_audio(audio_file, openai_client, gemini_model):
                success_count += 1
        except Exception as e:
            log(f"[ERRO] Falha ao processar {file}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    log("\n" + "="*60)
    log(f"PROCESSAMENTO COMPLETO!")
    log(f"Total processado: {success_count}/{len(all_files)} arquivos")
    log("="*60)

if __name__ == "__main__":
    main()
