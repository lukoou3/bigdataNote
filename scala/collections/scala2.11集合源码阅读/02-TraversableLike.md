# TraversableLike
TraversableLike的代码还是挺多的，一段一段看看

[toc]

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

## map(A => B)
map 中有初始化容量，flatMap中没有(估计是因为返回值可能为空)
```scala
def map[B, That](f: A => B)(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  def builder = { // extracted to keep method size under 35 bytes, so that it can be JIT-inlined
    val b = bf(repr)
    // map 中初始化容量，flatMap中没有(估计是因为返回值可能为空)
    b.sizeHint(this)
    b
  }
  val b = builder
  // map中用的+=， flatMap中用的 ++=
  for (x <- this) b += f(x)
  b.result
}
```


## flatMap(A => traversable[B])
map 中有初始化容量，flatMap中没有(估计是因为返回值可能为空)
```scala
def flatMap[B, That](f: A => GenTraversableOnce[B])(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  def builder = bf(repr) // extracted to keep method size under 35 bytes, so that it can be JIT-inlined
  val b = builder
  // map中用的+=， flatMap中用的 ++=
  for (x <- this) b ++= f(x).seq
  b.result
}
```

## filter(A => Boolean)
```scala
// filter和filterNot都是调用的这个
private def filterImpl(p: A => Boolean, isFlipped: Boolean): Repr = {
  val b = newBuilder
  for (x <- this)
    if (p(x) != isFlipped) b += x

  b.result
}

/** Selects all elements of this raversable collection which satisfy a predicate.
 *
 *  @param p     the predicate used to test elements.
 *  @return      a new raversable collection consisting of all elements of this raversable collection that satisfy the given
 *               predicate `p`. The order of the elements is preserved.
 */
def filter(p: A => Boolean): Repr = filterImpl(p, isFlipped = false)

def filterNot(p: A => Boolean): Repr = filterImpl(p, isFlipped = true)
```

## filterNot(A => Boolean)
```scala
def filterNot(p: A => Boolean): Repr = filterImpl(p, isFlipped = true)
```

## collect(partialFunction[A, B])
相当于先filter再map，一步到位。
```scala
def collect[B, That](pf: PartialFunction[A, B])(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  val b = bf(repr)
  // foreach的参数是pf.runWith(b += _)返回的函数。pf.runWith 是偏函数的方法，返回的是A => Boolean的函数。
  foreach(pf.runWith(b += _))
  b.result
}

// 偏函数中的方法，`pf.runWith(action)(x)` is equivalent to `if(pf isDefinedAt x) { action(pf(x)); true } else false`  
def runWith[U](action: B => U): A => Boolean = { x =>
  val z = applyOrElse(x, checkFallback[B])
  if (!fallbackOccurred(z)) { action(z); true } else false
}
```
`pf.runWith(action)(x)` is equivalent to `if(pf isDefinedAt x) { action(pf(x)); true } else false`  


## filterMap(A => Option[B]) 被注释的方法
此方法已在源码中被注释，可以理解。这个方法一是和collect类似，二是也可以由flatMap实现，和flatMap用于此参数一样。
```scala
def filterMap[B, That](f: A => Option[B])(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  val b = bf(repr)
  for (x <- this)
    f(x) match {
      case Some(y) => b += y
      case _ =>
    }
  b.result
}
```

## partitionA => Boolean)
根据谓语把此集合分成两个集合。

符合predicat就添加到l, 否则r，这里`(if (p(x)) l else r) += x`充分利用了scala所有表达式都有返回值的特性
```scala
// Partitions this traversable collection in two traversable collections according to a predicate.
def partition(p: A => Boolean): (Repr, Repr) = {
  val l, r = newBuilder
  // 符合predicat就添加到l, 否则r，这里`(if (p(x)) l else r) += x`充分利用了scala所有表达式都有返回值的特性
  for (x <- this) (if (p(x)) l else r) += x
  (l.result, r.result)
}
```

## groupBy(f: A => K)

```scala
def groupBy[K](f: A => K): immutable.Map[K, Repr] = {
  // 先用可变的Map计算，value是Repr的Builder
  val m = mutable.Map.empty[K, Builder[A, Repr]]
  for (elem <- this) {
    val key = f(elem)
    // getOrElseUpdate是可变map的方法，没有则加入并返回。
    val bldr = m.getOrElseUpdate(key, newBuilder)
    bldr += elem
  }
  
  // 再转换成Builder，value是Repr
  val b = immutable.Map.newBuilder[K, Repr]
  for ((k, v) <- m)
    b += ((k, v.result))

  // 最后返回结果
  b.result
}
```
**可变map的getOrElseUpdate感觉还是挺好用的**
```scala
// op是传名参数，效率很高
def getOrElseUpdate(key: A, op: => B): B =
  get(key) match {
    case Some(v) => v
    case None => val d = op; this(key) = d; d
  }
```

