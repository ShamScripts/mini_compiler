# Module Documentation: `modules/grammar_utils.py`

## 1. Module Overview

This module defines the formal grammar artifacts used for parser-construction evidence:

- context-free grammar (CFG)
- FIRST set computation
- FOLLOW set computation
- LL(1) parsing table generation
- SLR(1) automaton/action-goto table generation

Pipeline role:
- supports parser evaluation and theoretical artifacts
- used by LL(1)/SLR parser modules and menu output in `compiler.py`

---

## 2. Imports

- `import collections`  
  Used for `defaultdict(set)` in FIRST/FOLLOW/table construction.

---

## 3. `Grammar` Class

## `__init__(productions, start_symbol)`
Initializes:
- production dictionary
- start symbol
- non-terminals and terminals
- computed FIRST and FOLLOW sets

Terminal detection:
- any symbol in production bodies not present in non-terminal set is treated as terminal.

---

## 4. FIRST/FOLLOW Algorithms

## `_compute_first()`
Fixed-point iterative algorithm:
1. initialize FIRST(terminals) = terminal itself
2. repeatedly propagate FIRST sets through productions
3. handle epsilon (`""`) where appropriate
4. stop when no set changes

## `_compute_follow()`
Fixed-point iterative algorithm:
1. add `$` to FOLLOW(start symbol)
2. scan production bodies and propagate follow constraints
3. use FIRST(rest) and FOLLOW(head) rules
4. stop at convergence

---

## 5. Table Construction

## `get_ll1_table()`
Builds table `M[NonTerminal, lookahead] = production`:
- uses FIRST(body)
- uses FOLLOW(head) for epsilon productions

Return format:
- nested dictionary: `table[head][terminal] = body`

## `get_slr_table()`
Builds SLR artifacts:
- augmented grammar
- LR(0) item closure/goto
- canonical state collection
- ACTION table (shift/reduce/accept)
- GOTO table

Return:
- `action`, `goto_table`, `augmented_rules`

---

## 6. Grammar Definition

`MINI_COMPILER_GRAMMAR` includes:
- program/unit structure
- declarations and optional function declaration
- statements: assign, if, while, print, block
- boolean and arithmetic expression productions
- relational operators

`get_mini_compiler_grammar()` returns configured `Grammar` object with start symbol `"Program"`.

---

## 7. Data Structures Used

- `dict[str, list[list[str]]]` for productions
- `set` for terminals/non-terminals/FIRST/FOLLOW
- `defaultdict(set)` for iterative propagation
- LR states as `frozenset` of item tuples
- action/goto tables as dictionaries keyed by `(state, symbol)`

---

## 8. Examples

## FIRST/FOLLOW use
When menu option `7` is selected in `compiler.py`, the project prints:
- FIRST sets
- FOLLOW sets
- LL table entries
- sample SLR action/goto entries

## LL/SLR parser use
`modules/ll1_parser.py` and `modules/slr_parser.py` call:
- `get_mini_compiler_grammar()`
- `get_ll1_table()` / `get_slr_table()`

---

## 9. Error Handling

This module does not raise user-facing syntax errors directly.
It builds parser artifacts; runtime parse errors are handled by LL/SLR parser modules.

Potential table conflicts are not explicitly reported as dedicated diagnostics in current code.

---

## 10. Strengths and Limitations

### Strengths
- complete parser-theory support for coursework outputs
- automated FIRST/FOLLOW/table generation
- integrated with both LL(1) and SLR parser modules

### Limitations
- no explicit conflict-report API
- grammar and recursive parser must be manually kept aligned
- prints only sample parts of SLR table in UI (for readability)
