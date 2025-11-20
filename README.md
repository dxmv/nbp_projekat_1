# Poredjenje

## Gde se tacno nalaze rezultati?

**"How does the book implement string interning in the hash table, and what performance benefits does this optimization provide?"** - 

*"How does the book implement string interning in the hash table, and what performance benefits does this optimization provide?"* - Chapter 20, sekcija 5/

*"Why does jlox require a separate 'Resolver' pass before interpretation, and how does it use 'distance' (or hops) to fix the closure binding problem?"* - Chapter 11, sekcije 3,4,5/

## CrossRankingRAG

**Response:**
The book implements string interning in the hash table by using a sister function to `findEntry()`, called `tableFindString()`, which performs a hash table lookup for interning strings. This is done by using the `capacity` as a mask when wrapping the string's hash key.

The performance benefits of this optimization are significant. By interning strings, the equality operator on strings becomes much faster at runtime. This is because the hash table lookup allows for quick identification of duplicate strings, eliminating the need for character-by-character equality comparisons.

Additionally, the book notes that high-performance VMs for languages like JavaScript use sophisticated optimizations like "hidden classes" to avoid the overhead of hash table lookups. However, the optimization implemented in the book provides a good example of how to improve performance by reducing the overhead of hash table lookups.

It's also mentioned that walking the entire string to calculate the hash is kind of slow, and doing a hash table lookup for every field access is fast enough for many language implementations, but not ideal. The optimization implemented in the book helps to mitigate this issue by allowing for faster hash table lookups.

Overall, the optimization provides a significant performance benefit, especially when dealing with large numbers of strings. The trade-off is a small overhead when creating strings to intern them, but this is outweighed by the benefits of faster equality checks at runtime.

**Metadata:**
*   Chapter 30 | Section 30.2.2 | Page 581
*   Chapter 20 | Section 20.4 | Page 357
*   Chapter 12 | Section 12.3.1 | Page 197
*   Chapter 30 | Section 30.3.7 | Page 595
*   Chapter 20 | Section 20.5 | Page 371
*   Chapter 20 | Section 20.5 | Page 371
*   Chapter 20 | Section 20.4.1 | Page 359
*   Chapter 16 | Section 16.4 | Page 292
*   Chapter 20 | Section 20.4.2 | Page 360
*   Chapter 20 | Section 20.5 | Page 371

## HnswRAG

**Response:**
The book implements string interning in the hash table by automatically interning every unique string that is created. This means that whenever a new string is created, it is added to the table, which is used more like a hash set than a hash table, where the keys are the strings and the values are not important (in this case, `nil` is used).

The performance benefits of this optimization are:

1. **Faster equality checks**: With string interning, checking if two strings are equal becomes much faster, as it only requires comparing the pointers to the interned strings, rather than comparing the actual string characters.
2. **Improved performance in dynamically-typed languages**: In languages like Lox, where method calls and instance fields are looked up by name at runtime, fast string equality checks are critical. If string equality checks are slow, then looking up a method by name is slow, which can slow down the entire language.
3. **Reduced memory usage**: By deduplicating strings, string interning reduces the amount of memory used by the program, as multiple copies of the same string are not stored in memory.

Overall, the book's implementation of string interning in the hash table provides a significant performance optimization, especially in situations where strings are created and compared frequently.

**Metadata:**
*   Chapter 20 | Page 350
*   Chapter 20 | Section 20.4 | Page 357
*   Chapter 20 | Section 20.4.1 | Page 359
*   Chapter 20 | Section 20.4.3 | Page 362
*   Chapter 20 | Section 20.5 | Pages 367-368
*   Chapter 20 | Section 20.5 | Page 368
*   Chapter 20 | Section 20.5 | Pages 368-369
*   Chapter 20 | Section 20.5 | Page 371
*   Chapter 26 | Section 26.4.1 | Page 510
*   Chapter 30 | Section 30.2.2 | Page 581

## Time

*   **CrossRankingRAG:** 1.48 seconds
*   **HnswRAG:** 1.11 seconds

---

**Query:** *"Compare the parsing strategies of jlox and clox: which algorithms are used and how do they represent grammar rules?"*

## CrossRankingRAG

**Response:**
The parsing strategies of jlox and clox differ in their approach to recognizing keywords and representing grammar rules. 

