from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    INT = auto()
    FLOAT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    PRINT = auto()

    # Identifiers and literals
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()

    # Operators
    ASSIGN = auto()      # =
    PLUS = auto()        # +
    MINUS = auto()       # -
    MUL = auto()         # *
    DIV = auto()         # /
    MOD = auto()         # %

    # Relational
    LT = auto()          # <
    GT = auto()          # >
    LE = auto()          # <=
    GE = auto()          # >=
    EQ = auto()          # ==
    NE = auto()          # !=

    # Boolean
    AND = auto()         # &&
    OR = auto()          # ||
    NOT = auto()         # !

    # Delimiters
    SEMICOLON = auto()   # ;
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LPAREN = auto()      # (
    RPAREN = auto()      # )

    # Special
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __str__(self) -> str:
        return f"<{self.type.name}, {self.lexeme!r}, line={self.line}, col={self.column}>"


@dataclass
class LexicalError:
    message: str
    line: int
    column: int
    offending_char: str

    def __str__(self) -> str:
        return f"Lexical error at line {self.line}, col {self.column}: {self.message} (got {self.offending_char!r})"


KEYWORDS = {
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "print": TokenType.PRINT,
}

