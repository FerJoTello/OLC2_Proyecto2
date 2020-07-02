#print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__, __name__, str(__package__)))
from .SymbolTable import Scope
from .Instructions import *
actual_scope = Scope()
translation = ''
temp_count = -1
labels = {}
actual_label = ''
if_count = -1
for_count = -1


def translate_instruction(instruction):
    global actual_scope
    if isinstance(instruction, list):
        for instr in instruction:
            translate_instruction(instr)
    else:
        if isinstance(instruction, Block):
            saved_scope = actual_scope
            translate_instruction(instruction.instructions)
            actual_scope = saved_scope
        elif isinstance(instruction, Main):
            saved_scope = actual_scope  # deberia ser el ambito global
            translate_main(instruction)
            actual_scope = saved_scope
        elif isinstance(instruction, Function):
            saved_scope = actual_scope  # deberia ser el ambito global
            translate_function(instruction)
            actual_scope = saved_scope
        elif isinstance(instruction, Declaration):
            translate_declaration(instruction)
        elif isinstance(instruction, Assignation):
            translate_assignation(instruction)
        elif isinstance(instruction, Print):
            translate_print(instruction)
        elif isinstance(instruction, If):
            translate_if(instruction)
        elif isinstance(instruction, IfElse):
            translate_if_else(instruction)
        elif isinstance(instruction, For):
            translate_for(instruction)
        elif isinstance(instruction, FunctionCall):
            solve_function_call(instruction)
        elif isinstance(instruction, DeclarationList):
            translate_instruction(instruction.declarations)
        elif isinstance(instruction, StructAssignation):
            translate_struct_assignation(instruction)
        elif isinstance(instruction, StructInstance):
            translate_struct_instance(instruction)
        elif isinstance(instruction, StructDefinition):
            translate_struct_definition(instruction)
        elif isinstance(instruction, Label):
            translate_label(instruction)
        elif isinstance(instruction, Goto):
            translate_goto(instruction)
        elif isinstance(instruction, Expression):
            translate_expression(instruction)
        elif isinstance(instruction, Exit):
            append_to_label('exit;')


def translate_for(_for: For):
    # init_value puede ser una instruccion de asignacion o de declaracion, por lo que se traduce aparte
    translate_instruction(_for.init_value)
    # for_label es el que contiene las instrucciones que ejecutara el ciclo for
    for_label = inc_for()
    # continue_for_label es el que contiene el resto de instrucciones (las que se encuentran despues del bloque for)
    continue_for_label = 'c_' + for_label
    # se inicializa el nuevo label (for_label)
    init_label(for_label)
    # se agregan las instrucciones que el for debe de realizar
    # entre ellas esta la verificacion de la condicion
    condition = translate_expression(_for.condition)
    # se utiliza backpatch, por lo que al no cumplir la condicion se ejecutaria las instrucciones que el for debe de realizar
    append_to_label('if (!' + condition + ') goto ' +
                    continue_for_label + ';\n')
    # se traducen las instrucciones del bloque for
    translate_instruction(_for.instruction)
    # se traduce el 'step' del for. es una asignacion
    translate_assignation(_for.step)
    # finalmente se agrega el salto hacia el inicio de la etiqueta for_label para que vuelva a iterar
    append_to_label('goto ' + for_label + ';\n')
    # se inicializa continue_for_label como nuevo label y a el se le agregan las instrucciones pendientes. son las instrucciones fuera del for.
    init_label(continue_for_label)


def translate_print(print: Print):
    try:
        # es una cadena con mas atributos
        if len(print.expressions) > 1:
            import re
            # first deberia de contener la expresion principal del print por lo que es procesada para obtener un print
            first: str = translate_expression(print.expressions[0])[1:-1]
            pattern = r"%."
            # se obtienen los valores del string
            values = re.split(pattern, first)
            # en caso de tener mas parametros se debe de concatenar los valores
            i = 0
            for expression in print.expressions[1:]:
                expr = translate_expression(expression)
                # se concatena la cadena ingresada...
                append_to_label('print("' + values[i] + '");\n')
                # ...con su expresion
                append_to_label('print(' + expr + ');\n')
                i = i+1
            # si aun queda un ultimo valor que imprimir...
            if i == len(values)-1 and len(values[i]) > 0:
                # ... se concatena el ultimo valor
                append_to_label('print("' + values[i] + '");\n')
        else:
            # solo deberia de ser una expresion por lo que se imprime sin agregar nada mas
            first = translate_expression(print.expressions[0])
            append_to_label('print(' + first + ');\n')
    except Exception as e:
        print("Error en print :c\n")
        print(e)


