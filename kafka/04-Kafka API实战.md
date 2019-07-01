## Kafka API
### 环境准备
导入pom依赖
```xml
<dependencies>
    <!-- https://mvnrepository.com/artifact/org.apache.kafka/kafka-clients -->
    <dependency>
        <groupId>org.apache.kafka</groupId>
        <artifactId>kafka-clients</artifactId>
        <version>0.11.0.0</version>
    </dependency>
    <!-- https://mvnrepository.com/artifact/org.apache.kafka/kafka -->
    <dependency>
        <groupId>org.apache.kafka</groupId>
        <artifactId>kafka_2.12</artifactId>
        <version>0.11.0.2</version>
    </dependency>
</dependencies>
```

### Kafka生产者Java API
#### 创建生产者（新的API）
```java
package com.kafka.java.producer;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Properties;

//创建生产者（新API）
public class CustomProducer {
    public static void main(String[] args) {
        Properties props = new Properties();
        // Kafka服务端的主机名和端口号
        props.put("bootstrap.servers", "hadoop01:9092,hadoop02:9092,hadoop03:9092");
        // 等待所有副本节点的应答
        //props.put("acks", "all");
        props.put("acks", "1");
        // 消息发送最大尝试次数
        props.put("retries", 0);
        // 一批消息处理大小
        props.put("batch.size", 16384);
        // 请求延时
        props.put("linger.ms", 1);
        // 发送缓存区内存大小
        props.put("buffer.memory", 33554432);
        // key序列化
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        // value序列化
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        for (int i = 0; i < 50; i++) {
            producer.send(new ProducerRecord<String, String>("test", Integer.toString(i), "hello world-" + i));
        }

        //关闭资源
        producer.close();
    }
}
```

#### 创建生产者带回调函数（新的API）
```java
package com.kafka.java.producer;

import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;

import java.util.Properties;

//创建生产者带回调函数（新API）
public class CallBackProducer {

	public static void main(String[] args) throws InterruptedException {
		Properties props = new Properties();
		// Kafka服务端的主机名和端口号
		props.put("bootstrap.servers", "hadoop01:9092,hadoop02:9092,hadoop:9092");
		// 等待所有副本节点的应答
		props.put("acks", "all");
		// 消息发送最大尝试次数
		props.put("retries", 0);
		// 一批消息处理大小
		props.put("batch.size", 16384);
		// 增加服务端请求延时
		props.put("linger.ms", 1);
		// 发送缓存区内存大小
		props.put("buffer.memory", 33554432);
		// key序列化
		props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
		// value序列化
		props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
		// 自定义分区
//		props.put("partitioner.class", "com.atguigu.kafka.CustomPartitioner");

		KafkaProducer<String, String> kafkaProducer = new KafkaProducer<>(props);

		for (int i = 0; i < 50; i++) {
			Thread.sleep(100);
			kafkaProducer.send(new ProducerRecord<String, String>("test", "hh" + i), new Callback() {
				@Override
				public void onCompletion(RecordMetadata metadata, Exception exception) {
					if (metadata != null) {

						System.out.println(metadata.partition() + "---" + metadata.offset());
					}
				}
			});
		}

		//关闭资源
		kafkaProducer.close();

	}

}
```

#### 自定义分区生产者
0）需求：将所有数据存储到topic的第0号分区上。
1）定义一个类实现Partitioner接口，重写里面的方法
```java
import org.apache.kafka.clients.producer.Partitioner;
import org.apache.kafka.common.Cluster;

import java.util.Map;

public class CustomPartitioner implements Partitioner{
    @Override
    public int partition(String topic, Object key, byte[] keyBytes, Object value, byte[] valueBytes, Cluster cluster) {
        return 0;
    }

    @Override
    public void close() {

    }

    @Override
    public void configure(Map<String, ?> configs) {

    }
}
```

2）在代码中调用
```java
import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;

import java.util.Properties;

//创建生产者使用自定义分区器（新API）
public class CustomProducerWithPartitioner {
    public static void main(String[] args) throws Exception {
        Properties props = new Properties();
        // Kafka服务端的主机名和端口号
        props.put("bootstrap.servers", "hadoop01:9092,hadoop02:9092,hadoop:9092");
        // 等待所有副本节点的应答
        props.put("acks", "all");
        // 消息发送最大尝试次数
        props.put("retries", 0);
        // 一批消息处理大小
        props.put("batch.size", 16384);
        // 增加服务端请求延时
        props.put("linger.ms", 1);
        // 发送缓存区内存大小
        props.put("buffer.memory", 33554432);
        // key序列化
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        // value序列化
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        // 自定义分区
		props.put("partitioner.class", "com.kafka.java.CustomPartitioner");

        KafkaProducer<String, String> kafkaProducer = new KafkaProducer<>(props);

        for (int i = 0; i < 50; i++) {
            Thread.sleep(100);
            kafkaProducer.send(new ProducerRecord<String, String>("test", "hh_pp" + i), new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {
                    if (metadata != null) {

                        System.out.println(metadata.partition() + "---" + metadata.offset());
                    }
                }
            });
        }

        //关闭资源
        kafkaProducer.close();
    }
}
```

