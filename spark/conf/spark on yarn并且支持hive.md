# spark on yarn并且支持hive
spark像hive一样只在一台机器上就行，运行在yarn上，这样还可以使用不同的spark版本。


## 配置文件

### hive-site.xml
使spark支持hive。

hive-site.xml
```xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>

    <property>
        <name>hive.metastore.uris</name>
        <value>thrift://hadoop101:9083</value>
    </property>
    
</configuration>

```

### spark-env.sh
`HADOOP_CONF_DIR=/opt/module/hadoop-2.7.2/etc/hadoop`读取hadoop配置，使知道hdfs、yarn的环境变量。

spark-env.sh
```sh
#!/usr/bin/env bash

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# This file is sourced when running various Spark programs.
# Copy it as spark-env.sh and edit that to configure Spark for your site.

HADOOP_CONF_DIR=/opt/module/hadoop-2.7.2/etc/hadoop


# Options read when launching programs locally with
# ./bin/run-example or ./bin/spark-submit
# - HADOOP_CONF_DIR, to point Spark towards Hadoop configuration files
# - SPARK_LOCAL_IP, to set the IP address Spark binds to on this node
# - SPARK_PUBLIC_DNS, to set the public dns name of the driver program

# Options read by executors and drivers running inside the cluster
# - SPARK_LOCAL_IP, to set the IP address Spark binds to on this node
# - SPARK_PUBLIC_DNS, to set the public DNS name of the driver program
# - SPARK_LOCAL_DIRS, storage directories to use on this node for shuffle and RDD data
# - MESOS_NATIVE_JAVA_LIBRARY, to point to your libmesos.so if you use Mesos

# Options read in YARN client mode
# - HADOOP_CONF_DIR, to point Spark towards Hadoop configuration files
# - SPARK_EXECUTOR_CORES, Number of cores for the executors (Default: 1).
# - SPARK_EXECUTOR_MEMORY, Memory per Executor (e.g. 1000M, 2G) (Default: 1G)
# - SPARK_DRIVER_MEMORY, Memory for Driver (e.g. 1000M, 2G) (Default: 1G)

# Options for the daemons used in the standalone deploy mode
# - SPARK_MASTER_HOST, to bind the master to a different IP address or hostname
# - SPARK_MASTER_PORT / SPARK_MASTER_WEBUI_PORT, to use non-default ports for the master
# - SPARK_MASTER_OPTS, to set config properties only for the master (e.g. "-Dx=y")
# - SPARK_WORKER_CORES, to set the number of cores to use on this machine
# - SPARK_WORKER_MEMORY, to set how much total memory workers have to give executors (e.g. 1000m, 2g)
# - SPARK_WORKER_PORT / SPARK_WORKER_WEBUI_PORT, to use non-default ports for the worker
# - SPARK_WORKER_DIR, to set the working directory of worker processes
# - SPARK_WORKER_OPTS, to set config properties only for the worker (e.g. "-Dx=y")
# - SPARK_DAEMON_MEMORY, to allocate to the master, worker and history server themselves (default: 1g).
# - SPARK_HISTORY_OPTS, to set config properties only for the history server (e.g. "-Dx=y")
# - SPARK_SHUFFLE_OPTS, to set config properties only for the external shuffle service (e.g. "-Dx=y")
# - SPARK_DAEMON_JAVA_OPTS, to set config properties for all daemons (e.g. "-Dx=y")
# - SPARK_PUBLIC_DNS, to set the public dns name of the master or workers

# Generic options for the daemons used in the standalone deploy mode
# - SPARK_CONF_DIR      Alternate conf dir. (Default: ${SPARK_HOME}/conf)
# - SPARK_LOG_DIR       Where log files are stored.  (Default: ${SPARK_HOME}/logs)
# - SPARK_PID_DIR       Where the pid file is stored. (Default: /tmp)
# - SPARK_IDENT_STRING  A string representing this instance of spark. (Default: $USER)
# - SPARK_NICENESS      The scheduling priority for daemons. (Default: 0)
# - SPARK_NO_DAEMONIZE  Run the proposed command in the foreground. It will not output a PID file.

```

### spark-defaults.conf
`spark.yarn.jars=hdfs://hadoop101:9000/spark2.4/jars/*`,只是上传spark的jar到hdfs上的路径，配置了这个每次使用spark-submit命令时就不会上传jar了。


spark-defaults.conf
```
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Default system properties included when running spark-submit.
# This is useful for setting default environmental settings.

# Example:
# spark.master                     spark://master:7077
# spark.eventLog.enabled           true
# spark.eventLog.dir               hdfs://namenode:8021/directory
# spark.serializer                 org.apache.spark.serializer.KryoSerializer
# spark.driver.memory              5g
# spark.executor.extraJavaOptions  -XX:+PrintGCDetails -Dkey=value -Dnumbers="one two three"
spark.yarn.jars=hdfs://hadoop101:9000/spark2.4/jars/*
# spark.yarn.dist.archives=hdfs:///python/py_367.zip#py_367_env
# spark.yarn.appMasterEnv.PYSPARK_PYTHON=./py_367_env/py_367/bin/python

```

## spark命令
下面三个命令的参数都是通用的

### spark-submit
生产环境主要使用命令

### spark-shell
主要用于client模式测试
```
spark-shell --master yarn
spark-shell --master local[5]
```

### spark-sql
和hive的客户端类似，而且可用于saprksql生产环境使用，`spark-sql -e sql`
```
spark-sql --master yarn
spark-sql --master local[5]
```

### pyspark
pyspark调试测试环境，不过使用jupyter更好。

pyspark生产环境提交
```sh
spark-submit \
--master yarn \
--deploy-mode cluster \
--conf spark.yarn.dist.archives=hdfs:///python/py_367.zip#py_367_env \
--conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=./py_367_env/py_367/bin/python \
--conf spark.pyspark.driver.python=./py_367_env/py_367/bin/python \
--conf spark.pyspark.python=./py_367_env/py_367/bin/python \
pyspark_test.py


# client不行必须和driver的python环境保持一致
spark-submit \
--master yarn \
--deploy-mode client \
--conf spark.yarn.dist.archives=hdfs:///python/py_367.zip#py_367_env \
--conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=./py_367_env/py_367/bin/python \
--conf spark.pyspark.driver.python=./py_367_env/py_367/bin/python \
--conf spark.pyspark.python=./py_367_env/py_367/bin/python \
pyspark_test.py
```




```

```
