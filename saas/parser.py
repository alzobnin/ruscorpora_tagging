import sys
import itertools

class ParseException(Exception):
    pass


def parse_substack(substack):
    if len(substack) % 2 == 0:
        raise ParseException()
    conjuncts = []
    cur_conjunct = [substack[0]]
    for i in range(1, len(substack), 2):
        if substack[i] == '&':
            cur_conjunct.append(substack[i + 1])
        elif substack[i] == '|':
            conjuncts.append(cur_conjunct)
            cur_conjunct = [substack[i + 1]]
        else:
            raise ParseException()
    if cur_conjunct:
        conjuncts.append(cur_conjunct)
    for i in range(len(conjuncts)):
        if len(conjuncts[i]) == 1:
            conjuncts[i] = conjuncts[i][0]
        else:
            conjuncts[i] = ('&', conjuncts[i])
    if len(conjuncts) == 1:
        return conjuncts[0]
    return ('|', conjuncts)


def parse(s):
    stack = []
    word = ''
    brackets = []
    for c in s:
        if c not in '()|&':
            word += c
        else:
            if word.strip():
                stack.append(word.strip())
                word = ''
            if c == '(':
                brackets.append(len(stack))
                stack.append(c)
            elif c == ')':
                if not brackets:
                    raise ParseException()
                stack[brackets[-1]:] = [parse_substack(stack[brackets[-1] + 1:])]
                brackets.pop()
            else:
                stack.append(c)
    if brackets:
        raise ParseException()
    if word.strip():
        stack.append(word.strip())
    return parse_substack(stack)


def child_operands(tree):
    if type(tree) is str:
        return [tree]
    operator, operands = tree
    child_operands = []
    for operand in operands:
        if type(operand) == str:
            child_operands.append(operand)
        else:
            suboperator, suboperands = operand
            if suboperator == "|":
                child_operands += suboperands
            else:
                child_operands.append(operand)
    return child_operands


def flat(tree):
    if type(tree) is str:
        return tree
    operator, operands = tree
    operands = list(map(flat, operands))
    if operator in "|&" and len(operands) == 1:
        return operands[0]
    i = 0
    while i < len(operands):
        operand = operands[i]
        if not (type(operand) is str) and operand[0] == operator:
            operands[i:i+1] = operand[1]
        else:
            i += 1
    return operator, operands


def dnf(tree):
    if type(tree) is str:
        return tree
    operator, operands = tree
    operands = map(dnf, operands)
    operator, operands = flat((operator, operands))
    if operator == "&":
        operator = "|"
        sub_operands = list((child_operands(sub_tree) for sub_tree in operands))
        print list(sub_operands)
        operands = []
        for item in itertools.product(*sub_operands):
            print list(item)
            operands.append(('&', list(item)))
    return flat((operator, operands))


def join_disjuncts(tree):
    if type(tree) is str:
        return tree
    operator, operands = tree
    operands = list(map(join_disjuncts, operands))
    if operator == "&":
        return ",".join(sorted(operands))
    return operator, operands


def clause(param, value):
    if param in ("form", "lex"):
        if value.startswith("*"):
            rparam = "r" + param
            rvalue = value.decode("utf-8")[::-1].encode("utf-8")
            return '(sz_%s:"%s")' % (rparam, rvalue), 1
        elif "*" in value[1:-1]:
            rparam = "r" + param
            left, right = value.decode("utf-8").split("*", 1)
            left = left.encode("utf-8") + "*"
            rright = right[::-1].encode("utf-8") + "*"
            return '(sz_%s:"%s" /0 sz_%s:"%s")' % (param, left, rparam, rright), 2
    return '(sz_%s:"%s")' % (param, value), 1


def subs(tree, param):
    if type(tree) is str:
        if tree.startswith("-"):
            return '(sz_lex:"*" ~/0 %s)' % clause(param, tree[1:])[0]
        else:
            return clause(param, tree)
    operator, operands = tree
    if operator == "&":
        operator = " /0 "
        nodes_count = len(operands)
    else:
        operator = " %s " % operator
        nodes_count = 1
    operands = map(lambda x: subs(x, param)[0], operands)
    result = operator.join(operands)
    if operator != " /0 ":
        result = "(" + result + ")"
    return result, nodes_count


if __name__ == "__main__":
    tree = parse(sys.stdin.readline())
    print tree
    print child_operands(tree)
    print "Flat:", flat(tree)
    print dnf(tree)
    print join_disjuncts(dnf(tree))
