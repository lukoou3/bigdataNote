spark-sql是兼容hive的，可以使用hive的udf，把文件传到hdfs上，每次都注册hive临时函数，也方便修改。

```sql
create function strRepeat as 'com.hive.udf.StrRepeat' using jar 'hdfs:///hive-func/hive-func.jar';
desc function extended strRepeat;

add jar hdfs:///hive-func/hive-func.jar;
create temporary function strRepeat as 'com.hive.udf.StrRepeat';

-- 更新jar
-- hadoop fs -put -f hive-func.jar /hive-func
use gmall;
create function maxBy as 'com.hive.udaf.MaxBy' using jar 'hdfs:///hive-func/hive-func.jar';
desc function extended maxBy;


spark-sql --master yarn-client -e "
add jar hdfs:///hive-func/hive-func.jar;
create temporary function strRepeat as 'com.hive.udf.StrRepeat';
select user_id,login_date_first,strRepeat(login_date_first, 2) login_date_first2,login_date_last,login_count from gmall.dwt_user_topic limit 5;
" > out.txt

hive -e "
add jar hdfs:///hive-func/hive-func.jar;
create temporary function strRepeat as 'com.hive.udf.StrRepeat';
select user_id,login_date_first,strRepeat(login_date_first, 2) login_date_first2,login_date_last,login_count from gmall.dwt_user_topic limit 5;
" > out.txt
```

```java
package com.hive.udf;

import org.apache.hadoop.hive.ql.exec.UDF;

public class StrRepeat extends UDF {
    private final StringBuilder sb = new StringBuilder();

    public String evaluate(String value, int repeat) {
        if (value == null) {
            return null;
        }

        if(repeat <= 0){
            return null;
        }

        for (int i = 0; i < repeat; i++) {
            sb.append(value);
        }

        String rst = sb.toString();
        sb.delete(0, sb.length());

        return rst;
    }

}
```


```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <parent>
        <artifactId>HadoopTest</artifactId>
        <groupId>com.hadoop</groupId>
        <version>1.0-SNAPSHOT</version>
    </parent>
    <modelVersion>4.0.0</modelVersion>

    <artifactId>hive</artifactId>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
        <hive.version>2.3.0</hive.version>
    </properties>

    <dependencies>
        <!--添加hive依赖-->
        <dependency>
            <groupId>org.apache.hive</groupId>
            <artifactId>hive-exec</artifactId>
            <version>${hive.version}</version>
            <scope>provided</scope>
        </dependency>

    </dependencies>

    <build>
        <finalName>hive-func</finalName>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.0</version>
            </plugin>

            <plugin>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>2.5.5</version>
                <configuration>
                    <descriptorRefs>
                        <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
                </configuration>
                <executions>
                    <execution>
                        <id>make-zip</id>
                        <!-- 绑定到package生命周期阶段上 -->
                        <phase>package</phase>
                        <goals>
                            <!-- 绑定到package生命周期阶段上 -->
                            <goal>single</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```
