from tabulate import tabulate
from datetime import datetime
import re
import math

class Client(object):
    def __init__(self, id, name, email, cpf):
        """
        Constroi todos atributos do objeto client.

        Parameters
        ----------
            id : str
                ID do cliente
            name : str
                Nome do cliente
            email : str
                Email do cliente
            cpf : str
                CPF do cliente
        """

        if not isinstance(id, int):
            raise TypeError('O ID do cliente deve ser um inteiro.')

        if not isinstance(name, str):
            raise TypeError('O nome do cliente deve ser string.')
            
        if not isinstance(email, str):
            raise TypeError('O email do cliente deve ser string.')

        if not isinstance(cpf, str):
            raise TypeError('O CPF do cliente deve ser string.')

        regexEmail = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

        if not re.fullmatch(regexEmail, email):
            raise TypeError('Email invalido.')

        regexCpf = '^[0-9]{3}[\.]?[0-9]{3}[\.]?[0-9]{3}[-]?[0-9]{2}$'

        if not re.fullmatch(regexCpf, cpf):
            raise TypeError('CPF invalido.')

        self.id = id
        self.name = name
        self.email = email
        self.cpf = cpf
    
    def __repr__(self):
        return f'Client(id:{self.id}, name:{self.name}, email:{self.email}, cpf:{self.cpf})'

