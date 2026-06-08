# Panagiotis Christodoulou
# AM: 5501
# Username: cs225501

import sys

#token typese
TK_ID      = 'ID'     # anagnoristika
TK_INTEGER = 'INTEGER'  # integer numbers
TK_EOF     = 'EOF'   # telos arxeiou

KEYWORDS = {                    # dict gia grigoro elenxo
    'program': 'PROGRAM', 'declare': 'DECLARE', 'function': 'FUNCTION',
    'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'switchcase': 'SWITCHCASE',
    'forcase': 'FORCASE', 'incase': 'INCASE', 'whilecase': 'WHILECASE',
    'untilcase': 'UNTILCASE', 'when': 'WHEN', 'default': 'DEFAULT',
    'until': 'UNTIL', 'return': 'RETURN', 'input': 'INPUT', 'print': 'PRINT',
    'in': 'IN', 'inout': 'INOUT', 'and': 'AND', 'or': 'OR', 'not': 'NOT',
}

# PHASE 2 endiamesos kodikas me quadruples
quad_list = []       # lista me oles tis tetrades
temp_counter = 0     # metritis gia prosorines metavlites

def nextquad():   # epistrefei ton arithmo tis epomenis tetradas
    return len(quad_list) + 1

def genquad(op, x, y, z):     # dimiourgei nea tetrada kai tin vazei sti lista
    quad_list.append((op, x, y, z))

def newtemp():           # dimiourgei nea prosorini metavliti T_1, T_2 ktl
    global temp_counter
    temp_counter += 1
    name = 'T_' + str(temp_counter)
    # Phase 3A - prosthiki prosorinis metavlitis ston pinaka symbolon
    if len(symbol_table) > 0:
        add_entity({'type': 'TEMP', 'name': name})
    return name

def emptylist():         # keni lista etiketon
    return []

def makelist(x):    # lista me mia etiketa
    return [x]

def merge(l1, l2):       # sinxoneusi 2 liston
    return l1 + l2

def backpatch(lst, z):   # simplirosi tis 4is thesis ton tetradon tis listas me to z
    for q in lst:
        old = quad_list[q - 1]
        quad_list[q - 1] = (old[0], old[1], old[2], z)

# PHASE 3A - Pinakas Symbolon (Symbol Table)
symbol_table = []       # stoiva apo scopes
saved_scopes = {}       # apothikeuoume ta scopes gia tin phase 3B
symb_lines = []         # grammes gia to arxeio .symb

def add_scope(name):
    # Phase 3A - dimiourgeia neou scope kai push sti stoiva
    scope = {
        'name': name,
        'nesting_level': len(symbol_table),
        'entities': [],
        'offset': 12     # ta prota 12 bytes einai gia to frame header
    }
    symbol_table.append(scope)

def remove_scope():
    # Phase 3A - afairoume to scope kai to grafoume sto .symb
    scope = symbol_table.pop()
    # apothikeuoume gia tin phase 3B
    saved_scopes[scope['name']] = scope
    # grafoume sto symb_lines
    symb_lines.append('Scope: ' + scope['name'] + ' (nesting level: ' + str(scope['nesting_level']) + ')')
    for entity in scope['entities']:
        if entity['type'] == 'VAR':
            symb_lines.append('  VAR: ' + entity['name'] + ', offset=' + str(entity['offset']))
        elif entity['type'] == 'PARAM':
            symb_lines.append('  PARAM: ' + entity['name'] + ', offset=' + str(entity['offset']) + ', mode=' + entity['parMode'])
        elif entity['type'] == 'TEMP':
            symb_lines.append('  TEMP: ' + entity['name'] + ', offset=' + str(entity['offset']))
        elif entity['type'] == 'FUNC':
            args_str = ', '.join(['(' + a['parMode'] + ')' for a in entity['arguments']])
            fl = str(entity['framelength']) if entity['framelength'] is not None else '?'
            sq = str(entity['startQuad']) if entity['startQuad'] is not None else '?'
            symb_lines.append('  FUNC: ' + entity['name'] + ', startQuad=' + sq + ', framelength=' + fl + ', args=[' + args_str + ']')
    symb_lines.append('')

def add_entity(entity):
    # Phase 3A - prosthiki entity sto trexon scope
    scope = symbol_table[-1]
    if entity['type'] in ('VAR', 'PARAM', 'TEMP'):
        entity['offset'] = scope['offset']
        scope['offset'] += 4
    scope['entities'].append(entity)

def add_argument(parMode):
    # Phase 3A - prosthiki argument stin teleutaia FUNC tou parent scope
    parent = symbol_table[-2]
    for entity in reversed(parent['entities']):
        if entity['type'] == 'FUNC':
            entity['arguments'].append({'parMode': parMode})
            return

def search_entity(name):
    # Phase 3A - anazitisi apo to koryfaio scope pros ta kato
    for i in range(len(symbol_table) - 1, -1, -1):
        for entity in symbol_table[i]['entities']:
            if entity['name'] == name:
                return entity, symbol_table[i]['nesting_level']
    print("Semantic error: undeclared variable/function '" + name + "'")
    sys.exit(1)

