import eel
import importlib
import os


def get_providers():
	providers_data = {}

	providers = filter(lambda file: file.endswith('.py'), os.listdir('providers'))

	for provider in providers:
		provider = provider[:-3]

		providers_data[provider] = importlib.import_module('.' + provider, package='providers').__all__[0]()

	return providers_data


def download(provider, settings):
	...


def prepare(provider, settings):
	...


def train(provider, settings):
	...


def predict(provider, settings):
	...


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
	actions[action](provider, settings)


actions = [download, prepare, train, predict]


providers = get_providers()



# c.download_data(4000000, 50000)
# c.prepare_data()
# c.train_model()

application()
