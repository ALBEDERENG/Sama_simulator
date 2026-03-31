#Rotina para plotagem de mapas com as posições dos UE's e BS's posicionados extraídos do pkl informado no config. Necessário
import numpy as np
import matplotlib.pyplot as plt
from load_data import load_config, load_raw_data, load_xy_data, load_position_data, load_distance_data, load_data,create_list, load_media_data, load_data_filtered
from plot_data import draw_map
import os, sys
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yml')
config = load_config(CONFIG_PATH)
raw_data = load_raw_data(config['general']['file'], config['general']['type_link'])

mapa = np.load(config['general']['map'])
posicoes_das_bs = raw_data[19][59]['bs_position'][0][0]
posicoes_dos_ues = raw_data[19][59]['ue_position']


plt.figure(figsize=(8,4), dpi=120, facecolor='white')

# 🔹 fundo (continua matplotlib)
plt.imshow(mapa, cmap='gray')

# ================= UEs =================
y_ue = posicoes_dos_ues[:, 0]
x_ue = posicoes_dos_ues[:, 1]

sns.scatterplot(
    x=x_ue,
    y=y_ue,
    color='darkgoldenrod',
    s=30,
    label='UE'
)

# ================= BS =================

y_bs = posicoes_das_bs[:, 0]
x_bs = posicoes_das_bs[:, 1]

sns.scatterplot(
    x=x_bs,
    y=y_bs,
    color='red',
    s=200,
    marker='^',
    label='BS'
)

plt.legend(loc='upper right')
plt.title("Distribuição de UEs e BSs no bairro de Jardim Botânico (2 km²)")
plt.show()