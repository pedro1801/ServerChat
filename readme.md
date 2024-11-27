# Chat com Pyro4

Este é um sistema de chat básico desenvolvido em Python usando a biblioteca **Pyro4**. Ele suporta a comunicação entre clientes através de mensagens gerais ou privadas, com autenticação de usuários e gerenciamento de contas.

## Funcionalidades

- **Cadastro de Usuários:** Criação de contas com `UserLogin`, `UserName` e `PassWord`.
- **Login e Autenticação:** Validação de credenciais para acessar o sistema.
- **Mensagens Gerais:** Envio de mensagens visíveis para todos os usuários conectados.
- **Mensagens Privadas:** Comunicação direta entre dois usuários.
- **Gerenciamento de Conexões:** Listagem de usuários conectados no chat.

## Tecnologias Utilizadas

- Python
- Pyro4 (Python Remote Objects)
- CSV (para persistência dos dados de login)

## Estrutura do Projeto
ServerChat  
├── cliente.py  
├── loginCheck.csv  
├── readme.md  
└── server.py

## Configuração e Execução

### Requisitos

Certifique-se de que o **Python 3.x** está instalado no sistema. Instale também a biblioteca Pyro4:

$ pip install Pyro4

### Passos para Executar


1. **Inicialize o Servidor:**
   1. **Inicialize o Pyro4:**
        No terminal, execute o comando python -m Pyro4.naming para iniciar o servidor, ou se preferir fazer uma conexão remota use o argumento pyro4-ns -n "ipHost" para poder conectar diferentes máquinas, não esqueça de passar o argumento host="ipHost" dentro da classe Daemon e dentro da função locateNS.
   2. **Como iniciar o server**
        No terminal, execute o script `server.py` para iniciar o servidor:

python server.py

O servidor ficará aguardando conexões de clientes.

2. **Inicie o Cliente:**

Em outro terminal, execute o script `client.py` para iniciar o cliente:

python client.py

Siga as instruções na interface para fazer login, criar uma conta ou sair.

## Funcionalidades em Detalhes

### Servidor

- Registra e autentica clientes.
- Gerencia os modos de chat (geral ou privado).
- Envia mensagens para os clientes conectados.

### Cliente

- Faz login ou registra novos usuários.
- Envia mensagens gerais ou privadas.
- Lista os usuários conectados no sistema.

## Exemplo de Uso

1. Abra dois terminais, um para o servidor e outro para o cliente.
2. No cliente, escolha **"Criar Conta"** para se registrar.
3. Faça login com as credenciais criadas.
4. Envie mensagens gerais ou privadas para outros usuários conectados.
