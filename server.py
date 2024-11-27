import os
import csv
import Pyro4

# Variáveis globais
global client_urls, private_chat_list, all_chat_list
client_urls = {}
private_chat_list = {}
all_chat_list = {}

@Pyro4.expose
class ChatServer:
    def __init__(self):
        self.login_data_path = os.path.join(os.getcwd(), 'loginCheck.csv')

    # Registra um novo cliente no servidor
    def register_client(self, client_uri, client_name):
        global client_urls, private_chat_list, all_chat_list
        client_urls[client_name] = client_uri
        private_chat_list[client_name] = True
        all_chat_list[client_name] = True  # Permitir chat geral por padrão
        print(f'Cliente {client_name} conectado com sucesso!')

    # Remove um cliente do servidor
    def unregister_client(self, client_name):
        global client_urls, private_chat_list, all_chat_list
        if client_name in client_urls:
            del client_urls[client_name]
            del private_chat_list[client_name]
            del all_chat_list[client_name]
            print(f'Cliente {client_name} removido com sucesso!')

    # Altera o tipo de chat para um usuário
    def update_chat_status(self, user_name, is_private):
        global private_chat_list, all_chat_list
        if is_private:
            private_chat_list[user_name] = True
            all_chat_list[user_name] = False
        elif is_private is None:
            private_chat_list[user_name] = False
            all_chat_list[user_name] = False
        else:
            all_chat_list[user_name] = True
            private_chat_list[user_name] = False

    # Verifica se o nome de login já está em uso
    def is_valid_user(self, user_login):
        try:
            with open(self.login_data_path, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                user_logins = [row['UserLogin'] for row in reader]
            return user_login in user_logins
        except FileNotFoundError:
            return False

    # Registra um novo usuário
    def register_user(self, user_info):
        if not self.is_valid_user(user_info['UserLogin']):
            try:
                with open(self.login_data_path, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['UserLogin', 'UserName', 'PassWord'])
                    writer.writerow(user_info)
                return 'Usuário criado com sucesso!'
            except Exception as e:
                return f'Erro ao registrar usuário: {e}'
        else:
            return 'Usuário já existe!'

    # Verifica as credenciais de login
    def verify_login(self, user_login, password):
        try:
            with open(self.login_data_path, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = [row for row in reader]
            for row in data:
                if row['UserLogin'] == user_login and row['PassWord'] == password:
                    return True
            return False
        except FileNotFoundError:
            return False

    # Retorna o nome do usuário e o login
    def get_user_info(self, user_login):
        try:
            with open(self.login_data_path, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['UserLogin'] == user_login:
                        return [row['UserLogin'], row['UserName']]
        except FileNotFoundError:
            return None

    # Retorna todos os usuários conectados
    def get_all_connected_users(self):
        return list(client_urls.keys())

    # Envia uma mensagem para o chat
    def send_message(self, user_login, sender_name, recipient_name, message):
        try:
            print(f'Enviando mensagem de {sender_name} para {recipient_name}: {message}')
            if recipient_name is None:  # Enviar para todos
                for client_name, client_uri in list(client_urls.items()):
                    if client_name != user_login and all_chat_list[client_name]:
                        try:
                            client = Pyro4.Proxy(client_uri)
                            client.receive_message(f'\nMensagem de {sender_name} no chat geral: {message}')
                        except Pyro4.errors.CommunicationError:
                            self.unregister_client(client_name)
            else:  # Mensagem privada
                if recipient_name in client_urls:
                    client_uri = client_urls[recipient_name]
                    try:
                        client = Pyro4.Proxy(client_uri)
                        client.receive_message(f'\nMensagem privada de {sender_name}: {message}')
                    except Pyro4.errors.CommunicationError:
                        self.unregister_client(recipient_name)
                else:
                    client_uri = client_urls[user_login]
                    try:
                        client = Pyro4.Proxy(client_uri)
                        client.receive_message(f'\nMensagem: o usuário {recipient_name} não está conectado')
                    except Pyro4.errors.CommunicationError:
                        self.unregister_client(user_login)
        except Exception as e:
            print(f'Erro ao enviar mensagem: {e}')

# Configuração do servidor Pyro4
daemon = Pyro4.Daemon(host="ipMaquinaServidor")
ns = Pyro4.locateNS(host="ipMaquinaServidor")
uri = daemon.register(ChatServer)
print(f'ChatServer registrado como {uri}')
ns.register("chat.server", uri)
print("Servidor pronto para receber tarefas.")
daemon.requestLoop()