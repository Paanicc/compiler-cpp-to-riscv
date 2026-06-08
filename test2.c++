// Panagiotis Christodoulou
// AM: 5501
// Username: cs225501
program test2{
    declare x, y, z;
    declare result;

    function add(in a, in b)
    {
        return a + b
    }

    function multiply(in a, in b)
    {
        declare temp;
        temp := 0;
        while temp < b
            temp := temp + 1;
        return a * b
    }

    x := 10;
    y := 20;
    z := add(in x, in y);
    result := multiply(in z, in 3);
    print result;

    if x < y
    {
        if x <> 0
            z := x + y
        else
            z := 0
    };

    while x > 0
    {
        x := x - 1;
        y := y + 2
    };

    switchcase
        when z = 30 : 
            print z
        when z > 30 : 
            z := z - 1
        default: z := 0
    ;

    incase
        when result > 100 : 
            result := result - 50
        when result <= 100 : 
            result := result + 10
    ;

    forcase x = 5
        when y > 10 : 
            y := y - 1
        when y <= 10 :
            y := y + 1
    ;

    input result;
    print result
}
