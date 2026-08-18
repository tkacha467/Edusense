"""Domain-specific question dataset bank for EduSense AI RAG Question Engine."""
from typing import Dict, Any, List

DOMAIN_QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    # BCA Subjects
    "Programming in C & C++": [
        {
            "question_text": "What occurs when a dynamically allocated pointer in C++ created with 'new' is not freed using 'delete'?",
            "question_type": "MCQ",
            "difficulty_level": "MEDIUM",
            "marks": 1.0,
            "correct_answer": "B",
            "explanation": "Failing to release dynamically allocated memory results in a memory leak, consuming heap memory unnecessarily.",
            "hint": "Think about unused heap memory that remains unreferenced.",
            "options": [
                {"option_label": "A", "option_text": "Stack overflow error"},
                {"option_label": "B", "option_text": "Memory leak on heap"},
                {"option_label": "C", "option_text": "Automatic garbage collection"},
                {"option_label": "D", "option_text": "Compilation syntax error"}
            ]
        },
        {
            "question_text": "Which feature of C++ allows a function name to have multiple implementations based on argument types?",
            "question_type": "MCQ",
            "difficulty_level": "EASY",
            "marks": 1.0,
            "correct_answer": "A",
            "explanation": "Function overloading allows multiple functions in the same scope to share the same name with different parameters.",
            "hint": "It is a compile-time form of polymorphism.",
            "options": [
                {"option_label": "A", "option_text": "Function Overloading"},
                {"option_label": "B", "option_text": "Function Overriding"},
                {"option_label": "C", "option_text": "Virtual Method Dispatch"},
                {"option_label": "D", "option_text": "Friend Functions"}
            ]
        }
    ],
    "Data Structures & Algorithms": [
        {
            "question_text": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree (BST)?",
            "question_type": "MCQ",
            "difficulty_level": "MEDIUM",
            "marks": 1.0,
            "correct_answer": "C",
            "explanation": "In an unbalanced BST (degenerate tree), operations degrade to linear time complexity O(N), equivalent to a linked list.",
            "hint": "Consider a tree that degenerates into a single long chain.",
            "options": [
                {"option_label": "A", "option_text": "O(1)"},
                {"option_label": "B", "option_text": "O(log N)"},
                {"option_label": "C", "option_text": "O(N)"},
                {"option_label": "D", "option_text": "O(N log N)"}
            ]
        },
        {
            "question_text": "Which data structure follows the Last-In, First-Out (LIFO) operational principle?",
            "question_type": "MCQ",
            "difficulty_level": "EASY",
            "marks": 1.0,
            "correct_answer": "B",
            "explanation": "A Stack processes data in Last-In, First-Out (LIFO) order, where the last added element is popped first.",
            "hint": "Think of a stack of dinner plates.",
            "options": [
                {"option_label": "A", "option_text": "Queue"},
                {"option_label": "B", "option_text": "Stack"},
                {"option_label": "C", "option_text": "Heap"},
                {"option_label": "D", "option_text": "Graph"}
            ]
        }
    ],
    "Database Management Systems (DBMS)": [
        {
            "question_text": "Which database normalization form eliminates partial dependencies where non-prime attributes depend on part of a composite primary key?",
            "question_type": "MCQ",
            "difficulty_level": "HARD",
            "marks": 1.0,
            "correct_answer": "B",
            "explanation": "Second Normal Form (2NF) requires a relation to be in 1NF and have no partial functional dependencies.",
            "hint": "It comes immediately after removing repeating groups in 1NF.",
            "options": [
                {"option_label": "A", "option_text": "First Normal Form (1NF)"},
                {"option_label": "B", "option_text": "Second Normal Form (2NF)"},
                {"option_label": "C", "option_text": "Third Normal Form (3NF)"},
                {"option_label": "D", "option_text": "Boyce-Codd Normal Form (BCNF)"}
            ]
        }
    ],

    # MCA & Enterprise AI Subjects
    "Advanced Java & Enterprise Apps": [
        {
            "question_text": "In Spring Boot, which annotation is used to auto-inject dependency beans into a component constructor or field?",
            "question_type": "MCQ",
            "difficulty_level": "MEDIUM",
            "marks": 1.0,
            "correct_answer": "A",
            "explanation": "@Autowired marks a constructor, field, or setter method to be injected automatically by Spring IoC container.",
            "hint": "It tells Spring to automatically wire the bean.",
            "options": [
                {"option_label": "A", "option_text": "@Autowired"},
                {"option_label": "B", "option_text": "@InjectBean"},
                {"option_label": "C", "option_text": "@Component"},
                {"option_label": "D", "option_text": "@Service"}
            ]
        }
    ],
    "Artificial Intelligence & Expert Systems": [
        {
            "question_text": "In Logistic Regression, what is the output range of the Sigmoid activation function $\\sigma(z) = \\frac{1}{1 + e^{-z}}$?",
            "question_type": "MCQ",
            "difficulty_level": "MEDIUM",
            "marks": 1.0,
            "correct_answer": "C",
            "explanation": "The Sigmoid function squashes any real-valued input into a probability range between 0.0 and 1.0.",
            "hint": "Probabilities are bounded between zero and one.",
            "options": [
                {"option_label": "A", "option_text": "[-1.0, 1.0]"},
                {"option_label": "B", "option_text": "[0.0, infinity)"},
                {"option_label": "C", "option_text": "(0.0, 1.0)"},
                {"option_label": "D", "option_text": "[-infinity, +infinity]"}
            ]
        }
    ],

    # M.Sc. Data Science Subjects
    "Machine Learning & Pattern Recognition": [
        {
            "question_text": "What metric does a Random Forest Decision Tree use to measure impurity when deciding the optimal feature split?",
            "question_type": "MCQ",
            "difficulty_level": "MEDIUM",
            "marks": 1.0,
            "correct_answer": "A",
            "explanation": "Gini Impurity (or Information Gain via Entropy) measures the probability of misclassifying a randomly chosen element.",
            "hint": "It is named after an Italian statistician Corrado Gini.",
            "options": [
                {"option_label": "A", "option_text": "Gini Impurity"},
                {"option_label": "B", "option_text": "Euclidean Distance"},
                {"option_label": "C", "option_text": "Mahalanobis Distance"},
                {"option_label": "D", "option_text": "Cosine Similarity"}
            ]
        }
    ],
    "Deep Learning & Neural Networks": [
        {
            "question_text": "Which optimization technique prevents exploding gradients in Deep Recurrent Neural Networks (RNNs)?",
            "question_type": "MCQ",
            "difficulty_level": "HARD",
            "marks": 1.0,
            "correct_answer": "B",
            "explanation": "Gradient Clipping caps gradient values at a predefined maximum threshold, preventing numerical instability.",
            "hint": "It clips or clamps gradient vectors.",
            "options": [
                {"option_label": "A", "option_text": "L1 Lasso Regularization"},
                {"option_label": "B", "option_text": "Gradient Clipping"},
                {"option_label": "C", "option_text": "Batch Normalization"},
                {"option_label": "D", "option_text": "Dropout Layering"}
            ]
        }
    ],

    # M.Sc. Cyber Security
    "M.Sc. Cyber Security": [
        {
            "question_text": "Which mathematical problem forms the core security foundation of RSA Public Key Cryptography?",
            "question_type": "MCQ",
            "difficulty_level": "HARD",
            "marks": 1.0,
            "correct_answer": "C",
            "explanation": "RSA relies on the computational difficulty of factoring large composite prime numbers (Integer Factorization Problem).",
            "hint": "Multiplying prime numbers is easy, but factoring their product is hard.",
            "options": [
                {"option_label": "A", "option_text": "Discrete Logarithm Problem"},
                {"option_label": "B", "option_text": "Elliptic Curve Point Addition"},
                {"option_label": "C", "option_text": "Large Prime Integer Factorization"},
                {"option_label": "D", "option_text": "Symmetric XOR Cipher Permutation"}
            ]
        }
    ],

    # High School & Middle School Science/Maths
    "Physics": [
        {
            "question_text": "According to Newton's Second Law of Motion ($F = ma$), what happens to acceleration if force is doubled while mass remains constant?",
            "question_type": "MCQ",
            "difficulty_level": "EASY",
            "marks": 1.0,
            "correct_answer": "A",
            "explanation": "Acceleration is directly proportional to net force. Doubling force doubles acceleration.",
            "hint": "Acceleration varies directly with applied force.",
            "options": [
                {"option_label": "A", "option_text": "Acceleration doubles"},
                {"option_label": "B", "option_text": "Acceleration is halved"},
                {"option_label": "C", "option_text": "Acceleration stays unchanged"},
                {"option_label": "D", "option_text": "Acceleration quadruples"}
            ]
        }
    ]
}

