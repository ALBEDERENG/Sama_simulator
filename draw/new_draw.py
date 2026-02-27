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

#________________________________________________Load the configuration file______________________________________________
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yml')
config = load_config(CONFIG_PATH)
#____________________________________________________________________________________________________________________________________




#______________________________________Carregamento dos dados brutos armazenados em raw_data___________________________
raw_data = load_raw_data (config['general']['file'], config['general']['type_link']) #Função destinada a carregar o conteúdo do caminho do pkl e se é um caso de uplink ou downlink. O resultado será armazenado no rawdata
#____________________________________________________________________________________________________________________________________



#___Calculo da quantidade de BSs e simulações, com correção do limites máximos de simulação existente com o configurado_______________________________

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
#print ('Índices de cada BS são: ',bs_ue_list)
simulation_list = create_list(config['general']['s_min'],config['general']['s_max'],config['general']['s_step'],max_limit=max_sim_index)
#print('Índices de cada simulação BS-UE: ', simulation_list)


#carrega médias por BS
if config['graph']['y_var'] != 'distance':
            media = load_media_data(config['graph']['y_var'], bs_ue_list, simulation_list, raw_data)
            media = load_media_data(config['graph']['y_var'], bs_ue_list, simulation_list, raw_data)
            media = media.rename(columns={'media por simulação (axis)': 'media'})
            media['bs'] = media['bs'].astype(float)
            media['bs'] += 1
#___________________________________________________________________________________________________________________________________________



#_____________________________Comando que serve para registrar a data e hora pra quando o gráfico for gerado___________________________
time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
#___________________________________________________________________________________________________________________________________________



#__________________________________________Bloco de separação pelas condições de make______________________________________________________
match config['general']['make']:
     
#_____________________________________________(MAKE)Bloco de geração de gráficos______________________________________________________
    case 'graph':
        parametros = ['distance','cap','snr','avg_latency','user_time','user_bw','deficit','norm_deficit','start_latency','min_latency','max_latency']
        print('#_____________________________________________________________________________________________________')
        print('Make graph selected') #Prints e teste de seleção correta de x_var e y_var
        print('For variable x was selected: ',config['graph']['x_var'])
        print('For variable y was selected: ',config['graph']['y_var'])
        if config['graph']['x_var'] not in parametros or config['graph']['y_var'] not in parametros: #Teste de verificação se x_var e y_var estão nos parametros sugeridos
            print("x_var or y_var is empty, please select a parameter's glossary for them")
        print('')


#_________________________________(GRAPH)Carregamento de dados sendo atribuídos a x_var e y_var______________________________________________________
        x_data, y_data = load_xy_data(bs_ue_list,simulation_list,raw_data,x_var=config['graph']['x_var'],y_var=config['graph']['y_var'])
        #print('Os valores do eixo x são: ',x_data)
        #print('')
        #print('Os valores do eixo y são: ',y_data)
        #print('')
#___________________________________________________________________________________________________________________________________________



#___________________________________(GRAPH)Plotagem dos detalhes gráficos num gráfico base padrão______________________________________________________
        print('Ploting the graph variables x and y on graph')
        plt.figure(figsize=tuple(config['graph']['figsize']), dpi=config['graph']['resolution'])
        plt.title(config['graph']['title'])
        plt.xlabel(config['graph']['xlabel'])
        if config['graph']['graph_type'] != 'histplot' and config['graph']['graph_type'] != 'boxplot':
            plt.ylabel(config['graph']['ylabel'])
        else:
             plt.ylabel(' ')
        
        if config['graph']['media'] == 'True':
                print(' ')
                print("Generating media graph")
                plt.figure(dpi=300)
                sns.lineplot(data=media, x='bs', y='media', errorbar='sd', marker='o', linestyle="--", color='blue')
                plt.xlim(left=media['bs'].min())
                plt.ylim(bottom=media['media'].min())
                plt.xticks(sorted(media['bs'].unique()))
                plt.xlim(right=media['bs'].max())
                plt.xlabel("Índice de BS", size=14)
                plt.ylabel(config['graph']['ylabel'], size=14)
                plt.title(config['graph']['title'], size=16) #Esse bloco só está destinado a trabalhar somente caso for SNR?? E as outras configurações como cap e distance?
                plt.grid(True)
                plt.tight_layout()

        elif config['graph']['media'] == 'False':

