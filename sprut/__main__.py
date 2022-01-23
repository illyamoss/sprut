from .cli import run


def goodbye():
    print("Good bye BOSS! Have a nice day.")


try:
    run()
except KeyboardInterrupt:
    goodbye()
else:
    goodbye()
