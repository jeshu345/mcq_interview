import json
import random
from datetime import datetime
from faker import Faker

fake = Faker()

def generate_python_mcqs(num_questions=1000):
    questions = []
    topics = [
        "Data Types", "Control Structures", "Functions", 
        "OOP", "Modules", "Error Handling", "File Handling",
        "Comprehensions", "Built-in Functions", "Decorators"
    ]
    
    for q_id in range(1, num_questions + 1):
        topic = random.choice(topics)
        difficulty = random.choice(["Easy", "Medium", "Hard"])
        
        # Generate different question types based on topic
        if topic == "Data Types":
            question, options, answer = generate_data_type_question()
        elif topic == "Control Structures":
            question, options, answer = generate_control_flow_question()
        elif topic == "Functions":
            question, options, answer = generate_function_question()
        elif topic == "OOP":
            question, options, answer = generate_oop_question()
        elif topic == "Modules":
            question, options, answer = generate_module_question()
        elif topic == "Error Handling":
            question, options, answer = generate_error_handling_question()
        elif topic == "File Handling":
            question, options, answer = generate_file_handling_question()
        elif topic == "Comprehensions":
            question, options, answer = generate_comprehension_question()
        elif topic == "Built-in Functions":
            question, options, answer = generate_builtin_function_question()
        else:  # Decorators
            question, options, answer = generate_decorator_question()
        
        questions.append({
            "id": q_id,
            "question": question,
            "options": options,
            "answer": answer,
            "topic": topic,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat()
        })
    
    return questions

# Question generators for each topic
def generate_data_type_question():
    data_types = {
        "list": "Mutable, ordered collection",
        "tuple": "Immutable, ordered collection",
        "dict": "Key-value pairs, mutable",
        "set": "Unordered, unique elements",
        "frozenset": "Immutable set",
        "str": "Immutable sequence of characters",
        "bytes": "Immutable sequence of bytes",
        "bytearray": "Mutable sequence of bytes",
        "int": "Integer number",
        "float": "Floating point number",
        "complex": "Complex number",
        "bool": "Boolean value"
    }
    
    question_types = [
        ("Which Python data type is immutable and ordered?", ["tuple"], list(data_types.keys())),
        ("Which data type is mutable and unordered?", ["set"], list(data_types.keys())),
        ("Which of these is NOT a built-in data type?", ["array"], list(data_types.keys()) + ["array"]),
        ("What is the data type of (1, 2, 3)?", ["tuple"], list(data_types.keys())),
        ("Which data type uses key-value pairs?", ["dict"], list(data_types.keys()))
    ]
    
    q_text, correct, options_pool = random.choice(question_types)
    options = random.sample(options_pool, 4)
    if correct[0] not in options:
        options[0] = correct[0]
    random.shuffle(options)
    answer = chr(65 + options.index(correct[0]))
    
    return q_text, [f"{chr(65+i)}: {opt}" for i, opt in enumerate(options)], answer

def generate_control_flow_question():
    questions = [
        ("What does the 'pass' statement do in Python?", 
         ["Acts as a placeholder", "Terminates the loop", "Skips current iteration", "Raises an exception"],
         "A"),
        ("Which loop is used for iterating over a sequence?", 
         ["for loop", "while loop", "do-while loop", "repeat-until loop"],
         "A"),
        ("What is the purpose of the 'else' clause in a loop?", 
         ["Executes after loop completes normally", "Executes when loop is broken", "Handles exceptions", "Initializes loop variables"],
         "A"),
        ("Which keyword is used to skip to the next iteration?", 
         ["continue", "break", "pass", "skip"],
         "A"),
        ("What does the 'break' statement do?", 
         ["Terminates the loop", "Skips current iteration", "Restarts the loop", "Exits the program"],
         "A")
    ]
    return random.choice(questions)

def generate_function_question():
    questions = [
        ("What keyword defines a function in Python?", 
         ["def", "function", "define", "func"],
         "A"),
        ("Which of these is a valid function parameter marker?", 
         ["*args", "&args", "#args", "@args"],
         "A"),
        ("What does the 'return' statement do?", 
         ["Exits function and returns value", "Prints value to console", "Terminates program", "Continues function execution"],
         "A"),
        ("What is a lambda function?", 
         ["Anonymous function", "Recursive function", "Generator function", "Decorator function"],
         "A"),
        ("Which scope do variables defined in a function have by default?", 
         ["Local", "Global", "Module", "Built-in"],
         "A")
    ]
    return random.choice(questions)

def generate_oop_question():
    questions = [
        ("Which method is called automatically when an object is created?", 
         ["__init__", "__del__", "__str__", "__main__"],
         "A"),
        ("What is inheritance in OOP?", 
         ["Deriving new class from existing", "Hiding implementation details", "Bundling data with methods", "Multiple names for same method"],
         "A"),
        ("What is encapsulation?", 
         ["Bundling data with methods", "Deriving new classes", "Multiple inheritance", "Operator overloading"],
         "A"),
        ("Which decorator is used for class methods?", 
         ["@classmethod", "@staticmethod", "@method", "@classfunc"],
         "A"),
        ("What is polymorphism?", 
         ["Same interface for different types", "Hiding implementation", "Data bundling", "Class inheritance"],
         "A")
    ]
    return random.choice(questions)

