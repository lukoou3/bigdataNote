
Reduce文件会从Mapper任务中拉取很多小文件，小文件内部有序，但是整体是没序的，Reduce会合并小文件，然后套个归并算法，变成一个整体有序的文件。

reduce端完成三种事情：
①：shuffle，就是拉取数据
②：sort就是排序，对多个有序文件归并排序
③：reduce就是按组计算，可以自定义分组

## ReduceTask
### run
```java
public void run(JobConf job, final TaskUmbilicalProtocol umbilical)
    throws IOException, InterruptedException, ClassNotFoundException {
    job.setBoolean(JobContext.SKIP_RECORDS, isSkipping());

    if (isMapOrReduce()) {
      //reduce端完成三种事情：
      //①：shuffle，就是拉取数据
      //②：sort就是排序，对多个有序文件归并排序
      //③：reduce就是按组计算，可以自定义分组
      copyPhase = getProgress().addPhase("copy");
      sortPhase  = getProgress().addPhase("sort");
      reducePhase = getProgress().addPhase("reduce");
    }
    // start thread that will handle communication with parent
    TaskReporter reporter = startReporter(umbilical);
    
    boolean useNewApi = job.getUseNewReducer();
    initialize(job, getJobID(), reporter, useNewApi);

    // check if it is a cleanupJobTask
    if (jobCleanup) {
      runJobCleanupTask(umbilical, reporter);
      return;
    }
    if (jobSetup) {
      runJobSetupTask(umbilical, reporter);
      return;
    }
    if (taskCleanup) {
      runTaskCleanupTask(umbilical, reporter);
      return;
    }
    
    // Initialize the codec
    codec = initCodec();
    RawKeyValueIterator rIter = null;
    ShuffleConsumerPlugin shuffleConsumerPlugin = null;
    
    //mapred.combiner.class，这里也有一个combiner，对map端的输出进行combine
    Class combinerClass = conf.getCombinerClass();
    CombineOutputCollector combineCollector = 
      (null != combinerClass) ? 
     new CombineOutputCollector(reduceCombineOutputCounter, reporter, conf) : null;

    Class<? extends ShuffleConsumerPlugin> clazz =
          job.getClass(MRConfig.SHUFFLE_CONSUMER_PLUGIN, Shuffle.class, ShuffleConsumerPlugin.class);
        
    //下面是shuffle的过程                
    shuffleConsumerPlugin = ReflectionUtils.newInstance(clazz, job);
    LOG.info("Using ShuffleConsumerPlugin: " + shuffleConsumerPlugin);

    ShuffleConsumerPlugin.Context shuffleContext = 
      new ShuffleConsumerPlugin.Context(getTaskID(), job, FileSystem.getLocal(job), umbilical, 
                  super.lDirAlloc, reporter, codec, 
                  combinerClass, combineCollector, 
                  spilledRecordsCounter, reduceCombineInputCounter,
                  shuffledMapsCounter,
                  reduceShuffleBytes, failedShuffleCounter,
                  mergedMapOutputsCounter,
                  taskStatus, copyPhase, sortPhase, this,
                  mapOutputFile, localMapFiles);
    shuffleConsumerPlugin.init(shuffleContext);

    //返回数据的迭代器
    rIter = shuffleConsumerPlugin.run();//按顺序迭代

    // free up the data structures
    mapOutputFilesOnDisk.clear();
    
    //排序完成
    sortPhase.complete();                         // sort is complete
    //下面开始reduce分组计算
    setPhase(TaskStatus.Phase.REDUCE); 
    statusUpdate(umbilical);
    Class keyClass = job.getMapOutputKeyClass();
    Class valueClass = job.getMapOutputValueClass();
    //组比较器，判断key是否是一组，默认是使用map端的key比较器，可以自己设置GroupingComparator
    RawComparator comparator = job.getOutputValueGroupingComparator();//分组比较 对应解析源码1

    if (useNewApi) {
      runNewReducer(job, umbilical, reporter, rIter, comparator, //对应解析源码2
                    keyClass, valueClass);
    } else {
      runOldReducer(job, umbilical, reporter, rIter, comparator, 
                    keyClass, valueClass);
    }

    shuffleConsumerPlugin.close();
    done(umbilical, reporter);
  }

 源码1：分组比较器的源码

public RawComparator getOutputValueGroupingComparator() {
    //mapreduce.job.output.group.comparator.class
    Class<? extends RawComparator> theClass = getClass(
      JobContext.GROUP_COMPARATOR_CLASS, null, RawComparator.class);//用户没有设置分组比较器的时候，用map端的key比较器
    if (theClass == null) {
      return getOutputKeyComparator();//对应解析源码1.1
    }
    
    return ReflectionUtils.newInstance(theClass, this);
  }
```

