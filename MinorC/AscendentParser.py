from .Instructions import *
from .ply.yacc import yacc
from .Tokens import *
from graphviz import Graph
#print('__file__={0:<35} | __name__={1:<20} | __package__={2:<20}'.format(__file__, __name__, str(__package__)))
dot = None
n = -1
ast_nodes = {}


def node_inc():
    global n
    n = n + 1
    return 'n'+str(n)


precedence = (
    ('left', 'OP_OR'),
    ('left', 'OP_AND'),
    ('left', 'OPB_OR'),
    ('left', 'OPB_XOR'),
    ('left', 'OPB_AND'),
    ('nonassoc', 'OP_COMPARISSON', 'OP_DISTINCT'),
    ('nonassoc', 'S_LESS', 'S_GREATER', 'OP_LESS_EQUAL', 'OP_GREATER_EQUAL'),
    ('left', 'OPB_L_SHIFT', 'OPB_R_SHIFT'),
    ('left', 'S_SUM', 'S_SUBS'),
    ('left', 'S_ASTERISK', 'S_SLASH', 'S_PERCENTAGE'),
    ('right', 'UMINUS', 'OP_NOT', 'OPB_NOT',
     'ADRESS_OF', 'PRE_INCREMENT', 'PRE_DECREMENT'),
    ('left', 'POST_INCREMENT', 'POST_DECREMENT'),
)


def p_init(p):
    'init               :   start'
    p[0] = get_from_node(p[1])


def p_start(p):
    'start              :   start_instructions main'
    node_index = node_inc()
    dot.node(node_index, 'start')
    start_instructions = []
    for instruction in p[1]:
        dot.edge(node_index, instruction)
        start_instructions.append(get_from_node(instruction))
    dot.edge(node_index, p[2])
    add_to_node(node_index, start_instructions + [get_from_node(p[2])])
    p[0] = node_index


def p_start_single_main(p):
    'start              :   main'
    node_index = node_inc()
    dot.node(node_index, 'start')
    dot.edge(node_index, p[1])
    add_to_node(node_index, [get_from_node(p[1])])
    p[0] = node_index


def p_main(p):
    'main               :   R_INT R_MAIN S_L_PAR S_R_PAR block'
    node_index = node_inc()
    dot.node(node_index, 'int main( )')
    dot.edge(node_index, p[5])
    block = get_from_node(p[5])
    block.instructions.append(Exit())
    new_main = Main(block)
    add_to_node(node_index, new_main)
    p[0] = node_index


def p_start_instructions(p):
    'start_instructions :   start_instructions start_instruction'
    p[0] = p[1] + [p[2]]


def p_start_instructions_first(p):
    'start_instructions :   start_instruction'
    p[0] = [p[1]]


def p_start_instruction(p):
    '''start_instruction    :   declaration
                            |   assignation
                            |   struct_definition
                            |   struct_instance
                            |   struct_assignation
                            |   function'''
    p[0] = p[1]


def p_function_params(p):
    'function           :   function_id S_L_PAR list_param S_R_PAR block'
    function_id = get_from_node(p[1])
    parameters = []
    for param in p[3]:
        dot.edge(p[1], param)
        parameters.append(get_from_node(param))
    dot.edge(p[1], p[5])
    block = get_from_node(p[5])
    new_function = Function(
        function_id[0], function_id[1], parameters, block)
    add_to_node(p[1], new_function)
    p[0] = p[1]


def p_function(p):
    'function           :   function_id S_L_PAR S_R_PAR block'
    dot.edge(p[1], p[4])
    function_id = get_from_node(p[1])
    block = get_from_node(p[4])
    new_function = Function(
        function_id[0], function_id[1], None, block)
    add_to_node(p[1], new_function)
    p[0] = p[1]


def p_list_param(p):
    'list_param         :   list_param S_COMMA parameter'
    p[0] = p[1] + [p[3]]


def p_list_param_first(p):
    'list_param         :   parameter'
    p[0] = [p[1]]


def p_parameter(p):
    'parameter          :   primitive_type ID'
    node_index = node_inc()
    dot.node(node_index, 'parameter')
    dot.edge(node_index, p[1])
    dot.edge(node_index, p.slice[2].value)
    primitive_type = get_from_node(p[1])
    new_parameter = Parameter(primitive_type, p.slice[2].value)
    add_to_node(node_index, new_parameter)
    p[0] = node_index


