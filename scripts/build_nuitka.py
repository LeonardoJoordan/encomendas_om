import os
import subprocess

def compilar_projeto():
    print("Iniciando a compilação do backend com Nuitka...")
    
    # Caminho base do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_file = os.path.join(base_dir, "app", "main.py")
    
    # Parâmetros do Nuitka para empacotar o FastAPI e Uvicorn
    comando = [
        "python", "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--plugin-enable=pydantic",
        "--include-package=uvicorn",
        "--include-package=fastapi",
        "--include-package=sqlalchemy",
        "--output-dir=build",
        main_file
    ]
    
    try:
        subprocess.run(comando, check=True)
        print("✅ Compilação concluída com sucesso! O executável está na pasta 'build'.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante a compilação: {e}")

if __name__ == "__main__":
    compilar_projeto()