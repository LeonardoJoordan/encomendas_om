import os
import shutil
import sqlite3
import csv
from datetime import datetime, timezone, timedelta

# 1. Configuração de Fuso Horário (BRT)
BR_TZ = timezone(timedelta(hours=-3))
hoje_br = datetime.now(BR_TZ)
data_str = hoje_br.strftime('%Y-%m-%d')

# 2. Caminhos absolutos (resolve a partir de onde o script está rodando)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "database.sqlite3")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
DB_BACKUP_DIR = os.path.join(BACKUP_DIR, "db")
CSV_BACKUP_DIR = os.path.join(BACKUP_DIR, "relatorios_diarios")

# Cria as pastas de destino silenciosamente, se não existirem
os.makedirs(DB_BACKUP_DIR, exist_ok=True)
os.makedirs(CSV_BACKUP_DIR, exist_ok=True)

def realizar_backup():
    print(f"[{hoje_br.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando rotina de backup...")
    
    # --- PARTE A: CÓPIA DO BANCO DE DADOS ---
    db_backup_path = os.path.join(DB_BACKUP_DIR, f"database_backup_{data_str}.sqlite3")
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, db_backup_path)
        print(f" -> Cópia do banco salva em: {db_backup_path}")
    else:
        print(" -> ERRO: Banco de dados original não encontrado.")
        return

    # --- PARTE B: GERAÇÃO DO CSV DO DIA ---
    csv_path = os.path.join(CSV_BACKUP_DIR, f"relatorio_diario_{data_str}.csv")
    
    try:
        # Conecta direto no SQLite em modo leitura para não atrapalhar o FastAPI
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Filtra registros onde a data_chegada começa com a data de hoje
        query = f"SELECT * FROM encomendas WHERE data_chegada LIKE '{data_str}%'"
        cursor.execute(query)
        
        colunas = [description[0] for description in cursor.description]
        linhas = cursor.fetchall()
        
        # utf-8-sig injeta o BOM invisível para o Excel reconhecer os acentos do PT-BR
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(colunas)
            writer.writerows(linhas)
            
        print(f" -> Relatório CSV ({len(linhas)} registros hoje) salvo em: {csv_path}")
        
    except Exception as e:
        print(f" -> ERRO ao gerar CSV: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            
    print("Backup finalizado com sucesso.")

if __name__ == "__main__":
    realizar_backup()