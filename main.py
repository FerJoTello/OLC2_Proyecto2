#print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))
from MinorC import Tokens

Tokens.lexer.input("a=0;")
while True:
    tok = Tokens.lexer.token()
    if not tok:
        break
    print(tok)