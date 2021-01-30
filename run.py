import cmd

class FotorShell(cmd.Cmd):
    intro = 'Welcome to the fotor shell.'
    prompt = '(Fotor)'

if __name__ == '__main__':
    FotorShell().cmdloop()