def p_function_id_primitive(p):
    'function_id        :   primitive_type ID'
    node_index = node_inc()
    dot.node(node_index, 'function ' + p.slice[2].value + '()')
    dot.edge(node_index, p[1])
    function_id = [get_from_node(p[1]), p.slice[2].value]
    add_to_node(node_index, function_id)
    p[0] = node_index


def p_function_id_void(p):
    'function_id        :   R_VOID ID'
    node_index = node_inc()
    dot.node(node_index, 'function ' + p.slice[2].value + '()')
    node_type_index = node_inc()
    dot.node(node_type_index, 'void')
    dot.edge(node_index, node_type_index)
    function_id = ['void', p.slice[2].value]
    add_to_node(node_index, function_id)
    p[0] = node_index


def p_primitive_type(p):
    '''primitive_type   :   R_INT
                        |   R_DOUBLE
                        |   R_FLOAT
                        |   R_CHAR'''
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    add_to_node(node_index, p.slice[1].value)
    p[0] = node_index


def p_block(p):
    'block              :   S_L_BRA list_instructions S_R_BRA'
    node_index = node_inc()
    dot.node(node_index, '{ instructions block }')
    instructions = []
    for instruction in p[2]:
        dot.edge(node_index, instruction)
        instructions.append(get_from_node(instruction))
    new_block = Block(instructions)
    add_to_node(node_index, new_block)
    p[0] = node_index


def p_list_instructions(p):
    'list_instructions  :   list_instructions instruction'
    p[0] = p[1] + [p[2]]


def p_list_instructions_first(p):
    'list_instructions  :   instruction'
    p[0] = [p[1]]


def p_instruction(p):
    '''instruction      :   declaration
                        |   struct_definition
                        |   struct_instance
                        |   struct_assignation
                        |   assignation
                        |   label
                        |   if
                        |   switch
                        |   while
                        |   do
                        |   for
                        |   block
                        |   null
                        |   goto
                        |   break
                        |   continue
                        |   return
                        |   print
                        |   scan
                        |   expression S_SEMICOLON'''
    p[0] = p[1]


def p_declaration(p):
    'declaration        :   primitive_type list_declaration S_SEMICOLON'
    declarations = []
    for declaration in p[2]:
        dot.edge(p[1], declaration)
        declarations.append(get_from_node(declaration))
    new_declaration_list = DeclarationList(declarations)
    add_to_node(p[1], new_declaration_list)
    p[0] = p[1]


def p_list_declaration_id_expression(p):
    'list_declaration   :   list_declaration S_COMMA ID S_EQUAL expression'
    node_index = node_inc()
    dot.node(node_index, '=')
    node_index_id = node_inc()
    dot.node(node_index_id, p.slice[3].value)
    dot.edge(node_index, node_index_id)
    dot.edge(node_index, p[5])
    type = get_from_node(p[-1])
    identifier = Identifier(p.slice[1].value)
    expression = get_from_node(p[3])
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    # translate_assignation(get_id(p.slice[3].value), ast_nodes.get(p[5]))
    p[0] = p[1] + [node_index]


def p_list_declaration_id(p):
    'list_declaration   :   list_declaration S_COMMA ID'
    node_index = node_inc()
    dot.node(node_index, p.slice[3].value)
    type = get_from_node(p[-1])
    identifier = Identifier(p.slice[1].value)
    expression = Terminal(type)
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    p[0] = p[1] + [node_index]


def p_list_declaration_array_declaration(p):
    'list_declaration   :   list_declaration S_COMMA array_declaration'
    p[0] = p[1] + [p[3]]


def p_list_declaration_id_expression_first(p):
    'list_declaration   :   ID S_EQUAL expression'
    node_index = node_inc()
    dot.node(node_index, '=')
    node_index_id = node_inc()
    dot.node(node_index_id, p.slice[1].value)
    dot.edge(node_index, node_index_id)
    dot.edge(node_index, p[3])
    type = get_from_node(p[-1])
    identifier = Identifier(p.slice[1].value)
    expression = get_from_node(p[3])
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    # translate_assignation(get_id(p.slice[1].value), ast_nodes.get(p[3]))
    p[0] = [node_index]


