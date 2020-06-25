#print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))
from .ply import lex

reserved = {
    'auto':     'R_AUTO',
    'break':    'R_BREAK',
    'case':     'R_CASE',
    'char':     'R_CHAR',
    'const':    'R_CONST',
    'continue': 'R_CONTINUE',
    'default':  'R_DEFAULT',
    'do':       'R_DO',
    'double':   'R_DOUBLE',
    'float':    'R_FLOAT',
    'else':     'R_ELSE',
    'enum':     'R_ENUM',
    'extern':   'R_EXTERN',
    'for':      'R_FOR',
    'goto':     'R_GOTO',
    'if':       'R_IF',
    'int':      'R_INT',
    'main':     'R_MAIN',
    'printf':   'R_PRINTF',
    'register': 'R_REGISTER',
    'return':   'R_RETURN',
    'scanf':    'R_SCANF',
    'sizeof':   'R_SIZEOF',
    'struct':   'R_STRUCT',
    'switch':   'R_SWITCH',
    'void':     'R_VOID',
    'while':    'R_WHILE'
}

tokens = [
    'S_SUM',
    'S_SUBS',
    'S_ASTERISK',
    'S_SLASH',
    'S_PERCENTAGE',
    'S_EQUAL',
    'S_AMPERSAND',
    'S_L_PAR',
    'S_R_PAR',
    'S_L_SQR_BRA',
    'S_R_SQR_BRA',
    'S_L_BRA',
    'S_R_BRA',
    'S_PERIOD',
    'S_COMMA',
    'S_COLON',
    'S_SEMICOLON',
    'S_LESS',
    'S_GREATER',
    'OP_TERNARY',
    'OP_INCREASE',
    'OP_DECREASE',
    'OP_ASSIGN_SUM',
    'OP_ASSIGN_SUBS',
    'OP_ASSIGN_MULT',
    'OP_ASSIGN_DIV',
    'OP_ASSIGN_MOD',
    'OP_ASSIGN_L_SHIFT',
    'OP_ASSIGN_R_SHIFT',
    'OP_ASSIGN_AND',
    'OP_ASSIGN_XOR',
    'OP_ASSIGN_OR',
    'OP_COMPARISSON',
    'OP_DISTINCT',
    'OP_LESS_EQUAL',
    'OP_GREATER_EQUAL',
    'OP_NOT',
    'OP_OR',
    'OP_AND',
    'OPB_OR',
    'OPB_NOT',
    'OPB_XOR',
    'OPB_L_SHIFT',
    'OPB_R_SHIFT',
    'ID',
    'DECIMAL',
    'INTEGER',
    'CHARACTER',
    'STRING',
    'COMMENT'
] + list(reserved.values())

t_S_SUM                 = r'\+'
t_S_SUBS                = r'-'
t_S_ASTERISK            = r'\*'
t_S_SLASH               = r'/'
t_S_PERCENTAGE          = r'%'
t_S_EQUAL               = r'='
t_S_AMPERSAND           = r'&'
t_S_L_PAR               = r'\('
t_S_R_PAR               = r'\)'
t_S_L_SQR_BRA           = r'\['
t_S_R_SQR_BRA           = r'\]'
t_S_L_BRA               = r'{'
t_S_R_BRA               = r'}'
t_S_PERIOD              = r'\.'
t_S_COMMA               = r','
t_S_COLON               = r':'
t_S_SEMICOLON           = r';'
t_S_LESS                = r'<'
t_S_GREATER             = r'>'
t_OP_TERNARY             = r'\?'
t_OP_INCREASE           = r'\+\+'
t_OP_DECREASE           = r'--'
t_OP_ASSIGN_SUM         = r'\+='
t_OP_ASSIGN_SUBS        = r'-='
t_OP_ASSIGN_MULT        = r'\*='
t_OP_ASSIGN_DIV         = r'/='
t_OP_ASSIGN_MOD         = r'%='
t_OP_ASSIGN_L_SHIFT     = r'<<='
t_OP_ASSIGN_R_SHIFT     = r'>>='
t_OP_ASSIGN_AND         = r'&='
t_OP_ASSIGN_XOR         = r'\^='
t_OP_ASSIGN_OR          = r'\|='
t_OP_COMPARISSON        = r'=='
t_OP_DISTINCT           = r'!='
t_OP_LESS_EQUAL         = r'<='
t_OP_GREATER_EQUAL      = r'>='
t_OP_NOT                = r'!'
t_OP_OR                 = r'\|\|'
t_OP_AND                = r'&&'
t_OPB_OR                = r'\|'
t_OPB_NOT               = r'~'
t_OPB_XOR               = r'\^'
t_OPB_L_SHIFT           = r'<<'
t_OPB_R_SHIFT           = r'>>'

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_DECIMAL(t):
    r'\d+\.\d+'
    return t

def t_INTEGER(t):
    r'\d+'
    return t

def t_CHARACTER(t):
    r'(\".\"|\'.\')'
    return t

def t_STRING(t):
    r'(\'.*?\'|\".*?\")'
    return t

def t_COMMENT(t):
    r'//(.*)'
    t.lexer.lineno += 1
    t.lexer.skip(1)

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    newError =  "<tr><td><center>Léxico</center></td>\n"
    newError = newError + "<td><center>El caracter '"+t.value[0]+"' no pertenece al lenguaje MinorC.</center></td>\n" 
    newError = newError + "<td><center>" + str(t.lineno) + "</center></td>\n"
    newError = newError + "</tr>\n"
    #reported_errors.append(newError)
    t.lexer.skip(1)


lexer = lex.lex()