from typing import List

from Node import Node



class Basic_path:
    def __init__(self, precondition:Node, body:List[Node], post_condition:Node, generated_by, index:int):
        self.precondition = precondition
        self.body = body
        self.post_condition = post_condition
        self.generated_by = generated_by
        self.index = index