def translate_if_else(if_else: IfElse):
    expression = translate_expression(if_else.expression)
    # else_label es el que contiene las instrucciones que debe de realizar si NO se cumple la expresion (es el else)
    else_label = inc_if()
    # al label que debe de contener el if se le agrega un salto condicional
    # teniendo asi que si no se cumple la expresion original hace el salto a las instrucciones del else
    # (se utiliza backpatch)
    append_to_label('if (!' + expression + ') goto ' + else_label + ';\n')
    # se traducen las instrucciones del if
    translate_instruction(if_else.instruction)
    # if_label_continuation es el que contiene las instrucciones siguientes a todo el bloque if-else
    if_label_continuation = inc_if()
    # al label que debe de contener el if y las instrucciones que realiza si es verdadero se le debe de agregar tambien
    # el salto hacia la etiqueta que contiene las instrucciones restantes fuera del bloque if-else
    append_to_label('goto ' + if_label_continuation + ';\n')
    # se inicializa un nuevo label y se asigna como el label actual al label que simula el else
    init_label(else_label)
    # se traducen las instrucciones del else en su respectiva etiqueta (else_label)
    translate_instruction(if_else.else_instruction)
    # al label que simula el else se le agrega el salto
    append_to_label('goto ' + if_label_continuation + ';\n')
    # por ultimo se inicializa un nuevo label y se asigna como el label actual al label que contiene
    # las instrucciones pendientes
    init_label(if_label_continuation)


def translate_if(_if: If):
    expression = translate_expression(_if.expression)
    # if_label es el que contiene las instrucciones que se encuentran despues del if (NO entra al if)
    if_label = inc_if()
    # al label que debe de contener el if se le agrega un salto condicional
    # teniendo asi que si no se cumple la expresion original hace el salto a las instrucciones siguientes
    # (se utiliza backpatch)
    append_to_label('if (!' + expression + ') goto ' + if_label + ';\n')
    # se traducen las instrucciones del if
    translate_instruction(_if.instruction)
    # se inicializa un nuevo label y se asigna como el label actual a la continuacion del if
    init_label(if_label)


def init_label(label_name):
    '''Inicializa un nuevo label y se asigna como label actual'''
    global actual_label, labels
    labels[label_name] = label_name + ':\n'
    # se asigna como el label actual a la continuacion del if
    actual_label = label_name


def translate_goto(goto: Goto):
    append_to_label('goto ' + goto.id_label + ';\n')


def translate_label(label: Label):
    global actual_label, labels
    id = label.id
    labels[id] = id + ':\n'
    actual_label = id


def translate_struct_assignation(struct_assignation: StructAssignation):
    '''En Minor C, los structs y sus asignaciones constan de un acceso a sus atributos.
    En Augus, los structs son representados por medio de arreglos teniendo cada nombre del
    atributo al cual se está accediendo/definiendo como un índice de dicho arreglo.'''
    id = solve_struct_identifier(struct_assignation.struct_identifier)
    expression = translate_expression(struct_assignation.expression)
    append_to_label(id + ' = ' + expression + ';\n')


def translate_struct_instance(struct_instance: StructInstance):
    'Instancia un nuevo identificador para el struct.'
    get_id(struct_instance.identifier)


def translate_struct_definition(struct_definition: StructDefinition):
    'Sirve únicamente como validación semántica'


def translate_assignation(assignation: Assignation):
    expression = translate_expression(assignation.expression)
    id = solve_identifier(assignation.identifier)
    append_to_label(id + ' = ' + expression + ';\n')
    return id


def solve_identifier(identifier: Identifier):
    id = get_id(identifier)
    if identifier.index_list:
        for expression in identifier.index_list:
            solved_expression = translate_expression(expression)
            id = id + '[' + solved_expression + ']'
    return id


def solve_struct_identifier(struct_identifier: StructIdentifier):
    identifier = solve_identifier(struct_identifier.identifier)
    atribute: Identifier = struct_identifier.atribute
    identifier = identifier + "['" + atribute.id + "']"
    if atribute.index_list:
        for index_expression in atribute.index_list:
            index = translate_expression(index_expression)
            identifier = identifier + "[" + index + "]"
    return identifier


def translate_declaration(declaration: Declaration):
    if isinstance(declaration.expression, list):
        temp = get_id(declaration.identifier)
        i = 0
        for expression in declaration.expression:
            solved_expression = translate_expression(expression)
            name = temp + '[' + str(i) + ']'
            append_to_label(name + ' = ' + solved_expression + ';\n')
            i = i+1
    else:
        expression = translate_expression(declaration.expression)
        temp = get_id(declaration.identifier)
        append_to_label(temp + ' = ' + expression + ';\n')