#__________________________(GRAPH)Bloco de geração de gráfico para cada caso de tipo de traçado______________________________________________________

            #elif config['graph']['regression_line'] == 'False':
            match config['graph']['auto_scale']:
                    case 'True':
                        plt.autoscale()
                        plt.grid(config['graph']['grid'])
                    case 'False':
                        plt.xlim(config['graph']['xlim'])
                        plt.ylim(config['graph']['ylim'])
                        plt.grid(config['graph']['grid'])


            if config['graph']['graph_type'] == 'line':
                            print('Type of graph selected: Line')
                            data_long = pd.DataFrame({"x": x_data, "y": y_data})
                            data_long = data_long.sort_values(by="x").groupby("x", as_index=False).mean()
                            x_smooth = np.linspace(data_long["x"].min(), data_long["x"].max(), 500)  # Mais pontos para suavização
                            spl = make_interp_spline(data_long["x"], data_long["y"], k=1)  # k=3 para spline cúbica
                            y_smooth = spl(x_smooth)
                            sns.lineplot(data=data_long, x='x', y='y', color="blue")


            if config['graph']['graph_type'] == 'scatter':
                            print('Type of graph selected: Sactter')
                            #fig = sns.regplot(x=x_data, y=y_data, scatter_kws={'color': 'purple', 's': 10}, line_kws={'color': 'red'})
                            fig =  sns.scatterplot(x=x_data, y=y_data, color='purple', size=y_data, sizes=(10,10), legend=False)

            if config['graph']['graph_type'] == 'boxplot':
                    print('Type of graph selected: Boxplot')
                    fig = sns.boxplot(x=x_data)


            if config['graph']['graph_type'] == 'bar':
                    print('Type of graph selected: Barplot')
                    fig = sns.barplot(x=x_data, y=y_data, ci=None)


            if config['graph']['graph_type'] == 'histplot':
                    print('Type of graph selected: Histplot')
                    fig = sns.histplot(x_data)

    #________________________________(GRAPH)Bloco de geração de gráfico com reta regressão______________________________________________________

            if config['graph']['regression_line'] == 'True':
                            print(' ')
                            print('Regression line on')
                            sns.regplot(x=x_data,y=y_data,scatter=False,line_kws={'color': 'red'})
            elif config['graph']['regression_line'] == 'False':
                  print(' ')
                  print('Regression line off')

#___________________________________________________________________________________________________________________________________________


#______________________________________(GRAPH)Apresentação do gráfico produzido_____________________________________________________________________________

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        imagem1 = Image.open(buf)
        imagem1.show()
        print('')
        print('2) Your graph is ready!')




#______________(GRAPH)Processo de salvamento do gráfico em arquivo csv e geração de tabela na planilha com os dados_____________________________________________________________________________
        print('')
        s = input("3) Do you want to save your graph(y/n)?:")
        match s:
            case "y":
                output_dir = os.path.join("graphics", time)
                os.makedirs(output_dir, exist_ok=True)
                save_path = os.path.join(output_dir, config['graph']['save_as'] + '.png')
                save_path_csv = os.path.join(output_dir, config['graph']['save_as'] + '.csv')

                # salva arquivo .csv
                #with open(save_path_csv, mode='w', newline='') as arquivo_csv:
                #    escritor = csv.writer(arquivo_csv)
                #    escritor.writerow([config['graph']['x_var'], config['graph']['y_var']])
                #    for x, y in zip(x_data, y_data):
                #        escritor.writerow([x, y])



                # salva arquivo .csv
                with open(save_path_csv, mode='w', newline='') as arquivo_csv:
                    escritor = csv.writer(arquivo_csv)

                    if config['graph']['media'] == 'True':
                    # CSV consistente com o gráfico de média
                        escritor.writerow(['bs', config['graph']['y_var']])
                        for bs, val in zip(media['bs'], media['media']):
                            escritor.writerow([bs, val])

                    else:
                        # CSV consistente com gráfico normal
                        escritor.writerow([config['graph']['x_var'], config['graph']['y_var']])
                        for x, y in zip(x_data, y_data):
                            escritor.writerow([x, y])

                imagem1.save(save_path)
                print('')
                print("4) Graphic saved as " + str(config['graph']['save_as']) + "!")
            case "n":
                print('')
                print ("4) No data saved! End of process.")
            case _:
                print('')
                print ("4) Make the desired changes to config.yml!")
#___________________________________________________________________________________________________________________________________________