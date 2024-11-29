

class Node:
    def __init__(self,symbol,op,left,right):
        self.left = left
        self.right = right
        self.op = op
        self.symbol = symbol

    def print_node_rec(self):
        if (self.left is not None) and (self.right is not None):
            if isinstance(self.left, Node) and isinstance(self.right, Node):
                return "(" + self.symbol + "," + self.left.print_node_rec() + " " + self.right.print_node_rec() + ")"
            elif isinstance(self.left, Node):
                return "(" + self.symbol + "," + self.left.print_node_rec() + " " + str(self.right) + ")"
            elif isinstance(self.right, Node):
                return "(" + self.symbol + "," + str(self.left) + " " + self.right.print_node_rec() + ")"
            else:
                return "(" + self.symbol + "," + str(self.left)  + " " + str(self.right) + ")"
        elif self.left is not None:
            if isinstance(self.left, Node):
                return "(" + self.symbol + "," + self.left.print_node_rec() + ")"
            else:
                return "(" + self.symbol + "," + str(self.left) + ")"

    def subst(self, mapping):
        if self is None:
            return
        if isinstance(self, Node):
            if self.symbol == "variables" and self.left in mapping:
                return mapping[self.left]
            else:
                if isinstance(self.left, Node) and isinstance(self.right, Node):
                    return Node(self.symbol, self.op, self.left.subst(mapping), self.right.subst(mapping))
                elif isinstance(self.left, Node):
                    return Node(self.symbol, self.op, self.left.subst(mapping), self.right)
                elif isinstance(self.right, Node):
                    return Node(self.symbol, self.op, self.left, self.right.subst(mapping))
                else:
                    return Node(self.symbol, self.op, self.left, self.right)


