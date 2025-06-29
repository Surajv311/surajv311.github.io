---
layout: post 
title: OOPS! Did you know that?
category: technicalArticles
---

> Article also published in [Hashnode](https://surajv.hashnode.dev/) & [Dev.to](https://dev.to/surajv).

When I was learning C++ in my beginning college semesters I faced a lot of confusion in understanding what exactly the concepts of OOPS meant.<br>
I have made a lot of beginner-level mistakes and learned from them. As time passed by, OOPS became my favorite concept in the C++ language.<br>

Here I would slide through some of the important concepts in OOPS.

![ops.jpg](https://cdn.hashnode.com/res/hashnode/image/upload/v1599394653986/Ht5gf26--.jpeg)

Before diving into the basics of OOPS, Its important to know what is a **Class** and an **Object**.

* **Class**:
It is a user-defined datatype that has member functions and different data variables. Memory is allocated to the Class only when an Object is defined.

* **Object**:
It is an instance of the Class. In simple words, it is the blueprint of the Class.

```
// header files 
class Class_name
{ 
/*
Access specifier 
public variables: can be accessed from everywhere
protected variables: can be accessed by the classes of the same package
private variables: can be accessed within the same class only.
->This is helpful when you learn the concept of Abstraction in OOPS. 
*/
public: 

// data variables
int variable_A;

// member functions
void print_function() 
{ 
cout << "Value of variable is :" << variable_A; 
} 
}; 
  
main() { 
  
// declaring object <Syntax: Class_name object_name>
Class_name object;  

/*accessing the variables in class and assigning value to it via object*/
object.variable_A= 20;  
  
// accessing member function in class 
object.print_function(); 

} 
```

Now we will cover the four main concepts in OOPS.
<br>

* **Encapsulation and Abstraction**:

In a nutshell, Encapsulation means hiding your data in a package. Abstraction displaying only essential information and hiding the unnecessary details from the client/user. 
<br>
Create a separate header file in which you would define your entire class. Then you can access the components of your class using the objects in your main function.

```
// header file header.h 
#include <iostream>
using namespace std ;
// we are defining a class in our header file
class Classtwo
{
private:  // for data abstraction
int var = 5; 
public :
int functionOne(); // declaring functionOne inside class
};
int Classtwo::functionOne() // defining functionOne outside class
{
cout << "functionOne is called(in header file)\n";
}

```
``` 
//main.cpp
// other header files
#include "header.h"
// namespace...

main(){
/* class Classtwo is in header file*/
Classtwo objectOne;
objectOne.functionOne(); 
cout<< objectOne.var; // would output the value of var 
}
```

* **Inheritance**:

In a nutshell, the derived class inherits properties from the base class.

```
//header files 
class Base // parent class
{
public :
int number =5;
};
class Derived: public Base // child class 
{
public :
void printFunction()
{
cout<<"Hello World";
}
};

main(){
Derived obj; /*object of 'Derived' class can access public components of 'Base ' class*/

cout<< obj.number ; 
//would output the number which is in Base class
```

* **Polymorphism**:

In a nutshell, it means having different forms. There are two types of polymorphism. <br>

-> Runtime Polymorphism:<br>

It happens when we override a function in the program.
```
// header files 

class Virtual_one
{
public :
int fun_One()
{
cout<<"fun_One works in v1\n";
}
};
class Virtual_two : public Virtual_one 
{
public :
int fun_One()
{
cout<<"fun_One works in v2\n";
}
virtual int fun_() 
// 'virtual' is used for late binding and runtime polymorphism.
{
cout<<"fun_ works in v2\n";
}
};
class Virtual_three : public Virtual_two // inheritance
{
int fun_()
{
cout<<"fun_works in v3\n";
}
};

main()
{
Virtual_one objA;
Virtual_two objBA , *objBB = new Virtual_two(); 
/*defining pointer object BB*/

Virtual_three objC;
objBB = &objC; 
/*objBB pointer of Virtual_two carries address of objC*/

objA.fun_One();
/*fun_One of Virtual_one would be accessed as objA is of that class*/

objBA.fun_One();
/*fun_One of Virtual_two would be accessed as objBA is of that class*/

objBB->fun_(); 
/*fun_ function is in Virtual_two and Virtual_three classes, we have used 'virtual' keyword for this*/

/* Note:
HERE objBB pointer(of Virtual_two class) carries address of objC(of Virtual_three class). So in objBB->fun_(); The fun_() of Virtual_two class would be working, as objBB pointer belongs to that class.
But when you add the keyword 'virtual' : The fun_() of Virtual_three class would work. */

```

 <br>
-> Compiletime Polymorphism: <br>

It happens when we overload a function or an operator in the program.
<br>
Consider a case of Operator Overloading: 
```
// header files
class Op_ovrload 
{
int numberA;
int numberB ;
public :
int inputNum()
{
cin >> numberA >> numberB ; 
/*writing cin statements in class/header file is considered a bad practice though here it's just for simplicity of code*/
}

//  Without Overloading
Op_ovrload addTheSet(Op_ovrload tempObj)
{
Op_ovrload takeT_Obj ;

takeT_Obj.numberA = numberA + tempObj.numberA;
takeT_Obj.numberB = numberB + tempObj.numberB;

return takeT_Obj;
}

// With Overloading
Op_ovrload operator + (Op_ovrload tempObj) 
{ 
// tempObj is loaded as objB
Op_ovrload takeT_Obj ;

takeT_Obj.numberA= numberA + tempObj.numberA
takeT_Obj.numberB = numberB + tempObj.numberB;

return takeT_Obj;
}
};

main()
{
Op_ovrload objA ,objB , objC , objD;
// we would load values in objA and objB
objA.inputNum();
objB.inputNum();

objC = objA.addTheSet(objB);
objD = objA + objB;
/*objC and objD would output the same value. Here '+' has been overloaded*/
}
```

Consider the other case of function overloading:
```
// header files 

void printFun(int number) { 
  cout << " Value is" << number; 
} 
void printFun(double  num) { 
  cout << "Value is " << num; 
} 
/*Hence we can see the function is overloaded.
The same name of functions with different parameters passed. */

main() 
{ 
printFun(320); 
printFun(48.95); 
}
```

---------------------
