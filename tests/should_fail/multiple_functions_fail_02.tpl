
INT FUNCTION aFunction(INT a, INT b) {
    DECLARE (INT x, INT z);
    @PRE a < b;
    @POST a >= b;
    x := 0;
    z := 5;
    @LOOP a <= b;
    WHILE (a < b) {
        x := x + 1;
    }
    a := a + x;
    RETURN a;
}



INT FUNCTION randomFunction(INT a, INT b) {
    @PRE a < b ^ (a >= 0);
    @POST a > b;
    b := 5;
    a := a + 2;
    RETURN a;
}