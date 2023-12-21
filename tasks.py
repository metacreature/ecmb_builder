from invoke import task
from lib.ecmb_builder import ecmbBuilder
from lib.ecmblib.ecmb import ecmbException


@task()
def init(ctx, folder_name):
	print(' ', flush=True)
	try:
		builder = ecmbBuilder(folder_name)
		builder.initialize()
		print('\033[1;32;40m  SUCCESS!\x1b[0m\n', flush=True)
	except ecmbException as e:
		msg = '\n'.join(['  ' + p for p in str(e).split('\n')])
		print('\x1b[31;20m\n' + msg + '\n\n FAILED!  \x1b[0m\n', flush=True)
	


@task(optional=["volumes"])
def build(ctx, folder_name, volumes = None):
	print(' ', flush=True)
	try:
		builder = ecmbBuilder(folder_name)
		builder.build(volumes)
		print('\033[1;32;40m  SUCCESS! \x1b[0m\n', flush=True)
	except ecmbException as e:
		msg = '\n'.join(['  ' + p for p in str(e).split('\n')])
		print('\x1b[31;20m\n' + msg + '\n\n  FAILED!  \x1b[0m\n', flush=True)
	

