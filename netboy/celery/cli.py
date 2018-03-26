import os
import socket
import sys

from inquirer import themes

from netboy.celery.app import App

sys.path.append(os.path.realpath('.'))
import inquirer

if __name__ == '__main__':

    ENV_IP = os.environ.get('ENV_IP', '127.0.0.1')
    ip = ENV_IP
    if '.' not in ip:
        ip = [(s.connect(('223.5.5.5', 53)), s.getsockname()[0], s.close()) for s in
              [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    questions = [
        inquirer.Text('node', message="node name?", default='node01'),

        inquirer.List('log_level',
                      message="log level?",
                      choices=['DEBUG', 'INFO', 'WARNING', 'EXCEPTION', 'CRITICAL'],
                      default='INFO'
                      ),
        inquirer.Text('queue', message="queue name?", default='worker'),
        inquirer.Text('concurrency', message="concurrency?", default='8'),
    ]

    a = inquirer.prompt(questions, theme=themes.GreenPassion())

    cmd = ['worker', '-l' + a.get('log_level'), '-Anetboy.celery.tasks', '-Q' + a.get('queue'), '-n' + a.get('node'),
           '-c' + a.get('concurrency'), '-E'
           ]

    app = App().app
    app.worker_main(
        argv=cmd)
