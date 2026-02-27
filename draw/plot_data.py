import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import io
from PIL import Image


#customize the graph
def customize_graph (title=None, xlabel=None, ylabel=None, auto_scale=True, xlim=None, ylim=None, figsize=None,resolution=None, grid=None):
        plt.figure(figsize=figsize, dpi=resolution)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        match auto_scale:
            case 'True':
                plt.autoscale()
            case 'False':
                plt.xlim(xlim)
                plt.ylim(ylim)
        plt.grid(grid)

        return ()

# save de graph
def save_graph(complete=None, save_as=None, time=None):
    if complete == False:
        plt.show()
        print('2) Your graph is ready!')
        s = input("3) Do you want to save(y/n)?:")
        match s:
            case "y":
                output_dir = os.path.join("graphics", time)
                os.makedirs(output_dir, exist_ok=True)
                save_path = os.path.join(output_dir, save_as)
                plt.savefig(save_path)
            case "n":
                print("4) Make the desired changes to config.yml!")
            case _:
                print("Value not accepted!")
    else:
        plt.savefig(save_path)
        plt.close()

    return ()

# draw the graph
def draw_graph (x_var=None, y_var=None, n_bs=None, n_s=None, figsize=None, resolution=None, title=None, xlabel=None, ylabel=None, auto_scale=True, xlim=None, ylim=None, grid=None, raw_data=None):
        if x_var == 'distance' or y_var == 'distance':
              if x_var == 'distance':
                     x_data = load_distance_data(n_bs, n_s, raw_data)
                     y_data = load_data(y_var,n_bs,n_s, raw_data)
              else:
                     y_data = load_distance_data(n_bs,n_s,raw_data)
                     x_data = load_data(x_var,n_bs,n_s,raw_data)

        else:
           x_data, y_data = load_xy_data(x_var,y_var,n_bs,n_s, raw_data)

        #customize the graph
        customize_graph (title, xlabel, ylabel, auto_scale=True, xlim=None, ylim=None)

        #draw the graph
        match graph_type:
            case 'scatter':
                fig =  sns.scatterplot(x=x_data, y=y_data,size=1)
            case 'line':
                fig = sns.lineplot(x=x_data, y=y_data)
            case 'boxplot':
                fig = sns.boxplot(x=x_data, y=y_data)
            case 'bar':
                fig = sns.barplot(x=x_data, y=y_data, ci=None)
            case 'histplot':
                fig = sns.histplot(x_data)
            case _:
                print("Check the 'graph_type' parameter!")
        save_graph(False, save_as)

        return ()


def draw_map (uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data, bs_index_data, title, xlabel, ylabel, auto_scale=True, xlim=None, ylim=None,figsize=None,resolution=None, save_as=None, complete=False, grid=None, time=None ):
                customize_graph(title, xlabel, ylabel, auto_scale, xlim, ylim, figsize, resolution, grid)
                test = len(uex_off_data)
                if test != 0:
                     sns.scatterplot(x=uex_off_data, y=uey_off_data, marker='o', size=uex_off_data,sizes=(10,10), color='black', legend=False)
                else:
                     {}
                sns.scatterplot(x=bsx_data, y=bsy_data, hue=bs_index_data, marker='^', size=bsx_data, sizes=(200,200),legend=False, palette="rainbow")
                sns.scatterplot(x=uex_data, y=uey_data,hue=bs_index_data, marker='o',size=uex_data,sizes=(10,10),legend=False, palette="rainbow")

                if complete == False:
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    plt.close()
                    imagem1 = Image.open(buf)
                    imagem1.show()
                    print("2) Your map is ready!")
                    s = input("3) Do you want to save(y/n)?:")
                    match s:
                        case 'y':
                            output_dir = os.path.join("graphics", time)
                            os.makedirs(output_dir, exist_ok=True)
                            save_path = os.path.join(output_dir, save_as)
                            imagem1.save(save_path)
                        case 'n':
                            print("4) Make the desired changes to config.yml!")
                        case _:
                            print("Value not accepted!")
                elif complete == True:
                    output_dir = os.path.join("graphics", time)
                    os.makedirs(output_dir, exist_ok=True)
                    save_path = os.path.join(output_dir, save_as)
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    plt.close()
                    imagem1 = Image.open(buf)
                    imagem1.save(save_path)

                else:
                    print("True or False!")

                return ()




