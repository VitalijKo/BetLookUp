import requests
import neat
import os
import pickle
import json
import time
from pathlib import Path


class CSGORun:
	def __init__(self):
		self.name = 'csgorun'
		self.url = 'https://api.csgorun.pro/games/'

		provider_path = os.path.join(Path(__file__).parent, self.name)

		if not os.path.isdir(provider_path):
			os.mkdir(provider_path)

		self.games_path = os.path.join(provider_path, 'games.json')
		self.data_path = os.path.join(provider_path, 'data.csv')
		self.model_path = os.path.join(provider_path, 'model.pkl')
		self.config_path = 'config-feedforward.txt'

		self.games_data = []

	def __str__(self):
		return 'CSGORun'

	@property
	def last_game_id(self):
		game_id_numbers = list('4000000')

		for i in range(len(game_id_numbers)):
			for j in range(9):
				if not i and not j:
					j = 1

				game_id_numbers[i] = str(j)

				game_id = ''.join(game_id_numbers)

				r = requests.get(f'{self.url}{game_id}')

				if r.status_code != 200:
					game_id_numbers[i] = str(j - 1)

					break

		return game_id

	def get_game_data(self, game_id):
		while True:
			try:
				r = requests.get(f'{self.url}{game_id}', timeout=5)

				break
			except:
				time.sleep(5)

		if r.status_code != 200:
			return


		game_data = r.json()['data']

		crash = game_data['crash']
		bets = game_data['bets'][:10]

		for i in range(len(bets)):
			bet = game_data['bets'][i]

			coefficient = bet['coefficient']
			coefficient_auto = bet['coefficientAuto']
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

		while len(games_data) != count:
			print(len(games_data))
			
			data = self.get_game_data(game_id)

			if data and len(data['bets']) == 10:
				games_data.append(data)

			game_id -= 1

		return games_data[::-1]

	def download_data(self, start, count):
		games_data = self.get_games_data(start, count)

		with open(self.games_path, 'w') as games_file:
			json.dump(games_data, games_file)

	def prepare_data(self):
		with open(self.games_path, 'r') as games_file:
			games = json.load(games_file)

		data_file = open(self.data_path, 'w')

		last_games = []

		for game in games:
			game_data = ''

			crash = game['crash']
			bets = game['bets']

			for bet in bets:
				coefficient = bet['coefficient']
				coefficient_auto = bet['coefficient_auto']
				deposit = bet['deposit']
				withdraw = bet['withdraw']

				game_data += f'{coefficient},{coefficient_auto},{deposit},{withdraw},'

			if 'None' in game_data:
				continue

			game_data += str(crash)

			last_games.append(game_data)

			if len(last_games) == 6:
				last_games_data = ','.join(last_games[:5])

				data = f'{last_games_data},{crash}\n'

				data_file.write(data)

				last_games.pop(0)

		data_file.close()

	def load_data(self):
		with open(self.data_path) as data_file:
			data = data_file.read().splitlines()

		for i in range(len(data)):
			data[i] = list(map(float, data[i].split(',')))

		return data

	def save_model(self, genome):
		with open(self.model_path, 'wb') as model_file:
			genome = pickle.dump(genome, model_file)

		return genome

	def load_model(self):
		with open(self.model_path, 'rb') as model_file:
			genome = pickle.load(model_file)

		return genome

	def train_model(self):
		config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

		p = neat.Population(config)

		p.add_reporter(neat.StdOutReporter(True))

		stats = neat.StatisticsReporter()

		p.add_reporter(stats)

		self.load_data()

		winner = p.run(self.simulation, 100)

		self.save_model(winner)

	def predict(self):
		config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

		genome = self.load_model()

		genomes = [(1, genome)]

		choice = self.simulation(genomes, config)

	def simulation(self, genomes, config):
		nets = []
		players = []
		max_balance = 0

		with open(self.data_path) as data_file:
			games_data = data_file.read().splitlines()

		for _, g in genomes:
			net = neat.nn.FeedForwardNetwork.create(g, config)
			nets.append(net)

			g.fitness = 0

			players.append(Player())

		while games_data:
			data = list(map(float, games_data.pop(0).split(',')))

			game = data[:205]
			result = float(data[205]) >= 1.5

			for i in range(len(players)):
				output = nets[i].activate(game)

				choice = max(output)

				if choice == 1:
					if result:
						players[i].win()

					else:
						players[i].lose()

				else:
					players[i].wait(result)

			remaining_players = 0

			for i in range(len(players)):
				if players[i].alive:
					remaining_players += 1

					genomes[i][1].fitness += players[i].authority

					if players[i].balance > max_balance:
						max_balance = players[i].balance

			print(max_balance, remaining_players)

			if not remaining_players:
				break

		return choice


class Player:
	def __init__(self):
		self.balance = 10000
		self.bet = 100
		self.authority = 10

	@property
	def alive(self):
		return self.balance > 2000

	def win(self):
		self.balance += self.bet * 0.5

		if self.bet != 100:
			self.bet //= 2

		self.authority += 5

	def lose(self):
		self.balance -= self.bet
		self.bet *= 2
		self.authority -= 3

	def wait(self, result):
		if result:
			self.authority -= 0.5

		else:
			self.authority += 1


__all__ = [CSGORun]
