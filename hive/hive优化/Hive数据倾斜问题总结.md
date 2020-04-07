# Hive数据倾斜问题总结

## Hive数据倾斜
`https://github.com/polaris6/BigDataLearning/blob/ab0c3b8b15963250e51ef82158c2a1159048262f/src/hive/data_skew`

```
Hive数据倾斜

一、数据倾斜原因
    数据倾斜就是key分布不均匀，分发到不同的reduce上，个别reduce任务特别重，导致其他reduce都完成，而这些个别的reduce迟迟
不完成的情况。导致数据倾斜的原因有：
1、key分布不均匀
2、map端数据倾斜，输入文件太多且大小不一
3、reduce端数据倾斜，分区器问题
4、业务数据本身的特征


二、解决方案
1、参数调节：
    当出现小文件过多，需要合并小文件。可以通过set hive.merge.mapfiles=true来解决(在map-only job后合并文件，默认true)。
    设置 hive.map.aggr = true，Map端部分聚合，相当于Combiner。
    设置 hive.groupby.skewindata = true，数据倾斜的时候进行负载均衡，查询计划生成两个MR job，第一个job先进行key随机分配
处理，随机分布到Reduce中，每个Reduce做部分聚合操作，先缩小数据量。第二个job再进行真正的group by key处理，根据预处理的
数据结果按照Group By Key分布到Reduce中（这个过程可以保证相同的Key被分布到同一个Reduce中），完成最终的聚合操作。

2、SQL语句优化：
①、大小表Join：
    使用map join让小表（小于1000行）先进内存，在map端完成reduce。
    注：map join就是在map端做join，map join会把小表全部读入内存中，在map阶段直接拿另外一个表的数据和内存中表数据做匹配。

②、大表Join大表：
    大表连接大表时，如果是null值造成数据倾斜，那么把null值变成一个字符串加上随机数（赋予null值新的key值），把这部分倾斜
的数据分发到不同的reduce上，由于这个字符串关联不上，处理后并不影响最终结果。

③、count distinct大量相同特殊值：
    count distinct时，将值为null的情况单独处理，如果是计算count distinct，可以不用处理，直接过滤，在最后结果中加1。
如果还有其他计算，需要进行group by，可以先将值为空的记录单独处理，再和其他计算结果进行union。

④、采用sum() group by的方式来代替count(distinct)完成计算：
    select count(distinct colA) from table1;
    select count(1) from (select colA from table1 group by colA) alias_1;   group by也可以去重

3、特殊情况特殊处理：
    在业务逻辑优化的效果不好的情况下，可以将倾斜的数据单独拿出来处理，最后union回去。
```


## Hive数据倾斜问题总结
`https://cloud.tencent.com/developer/article/1011039`

### MapReduce数据倾斜
Hive查询最终转换为MapReduce操作，所以要先了解MapReduce数据倾斜问题。

MapReduce程序执行时，reduce节点大部分执行完毕，但是有一个或者几个reduce节点运行很慢，导致整个程序的处理时间很长，这是因为某一个key的条数比其他key多很多（有时是百倍或者千倍之多），这条key所在的reduce节点所处理的数据量比其他节点就大很多，从而导致某几个节点迟迟运行不完，此称之为数据倾斜。 

在map端和reduce端都有可能发生数据倾斜。在map端的数据倾斜会让多样化的数据集的处理效率更低。在reduce端的数据倾斜常常来源于MapReduce的默认分区器。Reduce数据倾斜一般是指map的输出数据中存在数据频率倾斜的状况，也就是部分输出键的数据量远远大于其它的输出键。

常见的数据倾斜有以下几类：

* 数据频率倾斜：某一个区域的数据量要远远大于其他区域。    
* 数据大小倾斜：部分记录的大小远远大于平均值。  

解决MapReduce数据倾斜思路有两类：

* 一是reduce 端的隐患在 map 端就解决    
* 二是对 key 的操作，以减缓reduce 的压力  

#### reduce 端的隐患在 map 端就解决
**方法1：Combine**

使用Combine可以大量地减小数据频率倾斜和数据大小倾斜。在可能的情况下，combine的目的就是聚合并精简数据。在加个combiner函数，加上combiner相当于提前进行reduce,就会把一个mapper中的相同key进行了聚合，减少shuffle过程中数据量，以及reduce端的计算量。这种方法可以有效的缓解数据倾斜问题，但是如果导致数据倾斜的key 大量分布在不同的mapper的时候，这种方法就不是很有效了。

**方法2：map端join** 

join 操作中，使用 map join 在 map 端就先进行 join ，免得到reduce 时卡住。

**方法3：group** 

能先进行 group 操作的时候先进行 group 操作，把 key 先进行一次 reduce,之后再进行 count 或者 distinct count 操作。

