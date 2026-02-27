def covert_to_km (data=None):
  data = (np.array(data)*30)/1000
  return data

def load_position_data(n_bs=None, n_s=None, raw_data=None):
    uex_data=[]
    uey_data=[]
    bsx_data=[]
    bsy_data=[]
    uex_off_data=[]
    uey_off_data=[]
    bs_index_data=[]
    i = n_bs
    t = n_s
    ue_position = raw_data[i][t]['ue_position']
    ue_dim = len(ue_position)
    for ue in range(0,ue_dim):
            df = raw_data[i][t]['ue_bs_table']['bs_index']
            bs_index = df.loc[ue]
            ue_x = ue_position[ue][0]
            ue_y = ue_position[ue][1]
            bs_x = raw_data[i][t]['bs_position'][0][0][bs_index][0]
            bs_y = raw_data[i][t]['bs_position'][0][0][bs_index][1]
            if bs_index != -1:
                 bs_index_data.append(bs_index)
                 uex_data.append(ue_x)
                 uey_data.append(ue_y)
                 bsx_data.append(bs_x)
                 bsy_data.append(bs_y)
            else:
                 uex_off_data.append(ue_x)
                 uey_off_data.append(ue_y)

    uex_data = covert_to_km(uex_data)
    uey_data = covert_to_km(uey_data)
    bsx_data = covert_to_km(bsx_data)
    bsy_data = covert_to_km(bsy_data)
    uex_off_data = covert_to_km(uex_off_data)
    uey_off_data = covert_to_km(uey_off_data)

    return uex_data, uey_data, bsx_data, bsy_data,uex_off_data, uey_off_data, bs_index_data

def load_distance_data(bs_ue_list=None, simulation_list=None, raw_data=None):
    distances = []
    distance=[]
    for i in bs_ue_list:
         distance=[]
         for t in simulation_list:
                ue_position = raw_data[i][t]['ue_position']
                ue_dim = len(ue_position)
                for ue in range(0,ue_dim):
                       df = raw_data[i][t]['ue_bs_table']['bs_index']
                       bs_index = df.loc[ue]
                       if bs_index != -1:
                               ue_x = ue_position[ue][0]
                               ue_y = ue_position[ue][1]
                               bs_x = raw_data[i][t]['bs_position'][0][0][bs_index][0]
                               bs_y = raw_data[i][t]['bs_position'][0][0][bs_index][1]
                               distance = convert_to_km(math.sqrt((bs_x - ue_x) ** 2 + (bs_y - ue_y) ** 2)
                               distances.append(distance)
    return distances
