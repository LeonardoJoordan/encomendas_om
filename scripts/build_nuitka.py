import os
import subprocess

def compilar_projeto():
    print("Iniciando a compilação do projeto com Nuitka...")
    
    # Caminho base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Apontamos para o launcher para abrir a interface gráfica com o IP
    launcher_file = os.path.join(base_dir, "launcher.py")
    
    # Parâmetros do Nuitka blindados para Linux (Mint/Ubuntu/Debian)
    comando = [
        "python3", "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--output-filename=Encomendas_3ºRCC",
        "--include-package=pydantic",     # <-- Trocamos o plugin pela inclusão direta do pacote
        "--enable-plugin=tk-inter",     # <-- Embutir bibliotecas da janela gráfica (evita precisar de apt install)
        "--include-package=uvicorn",
        "--include-package=fastapi",
        "--include-package=sqlalchemy",
        "--include-module=sqlite3",     # <-- Garante o motor do banco de dados
        "--include-module=encodings",   # <-- Vacina contra o bug dos acentos (força o pacote UTF-8 nativo)
        "--include-data-dir=frontend=frontend",
        "--include-data-file=icone.ico=icone.ico",
        "--include-data-file=index.html=index.html",
        "--output-dir=build",
        launcher_file
    ]
    
    try:
        subprocess.run(comando, check=True)
        print("✅ Compilação concluída com sucesso! O executável está na pasta 'build'.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante a compilação: {e}")

if __name__ == "__main__":
    compilar_projeto()