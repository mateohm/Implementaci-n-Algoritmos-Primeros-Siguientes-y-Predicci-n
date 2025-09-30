from collections import defaultdict

EPSILON = 'ε'

class Grammar:
    def __init__(self, rules):
        self.rules = defaultdict(list)
        self.nonterminals = set()
        self.terminals = set()
        self.start_symbol = None
        self._parse_rules(rules)

    def _parse_rules(self, rules):
        for left, right in rules:
            if self.start_symbol is None:
                self.start_symbol = left
            self.nonterminals.add(left)
            productions = right.split('|')
            for prod in productions:
                symbols = prod.strip().split()
                self.rules[left].append(symbols)
                for s in symbols:
                    if not s.isupper() and s != EPSILON:
                        self.terminals.add(s)

    def __str__(self):
        out = []
        for nt, prods in self.rules.items():
            out.append(f"{nt} -> {' | '.join([' '.join(p) for p in prods])}")
        return "\n".join(out)


def compute_first(grammar):
    first = defaultdict(set)

    def first_of(symbol):
        if symbol in grammar.terminals or symbol == EPSILON:
            return {symbol}
        if symbol in first and first[symbol]:
            return first[symbol]

        result = set()
        for production in grammar.rules[symbol]:
            for sym in production:
                sym_first = first_of(sym)
                result |= (sym_first - {EPSILON})
                if EPSILON not in sym_first:
                    break
            else:
                result.add(EPSILON)
        first[symbol] = result
        return result

    for nt in grammar.nonterminals:
        first_of(nt)
    return first


def compute_follow(grammar, first):
    follow = defaultdict(set)
    follow[grammar.start_symbol].add('$')  

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.rules.items():
            for prod in productions:
                for i, symbol in enumerate(prod):
                    if symbol in grammar.nonterminals:
                        trailer = set()
                        for sym in prod[i+1:]:
                            sym_first = first[sym] if sym in grammar.nonterminals else {sym}
                            trailer |= (sym_first - {EPSILON})
                            if EPSILON not in sym_first:
                                break
                        else:
                            trailer |= follow[nt]
                        old_size = len(follow[symbol])
                        follow[symbol] |= trailer
                        if len(follow[symbol]) > old_size:
                            changed = True
    return follow


def build_parsing_table(grammar, first, follow):
    table = defaultdict(dict)
    for nt, productions in grammar.rules.items():
        for prod in productions:
            first_set = set()
            for sym in prod:
                sym_first = first[sym] if sym in grammar.nonterminals else {sym}
                first_set |= (sym_first - {EPSILON})
                if EPSILON not in sym_first:
                    break
            else:
                first_set.add(EPSILON)

            for terminal in first_set - {EPSILON}:
                table[nt][terminal] = prod

            if EPSILON in first_set:
                for terminal in follow[nt]:
                    table[nt][terminal] = prod
    return table


# PRUEBA CON LA GRAMÁTICA

rules = [
    ("A", "a B C"),
    ("B", "b bas | big C boss"),
    ("C", "ε | c")
]

grammar = Grammar(rules)

print("Gramática:")
print(grammar)

first = compute_first(grammar)
print("\nPRIMEROS:")
for nt, s in first.items():
    print(f"FIRST({nt}) = {s}")

follow = compute_follow(grammar, first)
print("\nSIGUIENTES:")
for nt, s in follow.items():
    print(f"FOLLOW({nt}) = {s}")

table = build_parsing_table(grammar, first, follow)
print("\nTABLA DE PREDICCIÓN:")
for nt, row in table.items():
    for t, prod in row.items():
        print(f"M[{nt}, {t}] = {nt} -> {' '.join(prod)}")
