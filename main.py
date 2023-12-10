from flask import Flask, jsonify
import pandas as pd

NCM_path = './NCM.xlsx'
NCM_DESCRI = './NCM_DESCRI.xlsx'
data = pd.read_excel(NCM_path, converters={'NCM': str}).to_dict(orient='records')
data_descri = pd.read_excel(NCM_DESCRI,header=4, converters={'Código': str,'Descrição Concatenada': str}).to_dict(orient='records')
print(data_descri[0])
app = Flask(__name__)

def checancm(ncmRecebido):
    global uTrib, descri, Similar, descri_con
    uTrib = []  # Limpar a lista antes de uma nova consulta
    descri = []  # Limpar a lista antes de uma nova consulta
    descri_con = []
    Similar = []
    Valida = 0

    # Validate NCM length and format
    if len(ncmRecebido) != 8 or not ncmRecebido.isdigit():
        Valida = 3
    else:
        for x in range(len(data)):
            valor = str(data[x]['NCM'])

            if ncmRecebido == valor:
                uTrib.append(str(data[x]['uTrib']))
                for d in range(len(data_descri)):
                    Cod_NCM = data_descri[d]['Código']
                    Cod_Formatado = str(Cod_NCM).replace('.', '')
                    if Cod_Formatado == valor:
                        descri_encontrada = data_descri[d]['Descrição']
                        descri_con_encontrada = data_descri[d]['Descrição Concatenada']
                        descri_con_encontrada = descri_con_encontrada.lstrip('-')
                        descri_formatada = descri_encontrada.lstrip('-')
                        descri_con.append(descri_con_encontrada)
                        descri.append(descri_formatada)
                Valida = 1
                break

        if Valida != 1:
            Valida = 2
            for z in range(len(data)):
                valor = str(data[z]['NCM'])
                reduzido = valor[:6]

                if ncmRecebido[:6] == reduzido:
                    for d in range(len(data_descri)):
                        Cod_NCM = data_descri[d]['Código']
                        Cod_Formatado = str(Cod_NCM).replace('.', '')
                        if Cod_Formatado == valor:
                            descri_encontrada = data_descri[d]['Descrição']
                            descri_formatada = descri_encontrada.lstrip('-')
                            descri_con_encontrada = data_descri[d]['Descrição Concatenada']
                            descri_con_encontrada = descri_con_encontrada.lstrip('-')
                            descri_con.append(descri_con_encontrada)
                            descri.append(descri_formatada)
                    Similar.append(valor)
                    uTrib.append(str(data[z]['uTrib']))

    return Valida


# Rota para a raiz da API
@app.route('/')
def home():
    return 'Bem-vindo à API Flask!'

# Rota para retornar dados em formato JSON
@app.route('/api/<ncm>', methods=['GET'])
def get_data(ncm):

    resultado = checancm(ncm)

    if resultado == 1:
        data = {'NCM': ncm, 'Descricao': descri[0], 'Concatenado': descri_con[0] ,'uTrib': uTrib[0],'Status':'1'}
        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response,200

    elif resultado == 2:
         data = {'NCM': f'{ncm} inválido, foram encontrados similares', 'Concatenado': descri_con, 'Similares': Similar, 'Descricao_Similares' : descri,'Status': '2','uTrib' : uTrib}
         response = jsonify(data)
         return response,200

    elif resultado == 3 :
        data = {"Erro": "NCM digitado é inválido, tente outro NCM"}
        response = jsonify(data)
        return response,400

if __name__ == '__main__':
    app.run(debug=True)
