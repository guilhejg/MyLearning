class BankAccount:
    def __init__(self, first_name, last_name, account_id, account_type, pin, balance=0.0):
        # Inicializando os atributos
        self.first_name = first_name
        self.last_name = last_name
        self.account_id = account_id
        self.account_type = account_type
        self.pin = pin
        self.balance = balance  # Valor inicial da conta, padrão 0.0

    # Método para depositar dinheiro
    def deposit(self, amount):
        self.balance += amount  # Adiciona o valor ao saldo
        return self.balance  # Retorna o novo saldo

    # Método para sacar dinheiro
    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount  # Subtrai o valor do saldo
            return amount  # Retorna o valor retirado
        else:
            print("Saldo insuficiente!")
            return 0  # Caso o saque não seja possível, retorna 0

    # Método para exibir o saldo atual
    def display_balance(self):
        print(f"Saldo atual: ${self.balance:.2f}")  # Exibe o saldo com 2 casas decimais


# Criando uma nova conta bancária
account = BankAccount("John", "Doe", 123456, "Checking", 1234)

# Usando os métodos
account.deposit(96)  # Deposita $96
account.withdraw(25)  # Retira $25

# Exibindo o saldo atual
account.display_balance()  # Exibe o saldo atual