### GroupingComparator组比较器
**源码1.1排序比较器，当用户不设置的时候取排序比较器实现，此时如果用户配置排序比较器，用排序比较器，没有的话用默认的Key的比较器**
```java
public RawComparator getOutputKeyComparator() {
    Class<? extends RawComparator> theClass = getClass(
      JobContext.KEY_COMPARATOR, null, RawComparator.class);
    if (theClass != null)
      return ReflectionUtils.newInstance(theClass, this);
    return WritableComparator.get(getMapOutputKeyClass().asSubclass(WritableComparable.class), this);
  }
```

**总结：在Map端是真正改变（调整）Key的顺序的，在Reduce端是不会真正改变（调整）拉过来的其顺序的,Reduce不会重新排序，Reduce端强依赖Map端的输出。reduce端的GroupingComparator称之为二次排序，在map端排好序的基础上做key的分组边界。**

### WritableComparator
我们自定义组比较器一般继承WritableComparator即可，WritableComparator实现了RawComparator

```java
public interface RawComparator<T> extends Comparator<T> {

  /**
   * Compare two objects in binary.
   * b1[s1:l1] is the first object, and b2[s2:l2] is the second object.
   * 
   * @param b1 The first byte array.
   * @param s1 The position index in b1. The object under comparison's starting index.
   * @param l1 The length of the object in b1.
   * @param b2 The second byte array.
   * @param s2 The position index in b2. The object under comparison's starting index.
   * @param l2 The length of the object under comparison in b2.
   * @return An integer result of the comparison.
   */
  public int compare(byte[] b1, int s1, int l1, byte[] b2, int s2, int l2);

}
```

```java
public class WritableComparator implements RawComparator, Configurable {
    
    private final Class<? extends WritableComparable> keyClass;
    private final WritableComparable key1;
    private final WritableComparable key2;
    private final DataInputBuffer buffer;
   
    @Override
    public int compare(byte[] b1, int s1, int l1, byte[] b2, int s2, int l2) {
      try {
        buffer.reset(b1, s1, l1);                   // parse key1
        key1.readFields(buffer);
        
        buffer.reset(b2, s2, l2);                   // parse key2
        key2.readFields(buffer);
        
        buffer.reset(null, 0, 0);                   // clean up reference
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      
      return compare(key1, key2);                   // compare them
    }
    
    //我们只需重写这个方法即可
    public int compare(WritableComparable a, WritableComparable b) {
      return a.compareTo(b);
    }
  
    @Override
    public int compare(Object a, Object b) {
      return compare((WritableComparable)a, (WritableComparable)b);
    }

}
```


### runNewReduce
```java
void runNewReducer(JobConf job,
                     final TaskUmbilicalProtocol umbilical,
                     final TaskReporter reporter,
                     RawKeyValueIterator rIter,
                     RawComparator<INKEY> comparator,
                     Class<INKEY> keyClass,
                     Class<INVALUE> valueClass
                     ) throws IOException,InterruptedException, 
                              ClassNotFoundException {
    // wrap value iterator to report progress.
    final RawKeyValueIterator rawIter = rIter;//真正的迭代器
    rIter = new RawKeyValueIterator() {
      public void close() throws IOException {
        rawIter.close();
      }
      public DataInputBuffer getKey() throws IOException {
        return rawIter.getKey();
      }
      public Progress getProgress() {
        return rawIter.getProgress();
      }
      public DataInputBuffer getValue() throws IOException {
        return rawIter.getValue();
      }
      public boolean next() throws IOException {
        boolean ret = rawIter.next();
        reporter.setProgress(rawIter.getProgress().getProgress());
        return ret;
      }
    };
    // make a task context so we can get the classes
    org.apache.hadoop.mapreduce.TaskAttemptContext taskContext =
      new org.apache.hadoop.mapreduce.task.TaskAttemptContextImpl(job,
          getTaskID(), reporter);
    // make a reducer
    org.apache.hadoop.mapreduce.Reducer<INKEY,INVALUE,OUTKEY,OUTVALUE> reducer =
      (org.apache.hadoop.mapreduce.Reducer<INKEY,INVALUE,OUTKEY,OUTVALUE>)
        ReflectionUtils.newInstance(taskContext.getReducerClass(), job);
    org.apache.hadoop.mapreduce.RecordWriter<OUTKEY,OUTVALUE> trackedRW = 
      new NewTrackingRecordWriter<OUTKEY, OUTVALUE>(this, taskContext);
    job.setBoolean("mapred.skip.on", isSkipping());
    job.setBoolean(JobContext.SKIP_RECORDS, isSkipping());
    org.apache.hadoop.mapreduce.Reducer.Context 
         reducerContext = createReduceContext(reducer, job, getTaskID(),
                                               rIter, reduceInputKeyCounter, //构建上下文的时候把迭代器传进来
                                               reduceInputValueCounter, 
                                               trackedRW,
                                               committer,
                                               reporter, comparator, keyClass,//比较器  解析源码2.1
                                               valueClass);
    try {
      reducer.run(reducerContext);//构建完上下文之后运行Redude的Run方法 
    } finally {
      trackedRW.close(reducerContext);
    }
  }
```

