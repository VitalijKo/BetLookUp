import requests
import neat
import json
import pickle
import os
import random
import time
from pathlib import Path


class CSGORun:
	def __init__(self, log, check):
		self.service_name = self.__class__.__name__
		self.name = self.service_name.lower()
		self.url = 'https://onemails.net/games/'

		provider_path = os.path.join(Path(__file__).parent, self.name)

		if not os.path.isdir(provider_path):
			os.mkdir(provider_path)

		self.games_path = os.path.join(provider_path, 'games.json')
		self.data_path = os.path.join(provider_path, 'data.csv')
		self.model_path = os.path.join(provider_path, 'model.pkl')
		self.config_path = 'config-feedforward.txt'

		self.log = log
		self.check = check

		self.running = False
		self.real = False
		self.multiplier = None
		self.games_data = []

	def __str__(self):
		return self.service_name

	@property
	def last_game_id(self):
		self.log('[yellow]Finding last game...[end]')

		game_id_numbers = list('0000000')

		for i in range(len(game_id_numbers)):
			for j in range(10):
				if not i and not j:
					j = 1

				game_id_numbers[i] = str(j)

				game_id = ''.join(game_id_numbers)

				r = requests.get(f'{self.url}{game_id}')

				if not r.ok:
					game_id_numbers[i] = str(j - 1)

					print(game_id)

					break

		self.log('[green]Last game found![end]')

		return int(game_id)

	@staticmethod
	def game_to_list(game):
		game_data = []

		crash = game['crash']
		bets = game['bets']

		coefficient = 0
		coefficient_auto = 0
		deposit = 0
		withdraw = 0

		for bet in bets:
			coefficient += bet['coefficient'] or 0
			coefficient_auto += bet['coefficient_auto'] or 0
			deposit += bet['deposit'] or 0
			withdraw += bet['withdraw'] or 0

		coefficient = round(coefficient / len(bets), 2)
		coefficient_auto = round(coefficient_auto / len(bets), 2)
		deposit = round(deposit / len(bets), 2)
		withdraw = round(withdraw / len(bets), 2)

		game_data = [coefficient, coefficient_auto, deposit, withdraw, crash]

		return game_data

	def get_game_data(self, game_id):
		if not self.check()():
			return

		fails = 0

		while True:
			try:
				r = requests.get(f'{self.url}{game_id}', timeout=5)

				break
			except:
				if not self.check()():
					return

				fails += 1

				if fails == 6:
					return 1

				time.sleep(5)

		if r.status_code != 200:
			return 1

		game_data = r.json()['data']

		crash = game_data['crash']
		bets = game_data['bets'][:10]

		for i in range(len(bets)):
			bet = game_data['bets'][i]

			coefficient = bet['coefficient'] or 0
			coefficient_auto = bet['coefficientAuto'] or 0
			deposit = bet['deposit']['amount'] or 0
			withdraw = bet['withdraw']['amount'] or 0

			bets[i] = {
				'coefficient': coefficient,
				'coefficient_auto': coefficient_auto,
				'deposit': deposit,
				'withdraw': withdraw
			}

		game_data = {
			'crash': crash,
			'bets': bets
		}

		return game_data

	def get_games_data(self, start, count):
		games_data = []
		game_id = start
		period = count // 10 if count >= 10 else 1

		while len(games_data) != count:
			data = self.get_game_data(game_id)

			if not data:
				return

			if isinstance(data, dict) and len(data['bets']) == 10:
				if period != 1 and not len(games_data) % period:
					self.log(f'[yellow]Downloading games... {len(games_data) // period * 10}%[end]')

				games_data.append(data)

			game_id -= 1

		if period != 1:
			self.log(f'[yellow]Downloading games... 100%[end]')

		return games_data[::-1]

	def download_data(self, start, count):
		self.log()

		games_data = self.get_games_data(start, count)

		if games_data is None:
			self.log('[red]Downloading stopped![end]')

			return 1

		self.log('[green]Games downloaded![end]')
		self.log('[yellow]Saving games...[end]')

		with open(self.games_path, 'w') as games_file:
			json.dump(games_data, games_file)

		self.log(f'[green]Games saved to[end] [yellow]{self.name}/games.json[end][green]![end]')

	def process_data(self):
		self.log()
		self.log('[yellow]Loading games...[end]')

		try:
			with open(self.games_path, 'r') as games_file:
				games = json.load(games_file)
		except Exception as e:
			self.log('[red]Games file not found![end]')

			return

		self.log('[green]Games loaded![end]')

		data_file = open(self.data_path, 'w')
		period = len(games) // 10 if len(games) >= 10 else 1
		last_games = []

		for g, game in enumerate(games):
			if not self.check()():
				self.log('[red]Processing stopped![end]')

				return 1

			game_data = ''

			crash = game['crash']
			bets = game['bets']

			coefficient = 0
			coefficient_auto = 0
			deposit = 0
			withdraw = 0

			for bet in bets:
				coefficient += bet['coefficient'] or 0
				coefficient_auto += bet['coefficient_auto'] or 0
				deposit += bet['deposit'] or 0
				withdraw += bet['withdraw'] or 0

			coefficient = round(coefficient / len(bets), 2)
			coefficient_auto = round(coefficient_auto / len(bets), 2)
			deposit = round(deposit / len(bets), 2)
			withdraw = round(withdraw / len(bets), 2)

			game_data += f'{coefficient},{coefficient_auto},{deposit},{withdraw},{crash}'

			if 'None' in game_data:
				continue

			last_games.append(game_data)

			if len(last_games) == 6:
				last_games_data = ','.join(last_games[:5])

				data = f'{last_games_data},{crash}\n'

				data_file.write(data)

				last_games.pop(0)

				if period != 1 and not g % period:
					self.log(f'[yellow]Processing data... {g // period * 10}%[end]')

		self.log('[yellow]Processing data... 100%[end]')
		self.log(f'[green]Data saved to[end] [yellow]{self.name}/data.csv[end][green]![end][br]')

		data_file.close()

	def load_data(self):
		self.log('[yellow]Loading data...[end]')

		try:
			with open(self.data_path, 'r') as data_file:
				self.games_data = data_file.read().splitlines()
		except:
			self.log('[red]Data file not found![end]')

			return

		try:
			for i in range(len(self.games_data)):
				self.games_data[i] = list(map(float, self.games_data[i].split(',')))
		except:
			self.log('[red]Data file is invalid![end]')

			return

	def save_model(self, genome):
		self.log('[yellow]Saving model...[end]')

		with open(self.model_path, 'wb') as model_file:
			genome = pickle.dump(genome, model_file)

		self.log(f'[green]Model saved to[end] [yellow]{self.name}/model.pkl[end][green]![end][br]')


	def load_model(self):
		self.log('[yellow]Loading model...[end]')

		try:
			with open(self.model_path, 'rb') as model_file:
				genome = pickle.load(model_file)
		except:
			return

		return genome

	def train_model(self, multiplier):
		self.log()

		config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

		p = neat.Population(config)

		p.add_reporter(neat.StdOutReporter(True))

		stats = neat.StatisticsReporter()

		p.add_reporter(stats)

		self.multiplier = multiplier

		winner = p.run(self.simulation, 100)

		self.multiplier = None

		self.log('[green]Training done![end]')

		self.save_model(winner)

	def predict(self, balance, bet):
		self.log()

		data_file = open(self.data_path, 'a')

		config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

		genome = self.load_model()
		genomes = [(1, genome)]

		player = Player(balance=balance, min_bet=bet)

		last_game_id = self.last_game_id
		last_games = self.get_games_data(last_game_id - 1, 5)

		if not last_games:
			return

		wrong = 0
		correct = 0
		max_balance = 0

		self.log()

		while True:
			if not (wrong + correct) % 5:
				self.log()
				self.log(f'[green]Correct:[end] {correct} [red]Wrong:[end] {wrong}')

			self.games_data = [[]]

			game_data = ''

			for game in last_games:
				game = self.game_to_list(game)
	
				self.games_data[0] += game

				game_data += ','.join(list(map(str, game))) + ','

			choice = self.simulation(genomes, config)

			color = 'green' if choice == 1 else 'yellow'

			if choice == 1:
				self.log('Prediction: [green]x1.5[end]')

			else:
				self.log('Prediction: [yellow]SKIP[end]')

			while True:
				try:
					game = self.get_game_data(last_game_id)

					if not game:
						data_file.close()

						return

					elif isinstance(game, dict):
						break
				except:
					continue

			last_game_id += 1
			last_games.pop(0)
			last_games.append(game)

			crash = game['crash']

			game_data += f'{crash}\n'

			data_file.write(game_data)

			if choice == 1:
				if crash >= 1.5:
					player.win()

					correct += 1
					color = 'green'

					if player.balance > max_balance:
						max_balance = player.balance

				else:
					player.lose()

					wrong += 1
					color = 'red'

			else:
				player.wait(crash >= 1.5)

				if crash >= 1.5:
					wrong += 1
					color = ''

				else:
					correct += 1
					color = 'green'

			if not player.alive:
				data_file.close()

				self.log('[red]You lost![end]')
				self.log(f'[red]Max balance:[end] {max_balance}')

				return

			self.log(f'Result: [{color}]x{crash}[end]')
			self.log(f'Balance: [yellow]{player.balance}$[end] Bet: [yellow]{player.bet}$[end]')

	def simulation(self, genomes, config):
		nets = []
		players = []
		min_balance = 1000000
		max_balance = 0
		stakes = 0
		skips = 0

		if not self.real:
			self.load_data()

			random.shuffle(self.games_data)

			if len(self.games_data) >= 10000:
				stop = len(self.games_data) // 10

			self.games_data = self.games_data[:stop]

			self.log('[yellow]Training model...[end]')

		for _, g in genomes:
			net = neat.nn.FeedForwardNetwork.create(g, config)
			nets.append(net)

			g.fitness = 0

			players.append(Player())

		while self.games_data:
			data = self.games_data.pop(0)

			if self.real:
				return nets[0].activate(data)[0]

			game = data[:25]

			result = float(data[25]) >= 1.5

			for i in range(len(players)):
				choice = nets[i].activate(game)[0]

				if choice == 1:
					stakes += 1

					if result:
						players[i].win()

					else:
						players[i].lose()

				else:
					skips += 1

					players[i].wait(result)

			remaining_players = 0

			for i in range(len(players)):
				if players[i].alive:
					remaining_players += 1

					genomes[i][1].fitness = players[i].authority

					if players[i].balance > max_balance:
						max_balance = players[i].balance

					elif players[i].balance < min_balance:
						min_balance = players[i].balance

				else:
					genomes[i][1].fitness = 0

			if not remaining_players:
				break

		if not self.real:
			print(f'Max balance: {max_balance}')
			print(f'Min balance: {min_balance}')
			print(f'Stakes: {stakes}')
			print(f'Skips: {skips}')

		return choice


class Player:
	def __init__(self, balance=10000, min_balance=2000, min_bet=100):
		self.balance = balance
		self.min_balance = self.balance // min_bet
		self.min_bet = min_bet
		self.bet = min_bet
		self.authority = 10

	@property
	def alive(self):
		return self.balance > self.min_balance

	def win(self):
		self.balance += self.bet * 0.5

		if self.bet != self.min_bet:
			self.bet //= 2

		self.authority += 3

	def lose(self):
		self.balance -= self.bet
		self.bet *= 2
		self.authority -= 3

	def wait(self, result):
		if result:
			self.authority -= 2

		else:
			self.authority += 5


__all__ = [CSGORun]
