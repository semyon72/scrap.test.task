from app.executors.ria_used_cars import Executor
from app import env


if __name__ == '__main__':
    Executor(env).execute()