#### 对 key 的操作，以减缓reduce 的压力
因为map阶段对数据处理方法不当，或者说Key设计不当，导致大量数据聚集到某个key下。这个问题再《数据结构》的hash算法中有详细解决办法（增大数组容量，选择恰当素数）。所以大家很快想到一个解决办法，重新设计key，使得数据均匀分不到每个key下面（通常需要增加reduce数），这样reduce节点收到的数据也相对均匀。

这里提供一个解决办法，自定义Partitioner，可以将key均匀分布。
```java
package cn.hadron.mr.ncdc;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.mapreduce.lib.partition.HashPartitioner;

public class MyPartitioner extends HashPartitioner<Weather, DoubleWritable> {
    // 执行时间越短越好
    public int getPartition(Weather key, DoubleWritable value, int numReduceTasks) {
        // 根据年份分区
        return key.getYear() % numReduceTasks;
    }
}
```

### 诊断数据倾斜
在发现了倾斜数据的存在之后，就很有必要诊断造成数据倾斜的那些键。有一个简便方法就是在代码里实现追踪每个键的最大值。为了减少追踪量，可以设置数据量阀值，只追踪那些数据量大于阀值的键，并输出到日志中。
```java
private int MAXVAL=100;
public void reduce(Text key, Iterator<Text> values,OutputCollector<Text, Text> output,
                    Reporter reporter) throws IOException {  
     int i = 0;
     while (values.hasNext()) {
         values.next();
         i++;
     }
     if (i> MAXVAL) {
         log.info("Received " + i + " values for key " + key);
     }
 }
```

### Hive数据倾斜
Hive产生数据倾斜的原因

* key分布不均匀    
* 业务数据本身的特性    
* 建表时考虑不周    
* 某些SQL语句本身就有数据倾斜

解决办法如下

#### 调参
```
hive.map.aggr=true
```
Map端部分聚合，相当于Combiner

```
hive.groupby.skewindata=true
```
有数据倾斜的时候进行负载均衡，当选项设定为 true，生成的查询计划会有两个 MR Job。第一个 MR Job 中，Map 的输出结果集合会随机分布到 Reduce 中，每个 Reduce 做部分聚合操作，并输出结果，这样处理的结果是相同的 Group By Key 有可能被分发到不同的 Reduce 中，从而达到负载均衡的目的；第二个 MR Job 再根据预处理的数据结果按照 Group By Key 分布到 Reduce 中（这个过程可以保证相同的 Group By Key 被分布到同一个 Reduce 中），最后完成最终的聚合操作。

#### SQL调优
* 如何Join：关于驱动表的选取，选用join key分布最均匀的表作为驱动表。做好列裁剪和filter操作，以达到两表做join的时候，数据量相对变小的效果。    
* 大小表Join：使用map join让小的维度表（1000条以下的记录条数） 先进内存。在map端完成reduce.    
* 大表Join大表：把空值的key变成一个字符串加上随机数，把倾斜的数据分到不同的reduce上，由于null值关联不上，处理后并不影响最终结果。    
* count distinct大量相同特殊值：count distinct时，将值为空的情况单独处理，如果是计算count distinct，可以不用处理，直接过滤，在最后结果中加1。如果还有其他计算，需要进行group by，可以先将值为空的记录单独处理，再和其他计算结果进行union。    
* group by维度过小：采用sum() group by的方式来替换count(distinct)完成计算。    
* 特殊情况特殊处理：在业务逻辑优化效果的不大情况下，有些时候是可以将倾斜的数据单独拿出来处理。最后union回去。  


### 小结
使map的输出数据更均匀的分布到reduce中去，是我们的最终目标。由于Hash算法的局限性，按key Hash会或多或少的造成数据倾斜。大量经验表明数据倾斜的原因是人为的建表疏忽或业务逻辑可以规避的。在此给出较为通用的步骤：

* 1、采样log表，哪些user_id比较倾斜，得到一个结果表tmp1。由于对计算框架来说，所有的数据过来，他都是不知道数据分布情况的，所以采样是并不可少的。    
* 2、数据的分布符合社会学统计规则，贫富不均。倾斜的key不会太多，就像一个社会的富人不多，奇特的人不多一样。所以tmp1记录数会很少。把tmp1和users做map join生成tmp2,把tmp2读到distribute file cache。这是一个map过程。    
* 3、map读入users和log，假如记录来自log,则检查user_id是否在tmp2里，如果是，输出到本地文件a,否则生成`<user_id,value>`的key,value对，假如记录来自member,生成`<user_id,value>`的key,value对，进入reduce阶段。    
* 4、最终把a文件，把Stage3 reduce阶段输出的文件合并起写到hdfs。  

如果确认业务需要这样倾斜的逻辑，考虑以下的优化方案：

* 1、对于join，在判断小表不大于1G的情况下，使用map join    
* 2、对于group by或distinct，设定 hive.groupby.skewindata=true    
* 3、尽量使用上述的SQL语句调节进行优化  





```

```
