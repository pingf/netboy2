import logging


def analyse_it(payload, response):
    # print('*analyser*' * 20)
    log = logging.getLogger('netboy')
    log.info('analyser!')
    total = len(response)
    normal = 0
    for resp in response:
        state = resp.get('state')
        if state == 'normal':
            normal += 1
    log.warning('state norlmal: '+str(normal))
    log.warning('state error: '+str(total - normal))
