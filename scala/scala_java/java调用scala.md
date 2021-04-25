
## scala中基本数据类型调用javaobject问题
java中参数为Integer、Object的scala中可以直接调用传入int

Object[]的必须传入Array[AnyRef]，里面不能有int，必须显示的使用java.lang.Integer

对于传入Object[]的方法，可以重写一个scala的方法，参数为Array[Any]，里面遍历数组调用java参数为Integer、Object的方法

**java中方法参数为object变参时，scala调用是必须显示的转any为AnyRef，或者传Array[Any], 传Any时编译时会报错；java中方法参数为object参数时编译没问题**

**java中方法参数为Object[]时，scala调用是必须显示传Array[AnyRef]，否则编译器就是报错, any_array.asInstanceOf[Array[AnyRef]]传入即可，Array[Any]编译时本来就是编译成Array[Object]**

**scala的Array和java的是一样的，不支持协变的，Array[Any]其实就是Array[AnyRef]，编译不通过大胆的asInstanceOf[Array[AnyRef]]。Array[Int]就是Array[Int]不能asInstanceOf[Array[AnyRef]]。不必担心Array[Any] asInstanceOf[Array[AnyRef]] 报错，Array[Int]不能被赋值成Array[Any]，因为数组是不支持协变的。**

```java
package basetype;

public class JavaObject {

    public static void testInteger(Integer a){
        System.out.println(a);
    }

    public static void testObject(Object a){
        System.out.println(a);
    }

    public static void testObjectArray(Object[] array){
        System.out.println(array);
    }
}

```

```scala
package basetype

object Test {

  def testJavaObjectArray(array: Array[Any]): Unit ={
    for (elem <- array) {
      JavaObject.testObject(elem)
    }
  }

  def main(args: Array[String]): Unit = {
    val list = Array[Any](1, "2", 3D)
    testJavaObjectArray(list)

    println("-----------------------")

    JavaObject.testInteger(1)
    JavaObject.testObject(1)

    val a = 2
    JavaObject.testInteger(a)
    JavaObject.testInteger(a)

    val array: Array[AnyRef] = Array[AnyRef](1:java.lang.Integer, "2", 3D:java.lang.Double)
    JavaObject.testObjectArray(array)

    val b = 3D
    val array1: Array[AnyRef] = Array[AnyRef](new java.lang.Integer(a), "2", new java.lang.Double(b))
    JavaObject.testObjectArray(array1)
  }

}
```

### 反编译查看
```java
package basetype;

import scala.*;
import scala.runtime.*;
import scala.reflect.*;
import scala.collection.*;

public final class Test$
{
    public static final Test$ MODULE$;
    
    static {
        new Test$();
    }
    
    public void testJavaObjectArray(final Object[] array) {
        Predef$.MODULE$.genericArrayOps((Object)array).foreach((Function1)new Test$$anonfun$testJavaObjectArray.Test$$anonfun$testJavaObjectArray$1());
    }
    
    public void main(final String[] args) {
        final Object[] list = (Object[])Array$.MODULE$.apply((Seq)Predef$.MODULE$.genericWrapArray((Object)new Object[] { BoxesRunTime.boxToInteger(1), "2", BoxesRunTime.boxToDouble(3.0) }), ClassTag$.MODULE$.Any());
        this.testJavaObjectArray(list);
        Predef$.MODULE$.println((Object)"-----------------------");
        JavaObject.testInteger(Predef$.MODULE$.int2Integer(1));
        JavaObject.testObject(BoxesRunTime.boxToInteger(1));
        final int a = 2;
        JavaObject.testInteger(Predef$.MODULE$.int2Integer(a));
        JavaObject.testInteger(Predef$.MODULE$.int2Integer(a));
        final Object[] array = { Predef$.MODULE$.int2Integer(1), "2", Predef$.MODULE$.double2Double(3.0) };
        JavaObject.testObjectArray(array);
        final double b = 3.0;
        final Object[] array2 = { new Integer(a), "2", new Double(b) };
        JavaObject.testObjectArray(array2);
    }
    
    private Test$() {
        MODULE$ = this;
    }
}
```

### Predef与BoxesRunTime
这都是编译器做的事
Predef
```scala
implicit def byte2Byte(x: Byte)           = java.lang.Byte.valueOf(x)
implicit def short2Short(x: Short)        = java.lang.Short.valueOf(x)
implicit def char2Character(x: Char)      = java.lang.Character.valueOf(x)
implicit def int2Integer(x: Int)          = java.lang.Integer.valueOf(x)
implicit def long2Long(x: Long)           = java.lang.Long.valueOf(x)
implicit def float2Float(x: Float)        = java.lang.Float.valueOf(x)
implicit def double2Double(x: Double)     = java.lang.Double.valueOf(x)
implicit def boolean2Boolean(x: Boolean)  = java.lang.Boolean.valueOf(x)

implicit def Byte2byte(x: java.lang.Byte): Byte             = x.byteValue
implicit def Short2short(x: java.lang.Short): Short         = x.shortValue
implicit def Character2char(x: java.lang.Character): Char   = x.charValue
implicit def Integer2int(x: java.lang.Integer): Int         = x.intValue
implicit def Long2long(x: java.lang.Long): Long             = x.longValue
implicit def Float2float(x: java.lang.Float): Float         = x.floatValue
implicit def Double2double(x: java.lang.Double): Double     = x.doubleValue
implicit def Boolean2boolean(x: java.lang.Boolean): Boolean = x.booleanValue
```

BoxesRunTime
```scala
public static java.lang.Integer boxToInteger(int i) {
    return java.lang.Integer.valueOf(i);
}

public static java.lang.Long boxToLong(long l) {
    return java.lang.Long.valueOf(l);
}

public static int unboxToInt(Object i) {
    return i == null ? 0 : ((java.lang.Integer)i).intValue();
}

public static long unboxToLong(Object l) {
    return l == null ? 0 : ((java.lang.Long)l).longValue();
}
```


## scala中基本数据类型的泛型
java中调用返回scala中基本数据类型的泛型，必须使用Object

```scala
object ScalaObject {
  def getMap:Map[Int, String] = Map(1 -> "a", 2 -> "b", 3 -> "c")
}
```
java中调用：
```java
//Map[Int, String]这里必须用Object
Map<Object, String> map = ScalaObject.getMap();
System.out.println(map);
```

## scala中抛出的异常方法
scala中抛出的异常方法默认不是像java中那样声明的，如果必须需要在java中处理异常需要加上注解：
```scala
object ScalaObject {
  //加上这个注解，java中就不得不处理这个异常了
  @throws[Exception]("params can not null")
  def getString(a:String, b:String) = {
    if(a == null || b == null)
      throw new Exception("can not null")
    a + b
  }
}
```

```java
try {
    str = ScalaObject.getString("1", "2");
    System.out.println(str);

    str = ScalaObject.getString("1", null);
    System.out.println(str);
} catch (Exception e) {
    //.printStackTrace();
    System.out.println("catch exception");
}
```



