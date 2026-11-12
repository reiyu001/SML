let a = 10;
let b = 2;

a = b;
a += b;
a -= b;
a *= b;
a /= b;

let arithmetic = a + b - a * b / a % b ^ 2;
let comparison = a == b != a < b > a <= b >= a;
let logic = true && false || !false;

a++;
--b;