def p_list_declaration_id_first(p):
    'list_declaration   :   ID'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    # translate_assignation(get_id(p.slice[1].value), '0')
    type = get_from_node(p[-1])
    identifier = Identifier(p.slice[1].value)
    expression = Terminal(type)
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    p[0] = [node_index]


def p_list_declaration_array_declaration_first(p):
    'list_declaration   :   array_declaration'
    p[0] = [p[1]]


def p_array_declaration_expression(p):
    'array_declaration  :   ID S_L_SQR_BRA expression S_R_SQR_BRA S_EQUAL array_expression'
    node_index = node_inc()
    dot.node(node_index, '=')
    node_index_id = node_inc()
    dot.node(node_index_id, p.slice[1].value + '[ ]')
    dot.edge(node_index_id, p[3])
    dot.edge(node_index, node_index_id)
    dot.edge(node_index, p[6])
    type = get_from_node(p[-1])
    identifier = Identifier(
        p.slice[1].value, [get_from_node(p[3])])
    expression = get_from_node(p[6])
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    p[0] = node_index


def p_array_declaration_empty_expression(p):
    'array_declaration  :   ID S_L_SQR_BRA S_R_SQR_BRA S_EQUAL array_expression'
    node_index = node_inc()
    dot.node(node_index, '=')
    node_index_id = node_inc()
    dot.node(node_index_id, p.slice[1].value + '[ ]')
    dot.edge(node_index, node_index_id)
    dot.edge(node_index, p[5])
    type = get_from_node(p[-1])
    identifier = Identifier(p.slice[1].value, [])
    expression = get_from_node(p[5])
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    p[0] = node_index


def p_array_declaration_empty(p):
    'array_declaration  :   ID S_L_SQR_BRA S_R_SQR_BRA'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value + '[ ]')
    type = get_from_node(p[-1])
    identifier = Identifier(p.slice[1].value, [])
    expression = Terminal(type, 'array()')
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    p[0] = node_index


def p_array_declaration_id_brackets(p):
    'array_declaration  :   ID brackets'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value + '[ ]' * len(p[2]))
    index_list = []
    for node_bracket in p[2]:
        dot.edge(node_index, node_bracket)
        index_list.append(get_from_node(node_bracket))
    type = get_from_node(p[-1])
    identifier = Identifier(p.slice[1].value, index_list)
    expression = Terminal(type)
    new_declaration = Declaration(type, identifier, expression)
    add_to_node(node_index, new_declaration)
    p[0] = node_index


def p_array_expression_list(p):
    'array_expression   :   S_L_BRA list_expressions S_R_BRA'
    node_index = node_inc()
    dot.node(node_index, '{ }')
    list_expressions = []
    for expression in p[2]:
        dot.edge(node_index, expression)
        list_expressions.append(get_from_node(expression))
    add_to_node(node_index, list_expressions)
    p[0] = node_index


def p_array_expression_string(p):
    'array_expression   :   STRING'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    expression = Terminal(p.slice[1].type, p.slice[1].value)
    add_to_node(node_index, expression)
    p[0] = node_index


def p_struct_definition(p):
    'struct_definition  :   struct_type S_L_BRA list_struct_decla S_R_BRA S_SEMICOLON'
    declarations = []
    for element in p[3]:
        dot.edge(p[1], element)
        declarations.append(get_from_node(element))
    id = get_from_node(p[1])
    new_struct_definition = StructDefinition(id, declarations)
    add_to_node(p[1], new_struct_definition)
    p[0] = p[1]


def p_list_struct_decla(p):
    'list_struct_decla  :   list_struct_decla declaration'
    p[0] = p[1] + [p[2]]


def p_list_struct_decla_first(p):
    'list_struct_decla  :   declaration'
    p[0] = [p[1]]


def p_struct_instance(p):
    'struct_instance    :   struct_type identifier S_SEMICOLON'
    struct_type = get_from_node(p[1])
    identifier = get_from_node(p[2])
    if not identifier.index_list:
        identifier.index_list = []
    new_struct_instance = StructInstance(struct_type, identifier)
    add_to_node(p[1], new_struct_instance)
    dot.edge(p[1], p[2])
    p[0] = p[1]


