
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

INT FUNCTION randomFunction(INT a, INT b) {
    @PRE a < b;
    @POST a > b;
    IF (a == 5) {
        a := b + 1;
    } ELSE {
        a := b + 2;
    }
    RETURN a;
}