def current_scope():
    # Phase 3A - epistrofi tou trexontos scope
    return symbol_table[-1]

# grapsimo arxeiou .int
def create_int_file(filename):
    name = filename.rsplit('.', 1)[0] + '.int'
    with open(name, 'w', encoding='utf-8') as f:
        for i, q in enumerate(quad_list):
            f.write(str(i + 1) + ': ' + str(q[0]) + ', ' + str(q[1]) + ', ' + str(q[2]) + ', ' + str(q[3]) + '\n')

# Phase 3A - grapsimo arxeiou .symb
def create_symb_file(filename):
    name = filename.rsplit('.', 1)[0] + '.symb'
    with open(name, 'w', encoding='utf-8') as f:
        for line in symb_lines:
            f.write(line + '\n')

# PHASE 3B - Paragogi Telikou Kodika (RISC-V Assembly)
asm_lines = []         # grammes assembly

def emit(line):
    # Phase 3B - prosthiki grammis assembly
    asm_lines.append(line)

def find_entity_for_codegen(name, current_scope_name):
    # Phase 3B - vriskei to entity kai to nesting level
    # prota psaxnei sto current scope, meta stous progonous
    if current_scope_name in saved_scopes:
        scope = saved_scopes[current_scope_name]
        for entity in scope['entities']:
            if entity['name'] == name:
                return entity, scope['nesting_level']
    # psaxnei se ola ta scopes
    for scope_name in saved_scopes:
        if scope_name == 'main_framelength':
            continue
        scope = saved_scopes[scope_name]
        for entity in scope['entities']:
            if entity['name'] == name:
                return entity, scope['nesting_level']
    return None, None

def get_func_info(func_name):
    # Phase 3B - vriskei to FUNC entity gia na parei framelength/startQuad
    for scope_name in saved_scopes:
        if scope_name == 'main_framelength':
            continue
        scope = saved_scopes[scope_name]
        for entity in scope['entities']:
            if entity['type'] == 'FUNC' and entity['name'] == func_name:
                return entity
    return None

def gnlvcode(v_name, current_level, current_scope_name):
    # Phase 3B - metaferei ston t0 tin dieuthinsi mias mi topikis metavlitis
    entity, v_level = find_entity_for_codegen(v_name, current_scope_name)
    emit('lw t0,-4(sp)')
    for i in range(current_level - v_level - 1):
        emit('lw t0,-4(t0)')
    emit('addi t0,t0,-' + str(entity['offset']))

def loadvr(v, reg, current_level, current_scope_name):
    # Phase 3B - fortosi tis timis v ston kataxoriti reg
    # an einai stathera
    try:
        int(v)
        emit('li ' + reg + ',' + str(v))
        return
    except ValueError:
        pass
    entity, v_level = find_entity_for_codegen(v, current_scope_name)
    if entity is None:
        emit('li ' + reg + ',' + str(v))
        return
    # an einai global (nesting level 0 = main program)
    if v_level == 0:
        emit('lw ' + reg + ',-' + str(entity['offset']) + '(gp)')
    elif v_level == current_level:
        # topiki metavliti, prosorini, h parametros CV
        if entity['type'] in ('VAR', 'TEMP'):
            emit('lw ' + reg + ',-' + str(entity['offset']) + '(sp)')
        elif entity['type'] == 'PARAM' and entity['parMode'] == 'CV':
            emit('lw ' + reg + ',-' + str(entity['offset']) + '(sp)')
        elif entity['type'] == 'PARAM' and entity['parMode'] == 'REF':
            # i parametros krataei dieuthinsi, prota fortonoume tin dieuthinsi
            emit('lw t0,-' + str(entity['offset']) + '(sp)')
            emit('lw ' + reg + ',(t0)')
    else:
        # mi topiki metavliti, xrisimopoioume gnlvcode
        if entity['type'] in ('VAR', 'TEMP') or (entity['type'] == 'PARAM' and entity['parMode'] == 'CV'):
            gnlvcode(v, current_level, current_scope_name)
            emit('lw ' + reg + ',(t0)')
        elif entity['type'] == 'PARAM' and entity['parMode'] == 'REF':
            gnlvcode(v, current_level, current_scope_name)
            emit('lw t0,(t0)')
            emit('lw ' + reg + ',(t0)')