def p_struct_assignation(p):
    'struct_assignation :   struct_identifier S_EQUAL expression S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, '=')
    dot.edge(node_index, p[1])
    dot.edge(node_index, p[3])
    expression = get_from_node(p[3])
    struct_identifier = get_from_node(p[1])
    new_struct_assignation = StructAssignation(struct_identifier, expression)
    add_to_node(node_index, new_struct_assignation)
    p[0] = node_index


def p_struct_identifier(p):
    'struct_identifier  :   identifier S_PERIOD identifier'
    node_index = node_inc()
    dot.node(node_index, '.')
    dot.edge(node_index, p[1])
    dot.edge(node_index, p[3])
    identifier = get_from_node(p[1])
    atribute = get_from_node(p[3])
    new_struct_identifier = StructIdentifier(identifier, atribute)
    add_to_node(node_index, new_struct_identifier)
    p[0] = node_index


def p_struct_type(p):
    'struct_type        :   R_STRUCT ID'
    node_index = node_inc()
    dot.node(node_index, 'struct ' + p.slice[2].value)
    add_to_node(node_index, p.slice[2].value)
    p[0] = node_index


def p_identifier_array(p):
    'identifier         :   ID brackets'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value + '[ ]' * len(p[2]))
    # temp = get_id(p.slice[1].value)
    index_list = []
    for node_bracket in p[2]:
        dot.edge(node_index, node_bracket)
        index_list.append(get_from_node(node_bracket))
    # ast_nodes.put(node_index, temp + index)
    # new_node = new_Leaf('IDENTIFIER', p.slice[1].value)
    # gda_nodes[node_index] = new_node
    new_identifier = Identifier(p.slice[1].value, index_list)
    add_to_node(node_index, new_identifier)
    p[0] = node_index


def p_identifier(p):
    'identifier         :   ID'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    # crea una variable temporal para el id (si es que no habia sido creada y se agrega a la 'tabla de simbolos')
    # temp = get_id(p.slice[1].value)
    # new_node = new_Leaf('IDENTIFIER', p.slice[1].value)
    # gda_nodes[node_index] = new_node
    new_identifier = Identifier(p.slice[1].value)
    add_to_node(node_index, new_identifier)
    p[0] = node_index


def p_assignation(p):
    'assignation      :   identifier S_EQUAL expression S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, p.slice[2].value)
    dot.edge(node_index, p[1])
    dot.edge(node_index, p[3])
    identifier = get_from_node(p[1])
    expression = get_from_node(p[3])
    new_assignation = Assignation(identifier, expression)
    add_to_node(node_index, new_assignation)
    p[0] = node_index


def p_op_assignation(p):
    '''assignation      :   identifier OP_ASSIGN_SUM expression S_SEMICOLON
                        |   identifier OP_ASSIGN_SUBS expression S_SEMICOLON
                        |   identifier OP_ASSIGN_MULT expression S_SEMICOLON
                        |   identifier OP_ASSIGN_DIV expression S_SEMICOLON
                        |   identifier OP_ASSIGN_MOD expression S_SEMICOLON
                        |   identifier OP_ASSIGN_AND expression S_SEMICOLON
                        |   identifier OP_ASSIGN_XOR expression S_SEMICOLON
                        |   identifier OP_ASSIGN_OR expression S_SEMICOLON'''
    node_index = node_inc()
    dot.node(node_index, p.slice[2].value)
    dot.edge(node_index, p[1])
    dot.edge(node_index, p[3])
    identifier = get_from_node(p[1])
    expression = get_from_node(p[3])
    operation = Binary(p.slice[2].value, identifier, expression)
    new_assignation = Assignation(identifier, operation)
    add_to_node(node_index, new_assignation)
    p[0] = node_index


