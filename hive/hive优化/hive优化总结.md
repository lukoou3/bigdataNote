[toc]

# Hive性能优化
摘抄自：`https://cloud.tencent.com/developer/article/1634088`

## 1. 概述

### 1.1 hive的特征：

* 可以通过SQL轻松访问数据的工具，从而实现数据仓库任务，如提取/转换/加载（ETL），报告和数据分析；    
* 它可以使已经存储的数据结构化；    
* 可以直接访问存储在Apache HDFS或其他数据存储系统（如Apache[HBase](https://cloud.tencent.com/product/hbase?from=10680 "HBase")）中的文件；    
* Hive除了支持MapReduce计算引擎，还支持Spark和Tez这两种分布式计算引擎；    
* 它提供类似sql的查询语句HiveQL对数据进行分析处理；    
* 数据的存储格式有多种，比如数据源是二进制格式，普通文本格式等等；

### 1.2 hive的优势：

hive强大之处不要求数据转换成特定的格式，而是利用hadoop本身InputFormat API来从不同的数据源读取数据，同样地使用OutputFormat API将数据写成不同的格式。所以对于不同的数据源，或者写出不同的格式就需要不同的对应的InputFormat和OutputFormat类的实现。以stored as textFile为例，其在底层java API中表现是输入InputFormat格式：TextInputFormat以及输出OutputFormat格式：HiveIgnoreKeyTextOutputFormat。这里InputFormat中定义了如何对数据源文本进行读取划分，以及如何将切片分割成记录存入表中。而OutputFormat定义了如何将这些切片写回到文件里或者直接在控制台输出。

Hive拥有统一的元数据管理，所以和Spark、Impala等SQL引擎是通用的。通用是指，在拥有了统一的metastore之后，在Hive中创建一张表，在Spark/Impala中是能用的；反之在Spark中创建一张表，在Hive中也是能用的，只需要共用元数据，就可以切换SQL引擎，涉及到了Spark sql和Hive On Spark。

不仅如此Hive使用SQL语法，提供快速开发的能力，还可以通过用户定义的函数（UDF），用户定义的聚合（UDAF）和用户定义的表函数（UDTF）进行扩展，避免了去写mapreducce，减少开发人员的学习成本。Hive中不仅可以使用逗号和制表符分隔值（CSV/TSV）文本文件，还可以使用Sequence File、RC、ORC、Parquet（知道这几种存储格式的区别）。当然Hive还可以通过用户来自定义自己的存储格式，基本上前面说到几种格式完全够了。Hive旨在最大限度地提高可伸缩性（通过向Hadoop集群动态田间更多机器扩展），性能，可扩展性，容错性以及与其输入格式的松散耦合。

数据离线处理，比如日志分析，海量数据结构化分析。

## 2. Hive函数

Hive的SQL还可以通过用户定义的函数（UDF），用户定义的聚合（UDAF）和用户定义的表函数（UDTF）进行扩展。

当Hive提供的内置函数无法满足你的业务处理需要时，此时就可以考虑使用用户自定义函数（UDF）。

**UDF、UDAF、UDTF**的区别：

* UDF（User-Defined-Function）一进一出    
* UDAF（User-Defined Aggregation Funcation）聚集函数，多进一出    
* UDTF（User-Defined Table-Generating Functions）一进多出，如lateral view explore()

## 3. Hive优化

### 3.1 慎用api

我们知道大数据场景下不害怕数据量大，害怕的是数据倾斜，怎样避免数据倾斜，找到可能产生数据倾斜的函数尤为关键，数据量较大的情况下，慎用count(distinct)，count(distinct)容易产生倾斜问题。

### 3.2 自定义UDAF函数优化

sum，count，max，min等UDAF，不怕数据倾斜问题，hadoop在map端汇总合并优化，是数据倾斜不成问题。

### 3.3 设置合理的map reduce的task数量

#### 3.3.1 map阶段优化

```sql
mapred.min.split.size: 指的是数据的最小分割单元大小；min的默认值是1B
mapred.max.split.size: 指的是数据的最大分割单元大小；max的默认值是256MB
通过调整max可以起到调整map数的作用，减小max可以增加map数，增大max可以减少map数。
需要提醒的是，直接调整mapred.map.tasks这个参数是没有效果的。
```

举例：

a) 假设input目录下有1个文件a，大小为780M，那么hadoop会将该文件a分隔成7个块（6个128M的块和1个12M的块），从而产生7个map书；

b) 假设input目录下有3个文件a,b,c，大小分别为10M，20M，130M，那么hadoop会分隔成4个块（10M，20M，128M，2M），从而产生4个map数；

注意：如果文件大于块大小（128M），那么会拆分，如果小于块大小，则把该文件当成一个块。

其实这就涉及到小文件的问题：如果一个任务有很多小文件（远远小于块大小128M），则每个小文件也会当做一个块，用一个map任务来完成。

