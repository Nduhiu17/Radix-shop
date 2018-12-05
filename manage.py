#!/usr/bin/env bash
from flask_script import Manager, Server
from app import app

manager = Manager(app)

manager.add_command('server', Server)

if __name__ == '__main__':
    manager.run()