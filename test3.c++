// Panagiotis Christodoulou
// AM: 5501
// Username: cs225501
program test3{
    declare a, b, c, d;
    declare counter, total;
    function factorial(in n)
    {
        declare result;
        result := 1;
        while n > 1
        {
            result := result * n;
            n := n - 1
        };
        return result
    }

    function max(in x, in y)
    {
        declare r;
        if x >= y
            r := x
        else
            r := y;
        return r
    }

    function compute(in a, in b, inout c)
    {
        declare temp;

        function helper(in val)
        {
            return val * 2 + 1
        }

        temp := helper(in a) + helper(in b);
        c := temp;
        return temp - (a + b)
    }

    a := 1;
    b := 2;
    c := 3;
    d := 0;

    d := (a + b) * (c - a) / (b + 1);
    d := a * b + c * (a + b - (c * 2));
    d := (+a) + (-b) * c;

    total := factorial(in 5);
    counter := max(in a, in b);
    d := compute(in a, in b, inout c);
    print total;

    if a < b
    {
        if b < c
        {
            if c < 100
            {
                d := d + 1;
                print d
            }
            else
                d := 0
        }
        else
            d := -1
    }
    else
        d := -2;

    counter := 0;
    while counter < 10
    {
        b := 0;
        while b < 5
            b := b + 1;
        counter := counter + 1
    };

    switchcase
        when a = 1 : {
            a := a + 1;
            b := b + 1;
            c := a + b
        }
        when a = 2 : {
            a := a * 2;
            b := b * 2
        }
        when a > 2 : a := 0
        default: {
            a := 1;
            b := 1;
            c := 1
        }
    ;

    whilecase
        when a < 10 : a := a + 1
        when b < 10 : b := b + 1
        default: print a
    ;

    incase
        when a = 1 : a := a + 10
        when [a > 1 and a < 20] : a := a + 5
        when not [a < 100] : a := 0
    ;

    untilcase
        when a < 50 : a := a + 1
        when b < 50 : b := b + 1
        until [a >= 50 and b >= 50]
    ;

    forcase counter = 0
        when a > 0 : {
            a := a - 1;
            total := total + a
        }
        when b > 0 : b := b - 1
    ;

    if a = 0 or [b > 0 and c > 0]
        print 1
    else
    {
        if not [a = 0]
            print 0
    };

    input a;
    print a + b * c - d / (a + 1)
}
