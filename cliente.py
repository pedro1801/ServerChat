import Pyro4
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import threading

# Classe para receber mensagens do servidor
@Pyro4.expose
class ChatClient:
    def __init__(self, user_login):
        self.user_login = user_login
        self.root = tk.Tk()
        self.root.withdraw()
        self.chat_box = None
        self.entry = None
        self.recipient_name = None
        self.client_name = None

    def create_chat_window(self, title):
        self.root = tk.Tk()
        self.root.title(title)
        self.chat_box = scrolledtext.ScrolledText(self.root, state='disabled', width=50, height=20)
        self.chat_box.pack(padx=10, pady=10)
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)

    def receive_message(self, message):
        """Recebe uma mensagem do servidor."""
        self.chat_box.config(state='normal')
        self.chat_box.insert(tk.END, message + "\n")
        self.chat_box.config(state='disabled')
        self.chat_box.yview(tk.END)

    def send_message(self, event=None):
        message = self.entry.get()
        if message:
            def send():
                try:
                    if message.lower() == 'sair':
                        self.root.after(0, self.close_chat)
                        return
                    if self.recipient_name:
                        # Envia mensagem privada
                        server.send_message(self.user_login, self.client_name, self.recipient_name, message)
                        self.receive_message(f'Você (privado): {message}')  # Exibe a mensagem enviada na interface do remetente
                    else:
                        # Envia mensagem para todos
                        server.send_message(self.user_login, self.client_name, None, message)
                        self.receive_message(f'Você (geral): {message}')  # Exibe a mensagem enviada na interface do remetente
                    self.entry.delete(0, tk.END)
                except Pyro4.errors.CommunicationError:
                    self.root.after(0, lambda: messagebox.showerror("Erro", "Falha na comunicação com o servidor ao enviar a mensagem."))
            
            threading.Thread(target=send).start()
            
    def close_chat(self):
        if self.root:
            self.root.withdraw()
            self.root.after(0, lambda: start_communication(self))

    def close(self):
        try:
            server.unregister_client(self.user_login)
        except Pyro4.errors.CommunicationError:
            pass
        if self.root:
            self.root.destroy()
            self.root = None
        if daemon:
            daemon.shutdown()
        exit(0)

# Conexão do cliente ao servidor
try:
    ns = Pyro4.locateNS(host="ipMaquinaServidor")
    server = Pyro4.Proxy(ns.lookup("chat.server"))
    print(f"Conexão com o servidor estabelecida. {server}")
except Pyro4.errors.NamingError:
    messagebox.showerror("Erro", "Não foi possível localizar o servidor.")
    exit(1)

user_fields = ['UserLogin', 'UserName', 'PassWord']
user_info = {}
option = 0

def execute_task(server, function_name, *args):
    try:
        return getattr(server, function_name)(*args)
    except Pyro4.errors.CommunicationError:
        messagebox.showerror("Erro", f"Falha na comunicação com o servidor ao executar {function_name}.")
        return None

def validate_login():
    root = tk.Tk()
    root.withdraw()
    option = simpledialog.askinteger("Login", "1: Fazer Login\n2: Criar Conta\n3: Sair do Chat\nEscolha uma opção:")
    if option == 1:
        user_login = simpledialog.askstring("Login", "Informe o UserLogin:")
        password = simpledialog.askstring("Login", "Informe a senha:", show='*')
        is_valid = execute_task(server, 'verify_login', user_login, password)
        
        if is_valid:
            messagebox.showinfo("Sucesso", "Login feito com sucesso!")
            user_data = execute_task(server, 'get_user_info', user_login)
            return user_data
        else:
            messagebox.showerror("Erro", "Senha ou usuário inválidos! Tente novamente.")
            return validate_login()
    elif option == 2:
        user_info = {}
        for field in user_fields:
            user_info[field] = simpledialog.askstring("Registro", f'Informe {field}:')
        
        response = execute_task(server, 'register_user', user_info)
        messagebox.showinfo("Registro", response)
        return validate_login()
    elif option == 3:
        messagebox.showinfo("Sair", "Saindo do chat...")
        return None
    else:
        messagebox.showerror("Erro", "Escolha uma opção válida.")
        return validate_login()

def list_connected_users():
    try:
        return server.get_all_connected_users()
    except Pyro4.errors.CommunicationError:
        messagebox.showerror("Erro", "Falha na comunicação com o servidor ao listar usuários conectados.")
        return []

def send_to_all(client):
    client.recipient_name = None
    client.chat_box.config(state='normal')
    client.chat_box.insert(tk.END, "Modo de mensagem geral ativado. Digite 'sair' para sair.\n")
    client.chat_box.config(state='disabled')
    client.chat_box.yview(tk.END)

def send_to_user(client):
    option = simpledialog.askinteger("Mensagem Privada", "1: Ver Usuários Conectados\n2: Enviar Mensagem\n3: Voltar\nEscolha uma opção:")
    if option == 1:
        connected_users = list_connected_users()
        messagebox.showinfo("Usuários Conectados", "\n".join(connected_users))
        send_to_user(client)
    elif option == 2:
        client.recipient_name = simpledialog.askstring("Mensagem Privada", "Informe o usuário para enviar uma mensagem:")
        if client.recipient_name not in list_connected_users():
            messagebox.showerror("Erro", "Usuário não está conectado.")
            return
        client.chat_box.config(state='normal')
        client.chat_box.insert(tk.END, f"Modo de mensagem privada para {client.recipient_name} ativado. Digite 'sair' para sair.\n")
        client.chat_box.config(state='disabled')
        client.chat_box.yview(tk.END)
    elif option == 3:
        return
    else:
        messagebox.showerror("Erro", "Escolha uma opção válida!")
        send_to_user(client)

def start_communication(client):
    def ask_option():
        option = simpledialog.askinteger("Comunicação", "1: Mensagem Geral\n2: Mensagem para Usuário\n3: Sair\nEscolha uma opção:")
        if option == 1:
            client.create_chat_window("Chat Geral")
            send_to_all(client)
            client.root.protocol("WM_DELETE_WINDOW", client.close_chat)
            client.root.mainloop()
        elif option == 2:
            client.create_chat_window("Chat Privado")
            send_to_user(client)
            client.root.protocol("WM_DELETE_WINDOW", client.close_chat)
            client.root.mainloop()
        elif option == 3:
            client.close()
        else:
            messagebox.showerror("Erro", "Escolha uma opção válida!")
            client.root.after(0, ask_option)

    client.root.after(0, ask_option)

def main():
    user_data = validate_login()

    if user_data is not None:
        client = ChatClient(user_data[0])
        client.client_name = user_data[1]
        global daemon
        daemon = Pyro4.Daemon(host="ipMaquinaServidor")  # Cria um daemon para o cliente
        client_uri = daemon.register(client)  # Registra o cliente
        server.register_client(client_uri, user_data[0])  # Registra o cliente no servidor
        
        threading.Thread(target=daemon.requestLoop, daemon=True).start()

        # Cria uma janela principal oculta
        root = tk.Tk()
        root.withdraw()
        client.root = root

        start_communication(client)
        client.root.mainloop()

if __name__ == "__main__":
    main()