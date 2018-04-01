import argparse


from netboy.celery.app import App
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--log", help="display a square of a given number", type=str)
    parser.add_argument("--queue", help="display a cubic of a given number", type=str)
    parser.add_argument("--node", help="display a cubic of a given number", type=str)
    parser.add_argument("--concurrency", help="display a cubic of a given number", type=str)

    args = parser.parse_args()

    argv = ['worker', '-Anetboy.celery.tasks', '-E']

    if args.log:
        choices = ['DEBUG', 'INFO', 'WARNING', 'EXCEPTION', 'CRITICAL']
        if args.log in choices:
            argv.append('-l' + args.log)
    if args.queue:
        argv.append('-Q' + args.queue)
    if args.node:
        argv.append('-n' + args.node)
    if args.concurrency:
        argv.append('-c' + args.concurrency)

    app = App().app
    app.worker_main(argv=argv)
