INT FUNCTION abs(INT x) {
   @PRE TRUE;
   @POST rv >= 0 ^ rv == x v rv == -x;
    IF (x >= 0) {
       RETURN x;
    } ELSE {
       RETURN -x ;
    }
}

