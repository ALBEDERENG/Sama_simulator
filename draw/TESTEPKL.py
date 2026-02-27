import pickle

# Defina o caminho do seu arquivo
nome_arquivo = 'C:\TMP\Arquivos PKL - SAMA\PF20BS - 100 W - TDD 0,1.pkl'

try:
    # 'rb' significa 'read binary' (leitura binária), essencial para arquivos pickle
    with open(nome_arquivo, 'rb') as arquivo:
        conteudo = pickle.load(arquivo)
        
    print("Arquivo carregado com sucesso!")
    print(f"Tipo do objeto carregado: {type(conteudo)}")
    print(conteudo)

except FileNotFoundError:
    print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
except Exception as e:
    print(f"Erro ao abrir o arquivo: {e}")