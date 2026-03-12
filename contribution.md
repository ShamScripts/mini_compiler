# Contribution Details

## Question 1: Lexical Specification and Tokenization

- **M1 (Shambhavi Jha)**
  - Listed and classified all token categories from the language specification (keywords, identifiers, literals, operators, delimiters, punctuation).
  - Drafted the initial regular expressions for each token class in Python.

- **M2 (Venkata Shreya)**
  - Refined the regexes (multi-character operators, distinguishing keywords vs identifiers, int vs float literals).
  - Designed the Token structure (type, lexeme, line, column) and decided the token-stream print format.

- **M3 (Yuvaraj Nayak)**
  - Implemented the core lexer module in Python:
    - Reads the source program.
    - Applies regex rules in priority order.
    - Produces the token sequence.
  - Added lexical error detection and reporting (unexpected characters, malformed tokens) with line/column information.

- **M4 (Krishna Nagpal)**
  - Wrote the driver script that:
    - Loads the uniform evaluation program.
    - Runs the lexical analyzer.
    - Prints the full token stream and any lexical errors.
  - Prepared example token-stream output and a short explanation of how source lines map to tokens.
