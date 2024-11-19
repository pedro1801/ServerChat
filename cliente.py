import Pyro4
import os

# Classe para receber mensagens do servidor

@Pyro4.expose
class ChatClient:
    def __init__(self, UserLogin):
        self.userLogin = UserLogin
        
    def receive_message(self, message):
        """Recebe uma mensagem do servidor."""
        print(f"Nova mensagem recebida: {message}")

# Fazendo conexão do cliente ao server
ns = Pyro4.locateNS()
server = Pyro4.Proxy(ns.lookup("data.analysis1")) 

ListInfo = ['UserLogin','UserName','PassWord']
LoginCheck = False
Sair = False  
user_info = {}  
opcao = 0
def executar_tarefa(servidor, funcao, *args):
    try:
        return getattr(servidor, funcao)(*args)
    except Pyro4.errors.CommunicationError:
        print(f"Servidor para {funcao} falhou. Tentando outro servidor...")
        # Tenta encontrar outro servidor com a mesma função
        return None
    
def login_validation():
    opcao = int(input(' 1 : Fazer Login\n 2 : Criar Conta\n 3 : Sair Do Chat \n Escolha uma opção: '))
    os.system('clear')
    if opcao == 1:
        userLogin = input('Informe o UserLogin: ')
        password = input('Informe a senha: ')
        validacao = executar_tarefa(server, 'login_check', userLogin, password)
        
        if validacao:
            print('Login feito com sucesso!')
            resposta = executar_tarefa(server, 'get_username', userLogin)
            return resposta
        else:
            print('Senha ou Usuario invalido! Tente novamente.')
            return login_validation()  # Retorna o valor da chamada recursiva
    
    elif opcao == 2:
        user_info = {}
        for info in ListInfo:
            valor = input(f'Informe {info}: ')
            user_info[info] = valor
        
        resposta = executar_tarefa(server, 'insert_User', user_info)
        if not resposta:
            print('UserLogin já existente! Tente novamente.')
            return login_validation()  # Retorna o valor da chamada recursiva
        else:
            print('Conta criada com sucesso!')
            return login_validation()  # Continua o fluxo chamando a função novamente
    
    elif opcao == 3:
        print('Saindo do chat...')
        return None  # Encerra o programa
    
    else:
        print('Escolha uma opção válida.')
        return login_validation()  # Retorna o valor da chamada recursiva

def see_all_users():
    value = server.all_users_connected()
    return value

def send_for_all():
    print()

def send_for_user(client_login,client_name):
    opcao = input(' 1 - Ver Usuarios conectados\n 2 - Enviar Mensagem\n 3 - Voltar : ')
    os.system('clear')
    if opcao == '1':
        users_conneted = see_all_users()
        print(users_conneted)
        send_for_user(client_login,client_name)
    elif opcao == '2':
        print()
        send_for_user(client_login,client_name)
    elif opcao == '3':
        pass
    else:
        print('Escolha uma opcao valida!')
        send_for_user(client_login,client_name)


def start_comunication(client_login,client_name):
    while True:
        opcao = input(' 1 - Mensagem Geral\n 2 - Mesagem Usuario\n 3 - Sair : ')
        os.system('clear')
        if opcao == '1':
            send_for_all()
        elif opcao == '2':
            send_for_user(client_login,client_name)
        elif opcao == '3':
            break
        else:
            print('Escolha uma opcao valida!')

user_values = login_validation()
if user_values is not None:
    client = ChatClient(user_values[0])
    daemon = Pyro4.Daemon()  # Cria um daemon para o cliente
    client_uri = daemon.register(client)  # Registra o cliente
    server.register_client(client_uri,user_values[0])  # Registra o cliente no servidor
    start_comunication(user_values[0],user_values[1])
