## explode和lateral view
https://www.liangzl.com/get-article-detail-121725.html
### 一、explode()
这个函数大多数人都接触过，将一行数据转换成列数据，可以用于array和map类型的数据。

**用于array的语法如下**：
```
select explode(arraycol) as newcol from tablename;
```

* explode()：函数中的参数传入的是arrary数据类型的列名。  
* newcol：是给转换成的列命名一个新的名字，用于代表转换之后的列名。  
* tablename：原表名。  

**用于map的语法如下**：
```
select explode(mapcol) as (keyname,valuename) from tablename;
```

* explode()：函数中的参数传入的是map数据类型的列名。  
* 由于map是kay-value结构的，所以它在转换的时候会转换成两列，一列是kay转换而成的，一列是value转换而成的。  
* keyname：表示key转换成的列名称，用于代表key转换之后的列名。  
* valuename：表示value转换成的列名称，用于代表value转换之后的列名称。  
* 注意：这两个值需要在as之后用括号括起来然后以逗号分隔。  

**以上为explode()函数的用法，此函数存在局限性**：

* 其一：不能关联原有的表中的其他字段。  
* 其二：不能与group by、cluster by、distribute by、sort by联用。  
* 其三：不能进行UDTF嵌套。  
* 其四：不允许选择其他表达式。  

### 二、lateral view
lateral view是Hive中提供给UDTF的结合，它可以解决UDTF不能添加额外的select列的问题。

lateral view其实就是用来和想类似explode这种UDTF函数联用的，lateral view会将UDTF生成的结果放到一个虚拟表中，然后这个虚拟表会和输入行进行join来达到连接UDTF外的select字段的目的。

**格式一**
```
lateral view udtf(expression) tableAlias as columnAlias (,columnAlias)*
```
lateral view在UDTF前使用，表示连接UDTF所分裂的字段。
UDTF(expression)：使用的UDTF函数，例如explode()。
tableAlias：表示UDTF函数转换的虚拟表的名称。
columnAlias：表示虚拟表的虚拟字段名称，如果分裂之后有一个列，则写一个即可；如果分裂之后有多个列，按照列的顺序在括号中声明所有虚拟列名，以逗号隔开。

**格式二**
```
from basetable (lateral view)*
```
在from子句中使用，一般和格式一搭配使用，这个格式只是说明了lateral view的使用位置。
from子句后面也可以跟多个lateral view语句，使用空格间隔就可以了。

**格式三**
```
from basetable (lateral view outer)*
```
它比格式二只是多了一个outer，这个outer的作用是在UDTF转换列的时候将其中的空也给展示出来，UDTF默认是忽略输出空的，加上outer之后，会将空也输出，显示为NULL。这个功能是在Hive0.12是开始支持的。

### 三、案例
下面来说一个需求案例。

#### 1、需求
有一张hive表，分别是学生姓名name(string)，学生成绩score(map<string,string>),成绩列中key是学科名称，value是对应学科分数，请用一个hql求一下每个学生成绩最好的学科及分数、最差的学科及分数、平均分数。

表数据如下：
```
zhangsan|Chinese:80,Math:60,English:90
lisi|Chinese:90,Math:80,English:70
wangwu|Chinese:88,Math:90,English:96
maliu|Chinese:99,Math:65,English:60
```

#### 2、准备
下面来做一下准备工作，创建表，并将数据导入表中，操作如下：

创建表：
```
create table student_score(name string,score map<String,string>)
row format delimited
fields terminated by '|'
collection items terminated by ','
map keys terminated by ':';
```

导入数据：
```
load data local inpath '/home/test/score' overwrite into table student_score;
```
检查一下数据，如下图：
```
+---------------------+----------------------------------------------+--+
| student_score.name  |             student_score.score              |
+---------------------+----------------------------------------------+--+
| zhangsan            | {"Chinese":"80","Math":"60","English":"90"}  |
| lisi                | {"Chinese":"90","Math":"80","English":"70"}  |
| wangwu              | {"Chinese":"88","Math":"90","English":"96"}  |
| maliu               | {"Chinese":"99","Math":"65","English":"60"}  |
+---------------------+----------------------------------------------+--+
```


确认数据导入没有问题。

#### 3、分析
首先要处理这个表中的数据，本人第一想法是想找一下Hive有没有内置的操作map复杂类型的函数，可惜看了一遍，没有找到，这个思路只能放弃。

第二想法，是将map中的数据转换成一个虚拟表，然后与name字段关联，这样形成一张可操作的虚拟表。在查阅了资料之后，看到explode()函数可以做这个事情，首先写了一条语句：

```
select explode(score) from student_score;
select explode(score) as (key,value) from student_score;
```
结果：
```
+----------+--------+--+
|   key    | value  |
+----------+--------+--+
| Chinese  | 80     |
| Math     | 60     |
| English  | 90     |
| Chinese  | 90     |
| Math     | 80     |
| English  | 70     |
| Chinese  | 88     |
| Math     | 90     |
| English  | 96     |
| Chinese  | 99     |
| Math     | 65     |
| English  | 60     |
+----------+--------+--+
```


此函数验证了它却是可以做到分离map的功能，将行转为列，难么既然行转了列，那么只需要将name字段关联上，就可以进行统计操作了。

