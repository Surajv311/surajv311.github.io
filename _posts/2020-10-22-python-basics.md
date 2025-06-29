---
layout: post 
title: Basics of Python in a nutshell!
category: technicalArticles
---

> Article also published in [Hashnode](https://surajv.hashnode.dev/) & [Dev.to](https://dev.to/surajv).

Let's glide through all the basic concepts in Python : 

* To give single or multi-line comment use: 

```
#single line comment 

""" multi-line 
comment"""

```
* We can declare variables directly in Python without putting any data type unlike other languages like C/C++.

```
x = 8
y = "variable"
print(x) # to print a statement 
print(y)

a , b = "Hello" , "World"  # to assign values in single line 
print(a)
print(b)
```
* To get the data type of any object: 

```
x = 8
print(type(x))
```

* Basic operations in Python:

```
a = 4 
b = 9
print(a+b) # addition
print(a-b) # subtraction
print(a/b) # division
print(a*b) # multiplication
print(a**b) # exponentiation
```

* The basic data structures in Python are: <br>

-> List: An ordered collection that is changeable and allows duplicate members. <br> 

-> Tuple: An ordered collection that is unchangeable and allows duplicate members. <br> 

-> Set: An unordered and unindexed collection doesn't allow duplicate members.  <br> 

-> Dictionary: An unordered collection that is changeable and indexed. Also, it doesn't allow duplicate members. <br> 

```
a = ["Hello", "World", "!"]	#List
b = ("Hello", "World", "!")	#Tuple
c = {"Hello", "World", "!"}	#Set
d = {"name" : "Suraj", "age" : 18, "location": "India"}	#Dict
```

* To understand the data structures in detail:

1) List:

```
#To print items in list using for loop:
this_list = ["A", "B", "C"]
for x in this_list:   # don't forget indentation in python codes 
    print(x)

#To check if item is present in the list:
this_list = ["A", "B", "C"]
if "D" in this_list :
    print("present")

#Note: You may add print statements to view your results.

# Use the append() to append an item in the list:
this_list = ["A", "B", "C"]
this_list.append("D")

#To insert item at a specified index in the list:
this_list = ["A", "B", "C"]
this_list.insert(1, "D")

#To remove a specific item from the list:
this_list = ["A", "B", "C"]
this_list.remove("B")

#To pop last item from the list:
this_list = ["A", "B", "C"]
this_list.pop()

#To removes an item from a specified index
this_list = ["A", "B", "C"]
del this_list[1]

#To clear the entire list
this_list = ["A", "B", "C"]
this_list .clear()

#To find length of the entire list
this_list = ["A", "B", "C"]
len(this_list)

#To join two lists
this_list = ["A", "B", "C"]
another_list = ["D", 3, 4]
result_list = this_list + another_list 
# result_list would have elements from both list

#To convert List to Tuple:
this_list = ["A", "B", "C"]
tuple(this_list )

#To slice List:
this_list = ["A", "B", "C"]
this_list[3:8]  # slicing the list

```

2) Tuple:

```
# To print items in Tuple:
this_tuple = ("A", "B", "C")
for x in this_tuple:
    print(x)

#To find length of Tuple:
this_tuple = ("A", "B", "C")
print(len(this_tuple))

# Convert
this_tuple = ("A", "B", "C")
list(this_tuple) #converting tuple to list

#To find type of Tuple:
this_tuple = ("A", "B", "C")
print(type(this_tuple))

# To slice Tuples 
this_tuple = ("A", "B", "C", "D" , "E")
print(this_tuple[1:]) # to print items from index 1 
# to print items starting from index 2 to index 3 (i.e 4-1)
print(this_tuple[2:4]) 
print(this_tuple[::-1]) # to print in reverse manner

#To delete a tuple 
this_tuple = ("A", "B", "C")
del this_tuple 
```

3) Set:

```
# To print items in Set:
this_set = {"A", "B", "C"}
for x in thisset:
    print(x)

#To add items in set :
this_set = {"A", "B", "C"}
this_set .add("D")

#To update set :
this_set = {"A", "B", "C"}
this_set .update([1,2,3])

#To remove an item from a set:
this_set = {"A", "B", "C"}
this_set .remove("C")

#To pop item from set
this_set = {"A", "B", "C"}
this_set .pop()

#To clear everything from the set: 
this_set = {"A", "B", "C"}
this_set.clear()

#To add items form one set to another
this_set = {"A", "B", "C"}
another_set= {1, 2, 3}
this_set.update(another_set)
#Note: every time you run the command the items would be #shuffled which justify that items in set are unordered.

#Operations in Sets: 
this_set = {1,2,3,4,5}
another_set= {3,4,5,6,7}

print(this_set|another_set) #Union
print(this_set - another_set) #Difference
print(this_set & another_set) #Intersection
```

4) Dictionary:

```
#To print a Dictionary: 
# items are in key:value pairs
this_dict = {
  "Name": "Suraj",
  "Age": "18",
  "Year": 2020
}
print(this_dict) # You can also use a for loop.

#Adding new index key with value: 
this_dict = {"Name": "Suraj",  "Age": "18",  "Year": 2020}
this_dict["newItem"] = "newValue"

#To pop a value from a dictionary: 
this_dict.pop("Year") #specifying key value 

#To clear the Dictionary:
this_dict.clear()

#To copy items from one Dictionary to another : 
this_dict = {"Name": "Suraj",  "Age": "18",  "Year": 2020}
another_dict = this_dict.copy()
# then print 

#To delete a value from Dictionary:
this_dict = {"Name": "Suraj",  "Age": "18",  "Year": 2020}
del Dict["Age"] 
```

* Characters in Python : 

```
character = "Hello World!"
print(character[1]) # to get character at index 1 
print(character[3:7]) # to get character at from index 3 to 6 
#It can also be done using negative indexes

#To find the length of the character
len(character)

#Some other basic functions:
character = "Hello World!"
print(character .lower()) # to convert to lowercase
print(character .upper()) # to convert to uppercase
print(character .replace("W", "Y")) # To replace characters in it
print(character .split(",")) # returns ['Hello World!']
```

* Logical operators in Python:  <br>
They are used to combine conditional statements. <br>
```
and 	 - returns True if both statements are true .
or	 - returns True if one of the statements is true .
not	 - reverses the result, returns False if the result is true .
```

* Loops in Python: 

```
#For loop
num = 0 
for num in range(0, 10): 
    print(num) # to print numbers from the range

#While loop
while (num < 10):     
    num = num + 1
    print(num) # to print numbers
```

* If-else statements in Python:

```
num = 0 
for num in range(0, 10): 
    if(num<5):
        print(num) # to print numbers less than 5 
```


* Functions in Python:

```
def function(x):
    print("Function called")
    print("Value passed is ",x)

function(5)

# Now using lamda function.
# It can take any number of arguments, but can only have one #expression.
#syntax : lambda arguments : expression
function = lambda x : x*2
print("Returning a value twice the passed value:",function(10))
```

With this, we have slid through the basics.

----------------