def p_op_shift_assignation(p):
    '''assignation      :   identifier OP_ASSIGN_L_SHIFT expression S_SEMICOLON
                        |   identifier OP_ASSIGN_R_SHIFT expression S_SEMICOLON'''
    node_index = node_inc()
    dot.node(node_index, p.slice[2].value)
    dot.edge(node_index, p[1])
    dot.edge(node_index, p[3])
    identifier = get_from_node(p[1])
    expression = get_from_node(p[3])
    operation = Binary(
        p.slice[2].value[:2], identifier, expression)
    new_assignation = Assignation(identifier, operation)
    add_to_node(node_index, new_assignation)
    p[0] = node_index


def p_brackets_list(p):
    'brackets           :   brackets S_L_SQR_BRA expression S_R_SQR_BRA'
    p[0] = p[1] + [p[3]]


def p_brackets_first(p):
    'brackets           :   S_L_SQR_BRA expression S_R_SQR_BRA'
    p[0] = [p[2]]


def p_label(p):
    'label              :   ID S_COLON'
    node_index = node_inc()
    dot.node(node_index, 'label')
    node_index_id = node_inc()
    dot.node(node_index_id, p.slice[1].value)
    dot.edge(node_index, node_index_id)
    new_label = Label(p.slice[1].value)
    add_to_node(node_index, new_label)
    p[0] = node_index


def p_if(p):
    'if                 :   R_IF S_L_PAR expression S_R_PAR instruction'
    node_index = node_inc()
    dot.node(node_index, 'if')
    dot.edge(node_index, p[3])
    dot.edge(node_index, p[5])
    expression = get_from_node(p[3])
    instruction = get_from_node(p[5])
    new_if = If(expression, instruction)
    add_to_node(node_index, new_if)
    p[0] = node_index


def p_if_else(p):
    'if                 :   R_IF S_L_PAR expression S_R_PAR instruction R_ELSE instruction'
    node_index = node_inc()
    dot.node(node_index, 'if')
    dot.edge(node_index, p[3])
    dot.edge(node_index, p[5])
    node_index_else = node_inc()
    dot.edge(node_index, node_index_else)
    dot.node(node_index_else, 'else')
    dot.edge(node_index_else, p[7])
    expression = get_from_node(p[3])
    if_instruction = get_from_node(p[5])
    else_instruction = get_from_node(p[7])
    new_if_else = IfElse(
        expression, if_instruction, else_instruction)
    add_to_node(node_index, new_if_else)
    p[0] = node_index


def p_switch(p):
    'switch             :   R_SWITCH S_L_PAR expression S_R_PAR S_L_BRA final_case_list S_R_BRA'
    node_index = node_inc()
    dot.node(node_index, 'switch')
    dot.edge(node_index, p[3])
    node_case_index = node_inc()
    dot.node(node_case_index, 'case list')
    case_list = []
    for case in p[6]:
        dot.edge(node_case_index, case)
        case_list.append(get_from_node(case))
    dot.edge(node_index, node_case_index)
    expression = get_from_node(p[3])
    new_switch = Switch(expression, case_list)
    add_to_node(node_index, new_switch)
    p[0] = node_index


def p_final_case_list_default(p):
    'final_case_list    :   case_list default'
    p[0] = p[1] + [p[2]]


def p_final_case_list(p):
    'final_case_list    :   case_list'
    p[0] = p[1]


def p_case_list(p):
    'case_list          :   case_list case'
    p[0] = p[1] + [p[2]]


def p_case_list_first(p):
    'case_list          :   case'
    p[0] = [p[1]]


def p_case(p):
    'case               :   R_CASE expression S_COLON list_instructions'
    node_index = node_inc()
    dot.node(node_index, 'case')
    dot.edge(node_index, p[2])
    node_instructions_index = node_inc()
    dot.node(node_instructions_index, 'instructions list')
    instructions = []
    for instruction in p[4]:
        dot.edge(node_instructions_index, instruction)
        instructions.append(get_from_node(instruction))
    dot.edge(node_index, node_instructions_index)
    expression = get_from_node(p[2])
    new_case = Case(expression, instructions)
    add_to_node(node_index, new_case)
    p[0] = node_index


