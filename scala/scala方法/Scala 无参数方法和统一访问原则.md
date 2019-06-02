#### Scala 无参数方法和统一访问原则
在 Scala 中当方法不需要接受参数时可定义成两种类型的方法

1. def width(): Int   空括号方法(empty-paren method)
2. def width: Int  无参数方法(parameterless method)

从语法上讲，Scala 在调用上面那种类型的方法时都可以统一用 obj.width 的方式，实际对于无参数方法是只能用 obj.width 的方式，而空括号方法，既可以用 obj.width 也可以用 obj.width() 的形式。

那么 Scala 在方法无须参数时是定义空括号方法还是无参数方法时有什么约定呢？

```
当方法没有副作用(side effect)时，定义成无参数方法；当方法会产生副作用时，定义成空括号方法
```

那么又该如何识别方法是否有副作用呢？一般来说有副作用的地方会在于其结果类型是否为 Unit。如果某个函数不返回任何有用的值，也就是说如果返回类型为 Unit，那么这个函数唯一能产生的作用就只能是产生某种副作用，例如改变对象内部的某种状态，或是向控制台的输出等。有副作用的方法就像是数据库的存储过程(一般用于更新数据)，无副作用的方法像是数据库的函数(一般用于查询得到数据)。

当然，你可以定义出返回 Unit 结果，但不产生某种副作的方法，显然这样的方法是毫无意义的。

为什么无参数方法约定用 obj.width 的方式来访问呢，因为这种方式首先让你感觉它只是在引用 obj 的 width 属性，不应给对象 obj 产生副作用的，这应该很好理解。

为什么空括号方法要用 obj.width() 的形式呢，其实就是我们人为的添加括号() 以助于识别出这个方法会产生某种副作用。这里用 obj.width() 不准确，方法是 obj.update() 会更形象些。

下面说下统一访问原则(uniform access principle)

对于无参数方法的方法形式 obj.width 又像是在直接引用 obj 对象的 width 属性，这种统一性就叫做统一访问原则，就是说客代码不应由‘属性’ 是通过字段实现还是方法实现而受影响。例如前面的 def width: Int 可以写成 val width: Int，然而 obj.width 访问形式不变。

由于 Java 中没有统一访问原则，所以关于是 string.length()，而不 string.length；是 array.length，而不是 array.length() 的问题会突然间让人很迷惑。有了统一访问原则的 Scala，以及结合 length 方法是无副作用的，就会直接写成 string.length 和 array.length，而犯不着为此犹豫不决。

还有像  obj.toString，obj.hashCode, "reg express".r 类似的方法就会自然而然的省略掉后面的括号。

Scala 鼓励使用将不带参数且没有副作用的方法定义为无参数方法的风格，即省略空括号。但是永远也不要定义没有括号的带副作用的方法，因为这让人看上去是在使用属性，其实是放置了一个陷阱，这就像 Java 的某个 getter 方法实现把对象内部的状态给改了一般。

且 Scala 也更偏向于提倡设计没有副作用代码的程序，一方面是为函数式风格和并发考虑，同时也更容易测试。比如方法中返回字符串 "Hello World!"，总比 println("Hello World!") 的代码好测试，要捕获 println("Hello World!") 还得用输出重定向。






https://blog.csdn.net/wisgood/article/details/51590144