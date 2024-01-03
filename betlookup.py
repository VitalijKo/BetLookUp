import eel
import importlib
import os
import time


def log(message=None):
	if message is not None:
		message = message.replace('[end]', '</span>')
		message = message.replace('[', '<span class="')
		message = message.replace(']', '">')

		time.sleep(1)

	eel.log(message)


def get_providers():
	providers_data = {}

	providers = filter(lambda file: file.endswith('.py'), os.listdir('providers'))

	for provider in providers:
		provider = provider[:-3]

		module = importlib.import_module('.' + provider, package='providers').__all__[0]
		providers_data[provider] = module(log, lambda: eel.get_running())

	return providers_data


def download(provider, settings):
	start = settings.get('start')
	count = settings.get('count')

	if not isinstance(start, int) or not isinstance(count, int):
		return 1

	provider.running = True
	provider.download_data(start, count)

def process(provider, settings):
	provider.running = True
	provider.process_data()


def train(provider, settings):
	multiplier = settings.get('multiplier')

	if not isinstance(multiplier, float):
		return 1

	provider.running = True
	provider.train_model(multiplier)


def predict(provider, settings):
	balance = settings.get('balance')
	bet = settings.get('bet')

	if not isinstance(balance, int) or not isinstance(bet, int):
		return 1

	provider.running = True
	provider.real = True
	provider.predict(balance, bet)


def application():
	eel.init('ui')
	eel.start(
		'app.html',
		disable_cache=True,
		cmdline_args=[
			'--incognito',
			'--no-experiments',
			'--window-size=700,1000',
			'--window-position=700,50'
		]
	)


@eel.expose()
def load_providers():
	providers_names = {provider: providers[provider].service_name for provider in providers}

	eel.load_providers(providers_names)


@eel.expose()
def run(provider, action, settings):
	if provider not in providers:
		return 1

	provider = providers[provider]

	if provider.running or actions[action](provider, settings):
		return 1

	provider.running = False
	provider.real = False

	eel.stop()


actions = [download, process, train, predict]

providers = get_providers()

application()
