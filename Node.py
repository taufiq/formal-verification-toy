from constants import *
class Node:
    """
    Represents a node in an abstract syntax tree
    
    Attributes:
        symbol (str): Symbol representing the node type.
        op (str): Operator for binary operations.
        left (Node | any): Left child node or value.
        right (Node | any): Right child node or value.
        eval_type (str): Type used for evaluation.
    """
    def __init__(self, symbol, op, left, right, eval_type):
        self.left = left
        self.right = right
        self.op = op
        self.symbol = symbol
        self.eval_type = eval_type

    # 2 recurse
    # 1 don't recurse
    # 0 don't include
    def print_node_rec_aux(self,left:int, right:int):
        assert 2 >= left >= 0 and 2 >= right >= 0

        left_str = self.left.print_node_rec() if left == 2 else (str(self.left) if left == 1 else "")
        right_str = self.right.print_node_rec() if right == 2 else (str(self.right) if right==1 else "")
        
        components = [self.op or self.symbol]
        if left_str:
            components.append(left_str)
        if right_str:
            components.append(right_str)
        
        return "(" + " ".join(components) + ")"
        # assert(2 >= left >= 0 and 2 >= right >= 0)

        # print_symbol  = self.op if self.op else self.symbol
        # if left == 2 and right == 2:
        #     return "(" + print_symbol + " " + self.left.print_node_rec() + "," + self.right.print_node_rec() + ")"
        # elif left == 2 and right == 1:
        #     return "(" + print_symbol + " " + self.left.print_node_rec() + "," + str(self.right) + ")"
        # elif left == 2 and right == 0:
        #     return "(" + self.symbol + " " + self.left.print_node_rec() + ")"
        # elif left == 1 and right == 2:
        #     return "(" + print_symbol + " " + str(self.left) + "," + self.right.print_node_rec() + ")"
        # elif left == 1 and right == 1:
        #     return "(" + print_symbol + " " + str(self.left) + "," + str(self.right) + ")"
        # elif left == 1 and right == 0:
        #     return "(" + print_symbol + " " + str(self.left) +  ")"
        # elif left == 0 and right == 2:
        #     return "(" + self.symbol + " " + self.right.print_node_rec() + ")"
        # elif left == 0 and right == 1:
        #     return "(" + print_symbol + " " + str(self.right) +  ")"
        # elif left == 0 and right == 0:
        #     return "(" + print_symbol + ")"
    
    
    def printWhileLoopBody(self, loop_body):
        return "".join(statement.print_node_rec() for statement in loop_body)
    # def printWhileLoopBody(self, loop_body):
    #     loop_body_string = ""
    #     for statement in loop_body:
    #         loop_body_string += statement.print_node_rec()
    #     return loop_body_string


    def print_node_rec(self):
        if self.symbol == TERMINAL_IF_THEN_ELSE:
            condition, then_body, else_body = self.left
            return f"(if {condition.print_node_rec()} then {then_body.print_node_rec()} else {else_body.print_node_rec()})"
        if self.symbol == TERMINAL_WHILE_LOOP:
            guard, *body = self.left
            return f"while_loop({guard.print_node_rec()}, {self.printWhileLoopBody(body)})"
        
        left_type = 2 if isinstance(self.left, Node) else 1 if self.left else 0
        right_type = 2 if isinstance(self.right, Node) else 1 if self.right else 0
        return self.print_node_rec_aux(left_type, right_type)
        
        # if self.symbol == 'if_then_else':
        #     condition, then_body, else_body = self.left
        #     return f"(if {condition.print_node_rec()} then {then_body.print_node_rec()} else {else_body.print_node_rec()})"
        # if self.symbol == 'while_loop':
        #     guard = self.left[0]
        #     body = self.left[1:]
        #     return f"while_loop({guard.print_node_rec()}, {self.printWhileLoopBody(body)})"
        # if (self.left is not None) and (self.right is not None):
        #     if isinstance(self.left, Node) and isinstance(self.right, Node):
        #         return self.print_node_rec_aux(2,2)
        #     elif isinstance(self.left, Node):
        #         return self.print_node_rec_aux(2,1)
        #     elif isinstance(self.right, Node):
        #         return self.print_node_rec_aux(1,2)
        #     else:
        #         return self.print_node_rec_aux(1, 1)
        # elif self.left is not None:
        #     if isinstance(self.left, Node):
        #         return self.print_node_rec_aux(2,0)
        #     else:
        #         return self.print_node_rec_aux(1,0)

    def subst(self, mapping):
        def apply_subst(node):
            return node.subst(mapping) if isinstance(node, Node) else node
        
        if self.symbol == TERMINAL_VARIABLES and self.left in mapping:
            return mapping[self.left]
        elif self.symbol == TERMINAL_IF_THEN_ELSE:
            condition, then_body, else_body = self.left
            return Node(TERMINAL_IF_THEN_ELSE, None, 
                        (apply_subst(condition), apply_subst(then_body), apply_subst(else_body)),
                        None, self.eval_type)
        else:
            return Node(self.symbol, self.op,
                        apply_subst(self.left), apply_subst(self.right), self.eval_type)
        # if self is None:
        #     return
        # if isinstance(self, Node):
        #     if self.symbol == "variables" and self.left in mapping:
        #         return mapping[self.left]
        #     elif self.symbol == "if_then_else":
        #         condition, then_body, else_body = self.left
        #         new_condition = condition.subst(mapping) if isinstance(condition, Node) else condition
        #         new_then = then_body.subst(mapping) if isinstance(then_body, Node) else then_body
        #         new_else = else_body.subst(mapping) if isinstance(else_body, Node) else else_body
        #         return Node("if_then_else", None, (new_condition, new_then, new_else), None, self.eval_type)
        #     else:
        #         if isinstance(self.left, Node) and isinstance(self.right, Node):
        #             return Node(self.symbol, self.op, self.left.subst(mapping), self.right.subst(mapping), self.eval_type)
        #         elif isinstance(self.left, Node):
        #             return Node(self.symbol, self.op, self.left.subst(mapping), self.right, self.eval_type)
        #         elif isinstance(self.right, Node):
        #             return Node(self.symbol, self.op, self.left, self.right.subst(mapping), self.eval_type)
        #         else:
        #             return Node(self.symbol, self.op, self.left, self.right, self.eval_type)

    def validate_implication(self, implication_left):
        if implication_left.eval_type != TERMINAL_BOOL:
            raise TypeError("Implication must be of type bool")
        if self.symbol != TERMINAL_ANNOTATION:
            raise ValueError("Implication can only be applied to an annotation")

    def add_implication(self, implication_left):
        self.validate_implication(implication_left)
        return Node(TERMINAL_ANNOTATION, "@", Node(TERMINAL_IMPLIES, "=>", implication_left, self.left, TERMINAL_BOOL), None, TERMINAL_BOOL)

