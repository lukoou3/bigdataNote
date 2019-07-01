## Kafka与Flume
### Kafka与Flume比较
在企业中必须要清楚流式数据采集框架 flume 和 kafka 的定位是什么：

flume：Cloudera 公司研发：

* 适合多个生产者；（一个生产者对应一个 Agent 任务）  
* 适合下游数据消费者不多的情况；（多 channel 多 sink 会耗费很多内存）  
* 适合数据安全性要求不高的操作；（实际中更多使用 Memory Channel）  
* 适合与 Hadoop 生态圈对接的操作。（Cloudera 公司的特长）  

kafka：Linkedin 公司研发：

* 适合数据下游消费者众多的情况；（开启更多的消费者任务即可，与 Kafka 集群无关）  
* 适合数据安全性要求较高的操作，支持replication。（数据放在磁盘里）  

因此我们常用的一种模型是：
```
线上数据 --> flume(适合采集tomcat日志) --> kafka(离线/实时) --> flume(根据情景增删该流程) --> HDFS
```

#### Flume 与 kafka 集成
1）配置flume(flume-kafka.conf)
```
# define
a1.sources = r1
a1.sinks = k1
a1.channels = c1

# source
a1.sources.r1.type = exec
a1.sources.r1.command = tail -F -c +0 /opt/module/datas/flume.log
a1.sources.r1.shell = /bin/bash -c

# sink
a1.sinks.k1.type = org.apache.flume.sink.kafka.KafkaSink
a1.sinks.k1.kafka.bootstrap.servers = hadoop102:9092,hadoop103:9092,hadoop104:9092
a1.sinks.k1.kafka.topic = first
a1.sinks.k1.kafka.flumeBatchSize = 20
a1.sinks.k1.kafka.producer.acks = 1
a1.sinks.k1.kafka.producer.linger.ms = 1

# channel
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100

# bind
a1.sources.r1.channels = c1
a1.sinks.k1.channel = c1
```

2） 启动kafka IDEA消费者

3） 进入flume根目录下，启动flume
```
[atguigu@hadoop102 flume]$ bin/flume-ng agent -n a1 -c conf/ -f job/flume-kafka.conf 
```
4） 向 /opt/module/datas/flume.log里追加数据，查看kafka消费者消费情况
```
[atguigu@hadoop102 datas]$$ echo hello > /opt/module/datas/flume.log
```

