import os
import io
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime

# ======================================================================================
# ========================= ÁREA DE CONFIGURAÇÃO DO USUÁRIO =============================
# ======================================================================================

CSV_FILES = [
    r"C:\tmp\CAPXDISTANCEPF-100W.csv",
    r"C:\tmp\CAPXDISTANCEBCQI-100W.csv"
]

CURVA = [
    "PF 30m 100 W",
    "BCQI 30m 100 W"
]

MEDIA = 'TRUE'          # 'TRUE' ou 'FALSE'
graph_type = 'scatter'  # 'line', 'scatter', 'histplot', 'boxplot'

NOME_SAIDA = "grafico_capxdistance_comparacao"

# ======================================================================================
# ============================= RESOLUÇÃO DE CAMINHO ====================================
# ======================================================================================

if len(CSV_FILES) != len(CURVA):
    raise ValueError("CSV_FILES e CURVA devem ter o mesmo tamanho.")

OUTPUT_BASE = os.path.join(os.getcwd(), "graphics")
time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = os.path.join(OUTPUT_BASE, time)
os.makedirs(output_dir, exist_ok=True)

save_path_png = os.path.join(output_dir, NOME_SAIDA + ".png")
save_path_csv = os.path.join(output_dir, NOME_SAIDA + ".csv")

# ======================================================================================
# ================================ PROCESSAMENTO + GRÁFICO ==============================
# ======================================================================================

plt.figure(figsize=(10, 6))

dados_csv_final = []
header_csv_saida = None

for csv_path, nome_curva in zip(CSV_FILES, CURVA):

    df = pd.read_csv(csv_path)

    # Garante apenas 2 colunas (como especificado)
    df = df.iloc[:, :2].dropna()

    # Captura o header original apenas uma vez
    if header_csv_saida is None:
        header_csv_saida = list(df.columns)

    col_x, col_y = header_csv_saida

    # ==========================================================================
    # MEDIA == 'TRUE' → média é o dado final
    # ==========================================================================
    if MEDIA == 'TRUE':

        # ---- dados brutos (visualização)
        if graph_type == 'scatter':
            plt.scatter(df[col_x], df[col_y], alpha=0.3)
        elif graph_type == 'line':
            plt.plot(df[col_x], df[col_y], alpha=0.3)

        # ---- cálculo da média
        df_final = (
            df.groupby(col_x, as_index=False)[col_y]
              .mean()
              .sort_values(col_x)
        )

        df_final["curva"] = nome_curva
        dados_csv_final.append(df_final)

        # ---- curva média
        plt.plot(
            df_final[col_x],
            df_final[col_y],
            marker='o',
            linewidth=2.5,
            label=nome_curva
        )

    # ==========================================================================
    # MEDIA == 'FALSE' → dado final = dado bruto
    # ==========================================================================
    else:

        df_final = df.copy()
        df_final["curva"] = nome_curva
        dados_csv_final.append(df_final)

        if graph_type == 'scatter':
            plt.scatter(df[col_x], df[col_y], label=nome_curva)

        elif graph_type == 'line':
            plt.plot(df[col_x], df[col_y], label=nome_curva)

        elif graph_type == 'histplot':
            plt.hist(df[col_y], bins=30, alpha=0.6, label=nome_curva)

        elif graph_type == 'boxplot':
            plt.boxplot(df[col_y], positions=[CURVA.index(nome_curva)], widths=0.6)

# ======================================================================================
# =================================== AJUSTES FINAIS ===================================
# ======================================================================================

plt.xlabel(col_x)
plt.ylabel(col_y)
plt.title(f"{col_y} x {col_x}")
plt.grid(True)

if graph_type != 'boxplot':
    plt.legend()

# ======================================================================================
# ========================== SALVAR PNG + CSV E ABRIR IMAGEM ============================
# ======================================================================================

plt.savefig(save_path_png, dpi=300)

df_saida = pd.concat(dados_csv_final, ignore_index=True)

with open(save_path_csv, 'w', encoding='utf-8') as f:
    # header copiado exatamente dos CSVs de entrada (2 colunas)
    f.write(','.join(header_csv_saida) + '\n')

    # dados com 3 colunas (curva na terceira)
    df_saida.to_csv(
        f,
        index=False,
        header=False
    )

buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
plt.close()

Image.open(buf).show()

# ======================================================================================
# =================================== MENSAGEM FINAL ===================================
# ======================================================================================

print("\n✅ Arquivos gerados com sucesso!")
print("📌 PNG:", save_path_png)
print("📌 CSV:", save_path_csv)
