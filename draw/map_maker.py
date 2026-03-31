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

posicoes_das_bs = raw_data[19][59]['bs_position'][0][0]
posicoes_dos_ues = raw_data[19][59]['ue_position']
#ue_pos --> ue_pos[índice do UE, x = 1  e y = 0] 
#Ex: UE_25 = [55,10] --> UE_25_y = ue_pos[25,0] = 10 e UE_25_X = ue_pos[25,1] = 55


mapa = np.load(r'C:\TMP\map_jardim_botanico_atualizado.npy') #INFORMAR O ARQUIVO NUMPY DO MAPA
#posicoes_dos_ues = np.load(r'C:\TMP\ue_pos_botafogo_2.npy')
#posicoes_das_bs = np.load(r'C:\TMP\bs_pos_botafogo_2.npy')

plt.figure(figsize=(8,4),dpi=120,facecolor='white')
plt.imshow(mapa, cmap='gray')

y_ue = posicoes_dos_ues[:, 0]
x_ue = posicoes_dos_ues[:, 1]

plt.scatter(x_ue, y_ue, c='red', s=10, label='UE')

# BS
#bs =posicoes_das_bs[0,0,:,:].copy()
bs = posicoes_das_bs.copy()
y_bs = bs[:, 0]
x_bs = bs[:, 1]

plt.scatter(x_bs, y_bs, c='purple', s=150, marker='^', label='BS')

plt.legend(loc='upper right')
plt.title("Distribuição de UE's e BS no bairro de Jardim Botânico(1 km²)")
plt.show()