import os
import sys
import gdown
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def extract_file_id(drive_url):
    """Extrai o file ID de uma URL do Google Drive"""
    if '/file/d/' in drive_url:
        file_id = drive_url.split('/file/d/')[1].split('/')[0]
        return file_id
    elif 'id=' in drive_url:
        file_id = drive_url.split('id=')[1].split('&')[0]
        return file_id
    else:
        log("[ERRO] Formato de URL do Google Drive nao reconhecido")
        return None

def download_from_drive(drive_url, output_folder="aulas"):
    """Baixa um arquivo do Google Drive para a pasta especificada"""
    log("="*60)
    log("DOWNLOAD DO GOOGLE DRIVE")
    log("="*60)

    # Criar pasta de destino se não existir
    os.makedirs(output_folder, exist_ok=True)

    # Extrair file ID
    file_id = extract_file_id(drive_url)
    if not file_id:
        return None

    log(f"File ID extraido: {file_id}")

    # URL de download direto
    download_url = f"https://drive.google.com/uc?id={file_id}"

    log(f"Iniciando download...")

    try:
        # Download do arquivo
        output_path = gdown.download(download_url, quiet=False, fuzzy=True)

        if not output_path:
            log("[ERRO] Falha ao baixar o arquivo")
            return None

        # Mover para pasta aulas se não estiver lá
        if not output_path.startswith(output_folder):
            filename = Path(output_path).name
            new_path = os.path.join(output_folder, filename)

            # Se já existir, remover o antigo
            if os.path.exists(new_path):
                os.remove(new_path)

            os.rename(output_path, new_path)
            output_path = new_path

        file_size = os.path.getsize(output_path) / (1024 * 1024)
        log(f"[OK] Arquivo baixado: {output_path}")
        log(f"[OK] Tamanho: {file_size:.2f} MB")

        return output_path

    except Exception as e:
        log(f"[ERRO] Falha no download: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) < 2:
        log("[ERRO] Uso: python download_from_drive.py <URL_DO_GOOGLE_DRIVE>")
        sys.exit(1)

    drive_url = sys.argv[1]
    output_path = download_from_drive(drive_url)

    if output_path:
        log("\n" + "="*60)
        log(f"DOWNLOAD CONCLUIDO!")
        log(f"Arquivo salvo em: {output_path}")
        log("="*60)
        return output_path
    else:
        log("\n[ERRO] Download falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
