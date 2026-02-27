#ROTINA QUE PERMITE GERAR GRÁFICO DE % of UE reach Throughtput X BS, THROUGHPUT X BS (CORRIGIDO) e gráfico de DENSITY 
#Testando acréscimo modificação de Throghuput X UE/BS Ratio e % of UE reach Throughtput X UE/BS Ratio (Desenvolvendo)
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
#______________________________________________________________________________________________________________________

#______________________________________Carregamento dos dados brutos__________________________________________________
raw_data = load_raw_data(config['general']['file'], config['general']['type_link'])
#______________________________________________________________________________________________________________________

#___Calculo da quantidade de BSs e simulações__________________________________________________________________________
max_bs_index = len(raw_data)
max_sim_index = len(raw_data[0]) if max_bs_index > 0 else 0


def create_list(min_value, max_value=None, step=1, max_limit=None):
    if max_value is None:
        max_value = min_value
    if max_limit is not None and max_value > max_limit:
        print(f"WARNING: max_value {max_value} exceeds the data limit ({max_limit}), adjusting to {max_limit}")
        max_value = max_limit
    start = max(min_value - 1, 0)
    if start >= max_value:
        return []
    return list(range(start, max_value, step))


bs_ue_list = create_list(
    config['general']['bs_ue_min'],
    config['general']['bs_ue_max'],
    config['general']['bs_ue_step'],
    max_limit=max_bs_index
)

simulation_list = create_list(
    config['general']['s_min'],
    config['general']['s_max'],
    config['general']['s_step'],
    max_limit=max_sim_index
)

#__________________________________Carrega médias por BS______________________________________________________________
if config['graph']['y_var'] != 'distance':
    media = load_media_data(config['graph']['y_var'], bs_ue_list, simulation_list, raw_data)
    media = load_media_data(config['graph']['y_var'], bs_ue_list, simulation_list, raw_data)
    media = media.rename(columns={'media por simulação (axis)': 'media'})
    media['bs'] = media['bs'].astype(float)
    media['bs'] += 1
#______________________________________________________________________________________________________________________

#_____________________________Registro de data e hora_______________________________________________________________
time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#______________________________________________________________________________________________________________________

