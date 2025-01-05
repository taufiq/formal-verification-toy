INT FUNCTION simpleMul(INT a, INT b) {
    DECLARE (INT i, INT result);
    @PRE a > 0 ^ b > 0;
    @POST rv == a * b;
    result := 0;
    i := a;
    @LOOP (result + (i * b) == 0 + (a * b)) ^ (a > 0) ^ (result >= 0) ^ (b > 0);
    WHILE (i > 0) {
        result := result + b;
        i = i - 1;
    }
    RETURN result;
}