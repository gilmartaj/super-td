# 🇧🇷 Super Tesouro Direto Bot

Um robô que monitora e notifica via Telegram sobre alterações nas taxas dos títulos oferecidos pelo Tesouro Direto.

A versão oficial deste projeto está enviando as mensagens em https://t.me/RepositorioDoTesouroDireto

## 🚀 Pré-requisitos

- Ter o **Python** instalado na máquina.
- Um **Token de Bot** do Telegram (obtido via @BotFather).
- Saber o **ID do Chat** (canal/grupo/usuário) onde as mensagens serão enviadas.

## 🛠️ Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/gilmartaj/super-td
   cd super-td
   ```

2. **Configure as variáveis de ambiente:**

    Crie um arquivo chamado __.env__ na raiz do projeto contendo os seguintes parâmetros e preencha com seus dados:

    ```
    BOT_TOKEN=id_so_seu_bot
    ID_REPOSITORIO=id_do_seu_chat_do_telegram
    RODAPE=@SeuCanalNoTelegram
    ```

3. **Instale as dependências do projeto:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Execute o arquivo main.py:**

    ```bash
    python3 main.py
    ```

* **Docker:**

    Caso você esteja acostumado a usar Docker/Compose, o projeto já está preparado para rodar como container, basta substituir o __passo 4__ pela construção e execução do container:

    ```bash
    docker compose up -d --build
    ```
