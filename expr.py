from enum import Enum

class Z3Serializer:
    @staticmethod
    def serialize(expression):
        serialize = Z3Serializer.serialize
        if isinstance(expression, BinaryExpression):
            if expression.op == BinaryOperator.IMPLIES:
                return f"z3.Implies({serialize(expression.left)}, {serialize(expression.right)})"
            if expression.op == BinaryOperator.AND:
                return f"z3.And({serialize(expression.left)}, {serialize(expression.right)})"
            if expression.op == BinaryOperator.OR:
                return f"z3.Or({serialize(expression.left)}, {serialize(expression.right)})"
            if expression.op in BINARY_OPERATOR_Z3_MAPPING:
                return f"({serialize(expression.left)} {BINARY_OPERATOR_Z3_MAPPING[expression.op]} {serialize(expression.right)})"
            else:
                return f"({serialize(expression.left)} {expression.op} {serialize(expression.right)})"
        return str(expression)

class Expression:
    def __init__(self):
        pass

class NotExpression:
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"(!{self.expression})"

class BinaryExpression:
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __repr__(self):
        if self.op in BINARY_OPERATOR_Z3_MAPPING:
            return f"({self.left} {BINARY_OPERATOR_Z3_MAPPING[self.op]} {self.right})"
        return f"({self.left} {self.op} {self.right})"

class IntBinaryExpression(BinaryExpression):
    def __init__(self, left, right, op):
        super().__init__(left, right, op)

class BooleanBinaryExpression(BinaryExpression):
    def __init__(self, left, right, op):
        super().__init__(left, right, op)

class UnaryExpression:
    def __init__(self, expression, op):
        self.expression = expression
        self.op = op
    
    def __repr__(self):
        return f"({self.op} {self.expression})"

class ParameterDeclarationExpression:
    def __init__(self, variable, type):
        self.variable = variable

class LiteralExpression:
    def __init__(self, value, type):
        self.value = value
        self.type = type
    
    def __repr__(self):
        return str(self.value)

class VariableExpression:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return self.name

class BooleanLiteralExpression(LiteralExpression):
    def __init__(self, value):
        super().__init__(value, DataType.BOOL)

class IntLiteralExpression(LiteralExpression):
    def __init__(self, value):
        super().__init__(value, DataType.INT)

class ComparisonBinaryExpression(BinaryExpression):
    def __init__(self, left, right, op):
        super().__init__(left, right, op)

class DataType(Enum):
    INT = 0
    BOOL = 1

class BinaryOperator(Enum):
    PLUS = 0
    MINUS = 1
    TIMES = 2
    EQUALS = 4
    NOT_EQUALS = 5
    LESS_THAN = 6
    LESS_THAN_EQUALS = 7
    GREATER_THAN = 8
    GREATER_THAN_EQUALS = 9
    AND = 10
    OR = 11
    IMPLIES = 12

BINARY_OPERATOR_Z3_MAPPING= {
    BinaryOperator.PLUS: "+",
    BinaryOperator.MINUS: "-",
    BinaryOperator.TIMES: "*",
    BinaryOperator.EQUALS: "==",
    BinaryOperator.LESS_THAN: "<",
    BinaryOperator.LESS_THAN_EQUALS: "<=",
    BinaryOperator.GREATER_THAN: ">",
    BinaryOperator.GREATER_THAN_EQUALS: ">=",
    BinaryOperator.AND: "z3.And",
    BinaryOperator.OR: "z3.Or",
    BinaryOperator.IMPLIES: "z3.Implies",
}