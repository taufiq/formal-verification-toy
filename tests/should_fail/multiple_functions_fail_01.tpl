
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
    @PRE a < b ^ (a >= 0);
    @POST a > b;
    b := 5;
    a := a + 2;
    RETURN a;
}




