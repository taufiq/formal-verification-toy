
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'nonassocCOMPARATORleftBOOLEAN_OPERATORleftPLUSMINUSleftTIMESrightUMINUSANNOTATION ASSIGNMENT BOOLEAN_OPERATOR BOOL_TYPE COMPARATOR ELSE IF IMPLIES INT_TYPE LPAREN MINUS NUMBER PLUS RPAREN THEN TIMES VARIABLEstart : assignment\n             | expression\n             | annotation\n             | formula\n             | declarationdeclaration : BOOL_TYPE VARIABLEdeclaration : INT_TYPE VARIABLEannotation : ANNOTATION formulaassignment : VARIABLE ASSIGNMENT expressionexpression : expression PLUS expressionexpression : expression MINUS expressionexpression : expression TIMES expressionexpression : LPAREN expression RPARENexpression : NUMBERexpression : VARIABLEexpression : MINUS expression %prec UMINUSformula : expression COMPARATOR expressionformula : formula BOOLEAN_OPERATOR formulaformula : VARIABLEformula : LPAREN formula RPARENformula : formula IMPLIES formulaformula : IF formula THEN assignment ELSE assignment'
    
_lr_action_items = {'VARIABLE':([0,8,9,11,12,13,14,15,16,17,18,19,20,21,23,31,46,49,],[7,24,27,30,30,33,34,24,24,24,24,30,30,24,24,30,48,48,]),'LPAREN':([0,8,9,11,12,15,16,17,18,19,20,21,23,31,],[9,23,9,31,31,23,23,23,23,31,31,23,23,31,]),'NUMBER':([0,8,9,11,12,15,16,17,18,19,20,21,23,31,],[10,10,10,10,10,10,10,10,10,10,10,10,10,10,]),'MINUS':([0,3,7,8,9,10,11,12,15,16,17,18,19,20,21,22,23,24,25,27,29,30,31,35,36,37,38,41,42,43,45,],[8,16,-15,8,8,-14,8,8,8,8,8,8,8,8,8,-16,8,-15,16,-15,16,-15,8,-10,-11,-12,16,16,16,-13,16,]),'ANNOTATION':([0,],[11,]),'IF':([0,9,11,12,19,20,31,],[12,12,12,12,12,12,12,]),'BOOL_TYPE':([0,],[13,]),'INT_TYPE':([0,],[14,]),'$end':([1,2,3,4,5,6,7,10,22,24,28,30,33,34,35,36,37,38,39,40,41,43,44,50,],[0,-1,-2,-3,-4,-5,-15,-14,-16,-15,-8,-19,-6,-7,-10,-11,-12,-17,-18,-21,-9,-13,-20,-22,]),'PLUS':([3,7,10,22,24,25,27,29,30,35,36,37,38,41,42,43,45,],[15,-15,-14,-16,-15,15,-15,15,-15,-10,-11,-12,15,15,15,-13,15,]),'TIMES':([3,7,10,22,24,25,27,29,30,35,36,37,38,41,42,43,45,],[17,-15,-14,-16,-15,17,-15,17,-15,17,17,-12,17,17,17,-13,17,]),'COMPARATOR':([3,7,10,22,24,25,27,29,30,35,36,37,43,45,],[18,-15,-14,-16,-15,18,-15,18,-15,-10,-11,-12,-13,18,]),'BOOLEAN_OPERATOR':([5,7,10,22,24,26,27,28,30,32,35,36,37,38,39,40,41,43,44,50,],[19,-19,-14,-16,-15,19,-19,19,-19,19,-10,-11,-12,-17,-18,19,-9,-13,-20,-22,]),'IMPLIES':([5,7,10,22,24,26,27,28,30,32,35,36,37,38,39,40,41,43,44,50,],[20,-19,-14,-16,-15,20,-19,20,-19,20,-10,-11,-12,-17,-18,20,-9,-13,-20,-22,]),'ASSIGNMENT':([7,48,],[21,21,]),'RPAREN':([10,22,24,25,26,27,30,35,36,37,38,39,40,41,42,43,44,45,50,],[-14,-16,-15,43,44,-15,-15,-10,-11,-12,-17,-18,-21,-9,43,-13,-20,43,-22,]),'THEN':([10,22,24,30,32,35,36,37,38,39,40,41,43,44,50,],[-14,-16,-15,-19,46,-10,-11,-12,-17,-18,-21,-9,-13,-20,-22,]),'ELSE':([10,22,24,35,36,37,41,43,47,],[-14,-16,-15,-10,-11,-12,-9,-13,49,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'start':([0,],[1,]),'assignment':([0,46,49,],[2,47,50,]),'expression':([0,8,9,11,12,15,16,17,18,19,20,21,23,31,],[3,22,25,29,29,35,36,37,38,29,29,41,42,45,]),'annotation':([0,],[4,]),'formula':([0,9,11,12,19,20,31,],[5,26,28,32,39,40,26,]),'declaration':([0,],[6,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> start","S'",1,None,None,None),
  ('start -> assignment','start',1,'p_start','parser.py',45),
  ('start -> expression','start',1,'p_start','parser.py',46),
  ('start -> annotation','start',1,'p_start','parser.py',47),
  ('start -> formula','start',1,'p_start','parser.py',48),
  ('start -> declaration','start',1,'p_start','parser.py',49),
  ('declaration -> BOOL_TYPE VARIABLE','declaration',2,'p_bool_declaration','parser.py',54),
  ('declaration -> INT_TYPE VARIABLE','declaration',2,'p_int_declaration','parser.py',62),
  ('annotation -> ANNOTATION formula','annotation',2,'p_annotation','parser.py',71),
  ('assignment -> VARIABLE ASSIGNMENT expression','assignment',3,'p_assignment','parser.py',76),
  ('expression -> expression PLUS expression','expression',3,'p_expression_plus','parser.py',81),
  ('expression -> expression MINUS expression','expression',3,'p_expression_minus','parser.py',85),
  ('expression -> expression TIMES expression','expression',3,'p_expression_times','parser.py',89),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_parenthesis_expr','parser.py',93),
  ('expression -> NUMBER','expression',1,'p_expression_num','parser.py',97),
  ('expression -> VARIABLE','expression',1,'p_expression_variable','parser.py',101),
  ('expression -> MINUS expression','expression',2,'p_expr_uminus','parser.py',108),
  ('formula -> expression COMPARATOR expression','formula',3,'p_formula_comparison','parser.py',113),
  ('formula -> formula BOOLEAN_OPERATOR formula','formula',3,'p_formula_logic_op','parser.py',117),
  ('formula -> VARIABLE','formula',1,'p_formula_variable','parser.py',121),
  ('formula -> LPAREN formula RPAREN','formula',3,'p_formula_expr','parser.py',128),
  ('formula -> formula IMPLIES formula','formula',3,'p_formula_implies','parser.py',132),
  ('formula -> IF formula THEN assignment ELSE assignment','formula',6,'p_if_then_else','parser.py',136),
]
