#include <iostream>
#include <string>

using namespace std;

void print(string x)
{
cout << x << endl;
}


string itos(int x)
{
return to_string(x);
}


int length(string x)
{
return x.length();
}


char get(int x, string y)
{
if(x < 0 || x > y.length()){
return '\0';
} else {
 return y.at(x);
}
}


string reads()
{
string x;
cin >> x;
return x;
}


int readi()
{
int x;
cin >> x;
return x;
}


float readf()
{
float x;
cin >> x;
return x;
}


float itof(int x)
{
return (float)(x);
}


string ftos(float x)
{
return to_string(x);
}

int main()
{
    print("hello world");
    auto x = 5;
    auto y = 10;
    while (x > 0 and(y < 15)){
     x = (x - 1);
     y = (y + 5);
    }
    print(itos(x));
    print(itos(y));
    if ((y > x)){
     print("true");
    }
    if ((not (false))){
     print("False");
    }
return 0;
}