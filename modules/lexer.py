import re
from .tokens import TokenType, Token, LexicalError, KEYWORDS


class Lexer:
    """regex-based lexer"""

    TOKEN_SPECS = [
        ("FLOAT_LITERAL", r"\d+\.\d+"),
        ("INT_LITERAL", r"\d+"),
        ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),

        ("LE", r"<="),
        ("GE", r">="),
        ("EQ", r"=="),
        ("NE", r"!="),
        ("AND", r"&&"),
        ("OR", r"\|\|"),

        ("ASSIGN", r"="),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("MUL", r"\*"),
        ("DIV", r"/"),
        ("MOD", r"%"),
        ("LT", r"<"),
        ("GT", r">"),
        ("NOT", r"!"),

        ("SEMICOLON", r";"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
    ]

    WHITESPACE_PATTERN = re.compile(r"[ \t]+")

    def __init__(self, source):
        self.source = source.replace("\r\n", "\n").replace("\r", "\n")
        self.pos = 0
        self.line = 1
        self.column = 1
        self._compiled_specs = [
            (name, re.compile(pattern)) for name, pattern in self.TOKEN_SPECS
        ]

    def _current_char(self):
        if self.pos >= len(self.source):
            return ""
        return self.source[self.pos]

    def _advance(self, text):
        for ch in text:
            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        self.pos += len(text)

    def _skip_whitespace(self):
        while self.pos < len(self.source):
            ch = self._current_char()
            if ch in (" ", "\t"):
                m = self.WHITESPACE_PATTERN.match(self.source, self.pos)
                if not m:
                    self.pos += 1
                    self.column += 1
                else:
                    self._advance(m.group(0))
            elif ch == "\n":
                self._advance("\n")
            else:
                break

    def tokenize(self):
        tokens = []
        errors = []

        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source):
                break

            start_line = self.line
            start_col = self.column
            chunk = self.source[self.pos :]

            matched = False
            for name, pattern in self._compiled_specs:
                m = pattern.match(chunk)
                if m:
                    lexeme = m.group(0)
                    matched = True
                    self._advance(lexeme)

                    if name == "ID":
                        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
                    else:
                        token_type = getattr(TokenType, name)

                    tokens.append(Token(token_type, lexeme, start_line, start_col))
                    break

            if not matched:
                offending = self._current_char()
                errors.append(
                    LexicalError(
                        message=f"Unexpected character {offending!r}",
                        line=start_line,
                        column=start_col,
                        offending_char=offending,
                    )
                )
                self._advance(offending)

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens, errors