## Boolean forall(A => Boolean)
是否全部元素满足。
```scala
// Tests whether a predicate holds for all elements of this traversable collection.
def forall(p: A => Boolean): Boolean = {
  var result = true
  breakable {
    for (x <- this)
      if (!p(x)) { result = false; break }
  }
  result
}
```

## Boolean exists(A => Boolean)
是否有一个元素全部满足。
```scala
// Tests whether a predicate holds for some of the elements of this traversable collection.
def exists(p: A => Boolean): Boolean = {
  var result = false
  breakable {
    for (x <- this)
      if (p(x)) { result = true; break }
  }
  result
}
```

## Option[A] find(p: A => Boolean)
返回第一个匹配的元素Option[A]，找不到返回None。
```scala
/** Finds the first element of the this traversable satisfying a predicate, if any.
 *
 *  @param p    the predicate used to test elements.
 *  @return     an option value containing the first element in the this traversable
 *              that satisfies `p`, or `None` if none exists.
 */
def find(p: A => Boolean): Option[A] = {
  var result: Option[A] = None
  breakable {
    for (x <- this)
      if (p(x)) { result = Some(x); break }
  }
  result
}
```

## scan(z: B)(op: (B, B) => B)
就是调用的scanLeft，唯一的不同就是多了一个限制：`B >: A`。

```scala
def scan[B >: A, That](z: B)(op: (B, B) => B)(implicit cbf: CanBuildFrom[Repr, B, That]): That = scanLeft(z)(op)
```

## scanLeft(z: B)(op: (B, A) => B)
把初始的元素和每个计算后的元素放到新的集合返回，计算结果是一直累计的，集合的size + 1。
```scala
def scanLeft[B, That](z: B)(op: (B, A) => B)(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  val b = bf(repr)
  // 初始化容量
  b.sizeHint(this, 1)
  var acc = z
  // 初始元素也加入了。
  b += acc
  for (x <- this) { acc = op(acc, x); b += acc }
  b.result
}
```

## scanRight(z: B)(op: (A, B) => B)
从右边扫描。
```scala
@migration("The behavior of `scanRight` has changed. The previous behavior can be reproduced with scanRight.reverse.", "2.9.0")
def scanRight[B, That](z: B)(op: (A, B) => B)(implicit bf: CanBuildFrom[Repr, B, That]): That = {
  var scanned = List(z)
  var acc = z
  for (x <- reversed) {
    acc = op(x, acc)
    scanned ::= acc
  }
  
  // 不知道为啥分了两步，感觉像scanLeft一样也可以一步就完成。
  val b = bf(repr)
  for (elem <- scanned) b += elem
  b.result
}
```
reversed是在TraversableOnce中定义的：
```scala
protected[this] def reversed = {
  var elems: List[A] = Nil
  // 为啥人家的代码这个简洁
  self foreach (elems ::= _)
  elems
}
```


## head、headOption
head返回A，没有就抛出NoSuchElementException异常。

headOption返回Option[A]。
```scala
/** Selects the first element of this traversable collection.
 *  $orderDependent
 *  @return  the first element of this traversable collection.
 *  @throws NoSuchElementException if the traversable collection is empty.
 */
def head: A = {
  var result: () => A = () => throw new NoSuchElementException
  breakable {
    for (x <- this) {
      result = () => x
      break
    }
  }
  result()
}

/** Optionally selects the first element.
 *  $orderDependent
 *  @return  the first element of this traversable collection if it is nonempty,
 *           `None` if it is empty.
 */
def headOption: Option[A] = if (isEmpty) None else Some(head)
```

## tail
相当于list[1:]，但是集合为空时会抛出异常。

head 和 tail 相对应，必须要求集合至少有一个元素。
```scala
// Selects all elements except the first.
override def tail: Repr = {
  if (isEmpty) throw new UnsupportedOperationException("empty.tail")
  drop(1)
}
```

## last、lastOption
和head、headOption相反。
```scala
def last: A = {
  var lst = head
  for (x <- this)
    lst = x
  lst
}

def lastOption: Option[A] = if (isEmpty) None else Some(last)
```

## init
相当于list[:-1]，但是集合为空时会抛出异常。

last 和 init 相对应，必须要求集合至少有一个元素。

**看看人家是怎么在循环中判断最后一个元素的**
```scala
// Selects all elements except the last.
def init: Repr = {
  if (isEmpty) throw new UnsupportedOperationException("empty.init")
  var lst = head
  var follow = false
  val b = newBuilder
  b.sizeHint(this, -1)
  for (x <- this) {
    // 第一次不加，之后加入上一个元素，这样就避过了最后一个元素
    if (follow) b += lst
    else follow = true
    lst = x
  }
  b.result
}
```