def p_default(p):
    'default            :   R_DEFAULT S_COLON list_instructions'
    node_index = node_inc()
    dot.node(node_index, 'default')
    node_instructions_index = node_inc()
    dot.node(node_instructions_index, 'instructions list')
    instructions = []
    for instruction in p[3]:
        dot.edge(node_instructions_index, instruction)
        instructions.append(get_from_node(instruction))
    dot.edge(node_index, node_instructions_index)
    new_default = Default(instructions)
    add_to_node(node_index, new_default)
    p[0] = node_index


def p_while(p):
    'while              :   R_WHILE S_L_PAR expression S_R_PAR instruction'
    node_index = node_inc()
    dot.node(node_index, 'while')
    dot.edge(node_index, p[3])
    dot.edge(node_index, p[5])
    expression = get_from_node(p[3])
    instruction = get_from_node(p[5])
    new_while = While(expression, instruction)
    add_to_node(node_index, new_while)
    p[0] = node_index


def p_do(p):
    'do                 :   R_DO instruction R_WHILE S_L_PAR expression S_R_PAR S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'do')
    dot.edge(node_index, p[2])
    node_while_index = node_inc()
    dot.node(node_while_index, 'while')
    dot.edge(node_while_index, p[5])
    dot.edge(node_index, node_while_index)
    instruction = get_from_node(p[2])
    expression = get_from_node(p[5])
    new_do = Do(instruction, expression)
    add_to_node(node_index, new_do)
    p[0] = node_index


def p_for_assignation(p):
    'for                :   R_FOR S_L_PAR assignation expression S_SEMICOLON step S_R_PAR instruction'
    node_index = node_inc()
    dot.node(node_index, 'for')
    dot.edge(node_index, p[3])
    dot.edge(node_index, p[4])
    dot.edge(node_index, p[6])
    dot.edge(node_index, p[8])
    init_value = get_from_node(p[3])
    condition = get_from_node(p[4])
    step = get_from_node(p[6])
    instruction = get_from_node(p[8])
    new_for = For(init_value, condition, step, instruction)
    add_to_node(node_index, new_for)
    p[0] = node_index


def p_for_declaration(p):
    'for                :   R_FOR S_L_PAR declaration expression S_SEMICOLON step S_R_PAR instruction'
    node_index = node_inc()
    dot.node(node_index, 'for')
    dot.edge(node_index, p[3])
    dot.edge(node_index, p[4])
    dot.edge(node_index, p[6])
    dot.edge(node_index, p[8])
    init_value = get_from_node(p[3])
    condition = get_from_node(p[4])
    step = get_from_node(p[6])
    instruction = get_from_node(p[8])
    new_for = For(init_value, condition, step, instruction)
    add_to_node(node_index, new_for)
    p[0] = node_index


def p_step(p):
    '''step             :   assignation
                        |   inc
                        |   dec'''
    p[0] = p[1]


def p_null(p):
    'null               :   S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, ';')
    new_null = Null()
    add_to_node(node_index, new_null)
    p[0] = node_index


def p_goto(p):
    'goto               :   R_GOTO ID S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'goto')
    node_index_id = node_inc()
    dot.node(node_index_id, p.slice[2].value)
    dot.edge(node_index, node_index_id)
    new_goto = Goto(p.slice[2].value)
    add_to_node(node_index, new_goto)
    p[0] = node_index


def p_break(p):
    'break              :   R_BREAK S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'break')
    p[0] = node_index


def p_continue(p):
    'continue           :   R_CONTINUE S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'continue')
    p[0] = node_index


def p_return_empty(p):
    'return             :   R_RETURN S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'return')
    p[0] = node_index


def p_return_expression(p):
    'return             :   R_RETURN expression S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'return')
    dot.edge(node_index, p[2])
    p[0] = node_index


def p_print(p):
    'print              :   R_PRINTF S_L_PAR list_expressions S_R_PAR S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'printf( )')
    for expression in p[3]:
        dot.edge(node_index, expression)
    p[0] = node_index


def p_scan(p):
    'scan               :   R_SCANF S_L_PAR S_R_PAR S_SEMICOLON'
    node_index = node_inc()
    dot.node(node_index, 'scanf( )')
    new_scan = Scan()
    add_to_node(node_index, new_scan)
    p[0] = node_index


def p_expression(p):
    '''expression       :   terminal
                        |   unary
                        |   binary
                        |   ternary'''
    p[0] = p[1]


