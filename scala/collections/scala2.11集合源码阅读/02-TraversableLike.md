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
在后面追加集合中的元素。

可以看到参数集合的元素B必须是A的父类型和reduce函数一样。
`++[B >: A, That](that: GenTraversableOnce[B])`
```scala
def ++[B >: A, That](that: GenTraversableOnce[B])(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  // 很多方法都有，用于构建目标集合
  val b = bf(repr)
  if (that.isInstanceOf[IndexedSeqLike[_, _]]) b.sizeHint(this, that.seq.size)
  //先加自己的
  b ++= thisCollection
   //后加参数的
  b ++= that.seq
  b.result
}
```

## ++:(traversable)
在前面追加集合中的元素。

这个操作符匹配的是右边对象的方法。也就是`a ++: b` 等价于 `b.++:(b)`。
```scala
/** As with `++`, returns a new collection containing the elements from the left operand followed by the
 *  elements from the right operand.
 *
 *  It differs from `++` in that the right operand determines the type of
 *  the resulting collection rather than the left one.
 *  Mnemonic: the COLon is on the side of the new COLlection type.
 *
 *  @param that   the traversable to append.
 *  @tparam B     the element type of the returned collection.
 *  @tparam That  $thatinfo
 *  @param bf     $bfinfo
 *  @return       a new collection of type `That` which contains all elements
 *                of this raversable collection followed by all elements of `that`.
 */
def ++:[B >: A, That](that: TraversableOnce[B])(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  // 很多方法都有，用于构建目标集合
  val b = bf(repr)
  // that.isInstanceOf[IndexedSeqLike[_, _]]：这里的泛型不能少
  // b.sizeHint(this, that.size)：初始化容量
  if (that.isInstanceOf[IndexedSeqLike[_, _]]) b.sizeHint(this, that.size)
  // 先加参数的
  b ++= that
  // 后加自己的
  b ++= thisCollection
  b.result
}

// 和上面一样，就是参数为Traversable类型
def ++:[B >: A, That](that: Traversable[B])(implicit bf: CanBuildFrom[Repr, B, That]): That =
  (that ++ seq)(breakOut)
```













```scala

```