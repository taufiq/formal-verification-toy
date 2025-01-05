INT FUNCTION pos_double(INT x) {
    DECLARE (INT double_x);
    @PRE x > 0;
    @POST rv == 2 * x;
    double_x := x;
    @LOOP double_x <= 2 * x;
    WHILE (NOT (double_x == 2*x)) {
        double_x := double_x + 1;
    }
    RETURN double_x;
}