def translate_main(main: Main):
    global actual_scope
    # el label 'main' de Augus se le concatena un salto hacia 'int_main' el cual representa a la funcion main() de MinorC
    append_to_label('goto int_main;\n', 'main')
    # se agrega a la tabla de simbolos actual
    actual_scope.put('main', 'int_main')
    # se inicializa el nuevo label
    init_label('int_main')
    # traduce sus instrucciones (es un Block)
    translate_instruction(main.block)


def translate_function(function: Function):
    global actual_scope
    # el label representa a la funcion indicando su tipo e identificador
    label = str(function.return_type.name) + '_' + function.id
    # se agrega a la tabla de simbolos actual
    actual_scope.put(function.id, label)
    # se inicializa el nuevo label
    init_label(label)
    # se traducen sus instrucciones
    translate_instruction(function.instructions)
    # se le agrega un salto para indicar el regreso de la llamada
    append_to_label('goto return_' + label + ';\n')


def translate_expression(expression):
    if isinstance(expression, Terminal):
        if isinstance(expression, Identifier):
            return solve_identifier(expression)
        elif isinstance(expression, StructIdentifier):
            return solve_struct_identifier(expression)
        elif isinstance(expression, FunctionCall):
            return solve_function_call(expression)
        return expression.value
    elif isinstance(expression, Binary):
        temporal = inc_temp()
        # $t0 = 1 + 1;
        op1 = translate_expression(expression.operand1)
        op2 = translate_expression(expression.operand2)
        append_to_label(temporal + ' = ' + op1 +
                        ' ' + expression.operator + ' ' + op2 + ';\n')
        return temporal
    elif isinstance(expression, Unary):
        temporal = inc_temp()
        # $t0 = -1;
        operand = translate_expression(expression.operand)
        append_to_label(
            temporal + ' = ' + expression.operator + ' ' + operand + ';\n')
        return temporal
    elif isinstance(expression, Conversion):
        temporal = inc_temp()
        # $t0 = (int) 'operand';
        expression = translate_expression(expression.expression)
        append_to_label(
            temporal + ' = (' + type + ') ' + expression + ';\n')
        return temporal
    elif isinstance(expression, str):
        append_to_label(temporal + ' = ' + expression + ';\n')
        return temporal
    elif isinstance(expression, Ternary):
        'Todavia no se :p'


def solve_function_call(function_call: FunctionCall):
    global actual_scope
    # de la tabla de simbolos se busca el label que representa a la funcion por medio de su id
    label = actual_scope.get(function_call.id)
    # se agrega un salto hacia el label de la funcion
    append_to_label('goto ' + label + ';\n')
    # inicializa un nuevo label que representa al retorno de la funcion.
    # ejecutara las instrucciones restantes. las que se encuentran despues de la llamada
    init_label('return_' + label)


def get_id(identifier: Identifier):
    '''Revisa en la tabla de simbolos si existe una variable con ese id.
    Si no, la crea y devuelve el temporal que funciona como identificador'''
    global actual_scope
    id = identifier.id
    temporal = actual_scope.get(id)
    if not temporal:
        if not identifier.index_list:
            temporal = inc_temp()
            actual_scope.put(id, temporal)
        else:
            temporal = inc_temp()
            actual_scope.put(id, temporal)
            append_to_label(temporal + ' = array();\n')
    return temporal


def reset_translation():
    global actual_scope, translation, temp_count, if_count, labels, actual_label
    # Almacena los nombres de las variables de MinorC y los relaciona con las variables temporales de Augus
    actual_scope = Scope()
    translation = ''
    temp_count = -1
    if_count = -1
    labels = {}
    actual_label = 'main'
    labels['main'] = 'main:\n'


def get_translation():
    global translation, labels
    for key in labels:
        label = labels.get(key)
        translation = translation + label
    return translation


def append_to_label(new_instr, label=None):
    global labels, actual_label
    if not label:
        label = actual_label
    instructions = labels.get(label)
    instructions = instructions + new_instr
    labels[label] = instructions


def inc_for():
    global for_count
    for_count = for_count + 1
    return 'for_' + str(for_count)


def inc_if():
    global if_count
    if_count = if_count + 1
    return 'if_' + str(if_count)


def inc_temp():
    global temp_count
    temp_count = temp_count + 1
    return '$t' + str(temp_count)


def start_translation(instructions):
    reset_translation()
    print('Inicia traduccion:')
    translate_instruction(instructions)
    return get_translation()


if __name__ == "__main__":
    print('xd')