## Reducer
```java
@Checkpointable
@InterfaceAudience.Public
@InterfaceStability.Stable
public class Reducer<KEYIN,VALUEIN,KEYOUT,VALUEOUT> {

  /**
   * The <code>Context</code> passed on to the {@link Reducer} implementations.
   */
  public abstract class Context 
    implements ReduceContext<KEYIN,VALUEIN,KEYOUT,VALUEOUT> {
  }

  /**
   * Called once at the start of the task.
   */
  protected void setup(Context context
                       ) throws IOException, InterruptedException {
    // NOTHING
  }

  /**
   * This method is called once for each key. Most applications will define
   * their reduce class by overriding this method. The default implementation
   * is an identity function.
   */
  @SuppressWarnings("unchecked")
  protected void reduce(KEYIN key, Iterable<VALUEIN> values, Context context
                        ) throws IOException, InterruptedException {
    for(VALUEIN value: values) {
      context.write((KEYOUT) key, (VALUEOUT) value);
    }
  }

  /**
   * Called once at the end of the task.
   */
  protected void cleanup(Context context
                         ) throws IOException, InterruptedException {
    // NOTHING
  }

  /**
   * Advanced application writers can use the 
   * {@link #run(org.apache.hadoop.mapreduce.Reducer.Context)} method to
   * control how the reduce task works.
   */
  public void run(Context context) throws IOException, InterruptedException {
    setup(context);
    try {
      //这里的context就是ReduceContextImpl
      while (context.nextKey()) {
        reduce(context.getCurrentKey(), context.getValues(), context);
        // If a back up store is used, reset it
        Iterator<VALUEIN> iter = context.getValues().iterator();
        if(iter instanceof ReduceContext.ValueIterator) {
          ((ReduceContext.ValueIterator<VALUEIN>)iter).resetBackupStore();        
        }
      }
    } finally {
      cleanup(context);
    }
  }
}
```


## ReduceContextImpl
createReduceContext实现构建上下文的源码，确定了key分组迭代的逻辑。
```java
public ReduceContextImpl(Configuration conf, TaskAttemptID taskid,
                           RawKeyValueIterator input, //把迭代器传给输入对象Input
                           Counter inputKeyCounter,
                           Counter inputValueCounter,
                           RecordWriter<KEYOUT,VALUEOUT> output,
                           OutputCommitter committer,
                           StatusReporter reporter,
                           RawComparator<KEYIN> comparator,
                           Class<KEYIN> keyClass,
                           Class<VALUEIN> valueClass
                          ) throws InterruptedException, IOException{
    super(conf, taskid, output, committer, reporter);
    this.input = input;
    this.inputKeyCounter = inputKeyCounter;
    this.inputValueCounter = inputValueCounter;
    this.comparator = comparator;
    this.serializationFactory = new SerializationFactory(conf);
    this.keyDeserializer = serializationFactory.getDeserializer(keyClass);
    this.keyDeserializer.open(buffer);
    this.valueDeserializer = serializationFactory.getDeserializer(valueClass);
    this.valueDeserializer.open(buffer);
    hasMore = input.next();
    this.keyClass = keyClass;
    this.valueClass = valueClass;
    this.conf = conf;
    this.taskid = taskid;
  }
  /** Start processing next unique key. */
  //实际上Reduce中run方法中的contect.netKey调用的逻辑，只要文件文件还有数据就返回true
  public boolean nextKey() throws IOException,InterruptedException {//实际上Reduce中run方法中的contect.netKey调用的逻辑
    //还有数据并且下一个数据key是相同的，就把value
    while (hasMore && nextKeyIsSame) {//第一次假 放空
      nextKeyValue();
    }
    if (hasMore) {
      if (inputKeyCounter != null) {
        inputKeyCounter.increment(1);
      }
      return nextKeyValue();
    } else {
      return false;
    }
  }

  /**
   * Advance to the next key/value pair.
   */
  @Override
  public boolean nextKeyValue() throws IOException, InterruptedException {
    if (!hasMore) {
      key = null;
      value = null;
      return false;
    }
    //下一个不同就是第一个
    firstValue = !nextKeyIsSame;
    DataInputBuffer nextKey = input.getKey();
    currentRawKey.set(nextKey.getData(), nextKey.getPosition(), 
                      nextKey.getLength() - nextKey.getPosition());
    buffer.reset(currentRawKey.getBytes(), 0, currentRawKey.getLength());
    key = keyDeserializer.deserialize(key);
    DataInputBuffer nextVal = input.getValue();
    buffer.reset(nextVal.getData(), nextVal.getPosition(), nextVal.getLength()
        - nextVal.getPosition());
    value = valueDeserializer.deserialize(value);

    currentKeyLength = nextKey.getLength() - nextKey.getPosition();
    currentValueLength = nextVal.getLength() - nextVal.getPosition();

    if (isMarked) {
      backupStore.write(nextKey, nextVal);
    }

    hasMore = input.next();
    if (hasMore) {
      nextKey = input.getKey();
      //判断当前key和下一个Key是否相等。这里我们可以自定义分组。
      nextKeyIsSame = comparator.compare(currentRawKey.getBytes(), 0, 
                                     currentRawKey.getLength(),
                                     nextKey.getData(),
                                     nextKey.getPosition(),
                                     nextKey.getLength() - nextKey.getPosition()
                                         ) == 0;//判断当前key和下一个Key是否相等。
    } else {
      nextKeyIsSame = false;
    }
    inputValueCounter.increment(1);
    return true;
  }

  public KEYIN getCurrentKey() {
    return key;
  }

  @Override
  public VALUEIN getCurrentValue() {
    return value;
  }
  
  public Iterable<VALUEIN> getValues() throws IOException, InterruptedException {
    return iterable;
  }
```

