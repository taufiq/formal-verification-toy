from abc import abstractmethod

from expr import BooleanUnaryExpression, BooleanBinaryExpression, BooleanLiteralExpression, IntUnaryExpression, \
    IntBinaryExpression, IntLiteralExpression


class Statement:
    def __init__(self):
        self.context = None

class AssignmentStatement(Statement):
    def __init__(self, variable, expression):
        super().__init__()
        self.variable = variable
        self.expression = expression

class BooleanAssignmentStatement(AssignmentStatement):
    def __init__(self, variable, expression):
        super().__init__(variable, expression)
    
    def __repr__(self):
        return f"Boolean Assignment: {self.variable} = {self.expression}"

class IntAssignmentStatement(AssignmentStatement):
    def __init__(self, variable, expression):
        super().__init__(variable, expression)
    
    def __repr__(self):
        return f"Int Assignment: {self.variable} = {self.expression}"

class WhileLoopStatement(Statement):
    def __init__(self, condition, body, invariant=None):
        super().__init__()
        assert (isinstance(condition, BooleanUnaryExpression) or isinstance(condition, BooleanBinaryExpression))
        self.condition = condition
        self.body = body
        self.invariant = invariant

    def is_last_statement(self, statement):
        if self.body == []:
            return True
        return self.body[-1] == statement

class ForStatement(Statement):
    def __init__(self, initial_statement, condition, increment_statement, body):
        super().__init__()
        self.initial_statement = initial_statement
        self.condition = condition
        self.increment_statement = increment_statement
        self.body = body

class IfThenElseStatement(Statement):
    def __init__(self, condition, then_body, else_body):
        super().__init__()
        assert (isinstance(condition, BooleanUnaryExpression) or isinstance(condition, BooleanBinaryExpression))
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def __repr__(self):
        return f"IF ({self.condition}) THEN {self.then_body} ELSE {self.else_body}"


class FunctionDeclarationStatement(Statement):
    def __init__(self, function_name, parameter_list, body):
        super().__init__()
        self.function_name = function_name
        self.parameter_list = parameter_list
        self.body = body

    def __repr__(self):
        return f"FUNCTION {self.function_name} ({', '.join(self.parameter_list)}) {{ {self.body} }}"

    @abstractmethod
    def check_valid_return_statement(self, return_statement):
        pass

class ReturnStatement(Statement):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def __repr__(self):
        return f"RETURN {self.expression}"


class IntFunctionDeclarationStatement(FunctionDeclarationStatement):
    def __init__(self, function_name, parameter_list, body):
        super().__init__(function_name, parameter_list, body)

    def __repr__(self):
        return f"INT FUNCTION {self.function_name} ({', '.join(self.parameter_list)}) {{ {self.body} }}"

    def check_valid_return_statement(self, return_statement: ReturnStatement):
        return isinstance(return_statement.expression, IntUnaryExpression) \
        or isinstance(return_statement.expression, IntBinaryExpression) \
        or isinstance(return_statement.expression, IntLiteralExpression)

class BoolFunctionDeclarationStatement(FunctionDeclarationStatement):
    def __init__(self, function_name, parameter_list, body):
        super().__init__(function_name, parameter_list, body)

    def __repr__(self):
        return f"BOOL FUNCTION {self.function_name} ({', '.join(self.parameter_list)}) {{ {self.body} }}"

    def check_valid_return_statement(self, return_statement: ReturnStatement):
        return isinstance(return_statement.expression, BooleanUnaryExpression) \
        or isinstance(return_statement.expression, BooleanBinaryExpression) \
        or isinstance(return_statement.expression, BooleanLiteralExpression)



class AnnotationStatement(Statement):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression
    
    def __repr__(self):
        return f"@{self.expression}"

class PreAnnotationStatement(AnnotationStatement):
    def __init__(self, expression):
        super().__init__(expression)
    
    def __repr__(self):
        return f"@Pre {self.expression}"

class PostAnnotationStatement(AnnotationStatement):
    def __init__(self, expression):
        super().__init__(expression)
    
    def __repr__(self):
        return f"@Post {self.expression}"

class LoopAnnotationStatement(AnnotationStatement):
    def __init__(self, expression):
        super().__init__(expression)
    
    def __repr__(self):
        return f"@Loop {self.expression}"

class AssumptionStatement(Statement):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def __repr__(self):
        return f"ASSUME {self.expression}"

class DeclarationStatement(Statement):
    def __init__(self, variable, type):
        super().__init__()
        self.variable = variable
        self.type = type

    def __repr__(self):
        return f"Variable Declaration: {self.type} {self.variable}"

class BooleanDeclarationStatement(DeclarationStatement):
    def __init__(self, variable):
        super().__init__(variable, "bool")

class IntDeclarationStatement(DeclarationStatement):
    def __init__(self, variable):
        super().__init__(variable, "int")

class Program:
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return "\n".join(str(statement) for statement in self.statements)
