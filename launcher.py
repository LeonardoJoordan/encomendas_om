import tkinter as tk
import subprocess
import sys
import webbrowser
import time

class EncomendasLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Encomendas OM - Servidor")
        self.root.geometry("350x180")
        self.root.resizable(False, False)
        
        # Centraliza a janela
        self.root.eval('tk::PlaceWindow . center')

        self.processo_servidor = None

        # Elementos da Interface
        self.lbl_titulo = tk.Label(root, text="Gestor do Servidor", font=("Arial", 14, "bold"))
        self.lbl_titulo.pack(pady=10)

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
        comando = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
        
        try:
            self.processo_servidor = subprocess.Popen(comando)
            self.lbl_status.config(text="Status: Rodando (Porta 8000)", fg="green")
            self.btn_toggle.config(text="Desligar Servidor", bg="#dc3545") # Fica vermelho
            
            # Aguarda um segundo para o servidor subir e abre o navegador
            self.root.after(1000, lambda: webbrowser.open("http://127.0.0.1:8000"))
        except Exception as e:
            self.lbl_status.config(text=f"Erro ao ligar", fg="red")
            print(f"Erro: {e}")

    def desligar_servidor(self):
        if self.processo_servidor:
            self.processo_servidor.terminate() # Mata o processo do servidor
            self.processo_servidor.wait()      # Aguarda ele fechar completamente
            self.processo_servidor = None
            
        self.lbl_status.config(text="Status: Desligado", fg="red")
        self.btn_toggle.config(text="Ligar Servidor", bg="#28a745") # Fica verde

    def fechar_aplicativo(self):
        self.desligar_servidor()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EncomendasLauncher(root)
    root.mainloop()