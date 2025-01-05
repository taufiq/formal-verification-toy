from enum import Enum



class InvalidExpressionType(Exception):
    def __init__(self, message="Invalid Expression Type"):
        super().__init__(message)

class Z3Serializer:
    @staticmethod
    def serialize(expression):
        serialize = Z3Serializer.serialize
        if isinstance(expression, BinaryExpression):
            if expression.op == "=>":
                return f"z3.Implies({serialize(expression.left)}, {serialize(expression.right)})"
            if expression.op == '^':
                return f"z3.And({serialize(expression.left)}, {serialize(expression.right)})"
            if expression.op == 'v':
                return f"z3.Or({serialize(expression.left)}, {serialize(expression.right)})"
            if expression.op in BINARY_OPERATOR_Z3_MAPPING:
                return f"({serialize(expression.left)} {BINARY_OPERATOR_Z3_MAPPING[expression.op]} {serialize(expression.right)})"
            else:
                return f"({serialize(expression.left)} {expression.op} {serialize(expression.right)})"
        elif isinstance(expression, NotExpression):
            return f"z3.Not({serialize(expression.expression)})"
        elif isinstance(expression, BooleanLiteralExpression):
            if expression.value == "TRUE":
                return f"True"
            elif expression.value == "FALSE":
                return "False"
        return str(expression)


def check_expression_type(expression, expected_type):
    if (isinstance(expression, IntUnaryExpression) \
    or isinstance(expression, IntBinaryExpression) \
    or isinstance(expression, IntLiteralExpression) \
    or (isinstance(expression, VariableExpression) and expression.type == DataType.INT) \
    or (isinstance(expression, ReturnValueVariableExpression))) \
    and (expected_type == DataType.INT):
        return True
    elif (isinstance(expression, BooleanUnaryExpression) \
    or isinstance(expression, BooleanBinaryExpression) \
    or isinstance(expression, BooleanLiteralExpression) \
    or (isinstance(expression, VariableExpression) and expression.type == DataType.BOOL) \
    or (isinstance(expression, ReturnValueVariableExpression))) \
    and expected_type == DataType.BOOL:
        return True
    else:
        return False

def assert_expression_type(expression, expected_type):
    if (isinstance(expression, IntUnaryExpression) \
    or isinstance(expression, IntBinaryExpression) \
    or isinstance(expression, IntLiteralExpression) \
    or (isinstance(expression, VariableExpression) and expression.type == DataType.INT) \
    or (isinstance(expression, ReturnValueVariableExpression))) \
    and (expected_type == DataType.INT):
        return True
    elif (isinstance(expression, BooleanUnaryExpression) \
    or isinstance(expression, BooleanBinaryExpression) \
    or isinstance(expression, BooleanLiteralExpression) \
    or (isinstance(expression, VariableExpression) and expression.type == DataType.BOOL) \
    or (isinstance(expression, ReturnValueVariableExpression))) \
    and expected_type == DataType.BOOL:
        return True
    else:
        raise InvalidExpressionType()

class Expression:
    def __init__(self):
        pass

                                    ###### BINARY EXPRESSIONS ######

class BinaryExpression:
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __repr__(self):
        if self.op in BINARY_OPERATOR_TEXT_MAPPING:
            return f"({self.left} {BINARY_OPERATOR_TEXT_MAPPING[self.op]} {self.right})"
        return f"({self.left} {self.op} {self.right})"

class IntBinaryExpression(BinaryExpression):
    def __init__(self, left, right, op):
        assert_expression_type(left, DataType.INT)
        assert_expression_type(right, DataType.INT)
        super().__init__(left, right, op)

class BooleanBinaryExpression(BinaryExpression):
    def __init__(self, left, right, op):
        super().__init__(left, right, op)

class ComparisonBinaryExpression(BooleanBinaryExpression):
    def __init__(self, left, right, op):
        if (check_expression_type(left, DataType.INT) and
            check_expression_type(right, DataType.INT)) or \
                (check_expression_type(left, DataType.BOOL) and
                 check_expression_type(right, DataType.BOOL)):
            super().__init__(left, right, op)
        else:
            raise InvalidExpressionType()

class ImpliesExpression(BooleanBinaryExpression):
    def __init__(self, left, right, op):
        assert_expression_type(left, DataType.BOOL)
        assert_expression_type(right, DataType.BOOL)
        super().__init__(left, right, op)

                                    ###### UNARY EXPRESSIONS ######
class UnaryExpression:
    def __init__(self, expression, op):
        self.expression = expression
        self.op = op
    
    def __repr__(self):
        return f"({self.op} {self.expression})"

class IntUnaryExpression(UnaryExpression):
    def __init__(self, expression, op):
        assert_expression_type(expression, DataType.INT)
        super().__init__(expression, op)

class BooleanUnaryExpression(UnaryExpression):
    def __init__(self, expression, op):
        assert_expression_type(expression, DataType.BOOL)
        super().__init__(expression, op)

class NotExpression(BooleanUnaryExpression):
    def __init__(self, expression,op="NOT"):
        super().__init__(expression, op)

    def __repr__(self):
        return f"(!{self.expression})"

class UnaryMinusExpression(IntUnaryExpression):
    def __init__(self, expression,op):
        super().__init__(expression, op)

    def __repr__(self):
        return f"(!{self.expression})"

                                ###### PARAMETERS & VARIABLES ######

class VariableExpression:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return self.name

class ReturnValueVariableExpression:
    def __init__(self):
        self.name = "rv"
        self.type = None

    def __repr__(self):
        return self.name

                ###### LITERAL EXPRESSION ######
class LiteralExpression:
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
        return str(self.value)

class BooleanLiteralExpression(LiteralExpression):
    def __init__(self, value):
        super().__init__(value, DataType.BOOL)

class IntLiteralExpression(LiteralExpression):
    def __init__(self, value):
        super().__init__(value, DataType.INT)

#
# class ImpliesBinaryExpression(BinaryExpression):
#     def __init__(self, left, right):
#         super().__init__(left, right, BinaryOperator.IMPLIES)

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

BINARY_OPERATOR_TEXT_MAPPING= {
    BinaryOperator.PLUS: "+",
    BinaryOperator.MINUS: "-",
    BinaryOperator.TIMES: "*",
    BinaryOperator.EQUALS: "==",
    BinaryOperator.LESS_THAN: "<",
    BinaryOperator.LESS_THAN_EQUALS: "<=",
    BinaryOperator.GREATER_THAN: ">",
    BinaryOperator.GREATER_THAN_EQUALS: ">=",
    BinaryOperator.AND: "^",
    BinaryOperator.OR: "v",
    BinaryOperator.IMPLIES: "=>",
}