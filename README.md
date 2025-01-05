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

You can refer to the report to see a more in-depth explanation of the language. It is located under `/report`.

## Quick Start

You can declare functions in our language and declare the return type.

Currently we only support `INT` and `BOOL` return types.

Pre & Post Conditions can be specified using our `@PRE` and `@POST` annotations.

If you would like to verify a property of the return value you can refer to it using
`rv` (As shown in the example below).

In this example we have a absolute function and we want to verify that
the return value is >= 0.

```
INT FUNCTION abs(INT x) {
   @PRE TRUE;
   @POST rv >= 0;
    IF (x >= 0) {
       RETURN x;
    } ELSE {
       RETURN -x ;
    }
}
```

## Loops

We also support loop invariants!

To verify some invariant of loops, you can use the `@LOOP` annotation as shown below.

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
