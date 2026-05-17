---
layout: post 
title: Learning GoLang, gRPC, Protobuf
category: technicalArticles
---

> From my experience working at [Punch](https://www.punch.trade/). Read docs, youtube, GPT explanations. 

Learning Golang, gRPC, Protobuf. I may take occasional detours as a part of understanding things 'properly'. 

### Fundamentals

Nuances in Go: 
- Strict compile time checks, i.e: If you have declared a variable or imported a package in code, you MUST use it. Unused entities in code will lead to compile time errors thrown. 
  - Compiled vs Interpreted language: 
    - Your CPU runs instructions in 0s and 1s. So every instruction defined via a language must eventually become machine code. The difference is WHEN and HOW that translation happens.
    - Compiled languages Flow: Source code → Compiler → Machine code executable → Run the executable. Compiler: Reads the entire program; Does static analysis; Optimizes globally. Interpreted languages Flow: Source code → Interpreter → Execute line by line. Interpreter: Reads one statement, Executes it immediately, Moves to the next. Compiled languages came first. Note that today almost all modern “interpreted” languages compile internally.
    - What did interpreted languages solve?: Early computers were painful; Compilation took minutes to hours hence debugging meant: Write code, Compile, Run, Crash, Repeat. Interpreters solved this: Immediate feedback, Interactive programming (REPL), Dynamic behavior. For example:
    
      ```
      Eg1: — Calculator 
      In Python (Interpreted, can do interactive exploration): 
      >>> 10 * 3
      30
      >>> 10 * 3 + 5
      35
      >>> (10 * 3 + 5) / 7
      5.0
      In C (Compiled): 
      - Write the code first 
      #include <stdio.h>
      int main() {
          printf("%d\n", (10 * 3 + 5) / 7);
      }
      - Then run gcc calc.c -> ./a.out. 
      > Interpreter lets you think with the computer, compiler forces you to prepare a program first. Interpreters were not invented to replace compilation rather solve human feedback speed, not program execution speed.
      > Interpreted languages shine when you don’t yet know what the program should be, if you know, then Compiled language/Interpreted language would anyways work in similar way. 
      
      Eg2: Parsing unknown / messy data
      In Python: 
      import json
      with open("data.json") as f:
          data = json.load(f)
      type(data)
      len(data)
      data[0].keys()
      You inspect:
      >>> data[0]["user_id"]
      >>> data[0].get("timestamp")
      >>> [x for x in data if "error" in x]
      You discover the data while writing code.
      In C you must: 
      Decide struct layout upfront, Handle parsing manually, Recompile every structural change, Print + inspect. C forces decisions early. Python lets decisions happen late.
      ```
- Strong + static typing (but with inference). 
  - It is statically typed language, i.e: The type of every variable/expression is known before the program runs. Dynamic typic means the type of variable is know during runtime of program. 
  - Go gives capability to infer the type of variable even if you don't mention the type in code, during compile time, using it's type-inference. Eg: `Usual code eg: var x int = 10. But if you don't mention 'int', it will still be able to infer the type during compile time, i.e: var x = 10`.  
- If you don't assign a value to variable, Go assumes default values, it never leaves variables uninitialized. Eg: 

  ```
  | Type    | Zero value |
  | ------- | ---------- |
  | int     | 0          |
  | string  | ""         |
  | bool    | false      |
  | pointer | nil        |
  | slice   | nil        |
  | map     | nil        |
  ```
- No semicolons (mostly) to end code in line. Go takes care of it. Eg: `var x int = 10 is fine, no need for var x int = 10;`. 
- Explicit conversions must be done if required in values. Eg: `var y float64 = float64(x)`.
- if / for / switch need no parentheses.
- Only ONE loop keyword: for. No while, no do-while.
- Functions can return multiple values.

  ```
  func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("divide by zero")
    }
    return a / b, nil
  }
  ```
- Error handling is explicit. Eg: 

  ```
  result, err := divide(10, 2)
  if err != nil {
      return err
  }
  ```
- No classes, no inheritance. Go uses: structs, interfaces, composition. 
- Interfaces are implicit. Eg: 

  ```
  type Reader interface {
      Read() string
  }
  If a struct has Read(), it automatically implements Reader. No need to use a keyword like implements which we do like in Java. 
  ```
  - Pointers but no pointer arithmetic. Like: `p := &x, is fine, but can't do things like: p++ // illegal`. Some more info on pointers:
    
    ```
    var x int = 10
    var y *int
    y = &x
    ```

    | Expression | Meaning                | Type    | Value          |
    | ---------- | ---------------------- | ------- | -------------- |
    | x          | normal variable        | int     | 10             |
    | &x         | address of x           | *int    | memory address |
    | y          | pointer to x           | *int    | address of x   |
    | *y         | value at address y     | int     | 10             |
    | &y         | address of pointer y   | **int   | memory address |

    ```
    *int      → pointer to int
    *string   → pointer to string
    *float64  → pointer to float64
    *struct{} → pointer to struct
    *int guarantees dereferencing gives an int ~ Type safety (prevents invalid memory access)
    ```

	- Interesting [read on pointers](https://stackoverflow.com/questions/64235422/are-there-differences-between-int-pointer-and-char-pointer-in-c).

- Arrays vs slices: Arrays are fixed, Slices in Go are dynamic sized (mostly used). 
  
  ```
  var a [3]int // fixed size of 3 - arr
  var s []int // dynamic - slice

  Note:
  1. nil slice ≠ empty slice. Eg: 
     var s []int     // nil
     s := []int{}    // empty
  2. To add elements in slice, eg: s = append(s, "hello")
  3. Conversions:
       Array to Slice:
         a := [5]int{1, 2, 3, 4, 5}
         s := a[:] // Could also have partial slice [1:4]
       Slice to Array
         s := []int{1, 2, 3, 4, 5}
         var a [5]int
         copy(a[:], s)
  ```

- Maps must be initialized
  
  ```
  var m map[string]int
  Doing: m["a"] = 1 // Wrong
  Rather: m := make(map[string]int)
  ```
  
  Note: 

  | new                | make                    |
  | ------------------ | ----------------------- |
  | allocates memory   | allocates + initializes |
  | returns pointer    | returns value           |
  | rarely used        | commonly used           |


- func init() in Go is a special function that runs automatically during a package's initialization, before any other functions in the package are called, including main(). It's used for setup and configuration tasks. 
- No function overloading or hardcore OOPs kind of concept in Go. 
  
  ```
  Ex: 
  Java style OOP:
    class User {
        private String name;
        User(String name) {
            this.name = name;
        }
        public String greet() {
            return "Hi " + name;
        }
    }
  Go style OOP:
    type User struct {
        name string
    }
    func NewUser(name string) *User {
        return &User{name: name}
    }
    func (u *User) Greet() string {
        return "Hi " + u.name
    }
  
    > Creating a User value (without pointers) can be done like: u := User{name: "Suraj"}.
    > Now, coming back to our pointer OOP example:
       User{name: name} → creates a User value.
       & → takes its address.
       Result type → *User (pointer to User).
       Memory picture: 0x1000 ─▶ User{name: "Suraj"}.
    > In the (u *User) the receiver function, u is a pointer, u.name automatically dereferences the pointer (Go does this for you, else you would've to write like: (*u).name)
    > There is no separate “address type”. The only way to represent an address is with a pointer type (*User). Go does NOT allow raw memory addresses like C: return 0x7ffeefbff5a8; Only return &User{name: "Suraj"}. Can imagine as pointer types being safe abstraction over addresses.
    ```  

### Phase 1

- Keywords used: 
  - Declarations: package, import, var, const, type, func  
  - Control flow: if, for, switch, select
  - Concurrency: go, chan
  - Memory/lifecycle: new, make, defer
  - Error/exit: panic, recover, return
- Variable declarations:
  
  ```
  For Single variable:
  1. var x string = "" -> Used and declared inside/outside (global variable) functions; Declares + Assigns value

  2. var x = "" -> Used inside/outside functions; Go infers 'x' is a string during compile time (Go is statically typed language); Declares + Assigns value

  3. x := "" -> Used ONLY inside functions; Declares + Assigns value; It's var only, not const (we learn about this later)

  4. x = "hello" -> Used inside/outside functions; Assigns ONLY, hence 'x' must exist already

  For Multiple variables:
  1. 
  var name1, name2 string
  var age int
  var isAdmin bool
  name1 = "foo"
  name2 = "bar"
  age = 25
  isAdmin = false

  2. 
  var (
      name string = "suraj"
      age int = 25
      active bool = true
  )

  3. (type-interface taking care)
  var name, age, active = "suraj", 25, true

  4. 
  func main() {
      name, age, active := "suraj", 25, true
      _, _, _ = name, age, active
  }
  _ -> It is a blank identifier. Since Go requires every declared variable MUST be used, blank identifier flags to compiler that the variable exists, not deliberately using it, but may use in future. 
  ```

- Data Structures in Go:
  - Keywords:
    - var: mutable, package-level declaration
    - const: immutable 
    - type: define new types, used for: Structs, Interfaces, etc. 
    - func: functions
    - import: dependency management and package: namespace
      - A namespace is a named logical container that groups identifiers (functions, variables, types) so they don’t clash with others. In Go, packages are namespaces.
      - If a function/variable/struct/interface/const, etc., variable is capitalized - Means access is public, if smallcase then access is private (accessible only inside same package)
        
        ```
        func CreateUser() User {   // public function
            return User{Name: "Suraj", Age: 10}
        }
        func createUser() User {   // private function
            return User{Name: "Suraj", Age: 10}
        }
        ```

  - Data Structures: 
    
    ```
    The type is always on the RIGHT side, if not inferring. Eg: var x int, var s []string, var m map[string]int

    Normal variables ~
    > x := 10
    > var x string = ""
    > var name string
      name = "Suraj"

    Arrays (Fixed size) ~ 
    > var a [3]string
      a[0] = "a" 
    > x := [3]int{1, 2, 3}

    Slices (Dynamic size) ~
    > s := []int{1, 2, 3} // or 
    > s2 := []string{}
      s2 = append(s, "hello") // append is only in slice, not arrays
    > arr := [5]int{1, 2, 3, 4, 5}
      s := arr[1:4] // [2 3 4] // slice from an array 

    Maps (key → value) ~
    > m := map[string]int{
            "apple":  10,
            "banana": 20,
          }
      price := m["apple"]

    Pointers ~ 
    > x := 10
      p := &x   // pointer to x

    Structs ~ Holds data
    > type User struct {
          Name string
          Age  int
      }
      u := User{
          Name: "suraj",
          Age:  25,
      }
      fmt.Println(u.Name) // Capitalized, hence public access from all packages, if lowercase letters named in struct then private access.
      > Struct tags: They are defined as key-value pairs enclosed in backticks `` immediately following the field declaration. They are small pieces of metadata. They are ignored by normal Go code execution but are highly useful for tasks like data serialization, database mapping, and validation - which third-party libraries leverage, like Viper. Ex: 
		type User struct {
			Name     string `json:"user_name" db:"name,unique"`
			Age      int    `json:"age,omitempty"`
			Password string `json:"-"`
		}

    Interface (Projects behaviour, unlike struct) ~
    > type Speaker interface {
        Speak() string
      }
      // Any type that has Speak() string automatically implements Speaker interface, no need to use stuff like override, etc. Use eg: 
      func (p Person) Speak() string {
          return "Hello, I am " + p.Name
      }
    ```

	- Functions & Methods
	  - Function: standalone, not tied to any type. Method: function attached to a type (receiver), called on a value.
	  - Methods give behavior to structs; functions are just helpers. Eg: 
	  
	  ```
	  Normal/Free function:
	  func add(a int, b int) int {
	    return a + b
	  }

      Variadic functions: Accepts any number of arguments of the same type. Can be used for multiple arguments or slices.
	  // Variadic Mode: ...int → becomes []int inside function. Note that only last parameter can be variadic.
	  func sum(nums ...int) int {
		  total := 0
		  for _, n := range nums {
		      total += n
		  }
		  return total
	  }
	  sum(1, 2)
      sum(1, 2, 3)       
	  sum()           // Valid: nums is a nil slice
	  s := []int{1, 2, 3, 4} // using slice 
	  sum(s...)       // Must "unpack" with ...
      // You could also pass slices normally, eg: 
	  func sumForSlice(s []int) int { // Type must be []int
	      total := 0
	      for _, n := range s {      
	          total += n
	      }
	      return total
	  }
	  s2 := []int{1, 2, 3, 4}
	  sumForSlice(s2) // Pass directly; no unpacking needed   
	
	  Multiple returns function: 
	  func divide(a, b int) (int, error) {
	    if b == 0 {
	        return 0, errors.New("divide by zero")
	    }
	    return a / b, nil
	  }
		
	  Methods: Assume a struct, 
	  type User struct {
		  name string
	  }
	  Plain function (NOT attached to anything): 
	  	func sayHello(a, b int) {
		  	fmt.Println("hello", a, b)
	  	}
	  Method (attached to a struct): 
	  	func (u *User) sayHello(a, b int) {
	  		fmt.Println("hello", u.name, a, b)
	  	}
	  (u *User) means:
      	This function is attached to User and operates on a User object.
	  How it becomes accessible: 
	  	u := &User{name: "Suraj"}
	  	u.sayHello(1, 2) // Even though method receiver is *User, u.sayHello() works, as Go automatically takes care of addresses: (&u).sayHello()
	  
      A struct can have multiple behaviors by implementing multiple interfaces.
      type Flyer interface {
		 Fly() string
	  }
	  type Swimmer interface {
		 Swim() string
	  }
	  type Duck struct {
		 Name string
	  }
	  func (d Duck) Fly() string {
		 return d.Name + " is flying"
	  }
	  func (d *Duck) Swim() string {
		 return d.Name + " is swimming"
	  }
	  func main() {
		 d := Duck{Name: "Donald"}
		 var f Flyer = d // Way 1 to do it
		 var s Swimmer = &d // Way 2 to do it, since go handles pass by reference. Also note we are assigning struct d inside interface Flyer/Swimmer - will learn about it
		 fmt.Println(f.Fly())
		 fmt.Println(s.Swim())
	  }
	  How can an interface "equal" a struct?: var f Flyer = d.
        An interface value is two things: (interface type, concrete value). Hence above one is internally stored as:
		Flyer interface
		└── concrete type: Duck
		└── concrete value: Duck{Name: "Donald"}
		The interface does NOT become the struct. The struct is stored INSIDE the interface. This is different from java / python.
  
	  > Interfaces can only be satisfied by methods, not free functions. Consider same above example: 
		func Fly(d Duck) string {
			return d.Name + " is flying"
		}
		Fly(d)
		func (d Duck) Fly() string {
			return d.Name + " is flying"
		}
		d.Fly()
		Both are conceptually same, second form enables interface and method sets. 

	  > Value vs Pointer receiver nuance; Say the receiver is: 
  		> d Duck -> It cannot modify struct.
  		> d *Duck -> It can modify struct.  
		Another ex:
  		type Rectangle struct {
		    width, height int
		}
		func (r Rectangle) Area() int { // Define a method for the Rectangle struct using a value receiver
		    return r.width * r.height
		}
		func (r *Rectangle) Scale(factor int) { // Define a method with a pointer receiver to modify the original struct
		    r.width *= factor
		    r.height *= factor
		}
		func main() {
		    myRect := Rectangle{width: 10, height: 5} // Create an instance of the struct	    
		    fmt.Println("Area:", myRect.Area()) // Output: Area: 50
		    myRect.Scale(2)
		    fmt.Println("New Width:", myRect.width) // Output: New Width: 20
		}
	  ```
  
  - DataTypes:
    
    ```
    10      // int, we do have int8, int64, uint/uint8... - unsigned int which has positive values, etc... 
    3.14    // float64
    true    // bool
    "hi"    // string
    'A'     // byte
    '世'    // rune
    ```

- Loops/If-Else/Switches
  
  ```
  Normal loop:
  for i := 0; i < 5; i++ {
    fmt.Println(i)
  }

  Infinite loop:
  for {
	fmt.Println("running")
  }

  Loop over slice/map:
  for i, v := range nums {
    fmt.Println(i, v)
  }
  // i=index, v=value

  Run like while loop:
  for sum < 1000 {
  	sum += 1 // doubles the value of sum
  }

  If-Else:
  if x > 10 {
    fmt.Println("big")
  } else {
      fmt.Println("small")
  }

  Switch:
  switch day {
    case "Mon":
        fmt.Println("Start")
    case "Sun": 
        fmt.Println("Rest")
    default:
        fmt.Println("Other")
  }
  // Could also give multiple conditions like: case "Sun", "Tues":...
  // It's same as writing: case day == "Sun" || day == "Sun2":...
  ```

### Phase 2

File structure in Go: 
Assume:

```
hello-go/
├── go.mod
├── main.go
└── mathutils/
    └── add.go
```

Create go.mod using: `go mod init hello-go`. Note for production related projects, consider naming convention like: github.com/XYZCompanyOrName/project

go.mod can be imagined as: requirements.txt + project identity + version lock.

Keeping module name same as folder name is best practice, else when you import other packages, you'll have to do an explicit handling.
- Go mod or module name you define in command becomes the prefix for all imports inside this project. Hence use proper module name like: `go mod init github.com/X/myproject` therefore `import "github.com/X/myproject/internal/utils"`.
- Go does not support relative imports (except very special cases you should avoid) like: `import "./utils"`. Note that you could rename the folder, it wouldn't matter, Go builds based on module identity, not folder naming.
- Hence file in `/Users/X/work/nats-consumer/...` doesn't matter, Go sees it as it's inside `github.com/X/myproject/nats-consumer/...` 

Files: 

```
mathutils/add.go:
package mathutils
// Add is a public function
func Add(a int, b int) int {
    return a + b
}
// Note: Package name mathutils would be same across all files in that folder. Note that main.go, is a special package, since it's entrypoint file.  

main.go:
package main
import (
    "fmt"               // standard library
    "hello-go/mathutils" // local package
)
func main() {
    sum := mathutils.Add(3, 4)
    fmt.Println("Sum:", sum)
}
// Note: Import path = (module name initialized) + (folder or relative path from go.mod to the package directory).
```

Run program using: `go run .`

To install third party packages: go get github.com/google/uuid

When you do so, a go.sum file is created (you don’t edit this). It stores checksums, ensures integrity; Can be imagined as pip-lock/poetry.lock file in Python. 
Version selection happens via go.mod (what versions). Integrity is enforced via go.sum (prove this code hasn’t changed). 

Key Go Directory Naming Conventions: 

```
- cmd/: Contains entry points for executable binaries. Each subdirectory (cmd/app1, cmd/app2) acts as a main package, allowing a single repository to generate multiple binaries.
- internal/: Contains code intended only for this project, enforced by the Go compiler. Code in internal/ cannot be imported by other projects, making it ideal for encapsulated application logic.
- pkg/: Contains library code designed to be consumed by external applications or other projects, serving as a shared library.
- api/: Houses API definitions such as Swagger/OpenAPI specs, JSON schemas, or Protocol Buffers.
- configs/: Stores configuration files or default configuration templates.
- web/: Holds front-end components, such as static assets, HTML templates, or CSS/JS files.
- scripts/: Contains build, installation, analysis, or administrative scripts.
- testdata/: Stores data files required for tests; Go tools automatically ignore this directory during building.
- vendor/: Contains application dependencies. Although becoming less common with Go modules, it's still a standard directory name for vendored code.
- test/ (or tests/): Used for system or integration tests, rather than unit tests which usually reside alongside the code. 
```

Essential Go commands: 

```
go run .                 # run main package
go build                 # build binary
go build ./cmd/consumer  # build specific binary
go get github.com/google/uuid   # add dependency
go mod tidy                    # clean unused deps (VERY important)
go list -m all                 # list modules
go fmt ./...       # auto-format code
go vet ./...       # static analysis
go test ./...      # run all tests
```

### Phase 3

Go - Memory model 

- Memory model
  - A Go binary compiled for macOS will not run on Windows because binaries are OS and architecture-specific (like ARM64, x86_64), but Go allows cross-compiling by targeting the desired OS and CPU (like `GOOS=windows GOARCH=amd64 go build`). [Interesting read](https://www.digitalocean.com/community/tutorials/building-go-applications-for-different-operating-systems-and-architectures).
  - Every program uses two main memory regions (both reside in RAM):
    - Stack: Fast, Automatically managed, Function-scoped, Freed when function returns
    - Heap: Slower than stack, Manually (C) or GC-managed (Go/Java/Python), Used when data must live longer
  - Go decides stack vs heap at compile time using escape analysis - you don't do it, whereas Java relies on runtime JIT optimizations and Python allocates everything on the heap by design.
  - What Go GC does:
    - Find live objects, Free unreachable objects, Run concurrently with your program. This is called Concurrent mark-and-sweep (tricolor) GC.
      - White → not yet seen (assumed garbage)
      - Gray → seen, but children not scanned
      - Black → seen and fully scanned. A black object must never point to a white object for invariant GC. 
    - Properties: Mostly concurrent, Small pause times, Optimized for server workloads
    - Go’s GC runs at the same time as your program. 
    - **Write barrier**: When your program changes a pointer while GC is running, Go must inform the GC, called WB, handled by Go compiler itself. Problem without write barrier: GC thinks an object is unreachable -> Your code suddenly points to it -> GC frees it anyway → Crash. Write barrier prevents this. GC must be told about new pointers created while it is running, because the GC is making decisions based on a partial, moving snapshot of the heap.
    - **sync.Pool**: It is a temporary object recycling bin. Instead of: Allocate → use → GC frees. You do: Allocate once → reuse many times. Helps with heap allocations, fewer objects for GC to scan, shorter GC cycles, etc. Note: sync.Pool should NOT be used everywhere, its specific tool meant for temporary objects that reduce GC pressure, not a general cache or reuse mechanism.
    - **unsafe** keyword: It lets you break Go’s rules like: Type safety, Pointer safety, GC visibility guarantees. You gain: Speed, Control, Zero-copy tricks, etc. Risk: Crashes, Memory corruption, GC bugs. 
  - In Go, how fast you allocate matters more than how much memory you use. 
  - new(T) vs make(T)
    - In summary:
      - new: Allocates memory, Returns *T, Does NOT initialize runtime structures
      - make: Allocates + initializes, Returns T, Used for: slices, maps, channels
    - In detail: (Consider slices data structure as example)
      - Arrays in Go are static data structures with a fixed type and size. Slices are dynamic and built on top of arrays, defined by three components:
        - Data: pointer to the underlying array
        - Len: length of the slice
        - Cap: capacity of the slice (max length or array size)
      - Difference:

      | Feature | `new` | `make` |
      |-------|-------|--------|
      | **Purpose** | Allocates memory but does not initialize runtime structures (memory is zeroed) | Allocates **and initializes** slices, maps, and channels |
      | **Return value** | Pointer to zeroed memory of type `T` (`*T`) | Initialized (non-zero) value of type `T` |
      | **Slice underlying array** | Not allocated; pointer is `nil` | Allocates underlying array with specified length and capacity |
      | **Resulting slice** | `nil` slice (no backing array) | Non-`nil` slice with backing array |
      | **Usage** | Returns a pointer → needs dereferencing | Returns the value directly |
      | **Applicable types** | Any type (`struct`, `int`, `array`, etc.) | Only `slice`, `map`, `channel` |
      | **Ready to use?** | Often **not usable directly** | **Immediately usable** |

      - **Zeroing** means setting allocated memory to the zero value of the type (discussed in Fundamentals sections as well): Numeric types- 0, String- empty string "", Boolean- false, Pointer/slice/map/channel- nil, Struct- all fields zeroed by their respective zero values. 
      - When using new for a slice, the slice’s data pointer is nil, meaning no underlying array is allocated.
      - When using make, the underlying array is allocated and initialized to its zero values, making the slice ready for use.
      - There is no difference in observable behavior. But performance-wise, there is, Nil slices (created with new) will trigger automatic memory allocations and array resizing when elements are appended, potentially causing overhead due to repeated allocations and copying. Slices created with make and a predefined capacity avoid repeated allocations since the underlying array is pre-allocated.
        
        ```
        Note:
        sMake := make([]string, 3, 5)
        This means:
        | Property                  | Value      |
        | ------------------------- | ---------- |
        | Type                      | `[]string` |
        | Length (`len`)            | `3`        |
        | Capacity (`cap`)          | `5`        |
        | Underlying array size.    | `5`        |
        Visually:
        Underlying array (size = 5)
        +---------+---------+---------+---------+---------+
        |   ""    |   ""    |   ""    |    ?    |    ?    |
        +---------+---------+---------+---------+---------+
          ↑         ↑         ↑
          |--------- len=3 ---|
          |--------------- cap=5 ----------------|
        First 3 elements exist and are initialized ("")
        Last 2 slots exist but are not part of the slice yet

        Length (len): Number of elements you can access, Valid indices: 0 → len-1, Anything beyond len cannot be indexed. 
        Capacity (cap): Total space available before reallocation, How much you can grow using append without allocating new memory. 

        Now, if we do: sMake = append(sMake, "a"), sMake = append(sMake, "b")
        +---------+---------+---------+---------+---------+
        |   ""    |   ""    |   ""    |  "a"    |  "b"    |
        +---------+---------+---------+---------+---------+
        If you append beyond capacity. What Go does internally (also called Reallocation): 
        > Allocate a new, bigger array
        > Copy old elements
        > Append new element
        > Point slice header to new array
        > Old array is garbage-collected
        Capacity growth strategy is not guaranteed — don’t depend on exact numbers. 
        Very common pattern to initialize in Go: s := make([]T, 0, N) -> Means I have no elements yet, but I know how many I’ll need.
        ```

### Phase 4

Go - Error handling 

- Error handling  
  - defer: schedules a function call to run when the surrounding function returns, in other words defer runs after return is executed, but before the function actually exits. It executes in LIFO order. Although, avoid using it in extreme tight loops. Using defer to clean up resources is very common in Go. 
    
    ```
    Eg 1: 
    func main() {
      defer fmt.Println("world")
      fmt.Println("hello")
    }
    Output: 
    hello
    world

    Eg 2: 
    func main() {
      defer fmt.Println(1)
      defer fmt.Println(2)
      defer fmt.Println(3)
    }
    Output: 
    3
    2
    1
    ``` 
    - Note: **Immediately Invoked Function Expression** (IIFE) allows you to define a function without a name and execute it at the same moment. Use func() { }() only if you need at least one: go, defer, isolated scope, closure over variables, inline one-time logic. Else direct code. 
      
      ```
      Eg: 
      func(msg string) {
        fmt.Println(msg)
      }("Hello Go")
      > Breakdown:
          func(msg string) → define function
          { ... } → logic
          ("Hello Go") → pass arguments & execute
      > With go keyword → run function in new goroutine
      > defer needs a function
          Invalid: 
            defer file.Close()
          Valid: 
            defer func() {
              file.Close()
              db.Disconnect()
            }()
      ``` 

  - panic: immediately stops normal execution of the current goroutine and begins stack unwinding. There are certain operations in Go that automatically return panics and stop the program like indexing an array beyond its capacity, performing type assertions, etc. We can also generate panics of our own using the panic built-in function. It’s a last-resort mechanism for programmer errors or truly unrecoverable states. Only the panicking goroutine unwinds its stack (will learn about this in ex).
    - Deferred functions or other goroutines still run. 
    - Program crashes unless the panic is 'recovered'. `recover()` stops stack unwinding and only works inside a deferred function.
    - Note that if the caller can handle it → return an error. If the program is broken → panic.
      
      ```
      Ex 1: 
      func main() {
        panic("something went wrong")
      }
      Output: panic: something went wrong

      Ex 2: 
      func main() {
        defer fmt.Println("cleanup")
        panic("boom")
      }
      Output: 
      cleanup
      panic: boom

      Ex 3: Unwinding of stack: 
      Normal function calls: f1 → f2 → f3 → return → return → return
      Assume in panic: f1 → f2 → f3 → panic 
      At this point: 
        Go stops normal execution
        Go says: “I am not returning normally”
        Go enters panic mode
        The call stack looks like this at panic time:
        [f3 stack frame]  ← panic here
        [f2 stack frame]
        [f1 stack frame]
        Stack unwinding means: Go starts destroying stack frames one by one, from top to bottom.
        But before destroying each frame, Go runs its defers.
        Hence sequence: 
        panic →
        run defers of f3 →
        remove f3 frame →
        run defers of f2 →
        remove f2 frame →
        run defers of f1 →
        remove f1 frame →
        (no more frames)
        → program crash

      Ex 4: 
      func f3() {
        defer func() {
            fmt.Println("f3 defer")
        }()
        panic("boom")
      }
      func f2() {
        defer fmt.Println("f2 defer")
        f3()
      }
      func f1() {
        defer fmt.Println("f1 defer")
        f2()
      }
      func main() {
        f1()
      }
      Execution timeline: 
      panic in f3
      ↓
      run f3 defer
      ↓
      destroy f3 frame
      ↓
      run f2 defer
      ↓
      destroy f2 frame
      ↓
      run f1 defer
      ↓
      destroy f1 frame
      ↓
      no recover → crash
      Our crash could cascade all the way down. 
      Panic should be used in cases of: programmer errors, impossible states, initialization failures. Else errors. 
      Now add recover:
      func f3() {
          defer func() {
              if r := recover(); r != nil {
                  fmt.Println("recovered:", r)
              }
          }()
          panic("boom")
      }
      Execution now: 
      panic in f3
      ↓
      run f3 defer
      ↓
      recover() stops panic
      ↓
      f3 returns normally
      ↓
      f2 continues
      ↓
      f1 continues
      ↓
      program continues
      Stack unwinding stops immediately at the recover point. 
      Note: Recover only stops panics in the same goroutine
      ```

  - In Go, all failures fall into two buckets:
    - Bucket A — Expected, possible, recoverable. Handled with error. These are things that can legitimately happen even if your code is perfect. Examples:
      - File not found
      - Invalid user input
      - Network timeout
      - Permission denied
      - API returned 500
      - Database connection lost
      - JSON malformed from external source
        
        ```
        data, err := os.ReadFile("config.json")
        if err != nil {
            return err
        }
        ```

    - Bucket B — Impossible, programmer mistake, corrupted state. Handled with panic. These are situations where continuing makes no sense. Examples:
      - Index out of bounds
      - Nil pointer dereference
      - Map accessed concurrently without lock
      - Invariant violated
      - Impossible switch case
        
        ```
        if user == nil {
          panic("user must never be nil here")
        }
        ```

    - Should everything else use panic/defer/recover?: No. It happens rarely, but good to know. Use error for 99% of cases. panic for impossible cases. Most panic calls are added after a bug is discovered in production or during testing. The evolution of code from a "crashing bug" to a "robust feature" usually follows this three-stage lifecycle:
      - The Implicit Crash (The "Unknown" Phase)
        - The Bug: You assume data is perfect (e.g., a pointer is never nil).
        - The Result: The Go Runtime panics for you with a generic error (e.g., "nil pointer dereference").
        - The Outcome: Hard to debug; the program stops without explaining why the state was invalid.
      - The Explicit Panic (The "Defensive" Phase)
        - The Action: You add a manual if check that calls panic("descriptive message").
        - The Goal: To turn a "mysterious crash" into a clear assertion.
        - The Outcome: You’ve defined a "Programmer Error." You are signaling to other developers that they are using your function incorrectly.
      - The Graceful Error (The "Maturity" Phase)
        - The Action: You realize the "impossible state" might actually happen in production (e.g., a database record was deleted). You replace panic with return err.
        - The Goal: To move from crashing to communicating.
        - The Outcome: The program remains running. The caller now has the power to log the issue, retry, or show a friendly message to the user.

		```
      	Another ex: 
		func main() {
			divideByZero()
			fmt.Println("we survived dividing by zero!")
		
		}
		func divideByZero() {
			defer func() {
				if err := recover(); err != nil {
					log.Println("panic occurred:", err)
				}
			}()
			fmt.Println(divide(1, 0))
		}
		func divide(a, b int) int {
			if b == 0 {
				panic(nil)
			}
			return a / b
		}
	  	```

### Phase 5

Go - Concurrency 

- Concurrency
  - Go runs goroutines using its own scheduler on top of the OS scheduler. The OS schedules threads on CPU cores. The Go runtime schedules goroutines onto those threads using the G-M-P model, minimizing OS context switches and making concurrency cheap.
  - Python/Java use OS level threads which is heavy. Goroutine is NOT an OS thread. Under the hood (we would learn more):
    
    ```
    Millions of Goroutines
          ↓
    Go Scheduler
          ↓
    Few OS Threads
          ↓
    CPU Cores
    
    There is M:N scheduling. M goroutines & N OS threads. 
    ```

  - GMP Model: 
    - G – Goroutine: Lightweight execution unit; Starts with ~2KB stack; Millions possible; Scheduled by Go runtime
    - M – Machine (OS Thread): Real OS thread (pthread, etc.); Generally ~1MB; Scheduled by OS scheduler; Executes Go code only when it owns a P
    - P – Processor (Logical Processor): Go runtime abstraction; Holds: **Run queue of goroutines**, Scheduler context; Count = GOMAXPROCS
    - A goroutine runs only when an M holds a P.
      
      ```
      CPU Core
        ↓
      OS Scheduler → M (thread)
        ↓
      Go Scheduler → P → G (goroutine)
      ```

    - Assume configuration: Physical CPU cores = 4, Ps(GOMAXPROCS) = 10, OS threads (Ms) = 5. Gs could be say 100s. 
      - Maximum true parallelism = number of CPU cores. Hence, Max parallel execution = 4 goroutines
      - Ps do not map 1:1 to cores, they are logical. 
      - For Ps: At most 4Ms can be running simultaneously (one per core). Each running M must own 1P. So at most 4Ps can be active at a time. Remaining 6Ps are idle.
      - For Ms: OS scheduler runs 4Ms max. 1M will be waiting / sleeping. 
      - Having more Ms/Ps than physical capacity is waste of resources. 
  - In case of any blocking scenario: Goroutine blocks → Go detaches it; M runs another G; OS thread stays busy. 
  - Context switching: 
    - OS thread switch: Save registers, Kernel mode, Expensive. 100k threads -> impossible
    - Goroutine switch: User-space, Save small state, Very cheap. 100k goroutines -> fine
  - main() function is initial/default goroutine. 
    
    ```
    Sample Go routine: 
    func main() {
        sayHello("Alice") // Normal function call, assume it prints - blocks until complete
        go sayHello("Bob") // Goroutine - runs concurrently - simply add go keyword 
        time.Sleep(time.Second) // Without this sleep, main would exit before the goroutine runs hence you will not see "Bob" being printed
    }
    ```

    - When main exits, the entire program exits, killing all goroutines regardless of whether they've finished their work.
    - time.Sleep “works” but is wrong, for obvious reasons like although it gives time for goroutine to complete, you can't be guessing the timing, its flaky. We should wait for events, not time, which leads to concept of WaitGroups. 
  - WaitGroups: A sync.WaitGroup lets one goroutine wait until a set of goroutines finish.
    - Key rules:
      - Add(n) → number of goroutines to wait for
      - Done() → call once per goroutine
      - Wait() → blocks until counter reaches zero
    - Important: WaitGroup does NOT protect data. It only synchronizes completion
    
    ```
    Ex: 
    package main
    import (
      "fmt"
      "sync"
    )
    var wg sync.WaitGroup
    func sayHello(name string) {
      defer wg.Done()   // must be called once per goroutine
      fmt.Println("Hello", name)
    }
    func main() {
      names := []string{"Alice", "Bob", "Charlie", "Diana"}
      wg.Add(len(names)) // tell WaitGroup how many goroutines to wait for. Always call Add() before starting the goroutine
      for _, name := range names {
          go sayHello(name)
      }
      wg.Wait() // blocks until all Done() calls are made
      fmt.Println("All greetings printed")
    }

     **Goroutines interleave unpredictably. Hence the print order in above example may not be same as in list string**
    ```

    - For a WaitGroup, you must correctly account for every goroutine you want to wait for. WaitGroup is just a counter. What if goroutines ≠ wg.Add() count? Cases for count of: 
      - Waitgroups > Code Goroutines: wg.Wait blocks forever (logical deadlock), as counter doesn't reach 0.
      - Waitgroups < Code Goroutines: You get `panic: sync: negative WaitGroup counter`. 
    - What if number of waitgroups to add is unknown/unbounded?: Then WaitGroup may be the wrong tool. Better alternatives: Channel + close(), Worker pool with fixed workers, Context cancellation (discussed later). 
  - Mutex: A Mutual Exclusion lock ensures only one goroutine accesses critical data at a time. Helps in race conditions (concurrent access of data by multiple goroutines). In Java ecosystem, we use `volatile`/`synchronized` keywords. 
    
    ```
    Race condition: 
      func increment() {
          counter++
      }
      go increment()
      go increment()
      This may NOT produce 2. Read → modify → write is not atomic. 
      Although if we add waitGroups in this, you will get visible output, but that doesn't erase the fact that your code might be in race condition. Hence we use mutex locks. 
      Note: To know if your code is in race condition use: go run --race .
      Other example for race condition can be: Multiple goroutines calling APIs and appending result to some list. 
    ```

    - Basic Mutex: Lock before accessing shared data. Unlock immediately after. Using defer to unlock is a good practice. 
      
      ```
      var (
          counter int
          mu      sync.Mutex
      )
      func increment() {
          mu.Lock()
          counter++
          mu.Unlock()
      }
      ```

    - Types of Mutexes: 
      - sync.Mutex: Exclusive lock; Only one goroutine can access the critical section at a time; Simple, fast, commonly used. Limitation: Readers and writers are treated the same; Even read-only operations block each other
      - sync.RWMutex: Read-Write lock; Multiple readers allowed concurrently; Only one writer allowed; Writers block readers and other writers. If your program has many reads, less writes, use this. 
        
        ```
        Eg: 
        package main
        import (
          "fmt"
          "net/http"
          "sync"
        )
        var (
          wg      sync.WaitGroup
          mu      sync.Mutex
          signals []string
        )
        func getStatusCode(endpoint string) {
          defer wg.Done()
          res, err := http.Get(endpoint)
          if err != nil {
              fmt.Println("OOPS in endpoint")
              return
          }
          defer res.Body.Close()
          mu.Lock()
          signals = append(signals, endpoint)
          mu.Unlock()
          fmt.Printf("%d status code for %s\n", res.StatusCode, endpoint)
        }
        func main() {
          endpoints := []string{
              "https://google.com",
              "https://github.com",
              "https://golang.org",
          }
          wg.Add(len(endpoints)) // MUST be before starting goroutines
          for _, ep := range endpoints {
              go getStatusCode(ep)
          }
          wg.Wait() // blocks until all wg.Done() calls complete
          fmt.Println("Signals:", signals)
        }
        What happens: 
        1. wg.Add(len(endpoints)) - Tells WaitGroup how many goroutines to wait for.
        2. go getStatusCode(ep) - Launches each HTTP call concurrently.
        3. defer wg.Done() inside getStatusCode - Signals completion of one goroutine.
        4. mu.Lock() / mu.Unlock() - Protects shared slice signals from data races.
        5. wg.Wait() - Blocks main() until all HTTP calls finish.
        ```

  - Channels: 
    - Go provides three major concurrency tools: sync.Mutex, sync.WaitGroup, channels - each solving a different class of problem. 
      - What Mutex and WaitGroup Actually Solve: 
        - sync.Mutex: Protects shared memory, Ensures exclusive access, Prevents data races.
        - sync.WaitGroup: Waits for goroutines to finish execution, Does NOT pass data, Does NOT control access
    - Channel is a typed conduit through which goroutines communicate. Eg: `ch := make(chan int)`. 
      - Think of a channel as: A thread-safe queue (like a message passing queue); With built-in blocking (for backpressure handling from producer-consumer); That transfers data + control. 
      - Philosophy: Do not communicate by sharing memory, share memory by communicating.
      - They guarantee synchronization at the point of communication, not global ordering.
        - Send: `ch <- value`
        - Receive: `value := <-ch`. Note only `<-` symbol exists. 
        - Close: `close(ch)`. Only the sender (producer) should close the channel. (No more values will be sent, Receivers can still drain existing values)
          - If you read from a closed channel you get: 
            
            ```
            v, ok := <-ch 
            ok == false → channel is closed
            v → zero value
            ```
            
        - Channel Ownership:
		  
          ```
          // Compiler enforces ownership rules. You can restrict direction when passing a channel, but you cannot widen it again. Depending your use case, you may use bi-directional channel or restrict it 
		  func produceJobs(jobs chan<- int, n int) {
		    jobs <- 1      // ✅ allowed
			<-jobs         // ❌ compile-time error
		  }
          ```

    - Blocking Rules: 
      - Unbuffered Channel `ch := make(chan int)`: Send and Receive must happen at the same time like a handshake. Synchronization first, data second. If you send, but no receiver then its blocked (pending state), vice versa. Ex:
        
        ```
        go func() {
          ch <- 10
        }()
        fmt.Println(<-ch) // main goroutine listening from the subroutine which pushed data to some channel
        ```

      - Buffered Channel `ch := make(chan int, 2)`: Buffered channels decouple timing, but still synchronize.
        
        ```
        As seen above we initialized a channel of size 2. 
        ch <- 1 // ok
        ch <- 2 // ok
        ch <- 3 // blocks (buffer full)

        Other ex: Multiple Producers, Single Consumer
        ch := make(chan int)
        go func() { ch <- 1 }()
        go func() { ch <- 2 }()
        go func() { ch <- 3 }()
        for i := 0; i < 3; i++ {
            fmt.Println(<-ch)
        }
        All sends are received. Order is non-deterministic. If you want order to be deterministic, then of course a single sender must send data in guaranteed order. 
        ```

    - Blocked vs Deadlocked:
      - A goroutine is blocked when it is waiting for something. A program is deadlocked when: All goroutines are blocked, and no goroutine can ever make progress
      - In Go, the runtime's deadlock detector is only triggered when every single goroutine is blocked. As long as there is at least one "active" or "runnable" goroutine in the program's ecosystem, it will not panic, even if other goroutines are permanently blocked. 
      - Scenario 1: One sender, no receiver in main. If your main function (which is its own goroutine) tries to send to an unbuffered channel without a concurrent receiver, the program will panic immediately. Why? The runtime sees that the only goroutine in existence (the main one) is stuck. There is no other goroutine that could ever perform a receive to unblock it. Error: `fatal error: all goroutines are asleep - deadlock!`. 
      - Scenario 2: Two goroutines, one blocked, one "healthy" If you have one goroutine permanently blocked on a channel but another goroutine is still running (e.g., performing a long calculation or sleeping), the program will not panic. The "Healthy" Ecosystem: The runtime sees that progress is still being made elsewhere. It assumes the blocked goroutine might eventually be unblocked by the active ones.  
        - Goroutine Leak: This is considered a goroutine leak. The blocked goroutine will stay in memory forever, consuming resources until the entire program terminates naturally.
  
    - Solving a problem using Mutex + Waitgroups vs Channels
      
      ```
      Eg 1: 
      -- Mutex+Waitgroup:
      var (
      mu      sync.Mutex
      wg      sync.WaitGroup
      results []int
      )
      func worker(n int) {
        defer wg.Done()
        mu.Lock()
        results = append(results, n*n)
        mu.Unlock()
      }
      func main() {
        for i := 1; i <= 5; i++ {
            wg.Add(1)
            go worker(i)
        }
        wg.Wait()
      }
      -- Channels: 
      jobs := make(chan int)
      results := make(chan int)
      go func() {
        for i := 1; i <= 5; i++ {
            jobs <- i
        }
        close(jobs)
      }()
      go func() {
        for job := range jobs {
            results <- job * job
        }
        close(results)
      }()
      for res := range results {
        fmt.Println(res)
      }

      > Also imagine, if we had a case for backpressure, creating that only using Mutex would be difficult. 

      Differences: 
      | Feature             | Mutex | WaitGroup | Channel |
      | ------------------- | ----- | --------- | ------- |
      | Protect memory      | ✅     | ❌        | ❌      |
      | Wait for completion | ❌     | ✅        | ✅      |
      | Transfer data       | ❌     | ❌        | ✅      |
      | Enforce order       | ❌     | ❌        | ✅      |
      | Backpressure        | ❌     | ❌        | ✅      |
      | Lifecycle signaling | ❌     | ❌        | ✅      |

      Eg 2:
      -- Mutex + Waitgroup 
      Consider earlier example related to APIs, pseudocode: 
      func main() {
        endpoints := []string{
            "https://google.com",
            "https://github.com",
            "https://golang.org",
        }
        wg.Add(len(endpoints))...}...
        // If we reimagine it with channels (below)
      -- Channel  
      import (
      "fmt"
      "net/http"
      )
      func getStatusCode(endpoint string, ch chan<- string) {
        res, err := http.Get(endpoint)
        if err != nil {
            fmt.Println("OOPS in endpoint")
            return
        }
        defer res.Body.Close()
        fmt.Printf("%d status code for %s\n", res.StatusCode, endpoint)
        ch <- endpoint // send result
      }
      func main() {
        endpoints := []string{
            "https://google.com",
            "https://github.com",
            "https://golang.org",
        }
        ch := make(chan string)
        for _, ep := range endpoints {
            go getStatusCode(ep, ch)
        }
        var signals []string
        for i := 0; i < len(endpoints); i++ {
            signals = append(signals, <-ch)
        }
        fmt.Println("Signals:", signals)
      }
      What did it replace?: // Receiving N values is equivalent to waiting for N goroutines.
      | Old          | New                                   |
      | ------------ | ------------------------------------- |
      | `WaitGroup`  | Receive loop (`len(endpoints)` times) |
      | `Mutex`      | Single owner of data                  |
      | Shared slice | Message passing                       |
      | `wg.Done()`  | `ch <- value`                         |
      | `wg.Wait()`  | `<-ch` loop                           |
      ```

    - When to Use Channels: 
      - Goroutines need to communicate
      - Execution order matters
      - You want backpressure
      - You want pipeline or worker pool
      - You want clean shutdown signaling 
  - Select: It allows a goroutine to wait on multiple channel operations simultaneously, executing whichever becomes ready first, with optional non-blocking behavior via default.
    - If no case is ready and no default exists, select blocks.
    - Even if multiple cases are ready, Go executes only one.
    - If multiple cases are ready: Go picks one at random, this prevents starvation.
    - default case prevents blocking
    
    ```
    Ex1: 
    select {
    case msg := <-ch1: // Receive case is ready when ch1 has a value already available/ ch1 is closed
        fmt.Println(msg)
    case ch2 <- 10: // Send case is ready when ch2 has buffer space /there is a receiver already waiting
        fmt.Println("sent")
    default: // default is ready when no other case is ready
        fmt.Println("nothing ready")
    }

    Ex2: Fan-in (Multiple Inputs → One Output)
    select {
    case v := <-worker1:
        fmt.Println("worker1:", v)
    case v := <-worker2:
        fmt.Println("worker2:", v)
    }
    ```

  - context.Context: It is a signal carrier carrying cancellation/deadline/request-scoped signals. Imagine: A request comes in and you start 5 goroutines to process it, but the user disconnects or request times out; Now how to stop all those goroutines? We can't kill goroutines or force stop functions, hence Go gives you cooperative cancellation. Syntax: `ctx := context.Background()`. Note: 
    - Any function that blocks or loops must listen to ctx.Done(). 
    - Cancellation propagates downward, never upward. parent → child → grandchild. If grandchild cancels(), parent is unaffected. This prevents goroutine leaks/zombie process, etc. 
    
    ```
    Ex 1:
    func worker(ctx context.Context) {
      for {
        select {
        case <-ctx.Done():
          fmt.Println("worker stopped:", ctx.Err())
          return
        default:
          fmt.Println("working...")
          time.Sleep(500 * time.Millisecond)
        }
      }
    }
    func main() {
      ctx, cancel := context.WithCancel(context.Background())
      go worker(ctx)
      time.Sleep(2 * time.Second)
      cancel() // broadcast stop signal
      time.Sleep(1 * time.Second)
      fmt.Println("main exits")
    }
    What it does: 
      context.WithCancel creates: ctx, a hidden done channel
      Worker runs and selects on ctx.Done()
      cancel() is called
      ctx.Done() closes. Note: This blocks forever until someone cancels, then it unblocks immediately for ALL goroutines sharing the context, hence context scales.
      <-ctx.Done() unblocks instantly
      Worker exits cleanly
      No leak. Clean shutdown.

    Ex 2: 
    func fetchData(ctx context.Context) error {
    select {
      case <-time.After(3 * time.Second):
        fmt.Println("data fetched")
        return nil
      case <-ctx.Done():
        return ctx.Err()
      }
    }
    func main() {
      ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
      defer cancel()
      err := fetchData(ctx)
      fmt.Println("result:", err)
    }
    What it does: 
      main() — context creation: context.Background(), its root context (never cancels on its own). context.WithTimeout(...) creates: a child context, a timer, a Done channel. After 1 second, Go automatically calls cancel() internally.
      main and fetchData share the same context.
      Inside fetchData: time.After(3s) returns a channel that receives a value after 3 seconds. Until then → blocked. This represents slow work (API call, DB query, etc.)
      ctx.Done() is also a channel. It closes when the context is cancelled. Closing a channel unblocks all receivers immediately. 
      Its like: Try to finish work in 3s, but if the caller gives up in 1s — stop immediately.

    Ex 3: 
    Fan-Out (One → Many): Distribute work across multiple goroutines
      for i := 0; i < 4; i++ {
          go worker(jobs)
      }
    Fan-In (Many → One): Merge multiple result channels
      select {
      case r := <-c1:
      case r := <-c2:
      }
    ```

### Phase 6

Miscellaneous stuff in Go

- Testing: [Other doc](https://www.digitalocean.com/community/tutorials/how-to-write-unit-tests-in-go-using-go-test-and-the-testing-package)
  
  ```
  func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"both positive", 2, 3, 5},
        {"with zero", 0, 5, 5},
        {"negative", -1, 1, 0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := Add(tt.a, tt.b); got != tt.want {
                t.Fatalf("got %d, want %d", got, tt.want)
            }
        })
    }
  }
  ```

- Benchmarking: 
  
  ```
  func BenchmarkAdd(b *testing.B) {
      for i := 0; i < b.N; i++ {
          Add(2, 3)
      }
  }
  Command: go test -bench=.
  ```

- Fuzzing: It finds edge cases you didn’t think of.
  
  ```
  func FuzzParseInt(f *testing.F) {
    f.Add("123")
    f.Add("-1")
    f.Fuzz(func(t *testing.T, input string) {
        _, _ = strconv.Atoi(input)
    })
  }
  Command: go test -fuzz=.
  ```

- Race Detector
  
  ```
  var counter int
  go func() { counter++ }()
  go func() { counter++ }()
  Commands: 
  go test -race
  go run -race main.go
  ```

- Performance Profiling using pprof
  
  ```
  import _ "net/http/pprof"
  go http.ListenAndServe(":6060", nil)
  go tool pprof http://localhost:6060/debug/pprof/profile

  Runtime metrics: Use import "runtime/metrics"
  ```
- Tracing: It shows execution flow over time.
  
  ```
  trace.Start(os.Stdout)
  defer trace.Stop()
  go test -trace trace.out
  go tool trace trace.out
  ```
- Logging:
  
  ```
  import "log" or "slog"
  ```

- HTTP API Calls: [Interesting read](https://www.digitalocean.com/community/tutorials/how-to-make-http-requests-in-go)
  
  ```
  Use net/http package. It: 

  Creates a TCP listener
  Accepts connections
  For each connection: 
    Spawns a goroutine One goroutine per connection, not per request
    Parses HTTP requests
    Reuses the same connection (keep-alive)
    Dispatches to handlers
  Places you MUST set timeouts
    Server side
    http.Server{
        ReadTimeout:       5 * time.Second,
        ReadHeaderTimeout: 2 * time.Second,
        WriteTimeout:      10 * time.Second,
        IdleTimeout:       60 * time.Second,
    }
    Client side
    client := &http.Client{
        Timeout: 5 * time.Second,
    }
  ```

- Marshalling, sometimes also known as serialization, is the process of transforming program data in memory into a format that can be transmitted or saved elsewhere. The json.Marshal function, then, is used to convert Go data into JSON data.
- Similarly other things like Interface implementation patterns, Error design patterns, [Time related functions](https://www.digitalocean.com/community/tutorials/how-to-use-dates-and-times-in-go), etc. 

### Phase 7

Extras - gRPC, Protobuf


1. The Mental Model Shift — REST vs gRPC

When you use REST APIs, you think in terms of **resources and URLs**. You call `POST /users` or `GET /orders/123`. The URL is the thing you're targeting, and you manually define every route, handle the HTTP method, parse the JSON body, and write JSON back in the response. You own all of that plumbing.

gRPC flips this entirely. You think in terms of **functions (procedures)**. You're not hitting a URL — you're calling a method on a remote object, just like calling a function in your own code. The networking is abstracted away from you.

This concept is called **RPC — Remote Procedure Call**. The "remote" part means the function lives on another machine. The "procedure call" part means it feels like a local function to the caller. gRPC is Google's implementation of this idea, built on top of HTTP/2 and Protobuf.

So if you're coming from REST and wondering "what URL do I POST to?" — that question becomes irrelevant in gRPC. You just call a method. The framework handles the transport layer entirely.


2. What is Protobuf? (It's Actually Three Things)

Protobuf (short for Protocol Buffers) is where most confusion starts, because it is actually **three things bundled into one**, and people often only describe one of them.

**Thing 1 — A Schema Language (the `.proto` file)**: You write a `.proto` file that describes what your data looks like and what methods your service exposes. This is the "schema definition" or "schema validation" role. Think of it like TypeScript interfaces or a database schema — it defines the shape of your data and the contract between systems.

**Thing 2 — A Binary Encoding Format**: When your data actually travels over the network, Protobuf encodes it into a compact binary format. This is the "encode/decode" role — similar to what JSON does, but binary instead of human-readable text. The binary format uses field numbers (not field names) to identify fields, which is why it's significantly smaller and faster to parse than JSON.

**Thing 3 — A Code Generator**: You run the `protoc` compiler on your `.proto` file, and it automatically generates real working code (classes, methods, serializers, deserializers) in your language of choice — Python, Go, Java, Rust, etc. This is the "function generation" role. You never write the serialization logic by hand; protoc writes it for you.

All three of these are part of "Protobuf". That's the source of the confusion — when someone says "we use Protobuf", they mean all three things at once.


3. What is gRPC and What Does the Name Mean?

gRPC stands for **gRPC Remote Procedure Call** — yes, it's recursive, like GNU (GNU's Not Unix). The "g" technically changes with every version of the project and has meant things like "google", "good", "green", and "glorious" at different times. The important part is **RPC — Remote Procedure Call**.

gRPC is a **framework** built by Google that lets a program on one computer call a function on another computer as if it were a local function. It uses:

- **Protobuf** as the data format and schema system (though JSON is technically possible)
- **HTTP/2** as the transport layer (not HTTP/1.1)
- **Generated code** on both the client and server to handle all communication automatically

gRPC is particularly dominant in microservices architectures where many services need to talk to each other efficiently, because it offers strong type safety, very high performance, and an ergonomic developer experience once the initial setup is done.


4. Why gRPC Uses Protobuf Instead of JSON

gRPC can technically use JSON (there's a spec called gRPC-JSON transcoding), but almost nobody does, because Protobuf is the entire reason gRPC is worth using in the first place. Here's why Protobuf wins:

**Speed.** Binary formats are much faster for machines to parse than text-based formats. A machine reading a Protobuf message doesn't need to scan for quote characters, parse key names as strings, or handle escape sequences. It reads field numbers and jumps directly to the data.
  - Sidenote: A major performance advantage comes from HTTP/2 itself. Unlike typical REST setups using HTTP/1.1, gRPC uses persistent connections, multiplexed streams, header compression (HPACK), and efficient binary framing. This reduces repeated TCP handshakes, avoids many head-of-line blocking problems, and improves bandwidth utilization under heavy load.

**Size.** Protobuf is significantly smaller than JSON. Consider sending `{ "name": "Alice" }` — as JSON that's roughly 16 bytes of payload (plus 400–800 bytes of HTTP/1.1 headers). As Protobuf binary, the same data is about 7 bytes, with HTTP/2 header compression further reducing the overhead. At scale, across millions of requests per day, this compounds dramatically.

**Strictness and Type Safety.** JSON is flexible to a fault — you can send a string where an integer was expected, include unexpected fields, or omit required ones, and the receiver might silently mishandle it. Protobuf's schema is enforced at compile time. The generated code enforces field types and schema structure, catching many integration bugs at development time instead of production.

**Schema as Documentation.** With JSON REST APIs, you typically need separate documentation (OpenAPI/Swagger specs, Postman collections, Confluence pages) to describe what fields are expected. With Protobuf, the `.proto` file *is* the documentation, the contract, and the SDK generator all at once.

**Protobuf Evolution & Compatibility**: Once deployed, field numbers are part of your contract and must never change. Safe changes: adding new fields, adding new RPC methods. Breaking changes: changing a field number, reusing a deleted field number, changing a field type. If a client adds a field the server doesn't know about, the server silently ignores it. If a client removes a field, the server sees the default value. If either side changes a field type, you get decode failures or silent data corruption.


5. The .proto File — The Contract

Everything in gRPC starts with a `.proto` file. Think of it as a **contract between the server and the client** — like a restaurant menu that both the waiter and the kitchen agree on before any order is placed. Here is a full example with explanations inline:

```protobuf
// greeter.proto

syntax = "proto3";  // Tells the compiler which version of protobuf syntax to use.
                    // proto3 is the current standard.

// This defines the "service" — essentially a remote class with callable methods.
// Each "rpc" line is one callable endpoint/function.
service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
  //  ^ method name  ^ input message type  ^ output message type
  
  rpc SayGoodbye (GoodbyeRequest) returns (GoodbyeReply) {}
}

// A "message" is like a struct or class — it defines the shape of a request or response.
message HelloRequest {
  string name = 1;

  // The "= 1" is a FIELD NUMBER, not a default value.
  // Field numbers are the real identifiers used on the wire.

  // JSON sends field names repeatedly:
  // { "name": "Alice" }

  // Protobuf instead sends:
  // [field_number + wire_type] + [value bytes]

  // For this field:
  // string name = 1;
  //
  // if:
  // name = "Alice"

  // the binary payload becomes roughly:
  // 0A 05 41 6C 69 63 65

  // Where:
  // 0A -> field number 1 + wire type for length-delimited data
  // 05 -> string length (5 bytes)
  // 41 6C 69 63 65 -> ASCII bytes for "Alice"

  // Notice:
  // the string "name" never appears on the wire at all.

  // This is one reason protobuf messages are much smaller
  // and faster to parse than JSON.
}

message HelloReply {
  string message = 1;
}

message GoodbyeRequest {
  string name = 1;
}

message GoodbyeReply {
  string message = 1;
}
```

This single file simultaneously serves as your API documentation, your data schema, your type definitions, and the input to your code generator. Every other piece of the system is derived from it.


6. Code Generation — The Magic Step

Once you have your `.proto` file, you run the `protoc` compiler on it. This is what "code generation" means — protoc reads your schema and writes real, working code in your chosen language.

```bash
# For Python
protoc --python_out=. --grpc_python_out=. greeter.proto

# For Go
protoc --go_out=. --go-grpc_out=. greeter.proto
```

This generates two files (in Python's case):

**`greeter_pb2.py`** contains the Python classes for your messages — `HelloRequest`, `HelloReply`, `GoodbyeRequest`, `GoodbyeReply`. These classes have the serialization and deserialization logic baked in. You never write these by hand.

**`greeter_pb2_grpc.py`** contains two things. First, a **Stub class** for the client — this is the "remote control" object that has `SayHello()` and `SayGoodbye()` as methods you can call. Second, a **Servicer base class** for the server — this is the class you inherit from and implement with your business logic.

This is the "function generation" aspect of Protobuf. You defined `SayHello` in the `.proto` file, and now you have a real Python method `stub.SayHello(...)` to call without writing any of that infrastructure yourself.

What gRPC generates for you: client stubs, server interfaces, serialization/deserialization logic, transport plumbing.

What it does NOT generate: business logic, database access, validation rules, authorization, caching, observability.

You still write the actual application behavior yourself.


7. The Server — No net/http, No Manual Routes

This is one of the most important practical differences from REST. In a traditional Go REST server, you manually wire up every route:

```go
// REST way — you own all of this plumbing
mux := http.NewServeMux()
mux.HandleFunc("/users", handleUsers)       // manual route
mux.HandleFunc("/orders", handleOrders)     // manual route
http.ListenAndServe(":8080", mux)           // manual server start
```

With gRPC, you throw all of that away. **The gRPC server is your HTTP server.** It manages the port, the HTTP/2 connections, the routing, serialization, and deserialization. You only implement the business logic.

Here is a full Python gRPC server:

```python
# server.py
import grpc
import greeter_pb2        # generated message classes (HelloRequest, HelloReply, etc.)
import greeter_pb2_grpc   # generated service classes (Servicer base class)
from concurrent import futures

# You inherit from the generated Servicer base class and implement each method.
# This is YOUR business logic — the generated code handles all the networking.
class GreeterServicer(greeter_pb2_grpc.GreeterServicer):
    
    def SayHello(self, request, context):
        # "request" is already a HelloRequest Python object.
        # The binary Protobuf bytes were automatically deserialized for you.
        # You just work with normal Python objects.
        name = request.name  # e.g., "Alice"
        
        # You return a HelloReply object.
        # gRPC automatically serializes this back to binary before sending.
        return greeter_pb2.HelloReply(
            message=f"Hello, {name}! Welcome to gRPC."
        )
    
    def SayGoodbye(self, request, context):
        return greeter_pb2.GoodbyeReply(
            message=f"Goodbye, {request.name}. See you soon."
        )

# Standard boilerplate to start the server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# "Registering" your service is the gRPC equivalent of adding routes.
# But notice — you specify NO URLs. gRPC derives the routing from the proto schema.
greeter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)

server.add_insecure_port('[::]:50051')  # listen on port 50051
server.start()
server.wait_for_termination()
```

The `add_GreeterServicer_to_server` call does what `mux.HandleFunc(...)` was doing in REST — but instead of you specifying URL paths, gRPC automatically creates routes from the service and method names in your proto file. In normal application code, you rarely think about URLs, HTTP methods, or JSON parsing directly — the gRPC framework handles most transport concerns automatically.


8. The Client — Calling Remote Functions Like Local Ones

The client is where the RPC abstraction is most apparent. There is no URL construction, no `requests.post()`, no JSON serialization, no response parsing. You just call a method:

```python
# client.py
import grpc
import greeter_pb2
import greeter_pb2_grpc

# Step 1: Open a connection to the server (equivalent of creating an HTTP session)
channel = grpc.insecure_channel('localhost:50051')

# Step 2: Create a Stub — this is your "remote control" object.
# It has SayHello() and SayGoodbye() as real callable methods.
stub = greeter_pb2_grpc.GreeterStub(channel)

# Step 3: Call the remote method exactly like a local function.
# Under the hood: creates a HelloRequest, serializes to binary,
# sends over HTTP/2, receives binary response, deserializes to HelloReply.
# You see none of that — it's all handled by the generated code.
response = stub.SayHello(greeter_pb2.HelloRequest(name='Alice'))

print(response.message)  # Output: "Hello, Alice! Welcome to gRPC."

# Calling a second method is just calling another method — no new config needed
farewell = stub.SayGoodbye(greeter_pb2.GoodbyeRequest(name='Alice'))
print(farewell.message)  # Output: "Goodbye, Alice. See you soon."
```

From the developer's perspective, `SayHello` feels like a local function. The fact that it's making a network call to another machine — serializing your object to binary, sending it over HTTP/2, receiving a binary response, and deserializing it back — is entirely invisible to you.


9. Where Does the HTTP Request Actually Go?

This is the question that trips up developers coming from REST: "If there's no URL, where does the request go?"

The answer is that gRPC **does** use HTTP/2 under the hood, and there **is** a URL — but it's automatically derived from your proto schema, and you never write it yourself. The pattern is always:

```
POST https://<host>:<port>/<PackageName>.<ServiceName>/<MethodName>
```

So for the `SayHello` call in our example, the actual HTTP/2 request that goes over the wire is:

```
POST http://localhost:50051/Greeter/SayHello
Content-Type: application/grpc
[binary protobuf body — NOT JSON]
```

The body is the binary-encoded `HelloRequest`. It is not JSON. It's a compact sequence of bytes that only makes sense if you have the proto schema to decode it.

You never write this URL. You never serialize the body. gRPC generates this mapping from your `.proto` file and handles it automatically. This is the fundamental difference from REST — in REST, *you* design and manage the URLs. In gRPC, the framework owns the transport layer entirely.

gRPC Communication Patterns: So far we've only looked at unary RPC — one request, one response, exactly like a REST call. But gRPC supports three other patterns that REST simply cannot do without bolting on WebSockets or long-polling:

Server streaming — client sends one request, server streams back many responses over the same connection. Useful for live logs, real-time metrics, or replacing paginated polling.

Client streaming — client streams many requests, server replies once. Useful for batch uploads or telemetry ingestion where you want one connection rather than thousands of small HTTP calls.

Bidirectional streaming — client and server stream independently and simultaneously over one persistent connection. This is the natural fit for chat systems, real-time collaboration, or online gaming — use cases where REST would push you toward WebSockets.

These patterns are defined directly in the .proto file using the stream keyword:

```
service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}                            // unary
  rpc StreamUpdates (UpdateRequest) returns (stream UpdateResponse) {}           // server streaming
  rpc UploadChunks (stream ChunkRequest) returns (UploadReply) {}               // client streaming
  rpc Chat (stream ChatMessage) returns (stream ChatMessage) {}                 // bidirectional
}
```


10. Both Sides Must Speak gRPC

This is a critical architectural point. Unlike REST — where any client (a browser, curl, Postman, a Python script using `requests`) can talk to any server because everyone agrees on HTTP/1.1 + JSON — **gRPC requires both sides to understand the same protobuf contract.**

The client needs the generated stub code so it knows how to serialize a `HelloRequest` into binary and send it over HTTP/2. The server needs the generated servicer code so it knows how to deserialize that binary back into a real object and route it to the right method. If either side doesn't have the generated code from the `.proto` file, they literally cannot communicate — the binary format is meaningless without the schema to interpret it.

This is why in companies running microservices with gRPC, teams publish their `.proto` files to a **shared repository** (often called a "proto registry" or "buf registry"). Every team that wants to call your service pulls your `.proto` file, runs `protoc` in their language, and gets a fully working, type-safe client. The `.proto` file is your API documentation, your contract, and your SDK generator all in one.


11. Adding New Endpoints

Adding a new "endpoint" in gRPC means adding a new `rpc` line in your `.proto` file. The workflow is clean and consistent every time.

**Step 1 — Update the proto file.**

```protobuf
service Greeter {
  rpc SayHello   (HelloRequest)   returns (HelloReply)   {}
  rpc SayGoodbye (GoodbyeRequest) returns (GoodbyeReply) {}  // New endpoint — just one line
}

// Add the new message types
message GoodbyeRequest {
  string name = 1;
}

message GoodbyeReply {
  string message = 1;
}
```

**Step 2 — Regenerate the code** by re-running `protoc`. The generated stub and servicer now automatically include `SayGoodbye` on both the client side and the server side.

**Step 3 — Implement the method on the server.** In strongly-typed languages like Go, the compiler will actually *refuse to compile* until you implement every method declared in the proto service. This prevents you from accidentally shipping a server with unimplemented endpoints — a guarantee REST has no equivalent for.

```python
class GreeterServicer(greeter_pb2_grpc.GreeterServicer):
    
    def SayHello(self, request, context):
        return greeter_pb2.HelloReply(message=f"Hello, {request.name}!")
    
    # Must implement this now — gRPC framework will raise errors if you don't
    def SayGoodbye(self, request, context):
        return greeter_pb2.GoodbyeReply(message=f"Goodbye, {request.name}!")
```

**Step 4 — The client gets the updated `.proto` file**, regenerates, and can immediately call `stub.SayGoodbye(...)`. There is no API documentation to update, no Postman collection to edit, no URL to communicate to other teams. The proto file *is* all of that.

This is a significant developer experience win over REST, where adding a new endpoint means updating route handlers, updating documentation, updating any shared Postman collections, and manually communicating the change to all consumers.


12. Error Handling in gRPC

gRPC defines its own application-level status codes on top of HTTP/2.

Common status codes include: OK, InvalidArgument, NotFound, Unauthenticated, PermissionDenied, Internal. 

These status codes are language-neutral and consistent across
all gRPC clients and servers.


13. Testing gRPC — The curl Equivalent

This is one of the real friction points when first moving to gRPC, because **`curl` simply does not work** with gRPC. The reason is straightforward: `curl` speaks HTTP/1.1 and sends plain text, but gRPC expects HTTP/2 and a binary protobuf body. If you tried to `curl` a gRPC endpoint, the server would reject the connection entirely.

The ecosystem has built dedicated tools that act as the curl equivalent for gRPC.

Option 1: grpcurl — The True curl Equivalent

`grpcurl` is a command-line tool that works almost identically to curl, but speaks gRPC natively. Install it inside your container and use it from the terminal.

```bash
# The gRPC equivalent of:
# curl -X POST http://localhost:8080/greet -d '{"name": "Alice"}'

grpcurl -plaintext -d '{"name": "Alice"}' localhost:50051 Greeter/SayHello
```

`grpcurl` accepts JSON as input, automatically converts it to the correct protobuf binary, sends it to the server, receives the binary response, and converts it back to JSON for you to read. So your testing experience still feels JSON-like, even though the actual wire format is binary.

The `-plaintext` flag means "skip TLS", which is standard in local/container development just like using `http://` instead of `https://`.

The Server Reflection Problem: `grpcurl` needs to know your proto schema to serialize JSON input correctly. It can't just send raw text the way curl can. You have two ways to solve this:

**Option A — Point grpcurl at your proto file:**

```bash
grpcurl -plaintext -proto greeter.proto -d '{"name": "Alice"}' localhost:50051 Greeter/SayHello
```

This works but requires the proto file to be accessible wherever you're running the command, which can be inconvenient inside containers.

**Option B — Enable Server Reflection (recommended).**

Server reflection is a built-in gRPC feature where your server advertises its own schema at runtime. You enable it once with two lines of code, and then `grpcurl` (or any tool) can query the server to discover its own API without needing the `.proto` file present.

In Go:
```go
import "google.golang.org/grpc/reflection"

grpcServer := grpc.NewServer()
pb.RegisterGreeterServer(grpcServer, &GreeterServicer{})
reflection.Register(grpcServer)  // One line to make the server self-describing
```

In Python:
```python
from grpc_reflection.v1alpha import reflection
from greeter_pb2 import DESCRIPTOR

service_names = (
    greeter_pb2_grpc.DESCRIPTOR.services_by_name['Greeter'].full_name,
    reflection.SERVICE_NAME,
)
reflection.enable_server_reflection(service_names, server)
```

Once reflection is enabled, you can explore your API from the command line without any proto files:

```bash
# List all available services — like browsing all your endpoints
grpcurl -plaintext localhost:50051 list

# Describe a service in detail — like reading API documentation
grpcurl -plaintext localhost:50051 describe Greeter

# Make an actual call — no proto file needed at all
grpcurl -plaintext -d '{"name": "Alice"}' localhost:50051 Greeter/SayHello

# Call the second method
grpcurl -plaintext -d '{"name": "Alice"}' localhost:50051 Greeter/SayGoodbye
```

> **Note:** Server reflection is best practice to enable in development and staging environments. You may want to disable it in production for security reasons, since it exposes your full API surface to anyone who can reach the port.

Option 2: GUI Tools (Postman, BloomRPC)

Postman now supports gRPC natively. You point it at your server (with reflection enabled, or by importing your proto file) and get a visual interface to fill in fields and call methods — exactly like using Postman for REST. `BloomRPC` is another dedicated gRPC GUI tool. These are great for exploratory testing but not useful inside a container via terminal.

### Option 3: Write a Small Test Client Script

Since `protoc` generates client code for you anyway, the most natural container-friendly approach is a small test script in the same language as your service:

```python
# test_client.py — run this directly inside the container
import grpc
import greeter_pb2
import greeter_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = greeter_pb2_grpc.GreeterStub(channel)

# Test SayHello
response = stub.SayHello(greeter_pb2.HelloRequest(name='Alice'))
print(f"SayHello: {response.message}")

# Test SayGoodbye
farewell = stub.SayGoodbye(greeter_pb2.GoodbyeRequest(name='Alice'))
print(f"SayGoodbye: {farewell.message}")
```

Run it with `python test_client.py` inside the container. This is especially valuable because it exercises the *exact same code path* your real clients will use, giving higher confidence than any command-line tool.


## 14. The Full Picture — End to End Flow

Here is what happens, step by step, from the moment you write a proto file to the moment a client gets a response:

```
1. You write greeter.proto
         │
         ▼
2. Run protoc compiler
         │
         ├──► greeter_pb2.py          (message classes: HelloRequest, HelloReply, etc.)
         └──► greeter_pb2_grpc.py     (GreeterStub for client, GreeterServicer for server)
                      │
         ┌────────────┴────────────┐
         │                         │
      CLIENT                    SERVER
      imports Stub               imports Servicer
      calls stub.SayHello()      implements SayHello() with business logic
         │                         │
         │   HTTP/2 POST           │
         │   /Greeter/SayHello     │
         │   [binary protobuf] ───►│
         │                         │ deserializes binary → HelloRequest object
         │                         │ runs your SayHello() method
         │                         │ serializes HelloReply → binary
         │◄─── [binary response] ──┘
         │
      deserializes binary → HelloReply object
      response.message is available as a normal Python string
```

The key insight is that the binary serialization, HTTP/2 transport, routing, and deserialization are all handled invisibly by the generated code and the gRPC framework. You write the schema, you write the business logic, and the framework handles everything in between.


## 15. Quick Reference Comparison — REST vs gRPC

| Concern            | REST                                | gRPC                                                       |
| ------------------ | ----------------------------------- | ---------------------------------------------------------- |
| API style          | Resource-oriented (`/users/123`)    | Procedure/function-oriented (`SayHello`)                   |
| Transport          | Usually HTTP/1.1                    | HTTP/2 by default                                          |
| Data format        | Usually JSON (text)                 | Usually Protobuf (binary)                                  |
| Schema required    | Optional                            | Strongly expected (`.proto` file)                          |
| Client setup       | Any HTTP client                     | Generated client/stub typically used                       |
| Routes/URLs        | Manually designed                   | Auto-derived from proto service/method                     |
| Code generation    | Optional                            | Core part of workflow via `protoc`                         |
| Streaming support  | Not native (usually WebSockets/SSE) | Built in (server/client/bidirectional)                     |
| Adding an endpoint | New route + handler + docs          | New `rpc` line + regenerate code                           |
| Testing            | curl, browser, Postman              | grpcurl, Postman gRPC, test client                         |
| Type safety        | Mostly runtime validation           | Compile-time contract enforcement                          |
| Performance        | Good                                | Typically lower latency and smaller payloads               |
| Browser support    | Native                              | Requires gRPC-Web or transcoding                           |
| Human readability  | Human-readable payloads             | Binary payloads not human-readable                         |
| Best for           | Public APIs, browser/mobile clients | Internal microservices, streaming, high-throughput systems |


When to use gRPC, and when not to
gRPC is often an excellent default for internal microservices, high-throughput systems, anything with low-latency requirements, and any use case involving streaming. It pays off most when strong contracts across teams matter — the proto file eliminates entire categories of miscommunication.
Avoid it when you're building a public API, when your clients are browsers (gRPC requires a proxy like gRPC-Web in browser environments), or when you have a simple CRUD service with no performance pressure and no streaming needs. REST is simpler to debug, easier to test ad-hoc, and universally supported — don't reach for gRPC just because it's faster.

-----------------------------------------------
