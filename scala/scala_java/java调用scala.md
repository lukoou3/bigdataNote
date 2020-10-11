
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