而一个map任务启动和初始化的时间远远大于逻辑处理的时间，就会造成很大的资源浪费。而且，同时可执行的map数是受限的。那么，是不是保证每个map处理接近128M的文件块，就高枕无忧了？答案也是不一定。比如有一个127M的文件，正常会用一个map去完成，但这个文件只有一个或者两个小字段，却有几千万的记录，如果map处理的逻辑比较复杂，用一个map任务去做，肯定也比较耗时。

我们该如何去解决呢？？？

我们需要采取两种方式来解决：即减少map数和增加map数

* 减少map数量

```sql
假设一个SQL任务：
Select count(1) from popt_tbaccountcopy_meswhere pt = '2012-07-04';
该任务的inputdir :  /group/p_sdo_data/p_sdo_data_etl/pt/popt_tbaccountcopy_mes/pt=2012-07-04
共有194个文件，其中很多事远远小于128M的小文件，总大小9G，正常执行会用194个map任务。
Map总共消耗的计算资源：SLOTS_MILLIS_MAPS= 623,020

通过以下方法来在map执行前合并小文件，减少map数：
set mapred.max.split.size=100000000;
set mapred.min.split.size.per.node=100000000;
set mapred.min.split.size.per.rack=100000000;
set hive.input.format=org.apache.hadoop.hive.ql.io.CombineHiveInputFormat;
再执行上面的语句，用了74个map任务，map消耗的计算资源：SLOTS_MILLIS_MAPS= 333,500
对于这个简单SQL任务，执行时间上可能差不多，但节省了一半的计算资源。
大概解释一下，100000000表示100M, 
set hive.input.format=org.apache.hadoop.hive.ql.io.CombineHiveInputFormat;这个参数表示执行前进行小文件合并，
前面三个参数确定合并文件块的大小，大于文件块大小128m的，按照128m来分隔，
小于128m,大于100m的，按照100m来分隔，把那些小于100m的（包括小文件和分隔大文件剩下的），
进行合并,最终生成了74个块。
```


* 增大map数量

```sql
如何适当的增加map数？
当input的文件都很大，任务逻辑复杂，map执行非常慢的时候，可以考虑增加Map数，
来使得每个map处理的数据量减少，从而提高任务的执行效率。

 假设有这样一个任务：
    Select data_desc,
               count(1),
               count(distinct id),
               sum(case when ...),
               sum(case when ...),
               sum(...)
    from a group by data_desc

如果表a只有一个文件，大小为120M，但包含几千万的记录，如果用1个map去完成这个任务，肯定是比较耗时的，
这种情况下，我们要考虑将这一个文件合理的拆分成多个，
这样就可以用多个map任务去完成。
    set mapred.reduce.tasks=10;
      create table a_1 as 
      select * from a 
      distribute by rand(123);

这样会将a表的记录，随机的分散到包含10个文件的a_1表中，再用a_1代替上面sql中的a表，则会用10个map任务去完成。
每个map任务处理大于12M（几百万记录）的数据，效率肯定会好很多。
```


注意：看上去，貌似这两种有些矛盾，一个是要合并小文件，一个是要把大文件拆成小文件，这点正是重点需要关注的地方，使单个map任务处理合适的数据量；

**3.3.2 reduce阶段优化**

Reduce的个数对整个作业的运行性能有很大影响。如果Reduce设置的过大，那么将会产生很多小文件，对NameNode会产生一定的影响，而且整个作业的运行时间未必会减少；如果Reduce设置的过小，那么单个Reduce处理的数据将会加大，很可能会引起OOM异常。

如果设置了mapred.reduce.tasks/mapreduce.job.reduces参数，那么Hive会直接使用它的值作为Reduce的个数；如果mapred.reduce.tasks/mapreduce.job.reduces的值没有设置（也就是-1），那么Hive会根据输入文件的大小估算出Reduce的个数。根据输入文件估算Reduce的个数可能未必很准确，因为Reduce的输入是Map的输出，而Map的输出可能会比输入要小，所以最准确的数根据Map的输出估算Reduce的个数。

1. Hive自己如何确定reduce数：

reduce个数的设定极大影响任务执行效率，不指定reduce个数的情况下，Hive会猜测确定一个reduce个数，基于以下两个设定：

hive.exec.reducers.bytes.per.reducer（每个reduce任务处理的数据量，默认为1000^3=1G）

hive.exec.reducers.max（每个任务最大的reduce数，默认为999）

计算reducer数的公式很简单N=min（参数2，总输入数据量/参数1）

即，如果reduce的输入（map的输出）总大小不超过1G，那么只会有一个reduce任务；

```sql
如：select pt,count(1) from popt_tbaccountcopy_mes where pt = '2012-07-04' group by pt; 
            /group/p_sdo_data/p_sdo_data_etl/pt/popt_tbaccountcopy_mes/pt=2012-07-04 总大小为9G多，
  因此这句有10个reduce
```

2. 调整reduce个数方法一：

调整hive.exec.reducers.bytes.per.reducer参数的值；

set hive.exec.reducers.bytes.per.reducer=500000000; （500M）