def storerv(reg, v, current_level, current_scope_name):
    # Phase 3B - apothikefsi tou reg stin metavliti v
    entity, v_level = find_entity_for_codegen(v, current_scope_name)
    if entity is None:
        return
    # an einai global
    if v_level == 0:
        emit('sw ' + reg + ',-' + str(entity['offset']) + '(gp)')
    elif v_level == current_level:
        if entity['type'] in ('VAR', 'TEMP'):
            emit('sw ' + reg + ',-' + str(entity['offset']) + '(sp)')
        elif entity['type'] == 'PARAM' and entity['parMode'] == 'CV':
            emit('sw ' + reg + ',-' + str(entity['offset']) + '(sp)')
        elif entity['type'] == 'PARAM' and entity['parMode'] == 'REF':
            emit('lw t0,-' + str(entity['offset']) + '(sp)')
            emit('sw ' + reg + ',(t0)')
    else:
        if entity['type'] in ('VAR', 'TEMP') or (entity['type'] == 'PARAM' and entity['parMode'] == 'CV'):
            gnlvcode(v, current_level, current_scope_name)
            emit('sw ' + reg + ',(t0)')
        elif entity['type'] == 'PARAM' and entity['parMode'] == 'REF':
            gnlvcode(v, current_level, current_scope_name)
            emit('lw t0,(t0)')
            emit('sw ' + reg + ',(t0)')

def generate_final_code(program_name):
    # Phase 3B - paragogi telikou kodika apo tis tetrades
    # antisoixisi relop se RISC-V branch
    relop_map = {
        '=': 'beq', '<>': 'bne', '<': 'blt',
        '>': 'bgt', '<=': 'ble', '>=': 'bge'
    }
    # vrisko poia scopes antistoixoun se kathe block
    # gia na ksero to current_level kai current_scope_name
    block_info = {}  # block_name -> (nesting_level, scope_name)
    for scope_name in saved_scopes:
        if scope_name == 'main_framelength':
            continue
        scope = saved_scopes[scope_name]
        block_info[scope_name] = (scope['nesting_level'], scope_name)
    # header tou assembly
    emit('.data')
    emit('str_nl: .asciz "\\n"')
    emit('')
    emit('.text')
    # to prwto pragma einai jump stin main
    emit('L0:')
    emit('b L' + str(program_name))
    emit('')
    # current block tracking
    current_scope_name = None
    current_level = 0
    par_counter = 0       # metritis parametron gia call
    # epexergasia kathe tetradas
    for idx, quad in enumerate(quad_list):
        quad_num = idx + 1
        op = quad[0]
        x = quad[1]
        y = quad[2]
        z = quad[3]
        # etiketa gia kathe tetrada
        if op == 'begin_block' and x == program_name:
            emit('L' + str(program_name) + ':')
        emit('L' + str(quad_num) + ':')
        if op == 'begin_block':
            current_scope_name = x
            if x in block_info:
                current_level = block_info[x][0]
            if x == program_name:
                # main program: allocate frame kai set gp
                main_fl = saved_scopes.get('main_framelength', 12)
                emit('addi sp,sp,' + str(main_fl))
                emit('mv gp,sp')
            else:
                # sinartisi: save return address
                emit('sw ra,(sp)')
        elif op == 'end_block':
            if x == program_name:
                pass  # to halt exei idi ginei
            else:
                emit('lw ra,(sp)')
                emit('jr ra')
        elif op == 'halt':
            emit('li a0,0')
            emit('li a7,93')
            emit('ecall')
        elif op == ':=':
            loadvr(x, 't1', current_level, current_scope_name)
            storerv('t1', z, current_level, current_scope_name)
        elif op in ('+', '-', '*', '/'):
            loadvr(x, 't1', current_level, current_scope_name)
            loadvr(y, 't2', current_level, current_scope_name)
            if op == '+':
                emit('add t1,t1,t2')
            elif op == '-':
                emit('sub t1,t1,t2')
            elif op == '*':
                emit('mul t1,t1,t2')
            elif op == '/':
                emit('div t1,t1,t2')
            storerv('t1', z, current_level, current_scope_name)
        elif op == 'jump':
            emit('b L' + str(z))
        elif op in relop_map:
            loadvr(x, 't1', current_level, current_scope_name)
            loadvr(y, 't2', current_level, current_scope_name)
            emit(relop_map[op] + ' t1,t2,L' + str(z))
        elif op == 'out':
            loadvr(x, 't1', current_level, current_scope_name)
            emit('mv a0,t1')
            emit('li a7,1')
            emit('ecall')
            emit('la a0,str_nl')
            emit('li a7,4')
            emit('ecall')
        elif op == 'inp':
            emit('li a7,5')
            emit('ecall')
            storerv('a0', x, current_level, current_scope_name)
        elif op == 'retv':
            loadvr(x, 't1', current_level, current_scope_name)
            emit('lw t0,-8(sp)')
            emit('sw t1,(t0)')
        elif op == 'par':
            # x = parametros, y = tropos (CV/REF/RET)
            # vriskoume to onoma tis sinartisis apo to epomeno call
            callee_name = None
            for j in range(idx + 1, len(quad_list)):
                if quad_list[j][0] == 'call':
                    callee_name = quad_list[j][1]
                    break
                if quad_list[j][0] != 'par':
                    break
            func_info = get_func_info(callee_name) if callee_name else None
            callee_fl = func_info['framelength'] if func_info else 12
            # elegxoume an einai i proti parametros
            if idx == 0 or quad_list[idx - 1][0] != 'par':
                par_counter = 0
                # proti par: kanoume addi fp,sp,framelength
                emit('addi fp,sp,' + str(callee_fl))
            if y == 'CV':
                # perasma kata timi
                loadvr(x, 't0', current_level, current_scope_name)
                emit('sw t0,-' + str(12 + 4 * par_counter) + '(fp)')
                par_counter += 1
            elif y == 'REF':
                # perasma kata anafora
                entity_x, x_level = find_entity_for_codegen(x, current_scope_name)
                if entity_x is not None and x_level == current_level:
                    if entity_x['type'] in ('VAR', 'TEMP') or (entity_x['type'] == 'PARAM' and entity_x['parMode'] == 'CV'):
                        emit('addi t0,sp,-' + str(entity_x['offset']))
                        emit('sw t0,-' + str(12 + 4 * par_counter) + '(fp)')
                    elif entity_x['type'] == 'PARAM' and entity_x['parMode'] == 'REF':
                        emit('lw t0,-' + str(entity_x['offset']) + '(sp)')
                        emit('sw t0,-' + str(12 + 4 * par_counter) + '(fp)')
                elif entity_x is not None and x_level == 0:
                    # global variable
                    emit('addi t0,gp,-' + str(entity_x['offset']))
                    emit('sw t0,-' + str(12 + 4 * par_counter) + '(fp)')
                else:
                    # mi topiki metavliti
                    if entity_x is not None:
                        if entity_x['type'] in ('VAR', 'TEMP') or (entity_x['type'] == 'PARAM' and entity_x['parMode'] == 'CV'):
                            gnlvcode(x, current_level, current_scope_name)
                            emit('sw t0,-' + str(12 + 4 * par_counter) + '(fp)')
                        elif entity_x['type'] == 'PARAM' and entity_x['parMode'] == 'REF':
                            gnlvcode(x, current_level, current_scope_name)
                            emit('lw t0,(t0)')
                            emit('sw t0,-' + str(12 + 4 * par_counter) + '(fp)')
                par_counter += 1
            elif y == 'RET':
                # epistrofi timis - to x einai i prosorini metavliti
                entity_x, x_level = find_entity_for_codegen(x, current_scope_name)
                if entity_x is not None:
                    emit('addi t0,sp,-' + str(entity_x['offset']))
                    emit('sw t0,-8(fp)')
                par_counter += 1
        elif op == 'call':
            # x = onoma sinartisis
            func_info = get_func_info(x)
            callee_fl = func_info['framelength'] if func_info else 12
            callee_level = 0
            if x in block_info:
                callee_level = block_info[x][0]
            # sindesmos prospelasis (access link)
            if callee_level == current_level + 1:
                # i kalousa einai goneas tis klithisas
                emit('sw sp,-4(fp)')
            else:
                # idio vathos foliasmatous, exoun ton idio gonea
                emit('lw t0,-4(sp)')
                emit('sw t0,-4(fp)')
            # metafora sp kai klisi
            emit('addi sp,sp,' + str(callee_fl))
            emit('jal L' + str(func_info['startQuad']))
            emit('addi sp,sp,-' + str(callee_fl))
    emit('')

