BOOL FUNCTION is_checker_board(BOOL a, BOOL b, BOOL c, BOOL d) {
    @PRE TRUE;
    @POST rv == (a^c^NOT(b)^NOT(d)) v (NOT(a)^NOT(c)^b^d);
    IF (a^c) {
        IF (NOT(b)^NOT(d)) {
            RETURN TRUE;
        } ELSE {
            NOP;
        }
    } ELSE {
        NOP;
    }

    IF (b^d) {
        IF(NOT(a)^NOT(c)) {
            RETURN TRUE;
        } ELSE {
            NOP;
        }
    } ELSE {
        NOP;
    }
    RETURN FALSE;
}