select pt, count(1) from popt_tbaccountcopy_mes where pt = '2012-07-04' group by pt;

这次有20个reduce

3. 调整reduce个数方法二：

set mapred.reduce.tasks=15;

select pt,count(1) from popt_tbaccountcopy_mes where pt = '2012-07-04' group by pt;

这次有15个reduce

4. reduce个数并不是越多越好；

同map一样，启动和初始化reduce也会消耗时间和资源；

另外，有多少个reduce，就会有个多少个输出文件，如果生成了很多个小文件，那么如果这些小文件作为下一个任务的输入，则也会出现小文件过多的问题；

5. 什么情况下只有一个reduce；

很多时候你会发现任务中不管数据量多大，不管你有没有调整reduce个数的参数，任务中一直都只有一个reduce任务；其实只有一个reduce任务的情况，除了数据量小于hive.exec.reducers.bytes.per.reducer参数值的情况外，还有以下原因：

* 没有group by的汇总，比如把select pt,count(1) from popt_tbaccountcopy_mes where pt = ‘2012-07-04’ group by pt; 写成select count(1) from popt_tbaccountcopy_mes where pt = ‘2012-07-04’; 这点非常常见，希望大家尽量改写。    
* 用了Order by    
* 有笛卡尔积。

注意：在设置reduce个数的时候也需要考虑这两个原则：使大数据量利用合适的reduce数；是单个reduce任务处理合适的数据量；

### 3.4 小文件合并优化

