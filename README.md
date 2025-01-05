# Introduction

Welcome to our toy verification tool! We've written some test cases in `tests/` folder.

# Setup

`pip install -r requirements.txt`

# Running

You can write code in `.tpl` files and verify them.
`python3 main.py <path_to_tpl_file>`

# Running tests

`python3 run_tests.py`

# Instructions

## Detailed Description

You can refer to the report to see a more in-depth explanation of the language. It is located under `/report/report.pdf`.

## Quick Start

All instructions should be placed inside a function declaration, function calls are not supported.

Currently we only support `INT` and `BOOL`types.

Pre & Post Conditions can be specified using our `@PRE` and `@POST` annotations.

If you would like to verify a property of the return value you can refer to it using
`rv` (As shown in the example below).

In this example we want to verify if the function abs returns the  absolute value of the variable x.

```
INT FUNCTION abs(INT x) {
   @PRE TRUE;
   @POST rv >= 0 ^ rv == x v rv == -x;
    IF (x >= 0) {
       RETURN x;
    } ELSE {
       RETURN -x ;
    }
}
```

## Loops

We also support loop invariants!

To verify an invariant of a loop, you can use the `@LOOP` annotation as shown below.

```
INT FUNCTION aFunction(INT a, INT b) {
    DECLARE (INT x, BOOL z);
    @PRE a < b;
    @POST a >= b;
    @LOOP a <= b;
    WHILE (a < b) {
        a := a + 1;
    }
    RETURN a;
}
```

## Multiple Functions

Want to verify multiple functions at once? You can add them into the same `.tpl` file and
our verifier will check all of them.
