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


def application():
    eel.init('ui')
    eel.start(
    	'app.html',
        disable_cache=True,
        cmdline_args=[
            '--incognito',
            '--no-experiments',
            '--window-size=700,100',
            '--window-position=700,220'
        ]
    )


@eel.expose()
def download_update():
    eel.call_alert(
        'error',
        'Error',
        'Some error occured.'
    )


providers = get_providers()


# c.download_data(4000000, 50000)
# c.prepare_data()
# c.train_model()

application()
