import Pyro4

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
def logi_validation():
    opcao = int(input(' 1 : Fazer Longin\n 2 : Criar Conta\n 3 : Sair Do Chat \n Escolha uma opção :'))
    if opcao == 1:
        userLogin = input('Informe o UserLogin: ')
        password = input('Informe a senha: ')
        validacao = executar_tarefa(server,'login_check',userLogin,password)
        if validacao:
            print('Login feito com sucesso!')
        else:
            print('Senha ou Usuario invalido!')
            logi_validation()
    elif opcao == 2:
        user_info = {}    
        for info in ListInfo:
            valor = input(f'Informe {info} :')
            user_info[info] = valor
        resposta = executar_tarefa(server,'insert_User',user_info)
        if not resposta:
            print('UserLogin já existente!')
            logi_validation()
        else:
            print(resposta)
    elif opcao == 3:
        pass
    else:
        print('Escolha uma opção valida')
        logi_validation()          
logi_validation()    