def p_terminal_primitive(p):
    '''terminal         :   INTEGER
                        |   DECIMAL
                        |   CHARACTER
                        |   STRING'''
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    # terminal = new_Leaf(p.slice[1].type, p.slice[1].value)
    new_terminal = Terminal(p.slice[1].type, p.slice[1].value)
    add_to_node(node_index, new_terminal)
    p[0] = node_index


def p_terminal_expression(p):
    'terminal           :   S_L_PAR expression S_R_PAR'
    p[0] = p[2]


def p_terminal_function_identifier(p):
    '''terminal         :   function_call
                        |   identifier'''
    p[0] = p[1]


def p_terminal_struct_identifier(p):
    'terminal           :   struct_identifier'
    p[0] = p[1]


def p_binary(p):
    '''binary           :   expression S_SUM expression
                        |   expression S_SUBS expression
                        |   expression S_ASTERISK expression
                        |   expression S_SLASH expression
                        |   expression S_PERCENTAGE expression
                        |   expression OP_AND expression
                        |   expression OP_OR expression
                        |   expression OP_COMPARISSON expression
                        |   expression OP_DISTINCT expression
                        |   expression OP_LESS_EQUAL expression
                        |   expression OP_GREATER_EQUAL expression
                        |   expression S_LESS expression
                        |   expression S_GREATER expression
                        |   expression S_AMPERSAND expression %prec OPB_AND
                        |   expression OPB_OR expression
                        |   expression OPB_XOR expression
                        |   expression OPB_L_SHIFT expression
                        |   expression OPB_R_SHIFT expression'''
    node_index = node_inc()
    dot.node(node_index, p.slice[2].value)
    dot.edge(node_index, p[1])
    dot.edge(node_index, p[3])
    # new_node = new_binary_Node(p.slice[2], gda_nodes.get(p[1]), gda_nodes.get(p[3]))
    # gda_nodes[node_index] = new_node
    operand1 = get_from_node(p[1])
    operand2 = get_from_node(p[3])
    new_binary = Binary(p.slice[2].value, operand1, operand2)
    add_to_node(node_index, new_binary)
    p[0] = node_index


def p_unary(p):
    '''unary            :   S_SUBS expression %prec UMINUS
                        |   OP_NOT expression
                        |   OPB_NOT expression
                        |   S_AMPERSAND expression %prec ADRESS_OF'''
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    dot.edge(node_index, p[2])
    expression = get_from_node(p[2])
    new_unary = Unary(p.slice[1].value, expression)
    add_to_node(node_index, new_unary)
    p[0] = node_index


def p_unary_prod(p):
    '''unary            :   inc
                        |   dec
                        |   conversion'''
    p[0] = p[1]


def p_inc(p):
    '''inc              :   pre_inc
                        |   post_inc'''
    p[0] = p[1]


def p_post_inc(p):
    'post_inc           :   terminal OP_INCREASE %prec POST_INCREMENT'
    node_index = node_inc()
    dot.node(node_index, p.slice[2].value)
    dot.edge(node_index, p[1])
    operand1 = get_from_node(p[1])
    operand2 = Terminal('INTEGER', '1')
    new_binary = Binary('+', operand1, operand2)
    add_to_node(node_index, new_binary)
    p[0] = node_index


def p_pre_inc(p):
    'pre_inc            :   OP_INCREASE terminal %prec PRE_INCREMENT'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    dot.edge(node_index, p[2])
    operand1 = Terminal('INTEGER', '1')
    operand2 = get_from_node(p[2])
    new_binary = Binary('+', operand1, operand2)
    add_to_node(node_index, new_binary)
    p[0] = node_index


def p_dec(p):
    '''dec              :   pre_dec
                        |   post_dec'''
    p[0] = p[1]


def p_post_dec(p):
    'post_dec           :   terminal OP_DECREASE %prec POST_DECREMENT'
    node_index = node_inc()
    dot.node(node_index, p.slice[2].value)
    dot.edge(node_index, p[1])
    operand1 = get_from_node(p[1])
    operand2 = Terminal('INTEGER', '1')
    new_binary = Binary('-', operand1, operand2)
    add_to_node(node_index, new_binary)
    p[0] = node_index


