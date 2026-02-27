import matplotlib.pyplot as plt
import seaborn as sns
import io
import os, sys
from datetime import datetime
from PIL import Image
import pandas as pd
from matplotlib.lines import lineStyles
from numpy.ma.core import minimum
from load_data import load_config, load_raw_data, load_xy_data, load_position_data, load_distance_data, load_data,create_list, load_media_data, load_data_filtered
from plot_data import draw_map
from scipy.interpolate import make_interp_spline
import numpy as np
import csv

#Load the configuration file____________________________________________________________________________________________________________________________________
#config = load_config('/home/albberto/Documentos/DRAWSAMA/Sama_simulator-main/draw/config.yml') #Config receberá através do uso da função load_config, o conteúdo armazenado no config.yml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yml')
config = load_config(CONFIG_PATH)

##Importante!! Atualizar a função a cima load_config com o diretório da pasta onde está presente o arquivo config.yml!! --> ATUALIZADO-------------------------------------------------------
#____________________________________________________________________________________________________________________________________




#Load the raw data (downlink or uplink) from the .pkl file____________________________________________________________________________________________________________________________________
raw_data = load_raw_data (config['general']['file'], config['general']['type_link']) #Função destinada a carregar o conteúdo do caminho do pkl e se é um caso de uplink ou downlink. O resultado será armazenado no rawdata
#____________________________________________________________________________________________________________________________________



#____________________________________________________________________________________________________________________________________
#Calculate raw_data's length which is the same of number of simulations____________________________________________________________________________________________________________________________________
#Calcula os tamanhos reais do raw_data (quantidade de BSs e simulações) -----------------------------Minha modificação
max_bs_index = len(raw_data)  #Quantidade real de BSs no raw_data = Número de simulações
max_sim_index = len(raw_data[0]) if max_bs_index > 0 else 0  #Quantidade de simulação PARA CADA BS

def create_list(min_value, max_value=None, step=1, max_limit=None):
    if max_value is None: #Caso o usuário não tenha colocado o número máximo de Bs, será assumido o valor mínimo
        max_value = min_value

    if max_limit is not None and max_value > max_limit: #Caso o usuário tenha colocado o número máximo de Bs, mas é maior que o máximo de bs no raw_data, modifica para o limite
        print(f"WARNING: max_value {max_value} exceeds the data limit ({max_limit}), adjusting to {max_limit}")
        max_value = max_limit

    start = max(min_value - 1, 0) #Garante que o valor de início nunca seja negativo.

    if start >= max_value: #Se o valor mínimo, que não é negativo, estiver a cima do limite superior estabelecido, será retornado uma lista vazia, pois os limites não estão dentro do solicitado
        return []

    return list(range(start, max_value, step)) #Retorna uma lista com índice inicial sendo o do start, final sendo o max_value, na contagem de 1 passo

bs_ue_list = create_list(config['general']['bs_ue_min'],config['general']['bs_ue_max'],config['general']['bs_ue_step'],max_limit=max_bs_index)
print(config['general']['bs_ue_max'])
print (bs_ue_list)
simulation_list = create_list(config['general']['s_min'],config['general']['s_max'],config['general']['s_step'],max_limit=max_sim_index)


#carrega médias por BS
media = load_media_data(config['graph']['y_var'], bs_ue_list, simulation_list, raw_data)
media = load_media_data(config['graph']['y_var'], bs_ue_list, simulation_list, raw_data)
media = media.rename(columns={'media por simulação (axis)': 'media'})
media['bs'] = media['bs'].astype(float)
media['bs'] += 1
#___________________________________________________________________________________________________________________________________________
time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #Comando que serve para registrar a data e hora pra quando o gráfico for gerado.


#Construção da saída caso make: graph_________________________________________________________________________________________________________________________________________________________________________________________

#sns.lineplot(media, 'bs', 'media por simulação (axis)') --> Linha desnecessária?



#####################################################################################################################################


 ############################  Glossary #################################
                            #    'distance' → Distance between the UE and its respective BS (Km)   #
                            #    'cap' → Capacity (Mbps)                                           #
                            #    'snr' → Signal-to-noise ratio (dB)                                #
                            #    'avg_latency' → Average latency (ms)                              #
                            #    'user_time' → Time each UE was connected to its BS (ms)           #
                            #    'user_bw' → Bandwidth used by each UE (ms)                        #
                            #    'deficit' → Capacity required to achieve target capacity (Mbps)   #
                            #    'norm_deficit' → Capacity deficit averages (Mbps)                 #
                            #    'start_latency' →  First message exchange between UE and BS (ms)  #
                            #    'min_latency' → Minimum latency (ms)                              #
                            #    'max_latency' → Maximum latency (ms)                              #
                            ########################################################################

####################################################################################################################################