## take(n)
取前n个元素。

相当于list[:n]。

take(n) 和 drop(n)正好是整个集合。
```scala
def take(n: Int): Repr = slice(0, n)
```

## drop(n)
返回删除了前n个元素后的集合。

相当于list[n:]，但当n为负数时返回list[0:]。

sliceWithKnownDelta就是取切片，第三个参数是设置初始化容量大小用的。
```scala
def drop(n: Int): Repr =
  if (n <= 0) {
    val b = newBuilder
    b.sizeHint(this)
    (b ++= thisCollection).result
  }
  else sliceWithKnownDelta(n, Int.MaxValue, -n)
```


## slice(from, until)
顾名思义。
```scala
def slice(from: Int, until: Int): Repr =
  sliceWithKnownBound(scala.math.max(from, 0), until)
```

## 实现切片的私有函数
内部实现切片的私有函数，都要求from >= 0。
```scala
// 最终都是调用的这个
// Precondition: from >= 0, until > 0, builder already configured for building.
private[this] def sliceInternal(from: Int, until: Int, b: Builder[A, Repr]): Repr = {
  var i = 0
  breakable {
    for (x <- this) {
      if (i >= from) b += x
      i += 1
      if (i >= until) break
    }
  }
  b.result
}
// Precondition: from >= 0
private[scala] def sliceWithKnownDelta(from: Int, until: Int, delta: Int): Repr = {
  val b = newBuilder
  if (until <= from) b.result
  else {
    b.sizeHint(this, delta)
    sliceInternal(from, until, b)
  }
}
// Precondition: from >= 0
private[scala] def sliceWithKnownBound(from: Int, until: Int): Repr = {
  val b = newBuilder
  if (until <= from) b.result
  else {
    b.sizeHintBounded(until - from, this)
    sliceInternal(from, until, b)
  }
}
```

## takeWhile(predicate)
n为第一个不满足predicate的元素索引，就是返回list[:n]。

```scala
def takeWhile(p: A => Boolean): Repr = {
  val b = newBuilder
  breakable {
    for (x <- this) {
      // 不满足就break
      if (!p(x)) break
      b += x
    }
  }
  b.result
}
```

## dropWhile(predicate)
n为第一个不满足predicate的元素索引，就是返回list[n:]。
```scala
def dropWhile(p: A => Boolean): Repr = {
  val b = newBuilder
  var go = false
  for (x <- this) {
    // 只要x不满足条件，go 一直为true
    if (!go && !p(x)) go = true    
    if (go) b += x
  }
  b.result
}
```

## span(predicate)
相当于一次性返回takeWhile(p), dropWhile(p)的二元组。

```scala
def span(p: A => Boolean): (Repr, Repr) = {
  val l, r = newBuilder
  var toLeft = true
  for (x <- this) {
    // 只要一次不满足，以后就都是false
    toLeft = toLeft && p(x)
    (if (toLeft) l else r) += x
  }
  (l.result, r.result)
}
```

## splitAt(n)
相当于一次性返回take(n), drop(n)的二元组。

```scala
def splitAt(n: Int): (Repr, Repr) = {
  val l, r = newBuilder
  l.sizeHintBounded(n, this)
  if (n >= 0) r.sizeHint(this, -n)
  var i = 0
  for (x <- this) {
    // 这种用法真是随处可见
    (if (i < n) l else r) += x
    i += 1
  }
  (l.result, r.result)
}
```

## tails
返回依次tail的迭代器，第一个为本集合，最后一个为空集合。

example  `List(1,2,3).tails = Iterator(List(1,2,3), List(2,3), List(3), Nil)`
```scala
/** Iterates over the tails of this traversable collection. The first value will be this
 *  traversable collection and the final one will be an empty traversable collection, with the intervening
 *  values the results of successive applications of `tail`.
 *
 *  @return   an iterator over all the tails of this traversable collection
 *  @example  `List(1,2,3).tails = Iterator(List(1,2,3), List(2,3), List(3), Nil)`
 */
def tails: Iterator[Repr] = iterateUntilEmpty(_.tail)
```

## inits
返回依次init的迭代器，第一个为本集合，最后一个为空集合。

example  `List(1,2,3).inits = Iterator(List(1,2,3), List(1,2), List(1), Nil)`
```scala
/** Iterates over the inits of this traversable collection. The first value will be this
 *  traversable collection and the final one will be an empty traversable collection, with the intervening
 *  values the results of successive applications of `init`.
 *
 *  @return  an iterator over all the inits of this traversable collection
 *  @example  `List(1,2,3).inits = Iterator(List(1,2,3), List(1,2), List(1), Nil)`
 */
def inits: Iterator[Repr] = iterateUntilEmpty(_.init)
```

