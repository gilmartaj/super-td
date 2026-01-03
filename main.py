import datetime
import json
import os
import re
import time
import traceback

# Usada para requisições REST, pois a tradicional biblioteca "requests" não funciona
# bem para o propósito deste bot
import curl_cffi
import dotenv

import utilitarios as util

# Expressão regular para um número com casas decimais
PATTERN = r"\d+([,\.]\d+)? ?%"

# Cabeçalhos da requisição
# Outros cabeçalhos podem ser incluídos pela biblioteca para se aproximar
# de uma requisição realizada por um navegador web
CABECALHOS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://www.tesourodireto.com.br/produtos/dados-sobre-titulos/rendimento-dos-titulos',
}

def enviar_mensagem(bot_token, id_chat, mensagem, parse_mode=None):
    URL = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    dados_requisicao = {
        "chat_id": id_chat,
        "text": mensagem,
        "parse_mode": parse_mode
    }
    try:
        response = curl_cffi.requests.post(URL, json=dados_requisicao, headers={"Content-Type": "application/json"})
        return response.status_code // 100 == 2
    except:
        traceback.print_exc()
    return False

def main():

    # Carrega variáveis de ambiente em tempo de execução a partir de um arquivo .env
    # presente no diretótio de execução do programa
    dotenv.load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ID_REPOSITORIO = os.getenv("ID_REPOSITORIO")

    ultimas_taxas = {}
    lista_anterior = []

    try:
        if os.path.exists("dados.json"):
            with open("dados.json", "r") as arq:
                dados = json.loads(arq.read())
                ultimas_taxas = dados["ultimas_taxas"]
                lista_anterior = dados["lista_anterior"]
    except:
        pass

    session = curl_cffi.requests.Session()
    
    reconsultas = 0
    while True:
        try:

            # Se necessário espera até chegar um horário próximo ao da abertura do Tesouro
            # para realizar a verificação de atualização
            h = util.agora()
            print(h)
            parada = datetime.datetime(h.year, h.month, h.day, 9, 30, tzinfo=h.tzinfo)
            if not util.eh_dia_util(h) or h.hour > 18:
                parada += datetime.timedelta(days=1)
            elif h.hour > 9 or h.hour == 9 and h.minute > 28:
                parada = None

            if parada:
                try:
                    espera = parada - util.agora()
                    if espera.total_seconds() > 0:
                        print(f"Esperando até {parada}...") 
                        time.sleep(espera.total_seconds())
                except:
                    traceback.print_exc()

            # Acessa a página inicial do site do Tesouro Direto para atualizar os cookies da sessão
            session.get("https://www.tesourodireto.com.br", impersonate="firefox")
                
            # O impersonate="firefox" faz a mágica de imitar o navegador
            response = session.get("https://www.tesourodireto.com.br/o/rentabilidade/investir", headers=CABECALHOS, impersonate="firefox")
            print(response.status_code)
            if response.status_code == 200:

                lista = response.json()
                lista = [{"treasuryBondName": x["treasuryBondName"], "investmentProfitabilityIndexerName": x["investmentProfitabilityIndexerName"]} for x in lista]

                """aux = list(filter(lambda x: "educa" in x["treasuryBondName"].lower(), lista))
                if len(aux) > 3:
                    aux = [aux[0], aux[len(aux)//2], aux[-1]]

                lista = [x for x in lista if not "educa" in x["treasuryBondName"].lower()]
                lista.extend(aux)"""
                
                # Lógica rudimentar para "desmisturar" títulos sem e com juros semestrais
                for i in range(len(lista)):
                    if i > 0 and not "semestrais" in lista[i]["treasuryBondName"].lower():
                        ref = -1
                        for j in range(i):
                            if "semestrais" in lista[j]["treasuryBondName"].lower() and lista[i]["treasuryBondName"][:13] == lista[j]["treasuryBondName"][:13]:
                                ref = j
                                break
                        if ref > -1:
                            for j in reversed(range(ref, i)):
                                temp = lista[j]
                                lista[j] = lista[j+1]
                                lista[j+1] = temp

                ant = ""
                msg = ""
                if lista == lista_anterior:
                    print("Sem alterações")
                if len(lista) < len(lista_anterior):
                    print(len(lista), len(lista_anterior))
                    if reconsultas < 3:
                        reconsultas += 1
                        time.sleep(90)
                        continue
                reconsultas = 0
                if lista != lista_anterior:

                    for t in lista:

                        l = f'{t["treasuryBondName"]}: *{t["investmentProfitabilityIndexerName"]}* '
                        
                        match = re.search(PATTERN, t["investmentProfitabilityIndexerName"])
                        if match:
                            v = round(float(match.group().replace(",",".").replace("%","")),4)
                            # Inclui caracteres especiais no fim da linha indicando se a taxa atual subiu
                            # ou abaixou em relação à taxa aanterior do mesmo título
                            if t["treasuryBondName"] in ultimas_taxas:
                                if v > ultimas_taxas[t["treasuryBondName"]]:
                                    #l += " `\u23EB`"
                                    l += "\u25b2"
                                elif v < ultimas_taxas[t["treasuryBondName"]]:
                                    #l += " `\u23EC`"
                                    l += "\u25bc"
                            ultimas_taxas[t["treasuryBondName"]] = v

                        # Apenas "perfumaria" adicionando emojis com cores diferentes para tipos diferentes de títulos
                        if "tesouro selic" in l.lower():
                            l = "`\U0001f7e7`" + l
                        if "tesouro prefixado" in l.lower():
                            l = "`\U0001f7e6`" + l
                        if "tesouro ipca+" in l.lower():
                            l = "`\U0001f7e5`" + l
                        if "tesouro renda+" in l.lower():
                            l = "`\U0001f7ea`" + l
                        if "tesouro educa+" in l.lower():
                            l = "`\U0001f7e9`" + l

                        l = l.replace("Tesouro ", "")
                        l = l.replace("com Juros Semestrais", "Juros Sem.")
                        l = l.replace("Aposentadoria Extra ", "")

                        temp_ant = l.split()[0]
                        if ant and ant != temp_ant:
                            print("")
                            msg += "\n"
                        ant = temp_ant

                        msg += "" + l + "\n"

                    if msg:
                        msg = f'*\U0001f1e7\U0001f1f7Tesouro Direto* - Atualização\n\U0001f5d3\uFE0F_{util.agora().strftime("%d/%m/%Y %H:%M")}_\n\n' + msg + "\n" + os.getenv("RODAPE")
                        msg = msg.replace("+", r"\+").replace("-", r"\-").replace(".", r"\.")
                        print(msg)
                        
                        try:
                            if not enviar_mensagem(BOT_TOKEN, ID_REPOSITORIO, msg, parse_mode="MarkdownV2"):
                                raise Exception("Erro ao enviar mensagem")
                        except:
                            traceback.print_exc()
                            time.sleep(60)
                            if not enviar_mensagem(BOT_TOKEN, ID_REPOSITORIO, msg, parse_mode="MarkdownV2"):
                                raise Exception("Erro ao enviar mensagem")

                try:
                    lista_anterior = lista
                    with open("dados.json", "w") as arq:
                        arq.write(json.dumps({"ultimas_taxas": ultimas_taxas, "lista_anterior": lista}))
                except:
                    traceback.print_exc()
        except:
            traceback.print_exc()
        time.sleep(600)
      
if __name__ == "__main__":
    main()