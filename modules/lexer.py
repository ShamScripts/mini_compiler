"""
Lexical analyzer
"""

import re

from .tokens import TokenType, Token, LexicalError, KEYWORDS

VALID_DESC = "valid token (identifier, literal, operator, or delimiter)"   # Message shown when a character doesn't match any token pattern

LEXICAL_SPEC = [
    ("Keywords", "int, float, if, else, while, print"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("INT_LITERAL", r"\d+"),
    ("FLOAT_LITERAL", r"\d+\.\d+"),
    ("Operators", "= + - * / % < > <= >= == != && || !"),
    ("Delimiters", "; { } ( )"),
]


def _err_class(ch: str) -> tuple[str, str]:
    if not ch:
        return "Unexpected end of input", VALID_DESC
    if ch == ".":
        return "Malformed float (e.g. extra decimal point)", VALID_DESC
    if ch in "^$#@~`\\":
        return "Illegal character (not in language)", VALID_DESC
    if ch in "&|" or ch in "<>!=+-*/%":
        return "Unsupported or invalid operator", VALID_DESC
    return "Illegal character (not in language)", VALID_DESC


class Lexer:
    """Scans source code character by character and produces a stream of tokens."""

    # Order matters: longer patterns first (e.g. float before int, <= before <)
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

    def __init__(self, source: str):
        self.source = source.replace("\r\n", "\n").replace("\r", "\n")
        self.pos = 0
        self.line = 1
        self.column = 1
        self._specs = [(n, re.compile(p)) for n, p in self.TOKEN_SPECS]

    def _peek(self) -> str:
        if self.pos >= len(self.source):
            return ""
        return self.source[self.pos]

    def _advance(self, text: str) -> None:
        for ch in text:
            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        self.pos += len(text)

    def _skip_ws(self) -> None:
        while self.pos < len(self.source):
            ch = self._peek()
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

    def tokenize(self) -> tuple[list[Token], list[LexicalError]]:
        tokens = []
        errors = []
        while self.pos < len(self.source):
            self._skip_ws()
            if self.pos >= len(self.source):
                break

            ln, col = self.line, self.column
            chunk = self.source[self.pos :]
            matched = False

            for name, pat in self._specs:
                m = pat.match(chunk)
                if m:
                    lex = m.group(0)
                    matched = True
                    self._advance(lex)
                    tt = KEYWORDS.get(lex, TokenType.IDENTIFIER) if name == "ID" else getattr(TokenType, name)
                    tokens.append(Token(tt, lex, ln, col))
                    break

            if not matched:
                bad = self._peek()
                err_type, exp = _err_class(bad)
                errors.append(LexicalError(error_type=err_type, expected=exp, line=ln, column=col, offending_char=bad or "<EOF>"))
                self._advance(bad)

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens, errors

