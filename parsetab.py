
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ANNOTATION ASSIGNMENT BOOLEAN_OPERATOR COMPARATOR DIVIDE FALSE LPAREN MINUS NUMBER PLUS RPAREN TIMES TRUE TRUTH_VALUES VARIABLEstatement : annotationstatement : assignmentstatement : expressionannotation : ANNOTATION expressionassignment : VARIABLE ASSIGNMENT expressionexpression : expression COMPARATOR termexpression : expression BOOLEAN_OPERATOR termterm : VARIABLEexpression : expression PLUS expressionexpression : expression MINUS termexpression : termterm : term TIMES factorterm : TRUEterm : term DIVIDE factorterm : factorfactor : NUMBERfactor : LPAREN expression RPAREN'
    
_lr_action_items = {'ANNOTATION':([0,],[5,]),'VARIABLE':([0,5,11,12,13,14,15,18,],[6,17,17,17,17,17,17,17,]),'TRUE':([0,5,11,12,13,14,15,18,],[9,9,9,9,9,9,9,9,]),'NUMBER':([0,5,11,12,13,14,15,18,19,20,],[10,10,10,10,10,10,10,10,10,10,]),'LPAREN':([0,5,11,12,13,14,15,18,19,20,],[11,11,11,11,11,11,11,11,11,11,]),'$end':([1,2,3,4,6,7,8,9,10,16,17,22,23,24,25,26,27,28,29,],[0,-1,-2,-3,-8,-11,-15,-13,-16,-4,-8,-6,-7,-9,-10,-5,-12,-14,-17,]),'COMPARATOR':([4,6,7,8,9,10,16,17,21,22,23,24,25,26,27,28,29,],[12,-8,-11,-15,-13,-16,12,-8,12,-6,-7,12,-10,12,-12,-14,-17,]),'BOOLEAN_OPERATOR':([4,6,7,8,9,10,16,17,21,22,23,24,25,26,27,28,29,],[13,-8,-11,-15,-13,-16,13,-8,13,-6,-7,13,-10,13,-12,-14,-17,]),'PLUS':([4,6,7,8,9,10,16,17,21,22,23,24,25,26,27,28,29,],[14,-8,-11,-15,-13,-16,14,-8,14,-6,-7,14,-10,14,-12,-14,-17,]),'MINUS':([4,6,7,8,9,10,16,17,21,22,23,24,25,26,27,28,29,],[15,-8,-11,-15,-13,-16,15,-8,15,-6,-7,15,-10,15,-12,-14,-17,]),'ASSIGNMENT':([6,],[18,]),'TIMES':([6,7,8,9,10,17,22,23,25,27,28,29,],[-8,19,-15,-13,-16,-8,19,19,19,-12,-14,-17,]),'DIVIDE':([6,7,8,9,10,17,22,23,25,27,28,29,],[-8,20,-15,-13,-16,-8,20,20,20,-12,-14,-17,]),'RPAREN':([7,8,9,10,17,21,22,23,24,25,27,28,29,],[-11,-15,-13,-16,-8,29,-6,-7,-9,-10,-12,-14,-17,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'statement':([0,],[1,]),'annotation':([0,],[2,]),'assignment':([0,],[3,]),'expression':([0,5,11,14,18,],[4,16,21,24,26,]),'term':([0,5,11,12,13,14,15,18,],[7,7,7,22,23,7,25,7,]),'factor':([0,5,11,12,13,14,15,18,19,20,],[8,8,8,8,8,8,8,8,27,28,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> statement","S'",1,None,None,None),
  ('statement -> annotation','statement',1,'p_statement_annotation','parser.py',5),
  ('statement -> assignment','statement',1,'p_statement_assignment','parser.py',9),
  ('statement -> expression','statement',1,'p_statement_expression','parser.py',13),
  ('annotation -> ANNOTATION expression','annotation',2,'p_annotation','parser.py',17),
  ('assignment -> VARIABLE ASSIGNMENT expression','assignment',3,'p_assignment','parser.py',21),
  ('expression -> expression COMPARATOR term','expression',3,'p_comparison','parser.py',25),
  ('expression -> expression BOOLEAN_OPERATOR term','expression',3,'p_logic_op','parser.py',29),
  ('term -> VARIABLE','term',1,'p_term_variable','parser.py',33),
  ('expression -> expression PLUS expression','expression',3,'p_expression_plus','parser.py',37),
  ('expression -> expression MINUS term','expression',3,'p_expression_minus','parser.py',41),
  ('expression -> term','expression',1,'p_expression_term','parser.py',45),
  ('term -> term TIMES factor','term',3,'p_term_times','parser.py',49),
  ('term -> TRUE','term',1,'p_term_boolean','parser.py',53),
  ('term -> term DIVIDE factor','term',3,'p_term_div','parser.py',57),
  ('term -> factor','term',1,'p_term_factor','parser.py',61),
  ('factor -> NUMBER','factor',1,'p_factor_num','parser.py',65),
  ('factor -> LPAREN expression RPAREN','factor',3,'p_factor_expr','parser.py',69),
]