def get_domain_questions(subject_name: str, topic_name: str = None, count: int = 3) -> List[Dict[str, Any]]:
    """Returns domain-grounded, topic-specific questions."""
    # Find matching questions by subject key
    matched = []
    for key, q_list in DOMAIN_QUESTION_BANK.items():
        if key.lower() in subject_name.lower() or subject_name.lower() in key.lower():
            matched.extend(q_list)
            break

    if not matched:
        # Generic fallback grounded in topic
        t_label = topic_name or subject_name or "Core Principles"
        matched = [
            {
                "question_text": f"Which fundamental principle governs the core operational mechanics of {t_label}?",
                "question_type": "MCQ",
                "difficulty_level": "MEDIUM",
                "marks": 1.0,
                "correct_answer": "A",
                "explanation": f"The core operational framework of {t_label} relies on algorithmic state transitions and mathematical optimization.",
                "hint": f"Consider the primary definition of {t_label}.",
                "options": [
                    {"option_label": "A", "option_text": f"Algorithmic State Optimization in {t_label}"},
                    {"option_label": "B", "option_text": "Random Unbounded State Traversal"},
                    {"option_label": "C", "option_text": "Static Linear Hardcoding"},
                    {"option_label": "D", "option_text": "Non-deterministic Memory Overwrite"}
                ]
            },
            {
                "question_text": f"When evaluating performance benchmarks in {t_label}, what primary metric is analyzed?",
                "question_type": "MCQ",
                "difficulty_level": "EASY",
                "marks": 1.0,
                "correct_answer": "B",
                "explanation": f"Performance evaluation in {t_label} measures accuracy, execution latency, and resource efficiency.",
                "hint": "Think about execution speed and accuracy metrics.",
                "options": [
                    {"option_label": "A", "option_text": "Raw Storage File Size"},
                    {"option_label": "B", "option_text": "Execution Latency & Accuracy Score"},
                    {"option_label": "C", "option_text": "Display Pixel Resolution"},
                    {"option_label": "D", "option_text": "Network Socket Buffer Count"}
                ]
            }
        ]

    # Repeat or slice to requested count
    result = []
    for i in range(count):
        item = dict(matched[i % len(matched)])
        result.append(item)

    return result