可惜的是，explode函数怎么使用，都关联不了name字段。

既然Hive有这些东西，肯定能够做到关联其他字段的，这是本人作为一个程序员的信念，如果没有的话，这个功能做出来就是鸡肋了，只有关联了其他可以确定其为唯一消息的字段，这样的功能才又意义。

又在网上查询到，经常和explode函数和用的就是lateral view函数，那么这两个结合就能做到关联其他字段。写法如下：
```
select name,key,value from student_score lateral view explode(score) scntable as key,value;
```
结果如下：
```
+-----------+----------+--------+--+
|   name    |   key    | value  |
+-----------+----------+--------+--+
| zhangsan  | Chinese  | 80     |
| zhangsan  | Math     | 60     |
| zhangsan  | English  | 90     |
| lisi      | Chinese  | 90     |
| lisi      | Math     | 80     |
| lisi      | English  | 70     |
| wangwu    | Chinese  | 88     |
| wangwu    | Math     | 90     |
| wangwu    | English  | 96     |
| maliu     | Chinese  | 99     |
| maliu     | Math     | 65     |
| maliu     | English  | 60     |
+-----------+----------+--------+--+
```


看到上面的数据，就是我们想要的结果，产生了这样一个虚拟表之后，所有的工作都变的简单了起来。

从上面两条语句可以看出，explode在select句中和在from子句中给虚拟字段命名的格式稍微有些差别，select句中需要加括号，from子句中不需要括号。

以上是这个需求的难点，其他的就不在做过多的说明。

#### 4、结果
下面将结果抛出来，这可能不是最优的，但是是一种方式：
```
select sname,gk,gv,bk,bv,av from (
select * from (
select C.name as sname,C.key as gk,C.value as gv from (
select name,max(value) as gv from (
select name,key,value from student_score
lateral view explode(score) scnTable as key,value) as A
group by name) as B
left join
(select name,key,value from student_score
lateral view explode(score) scnTable as key,value) as C
on B.name=C.name and B.gv=C.value) as GG
left join
(select C.name as bname,C.key as bk,C.value as bv from
(select name,min(value) as bv from (
select name,key,value from student_score
lateral view explode(score) scnTable as key,value) as A
group by name) as B
left join
(select name,key,value from student_score
lateral view explode(score) snTable as key,value) as C
on B.name=C.name and B.bv=C.value) as BB
on GG.sname=BB.bname) as SS
left join
(select name as aname,avg(value) as av from (
select name,key,value from student_score
lateral view explode(score) scnTable as key,value) as A 
group by name) AA
on SS.sname=AA.aname;
```
结果如下：

列名依次为：姓名、最好成绩的科目、分数、最差成绩的科目、分数、平均分
```
+-----------+----------+-----+----------+-----+--------------------+--+
|   sname   |    gk    | gv  |    bk    | bv  |         av         |
+-----------+----------+-----+----------+-----+--------------------+--+
| lisi      | Chinese  | 90  | English  | 70  | 80.0               |
| maliu     | Chinese  | 99  | English  | 60  | 74.66666666666667  |
| wangwu    | English  | 96  | Chinese  | 88  | 91.33333333333333  |
| zhangsan  | English  | 90  | Math     | 60  | 76.66666666666667  |
+-----------+----------+-----+----------+-----+--------------------+--+
```

这里需要说一些，Hive中的基本数据类型，string类型应该是使用的自动转换机制，转换为了int，这里将score map<string,string>声明为score map<string,int>也是可以的。

通过中间表解决：
```
create table testdb.student_score_info(
name string,
subject string,
score int
)
row format delimited fields terminated by '\t';

insert into table testdb.student_score_info
select name,key,value from testdb.student_score lateral view explode(score) scntable as key,value;
```

查询：
```
select name,subject,score from testdb.student_score_info;

+-----------+----------+--------+--+
|   name    | subject  | score  |
+-----------+----------+--------+--+
| zhangsan  | Chinese  | 80     |
| zhangsan  | Math     | 60     |
| zhangsan  | English  | 90     |
| lisi      | Chinese  | 90     |
| lisi      | Math     | 80     |
| lisi      | English  | 70     |
| wangwu    | Chinese  | 88     |
| wangwu    | Math     | 90     |
| wangwu    | English  | 96     |
| maliu     | Chinese  | 99     |
| maliu     | Math     | 65     |
| maliu     | English  | 60     |
+-----------+----------+--------+--+


select a.name,score_max,score_min,score_avg from
(
select name,max(score) score_max from testdb.student_score_info group by name
) a
left join
(
select name,min(score) score_min from testdb.student_score_info group by name
) b on a.name = b.name
left join
(
select name,avg(score) score_avg from testdb.student_score_info group by name
) c on a.name = c.name;

+-----------+------------+------------+--------------------+--+
|  a.name   | score_max  | score_min  |     score_avg      |
+-----------+------------+------------+--------------------+--+
| lisi      | 90         | 70         | 80.0               |
| maliu     | 99         | 60         | 74.66666666666667  |
| wangwu    | 96         | 88         | 91.33333333333333  |
| zhangsan  | 90         | 60         | 76.66666666666667  |
+-----------+------------+------------+--------------------+--+
```
