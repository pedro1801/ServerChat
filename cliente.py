import Pyro4
import os

# Classe para receber mensagens do servidor
@Pyro4.expose
class ChatClient:
    def __init__(self, user_login):
        self.user_login = user_login

    def receive_message(self, message):
        """Recebe uma mensagem do servidor."""
        print(message)

# Conexão do cliente ao servidor
ns = Pyro4.locateNS()
server = Pyro4.Proxy(ns.lookup("chat.server"))

user_fields = ['UserLogin', 'UserName', 'PassWord']
user_info = {}
option = 0

def execute_task(server, function_name, *args):
    try:
        return getattr(server, function_name)(*args)
    except Pyro4.errors.CommunicationError:
        print(f"Falha na comunicação com o servidor ao executar {function_name}.")
        return None

def validate_login():
    option = int(input('1: Fazer Login\n2: Criar Conta\n3: Sair do Chat\nEscolha uma opção: '))
    os.system('clear')
    if option == 1:
        user_login = input('Informe o UserLogin: ')
        password = input('Informe a senha: ')
        is_valid = execute_task(server, 'verify_login', user_login, password)
        
        if is_valid:
            print('Login feito com sucesso!')
            user_data = execute_task(server, 'get_user_info', user_login)
            return user_data
        else:
            print('Senha ou usuário inválidos! Tente novamente.')
            return validate_login()
    elif option == 2:
        user_info = {}
        for field in user_fields:
            user_info[field] = input(f'Informe {field}: ')
        
        response = execute_task(server, 'register_user', user_info)
        if response == 'Usuário já existe!':
            print(response)
            return validate_login()
        else:
            print(response)
            return validate_login()
    elif option == 3:
        print('Saindo do chat...')
        return None
    else:
        print('Escolha uma opção válida.')
        return validate_login()

def list_connected_users():
    return server.get_all_connected_users()

def send_to_all(client_login, client_name):
    option = input('1: Enviar Mensagem e Receber\n2: Voltar\nEscolha uma opção: ')
    os.system('clear')
    if option == '1':
        server.update_chat_status(client_login, False)
        print('Para sair deste modo de chat, digite "sair".')
        while True:
            message = input('Digite sua mensagem: ')
            if message.lower() == 'sair':
                server.update_chat_status(client_login, None)
                break
            else:
                server.send_message(client_login, client_name, None, message)
    elif option == '2':
        return
    else:
        send_to_all(client_login, client_name)

def send_to_user(client_login, client_name):
    option = input('1: Ver Usuários Conectados\n2: Enviar Mensagem\n3: Voltar\nEscolha uma opção: ')
    os.system('clear')
    if option == '1':
        connected_users = list_connected_users()
        print(connected_users)
        send_to_user(client_login, client_name)
    elif option == '2':
        server.update_chat_status(client_login, True)
        recipient_name = input('Informe o usuário para enviar uma mensagem: ')
        print('Para sair deste modo de chat, digite "sair".')
        while True:
            message = input(f'Digite sua mensagem para {recipient_name}: ')
            if message.lower() == 'sair':
                server.update_chat_status(client_login, None)
                break
            else:
                server.send_message(client_login, client_name, recipient_name, message)
    elif option == '3':
        return
    else:
        print('Escolha uma opção válida!')
        send_to_user(client_login, client_name)

def start_communication(client_login, client_name):
    while True:
        option = input('1: Mensagem Geral\n2: Mensagem para Usuário\n3: Sair\nEscolha uma opção: ')
        os.system('clear')
        if option == '1':
            send_to_all(client_login, client_name)
        elif option == '2':
            send_to_user(client_login, client_name)
        elif option == '3':
            daemon.shutdown()
            break
        else:
            print('Escolha uma opção válida!')

user_data = validate_login()

if user_data is not None:
    client = ChatClient(user_data[0])
    daemon = Pyro4.Daemon()  # Cria um daemon para o cliente
    client_uri = daemon.register(client)  # Registra o cliente
    server.register_client(client_uri, user_data[0])  # Registra o cliente no servidor
    
    import threading
    threading.Thread(target=start_communication, args=(user_data[0], user_data[1]), daemon=True).start()
    daemon.requestLoop()