我们知道文件数目小，容易在[文件存储](https://cloud.tencent.com/product/cfs?from=10680 "文件存储")端造成瓶颈，给HDFS带来压力，影响处理效率。对此，可以通过合并Map和Reduce的结果文件来消除这样的影响。

用于设置合并的参数有：

* 是否合并Map输出文件：hive.merge.mapfiles=true（默认值为true）    
* 是否合并Reduce端输出文件：hive.merge.mapredfiles=false（默认值为false）    
* 合并文件的大小：hive.merge.size.per.task=256*1000*1000（默认值为256000000）

#### 3.4.1 Hive优化之小文件问题及其解决方案：

**小文件是如何产生的：**

* 动态分区插入数据，产生大量的小文件，从而导致map数量剧增；    
* reduce数量越多，小文件也越多（reduce的个数和输出文件是对应的）；    
* 数据源本身就包含大量的小文件。

**小文件问题的影响：**

* 从Hive的角度看，小文件会开很多map，一个map开一个JVM去执行，所以这些任务的初始化，启动，执行会浪费大量的资源，严重影响性能。    
* 在HDFS中，每个小文件对象约占150byte，如果小文件过多会占用大量内存。这样NameNode内存容量严重制约了集群的扩展。

**小文件问题的解决方案：**

从小文件产生的途径就可以从源头上控制小文件数量，方法如下：

* 使用Sequencefile作为表存储格式，不要用textfile，在一定程度上可以减少小文件；    
* 减少reduce的数量（可以使用参数进行控制）；    
* 少用动态分区，用时记得按distribute by分区；

对于已有的小文件，我们可以通过以下几种方案解决：

* 使用hadoop archive命令把小文件进行归档；    
* 重建表，建表时减少reduce数量；    
* 通过参数进行调节，设置map/reduce端的相关参数，如下：


```sql
//每个Map最大输入大小(这个值决定了合并后文件的数量)  
set mapred.max.split.size=256000000;    
//一个节点上split的至少的大小(这个值决定了多个DataNode上的文件是否需要合并)  
set mapred.min.split.size.per.node=100000000;  
//一个交换机下split的至少的大小(这个值决定了多个交换机上的文件是否需要合并)    
set mapred.min.split.size.per.rack=100000000;  
//执行Map前进行小文件合并  
set hive.input.format=org.apache.hadoop.hive.ql.io.CombineHiveInputFormat;   

设置map输出和reduce输出进行合并的相关参数：
[java] view plain copy
//设置map端输出进行合并，默认为true  
set hive.merge.mapfiles = true  
//设置reduce端输出进行合并，默认为false  
set hive.merge.mapredfiles = true  
//设置合并文件的大小  
set hive.merge.size.per.task = 256*1000*1000  
//当输出文件的平均大小小于该值时，启动一个独立的MapReduce任务进行文件merge。  
set hive.merge.smallfiles.avgsize=16000000 
```


### 3.5 SQL优化

#### 3.5.1 列裁剪

Hive在读数据的时候，可以只读取查询中所需要用到的列，而忽略其他列。例如，若有以下查询：

```sql
SELECT a,b FROM q WHERE e<10;
```

在实施此项查询中，Q表有5列（a，b，c，d，e），Hive只读取查询逻辑中真实需要的3列a、b、e， 而忽略列c，d；这样做节省了读取开销，中间表存储开销和数据整合开销。

裁剪对应的参数项为：hive.optimize.cp=true（默认值为真）

#### 3.5.2 分区裁剪

可以在查询的过程中减少不必要的分区。例如，若有以下查询：

```sql
SELECT * FROM (SELECT a1, COUNT(1) FROM T GROUP BY a1) subq WHERE subq.prtn=100; # （多余分区）
SELECT * FROM T1 JOIN (SELECT * FROM T2) subq ON (T1.a1=subq.a2) WHERE subq.prtn=100;
```

查询语句若将"subq.prtn=100"条件放入子查询中更为高效，可以减少读入的分区数目。Hive自动执行这种裁剪优化。

分区参数为：hive.optimize.pruner=true（默认值为真）

#### 3.5.3 熟练使用SQL提高查询

熟练地使用SQL，能写出高效率的查询语句。

场景：有一张user表，为卖家每天收到表，user_id，ds（日期）为key，属性有主营类目，指标有交易金额，交易笔数。每天要取前10天的总收入，总笔数，和最近一天的主营类目。

**解决方法 1**如下所示：常用方法


```sql
INSERT OVERWRITE TABLE t1
SELECT user_id, substr(MAX(CONCAT(ds,cat),9) AS main_cat) FROM users
WHERE ds=20120329 // 20120329 为日期列的值，实际代码中可以用函数表示当天日期GROUP BY user_id;

INSERT OVERWRITE TABLE t2
SELECT user_id,sum(qty) AS qty, SUM(amt) AS amt FROM users
WHERE ds BETWEEN 20120301 AND 20120329
GROUP BY user_id;

SELECT t1.user_id, t1.main_cat, t2.qty, t2.amt FROM t1
JOIN t2 ON t1.user_id=t2.user_id
```


下面给出方法1的思路，实现步骤如下：

第一步：利用分析函数，取每个user_id最近一天的主营类目，存入临时表t1；

第二步：汇总10天的总交易金额，交易笔数，存入临时表t2；

第三步：关联t1、t2，得到最终的结果。

**解决方法 2**如下所示：优化方法

```sql
SELECT user_id, substr(MAX(CONCAT(ds, cat)), 9) AS main_cat, SUM(qty), SUM(amt) FROM users
WHERE ds BETWEEN 20120301 AND 20120329
GROUP BY user_id
```

在工作中我们总结出：方案2的开销等于方案1的第二步开销，性能提升，由原有的25分钟完成，缩短为10分钟以内完成。节省了两个临时表的读写是一个关键原因，这种方式也适用于Oracle中的数据查找工作。

SQL具有普适性，很多SQL通用的优化方案在Hadoop分布式计算方式中也可以达到效果。

#### 3.5.5 不同数据类型关联产生的倾斜问题

问题：不同数据类型id的关联会产生数据倾斜问题。

一张表的s8的日志，每个商品一条记录，要和商品表关联。但关联却碰到倾斜的问题。s8的日志中有32位字符串商品id，也有数值商品id，日志中类型是string的，但商品中的数值id是bigint的。猜想问题的原因是把s8的商品id转成数值id做hash来分配Reduce，所以字符串id的s8日志，都到一个Reduce上了，解决的方法验证了这个猜测。

解决方法：把数据类型转换成字符串类型

```sql
SELECT * FROM s8_log a LEFT OUTER
JOIN r_auction_auctions b ON a.auction_id=CAST(b.auction_id AS STRING)
```

调优结果显示：数据表处理由1小时30分钟经代码调整后可以在20分钟内完成。

#### 3.5.6 利用Hive对UNION ALL优化的特性

多表union all会优化成一个job。

问题：比如推广效果表要和商品表关联，效果表中的auction_id列既有32位字符串商品id，也有数字id，和商品表关联得到商品的信息。

解决方法：Hive SQL性能会比较好

```sql
SELECT * FROM effect a
JOIN
(SELECT auction_id AS auction_id FROM auctions
UNION ALL
SELECT auction_string_id AS auction_id FROM auctions) b
ON a.auction_id=b.auction_id
```

比分别过滤数字id，字符串id然后分别和商品表关联性能要好。

这样写的好处：1个MapReduce作业，商品表只读一次，推广效果表只读取一次。把这个SQL换成Map/Reduce代码的话，Map的时候，把a表的记录打上标签a，商品表记录每读取一条，打上标签b，变成两个<key, value>对，<(b，数字id)，value>，<(b，字符串id)，value>。

所以商品表的HDFS读取只会是一次。

#### 3.5.7 解决Hive对UNION ALL优化的短板

Hive对union all的优化的特性：对union all优化只局限于非嵌套查询

* 消灭子查询内的group by

示例1：子查询内有group by

```sql
SELECT * FROM
(SELECT * FROM t1 GROUP BY c1,c2,c3 UNION ALL SELECT * FROM t2 GROUP BY c1,c2,c3) t3
GROUP BY c1,c2,c3
```

从业务逻辑上说，子查询内的GROUP BY怎么看都是多余（功能上的多余，除非有COUNT(DISTINCT)），如果不是因为Hive Bug或者性能上的考量（曾经出现如果不执行子查询GROUP BY，数据得不到正确的结果的Hive Bug）。所以这个Hive按经验转换成如下所示：

```sql
SELECT * FROM (SELECT * FROM t1 UNION ALL SELECT * FROM t2) t3 GROUP BY c1,c2,c3
```

调优结果：经过测试，并未出现union all的Hive Bug，数据是一致的。MapReduce的作业数由3减少到1。

t1相当于一个目录，t2相当于一个目录，对Map/Reduce程序来说，t1、t2可以作为Map/Reduce作业的mutli inputs。这可以通过一个Map/Reduce来解决这个问题。Hadoop的计算框架，不怕数据多，就怕作业数多。

但如果换成是其他计算平台如Oracle，那就不一定了，因为把大输入拆成两个输入，分别排序汇总成merge（假如两个子排序是并行的话），是有可能性能更优的（比如希尔排序比冒泡排序的性能更优）。

* 消灭子查询内的COUNT(DISTINCT)，MAX，MIN

```sql
SELECT * FROM 
(SELECT * FROM t1
UNION ALL SELECT c1,c2,c3 count(DISTINCT c4) FROM t2 GROUP BY c1,c2,c3) t3
GROUP BY c1,c2,c3
```

由于子查询里头有COUNT(DISTINCT)操作，直接去GROUP BY将达不到业务目标。这时采用临时表消灭COUNT(DISTINCT)作业不但能解决倾斜问题，还能有效减少jobs。

```sql
INSERT t4 SELECT c1,c2,c3,c4 FROM t2 GROUP BY c1,c2,c3;
SELECT c1,c2,c3,SUM(income),SUM(uv) FROM
(SELECT c1,c2,c3,income,0 AS uv FROM t1
UNION ALL
SELECT c1,c2,c3,0 AS income, 1 AS uv FROM t2) t3
GROUP BY c1,c2,c3;
```

job数是2，减少一半，而且两次Map/Reduce比COUNT(DISTINCT)效率更高。

调优结果：千万级别的类目表，member表，与10亿级的商品表关联。原先1963s的任务经过调整，1152s即完成。

* 消灭子查询内的JOIN

```sql
SELECT * FROM
(SELECT * FROM t1 UNION ALL SELECT * FROM t4 UNION ALL SELECT * FROM t2 JOIN t3 ON t2.id=t3.id) x
GROUP BY c1,c2;
```

上面代码运行会有5个jobs。加入先JOIN生存临时表的话t5，然后UNION ALL，会变成2个jobs。

```sql
INSERT OVERWRITE TABLE t5
SELECT * FROM t2 JOIN t3 ON t2.id=t3.id;
SELECT * FROM (t1 UNION ALL t4 UNION ALL t5);
```

调优结果显示：针对千万级别的广告位表，由原先5个Job共15分钟，分解为2个job，一个8-10分钟，一个3分钟。

#### 3.5.8 COUNT(DISTINCT)

计算uv的时候，经常会用到COUNT(DISTINCT)，但在数据比较倾斜的时候COUNT(DISTINCT)会比较慢。这时可以尝试用GROUP BY改写代码计算uv。数据量小的时候无所谓，数据量大的情况下，由于COUNT DISTINCT操作需要用一个Reduce Task来完成，这一个Reduce需要处理的数据量太大，就会导致整个Job很难完成，一般COUNT DISTINCT使用先GROUP BY再COUNT的方式替换：

* 原有代码

```sql
①
INSERT OVERWRITE TABLE s_dw_tanx_adzone_uv PARTITION (ds=20120329) 
SELECT 20120329 AS thedate,adzoneid,COUNT(DISTINCT acookie) AS uv FROM s_ods_log_tanx_pv t WHERE t.ds=20120329 GROUP BY adzoneid;

②
select count(distinct id) from bigtable;
```

关于COUNT(DISTINCT)的数据倾斜问题不能一概而论，要依情况而定，下面是我测试的一组数据：

测试数据：169857条


```sql
①
#统计每日IP
CREATE TABLE ip_2014_12_29 AS SELECT COUNT(DISTINCT ip) AS FROM logdfs WHERE logdate='2014_12_29';
耗时：24.805 seconds
#统计每日IP(改造)
CREATE TABLE ip_2014_12_29 AS SELECT COUNT(1) AS IP FROM (SELECT DISTINCT ip from logdfs WHERE logdate='2014_12_29') tmp;
耗时：46.833 seconds

②
 select count(id) from (select id from bigtable group by id) a;
```


测试结果表明：明显改造后的语句比之前耗时，这时因为改造后的语句有2个SELECT，多了一个job，这样在数据量小的时候，数据不会存在倾斜问题。

#### 3.5.9 JOIN操作

##### 3.5.9.1 小表、大表JOIN

在使用写有Join操作的查询语句时有一条原则：应该将条目少的表/子查询放在Join操作符的左边。原因是在Join操作的Reduce阶段，位于Join操作符左边的表的内容会被加载进内存，将条目少的表放在左边，可以有效减少发生OOM错误的几率；再进一步，可以使用Group让小的维度表（1000条以下的记录条数）先进内存。在map端完成reduce。

实际测试发现：新版的hive已经对小表JOIN大表和大表JOIN小表进行了优化。小表放在左边和右边已经没有明显区别。

案例实操：

（1）关闭mapjoin功能（默认是打开的）

set hive.auto.convert.join=false;

（2）执行小表JOIN大表语句

```sql
insert overwrite table jointable
select b.id, b.time, b.uid, b.keyword, b.url_rank, b.click_num, b.click_url
from smalltable s
left join bigtable  b
on b.id = s.id;
```

Time taken: 35.921 seconds

（3）执行大表JOIN大表语句

```sql
insert overwrite table jointable
select b.id, b.time, b.uid, b.keyword, b.url_rank, b.click_num, b.click_url
from bigtable  b
left join smalltable  s
on s.id = b.id;
```

Time taken: 34.196 seconds；

##### 3.5.9.2 大表JOIN大表

**1）空Key过滤**

问题：日志中常会出现信息丢失，比如每日约为20亿的全网日志，其中的user_id为主键，在日志收集过程中会丢失，出现主键为null的情况，如果取其中的user_id和bmw_users关联，就会碰到数据倾斜的问题。原因是Hive中，主键为null值的项会被当做相同的Key而分配进同一个计算Map。

解决方法1：user_id为空的不参与关联，子查询过滤null

```sql
SELECT * FROM log a
JOIN bmw_users b ON a.user_id IS NOT NULL AND a.user_id=b.user_id
UNION ALL SELECT * FROM log a WHERE a.user_id IS NULL
```

解决方法2 如下所示：函数过滤null

```sql
SELECT * FROM log a LEFT OUTER
JOIN bmw_users b ON
CASE WHEN a.user_id IS NULL THEN CONCAT('dp_hive', RAND()) ELSE a.user_id END = b.user_id;
```

调优结果：原先由于数据倾斜导致运行时长超过1小时，解决方法1运行每日平均时长25分钟，解决方法2运行的每日平均时长在20分钟左右。优化效果很明显。

我们在工作中总结出：解决方法2比解决方法1效果更好，不但IO少了，而且作业数也少了。解决方法1中log读取两次，job数为2。解决方法2中job数是1。这个优化适合无效id（比如-99，‘’，null等）产生的倾斜问题。把空值的key变成一个字符串加上随机数，就能把倾斜的数据分到不同的Reduce上，从而解决数据倾斜问题。因为空值不参与关联，即使分到不同的Reduce上，也不会影响最终的结果。附上Hadoop通用关联的实现方法是：关联通过二次排序实现的，关联的列为partition key，关联的列和表的tag组成排序的group key，根据partition key分配Reduce。同一Reduce内根据group key排序。

##### 3.5.9.3 MAP JOIN操作

如果不指定MapJoin或者不符合MapJoin的条件，那么Hive解析器会将Join操作转换成Common Join，即：在Reduce阶段完成join。容易发生数据倾斜。可以用MapJoin把小表全部加载到内存在map端进行join，避免reducer处理。

* 开启MapJoin参数设置：

1) 设置自动选择MapJoin