**context.getValues的最终实现是一个迭代器**

ValueIterator是ReduceContextImpl的内部类，可以访问到ReduceContextImpl的属性。
```java
protected class ValueIterator implements ReduceContext.ValueIterator<VALUEIN> {

    private boolean inReset = false;
    private boolean clearMarkFlag = false;

    @Override
    public boolean hasNext() {
      try {
        if (inReset && backupStore.hasNext()) {
          return true;
        } 
      } catch (Exception e) {
        e.printStackTrace();
        throw new RuntimeException("hasNext failed", e);
      }
      //第一个值或者下一个key相同
      return firstValue || nextKeyIsSame;
    }

    @Override
    public VALUEIN next() {
      if (inReset) {
        try {
          if (backupStore.hasNext()) {
            backupStore.next();
            DataInputBuffer next = backupStore.nextValue();
            buffer.reset(next.getData(), next.getPosition(), next.getLength()
                - next.getPosition());
            value = valueDeserializer.deserialize(value);
            return value;
          } else {
            inReset = false;
            backupStore.exitResetMode();
            if (clearMarkFlag) {
              clearMarkFlag = false;
              isMarked = false;
            }
          }
        } catch (IOException e) {
          e.printStackTrace();
          throw new RuntimeException("next value iterator failed", e);
        }
      } 

      // if this is the first record, we don't need to advance
      if (firstValue) {
        firstValue = false;
        return value;
      }
      // if this isn't the first record and the next key is different, they
      // can't advance it here.
      if (!nextKeyIsSame) {
        throw new NoSuchElementException("iterate past last value");
      }
      // otherwise, go to the next key/value pair
      try {
        nextKeyValue();//这个迭代器自身是没有数据的，在Next中调用的还是 nextKeyValue，在这个NextKeyValue中调用的是Input的输入数据
        return value;
      } catch (IOException ie) {
        throw new RuntimeException("next value iterator failed", ie);
      } catch (InterruptedException ie) {
        // this is bad, but we can't modify the exception list of java.util
        throw new RuntimeException("next value iterator interrupted", ie);        
      }
    }
```

**总结：以上说明一个流程。Reduce会拉回一个数据集，然后封装一个迭代器，真迭代器，ReduceContext会基于这个迭代器给我们封装一个方法，其中包括NextKeyValue这个方法，通过这个方法简介更新Key，Value的值，然后再Reduce方法的Run中有一个While循环，调用的是NextKey方法，底层调用的还是netxkeyValue方法，然后调用Reduce方法，传进去context.getCurrentKey(), context.getValues()两个方法，然后基于Value方法迭代，里面有HasNext和Next方法，Next方法实际上调用的还是真正的迭代器，最终数据时从镇迭代器中迭代出来的，在真正迭代器中有一个重要的标识NextKeyisSame,这个标识会被hasNext方法用到然后判断下一个key是否 相同，直到一组数据。**






```java

```




