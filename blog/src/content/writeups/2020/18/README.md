---
year: 2020
day: 18
title: "Operation Order"
slug: "2020/day/18"
pub_date: "2020-12-21"
---

## Part 1

Have you ever been curious how Python turns text into code?

It's done via a process called **lexing** - the code is broken up and returned as a list of **tokens**. A token is fundamental building block of code - all punctuation falls into this, as do strings, numbers, and keywords (`return`, `def`, etc). If there are syntax errors, they're caught during this step - the lexer will falter.

Next, a **parser** walks through the tokens and groups them into objects based on **precedence**. The parser is what knows the rules that dictate that `*` takes precedence over `+`. Those objects are stored in an **Abstract Syntax Tree**, which describes, unambiguously, the shape and structure of a program.

Then, the AST is evaluated, which takes AST nodes and translates them into something native to the language that's doing this work. In Python's case, that's C. It then does the computation and substitutes the results (`1 + 2` becomes `3`). Eventually, some sort of output happens.

Now, you don't actually need to know most of that for the purposes of today's puzzle, but I felt it helpful background. If you want to read more about it how lexers, parsers, and ASTs work, I wholeheartedly recommend [Writing An Interpreter In Go](https://interpreterbook.com/) (which you don't have to do in `go`). I've got a Typescript version [here](https://github.com/xavdid/monkey-ts).

Anyway.

To solve this puzzle, we need to write our own (very) little version of the above, which will step through tokens and perform math while disregarding operator precedence.

The input has two important features:

1. all the numbers are single digit. There's never a `+ 10` or anything
1. It always follows the pattern `number`, `operator`, `number`, `operator`, ...

Part 1 is helpful for tokenizing the input - each character is a token! We don't have to worry about figuring out that `10` is actually a single token in disguise. We don't care about the spaces (just the actual characters), so we can remove them:

```py
for line in self.input:
    tokens = line.replace(' ', '')
```

Pretty harmless so far! We could also send the replaced string through a `list` call, but for our purposes (stepping through the tokens via an index, one at a time) a `list` and `string` are identical.

Let's start without the parens. Our loop will be able to take advantage of the alternating number / operator pattern mentioned in the second item above. If we get a number, we store it. If we get an operator and we've got a number, we combine the two and stash that number.

We can store representations of the `+` and `*` as their underlying Python functions (`__add__` and `__mul__`).

```py
from operator import __add__, __mul__

OPERATORS = {"+": __add__, "*": __mul__}

def solve(equation: str) -> int:
    number = None
    operator = None
    pointer = 0

    while pointer < len(equation):
        head = equation[pointer]
        if head in OPERATORS:
            operator = OPERATORS[head]
        else:
            if operator:
                number = operator(int(head), number)
                operator = None
            else:
                number = int(head)
        pointer += 1

    return number
```

Assuming our input is valid and the above patterns hold, this will walk through the input and add or multiple the current result by the previous result.

Next up is handling the parentheses. We have to totally resolve anything in the parens before we do the outside. If you treat the inside of the parens as its own little sub-equation then we can re-use our existing `solve` method. Sounds like recursion to me!

`solve(1 + (2 * 3) * 4)` is the same as `solve(1 + solve(2 * 3) * 4)`. We know that we need to do such recursion when we hit an `(` and need to pass in everything in front of the `(`. We also know that when we find our first `)`, we should immediately return.

```py
... # operator code
else:
    if head == ")":
        return number

    if head == "(":
        head = solve(equation[pointer + 1 :])

    ...
```

This nearly works! The only problem is that when we back from our recursion, we pick right up when we left off. Instead, we need to jump our pointer ahead to the end of the sub-equation. To do that, we need to return the pointer from the function:

```py
... # operator code
else:
    if head == ")":
        return number, pointer
    if head == "(":
        # strip off the first paren and recurse the rest
        head, offset = solve(equation[pointer + 1 :])
        # extra 1 because the offset started at 0
        pointer += offset + 1

    ...

# outside the while loop
# pointer doesn't matter for final return, but
# it's good to keep a consistent return signature
return number, 0
```

Our actual solution is straightforward:

```py
return sum([solve(line.replace(" ", ""))[0] for line in self.input])
```

I'm happy with how this turned out, but I spent a long time messing with a worse (and increasingly convoluted) solution. If you like reading messy, dysfunctional code, you can check that out [here](https://gist.github.com/xavdid/238c8504994d887a2951224a07b32336).

## Part 2

For part 2, I wanted to go a different direction. Partly because I couldn't think of a good way to adapt my part 1 solution, partly because this one sounded fun.

Python is already very good at parsing code; we just need to trick it into parsing code differently. I mentioned in the lengthy intro above that a parser creates an Abstract Syntax Tree. An AST precisely describes the program using a set of nested structures. The following program:

```py
a = 1 + 2
print(a * 3)
```

Might look like this (pseudocode):

```json
{
  "type": "program",
  "statements": [
    {
      "type": "assignment",
      "destination": {
        "type": "identifier",
        "value": "a"
      },
      "expression": {
        "type": "binary_operation",
        "operation": "add",
        "left": {
          "type": "number",
          "value": 1
        },
        "right": {
          "type": "number",
          "value": 2
        }
      }
    },
    {
      "type": "function",
      "name": "print",
      "arguments": [
        {
          "type": "binary_operation",
          "operation": "mul",
          "left": {
            "type": "identifier",
            "value": "a"
          },
          "right": {
            "type": "number",
            "value": 3
          }
        }
      ]
    }
  ]
}
```

It's verbose, but you can see how the structure of the program is represented. As you can imagine, Python parses operator precedence correctly. `1 + 2 * 3` gives (something like):

```json
{
  "statements": [
    {
      "type": "binary_operation",
      "left": {
        "type": "number",
        "value": 1
      },
      "right": {
        "type": "binary_operation",
        "left": {
          "type": "number",
          "value": 2
        },
        "right": {
          "type": "number",
          "value": 3
        }
      }
    }
  ]
}
```

Note that the parser correctly groups `2 * 3`, something we want to take advantage of. Python actually exposes its AST tools in code itself:

```py
import ast

print(ast.dump(ast.format('1 + 2 * 3', mode='eval')))

# I formatted this manually to make it clearer
Expression(
    body=BinOp(
        left=Constant(value=1),
        op=Add(),
        right=BinOp(
            left=Constant(value=2),
            op=Mult(),
            right=Constant(value=3)
        )
    )
)
```

If we replace the `+` with `/` and `*` with `-` in the input string so that Python parses them the opposite way, then they'll be grouped correctly for the purposes of this puzzle:

```py
Expression(
    body=BinOp(
        left=BinOp(
            left=Constant(value=1),
            op=Div(),
            right=Constant(value=2)),
        op=Sub(),
        right=Constant(value=3)
    )
)
```

All that remains is to edit the AST so that `Div()` becomes `Add()` and `Sub()` is reverted to `Mult()`. Luckily, Python has [a class for this](https://docs.python.org/3/library/ast.html#ast.NodeTransformer)): `ast.NodeTransformer`:

```py
import ast

class SwapPrecedence(ast.NodeTransformer):
    def visit_Sub(self, node):
        return ast.Mult()

    def visit_Div(self, node):
        return ast.Add()
```

This class handled all the hard parts about visiting nodes, so all we do is define some methods to be called for all instances of certain node types. There's not a built-in way to render the new AST back to code, but you can imagine it as something like `(1 + 2) * 3`. Python already knows how to execute that correctly, so we can run it straight through `eval` (something you should only use in very controlled environments. Let's wrap up:

```py
total = 0
for line in self.input:
    tree = ast.parse(line.replace("+", "/").replace("*", "-"), mode="eval")
    new_tree = SwapPrecedence().visit(tree)
    total += eval(compile(new_tree, filename="", mode="eval"))

return total
```

Don't worry about the `mode` kwargs there - it just makes everything play nicely together. We could have used this for part 1 as well if we swapped `*` to `-`, parsed it, and swapped it back. I like our part 1 answer though, so I'll leave it as is.