set hive.auto.convert.join = true;默认为true

2) 大表小表的阀值设置（默认25M一下认为是小表）：

set hive.mapjoin.smalltable.filesize=25000000;

* MapJoin工作机制

![](assets/markdown-img-paste-20200731095807101.png)

上图是Hive MapJoin的原理图，从图中可以看出MapJoin分为两个阶段：

（1）通过MapReduce Local Task，将小表读入内存，生成内存HashTableFiles上传至Distributed Cache中，这里会对HashTableFiles进行压缩。

（2）MapReduce Job在Map阶段，每个Mapper从Distributed Cache读取HashTableFiles到内存中，顺序扫描大表，在Map阶段直接进行Join，将数据传递给下一个MapReduce任务。也就是在map端进行join避免了shuffle。

Join操作在Map阶段完成，不再需要Reduce，有多少个Map Task，就有多少个结果文件。

实例：

（1）开启MapJoin功能

set hive.auto.convert.join = true; 默认为true

（2）执行小表JOIN大表语句

```sql
insert overwrite table jointable
select b.id, b.time, b.uid, b.keyword, b.url_rank, b.click_num, b.click_url
from smalltable s
join bigtable  b
on s.id = b.id;
```

Time taken: 24.594 seconds

（3）执行大表JOIN小表语句

