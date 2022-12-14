from flask import Flask

server = Flask('my_server')

@server.route('/')
def index():
    return 'Hello World from a containerized server'

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=5000)