parametros = ['distance','cap','snr','avg_latency','user_time','user_bw','deficit','norm_deficit','start_latency','min_latency','max_latency']

match config['general']['make']:
    case 'graph':
        #var_x = config['graph']['x_var']
        #var_y = config['graph']['y_var']
        if config['graph']['x_var'] not in parametros or config['graph']['y_var'] not in parametros:
            print("x_var or y_var is empty, please select a parameter's glossary for them")
        if config['graph']['media'] == 'True':
            print('Use of media is required!')



#if config['general']['make'] == 'graph': #Carregamento e análise de dados de coordenadas dos eixos x e y
        if config['graph']['x_var'] == 'distance' or config['graph']['y_var']=='distance':
            if config['graph']['x_var'] == 'distance':
                x_data = load_distance_data(bs_ue_list, simulation_list, raw_data)
                y_data = load_data_filtered(config['graph']['y_var'], bs_ue_list, simulation_list, raw_data)
                print(y_data)
            else:
                y_data = load_distance_data(bs_ue_list, simulation_list, raw_data)
                x_data = load_data_filtered(config['graph']['x_var'], bs_ue_list, simulation_list, raw_data)

        else:
            x_data, y_data = load_xy_data(config['graph']['x_var'],config['graph']['y_var'],bs_ue_list,simulation_list, raw_data) 


        #Montagem do design do grafico gerado
        plt.figure(figsize=tuple(config['graph']['figsize']), dpi=config['graph']['resolution'])
        plt.title(config['graph']['title'])
        plt.xlabel(config['graph']['xlabel'])
        plt.ylabel(config['graph']['ylabel'])
        match config['graph']['auto_scale']:
            case 'True':
                plt.autoscale()
                plt.grid(config['graph']['grid'])
            case 'False':
                plt.xlim((config['graph']['xlim']))
                plt.ylim(config['graph']['ylim'])
                plt.grid(config['graph']['grid'])


        #draw the graph
        match config['graph']['graph_type']:
            case 'scatter':
                fig =  sns.scatterplot(x=x_data, y=y_data, color='purple', size=y_data, sizes=(1,1), legend=False)
            case 'line':
                if (config['graph']['x_var'] == 'distance' or config['graph']['y_var'] == 'distance') and  config['graph']['media'] == 'False' :
                    print(f"len(x_data) = {len(x_data)}")
                    print(f"len(y_data) = {len(y_data)}")
                    data_long = pd.DataFrame({"x": x_data, "y": y_data})
                    data_long = data_long.sort_values(by="x").groupby("x", as_index=False).mean()
                    x_smooth = np.linspace(data_long["x"].min(), data_long["x"].max(), 500)  # Mais pontos para suavização
                    spl = make_interp_spline(data_long["x"], data_long["y"], k=1)  # k=3 para spline cúbica
                    y_smooth = spl(x_smooth)
                    sns.lineplot(data=data_long, x='x', y='y', color="blue")
                elif config['graph']['media'] == 'True':
                    plt.figure(dpi=300)
                    sns.lineplot(data=media, x='bs', y='media', errorbar='sd', marker='o', linestyle="--", color='blue')
                    plt.xlim(left=media['bs'].min())
                    plt.ylim(bottom=media['media'].min())
                    plt.xticks(sorted(media['bs'].unique()))
                    plt.xlim(right=media['bs'].max())
                    plt.xlabel("Número de BSs", size=14)
                    plt.ylabel("SNR (dB)", size=14)
                    plt.title("SNR x Número de BSs", size=16) #Esse bloco só está destinado a trabalhar somente caso for SNR?? E as outras configurações como cap e distance?
                    plt.grid(True)
                    plt.tight_layout()
                else:
                    fig = sns.lineplot(x=x_data, y=y_data)
            case 'boxplot':
                fig = sns.boxplot(x=x_data, y=y_data)
            case 'bar':
                fig = sns.barplot(x=x_data, y=y_data, ci=None)
            case 'histplot':
                fig = sns.histplot(x_data)
            case _:
                print("Check the 'graph_type' parameter!")
    #Faltando o programa para 'bar', 'boxplot' or 'histplot')???



    #Bloco de configuração de salvamento da saída gerada_________________________________________________________________________________________________________________________________________________________________________________________

        # save the graph
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        imagem1 = Image.open(buf)
        imagem1.show()
        print('2) Your graph is ready!')
        s = input("3) Do you want to save your graph(y/n)?:")
        match s:
            case "y":
                output_dir = os.path.join("graphics", time)
                os.makedirs(output_dir, exist_ok=True)
                save_path = os.path.join(output_dir, config['graph']['save_as'] + '.png')
                save_path_csv = os.path.join(output_dir, config['graph']['save_as'] + '.csv')

                # salva arquivo .csv
                with open(save_path_csv, mode='w', newline='') as arquivo_csv:
                    escritor = csv.writer(arquivo_csv)
                    escritor.writerow([config['graph']['x_var'], config['graph']['y_var']])
                    for x, y in zip(x_data, y_data):
                        escritor.writerow([x, y])

                imagem1.save(save_path)
                print("4) Graphic saved as " + str(config['graph']['save_as']) + "!")

            case _:
                print ("4) Make the desired changes to config.yml!")



    #Construção da saída caso make: map_________________________________________________________________________________________________________________________________________________________________________________________

    case 'map':

        #draw maps (complete == true --> draw all maps | complete == false --> draw a specific map)
        if config['map']['complete'] == True:
            for t in bs_ue_list:
                for i in simulation_list:
                    title = config['map']['title'] +  ' (' + str(t+1)  + ' BSs, simulation ' + str(i+1) + ')'
                    save_as = str(t+1) +' BSs and ' + str(i+1) + ' simulation_' + config['map']['save_as']
                    uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data,bs_index_data = load_position_data(t, i, raw_data)
                    draw_map(uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data, bs_index_data, title,config['map']['xlabel'], config['map']['ylabel'], config['map']['auto_scale'], config['map']['xlim'], config['map']['ylim'], config['map']['figsize'], config['map']['resolution'], save_as, config['map']['complete'],config['map']['grid'],time )
        elif config['map']['complete'] == False:
            uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data,bs_index_data = load_position_data(config['general']['bs_ue_min'], config['general']['s_min'], raw_data)
            draw_map(uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data, bs_index_data, config['map']['title'],config['map']['xlabel'], config['map']['ylabel'], config['map']['auto_scale'], config['map']['xlim'], config['map']['ylim'], config['map']['figsize'], config['map']['resolution'], config['map']['save_as'], config['map']['complete'],config['map']['grid'],time)
        else:
            print('Complete just be True or False!')





    #Construção da saída caso make: grid_________________________________________________________________________________________________________________________________________________________________________________________

    case 'grid':

        x_labels = config['grid']["x_labels"]
        y_labels = config['grid']["y_labels"]
        folders_matrix = config['grid']["folders_matrix"]

        n_lines, n_cols = len(y_labels), len(x_labels)


        # Cria os subplots
        fig, axes = plt.subplots(n_lines, n_cols, figsize=(5 * n_cols, 4 * n_lines), sharex=True, sharey=True, dpi=300)
        fig.suptitle("Distância x SNR", fontsize=16)


        # Função para encontrar o único CSV dentro de uma pasta
        def find_csv_in_folder(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
            assert len(files) == 1, f"Esperado 1 CSV em {folder_path}, mas encontrei {len(files)}."
            return os.path.join(folder_path, files[0])


        # Loop principal
        for i in range(n_lines):
            for j in range(n_cols):
                folder = '/home/cristiano/PycharmProjects/Sama_simulator/draw/graphics/'+ folders_matrix[i][j]
                csv_path = find_csv_in_folder(folder)
                df = pd.read_csv(csv_path)

                ax = axes[i, j]
                ax.set_xlabel("Distância (km)")
                ax.xaxis.set_tick_params(labelbottom=True, size=16)

                ax.set_ylabel("SNR (dB)")
                ax.yaxis.set_tick_params(labelleft=True, size=16)


                ax.scatter(df['distance'], df['snr'], alpha=0.1, s=1, color="purple")


                # Força os eixos a começarem no zero
                ax.set_xlim(left=0)
                ax.set_ylim(bottom=0)

                # Ativa o grid
                ax.grid(True, linestyle='-', alpha=0.5)

                if i == n_lines - 1:
                    ax.annotate(x_labels[j], xy=(0.5, -0.3), xycoords='axes fraction', ha='center', fontsize=12)
                if j == n_cols - 1:
                    ax.annotate(y_labels[i], xy=(1.02, 0.5), xycoords='axes fraction', rotation=270, va='center', fontsize=12)


        plt.subplots_adjust(hspace=0.4)
        plt.tight_layout()
        # save the graph
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        buf.seek(0)
        plt.close()
        imagem1 = Image.open(buf)
        imagem1.show()
        print('2) Your facet grid is ready!')
        s = input("3) Do you want to save your facet grid(y/n)?:")
        match s:
            case "y":
                output_dir = os.path.join("graphics", time)
                os.makedirs(output_dir, exist_ok=True)
                save_path = os.path.join(output_dir, config['graph']['save_as'] + '.png')

                imagem1.save(save_path)
                print("4) Graphic saved as " + str(config['graph']['save_as']) + "!")

            case _:
                print("4) Make the desired changes to config.yml!")
if config['general']['make'] == None:
    print("The variable make just be 'map' or 'graph'!")
