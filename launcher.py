import multiprocessing
import uvicorn
from app.main import app as fastapi_app
import tkinter as tk
import sys
import webbrowser
import time
import socket
import os
from PIL import Image
import pystray
from pystray import MenuItem as item

def worker_servidor():
    """Roda o Uvicorn de forma nativa no processo filho, sem depender do terminal."""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

def obter_ip_local():
    try:
        # Tenta conectar a um DNS público para forçar o SO a usar a interface de rede principal
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class EncomendasLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Encomendas OM - Servidor")
        self.root.geometry("350x220")
        self.root.resizable(False, False)
        
        # Centraliza a janela
        self.root.eval('tk::PlaceWindow . center')

        self.processo_servidor = None
        self.tray_icon = None  # Evita crash ao tentar fechar o programa

        # Elementos da Interface
        self.lbl_titulo = tk.Label(root, text="Gestor do Servidor", font=("Arial", 14, "bold"))
        self.lbl_titulo.pack(pady=10)

        self.lbl_ip = tk.Label(root, text="", font=("Arial", 11, "bold"), fg="#0056b3")
        self.lbl_ip.pack(pady=2)

        self.lbl_status = tk.Label(root, text="Status: Desligado", font=("Arial", 12), fg="red")
        self.lbl_status.pack(pady=5)

        self.btn_toggle = tk.Button(
            root, text="Ligar Servidor", font=("Arial", 12, "bold"), 
            bg="#28a745", fg="white", width=20, command=self.toggle_servidor
        )
        self.btn_toggle.pack(pady=10)

        # Garante que o servidor feche se o usuário fechar a janela no "X"
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicativo)

        # Auto-start ao abrir o launcher
        self.toggle_servidor()

    def toggle_servidor(self):
        if self.processo_servidor is None:
            self.ligar_servidor()
        else:
            self.desligar_servidor()

    def ligar_servidor(self):
        # Inicia o Uvicorn como um subprocesso invisível usando o mesmo Python do ambiente
        
        try:
            # Inicia o servidor usando o multiprocessamento nativo do Python
            self.processo_servidor = multiprocessing.Process(target=worker_servidor)
            self.processo_servidor.start()
            self.lbl_status.config(text="Status: Rodando (Porta 8000)", fg="green")
            ip_rede = obter_ip_local()
            self.lbl_ip.config(text=f"Acesso Rede: http://{ip_rede}:8000")
            self.btn_toggle.config(text="Desligar Servidor", bg="#dc3545") # Fica vermelho
            
            # Aguarda um segundo para o servidor subir e abre o navegador
            self.root.after(1000, lambda: webbrowser.open("http://127.0.0.1:8000"))
        except Exception as e:
            self.lbl_status.config(text=f"Erro ao ligar", fg="red")
            print(f"Erro: {e}")

    def desligar_servidor(self):
        if self.processo_servidor:
            self.processo_servidor.terminate()
            self.processo_servidor.join()  # Aguarda o processo morrer de vez
            self.processo_servidor = None
            
        self.lbl_status.config(text="Status: Desligado", fg="red")
        self.btn_toggle.config(text="Ligar Servidor", bg="#28a745") # Fica verde
        self.lbl_ip.config(text="")

    def fechar_aplicativo(self):
        if self.processo_servidor is not None:
            # Se o servidor estiver rodando, minimiza para a bandeja
            self.root.withdraw()
            self.criar_icone_bandeja()
        else:
            # Se o servidor estiver desligado, fecha tudo
            self.encerrar_programa_realmente()

    def criar_icone_bandeja(self):
        import sys
        # Como launcher.py e icone.png estão na mesma pasta (raiz), basta pegar o diretório atual
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Mudamos para .ico
        caminho_icone = os.path.join(base_dir, "icone.ico")
        
        # Abre a imagem multi-resolução
        image = Image.open(caminho_icone)
        
        # Cria o menu de contexto
        menu = pystray.Menu(
            item('Abrir Painel', self.restaurar_janela, default=True),
            item('Desligar e Sair', self.encerrar_programa_realmente)
        )
        
        # Inicia o ícone na bandeja
        # MUDANÇA CRÍTICA: Alteramos o primeiro parâmetro ("Encomendas_V2") para quebrar o cache do Linux/Windows
        self.tray_icon = pystray.Icon("Encomendas_V2", image, "Servidor Encomendas", menu)
        self.tray_icon.run()

    def restaurar_janela(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.deiconify) # Traz a janela de volta

    def encerrar_programa_realmente(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.desligar_servidor()
        self.root.destroy()

if __name__ == "__main__":
    # Trava obrigatória para o multiprocessing funcionar dentro de executáveis compilados (Nuitka/PyInstaller)
    multiprocessing.freeze_support()
    
    root = tk.Tk()
    app = EncomendasLauncher(root)
    root.mainloop()