In jlox, the parsing is done using a recursive descent approach. This involves defining a set of functions, each of which corresponds to a particular grammar rule. These functions consume tokens from the input stream and return a syntax tree that represents the parsed code.

In contrast, clox uses a combination of techniques, including Pratt's parsing algorithm, to parse the grammar rules. Pratt's algorithm is a top-down parsing technique that uses a set of parsing functions to recognize the grammar rules. This approach allows for more efficient parsing and better error handling.

In terms of representing grammar rules, jlox uses a more traditional approach, where each grammar rule is represented by a separate function. In clox, the grammar rules are represented using a more flexible data structure, which allows for easier modification and extension of the grammar.

Overall, the parsing strategy used in clox is more efficient and flexible than the one used in jlox, and it allows for better representation of complex grammar rules. However, both approaches have their own strengths and weaknesses, and the choice of parsing strategy depends on the specific requirements of the project.

It's worth noting that clox also uses predictive parsing, which can get tricky when dealing with complex grammars that require looking ahead a large number of tokens. However, the use of Pratt's algorithm and other techniques helps to mitigate this issue and provides a more efficient and effective parsing strategy. 

In summary, the main differences between the parsing strategies of jlox and clox are:

* jlox uses recursive descent, while clox uses a combination of techniques, including Pratt's algorithm
* jlox represents grammar rules using separate functions, while clox uses a more flexible data structure
* clox is more efficient and flexible than jlox, but may be more complex to implement.

**Metadata:**
*   Chapter 22 | Section 22.5 | Page 404
*   Chapter 16 | Section 16.3.3 | Page 291
*   Chapter 6 | Section 6.2.1 | Page 82
*   Chapter 17 | Section 17.2.1 | Page 302
*   Chapter 17 | Page 299
*   Chapter 17 | Section 17.1 | Page 300
*   Chapter 5 | Section 5.4 | Page 76
*   Chapter 6 | Section 6.4 | Page 90
*   Chapter 13 | Section 13.3.1 | Page 223
*   Chapter 6 | Section 6.1 | Page 80

## HnswRAG

**Response:**
The parsing strategies of jlox and clox differ in their approach to parsing and representing grammar rules. 

In jlox, the parsing strategy is not explicitly mentioned, but it is implied to be more complex and possibly less efficient. The text mentions that the author "cobbled together a mishmash of regular expressions and substring operations" in the past, which suggests that jlox may not have a sophisticated parsing algorithm.

In contrast, clox uses a more elegant and efficient parsing algorithm called "top-down operator precedence parsing", also known as Pratt parsing. This algorithm is used to parse expressions and handles prefix, postfix, infix, and mixfix operators, as well as precedence and associativity. The grammar rules in clox are represented as methods inside a class, where each method corresponds to a specific grammar rule. The parser consumes a flat input sequence of tokens and uses a "current" pointer to point to the next token to be parsed.

In terms of representing grammar rules, clox uses a more straightforward approach, where each grammar rule is translated directly into a Java method. This approach makes it easier to understand and maintain the parser. The text also mentions that the grammar is "dead simple" and that the translation to Java is straightforward.

Overall, the parsing strategy of clox is more sophisticated and efficient than that of jlox, and it uses a more elegant and scalable algorithm to represent grammar rules. The use of Pratt parsing in clox allows it to handle complex expressions and grammar rules in a more robust and maintainable way.

**Metadata:**
*   Chapter 5 | Section 5.4 | Page 76
*   Chapter 6 | Section 6.1 | Page 80
*   Chapter 6 | Section 6.2 | Page 81
*   Chapter 9 | Section 9.4 | Page 140
*   Chapter 15 | Section 15.3.1 | Pages 277-278
*   Chapter 16 | Section 16.4 | Page 297
*   Chapter 17 | Page 299
*   Chapter 17 | Page 299
*   Chapter 17 | Section 17.1 | Pages 299-300
*   Chapter 21 | Section 21.4 | Page 386

## Time

*   **CrossRankingRAG:** 2.08 seconds
*   **HnswRAG:** 1.25 seconds

---

**Query:** *"Why does jlox require a separate 'Resolver' pass before interpretation, and how does it use 'distance' (or hops) to fix the closure binding problem?"*

## CrossRankingRAG

**Response:**
Jlox requires a separate 'Resolver' pass before interpretation to resolve variable references and bind them to their corresponding declarations. This is necessary to avoid coupling between the interpreter and the resolver, which can lead to subtle bugs and make the code harder to maintain.

