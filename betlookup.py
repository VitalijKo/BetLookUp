import eel
import importlib
import os


def get_providers():
	providers_data = {

	}

	providers = filter(lambda file: file.endswith('.py'), os.listdir('providers'))

	for provider in providers:
		provider = provider[:-3]

		providers_data[provider] = importlib.import_module('.' + provider, package='providers').__all__[0]()

	return providers_data


def application():
    eel.init('ui')

    try:
        eel.start(
        	'app.html',
            disable_cache=True,
            close_callback=close_callback,
            cmdline_args=[
                '--incognito',
                '--no-experiments',
                '--window-size=700,800',
                '--window-position=700,220'
            ]
        )
    except:
        os.kill(os.getpid(), signal.SIGTERM)


providers = get_providers()

c = providers['csgorun']

print(c)

exit()

c = CSGORun()
# c.download_data(4000000, 50000)
# c.prepare_data()
c.train_model()
