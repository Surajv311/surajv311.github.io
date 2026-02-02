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

- Testing: 
  
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

- HTTP Calls: [Interesting read](https://www.digitalocean.com/community/tutorials/how-to-make-http-requests-in-go)
  
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
- Similarly other things like Interface implementation patterns, Error design patterns, Time related libraries, etc. 

### Phase 7

Extras - gRPC, Protobuf

- Protocol Buffers are:
  - A language‑neutral interface definition language (IDL). A binary serialization format. A schema + compatibility system. 
  - Protobuf files (`.proto`) define:
    - Services (RPC methods)
    - Request / Response message schemas
    - Field numbers (critical for compatibility)
    
    ```
    Example:
    syntax = "proto3";
    // Package name used inside the generated code
    package user.v1;
    // Where Go code will live
    option go_package = "github.com/example/project/gen/user/v1;userv1";
    // UserService exposes user-related RPCs
    service UserService {
      // Get a user by ID
      rpc GetUser(GetUserRequest) returns (GetUserResponse);
      // Create a new user
      rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
    }
    // Messages: Request for fetching a user
    message GetUserRequest {
      // Unique user identifier
      int64 id = 1;
    }
    ----------------------------------------------------------------
    __Note__: Observe we have marked field with number above. 
    They are the real identifiers of fields on the wire — not the field names. What goes on the wire (meaning the exact bytes that leave one machine and travel to another machine over the network):
    
    JSON sends names + values:
    {
      "id": 42,
      "name": "Alice"
    }
    Wire contains: "id" + ":" + "42" + "name" + ":" + "Alice" ...: Actual bytes: 7b 22 69 64 22 3a 34 32 2c 22 6e... 
  
    Protobuf sends (tag + type) + value:
    For id = 1 (int64): [ field_number << 3 | wire_type ] [ value bytes ]
    So on the wire it’s more like: 08 2A. No field names at all.
  
    > JSON "id":42: ~7 bytes, Protobuf id=1 → 42: bytes. This makes it much more compact than JSON. The numbers must not change, its part of contract. 
    > Serialization/Deserialization is also fast.  
    > Protobuf sends data as compact numeric keys and values. Client and server map those numeric keys to real field names using the shared schema. In other words: Protobuf compresses the “key” part of key-value data into tiny numbers, relying on a shared schema instead of repeating field names on the wire.
    ----------------------------------------------------------------
  
    // Response containing user data
    message GetUserResponse {
      int64 id = 1;
      string name = 2;
      string email = 3;
    }
    // Request for creating a user
    message CreateUserRequest {
      string name = 1;
      string email = 2;
    }
    // Response after user creation
    message CreateUserResponse {
      int64 id = 1; // newly generated ID
    }
    ```

    - The `.proto` file is the shared contract between client and server. Client and server compile against the same contract. Can live in:
      - Shared proto repo (best practice)
      - Published artifact (Go module, Maven package)
      - Copied into both repos (simpler teams)
    - Running `protoc` (stands for Protocol Buffer Compiler is the command-line tool used to generate source code from .proto definition - yes, you can generate pieces of code in your repository. Sample command for golang: `protoc --proto_path=SRC_DIR --go_out=DST_DIR FILENAME.proto`) generates:
      - Generated (Automatic): Client stubs (typed methods), Server interfaces, Serialization / deserialization logic, Network plumbing
        - You get two Go files: `user.pb.go` → messages (structs, serialization), `user_grpc.pb.go` → client & server interfaces. 
        - Consider the same previously shared proto file example (previous points) and assume you ran the command; Then:
  
        ```
        Generated code in user.pb.go

        type GetUserRequest struct {
        Id int64
        }

        type GetUserResponse struct {
          Id    int64
          Name  string
          Email string
        }

        type CreateUserRequest struct {
          Name  string
          Email string
        }

        type CreateUserResponse struct {
          Id int64
        }
        ------------------------------------
        Generated code in user_grpc.pb.go
        
        // Client interface
        type UserServiceClient interface {
          GetUser(
            ctx context.Context,
            in *GetUserRequest,
            opts ...grpc.CallOption,
          ) (*GetUserResponse, error)
          CreateUser(
            ctx context.Context,
            in *CreateUserRequest,
            opts ...grpc.CallOption,
          ) (*CreateUserResponse, error)
        }
        // Client constructor
        func NewUserServiceClient(cc grpc.ClientConnInterface) UserServiceClient

        // Client code implementation in real life, when you import the generated interfaces from proto files, eg:
        conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
        client := userv1.NewUserServiceClient(conn)
        resp, err := client.GetUser(ctx, &userv1.GetUserRequest{
          Id: 42,
        })

        // Server interface - You must implement the interface function
        type UserServiceServer interface {
          GetUser(
            context.Context,
            *GetUserRequest,
          ) (*GetUserResponse, error)
          CreateUser(
            context.Context,
            *CreateUserRequest,
          ) (*CreateUserResponse, error)
        }
        // Registration function
        func RegisterUserServiceServer(
          s grpc.ServiceRegistrar,
          srv UserServiceServer,
        )

        // Server code implementation in real life, when you import the generated interfaces from proto files, eg:
        type UserServer struct {
          userv1.UnimplementedUserServiceServer
        }
        func (s *UserServer) GetUser(
          ctx context.Context,
          req *userv1.GetUserRequest,
        ) (*userv1.GetUserResponse, error) {
          return &userv1.GetUserResponse{
            Id:    req.Id,
            Name:  "Alice",
            Email: "alice@example.com",
          }, nil
        }
        // Registration - It tells the gRPC server: When a request for this service + method comes in, call THESE Go functions.
        grpcServer := grpc.NewServer()
        userv1.RegisterUserServiceServer(grpcServer, &UserServer{})
        ```
  
      - NOT Generated (You Must Write): Business logic, Database access, Validation rules, Authorization, Caching, Observability
      - Hence backend and client teams accordingly implement their contract and business logic defined in protobuf. 
    - Schema Enforcement & Validation
      - REST + JSON: Parse JSON, Validate schema (Pydantic / Joi / etc.), Handle runtime errors.
      - gRPC + Protobuf: Binary decoded automatically, Schema enforced at compile time, No JSON parsing, No runtime schema validation needed. But business validation is still manual.
    - Protobuf Evolution & Compatibility Rules: 
      - Safe Changes (Backward Compatible): Add new fields in proto file, Add new RPC methods
      - Unsafe / Breaking Changes: Change field number, Reuse deleted field numbers, Change field type
    - What happens if client updates proto but server doesn't:

      | Change               | Result                      |
      | -------------------- | --------------------------- |
      | Client adds field    | Server ignores it           |
      | Client removes field | Server sees default value   |
      | Client changes type  | Decode failure / corruption |

- gRPC is
  - A high‑performance RPC (Remote Procedure Call) framework developed by Google. Built on HTTP/2. Uses Protocol Buffers (Protobuf) as default serialization format. Enables strongly‑typed, contract‑first APIs between services. 
  - Mental model: gRPC = calling a remote function as if it were a local function. We'll learn more. 
  - gRPC Error Handling: Uses status codes, not HTTP codes directly. Common codes: OK, InvalidArgument, NotFound, Unauthenticated, PermissionDenied, Internal.
  - gRPC Communication Patterns:
    - Unary (request → response)
    - Server streaming: Client sends one request, server streams many responses. Eg: Logs, Live metrics, Pagination replacement. No repeated HTTP calls, Continuous data flow. 
    - Client streaming: Client streams many requests, server sends one response. Eg: Batch uploads, Telemetry ingestion. Why fast: One connection, Reduced overhead. 
    - Bidirectional streaming: Client and server stream independently. Eg: Chat systems, Real-time collaboration, Online gaming. REST equivalent: WebSockets (extra complexity). 
  - REST supports only unary‑like behavior.
  - Transport layer differences: 
    - REST: Usually HTTP/1.1, Text-based JSON, One request–response per call, Limited multiplexing (means sending multiple independent streams of data or request over a single connection at the same time), Headers sent repeatedly, Often opens new TCP connections (unless keep-alive is tuned).
    - gRPC: Built on HTTP/2, Binary framing, Single long-lived/Persistent TCP connection so no TCP+TLS handshake per request, Multiplexed streams over one connection so no head-of-line blocking, Header compression (HPACK), Flow control at transport level
    - Result: Fewer TCP handshakes, Lower latency, Better bandwidth utilization, Much lower CPU cost, Smaller payloads so faster encode/decode (Protobuf). Although debugging in gRPC ecosystem is harder than REST. 
  - Can REST Use Protobuf?: Yes, but uncommon. Used when: Browser or external clients are required. Options:
    - REST with protobuf payloads (`application/x-protobuf`)
    - grpc‑gateway (REST → gRPC translation)
  - When to Use gRPC: 
    - Best for: Internal microservices, High‑throughput systems, Low latency requirements, Streaming use cases, Strong contracts across teams
    - Avoid when: Public APIs, Browser‑heavy clients, Simple CRUD apps

------------------------------------------------