def create_asm_file(filename):
    # Phase 3B - grapsimo arxeiou .asm
    name = filename.rsplit('.', 1)[0] + '.asm'
    with open(name, 'w', encoding='utf-8') as f:
        for line in asm_lines:
            f.write(line + '\n')

class Token:
    def __init__(self, token_type, value, linenum):
        self.type = token_type   # ti eidos token einai
        self.value = value          # timi pou diavastike
        self.linenum = linenum  # se pia grammi einai
    def __str__(self):
        return "Token(" + self.type + ", '" + self.value + "', line " + str(self.linenum) + ")"


#lektikos analitis diavazei char char kai ftiaxnei tokens
class Lexer:
    def __init__(self, src):
        self.src = src          # source code se string
        self.position = 0       # position sto string
        self.line = 1            # metritis grammon

    def error(self, message):
        print("Lexical error at line " + str(self.line) + ": " + message)
        sys.exit(1)              # stop

    def next_token(self):                    #prospername kena sxolia
        while self.position < len(self.src):
            ch = self.src[self.position]

            if ch in (' ', '\t', '\r', '\n'): # empty chars
                if ch == '\n': 
                    self.line += 1   # change line
                self.position += 1
            elif ch == '/' and self.position + 1 < len(self.src):
                next_char = self.src[self.position + 1]
                if next_char == '/':      
                    self.position += 2
                    while self.position < len(self.src) and self.src[self.position] != '\n':
                        self.position += 1
                elif next_char == '*': 
                    self.position += 2
                    closed = False
                    while self.position + 1 < len(self.src):
                        if self.src[self.position] == '*' and self.src[self.position + 1] == '/':
                            self.position += 2   #found the close
                            closed = True
                            break
                        if self.src[self.position] == '\n':
                            self.line += 1
                        self.position += 1
                    if not closed:       # den ekleise pote
                        self.error("unclosed comment")
                else:
                    break  
            else:
                break 

        if self.position >= len(self.src):  #telos arxeiou
            return Token(TK_EOF, 'EOF', self.line)

        ch = self.src[self.position]
        line = self.line  # kratame tin grammi gia to token

        # anagnoristika kai keywords
        if ch.isalpha():  # ksekina me gramma
            start = self.position
            while self.position < len(self.src) and self.src[self.position].isalnum():  #grammata h psifia
                self.position += 1
            word = self.src[start:self.position]
            
            if len(word) > 30:  # max 30 characters
                self.error(word + "' exceeds max length of 30")
                
            if word in KEYWORDS:    # an eina keyword pairnei ton typo toy ,allios to ID
                token_type = KEYWORDS[word]
            else:
                token_type = TK_ID  
            return Token(token_type, word, line)

        # arithmo (mono psifia tou prosimo to vazei o parser)
        if ch.isdigit():
            start = self.position
            while self.position < len(self.src) and self.src[self.position].isdigit():
                self.position += 1
            num_str = self.src[start:self.position]
            
            if int(num_str) > 32767:  # elenxos orion
                self.error("integer " + num_str + " ektos orion (max 32767)")
            return Token(TK_INTEGER, num_str, line)

        # diploiu telestes ,blepo ene xaraktira mbros
        if ch == ':':
            if self.position + 1 < len(self.src) and self.src[self.position + 1] == '=':
                self.position += 2
                return Token(':=', ':=', line)        # anathesi
        
            else:
                self.position += 1
                return Token(':', ':', line)      

        if ch == '<':
            self.position += 1
            if self.position < len(self.src):
                if self.src[self.position] == '=':
                    self.position += 1
                    return Token('<=', '<=', line)   # mikrotero h iso
                if self.src[self.position] == '>':
                    self.position += 1
                    return Token('<>', '<>', line)         #diafortiko
            return Token('<', '<', line)       #mikrotero

        if ch == '>':
            self.position += 1
            if self.position < len(self.src) and self.src[self.position] == '=':
                self.position += 1
                return Token('>=', '>=', line)       # megalitero i iso
            return Token('>', '>', line)    # megalitero

        if ch in ['+', '-', '*', '/', '=', ',', ';', '(', ')', '{', '}', '[', ']']:
            self.position += 1
            return Token(ch, ch, line)  #o typos einai o idios o charaxtiras
        self.error("invalid character")    