```sql
insert overwrite table jointable
select b.id, b.time, b.uid, b.keyword, b.url_rank, b.click_num, b.click_url
from bigtable  b
join smalltable  s
on s.id = b.id;
```

Time taken: 24.315 seconds

##### 3.5.9.3 GROUP BY操作

默认情况下，Map阶段同一Key数据分发给一个reduce，当一个key数据过大时就倾斜了。进行GROUP BY操作时需要注意以下几点：

* Map端部分聚合

事实上并不是所有的聚合操作都需要在reduce部分进行，很多聚合操作都可以先在Map端进行部分聚合，然后reduce端得出最终结果。

（1）开启Map端聚合参数设置

set hive.map.aggr=true

（2）在Map端进行聚合操作的条目数目

set hive.grouby.mapaggr.checkinterval=100000

（3）有数据倾斜的时候进行[负载均衡](https://cloud.tencent.com/product/clb?from=10680 "负载均衡")（默认是false）

set hive.groupby.skewindata = true

* 有数据倾斜时进行负载均衡

此处需要设定hive.groupby.skewindata，当选项设定为true时，生成的查询计划有两个MapReduce任务。在第一个MapReduce中，map的输出结果集合会随机分布到reduce中，每个reduce做部分聚合操作，并输出结果。这样处理的结果是，相同的Group By Key有可能分发到不同的reduce中，从而达到负载均衡的目的；第二个MapReduce任务再根据预处理的数据结果按照Group By Key分布到reduce中（这个过程可以保证相同的Group By Key分布到同一个reduce中），最后完成最终的聚合操作。

#### 3.5.10 优化in/exists语句

虽然经过测验，hive1.2.1也支持in/exists操作，但还是推荐使用hive的一个高效替代方案：left semi join

比如说：

select a.id, a.name from a where a.id in (select b.id from b);
　　　　　　select a.id, a.name from a where exists (select id from b where a.id = b.id);

应该转换成：

select a.id, a.name from a left semi join b on a.id = b.id;

#### 3.5.11 排序选择

* **cluster by**: 对同一字段分桶并排序，不能和sort by连用；    
* **distribute by + sort by**: 分桶，保证同一字段值只存在一个结果文件当中，结合sort by 保证每个reduceTask结果有序；    
* **sort by**: 单机排序，单个reduce结果有序    
* **order by**：全局排序，缺陷是只能使用一个reduce

### 3.6 存储格式

可以使用列裁剪，分区裁剪，orc，parquet等这些列式存储格式，因为列式存储的表，每一列的数据在物理上是存储在一起的，Hive查询时会只遍历需要列数据，大大减少处理的数据量。

Hive支持ORCfile，这是一种新的表格存储格式，通过诸如谓词下推，压缩等技术来提高执行速度提升。对于每个HIVE表使用ORCfile应该是一件容易的事情，并且对于获得HIVE查询的快速响应时间非常有益。

作为一个例子，考虑两个大表A和B（作为文本存储，其中一些列未在此处指定，即行式存储的缺点）以及一个简单的查询，如：

SELECT A.customerID，A.name，A.age，A.address join B.role，B.department，B.salary ON A.customerID=B.customerID；

此查询可能需要很长时间才能执行，因为表A和B都以TEXT形式存储，进行全表扫描。

将这些表格转换为ORCFile格式通常会显着减少查询时间；

ORC支持压缩存储（使用ZLIB或如上所示使用SNAPPY），但也支持未压缩的存储。


```sql
CREATE TABLE A_ORC (
　　customerID int，name string，age int, address string
) STORED AS ORC tblproperties ("orc.compress" = "SNAPPY")；

INSERT INTO TABLE A_ORC SELECT * FROM A;

CREATE TABLE B_ORC (
       customerID int, role string, salary float, department string
) STORED AS ORC tblproperties ("orc.compress" = "SNAPPY");

INSERT INTO TABLE B_ORC SELECT * FROM B;

SELECT A_ORC.customerID, A_ORC.name, A_ORC.age, A_ORC.address join B_ORC.role，B_ORC.department, B_ORC.salary
ON A_ORC.customerID=B_ORC.customerID;
```


### 3.7 压缩格式

大数据场景下存储格式压缩格式尤为关键，可以提升计算速度，减少存储空间，降低网络io，磁盘io，所以要选择合适的压缩格式和存储格式，那么首先就了解这些东西。

#### 3.7.1 压缩的原因

Hive最终是转为MapReduce程序来执行的，而MapReduce的性能瓶颈在于网络IO和磁盘IO，要解决性能瓶颈，最主要的是减少数据量，对数据进行压缩是个好的方式。压缩虽然是减少了数据量，但是压缩过程要消耗CPU的，但是在Hadoop中，往往性能瓶颈不在于CPU，CPU压力并不大，所以压缩充分利用了比较空闲的CPU。

#### 3.7.2 常用压缩方法对比

![](assets/markdown-img-paste-20200731095828266.png)

各个压缩方式所对应的Class类：

![](assets/markdown-img-paste-20200731095836425.png)

#### 3.7.3 压缩方式的选择

压缩比率，压缩解压缩速度，是否支持Split

#### 3.7.4 压缩使用

Job输出文件按照block以Gzip的方式进行压缩：

```sql
set mapreduce.output.fileoutputformat.compress=true // 默认值是 false
set mapreduce.output.fileoutputformat.compress.type=BLOCK // 默认值是 Record
set mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.GzipCodec // 默认值是 org.apache.hadoop.io.compress.DefaultCodec
```

Map输出结果也以Gzip进行压缩：

```sql
set mapred.map.output.compress=true
set mapreduce.map.output.compress.codec=org.apache.hadoop.io.compress.GzipCodec // 默认值是 org.apache.hadoop.io.compress.DefaultCodec 
```

对Hive输出结果和中间都进行压缩：

```sql
set hive.exec.compress.output=true // 默认值是 false，不压缩
set hive.exec.compress.intermediate=true // 默认值是 false，为 true 时 MR 设置的压缩才启用
```

### 3.8 引擎的选择

Hive可以使用Apache Tez执行引擎而不是古老的Map-Reduce引擎。没有在环境中没有默认打开，在Hive查询开头将以下内容设置为‘true’来使用Tez：“设置hive.execution.engine = tez; ”，通过上述设置，你执行的每个HIVE查询都将利用Tez。目前Hive On Spark还处于试验阶段，慎用。

### 3.9 使用向量化查询

向量化查询执行通过一次性批量执行1024行而不是每次单行执行，从而提供扫描、聚合、筛选器和连接等操作的性能。在Hive 0.13中引入，此功能显着提高了查询执行时间，并可通过两个参数设置轻松启用：

设置hive.vectorized.execution.enabled = true;
 设置hive.vectorized.execution.reduce.enabled = true;

### 3.10 设置cost based query optimization

Hive自0.14.0开始，加入了一项“Cost based Optimizer”来对HQL执行计划进行优化，这个功能通过“hive.cbo.enable”来开启。在Hive 1.1.0之后，这个feature是默认开启的，它可以自动优化HQL中多个JOIN的顺序，并选择合适的JOIN算法。

Hive在提供最终执行前，优化每个查询的执行逻辑和物理执行计划。这些优化工作是交给底层来完成的。根据查询成本执行进一步的优化，从而产生潜在的不同决策：如何排序连接，执行哪种类型的连接，并行度等等。要使用基于成本的优化（也称为CBO），请在查询开始设置以下参数：

设置hive.cbo.enable = true;
 设置hive.compute.query.using.stats = true;
 设置hive.stats.fetch.column.stats = true;
 设置hive.stats.fetch.partition.stats = true;

### 3.11 模式选择

* 本地模式

对于大多数情况，Hive可以通过本地模式在单台机器上处理所有任务。对于小数据，执行时间可以明显被缩短。通过set hive.exec.mode.local.auto = true（默认为false）设置为本地模式，本地模式涉及到三个参数：

![](assets/markdown-img-paste-20200731095905155.png)

set hive.exec.mode.local.auto=true; 是打开hive自动判断是否启动本地模式的开关，但是只是打开这个参数不能保证启动本地模式，要当map任务数不超过hive.exec.mode.local.auto.input.files.max的个数并且map输入文件大小不超过hive.exec.mode.local.auto.inputbytes.max所指定的大小时，才能启动本地模式。

如下：用户可以通过设置hive.exec.mode.local.auto的值为true，来让Hive在适当的时候自动启动这个优化。

```sql
set hive.exec.mode.local.auto=true;  //开启本地mr
//设置local mr的最大输入数据量，当输入数据量小于这个值时采用local  mr的方式，默认为134217728，即128M
set hive.exec.mode.local.auto.inputbytes.max=50000000;
//设置local mr的最大输入文件个数，当输入文件个数小于这个值时采用local mr的方式，默认为4
set hive.exec.mode.local.auto.input.files.max=10;
```

* 并行模式

Hive会将一个查询转化成一个或多个阶段。这样的阶段可以是MapReduce阶段、抽样阶段、合并阶段、limit阶段。默认情况下，Hive一次只会执行一个阶段，由于job包含多个阶段，而这些阶段并非完全相互依赖，即：这些阶段可以并行执行，可以缩短整个job的执行时间。设置参数，set hive.exec.parallel=true,或者通过配置文件来完成：

hive> set hive.exec.parallel;

* 严格模式

Hive提供一个严格模式，可以防止用户执行那些可能产生意想不到的影响查询，通过设置Hive.mapred.modestrict来完成。

set Hive.mapred.modestrict;

### 3.12 JVM重用

Hadoop通常是使用派生JVM来执行map和reduce任务的。这时JVM的启动过程可能会造成相当大的开销，尤其是执行的job包含成百上千的task任务的情况。JVM重用可以使得JVM示例在同一个job中时候，通过参数mapred.job.reuse.jvm.num.tasks来设置。

### 3.13 推测执行

Hadoop推测执行可以触发执行一些重复的任务，尽管因对重复的数据进行计算而导致消耗更多的计算资源，不过这个功能的目标是通过加快获取单个task的结果以侦测执行慢的TaskTracker加入到没名单的方式来提高整体的任务执行效率。Hadoop的推测执行功能由2个配置控制着，通过mapred-site.xml中配置

mapred.map.tasks.speculative.execution=true
mapred.reduce.tasks.speculative.execution=true


