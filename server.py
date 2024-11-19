import os
import csv
import Pyro4

@Pyro4.expose
class ChatServer:
    def __init__(self):
        self.loginData = os.path.join(os.getcwd(),'loginCheck.csv')
        self.cliente_url = {}

    def register_client(self, client_uri, client_name):
        """Registra um novo cliente e seu nome."""
        self.cliente_url[client_uri] = client_name
    
    def Valid_User(self,UserLogin):
        with open(self.loginData, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        user_logins = [row['UserLogin'] for row in data]
        if UserLogin in user_logins:
            return True    
        return False

    def insert_User(self,userInfo):
        valid = self.Valid_User(userInfo['UserLogin'])
        if not valid:
            with open(self.loginData, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['UserLogin','UserName','PassWord'])
                writer.writerow(userInfo)
            return 'Usuario criado com sucesso!'
        else:
            return False
              
    def login_check(self,userLogin,password):

        with open(self.loginData, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        users_login = [row['UserLogin'] for row in data]
        password_users = [row['PassWord'] for row in data]

        for i,user in enumerate(users_login):

            if user == userLogin and password == password_users[i]:
                return True
        return False
    
    def get_username(self,userLogin):
        
        with open(self.loginData, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
        users_login = [row['UserLogin'] for row in data]
        users_names = [row['UserName'] for row in data]
        for i, users in enumerate(users_login):
            if users == userLogin:
                return [users,users_names[i]]
    
    def all_users_connected(self):
        list_all_users = []
        for users in self.cliente_url.values():
            list_all_users.append(users)
        return list_all_users

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(ChatServer)
ns.register("data.analysis1", uri)
print("Servidor pronto para receber tarefas.")
daemon.requestLoop()