def generate_module_question():
    modules = ["math", "os", "sys", "datetime", "json", "random", "re", "csv"]
    question_types = [
        (f"Which module provides mathematical functions?", ["math"], modules),
        (f"Which module handles file system operations?", ["os"], modules),
        (f"Which module is used for regular expressions?", ["re"], modules),
        (f"Which module handles JSON data?", ["json"], modules),
        (f"Which module provides system-specific parameters?", ["sys"], modules)
    ]
    
    q_text, correct, options_pool = random.choice(question_types)
    options = random.sample(options_pool, 4)
    if correct[0] not in options:
        options[0] = correct[0]
    random.shuffle(options)
    answer = chr(65 + options.index(correct[0]))
    
    return q_text, [f"{chr(65+i)}: {opt}" for i, opt in enumerate(options)], answer

def generate_error_handling_question():
    questions = [
        ("What is the purpose of try-except blocks?", 
         ["Handle exceptions", "Prevent errors", "Improve performance", "Validate inputs"],
         "A"),
        ("Which keyword raises an exception?", 
         ["raise", "throw", "except", "catch"],
         "A"),
        ("What does the 'finally' block do?", 
         ["Always executes", "Handles exceptions", "Cleans resources", "Tests code"],
         "A"),
        ("What is the base class for all exceptions?", 
         ["BaseException", "Exception", "Error", "Throwable"],
         "A"),
        ("Which exception is raised for division by zero?", 
         ["ZeroDivisionError", "ArithmeticError", "ValueError", "MathError"],
         "A")
    ]
    return random.choice(questions)

def generate_file_handling_question():
    modes = ["r", "w", "a", "rb", "wb", "ab", "r+", "w+", "a+"]
    question_types = [
        ("Which mode opens a file for reading?", ["r"], modes),
        ("Which mode truncates the file when opening?", ["w"], modes),
        ("Which mode appends to a file?", ["a"], modes),
        ("Which mode opens a file for binary writing?", ["wb"], modes),
        ("Which mode allows both reading and writing?", ["r+"], modes)
    ]
    
    q_text, correct, options_pool = random.choice(question_types)
    options = random.sample(options_pool, 4)
    if correct[0] not in options:
        options[0] = correct[0]
    random.shuffle(options)
    answer = chr(65 + options.index(correct[0]))
    
    return q_text, [f"{chr(65+i)}: {opt}" for i, opt in enumerate(options)], answer

def generate_comprehension_question():
    questions = [
        ("What is a list comprehension?", 
         ["Concise way to create lists", "Function that lists items", "Loop structure", "Data type"],
         "A"),
        ("Which is the correct dictionary comprehension?", 
         ["{k: v for k, v in iterable}", "[k: v for k, v in iterable]", "(k: v for k, v in iterable)", "{k, v for k, v in iterable}"],
         "A"),
        ("What does this do: [x**2 for x in range(5)]?", 
         ["Creates [0, 1, 4, 9, 16]", "Creates [1, 4, 9, 16, 25]", "Squares 5", "Raises error"],
         "A"),
        ("Which comprehension creates a generator?", 
         ["(x for x in iterable)", "[x for x in iterable]", "{x for x in iterable}", "{x: x for x in iterable}"],
         "A"),
        ("What is the main advantage of comprehensions?", 
         ["Concise and readable", "Faster execution", "Lower memory usage", "Better error handling"],
         "A")
    ]
    return random.choice(questions)

def generate_builtin_function_question():
    functions = ["len()", "type()", "str()", "int()", "float()", "list()", 
                "dict()", "set()", "range()", "input()", "print()", "sum()",
                "min()", "max()", "sorted()", "enumerate()", "zip()", "map()"]
    
    question_types = [
        ("Which function returns the number of items in an object?", ["len()"], functions),
        ("Which function converts a value to a string?", ["str()"], functions),
        ("Which function creates a sequence of numbers?", ["range()"], functions),
        ("Which function returns the largest item?", ["max()"], functions),
        ("Which function pairs elements from iterables?", ["zip()"], functions)
    ]
    
    q_text, correct, options_pool = random.choice(question_types)
    options = random.sample(options_pool, 4)
    if correct[0] not in options:
        options[0] = correct[0]
    random.shuffle(options)
    answer = chr(65 + options.index(correct[0]))
    
    return q_text, [f"{chr(65+i)}: {opt}" for i, opt in enumerate(options)], answer

def generate_decorator_question():
    questions = [
        ("What is a decorator in Python?", 
         ["Function that modifies another function", "Special class method", "Function decorator pattern", "Syntax for comments"],
         "A"),
        ("Which symbol is used for decorators?", 
         ["@", "#", "$", "%"],
         "A"),
        ("What is the main purpose of decorators?", 
         ["Extend function behavior", "Create functions", "Handle errors", "Improve performance"],
         "A"),
        ("Can decorators take arguments?", 
         ["Yes", "No", "Only in classes", "Only for methods"],
         "A"),
        ("Which decorator marks a static method?", 
         ["@staticmethod", "@classmethod", "@property", "@abstractmethod"],
         "A")
    ]
    return random.choice(questions)

if __name__ == "__main__":
    # Generate 1000 questions
    mcqs = generate_python_mcqs(1000)
    
    # Save to JSON file
    with open("python_mcqs.json", "w") as f:
        json.dump(mcqs, f, indent=2)
    
    print("✅ Generated 1000 Python MCQs in python_mcqs.json")
    print("📁 File is ready for MySQL import")