#__________________________________________Bloco MAKE_______________________________________________________________
match config['general']['make']:

    case 'graph':
        parametros = ['distance','cap','snr','avg_latency','user_time','user_bw','deficit','norm_deficit','start_latency','min_latency','max_latency']
        print('#_____________________________________________________________________________________________________')
        print('Make graph selected')
        if config['graph']['media'] == 'False':
            print('For variable x was selected: ',config['graph']['x_var'])
        print('For variable y was selected: ',config['graph']['y_var'])

        if config['graph']['x_var'] not in parametros or config['graph']['y_var'] not in parametros:
            print("x_var or y_var is empty, please select a parameter's glossary for them")

        print('')

        x_data, y_data = load_xy_data(
            bs_ue_list,
            simulation_list,
            raw_data,
            x_var=config['graph']['x_var'],
            y_var=config['graph']['y_var']
        )

        print('Ploting the graph variables x and y on graph')
        plt.figure(figsize=tuple(config['graph']['figsize']), dpi=config['graph']['resolution'])
        plt.title(config['graph']['title'])
        plt.xlabel(config['graph']['xlabel'])

        if config['graph']['graph_type'] != 'histplot' and config['graph']['graph_type'] != 'boxplot':
            plt.ylabel(config['graph']['ylabel'])
        else:
            plt.ylabel(' ')

        #====================================== BLOCO DE MÉDIA ==========================================
        if config['graph']['media'] == 'True':

            print(' ')
            print("Generating media graph")

            plt.figure(dpi=300)
            sns.lineplot(
                data=media,
                x='bs',
                y='media',
                errorbar='sd',
                marker='o',
                linestyle="--",
                color='blue'
            )

            plt.xlim(left=media['bs'].min())
            plt.ylim(bottom=media['media'].min())
            plt.xticks(sorted(media['bs'].unique()))
            plt.xlim(right=media['bs'].max())
            plt.xlabel("Índice de BS", size=14)
            plt.ylabel(config['graph']['ylabel'], size=14)
            plt.title(config['graph']['title'], size=16)
            plt.grid(True)
            plt.tight_layout()

            #=================== BLOCO %UEs QUE ATINGEM THROUGHPUT ======================================
            if (config['graph']['y_var'] == 'deficit' and
                config['graph']['deficit_%'] == 'True'):

                print(' ')
                print("Generating percentage of UEs that reached target throughput")

                percent_data = []

                for bs in bs_ue_list:

                    total_ues = 0
                    success_ues = 0

                    for sim in simulation_list:
                        try:
                            deficit_array = np.array(raw_data[bs][sim]['deficit'])
                            total_ues += len(deficit_array)
                            success_ues += np.sum(deficit_array < 0)
                        except:
                            pass

                    percent = (success_ues / total_ues) * 100 if total_ues > 0 else 0

                    # ==================================================
                    # SE FOR RAZÃO UE/BS
                    # ==================================================
                    if config['graph']['UE/BS_ratio'] == 'True':

                        num_ue = len(raw_data[bs][simulation_list[0]]['ue_position'])
                        num_bs = bs + 1
                        ratio = num_ue / num_bs

                        percent_data.append({
                            'ratio': ratio,
                            'percent': percent
                        })

                    # ==================================================
                    # SE FOR NÚMERO DE BS (PADRÃO)
                    # ==================================================
                    else:

                        percent_data.append({
                            'bs': bs + 1,
                            'percent': percent
                        })

                percent_df = pd.DataFrame(percent_data)

                if config['graph']['UE/BS_ratio'] == 'True':
                    percent_df = percent_df.sort_values(by='ratio')

                plt.figure(dpi=300)

                # ==================================================
                # GRÁFICO %UEs x BS
                # ==================================================
                if config['graph']['UE/BS_ratio'] == 'False':

                    print("Generating %UEs x Number of BS graph")

                    sns.lineplot(
                        data=percent_df,
                        x='bs',
                        y='percent',
                        marker='o',
                        linestyle='--'
                    )

                    plt.xlabel("Number of BSs", size=14)

                # ==================================================
                # GRÁFICO %UEs x UE/BS
                # ==================================================
                else:

                    print("Generating %UEs x UE/BS ratio graph")

                    sns.lineplot(
                        data=percent_df,
                        x='ratio',
                        y='percent',
                        marker='o',
                        linestyle='--'
                    )
                    plt.xticks(sorted(percent_df['bs'].unique()))
                    plt.xlabel("UE/BS Ratio", size=14)

                plt.ylabel("%UEs that reach target throughput", size=14)
                plt.title("%UEs that Reach the Target Throughput", size=16)
                plt.ylim(0, 100)
                plt.grid(True)
                plt.tight_layout()

            #=================== BLOCO THROUGHPUT x NÚMERO DE BS ===============================
            if config['graph']['y_var'] == 'cap' and config['graph']['media'] == 'True' and config['graph']['Throughput'] == 'True':

                print(' ')
                print("Generating Throughput graph")

                throughput_data = []

                for bs in bs_ue_list:

                    throughput_values = []

                    for sim in simulation_list:
                        try:
                            cap_array = np.array(raw_data[bs][sim]['cap'])

                            if cap_array.size > 0:
                                total_capacity = np.sum(cap_array)
                                throughput_values.append(total_capacity)
                        except:
                            pass

                    if len(throughput_values) > 0:

                        if config['graph']['UE/BS_ratio'] == 'True':

                            # --- Gráfico UE/BS ---
                            num_ue = len(raw_data[bs][simulation_list[0]]['ue_position'])
                            num_bs = bs + 1
                            ratio = num_ue / num_bs

                            throughput_data.append({
                                'ratio': ratio,
                                'throughput': np.mean(throughput_values)
                            })

                        else:

                            # --- Gráfico tradicional ---
                            throughput_data.append({
                                'bs': bs + 1,
                                'throughput': np.mean(throughput_values)
                            })

                throughput_df = pd.DataFrame(throughput_data)

                if config['graph']['UE/BS_ratio'] == 'True':
                    throughput_df = throughput_df.sort_values(by='ratio')

                # =============================
                # GRÁFICO 1: Throughput x BS
                # =============================
                if config['graph']['UE/BS_ratio'] == 'False':

                    print("Generating Throughput x Number of BS graph")

                    plt.figure(dpi=300)
                    sns.lineplot(
                        data=throughput_df,
                        x='bs',
                        y='throughput',
                        marker='o',
                        linestyle='--'
                    )
                    plt.xticks(sorted(throughput_df['bs'].unique()))

                    plt.xlabel("Number of BS", size=14)
                    plt.ylabel(config['graph']['ylabel'], size=14)
                    plt.title(config['graph']['title'], size=16)
                    plt.grid(True)
                    plt.tight_layout()

                # =============================
                # GRÁFICO 2: Throughput x UE/BS
                # =============================
                else:

                    print("Generating Throughput x UE/BS ratio graph")

                    plt.figure(dpi=300)
                    sns.lineplot(
                        data=throughput_df,
                        x='ratio',
                        y='throughput',
                        marker='o',
                        linestyle='--'
                    )

                    plt.xlabel("UE/BS Ratio", size=14)
                    plt.ylabel(config['graph']['ylabel'], size=14)
                    plt.title(config['graph']['title'], size=16)
                    plt.grid(True)
                    plt.tight_layout()

        #====================================== BLOCO SEM MÉDIA ==========================================
        elif config['graph']['media'] == 'False':

            match config['graph']['auto_scale']:
                case 'True':
                    plt.autoscale()
                    plt.grid(config['graph']['grid'])
                case 'False':
                    plt.xlim(config['graph']['xlim'])
                    plt.ylim(config['graph']['ylim'])
                    plt.grid(config['graph']['grid'])

            if config['graph']['graph_type'] == 'line':
                data_long = pd.DataFrame({"x": x_data, "y": y_data})
                data_long = data_long.sort_values(by="x").groupby("x", as_index=False).mean()
                sns.lineplot(data=data_long, x='x', y='y')

            if config['graph']['graph_type'] == 'scatter':
                sns.scatterplot(x=x_data, y=y_data)

            if config['graph']['graph_type'] == 'boxplot':
                sns.boxplot(x=x_data)

            if config['graph']['graph_type'] == 'bar':
                sns.barplot(x=x_data, y=y_data, ci=None)

            if config['graph']['graph_type'] == 'histplot':
                sns.histplot(x_data)

            if config['graph']['graph_type'] == 'density':
                x_clean = pd.Series(x_data).dropna()

                sns.kdeplot(
                    x=x_clean,
                    fill=False,
                    linewidth=2
                )

        #====================================== EXIBIÇÃO ===============================================
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        imagem1 = Image.open(buf)
        imagem1.show()

        #====================================== SALVAMENTO =============================================
        print('')
        s = input("3) Do you want to save your graph(y/n)?:")

        match s:

            case "y":

                output_dir = os.path.join("graphics", time)
                os.makedirs(output_dir, exist_ok=True)

                save_path = os.path.join(output_dir, config['graph']['save_as'] + '.png')
                save_path_csv = os.path.join(output_dir, config['graph']['save_as'] + '.csv')

                with open(save_path_csv, mode='w', newline='') as arquivo_csv:
                    escritor = csv.writer(arquivo_csv)

                    # ======================================================
                    # DENSITY
                    # ======================================================
                    if config['graph']['graph_type'] == 'density':

                        escritor.writerow([config['graph']['x_var']])
                        x_clean = pd.Series(x_data).dropna()

                        for value in x_clean:
                            escritor.writerow([value])

                    # ======================================================
                    # % UEs QUE ATINGEM THROUGHPUT (BS ou UE/BS)
                    # ======================================================
                    elif (config['graph']['media'] == 'True' and
                        config['graph']['y_var'] == 'deficit' and
                        config['graph']['deficit_%'] == 'True'):

                        if config['graph']['UE/BS_ratio'] == 'True':

                            escritor.writerow(['UE/BS_ratio', 'percent_ues_reaching_target'])

                            for _, row in percent_df.iterrows():
                                escritor.writerow([row['ratio'], row['percent']])

                        else:

                            escritor.writerow(['bs', 'percent_ues_reaching_target'])

                            for _, row in percent_df.iterrows():
                                escritor.writerow([row['bs'], row['percent']])

                    # ======================================================
                    # THROUGHPUT (BS ou UE/BS)
                    # ======================================================
                    elif (config['graph']['media'] == 'True' and
                        config['graph']['y_var'] == 'cap' and
                        config['graph']['Throughput'] == 'True'):

                        if config['graph']['UE/BS_ratio'] == 'True':

                            escritor.writerow(['UE/BS_ratio', 'Throughput'])

                            for _, row in throughput_df.iterrows():
                                escritor.writerow([row['ratio'], row['throughput']])

                        else:

                            escritor.writerow(['bs', 'Throughput'])

                            for _, row in throughput_df.iterrows():
                                escritor.writerow([row['bs'], row['throughput']])

                    # ======================================================
                    # MÉDIA NORMAL
                    # ======================================================
                    elif config['graph']['media'] == 'True':

                        escritor.writerow(['bs', config['graph']['y_var']])

                        for bs, val in zip(media['bs'], media['media']):
                            escritor.writerow([bs, val])

                    # ======================================================
                    # GRÁFICO SEM MÉDIA
                    # ======================================================
                    else:

                        escritor.writerow([config['graph']['x_var'], config['graph']['y_var']])

                        for x, y in zip(x_data, y_data):
                            escritor.writerow([x, y])

                imagem1.save(save_path)

                print('')
                print("4) Graphic saved as " + str(config['graph']['save_as']) + "!")

            case "n":
                print('')
                print("4) No data saved! End of process.")

            case _:
                print('')
                print("4) Make the desired changes to config.yml!")