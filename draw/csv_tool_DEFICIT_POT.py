import os
import io
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime

# ======================================================================================
# ========================= ÁREA DE CONFIGURAÇÃO DO USUÁRIO ============================
# ======================================================================================

# Lista de arquivos CSV (curvas)
CSV_FILES = [
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - BCQI20BS - 40 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - BCQI20BS - 60 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - BCQI20BS - 80 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - BCQI20BS - 100 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - RR20BS - 40 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - RR20BS - 60 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - RR20BS - 80 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - RR20BS - 100 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - PF20BS - 40 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - PF20BS - 60 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - PF20BS - 80 W.csv",
    r"C:\TMP\Arquivos csv - SAMA\UE% X BS\UE% X BS - PF20BS - 100 W.csv"
]

# Nome de cada curva (mesma ordem dos CSVs)
CURVA = [
    "BCQI 30m 40 W",
    "BCQI 30m 60 W",
    "BCQI 30m 80 W",
    "BCQI 30m 100 W",
    "RR 30m 40 W",
    "RR 30m 60 W",
    "RR 30m 80 W",
    "RR 30m 100 W",
    "PF 30m 40 W",
    "PF 30m 60 W",
    "PF 30m 80 W",
    "PF 30m 100 W"
]

# Nome das colunas no CSV
COLUNA_X = "bs"
COLUNA_Y = "percent_ues_reaching_target"

# Definições dos eixos X e Y
DEFINICAO_VAR_X = "Número de BS"
DEFINICAO_VAR_Y = "% UEs"
TITLE = "% UEs that reach the target throughput"

# Ativar modo densidade?
Density = "False"   # "True" ou "False"

# Nome do arquivo de saída
NOME_SAIDA = "grafico_comparacao"


# ======================================================================================
# ============================= VALIDAÇÕES INICIAIS ====================================
# ======================================================================================

if len(CSV_FILES) != len(CURVA):
    raise ValueError("O número de arquivos CSV deve ser igual ao número de nomes de curvas.")

OUTPUT_BASE = os.path.join(os.getcwd(), "graphics")
time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = os.path.join(OUTPUT_BASE, time)
os.makedirs(output_dir, exist_ok=True)

save_path_png = os.path.join(output_dir, NOME_SAIDA + ".png")
save_path_csv = os.path.join(output_dir, NOME_SAIDA + ".csv")

# ======================================================================================
# ================================ PROCESSAMENTO =======================================
# ======================================================================================

plt.figure(figsize=(10,6))

dados_para_csv = []

for csv_path, nome_curva in zip(CSV_FILES, CURVA):

    df = pd.read_csv(csv_path)

    if COLUNA_X not in df.columns:
        raise ValueError(f"Coluna {COLUNA_X} não encontrada no arquivo {csv_path}")

    df = df.dropna()

    # ==================================================================================
    # ============================== MODO DENSIDADE ====================================
    # ==================================================================================
    if Density == "True":

        valores = df[COLUNA_X].values
        serie = pd.Series(valores).dropna()

        # Guarda valores brutos para salvar depois
        df_temp = pd.DataFrame({
            "curva": nome_curva,
            "valor": serie
        })
        dados_para_csv.append(df_temp)

        # Plota densidade KDE
        serie.plot(kind="kde", linewidth=2, label=nome_curva)

    # ==================================================================================
    # ============================== MODO NORMAL =======================================
    # ==================================================================================
    else:

        if COLUNA_Y not in df.columns:
            raise ValueError(f"Coluna {COLUNA_Y} não encontrada no arquivo {csv_path}")

        df_media = (
            df.groupby(COLUNA_X, as_index=False)[COLUNA_Y]
              .mean()
              .sort_values(COLUNA_X)
        )

        df_media["curva"] = nome_curva
        dados_para_csv.append(df_media)

        plt.plot(
            df_media[COLUNA_X],
            df_media[COLUNA_Y],
            marker='o',
            label=nome_curva
        )

# ======================================================================================
# =============================== AJUSTES DO GRÁFICO ===================================
# ======================================================================================

if Density == "True":
    plt.xlabel(DEFINICAO_VAR_X)
    plt.ylabel(DEFINICAO_VAR_Y)
    plt.title(TITLE)
else:
    plt.xlabel(DEFINICAO_VAR_X)
    plt.ylabel(DEFINICAO_VAR_Y)
    plt.title(TITLE)

plt.grid(True)
plt.legend()

# ======================================================================================
# =============================== SALVAR DADOS =========================================
# ======================================================================================

df_saida = pd.concat(dados_para_csv, ignore_index=True)

plt.savefig(save_path_png, dpi=300)
df_saida.to_csv(save_path_csv, index=False)

# Mostrar imagem
buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
plt.close()

imagem = Image.open(buf)
imagem.show()

# ======================================================================================
# =================================== FINAL ============================================
# ======================================================================================

print("\n✅ Arquivos salvos com sucesso!")
print("📌 PNG:", save_path_png)
print("📌 CSV:", save_path_csv)