### Kafka消费者Java API
#### 自动维护消费情况
```java
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

import java.util.Arrays;
import java.util.Properties;

//消费者自动维护消费情况（新API）
//不能控制分区和offset，每次都是从最新的消息开始消费
public class CustomConsumer {
    public static void main(String[] args) {
        Properties props = new Properties();
        // 定义kakfa 服务的地址，不需要将所有broker指定上
        props.put("bootstrap.servers", "hadoop01:9092,hadoop02:9092,hadoop:9092");
        // 制定consumer group
        props.put("group.id", "g11");
        // 是否自动确认offset
        props.put("enable.auto.commit", "true");
        // 自动确认offset的时间间隔
        props.put("auto.commit.interval.ms", "1000");
        // key的序列化类
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // value的序列化类
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // 定义consumer
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);

        // 消费者订阅的topic, 可同时订阅多个
        consumer.subscribe(Arrays.asList("test"));

        while (true) {
            // 读取数据，读取超时时间为100ms
            ConsumerRecords<String, String> records = consumer.poll(100);
            System.out.println("********************************");

            for (ConsumerRecord<String, String> record : records)
                System.out.printf("topic = %s,partition = %d,offset = %d, key = %s, value = %s%n",record.topic(), record.partition(),record.offset(), record.key(), record.value());
        }
    }
}
```


#### 指定topic，指定partition，指定offset
主要的代码：
```java
//通过TopicPartition指定要消费的partition
TopicPartition seekToBeginPartition = new TopicPartition("test",0);
//对consumer指定partitionassign
consumer.assign(Arrays.asList(seekToBeginPartition));
//调用consumer.seekToBeginning指定从头开始消费
consumer.seekToBeginning(Arrays.asList(seekToBeginPartition));


//通过TopicPartition指定要消费的partition
TopicPartition seekToEndPartition = new TopicPartition("test",0);
//对consumer指定partitionassign
consumer.assign(Arrays.asList(seekToEndPartition));
//调用consumer.seekToBeginning指定从头开始消费
consumer.seekToEnd(Arrays.asList(seekToEndPartition));


//通过TopicPartition指定要消费的partition
TopicPartition seekPartition = new TopicPartition("test",0);
//对consumer指定partitionassign
consumer.assign(Arrays.asList(seekPartition));
//调用consumer.seekToBeginning指定从头开始消费
consumer.seek(seekPartition,156);
```

完整的代码：
```java
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;

import java.util.Arrays;
import java.util.Properties;

//指定partition,指定offset的数据
public class CustomConsumerPartitionOffset {
    public static void main(String[] args) {
        //testSeekToBeginning();
        //testSeekToEnd();
        testSeek();
    }

    //从头开始消费消息seekToBeginning()
    public static void testSeekToBeginning(){
        Properties props = new Properties();
        // 定义kakfa 服务的地址，不需要将所有broker指定上
        props.put("bootstrap.servers", "hadoop01:9092,hadoop02:9092,hadoop:9092");
        // 制定consumer group
        props.put("group.id", "group1");
        // key的序列化类
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // value的序列化类
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // 定义consumer
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);

        //通过TopicPartition指定要消费的partition
        TopicPartition seekToBeginPartition = new TopicPartition("test",0);
        //对consumer指定partitionassign
        consumer.assign(Arrays.asList(seekToBeginPartition));
        //调用consumer.seekToBeginning指定从头开始消费
        consumer.seekToBeginning(Arrays.asList(seekToBeginPartition));

        while (true) {
            // 读取数据，读取超时时间为100ms
            ConsumerRecords<String, String> records = consumer.poll(100);
            System.out.println("********************************");

            for (ConsumerRecord<String, String> record : records)
                System.out.printf("topic = %s,partition = %d,offset = %d, key = %s, value = %s%n",record.topic(), record.partition(),record.offset(), record.key(), record.value());
        }
    }

    //从尾开始消费消息seekToEnd()
    public static void testSeekToEnd(){
        Properties props = new Properties();
        // 定义kakfa 服务的地址，不需要将所有broker指定上
        props.put("bootstrap.servers", "hadoop01:9092,hadoop02:9092,hadoop:9092");
        // 制定consumer group
        props.put("group.id", "group1");
        // key的序列化类
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // value的序列化类
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // 定义consumer
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);

        //通过TopicPartition指定要消费的partition
        TopicPartition seekToEndPartition = new TopicPartition("test",0);
        //对consumer指定partitionassign
        consumer.assign(Arrays.asList(seekToEndPartition));
        //调用consumer.seekToBeginning指定从头开始消费
        consumer.seekToEnd(Arrays.asList(seekToEndPartition));

        while (true) {
            // 读取数据，读取超时时间为100ms
            ConsumerRecords<String, String> records = consumer.poll(100);
            System.out.println("********************************");

            for (ConsumerRecord<String, String> record : records)
                System.out.printf("topic = %s,partition = %d,offset = %d, key = %s, value = %s%n",record.topic(), record.partition(),record.offset(), record.key(), record.value());
        }
    }


    //消费指定offset消息seek()
    public static void testSeek(){
        Properties props = new Properties();
        // 定义kakfa 服务的地址，不需要将所有broker指定上
        props.put("bootstrap.servers", "hadoop01:9092,hadoop02:9092,hadoop:9092");
        // 制定consumer group
        props.put("group.id", "group1");
        // key的序列化类
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // value的序列化类
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        // 定义consumer
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);

        //通过TopicPartition指定要消费的partition
        TopicPartition seekPartition = new TopicPartition("test",0);
        //对consumer指定partitionassign
        consumer.assign(Arrays.asList(seekPartition));
        //调用consumer.seekToBeginning指定从头开始消费
        consumer.seek(seekPartition,156);

        while (true) {
            // 读取数据，读取超时时间为100ms
            ConsumerRecords<String, String> records = consumer.poll(100);
            System.out.println("********************************");

            for (ConsumerRecord<String, String> record : records)
                System.out.printf("topic = %s,partition = %d,offset = %d, key = %s, value = %s%n",record.topic(), record.partition(),record.offset(), record.key(), record.value());
        }
    }
}
```
























