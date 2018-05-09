def debug(body):
    with open('/tmp/log.txt', 'a') as f:
        f.write(str(body) + '\n')
