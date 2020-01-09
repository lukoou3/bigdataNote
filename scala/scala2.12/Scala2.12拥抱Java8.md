## Scala2.12拥抱Java8
`https://yanbin.blog/scala-2-12-java-8-sam-lambda/#more-8382`

### Scala2.12主要变化
Scala 从2.12版本只能运行在Java 8上。

Scala 2.12 带来的主要特性在于对 Java 8 的充分支持：

* Scala 可以有方法实现的 trait 直接编译为带默认方法的 Java 接口  
* Lambda 表达式无需生成相应的类，而是用到 invokedynamic 字节码指令(这个是 Java 7 加进来的新指令)  
* 最方便的功能莫过于终于支持 Java  8 风格的 Lambda，即功能性接口的 SAM(Single Abstract Method)  


带来的最大的变化是Scala和Java8实现Lambda、函数互操作。

在Scala代码中，可以使用=>表达式应用在Java Lambda表达式的位置。
```scala
//Scala code               
new Thread(() => println("running")).start
```

在Java代码中，可以使用Lamabda表达式作为函数对象应用在=>表达式的位置：
```java
//Java code                
scalaCollection.foreach(x-> x.toString())
```

不过在java中调用scala依然比较不方便，有诸多限制，比如Unit类型，隐士参数等在java中不管用，编译器会报错。

但是在scala中调用java却相当方便，终于可以快乐地在scala中调用java类时使用Lamabda表达式了。

之所以能这样替换，是因为Scala 2.12将lambda表达式编译的字节码和Java的字节码是一致的，而不是匿名函数的方式。
因此在Scala代码中，函数式接口（Functional interfaces,也叫SAM）都可以通过Scala的 =>实现。

### Scala 的 Lambda 内部实现
这儿主要是体验 Scala 如何使用 Java 8 风格的 Lambda. 在 Scala 2.12 之前，Scala 对 Lambda 的支持是为你准备了一大堆的 trait 类，有

* Function0, Function1, ...... Function22 (接收多个参数，返回一个值)   
* Product1, Product2, ...... Product22 (函数返回多个值，即 TupleX 时用的)  
* 类似的 Scala Tuple 的实现也是一堆的 Tuple1, Tuple2, ...... Tuple22.  

Scala 并不需要像 Java 那样区分 Function, Producer 和 Consumer，因为 Scala 的函数没有严格意义上区分是否有返回值，没有就是 Unit。

我们来看一下在 Scala 任意写一个 Lambda 生成了什么样的代码
```scala
val f1 = (a: Int, b: String) => a + b
```
如果查看在 sbt 项目的 target/scala-2.11/classes 中生成的字节码文件，发现上面一行生成的大致等效的代码如下(忽略细节)
```scala
Function f1 = new AbstractFunction2() {
    public final String apply(int a, String b) {
        return a + b;
    }
}
```
AbstractFunction2 是 scala.runtime 包中的类，它继承自 Function2 特质。

### Scala 2.12 之前对 SAM 的支持
但是对于想在 Scala 2.12 之前使用 Java 8 的功能性接口，写出来比 Java 8 还麻烦，必须要写成匿名类(和没有 Lambda 的 Java 一样)。因为 Scala 2.12 才是为 Java 8 而生的。

比如对于简单的声明一个 java.lang.Runnable 实例, 它是一个功能性接口，用 Java 8 可以这样写
```java
Runnable runnable = () -> {}
```

而 Scala 2.11 想要简单的写成如下方式是不行的
```scala
val runnable = () => {}   //这是不行的，它只是一个 Function0
val runnable: Runnable = () => {} //这样也不行，提示 () => Unit 不能赋给 Runnable 类型变量
val runnable = (Runnable) (() => {}) //强转也不行，Scala 不认识
```

正常情况下在 Scala 2.11 中创建一个 Runnable 实例需要这么写
```scala
val runnable = new Runnable {
  override def run(): Unit = ???
}
 
//所以启动一个线程需要这样
new Thread(new Runnable {
  override def run(): Unit = println("hello")
}).start()
```

是不是有一种似曾相识的感觉，和 Java 8 之前的写法如出一辙, 一点也没占上 Scala Lambda 的光。

其实 Scala 2.11 也是可以支持 Java 8 的 SAM 的，但只是一个实验性的特性，需要打开编译选项 `-Xexperimental`, 可以通过在 sbt 的 build.sbt 文件中加上一行
```
scalacOptions += "-Xexperimental"
```
来开启实验特性。同时若要让 IntelliJ IDEA 识别支持 SAM 的语法，也需要 IntelliJ IDEA 的 `Perferences/../Scala` Compiler 中勾选上 `Experimental Features` 选项框。如此在 Scala 2.11 中也可以写成
```scala
val runnable: Runnable = () => {}
new Thread(() => {}).start()
```
上面方法声明的 Runnable 与写成匿名类的方式是一样的了，内部也是实现为 Runnable 的匿名类。

这么一个简单例子打开实验选项来支持 SAM 还是可以的，但是在我经历的一个实际使用 Scala 2.11 的项目中试图打开实验选项却造成项目无法编译。所以实验性的东西需谨慎使用; 譬如说 Spark 2.2 官方并未声明能支持 Scala 2.12 的话，脱了裤子强行上就会有风险。

### Scala 2.12 对 SAM 的支持
现在已经没有惊喜了，就是在 Scala 2.11 中打开了 `-Xexperimental` 选项时的书写方式
```scala
val runnable: Runnable = () => {}
new Thread(() => {}).start()
```

只是到了在 Scala 2.12 中，`val runnable: Runnable = () => {}` 不再是生成一个实现了 Runnable 接口的匿名类，而是产生如下的字节码
```scala
0: invokedynamic #38,  0             // InvokeDynamic #0:run:()Ljava/lang/Runnable;
5: astore_2
```

### 实战自定义的 SAM
在 Scala 中我们可以定义一个抽象类或 trait
```scala
abstract class F2 {
  def foo(a: Int, b: String): String
}
 
//或者
trait F2 {
  def foo(a: Int, b: String): String
}
```

那么要声明一个 F2 实例的写法可以用
```scala
val f2: F2 = (a: Int, b: String) => a + b
 
//因为有 f2: F2 指定类型，所以参数列表中的类型可以省略
val f2: F2 = (a, b) => a + b
 
println(f2.foo(1, "100"))
```

如果不指定变量类型，只是声明为
```scala
val f2 = (a: Int, b: String) => a + b
f2.apply(1, "100")
```

那么 f2 只是一个 Function2 实例，因为没有上下文。这个和 Java 8 的 Lambda 类型推断差不多，只是 Scala 在无法确定类型的时候还那么多默认的 Function0, Function1, ...... Function22 可用。

同样，我们在给类型提供上下文时，比如方法参数的类型，也可以简化成 Java 8 那样的写法
```scala
//方法接受 F2 类型
def bar(f2: F2): String = f2.foo(1, "100")
 
//bar 方法参数中的 Lambda 会被推断为 F2 类型实例，而不会是 Function2
bar((a, b) => a + b)
```

说白了，就是 Java 8 怎么支持 SAM 的 Lambda, Scala 2.12 也是同样的语法风格，唯一不同的是参数列表与实现的分隔符分别是 `->` 与 `=>`。