#xirsimopoii 1 lookahead token kai akolouthei ti grammatiki
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()  #pairnoyme to proto token
        
    def error(self, message):
        print("Syntax error at line " + str(self.token.linenum) + ": " + message)
        sys.exit(1)

    def match(self, expected_type):
        if self.token.type == expected_type:  # an teriaxei proxoro
            value = self.token.value
            self.token = self.lexer.next_token()      # pairnoume to epomeno
            return value
        else:
            self.error("expected " + expected_type)

    def syntax_analyzer(self):
        self.program()             # ksekiname apo ton arxiko kodika
        self.match(TK_EOF)         
        create_int_file(sys.argv[1])           # grafoume to .int
        # Phase 3A - grafoume to .symb
        create_symb_file(sys.argv[1])
        # Phase 3B - paragogi telikou kodika kai grapsimo .asm
        program_name = quad_list[0][1] if quad_list else 'main'
        # vriskei to onoma tou programmatos apo tin teleutaia begin_block pou akolouthei halt
        for i in range(len(quad_list) - 1, -1, -1):
            if quad_list[i][0] == 'halt':
                for j in range(i, -1, -1):
                    if quad_list[j][0] == 'begin_block':
                        program_name = quad_list[j][1]
                        break
                break
        generate_final_code(program_name)
        create_asm_file(sys.argv[1])
        print("Compilation successfully completed")

    # kanones grammatikis (kathe methodos antistixoi se ena kanona)

    def program(self):
        self.match('PROGRAM')   # perimeno tin lexi "PROGRAM
        name = self.match(TK_ID)
        # Phase 3A - dimiourgeia scope gia to kyrious programma
        add_scope(name)
        self.programblock(name, True)

    # PHASE 2 - begin_block/end_block/halt
    def programblock(self, name, is_main):
        self.match('{')               # arxi block
        self.declarations()           # dilosi metavliton
        self.functions()              # orismoi synartiseon
        genquad('begin_block', name, '_', '_')
        # Phase 3A - to startQuad tis sinartisis einai to begin_block
        if not is_main:
            parent = symbol_table[-2]
            for entity in reversed(parent['entities']):
                if entity['type'] == 'FUNC' and entity['name'] == name:
                    entity['startQuad'] = nextquad() - 1
                    break
        self.statements_sequence()    # entoles
        if is_main:
            genquad('halt', '_', '_', '_')
        genquad('end_block', name, '_', '_')
        # Phase 3A - framelength kai remove scope
        if not is_main:
            parent = symbol_table[-2]
            for entity in reversed(parent['entities']):
                if entity['type'] == 'FUNC' and entity['name'] == name:
                    entity['framelength'] = current_scope()['offset']
                    break
        else:
            # Phase 3A - apothikeuoume to framelength tou main
            saved_scopes['main_framelength'] = current_scope()['offset']
        remove_scope()
        self.match('}')               # telos tou block

    def declarations(self):
        while self.token.type == 'DECLARE':         # oses declare ypraxoun
            self.match('DECLARE')
            self.varlist()
            self.match(';')

    def varlist(self):
        if self.token.type == TK_ID:
            vname = self.match(TK_ID)
            # Phase 3A - prosthiki metavlitis ston pinaka symbolon
            add_entity({'type': 'VAR', 'name': vname})
            while self.token.type == ',':  #metablites xorismenes me komma
                self.match(',')
                vname = self.match(TK_ID)
                # Phase 3A - prosthiki metavlitis ston pinaka symbolon
                add_entity({'type': 'VAR', 'name': vname})

    def functions(self):
        while self.token.type == 'FUNCTION':            #mhden h perissoteres synartiseis
            self.func()

    def func(self):
        self.match('FUNCTION')
        name = self.match(TK_ID)       # onoma synartisis
        # Phase 3A - prosthiki FUNC entity sto parent scope
        add_entity({'type': 'FUNC', 'name': name, 'startQuad': None, 'arguments': [], 'framelength': None})
        # Phase 3A - neo scope gia ti sinartisi
        add_scope(name)
        self.formalpars()       #typikes parametroi
        self.programblock(name, False)

    def formalpars(self):
        self.match('(')
        self.formalparlist()
        self.match(')')

    def formalparlist(self):
        if self.token.type == 'IN' or self.token.type == 'INOUT':     #an exei parametrous
            self.formalparitem()
            while self.token.type == ',':  #xorismenes me komma
                self.match(',')
                self.formalparitem()

    def formalparitem(self):
        if self.token.type == 'IN':  # perasma kata timi
            self.match('IN')
            pname = self.match(TK_ID)
            # Phase 3A - prosthiki parametrou ston pinaka symbolon
            add_entity({'type': 'PARAM', 'name': pname, 'parMode': 'CV'})
            add_argument('CV')
        elif self.token.type == 'INOUT':  # perasma kata anafora
            self.match('INOUT')
            pname = self.match(TK_ID)
            # Phase 3A - prosthiki parametrou ston pinaka symbolon
            add_entity({'type': 'PARAM', 'name': pname, 'parMode': 'REF'})
            add_argument('REF')
        else:
            self.error("expected IN or INOUT")

    def statements(self):
        if self.token.type == '{':    # an exei {
            self.match('{')
            self.statements_sequence()
            self.match('}')
        else:  
            self.statement()

    def statements_sequence(self):
        first_tokens = (TK_ID, 'IF', 'WHILE', 'SWITCHCASE', 'WHILECASE', 
                    'INCASE', 'FORCASE', 'UNTILCASE', 'INPUT', 'PRINT', 'RETURN')
        if self.token.type in first_tokens:          #an xekinaei entoli
            self.statement()
            while self.token.type == ';':  # ; einai diaxoristiko
                self.match(';')
                self.statement()

    def statement(self):
        if self.token.type == TK_ID:            #assignment
            self.assignment_stat()
        elif self.token.type == 'IF':       
            self.if_stat()
        elif self.token.type == 'WHILE':    
            self.while_stat()
        elif self.token.type == 'SWITCHCASE': 
            self.switchcase_stat()
        elif self.token.type == 'WHILECASE': 
            self.whilecase_stat()
        elif self.token.type == 'INCASE': 
            self.incase_stat()
        elif self.token.type == 'FORCASE': 
            self.forcase_stat()
        elif self.token.type == 'UNTILCASE': 
            self.untilcase_stat()
        elif self.token.type == 'INPUT':    # eisodos
            self.input_stat()
        elif self.token.type == 'PRINT':    # eksodos
            self.print_stat()
        elif self.token.type == 'RETURN':   # epistrofi timis
            self.return_stat()
        else: 
            self.error("expected statement")

    # PHASE 2 assignemtn me tetrada
    def assignment_stat(self):
        name = self.match(TK_ID)       # metavliti
        # Phase 3A - elegxos an i metavliti exei dilothei
        search_entity(name)
        self.match(':=')        # telestis anathesis
        e_place = self.expression()
        genquad(':=', e_place, '_', name)

    # PHASE 2 - backpatching gia if/else
    def if_stat(self):
        self.match('IF')
        b_true, b_false = self.condition()
        backpatch(b_true, nextquad())        # true pigenei stis entoles
        self.statements()
        ifList = makelist(nextquad())
        genquad('jump', '_', '_', '_')         # meta to if pigene sto telos
        backpatch(b_false, nextquad())         # false pigenei sto else h meta
        self.elsepart()
        backpatch(ifList, nextquad())    # to jump pigenei meta to else

    def elsepart(self):
        if self.token.type == 'ELSE':  # an iparxei else
            self.match('ELSE')
            self.statements()

    # PHASE 2 backpatching gia while
    def while_stat(self):
        self.match('WHILE')
        condquad = nextquad()     # thesi tis synthikis
        b_true, b_false = self.condition()
        backpatch(b_true, nextquad())
        self.statements()
        genquad('jump', '_', '_', condquad) # pisw stin synthiki
        backpatch(b_false, nextquad())      # eksodos apo to loop

    # PHASE 2 switchcase me exitlist
    def switchcase_stat(self):
        self.match('SWITCHCASE')
        exitlist = emptylist()
        while self.token.type == 'WHEN':
            self.match('WHEN')
            b_true, b_false = self.condition()
            self.match(':')
            backpatch(b_true, nextquad())
            self.statements()
            e = makelist(nextquad())
            genquad('jump', '_', '_', '_')  # jump stin eksodo
            exitlist = merge(exitlist, e)
            backpatch(b_false, nextquad())
        self.match('DEFAULT')
        self.match(':')
        self.statements()
        backpatch(exitlist, nextquad())   # ola ta jump pigenoun sto telos

    # san switchcase alla kani loop
    def whilecase_stat(self):
        self.match('WHILECASE')
        condquad = nextquad()       # arxi loop
        exitlist = emptylist()
        while self.token.type == 'WHEN':
            self.match('WHEN')
            b_true, b_false = self.condition()
            self.match(':')
            backpatch(b_true, nextquad())
            self.statements()
            e = makelist(nextquad())
            genquad('jump', '_', '_', '_')
            exitlist = merge(exitlist, e)
            backpatch(b_false, nextquad())
        self.match('DEFAULT')
        self.match(':')
        self.statements()
        genquad('jump', '_', '_', condquad) # loop pisw stin arxi
        backpatch(exitlist, nextquad())

    # incase me flag metavliti
    def incase_stat(self):
        self.match('INCASE')
        flag = newtemp()       # flag gia na kseroume an ektelestike kati
        firstquad = nextquad()
        genquad(':=', '0', '_', flag)       # arxikopoiisi flag = 0
        while self.token.type == 'WHEN':
            self.match('WHEN')
            b_true, b_false = self.condition()
            self.match(':')
            backpatch(b_true, nextquad())
            self.statements()
            genquad(':=', '1', '_', flag)   # flag = 1 an ektelestike
            backpatch(b_false, nextquad())
        genquad('=', '1', flag, firstquad)  # an flag==1, ksanapame stin arxi

    # forcase (arxikopoiisi + loop)
    def forcase_stat(self):
        self.match('FORCASE')
        id_name = self.match(TK_ID)
        # Phase 3A - elegxos an i metavliti exei dilothei
        search_entity(id_name)
        self.match('=')
        init_val = self.match(TK_INTEGER)
        genquad(':=', init_val, '_', id_name) # arxikopoiisi metavlitis
        condquad = nextquad()
        exitlist = emptylist()
        while self.token.type == 'WHEN':
            self.match('WHEN')
            b_true, b_false = self.condition()
            self.match(':')
            backpatch(b_true, nextquad())
            self.statements()
            e = makelist(nextquad())
            genquad('jump', '_', '_', '_')
            exitlist = merge(exitlist, e)
            backpatch(b_false, nextquad())
        genquad('jump', '_', '_', condquad) # loop pisw
        backpatch(exitlist, nextquad())

    # untilcase
    def untilcase_stat(self):
        self.match('UNTILCASE')
        condquad = nextquad()    # arxi tou loop
        while self.token.type == 'WHEN':
            self.match('WHEN')
            b_true, b_false = self.condition()
            self.match(':')
            backpatch(b_true, nextquad())
            self.statements()
            backpatch(b_false, nextquad())
        self.match('UNTIL')
        b_true, b_false = self.condition()
        backpatch(b_false, condquad)        # false = pisw sto loop
        backpatch(b_true, nextquad())       # true = eksodos

    def print_stat(self):
        self.match('PRINT')
        e_place = self.expression()
        genquad('out', e_place, '_', '_')   # tetrada eksodou

    def input_stat(self):
        self.match('INPUT')
        name = self.match(TK_ID)
        # Phase 3A - elegxos an i metavliti exei dilothei
        search_entity(name)
        genquad('inp', name, '_', '_')      # tetrada eisodou

    def return_stat(self):
        self.match('RETURN')
        e_place = self.expression()
        genquad('retv', e_place, '_', '_')  # tetrada epistrofis

    # paragogi par/call tetradon gia klisi sinartisis
    def actualpars(self):
        self.match('(')
        self.actualparlist()
        self.match(')')

    def actualparlist(self):
        if self.token.type == 'IN' or self.token.type == 'INOUT':
            self.actualparitem()
            while self.token.type == ',':
                self.match(',')
                self.actualparitem()

    def actualparitem(self):
        if self.token.type == 'IN':   # kata timi
            self.match('IN')
            e_place = self.expression()
            genquad('par', e_place, 'CV', '_')
        elif self.token.type == 'INOUT':  # kata anafora
            self.match('INOUT')
            name = self.match(TK_ID)
            # Phase 3A - elegxos an i metavliti exei dilothei
            search_entity(name)
            genquad('par', name, 'REF', '_')
        else:
            self.error("expected IN or INOUT")

    # condition epistrefei (true_list, false_list) - logiko OR
    def condition(self):
        b_true, b_false = self.boolterm()
        while self.token.type == 'OR':
            backpatch(b_false, nextquad())   # an false dokimase to epomeno
            self.match('OR')
            q2_true, q2_false = self.boolterm()
            b_true = merge(b_true, q2_true)
            b_false = q2_false
        return b_true, b_false

    # boolterm epistrefei (true_list, false_list)  logiko AND
    def boolterm(self):
        q_true, q_false = self.boolfactor()
        while self.token.type == 'AND':
            backpatch(q_true, nextquad())    # an true, dokimase kai to epomeno
            self.match('AND')
            r2_true, r2_false = self.boolfactor()
            q_false = merge(q_false, r2_false)
            q_true = r2_true
        return q_true, q_false

    # boolfactor epistrefei (true_list, false_list)
    def boolfactor(self):
        if self.token.type == 'NOT':      # NOT - antistrefoume tis listes
            self.match('NOT')
            self.match('[')
            b_true, b_false = self.condition()
            self.match(']')
            return b_false, b_true          # swap true me false!
        elif self.token.type == '[':  # apla brackets
            self.match('[')
            b_true, b_false = self.condition()
            self.match(']')
            return b_true, b_false
        else:         # E1 relop E2
            e1_place = self.expression()
            op = self.relational_oper()     # pairnoume ton telesti
            e2_place = self.expression()
            true_list = makelist(nextquad())
            genquad(op, e1_place, e2_place, '_')   # tetrada sigrkisis
            false_list = makelist(nextquad())
            genquad('jump', '_', '_', '_')          # jump an den isxiei
            return true_list, false_list

    # expression epistrefei place (onoma metavlitis h temp)
    def expression(self):
        sign = self.optional_sign()         # kratame to prosimo an iparxei
        t1_place = self.term()
        if sign == '-':          # arnhtiko prosimo
            w = newtemp()
            genquad('-', '0', t1_place, w)
            t1_place = w
        while self.token.type in ('+', '-'):
            op = self.match(self.token.type)
            t2_place = self.term()
            w = newtemp()          # nea prosorini gia to apotelesma
            genquad(op, t1_place, t2_place, w)
            t1_place = w
        return t1_place

    # term epistrefei place
    def term(self):
        f1_place = self.factor()
        while self.token.type in ('*', '/'):
            op = self.match(self.token.type)
            f2_place = self.factor()
            w = newtemp()
            genquad(op, f1_place, f2_place, w)
            f1_place = w
        return f1_place

    # factor epistrefei place
    def factor(self):
        if self.token.type == TK_INTEGER:     #arithmos
            return self.match(TK_INTEGER)
        elif self.token.type == '(':           
            self.match('(')
            place = self.expression()
            self.match(')')
            return place
        elif self.token.type == TK_ID:         # metavliti i klisi sinartisis
            name = self.match(TK_ID)
            # Phase 3A - elegxos an to onoma exei dilothei
            search_entity(name)
            return self.idtail(name)
        else:
            self.error("expected factor")

    # idtail - an akolouthei ( einai klisi sinartisis, allios apli metavliti
    def idtail(self, name):
        if self.token.type == '(':        # klisi sinartisis
            self.actualpars()
            w = newtemp()              # prosorini gia tin epistrefoumeni timi
            genquad('par', w, 'RET', '_')
            genquad('call', name, '_', '_')
            return w
        return name

    # epistrefei ton sxesiako telesti ws string
    def relational_oper(self):
        if self.token.type in ('=', '<=', '>=', '<>', '<', '>'):
            return self.match(self.token.type)
        else:
            self.error("expected relational operator")

    # epistrefei to prosimo an yparxei, allios None
    def optional_sign(self):
        if self.token.type in ('+', '-'):
            return self.match(self.token.type)
        return None



def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source_file>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            src = f.read()          #diavazo olo to arxeio
    except FileNotFoundError:
        print("Error: file '" + filename + "' not found")
        sys.exit(1)
    lexer = Lexer(src)            # dimiourgia lektikoy analiti
    parser = Parser(lexer)          # dimiourgia sintaktikoy analiti
    parser.syntax_analyzer()        # start analisis
if __name__ == '__main__':
    main()