## copyToArray(xs, start, len)
顾名思义。

start：copy的起始索引，len：copy的元素长度(超过数组的会被忽略)。

```scala
/** Copies elements of this traversable collection to an array.
 *  Fills the given array `xs` with at most `len` elements of
 *  this traversable collection, starting at position `start`.
 *  Copying will stop once either the end of the current traversable collection is reached,
 *  or the end of the array is reached, or `len` elements have been copied.
 *
 *  @param  xs     the array to fill.
 *  @param  start  the starting index.
 *  @param  len    the maximal number of elements to copy.
 *  @tparam B      the type of the elements of the array.
 */
def copyToArray[B >: A](xs: Array[B], start: Int, len: Int) {
  var i = start
  // 超过数组的会被忽略
  // min 是RichInt的方法，调用的math.min
  val end = (start + len) min xs.length
  breakable {
    for (x <- this) {
      if (i >= end) break
      xs(i) = x
      i += 1
    }
  }
}
```

## toIterator、toStream
顾名思义。
```scala
def toIterator: Iterator[A] = toStream.iterator
def toStream: Stream[A] = toBuffer.toStream
```

## toString
stringPrefix一般返回的就是类名。
```scala
  override def toString = mkString(stringPrefix + "(", ", ", ")")
```


## view
返回整个集合的视图。
```scala
/** Creates a non-strict view of this traversable collection.
 *
 *  @return a non-strict view of this traversable collection.
 */
def view = new TraversableView[A, Repr] {
  // lazy
  protected lazy val underlying = self.repr
  // self指向traversable collection的this，这是一个技巧
  override def foreach[U](f: A => U) = self foreach f
}
```

## view(from, until)
顾名思义。

```scala
/** Creates a non-strict view of a slice of this traversable collection.
 *
 *  Note: the difference between `view` and `slice` is that `view` produces
 *        a view of the current traversable collection, whereas `slice` produces a new traversable collection.
 *
 *  Note: `view(from, to)` is equivalent to `view.slice(from, to)`
 *  $orderDependent
 *
 *  @param from   the index of the first element of the view
 *  @param until  the index of the element following the view
 *  @return a non-strict view of a slice of this traversable collection, starting at index `from`
 *  and extending up to (but not including) index `until`.
 */
def view(from: Int, until: Int): TraversableView[A, Repr] = view.slice(from, until)
```

## withFilter(p)
filter和withFilter区别：filter直接返回新的集合，withFilter返回支持`map`, `flatMap`, `foreach`,  `withFilter`操作的WithFilter对象。

WithFilter对象相当于java8 的stream和saprk中的rdd，调用`map`, `flatMap`, `foreach`时才执行计算，再次调用withFilter返回的还是WithFilter对象。

for推导式中的if实际上就是调用的WithFilter。

先WithFilter再map，明显比先filter再map效率高
```scala
/** Creates a non-strict filter of this traversable collection.
 *
 *  Note: the difference between `c filter p` and `c withFilter p` is that
 *        the former creates a new collection, whereas the latter only
 *        restricts the domain of subsequent `map`, `flatMap`, `foreach`,
 *        and `withFilter` operations.
 *  $orderDependent
 *
 *  @param p   the predicate used to test elements.
 *  @return    an object of class `WithFilter`, which supports
 *             `map`, `flatMap`, `foreach`, and `withFilter` operations.
 *             All these operations apply to those elements of this traversable collection
 *             which satisfy the predicate `p`.
 */
def withFilter(p: A => Boolean): FilterMonadic[A, Repr] = new WithFilter(p)
```


## WithFilter内部类
类中定义的 WithFilter内部类：

很好理解。
```scala
// A class supporting filtered operations. Instances of this class are returned by method `withFilter`.
class WithFilter(p: A => Boolean) extends FilterMonadic[A, Repr] {

  def map[B, That](f: A => B)(implicit bf: CanBuildFrom[Repr, B, That]): That = {
    val b = bf(repr)
    for (x <- self)
      if (p(x)) b += f(x)
    b.result
  }

  def flatMap[B, That](f: A => GenTraversableOnce[B])(implicit bf: CanBuildFrom[Repr, B, That]): That = {
    val b = bf(repr)
    for (x <- self)
      if (p(x)) b ++= f(x).seq
    b.result
  }

  def foreach[U](f: A => U): Unit =
    for (x <- self)
      if (p(x)) f(x)

  def withFilter(q: A => Boolean): WithFilter =
    new WithFilter(x => p(x) && q(x))
}
```





```scala

```