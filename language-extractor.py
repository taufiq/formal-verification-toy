import inspect
import parser 

# Generated with GPT-4o

def extract_grammar():
    """Extract grammar rules from parser functions."""
    rules = []
    for name, obj in inspect.getmembers(parser):
        if inspect.isfunction(obj) and name.startswith('p_'):
            doc = obj.__doc__ or ""
            rules.append(doc.strip())
    return rules

def pretty_print_grammar(rules):
    """Pretty-print grammar rules."""
    print("Language Grammar:")
    print("-" * 40)
    for rule in rules:
        print(rule)
    print("-" * 40)

def save_grammar_to_file(rules, filename="grammar.txt"):
    """Save grammar rules to a file."""
    with open(filename, "w") as f:
        for rule in rules:
            f.write(rule + "\n")

# Main logic
if __name__ == "__main__":
    grammar_rules = extract_grammar()
    pretty_print_grammar(grammar_rules)
    save_grammar_to_file(grammar_rules)