class Store(object):
    def __init__(self, name, address):
        """
        Constroi todos atributos do objeto store.

        Parameters
        ----------
            name : str
                Nome da loja
            address : str
                Endereco da loja
            clients : list
                Lista de clientes cadastrados na loja
            rentals : list
                Lista de alugueis cadastrados na loja
                    {
                        model: hora/dia/semana
                        family: booleano que representa se o aluguel e da promocao familia
                        start: data inicio
                        end: data entrega
                        bikeId: indice na lista de bikes
                        clientId: indice do clients
                    }
            bikes : list
                Lista de biciletas cadastradas na loja
                    {
                        color: cor da bike
                        available: booleano que informa se esta disponivel
                    }
        """

        if not isinstance(name, str):
            raise TypeError('O nome da loja deve ser string.')
            
        if not isinstance(address, str):
            raise TypeError('O endereco da loja deve ser string.')

        self.name = name
        self.address = address
        self.clients = []
        self.rentals = []
        self.bikes = []
    
    def addBike(self, cor):
        '''
        Metodo que adiciona uma bicicleta a loja.

        Parameters:
        ----------
        cor : str
            Cor da bicicleta
        '''
        self.bikes.append({
            'id': len(self.bikes) + 1,
            'color': cor,
            'available': True
        })
    
    def addClient(self, name, email, cpf):
        '''
        Metodo que adiciona um cliente.

        Parameters:
        ----------
        name : str
            Nome do cliente
        email : str
            Email do cliente
        
        Returns
        -------
        None
        '''
        if self.findClientByEmail(email):
            raise TypeError('Cliente ja cadastrado.')

        self.clients.append(Client(len(self.clients) + 1, name, email, cpf))

    
    def addRental(self, model, email, quantity, family=False):
        '''
        Metodo que adiciona um aluguel.

        Parameters:
        ----------
        model : str
            Modelo de aluguel que pode ser por hora ("hourly"), diário ("daily") ou semanal ("weekly")
        email : str
            Email do cliente
        quantity : int
            Quantidade de alugueis
        family : boolean, optional
            Informa se o aluguel e da promocao em familia, por default e falso
        
        Returns
        -------
        None
        '''
        if not model in ['hourly', 'daily', 'weekly']:
            raise ValueError('Tipo de aluguel invalido.')
        
        if not isinstance(quantity, int):
            raise TypeError('A quantidade de alugueis deve ser inteira.')

        bikesAvailable = self.getAvailableBikes(quantity)

        if len(bikesAvailable) < quantity:
            raise KeyError('Bicicleta indisponivel.')

        existsClient = self.findClientByEmail(email)

        if not existsClient:
            raise KeyError('Cliente nao cadastrado.')
        
        if family and not (quantity >= 3 and quantity <= 5):
            raise ValueError('Aluguel para familia deve ser de 3 a 5 emprestimos.')
        
        for bike in bikesAvailable:
            bike['available'] = False

            self.rentals.append({
                'model': model,
                'family': family,
                'start': datetime.today(),
                'end': None,
                'bikeId': bike['id'],
                'clientId': existsClient.id
            })

    def getAvailableBikes(self, quantity):
        '''
        Metodo que busca as bicicletas disponiveis.

        Parameters:
        ----------
        quantity : int
            Quantidade de bicicletas que deseja buscar
        
        Returns
        -------
        Lista de dicionarios que representam as bicicletas
        '''
        bikes = []

        for bike in self.bikes:
            if len(bikes) == quantity:
                return bikes
            
            if bike['available']:
                bikes.append(bike)
        
        return bikes
    
    def findClientByEmail(self, email):
        '''
        Metodo que busca um cliente a partir do seu email.

        Parameters:
        ----------
        email : str
            Email do cliente
        
        Returns
        -------
        Cliente encontrado ou None
        '''
        for client in self.clients:
            if client.email == email:
                return client
        
        return None

    def showBikes(self):
        '''
        Metodo que imprime todas as bicicletas do estoque.

        Parameters:
        ----------
        None
        
        Returns
        -------
        None
        '''
        print(tabulate(self.bikes, headers="keys", tablefmt="fancy_grid"))

    def calculateRental(self, email):
        '''
        Metodo que calcula o valor de todos os alugueis de um cliente.

        Parameters:
        ----------
        email : str
            Email do cliente
        
        Returns
        -------
        value (float): Valor do aluguel
        '''
        client = self.findClientByEmail(email)

        rentals = [rent for rent in self.rentals if not rent['end'] and rent['clientId'] == client.id]

        bikes = [bike for bike in self.bikes for rent in self.rentals if rent['bikeId'] == bike['id'] and rent['clientId'] == client.id]

        for bike in bikes:
            bike['available'] = True

        value = 0

        valueForFamily = 0

        for rent in rentals:
            rent['end'] = datetime.today()

            if rent['model'] == 'hourly':
                if rent['family']:
                    valueForFamily += self.calculateTime(rent['model'], rent['start'], rent['end']) * 5
                else:
                    value += self.calculateTime(rent['model'], rent['start'], rent['end']) * 5
            elif rent['model'] == 'daily':
                if rent['family']:
                    valueForFamily += self.calculateTime(rent['model'], rent['start'], rent['end']) * 25
                else:
                    value += self.calculateTime(rent['model'], rent['start'], rent['end']) * 25
            elif rent['model'] == 'weekly':
                if rent['family']:
                    valueForFamily += self.calculateTime(rent['model'], rent['start'], rent['end']) * 100
                else:
                    value += self.calculateTime(rent['model'], rent['start'], rent['end']) * 100

        return value + (valueForFamily * 0.7)
    
    def calculateTime(self, model, start, end):
        '''
        Metodo que calcula o tempo do aluguel.

        Parameters:
        ----------
        model : str
            Modelo de aluguel que pode ser por hora ("hourly"), diário ("daily") ou semanal ("weekly")
        start : date
            Data de inicio do aluguel
        end : date
            Data de termino
        
        Returns
        -------
        value (int): Valor que representa a quantidade de tempo do aluguel
        '''
        if end < start:
            raise ValueError('A data de entrega deve ser depois da data de empréstimo.')

        value = 0

        if model == 'hourly':
            value = math.ceil((end - start).total_seconds()/ 3600)
        elif model == 'daily':
            value = math.ceil((end - start).total_seconds()/ 86400)
        elif model == 'weekly':
            value = math.ceil((end - start).total_seconds()/ 604800)
        
        if value < 1:
            return 1
        return value