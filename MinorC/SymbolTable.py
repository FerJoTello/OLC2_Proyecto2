class Symbol:
    def __init__(self, type, name, terminal, node):
        self.type = type
        self.name = name
        self.terminal = terminal
        self.node = node


class Scope:
    def __init__(self, prev_scope=None):
        self.symbol_table = {}
        self.prev_scope = prev_scope

    def get(self, key):
        symbol = self.symbol_table.get(key, None)
        if not symbol:
            try:
                return self.prev_scope.get(key)
            except AttributeError:
                return None
        return symbol

    def put(self, key, value):
        self.symbol_table[key] = value


if __name__ == "__main__":
    global_symbol_table = Scope()
    global_symbol_table.put('primero', 1)
    global_symbol_table.put('segundo', 2)
    #global_symbol_table.put('primero', 'otra vez')
    actual_symbol_table = Scope(global_symbol_table)
    symbol = actual_symbol_table.get('tercero')
    print(symbol)
