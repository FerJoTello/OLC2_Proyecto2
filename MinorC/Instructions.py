from enum import Enum
#print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__, __name__, str(__package__)))


class TYPE(Enum):
    INTEGER = 1
    DOUBLE = 2
    FLOAT = 3
    CHAR = 4
    STRING = 5
    VOID = 6
    STRUCT = 7
    ARRAY = 8


def set_type(type):
    types = {
        'int': TYPE.INTEGER,
        'double': TYPE.DOUBLE,
        'float': TYPE.FLOAT,
        'char': TYPE.CHAR,
        'void': TYPE.VOID,
        'struct': TYPE.STRUCT,
        'INTEGER': TYPE.INTEGER,
        'DECIMAL': TYPE.FLOAT,
        'CHARACTER': TYPE.CHAR,
        'STRING': TYPE.STRING
    }
    return types.get(type, None)


def set_value(type):
    types = {
        'int': '0',
        'double': '0.0',
        'float': '0.0',
        'char': "' '",
        'STRING': '" "'
    }
    return types.get(type, None)


class DeclarationList:
    def __init__(self, declarations):
        self.declarations = declarations


class Declaration:
    def __init__(self, type, identifier, expression):
        self.type = set_type(type)
        self.identifier = identifier
        self.expression = expression


class Assignation:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression


class Parameter:
    def __init__(self, type, id):
        self.type = set_type(type)
        self.id = id


class Function:
    def __init__(self, return_type, id, parameters, instructions):
        self.return_type = set_type(return_type)
        self.id = id
        self.parameters = parameters
        self.instructions = instructions


class Main:
    def __init__(self, block):
        self.return_type = TYPE.INTEGER
        self.id = 'main'
        self.parameters = None
        self.block = block


class StructDefinition:
    def __init__(self, id, declarations):
        self.id = id
        self.declarations = declarations


class StructInstance:
    def __init__(self, struct_type, identifier):
        self.struct_type = struct_type
        self.identifier = identifier


class StructAssignation:
    def __init__(self, struct_identifier, expression):
        self.struct_identifier = struct_identifier
        self.expression = expression


class Label:
    def __init__(self, id):
        self.id = id


class If:
    def __init__(self, expression, instruction):
        self.expression = expression
        self.instruction = instruction


class IfElse:
    def __init__(self, expression, instruction, else_instruction):
        self.expression = expression
        self.instruction = instruction
        self.else_instruction = else_instruction


class Switch:
    def __init__(self, expression, case_list):
        self.expression = expression
        self.case_list = case_list


class Case:
    def __init__(self, expression, instructions):
        self.expression = expression
        self.instructions = instructions


class Default:
    def __init__(self, instructions):
        self.instructions = instructions


class While:
    def __init__(self, expression, instruction):
        self.expression = expression
        self.instruction = instruction


class Do:
    def __init__(self, instruction, expression):
        self.instruction = instruction
        self.expression = expression


class For:
    def __init__(self, init_value, condition, step, instruction):
        self.init_value = init_value
        self.condition = condition
        self.step = step
        self.instruction = instruction


class Null:
    '''No hace nada pero sirve de instancia para trasladar la instruccion.'''


class Block:
    def __init__(self, instructions):
        self.instructions = instructions


class Break:
    'Sirve de instancia para trasladar la instruccion pero no guarda ningun atributo.'


class Continue:
    'Sirve de instancia para trasladar la instruccion pero no guarda ningun atributo.'


class Scan:
    'Sirve de instancia para trasladar la instruccion pero no guarda ningun atributo.'


class Return:
    def __init__(self, expression=None):
        self.expression = expression


class Print:
    def __init__(self, expressions):
        self.expressions = expressions


class Goto:
    def __init__(self, id_label):
        self.id_label = id_label


class Expression:
    '''Abstract class expression'''


class Terminal(Expression):
    def __init__(self, type, value=None):
        self.type = set_type(type)
        if not value:
            value = set_value(type)
        self.value = value


class Identifier(Terminal):
    def __init__(self, id, index_list=None):
        self.id = id
        self.index_list = index_list


class StructIdentifier(Terminal):
    def __init__(self, identifier, atribute):
        self.identifier = identifier
        self.atribute = atribute


class FunctionCall(Terminal):
    def __init__(self, id, parameters=None):
        self.id = id
        self.parameters = parameters


class Unary(Expression):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand


class Conversion(Expression):
    'Esta clase podria ser considerada expresion y heredar de Unary'

    def __init__(self, type, expression):
        self.type = type
        self.expression = expression


class Binary(Expression):
    def __init__(self, operator, operand1, operand2):
        self.operator = operator
        self.operand1 = operand1
        self.operand2 = operand2


class Ternary(Expression):
    def __init__(self, operand1, operand2, operand3):
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3


class Exit:
    'Utilizado para determinar el fin del programa para Augus'
