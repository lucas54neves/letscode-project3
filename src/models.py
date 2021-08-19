from tabulate import tabulate
from datetime import datetime
import re
import math

class Client(object):
    def __init__(self, id, name, email, cpf):
        self.id = id
        self.name = name
        self.email = email
        self.cpf = cpf
    
    def __repr__(self):
        return f'Client(id:{self.id}, name:{self.name}, email:{self.email}, cpf:{self.cpf})'

class Store(object):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.clients = []
        self.rents = []
        """
        {
            model: hora/dia/semana
            start: data inicio
            end: data entrega
            bikeId: indice na lista de bikes
            clientId: indice do clients
        }
        """
        self.bikes = []
        """
        {
            color: cor da bike
            available: booleano que informa se esta disponivel
        }
        """
    
    # Metodo que adicionar uma bicicleta
    def addBike(self, cor):
        self.bikes.append({
            'id': len(self.bikes) + 1,
            'color': cor,
            'available': True
        })
    
    # Metodo que adiciona um usuario
    def addClient(self, name, email, cpf):
        try:
            if not (isinstance(name, str) and isinstance(email, str) and isinstance(cpf, str)):
                raise TypeError('Os dados do cliente devem ser strings.')
            
            regexEmail = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

            if not re.fullmatch(regexEmail, email):
                raise TypeError('Email invalido.')
            
            if self.findClientByEmail(email):
                raise TypeError('Cliente ja cadastrado.')

            regexCpf = '^[0-9]{3}[\.]?[0-9]{3}[\.]?[0-9]{3}[-]?[0-9]{2}$'

            if not re.fullmatch(regexCpf, cpf):
                raise TypeError('CPF invalido.')

            self.clients.append(Client(len(self.clients) + 1,name, email, cpf))
        except TypeError as error:
            print(f'ERROR: {error.args[0]}')
        except:
            print(f'ERROR: Erro nao identificado.')

    
    # Metodo que adiciona um aluguel
    def addRental(self, model, email, quantity, family=False):
        try:
            if not model in ['hourly', 'daily', 'weekly']:
                raise ValueError('Tipo de aluguel invalido.')

            bikesAvailable = self.getAvailableBikes(quantity)

            if len(bikesAvailable) < quantity:
                raise KeyError('Bicicleta indisponivel.')

            existsClient = self.findClientByEmail(email)

            if not existsClient:
                raise KeyError('Cliente nao cadastrado.')
            
            if family and not (quantity >= 3 and quantity <= 5):
                raise KeyError('Aluguel para familia deve ser de 3 a 5 emprestimos.')
            
            for bike in bikesAvailable:
                bike['available'] = False

                self.rents.append({
                    'model': model,
                    'family': family,
                    'start': datetime.today(),
                    'end': None,
                    'bikeId': bike['id'],
                    'clientId': existsClient.id
                })
        except (ValueError, Exception, KeyError) as error:
            print(f'ERROR: {error.args[0]}')
        except:
            print(f'ERROR: Erro nao identificado.')

    # Metodo que retorna a primeira bicicleta displonivel
    def getAvailableBikes(self, quantity):
        bikes = []

        for bike in self.bikes:
            if len(bikes) == quantity:
                return bikes
            
            if bike['available']:
                bikes.append(bike)
        
        return bikes
    
    # Metodo que retorna o cliente pelo email
    def findClientByEmail(self, email):
        for client in self.clients:
            if client.email == email:
                return client
        
        return None

    # Metodo que exibe o estoque, ou seja, imprime todas as bicicletas
    def showBikes(self):
        print(tabulate(self.bikes, headers="keys", tablefmt="fancy_grid"))

    # Metodo que calcula o aluguel
    def calculateRent(self, email):
        client = self.findClientByEmail(email)

        rents = [rent for rent in self.rents if not rent['end'] and rent['clientId'] == client.id]

        bikes = [bike for bike in self.bikes for rent in self.rents if rent['bikeId'] == bike['id'] and rent['clientId'] == client.id]

        for bike in bikes:
            bike['available'] = True

        value = 0

        valueForFamily = 0

        for rent in rents:
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
    
    # Metodo que calcula o tempo
    def calculateTime(self, model, start, end):
        value = 0

        if model == 'hourly':
            value = math.ceil(divmod((end - start).total_seconds(), 3600)[0])
        elif model == 'daily':
            value = math.ceil(divmod((end - start).total_seconds(), 86400)[0])
        elif model == 'weekly':
            value = math.ceil(divmod((end - start).total_seconds(), 604800)[0])
        
        if value == 0:
            return 1
        return value