In the context of closures, jlox uses a concept called "distance" or "hops" to resolve variable references. When a variable is referenced inside a closure, the resolver needs to determine how many "hops" up the scope chain to look for the variable's declaration. This is done by keeping track of the distance between the variable reference and its declaration.

The resolver uses this distance information to bind the variable reference to its declaration, which helps to fix the closure binding problem. This problem occurs when a variable is referenced inside a closure, but its declaration is outside the closure's scope. By using the distance information, the resolver can correctly bind the variable reference to its declaration, even if it's outside the closure's scope.

In terms of performance, jlox's closures are not "free" because they require allocating all environments on the heap, which can lead to a significant performance price for local variables that are never closed over. However, the use of a separate resolver pass and the distance-based approach to binding variable references helps to mitigate this performance cost by ensuring that variable references are correctly bound and resolved.

It's worth noting that the provided text does not explicitly mention how the "distance" or "hops" are used to fix the closure binding problem, but it can be inferred that the resolver uses this information to correctly bind variable references to their declarations, which helps to resolve the closure binding problem. 

In the code, this is implemented in the `visitVariableExpr()` method in `lox/Interpreter.java` and `visitFunctionStmt()` method in `lox/Resolver.java`, where the resolver and interpreter work together to resolve variable references and bind them to their declarations. The `resolveFunction()` method in `lox/Resolver.java` is also relevant, as it replaces a single line to implement the resolver pass.

**Metadata:**
*   Chapter 11 | Section 11.2 | Page 174
*   Chapter 28 | Section 28.5.1 | Page 558
*   Chapter 15 | Section 15.2 | Page 264
*   Chapter 11 | Section 11.5.1 | Page 187
*   Chapter 11 | Section 11.3 | Page 175
*   Chapter 25 | Section 25.4.4 | Page 486
*   Chapter 11 | Section 11.5.1 | Page 188
*   Chapter 11 | Section 11.4.1 | Page 184
*   Chapter 25 | Section 25.4.4 | Page 487
*   Chapter 11 | Section 11.4.1 | Page 184

## HnswRAG

**Response:**
Jlox requires a separate 'Resolver' pass before interpretation to resolve variable bindings, which involves storing the binding between a variable and its declaration. This is necessary to minimize the collateral damage inflicted on the existing codebase and to make the most out of the existing Environment class.

The 'Resolver' pass uses 'distance' (or hops) to fix the closure binding problem by storing the resolution in a way that makes the most out of the existing Environment class. When the interpreter encounters a variable, it uses the 'distance' to determine which environment in the chain will have the variable. This is done using a helper method that walks a fixed number of hops up the parent chain and returns the environment there.

The 'distance' is used to calculate the number of hops up the parent chain to reach the environment where the variable is declared. This allows the interpreter to directly access the variable in the correct environment, rather than dynamically walking the chain of enclosing environments.

In the context of closures, the 'Resolver' pass is essential to handle cases where a closure accesses a variable declared in an outer function. By storing the 'distance' to the variable, the interpreter can correctly resolve the variable binding, even when the closure is created and the outer function has returned.

The use of 'distance' (or hops) in jlox helps to:

1. Avoid dynamic walking of the environment chain, which can lead to runtime errors if the variable is not defined.
2. Enable the interpreter to directly access the variable in the correct environment, making the code more efficient.
3. Handle closures that access variables declared in outer functions, which is essential for supporting first-class functions in the Lox language.

Overall, the 'Resolver' pass in jlox plays a crucial role in resolving variable bindings and handling closures, allowing the interpreter to correctly execute the code and provide a more efficient and robust implementation.

**Metadata:**
*   Chapter 11 | Section 11.1.2 | Page 173
*   Chapter 11 | Section 11.4 | Page 184
*   Chapter 11 | Section 11.4.1 | Pages 184-185
*   Chapter 12 | Section 12.3.2 | Page 199
*   Chapter 24 | Section 24.7 | Page 457
*   Chapter 25 | Page 458
*   Chapter 25 | Section 25.2.1 | Pages 468-469
*   Chapter 25 | Section 25.4.4 | Pages 486-487
*   Chapter 28 | Section 28.1.3 | Page 537
*   Chapter 28 | Section 28.2.3 | Page 542

## Time

*   **CrossRankingRAG:** 1.94 seconds
*   **HnswRAG:** 1.42 seconds

---