def p_pre_dec(p):
    'pre_dec            :   OP_DECREASE terminal %prec PRE_DECREMENT'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value)
    dot.edge(node_index, p[2])
    operand1 = Terminal('INTEGER', '1')
    operand2 = get_from_node(p[2])
    new_binary = Binary('-', operand1, operand2)
    add_to_node(node_index, new_binary)
    p[0] = node_index


def p_ternary(p):
    'ternary            :   expression OP_TERNARY expression S_COLON expression'
    node_ternary_index = node_inc()
    dot.node(node_ternary_index, p.slice[2].value)
    dot.edge(node_ternary_index, p[1])
    dot.edge(node_ternary_index, p[3])
    node_else_index = node_inc()
    dot.node(node_else_index, p.slice[4].value)
    dot.edge(node_else_index, p[5])
    dot.edge(node_ternary_index, node_else_index)
    operand1 = get_from_node(p[1])
    operand2 = get_from_node(p[3])
    operand3 = get_from_node(p[5])
    new_ternary = Ternary(operand1, operand2, operand3)
    add_to_node(node_ternary_index, new_ternary)
    p[0] = node_ternary_index


def p_function_call_empty(p):
    'function_call      :   ID S_L_PAR S_R_PAR'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value + '( )')
    new_function_call = FunctionCall(p.slice[1].value)
    add_to_node(node_index, new_function_call)
    p[0] = node_index


def p_function_call_expressions(p):
    'function_call      :   ID S_L_PAR list_expressions S_R_PAR'
    node_index = node_inc()
    dot.node(node_index, p.slice[1].value + '( )')
    parameters = []
    for expression in p[3]:
        dot.edge(node_index, expression)
        parameters.append(get_from_node(expression))
    new_function_call = FunctionCall(p.slice[1].value, parameters)
    add_to_node(node_index, new_function_call)
    p[0] = node_index


def p_function_call_sizeof(p):
    'function_call      :   R_SIZEOF S_L_PAR expression S_R_PAR'
    node_index = node_inc()
    dot.node(node_index, 'sizeof( )')
    dot.edge(node_index, p[3])
    parameter = [get_from_node(p[3])]
    new_function_call = FunctionCall(p.slice[1].value, parameter)
    add_to_node(node_index, new_function_call)
    p[0] = node_index


def p_list_expressions(p):
    'list_expressions   :   list_expressions S_COMMA expression'
    p[0] = p[1] + [p[3]]


def p_list_expressions_first(p):
    'list_expressions   :   expression'
    p[0] = [p[1]]


def p_conversion(p):
    '''conversion       :   S_L_PAR R_INT S_R_PAR expression
                        |   S_L_PAR R_FLOAT S_R_PAR expression
                        |   S_L_PAR R_CHAR S_R_PAR expression'''
    node_index = node_inc()
    dot.node(node_index, '(' + p.slice[2].value + ')')
    dot.edge(node_index, p[4])
    expression = get_from_node(p[4])
    new_conversion = Conversion(p.slice[2].value, expression)
    add_to_node(node_index, new_conversion)
    p[0] = node_index


def p_error(p):
    try:
        print('Error sintactico')
        print(p)
        newError = "<tr><td><center>Sintáctico</center></td>\n"
        newError = newError + "<td><center>No se esperaba '"+p.value+"'.</center></td>\n"
        newError = newError + "<td><center>" + \
            str(p.lineno) + "</center></td>\n"
        newError = newError + "</tr>\n"
        # reported_errors.append(newError)
    except AttributeError:
        print('end of file')


def reset_dot():
    global dot
    dot = Graph('AST')
    dot.filename = 'AST'
    dot.format = 'png'


def add_to_node(key, value):
    global ast_nodes
    ast_nodes[key] = value


def get_from_node(key):
    global ast_nodes
    return ast_nodes.get(key, None)


def reset_ast_nodes():
    global ast_nodes
    ast_nodes = {}


def parse(input):
    reset_dot()
    reset_ast_nodes()
    print('Valor ingresado:')
    print(input)
    instructions = yacc().parse(input)
    # dot.view()
    return instructions


if __name__ == "__main__":
    parse("1+2!=3+4 || 3==3")
