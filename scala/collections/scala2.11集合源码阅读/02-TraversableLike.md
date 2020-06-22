# TraversableLike
TraversableLike的代码还是挺多的，一段一段看看

## self和Breaks
```scala
trait TraversableLike[+A, +Repr] extends Any
                                    with HasNewBuilder[A, Repr]
                                    with FilterMonadic[A, Repr]
                                    with TraversableOnce[A]
                                    with GenTraversableLike[A, Repr]
                                    with Parallelizable[A, ParIterable[A]]
{
  //当前对象的别名，用于在内部类的方法中访问当前对象
  self =>

  // object Traversable中的breaks，用于循环的终止：
  //val breaks: Breaks = new Breaks
  import Traversable.breaks._

  ...
}
```

## isEmpty
返回集合是否为空。
```scala
/** Tests whether this traversable collection is empty.
 *
 *  @return    `true` if the traversable collection contain no elements, `false` otherwise.
 */
def isEmpty: Boolean = {
  var result = true
  breakable {
    // 这个循环就是调用的foreach方法，所以说子类只要实现了foreach方法就具备了集合的大多数方法。
    for (x <- this) {
      result = false
      break
    }
  }
  result
}
```

## hasDefiniteSize
返回集合是否有确定的的大小。默认为true，无限的集合子类可定会重写这个方法。
```scala
/** Tests whether this traversable collection is known to have a finite size.
 *  All strict collections are known to have finite size. For a non-strict
 *  collection such as `Stream`, the predicate returns `'''true'''` if all
 *  elements have been computed. It returns `'''false'''` if the stream is
 *  not yet evaluated to the end.
 *
 *  Note: many collection methods will not work on collections of infinite sizes.
 *
 *  @return  `'''true'''` if this collection is known to have finite size,
 *           `'''false'''` otherwise.
 */
def hasDefiniteSize = true
```

## ++(traversable)
可以看到参数集合的元素B必须是A的父类型和reduce函数一样。
`++[B >: A, That](that: GenTraversableOnce[B])`
```scala
def ++[B >: A, That](that: GenTraversableOnce[B])(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  val b = bf(repr)
  if (that.isInstanceOf[IndexedSeqLike[_, _]]) b.sizeHint(this, that.seq.size)
  //先加自己的
  b ++= thisCollection
   //后加参数的
  b ++= that.seq
  b.result
}
```

















```scala

```