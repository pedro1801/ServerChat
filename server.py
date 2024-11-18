import os
import csv
import Pyro4

@Pyro4.expose
class ChatServer:
    def __init__(self):
        pass
    
    def Valid_User(self,UserLogin):
        loginData = os.path.join(os.getcwd(),'loginCheck.csv')
        
        with open(loginData, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        user_logins = [row['UserLogin'] for row in data]
        if UserLogin in user_logins:
            return True    
        return False

    def insert_User(self,userInfo):
        valid = self.Valid_User(userInfo['UserLogin'])
        if not valid:
            loginData = os.path.join(os.getcwd(),'loginCheck.csv')
            with open(loginData, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['UserLogin','UserName','PassWord'])
                writer.writerow(userInfo)
            return 'Usuario criado com sucesso!'
        else:
            return False
        
        
    def login_check(self,userLogin,password):
        loginData = os.path.join(os.getcwd(),'loginCheck.csv')

        with open(loginData, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        users_login = [row['UserLogin'] for row in data]
        password_users = [row['PassWord'] for row in data]

        for i,user in enumerate(users_login):

            if user == userLogin and password == password_users[i]:
                return True
        return False
            
daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(ChatServer)
ns.register("data.analysis1", uri)
print("Servidor pronto para receber tarefas.")
daemon.requestLoop()