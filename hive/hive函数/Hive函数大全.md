[TOC]

## 一、关系运算：
### 1、等值比较: = 和 <=>
**语法**：A=B
**操作类型**：所有基本类型
**描述**: 如果表达式A与表达式B相等，则为TRUE；否则为FALSE。只要一个为null，返回null

```sql
hive> select 1 from iteblog where 1=1;
1

hive> select null = null;
NULL

hive> select 1 = null;
NULL

hive> select null = 1;
NULL
```

**语法**：A<=>B
**操作类型**：所有基本类型
**描述**: 如果A和B都为NULL，则返回TRUE，其他的和等号（=）操作符的结果一致，如果任一为NULL则结果为false

```sql
hive> select 1 <=> 1;
true

hive> select 1 <=> null;
false

hive> select null <=> 1;
false

hive> select null <=> null;
true

```

### 2、不等值比较: <> 和 !=
语法: A <> B
操作类型: 所有基本类型
描述: 如果表达式A为NULL，或者表达式B为NULL，返回NULL；如果表达式A与表达式B不相等，则为TRUE；否则为FALSE

```sql
hive> select 1 != null;
NULL

hive> select 1 <> null;
NULL

hive> select null <> null;
NULL

hive> select 1 <> 2;
true

hive> select 1 <> 1;
false

```

### 3、小于比较: <
语法: A < B
操作类型：所有基本类型
描述: 如果表达式A为NULL，或者表达式B为NULL，返回NULL；如果表达式A小于表达式B，则为TRUE；否则为FALSE

```sql
hive> select 1 from iteblog where 1 < 2;
1
```

### 4、小于等于比较: <=
语法: A <= B
操作类型: 所有基本类型
描述: 如果表达式A为NULL，或者表达式B为NULL，返回NULL；如果表达式A小于或者等于表达式B，则为TRUE；否则为FALSE

```sql
hive> select 1 from iteblog where 1 < = 1;
1
```

### 5、大于比较: >
语法: A > B
操作类型: 所有基本类型
描述: 如果表达式A为NULL，或者表达式B为NULL，返回NULL；如果表达式A大于表达式B，则为TRUE；否则为FALSE

```sql
hive> select 1 from iteblog where 2 > 1;
1
```

### 6、大于等于比较: >=
语法: A >= B
操作类型: 所有基本类型
描述: 如果表达式A为NULL，或者表达式B为NULL，返回NULL；如果表达式A大于或者等于表达式B，则为TRUE；否则为FALSE

```sql
hive> select 1 from iteblog where 1 >= 1;
1
```

### 7、区间比较: BETWEEN  AND 
语法: A [NOT] BETWEEN B AND C
操作类型: 所有基本类型
描述: 如果A，B或者C任一为NULL，则结果为NULL。如果A的值大于等于B而且小于或等于C，则结果为TRUE，反之为FALSE。如果使用NOT关键字则可达到相反的效果。区间范围为左闭右闭。

```sql
hive> select 2 between 1 and 3;
true

hive> select 2 between 2 and 2;
true

```

### 8、空值判断: IS NULL
语法: A IS NULL
操作类型: 所有类型
描述: 如果表达式A的值为NULL，则为TRUE；否则为FALSE

```sql
hive> select 1 from iteblog where null is null;
1
```

### 9、非空判断: IS NOT NULL
语法: A IS NOT NULL
操作类型: 所有类型
描述: 如果表达式A的值为NULL，则为FALSE；否则为TRUE

```sql
hive> select 1 from iteblog where 1 is not null;
1
```

### 10、in 范围判断: in (a,b,c)
语法: A IN ( A, B, C )
操作类型: 所有基本类型
描述: 如果A的值在范围内，则为TRUE；否则为FALSE

```sql
hive> select 4 in (2,3,4);
true

hive> select 1 in (2,3,4);
false

hive> select "4" in (2,3,4);
true

hive> select 4 in (2,3,"4");
true
```

### 11、LIKE比较: LIKE
语法: A [NOT] LIKE B
操作类型: strings
描述: `如果字符串A或者字符串B为NULL，则返回NULL；如果字符串A符合表达式B 的正则语法，则为TRUE；否则为FALSE。B中字符”_”表示任意单个字符，而字符”%”表示任意数量的字符。B的表达式说明如下：‘x%’表示A必须以字母‘x’开头，‘%x’表示A必须以字母’x’结尾，而‘%x%’表示A包含有字母’x’,可以位于开头，结尾或者字符串中间。如果使用NOT关键字则可达到相反的效果。`


```sql
hive> select 'football' like 'foot%';
true

hive> select 'football' like 'foot____';
true

hive> select 'football' not like 'fff%';
true
```

### 12、JAVA的LIKE操作: RLIKE
语法: A [NOT] RLIKE B
操作类型: strings
描述: 如果字符串A或者字符串B为NULL，则返回NULL；如果字符串A符合JAVA正则表达式B的正则语法，则为TRUE；否则为FALSE。

```sql
hive> select 'footbar' rlike '^f.*r$';
true

hive> select 'footbar' not rlike '^f.*r$';
false

#注意：判断一个字符串是否全为数字：
hive> select '123456' rlike '^\d+$';
true
```

### 13、REGEXP操作: REGEXP
语法: A [NOT] REGEXP B
操作类型: strings
描述: 功能与RLIKE相同

```sql
hive> select 'footbar' regexp '^f.*r$';
true

hive> select 'footbar' not regexp '^f.*r$';
false
```

## 二、数学运算：
### 1、加法操作: +
语法: A + B
操作类型：所有数值类型
说明：返回A与B相加的结果。结果的数值类型等于A的类型和B的类型的最小父类型（详见数据类型的继承关系）。比如，int + int 一般结果为int类型，而 int + double 一般结果为double类型

```sql
hive> select 1 + 9 from iteblog;
10
hive> create table iteblog as select 1 + 1.2 from iteblog;
hive> describe iteblog;
_c0     double
```

### 2、减法操作: -
语法: A – B
操作类型：所有数值类型
说明：返回A与B相减的结果。结果的数值类型等于A的类型和B的类型的最小父类型（详见数据类型的继承关系）。比如，int – int 一般结果为int类型，而 int – double 一般结果为double类型

```sql
hive> select 10 – 5 from iteblog;
5
hive> create table iteblog as select 5.6 – 4 from iteblog;
hive> describe iteblog;
_c0     double
```

### 3、乘法操作: *
语法: A * B
操作类型：所有数值类型
说明：返回A与B相乘的结果。结果的数值类型等于A的类型和B的类型的最小父类型（详见数据类型的继承关系）。注意，如果A乘以B的结果超过默认结果类型的数值范围，则需要通过cast将结果转换成范围更大的数值类型

```sql
hive> select 40 * 5 from iteblog;
200
```

### 4、除法操作: /
语法: A / B
操作类型：所有数值类型
说明：返回A除以B的结果。结果的数值类型为double

```sql
hive> select 40 / 5 from iteblog;
8.0
```
注意：hive中最高精度的数据类型是double,只精确到小数点后16位，在做除法运算的时候要特别注意
```sql
hive>select ceil(28.0/6.999999999999999999999) from iteblog limit 1;    
结果为4
hive>select ceil(28.0/6.99999999999999) from iteblog limit 1;           
结果为5
```

### 5、取余操作: %
语法: A % B
操作类型：所有数值类型
说明：返回A除以B的余数。结果的数值类型等于A的类型和B的类型的最小父类型（详见数据类型的继承关系）。

```sql
hive> select 41 % 5 from iteblog;
1
hive> select 8.4 % 4 from iteblog;
0.40000000000000036
```

```sql
注意：精度在hive中是个很大的问题，类似这样的操作最好通过round指定精度

hive> select round(8.4 % 4 , 2) from iteblog;
0.4
```

### 6、位与操作: &
语法: A & B
操作类型：所有数值类型
说明：返回A和B按位进行与操作的结果。结果的数值类型等于A的类型和B的类型的最小父类型（详见数据类型的继承关系）。

```sql
hive> select 4 & 8 from iteblog;
0
hive> select 6 & 4 from iteblog;
4
```

### 7、位或操作: |
语法: A | B
操作类型：所有数值类型
说明：返回A和B按位进行或操作的结果。结果的数值类型等于A的类型和B的类型的最小父类型（详见数据类型的继承关系）。

```sql
hive> select 4 | 8 from iteblog;
12
hive> select 6 | 8 from iteblog;
14
```

### 8、位异或操作: ^
语法: A ^ B
操作类型：所有数值类型
说明：返回A和B按位进行异或操作的结果。结果的数值类型等于A的类型和B的类型的最小父类型（详见数据类型的继承关系）。

```sql
hive> select 4 ^ 8 from iteblog;
12
hive> select 6 ^ 4 from iteblog;
2
```

### 9．位取反操作: ~
语法: `~`A
操作类型：所有数值类型
说明：返回A按位取反操作的结果。结果的数值类型等于A的类型。

```sql
hive> select ~6 from iteblog;
-7
hive> select ~4 from iteblog;
-5
```

## 三、逻辑运算： 
### 1、逻辑与操作: AND
语法: A AND B
操作类型：boolean
说明：如果A和B均为TRUE，则为TRUE；否则为FALSE。如果A为NULL或B为NULL，则为NULL

```sql
hive> select 1 from iteblog where 1=1 and 2=2;
1
```

### 2、逻辑或操作: OR
语法: A OR B
操作类型：boolean
说明：如果A为TRUE，或者B为TRUE，或者A和B均为TRUE，则为TRUE；否则为FALSE

```sql
hive> select 1 from iteblog where 1=2 or 2=2;
1
```

### 3、逻辑非操作: NOT
语法: NOT A
操作类型：boolean
说明：如果A为FALSE，或者A为NULL，则为TRUE；否则为FALSE

```sql
hive> select 1 from iteblog where not 1=2;
1
```

## 四、数值计算函数
### 1、取整函数: round
语法: round(double a)
返回值: BIGINT
说明: 返回double类型的整数值部分 （遵循四舍五入）

```sql
hive> select round(3.1415926) from iteblog;
3
hive> select round(3.5) from iteblog;
4
hive> create table iteblog as select round(9542.158) from iteblog;
hive> describe iteblog;
_c0     bigint

```

### 2、指定精度取整函数: round
语法: round(double a, int d)
返回值: DOUBLE
说明: 返回指定精度d的double类型

```sql
hive> select round(3.1415926,4) from iteblog;
3.1416
```

### 3、向下取整函数: floor
语法: floor(double a)
返回值: BIGINT
说明: 返回等于或者小于该double变量的最大的整数

```sql
hive> select floor(3.1415926) from iteblog;
3
hive> select floor(25) from iteblog;
25
```

### 4、向上取整函数: ceil
语法: ceil(double a)
返回值: BIGINT
说明: 返回等于或者大于该double变量的最小的整数

```sql
hive> select ceil(3.1415926) from iteblog;
4
hive> select ceil(46) from iteblog;
46
```

### 5、向上取整函数: ceiling
语法: ceiling(double a)
返回值: BIGINT
说明: 与ceil功能相同

```sql
hive> select ceiling(3.1415926) from iteblog;
4
hive> select ceiling(46) from iteblog;
46
```

### 6、取随机数函数: rand
语法: rand(),rand(int seed)
返回值: double
说明: 返回一个0到1范围内的随机数。如果指定种子seed，则会等到一个稳定的随机数序列

```sql
hive> select rand() from iteblog;
0.5577432776034763
hive> select rand() from iteblog;
0.6638336467363424
hive> select rand(100) from iteblog;
0.7220096548596434
hive> select rand(100) from iteblog;
0.7220096548596434
```

### 7、自然指数(对数)函数: exp 、ln
语法: exp(double a)
返回值: double
说明: 返回自然对数e的a次方

```sql
hive> select exp(2) from iteblog;
7.38905609893065
```

自然对数函数: ln
语法: ln(double a)
返回值: double
说明: 返回a的自然对数
```sql
hive> select ln(7.38905609893065) from iteblog;
2.0
```

### 8、以10为底对数函数: log10
语法: log10(double a)
返回值: double
说明: 返回以10为底的a的对数

```sql
hive> select log10(100) from iteblog;
2.0
```

### 9、以2为底对数函数: log2
语法: log2(double a)
返回值: double
说明: 返回以2为底的a的对数

```sql
hive> select log2(8) from iteblog;
3.0
```

### 10、对数函数: log
语法: log(double base, double a)
返回值: double
说明: 返回以base为底的a的对数

```sql
hive> select log(4,256) from iteblog;
4.0
```

### 11、幂运算函数: pow
语法: pow(double a, double p)
返回值: double
说明: 返回a的p次幂

```sql
hive> select pow(2,4) from iteblog;
16.0
```

### 12、幂运算函数: power
语法: power(double a, double p)
返回值: double
说明: 返回a的p次幂,与pow功能相同

```sql
hive> select power(2,4) from iteblog;
16.0
```

### 13、开平方函数: sqrt
语法: sqrt(double a)
返回值: double
说明: 返回a的平方根

```sql
hive> select sqrt(16) from iteblog;
4.0
```

### 14、二进制函数: bin
语法: bin(BIGINT a)
返回值: string
说明: 返回a的二进制代码表示

```sql
hive> select bin(7) from iteblog;
111
```

### 15、十六进制函数: hex
语法: hex(BIGINT a)
返回值: string
说明: 如果变量是int类型，那么返回a的十六进制表示；如果变量是string类型，则返回该字符串的十六进制表示

```sql
hive> select hex(17) from iteblog;
11
hive> select hex(‘abc’) from iteblog;
616263
```

### 16、反转十六进制函数: unhex
语法: unhex(string a)
返回值: string
说明: 返回该十六进制字符串所代码的字符串

```sql
hive> select unhex(‘616263’) from iteblog;
abc
hive> select unhex(‘11’) from iteblog;
-
hive> select unhex(616263) from iteblog;
abc
```

### 17、进制转换函数: conv
语法: conv(BIGINT num, int from_base, int to_base)
返回值: string
说明: 将数值num从from_base进制转化到to_base进制

```sql
hive> select conv(17,10,16) from iteblog;
11
hive> select conv(17,10,2) from iteblog;
10001
```

### 18、绝对值函数: abs
语法: abs(double a) abs(int a)
返回值: double int
说明: 返回数值a的绝对值

```sql
hive> select abs(-3.9) from iteblog;
3.9
hive> select abs(10.9) from iteblog;
10.9
```

### 19、正取余函数: pmod
语法: pmod(int a, int b),pmod(double a, double b)
返回值: int double
说明: 返回正的a除以b的余数

```sql
hive> select pmod(9,4) from iteblog;
1
hive> select pmod(-9,4) from iteblog;
3
```

### 20、正弦函数: sin
语法: sin(double a)
返回值: double
说明: 返回a的正弦值

```sql
hive> select sin(0.8) from iteblog;
0.7173560908995228
```

### 21、反正弦函数: asin
语法: asin(double a)
返回值: double
说明: 返回a的反正弦值

```sql
hive> select asin(0.7173560908995228) from iteblog;
0.8
```

### 22、余弦函数: cos
语法: cos(double a)
返回值: double
说明: 返回a的余弦值

```sql
hive> select cos(0.9) from iteblog;
0.6216099682706644
```

### 23、反余弦函数: acos
语法: acos(double a)
返回值: double
说明: 返回a的反余弦值

```sql
hive> select acos(0.6216099682706644) from iteblog;
0.9
```

### 24、positive函数: positive
语法: positive(int a), positive(double a)
返回值: int double
说明: 返回a

```sql
hive> select positive(-10) from iteblog;
-10
hive> select positive(12) from iteblog;
12
```

### 25、negative函数: negative
语法: negative(int a), negative(double a)
返回值: int double
说明: 返回-a

```sql
hive> select negative(-5) from iteblog;
5
hive> select negative(8) from iteblog;
-8
```

## 五、字符串函数
### 1、字符串长度函数：length
语法: length(string A)
返回值: int
说明：返回字符串A的长度

```sql
hive> select length('abcedfg') from iteblog;
7
```

### 2、字符串反转函数：reverse
语法: reverse(string A)
返回值: string
说明：返回字符串A的反转结果

```sql
hive> select reverse(abcedfg’) from iteblog;
gfdecba
```

### 3、字符串连接函数：concat
语法: concat(string A, string B…)
返回值: string
说明：返回输入字符串连接后的结果，支持任意个输入字符串。任意参数为null，返回null。

```sql
hive> select concat(‘abc’,'def’,'gh’) from iteblog;
abcdefgh
```

**任意参数为null，返回null**
```sql
hive> SELECT concat('abc', 'def');
abcdef

hive> SELECT concat('abc', null);
NULL
```

### 4、带分隔符字符串连接函数：concat_ws
语法: concat_ws(string SEP, string A, string B…)
返回值: string
说明：返回输入字符串连接后的结果，SEP表示各个字符串间的分隔符。
```sql
hive> select concat_ws(',','abc','def','gh') from iteblog;
abc,def,gh
```

**其实，concat_ws函数可以连接任意多个string和array(string)**
语法: concat_ws(separator, [string | array(string)]+)
返回值: string
说明：返回输入字符串连接后的结果，SEP表示各个字符串间的分隔符。

```sql
hive> SELECT concat_ws('.', 'www', array('facebook', 'com')) FROM src LIMIT 1;
'www.facebook.com'

hive> SELECT concat_ws('.', 'www', array('facebook', 'com'), 'cn');
OK
www.facebook.com.cn
```

**这个函数会跳过分隔符参数后的string类型的NULL，array(string)中的null并不会跳过，空字符串也不会跳过。**

```sql
hive> select concat_ws(',','abc','',null,"def");
abc,,def

hive> select concat_ws(',','abc',' ',null,"def");
abc, ,def

hive> select concat_ws(',','www', array('facebook',null ,'' ,'com'));
www,facebook,null,,com
```

### 5、字符串截取函数：substr,substring
语法: substr(string A, int start),substring(string A, int start)
返回值: string
说明：返回字符串A从start位置到结尾的字符串

```sql
hive> select substr('abcde',3) from iteblog;
cde
hive> select substring('abcde',3) from iteblog;
cde
hive>  select substr('abcde',-1) from iteblog;  #（和ORACLE相同）
e
```

### 6、字符串截取函数：substr,substring
语法: substr(string A, int start, int len),substring(string A, int start, int len)
返回值: string
说明：返回字符串A从start位置开始，长度为len的字符串

```sql
hive> select substr('abcde',3,2) from iteblog;
cd
hive> select substring('abcde',3,2) from iteblog;
cd
hive>select substring('abcde',-2,2) from iteblog;
de
```

### 7、字符串转大写函数：upper,ucase
语法: upper(string A) ucase(string A)
返回值: string
说明：返回字符串A的大写格式

```sql
hive> select upper('abSEd') from iteblog;
ABSED
hive> select ucase('abSEd') from iteblog;
ABSED
```

### 8、字符串转小写函数：lower,lcase
语法: lower(string A) lcase(string A)
返回值: string
说明：返回字符串A的小写格式

```sql
hive> select lower('abSEd') from iteblog;
absed
hive> select lcase('abSEd') from iteblog;
absed
```

### 9、去空格函数：trim
语法: trim(string A)
返回值: string
说明：去除字符串两边的空格

```sql
hive> select trim(' abc ') from iteblog;
abc
```

### 10、左边去空格函数：ltrim
语法: ltrim(string A)
返回值: string
说明：去除字符串左边的空格

```sql
hive> select ltrim(' abc ') from iteblog;
abc 
```

### 11、右边去空格函数：rtrim
语法: rtrim(string A)
返回值: string
说明：去除字符串右边的空格

```sql
hive> select rtrim(' abc ') from iteblog;
 abc
```

### 12、正则表达式替换函数：regexp_replace
语法: regexp_replace(string initial_string, string pattern, string replacement)
返回值: string
说明：将字符串initial_string中的符合java正则表达式pattern的部分替换为replacement。注意，在有些情况下要使用转义字符,类似oracle中的regexp_replace函数。

```sql
hive> SELECT regexp_replace('100-200', '\d+', 'num');
100-200
```

### 13、正则表达式解析函数：regexp_extract
语法: regexp_extract(string subject, string pattern, int index)
返回值: string
说明：将字符串subject按照pattern正则表达式的规则拆分，返回index指定的字符。

```sql
hive> select regexp_extract('foothebar', 'foo(.*?)(bar)', 1) from iteblog;
the
hive> select regexp_extract('foothebar', 'foo(.*?)(bar)', 2) from iteblog;
bar
hive> select regexp_extract('foothebar', 'foo(.*?)(bar)', 0) from iteblog;
foothebar
```

### 14、URL解析函数：parse_url
语法: parse_url(string urlString, string partToExtract [, string keyToExtract])
返回值: string
说明：返回从URL中抽取指定部分的内容，参数url是URL字符串，而参数partToExtract是要抽取的部分，这个参数包含(HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, and USERINFO,例如：parse_url('http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1', 'HOST') ='facebook.com'，如果参数partToExtract值为QUERY则可以指定第三个参数key  如：parse_url('http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1', 'QUERY', 'k1') =‘v1’

```sql
hive> SELECT parse_url('http://facebook.com/path/p1.php?query=1', 'HOST') FROM src LIMIT 1;
'facebook.com'
hive> SELECT parse_url('http://facebook.com/path/p1.php?query=1', 'QUERY') FROM src LIMIT 1;
'query=1'
hive>  SELECT parse_url('http://facebook.com/path/p1.php?query=1', 'QUERY', 'query') FROM src LIMIT 1;
'1'
```

### 15、URL解析函数：parse_url_tuple
语法: parse_url_tuple(url, partname1, partname2, ..., partnameN)
返回值: tuple
说明：返回从URL中抽取指定N部分的内容，参数url是URL字符串，而参数p1,p2,....是要抽取的部分，这个参数包含HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, USERINFO, QUERY:<KEY>。

```sql
parse_url_tuple(url, partname1, partname2, ..., partnameN) - extracts N (N>=1) parts from a URL.
It takes a URL and one or multiple partnames, and returns a tuple. All the input parameters and output column types are string.
Partname: HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, USERINFO, QUERY:<KEY_NAME>
Note: Partnames are case-sensitive, and should not contain unnecessary white spaces.
Example:
  > SELECT b.* FROM src LATERAL VIEW parse_url_tuple(fullurl, 'HOST', 'PATH', 'QUERY', 'QUERY:id') b as host, path, query, query_id LIMIT 1;
  > SELECT parse_url_tuple(a.fullurl, 'HOST', 'PATH', 'QUERY', 'REF', 'PROTOCOL', 'FILE',  'AUTHORITY', 'USERINFO', 'QUERY:k1') as (ho, pa, qu, re, pr, fi, au, us, qk1) from src a;sql
```

### 16、json解析函数：get_json_object
语法: get_json_object(string json_string, string path)
返回值: string
说明：解析json的字符串json_string,返回path指定的内容。如果输入的json字符串无效，那么返回NULL。get_json_object函数第一个参数填写json对象变量，第二个参数使用$表示json变量标识，然后用 . 或 [] 读取对象或数组；

```sql
hive> select  get_json_object('{"aaBc":1}','$.aaBc');
1

hive> select  get_json_object('[{"aaBc":1}]','$');
NULL

hive> select  get_json_object('[{"aaBc":1}]','$[0]');
{"aaBc":1}

hive> select  get_json_object('[{"aaBc":1}]','$.[0]');
{"aaBc":1}

hive> select  get_json_object('[{"aaBc":1}]','$[0].aaBc');
1
```

### 17、json解析函数：json_tuple
语法: json_tuple(jsonStr, k1, k2, ...)
返回值: tuple
说明: 从一个JSON字符串中获取多个键并作为一个元组返回，与get_json_object不同的是此函数能一次获取多个键值

当使用json_tuple对象时，可以显著提高效率，一次获取多个对象并且可以被组合使用，写法如下：
其中，需要使用lateral view 视图方法来写，不需要加$标示符读取对象

```sql
select a.timestamp,
 b.* 
from log a 
lateral view json_tuple(a.appevent, 'eventid', 'eventname') b as f1, f2;

-- 其中 b.* 代表的就是 f1,f2，也就是 appevent.eventid 、appevent.eventname
```

get_json_object与json_tuple在解析埋点数据时会经常用到，而且比较有效且很简单


### 18、空格字符串函数：space
语法: space(int n)
返回值: string
说明：返回长度为n的字符串

```sql
hive> select space(10) from iteblog;

hive> select length(space(10)) from iteblog;
10
```

### 19、重复字符串函数：repeat
语法: repeat(string str, int n)
返回值: string
说明：返回重复n次后的str字符串

```sql
hive> select repeat('abc',5) from iteblog;
abcabcabcabcabc
```

### 20、首字符ascii函数：ascii
语法: ascii(string str)
返回值: int
说明：返回字符串str第一个字符的ascii码

```sql
hive> select ascii('abcde') from iteblog;
97
```

### 21、左补足函数：lpad
语法: lpad(string str, int len, string pad)
返回值: string
说明：将str进行用pad进行左补足到len位

```sql
hive> select lpad('abc',10,'td') from iteblog;
tdtdtdtabc
注意：与GP，ORACLE不同，pad 不能默认
```

### 22、右补足函数：rpad
语法: rpad(string str, int len, string pad)
返回值: string
说明：将str进行用pad进行右补足到len位

```sql
hive> select rpad('abc',10,'td') from iteblog;
abctdtdtdt
```

### 23、分割字符串函数: split
语法: split(string str, string pat)
返回值: array
说明: 按照pat字符串分割str，会返回分割后的字符串数组

```sql
hive> select split('abtcdtef','t') from iteblog;
["ab","cd","ef"]
```

### 24、集合查找函数: find_in_set
语法: find_in_set(string str, string strList)
返回值: int
说明: 返回str在strlist第一次出现的位置，strlist是用逗号分割的字符串。如果没有找该str字符，则返回0。

```sql
hive> select find_in_set('ab','ef,ab,de') from iteblog;
2
hive> select find_in_set('at','ef,ab,de') from iteblog;
0
```

```sql
find_in_set(str,str_array) - Returns the first occurrence  of str in str_array where str_array is a comma-delimited string. Returns null if either argument is null. Returns 0 if the first argument has any commas.
Example:
  > SELECT find_in_set('ab','abc,b,ab,c,def') FROM src LIMIT 1;
  3
  > SELECT * FROM src1 WHERE NOT find_in_set(key,'311,128,345,956')=0;
  311  val_311
  128
```

### 25、数字格式化函数: format_number
语法: format_number(number x, int d)
返回值: string
说明: 将数值X转换成"#,###,###.##"格式字符串，并保留d位小数，如果d为0，将进行四舍五入且不保留小数。

```sql
format_number(X, D) - Formats the number X to a format like '#,###,###.##', rounded to D decimal places, and returns the result as a string. If D is 0, the result has no decimal point or fractional part. This is supposed to function like MySQL's FORMAT
Example:
  > SELECT format_number(12332.123456, 4) FROM src LIMIT 1;
  '12,332.1235'
```

### 26、单词首字母大写形式函数: initcap
语法: initcap(string A)
返回值: string
说明: 将字符串A每个单词转换第一个字母大写其余字母小写的字符串，以空格区分每个单词。

```sql
initcap(str) - Returns str, with the first letter of each word in uppercase, all other letters in lowercase. Words are delimited by white space.
Example:
 > SELECT initcap('tHe soap') FROM src LIMIT 1;
 'The Soap'
```

## 六、日期函数
### 1、UNIX时间戳转日期函数: from_unixtime
语法: from_unixtime(bigint unixtime[, string format])
返回值: string
说明: 转化UNIX时间戳（从1970-01-01 00:00:00 UTC到指定时间的秒数）到当前时区的时间格式。

将时间的秒值转换成format格式（format可为“yyyy-MM-dd hh:mm:ss”,“yyyy-MM-dd hh”,“yyyy-MM-dd hh:mm”等等）如from_unixtime(1250111000,"yyyy-MM-dd") 得到2009-03-12

```sql
hive> select from_unixtime(1564969729,'yyyy-MM-dd');
2019-08-05
```

```sql
from_unixtime(unix_time, format) - returns unix_time in the specified format
Example:
  > SELECT from_unixtime(0, 'yyyy-MM-dd HH:mm:ss') FROM src LIMIT 1;
  '1970-01-01 00:00:00'
```

### 2、获取当前UNIX时间戳函数: unix_timestamp
语法: unix_timestamp()
返回值: bigint
说明: 获得当前时区的UNIX时间戳

```sql
hive> select unix_timestamp();
1564969933
```

```sql
unix_timestamp([date[, pattern]]) - Returns the UNIX timestamp
Converts the current or specified time to number of seconds since 1970-01-01.
```

### 3、日期转UNIX时间戳函数: unix_timestamp
语法: unix_timestamp(string date)
返回值: bigint
说明: 转换格式为"yyyy-MM-dd HH:mm:ss"的日期到UNIX时间戳。如果转化失败，则返回0。

将格式为yyyy-MM-dd HH:mm:ss的时间字符串转换成时间戳  如unix_timestamp('2009-03-20 11:30:01') = 1237573801。

```sql
hive> select unix_timestamp('2011-12-07 13:01:03');
1323234063
```

### 4、指定格式日期转UNIX时间戳函数: unix_timestamp
语法: unix_timestamp(string date, string pattern)
返回值: bigint
说明: 转换pattern格式的日期到UNIX时间戳。如果转化失败，则返回0。

将指定时间字符串格式字符串转换成Unix时间戳，如果格式不对返回0 如：unix_timestamp('2009-03-20', 'yyyy-MM-dd') = 1237532400。

```sql
hive> select unix_timestamp('20111207 13:01:03','yyyyMMdd HH:mm:ss');
1323234063
```

### 5、日期转日期函数: to_date
语法: to_date(string timestamp)
返回值: string
说明: 返回日期时间字符串的日期部分。

```sql
hive> select to_date('2011-12-08 10:03:01');
2011-12-08
```

### 6、日期转年函数: year
语法: year(string date)
返回值: int
说明: 返回日期中的年。

```sql
hive> select year('2011-12-08 10:03:01');
2011
hive> select year('2012-12-08');
2012
```

### 7、日期转月函数: month
语法: month (string date)
返回值: int
说明: 返回日期中的月份。

```sql
hive> select month('2011-12-08 10:03:01');
12
hive> select month('2011-08-08');
8
```

### 8、日期转天函数: day
语法: day (string date)
返回值: int
说明: 返回日期中的天。

```sql
hive> select day('2011-12-08 10:03:01');
8
hive> select day('2011-12-24');
24
```

### 9、日期转小时函数: hour
语法: hour (string date)
返回值: int
说明: 返回日期中的小时。

```sql
hive> select hour('2011-12-08 10:03:01');
10
```

### 10、日期转分钟函数: minute
语法: minute (string date)
返回值: int
说明: 返回日期中的分钟。

```sql
hive> select minute('2011-12-08 10:03:01');
3
```

### 11、日期转秒函数: second
语法: second (string date)
返回值: int
说明: 返回日期中的秒。

```sql
hive> select second('2011-12-08 10:03:01');
1
```

### 12、日期转周函数: weekofyear
语法: weekofyear (string date)
返回值: int
说明: 返回日期在当前的周数。

返回时间字符串位于一年中的第几个周内  如weekofyear("1970-11-01 00:00:00") = 44, weekofyear("1970-11-01") = 44。

```sql
hive> select weekofyear('2011-12-08 10:03:01');
49
hive> select weekofyear('2019-01-01');
1
```

### 13、日期转季度函数: quarter
语法: quarter(date/timestamp/string)
返回值: int
说明: 返回日期在当前的季度数。

Returns the quarter of the year for a date, timestamp, or string in the range 1 to 4 (as of Hive 1.3.0). Example: quarter('2015-04-08') = 2.
返回当前时间属性哪个季度 如quarter('2015-04-08') = 2。

### 14、日期比较函数: datediff
语法: datediff(string enddate, string startdate)
返回值: int
说明: 返回结束日期减去开始日期的天数。

```sql
hive> select datediff('2009-03-01', '2009-02-27');
2
hive> select datediff('2009-03-01', '2009-03-03');
-2
```

### 15、日期增加函数: date_add
语法: date_add(string startdate, int days)
返回值: string
说明: 返回开始日期startdate增加days天后的日期。

```sql
hive> select date_add('2019-08-08', 7);
2019-08-15
hive> select date_add('2019-08-08', -7);
2019-08-01
hive> select date_add('2019-08-08 10:03:01', 7);
2019-08-15
```

```sql
date_add(start_date, num_days) - Returns the date that is num_days after start_date.
start_date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. num_days is a number. The time part of start_date is ignored.
Example:
   > SELECT date_add('2009-07-30', 1) FROM src LIMIT 1;
  '2009-07-31'
```

### 16、日期减少函数: date_sub
语法: date_sub (string startdate, int days)
返回值: string
说明: 返回开始日期startdate减少days天后的日期。

```sql
hive> select date_sub('2019-08-08', 7);
2019-08-01

hive> select date_sub('2019-08-08', -7);
2019-08-15

hive> select date_sub('2019-08-08 10:03:01', 7);
2019-08-01
```

```sql
date_sub(start_date, num_days) - Returns the date that is num_days before start_date.
start_date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. num_days is a number. The time part of start_date is ignored.
Example:
   > SELECT date_sub('2009-07-30', 1) FROM src LIMIT 1;
  '2009-07-29'
```

### 17、日期增加月份函数: add_months
语法: add_months(string start_date, int num_months)
返回值: string
说明: 返回开始日期startdate再增加num_months个月的日期。

Returns the date that is num_months after start_date (as of Hive 1.1.0). 

```sql
hive> select add_months('2019-08-08', 1);
2019-09-08

hive> select add_months('2019-08-08', -1);
2019-07-08

hive> select add_months('2019-08-08 10:03:01', 1);
2019-09-08

hive> select add_months('2019-08-08', 12);
2020-08-08
```

```sql
add_months(start_date, num_months) - Returns the date that is num_months after start_date.
start_date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. num_months is a number. The time part of start_date is ignored.
Example:
  > SELECT add_months('2009-08-31', 1) FROM src LIMIT 1;
 '2009-09-30'
```


### 18、日期当月最后一天函数: last_day
语法: last_day(string date)
返回值: string
说明: 返回日期这个月的最后一天的日期，忽略时分秒部分（HH:mm:ss）。

Returns the last day of the month which the date belongs to (as of Hive 1.1.0)

```sql
hive> select last_day('2019-02-01');
2019-02-28

hive> select last_day('2020-02-01');
2020-02-29
```

```sql
last_day(date) - Returns the last day of the month which the date belongs to.
date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. The time part of date is ignored.
Example:
  > SELECT last_day('2009-01-12') FROM src LIMIT 1;
 '2009-01-31'
```


### 19、下一个最近的星期X函数: next_day
语法: next_day(string start_date, string day_of_week)
返回值: string
说明: 返回开始日期startdate的下一个星期X所对应的日期。
说明：星期一到星期日的英文（Monday，Tuesday、Wednesday、Thursday、Friday、Saturday、Sunday）

Returns the first date which is later than start_date and named as day_of_week (as of Hive1.2.0). start_date is a string/date/timestamp. day_of_week is 2 letters, 3 letters or full name of the day of the week (e.g. Mo, tue, FRIDAY). The time part of start_date is ignored. Example: next_day('2015-01-14', 'TU') = 2015-01-20.

返回当前时间的下一个星期X所对应的日期(**可能是本周或下周的某一天**) 如：next_day('2015-01-14', 'TU') = 2015-01-20  以2015-01-14为开始时间，其下一个星期二所对应的日期为2015-01-20

```sql
#2019-08-05为周一

#取下一个周一（肯定是下一个周的周一，因为周一为第一天）
hive> select next_day('2019-08-05','MO');
2019-08-12

#取当前周的周一
hive> select date_add(next_day('2019-08-05','MO'),-7);
2019-08-05

#取当前周的周日（错误的，下一个周日可能是本周的）
hive> select date_add(next_day('2019-08-05','SU'),-7);
2019-08-04

#取当前周的周日（正确的，利用周一来计算）
hive> select date_add(next_day('2019-08-05','MO'),-1);
2019-08-11

#取当前周的周日（正确的，利用周一来计算，即使当天是周日也是可以的）
select date_add(next_day('2019-08-11','MO'),-1);
2019-08-11
```

```sql
next_day(start_date, day_of_week) - Returns the first date which is later than start_date and named as indicated.
start_date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. day_of_week is day of the week (e.g. Mo, tue, FRIDAY).Example:
  > SELECT next_day('2015-01-14', 'TU') FROM src LIMIT 1;
 '2015-01-20'
```

### 20、返回当前日期函数: current_date
语法: current_date()
返回值: string
说明: 返回当前时间日期。

Returns the current date at the start of query evaluation (as of Hive 1.2.0). All calls of current_date within the same query return the same value.

返回当前时间日期

```sql
hive> select current_date();
2019-08-05

hive> select concat(current_date()," 11:23");
2019-08-05 11:23
```

### 21、日期格式化函数: date_format
语法: date_format(date/timestamp/string ts, string fmt)
返回值: string
说明: 日期格式化。

Converts a date/timestamp/string to a value of string in the format specified by the date format fmt (as of Hive 1.2.0). 

按指定格式返回时间date 如：date_format("2016-06-22","MM-dd")=06-22

```sql
hive> SELECT date_format('2015-04-08', 'yyyy');
2015

hive> SELECT date_format('2015-04-08 11:12:12', 'yyyy');
2015

hive> SELECT date_format('2015-04-08 11:12:12', 'yyyy-MM');
2015-04

hive> SELECT date_format('2015-04-08 11:12:12', 'yyyy-MM');
2015-04

hive> SELECT date_format('2015-04-08 11:12:12', 'yyyy-MM-dd HH:mm:ss');
2015-04-08 11:12:12

hive> SELECT date_format('2015-04-08', 'yyyy-MM-dd HH:mm:ss');
2015-04-08 00:00:00

```

##### yyyymmdd和yyyy-mm-dd相互转换
yyyy-mm-dd转yyyymmdd可以使用date_format，yyyymmdd转yyyy-mm-dd没有直接的parse函数，可以自定义或者借助时间戳相关函数。

```sql
--20180905转成2018-09-05
select from_unixtime(unix_timestamp('20180905','yyyymmdd'),'yyyy-mm-dd')
from dw.ceshi_data
--结果如下：
2018-09-05
 
--2018-09-05转成20180905
select from_unixtime(unix_timestamp('2018-09-05','yyyy-mm-dd'),'yyyymmdd')
from dw.ceshi_data
--结果如下：
20180905
```

### 22、日期月份差函数: months_between
语法: months_between(date1, date2)
返回值: double
说明: 返回date1与date2之间相差的月份，如date1>date2，则返回正，`如果date1<date2,则返回负，否则返回0.0  如：months_between('1997-02-28 10:30:00', '1996-10-30') = 3.94959677  1997-02-28 10:30:00与1996-10-30相差3.94959677个月`。

Returns number of months between dates date1 and date2 (as of Hive 1.2.0).

```sql
months_between(date1, date2) - returns number of months between dates date1 and date2
If date1 is later than date2, then the result is positive. If date1 is earlier than date2, then the result is negative. If date1 and date2 are either the same days of the month or both last days of months, then the result is always an integer. Otherwise the UDF calculates the fractional portion of the result based on a 31-day month and considers the difference in time components date1 and date2.
date1 and date2 type can be date, timestamp or string in the format 'yyyy-MM-dd' or 'yyyy-MM-dd HH:mm:ss'. The result is rounded to 8 decimal places.
 Example:
  > SELECT months_between('1997-02-28 10:30:00', '1996-10-30');
 3.94959677
```

### 23、返回当前日期最开始年份或月份函数: trunc
语法: trunc(string date, string format)
返回值: string
说明: 返回时间的最开始年份或月份。

Returns date truncated to the unit specified by the format (as of Hive 1.2.0). Supported formats: MONTH/MON/MM, YEAR/YYYY/YY. Example: trunc('2015-03-17', 'MM') = 2015-03-01.

返回时间的最开始年份或月份  如trunc("2016-06-26",“MM”)=2016-06-01  trunc("2016-06-26",“YY”)=2016-01-01   注意所支持的格式为MONTH/MON/MM, YEAR/YYYY/YY

```sql
trunc(date, fmt) - Returns returns date with the time portion of the day truncated to the unit specified by the format model fmt. If you omit fmt, then date is truncated to the nearest day. It now only supports 'MONTH'/'MON'/'MM' and 'YEAR'/'YYYY'/'YY' as format.
date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. The time part of date is ignored.
Example:
  > SELECT trunc('2009-02-12', 'MM');
OK
 '2009-02-01'
 > SELECT trunc('2015-10-27', 'YEAR');
OK
 '2015-01-01'
```

## 七、条件函数
### 1、If函数: if
语法: if(boolean testCondition, T valueTrue, T valueFalseOrNull)
返回值: T
说明: 当条件testCondition为TRUE时，返回valueTrue；否则返回valueFalseOrNull

Returns valueTrue when testCondition is true, returns valueFalseOrNull otherwise.

如果testCondition 为true就返回valueTrue,否则返回valueFalseOrNull ，（valueTrue，valueFalseOrNull为泛型） 

```sql
hive> select if(1=2,100,200);
200
hive> select if(1=1,100,200);
100
```

### 2、nvl函数: nvl
语法: nvl(T value, T default_value)
返回值: T
说明: 如果value值为NULL就返回default_value,否则返回value

Returns default_value if value is null else returns value (as of HIve 0.11).

```sql
hive> SELECT nvl(null,'bla');
bla

hive> SELECT nvl(1,'bla');
1

hive> SELECT nvl(0,'bla');
0

hive> SELECT nvl('aa','bla');
aa
```

### 3、非空查找函数: coalesce
语法: COALESCE(T v1, T v2, …)
返回值: T
说明: 返回参数中的第一个非空值；如果所有值都为NULL，那么返回NUL3

```sql
hive> select COALESCE(null,'100','50′);
100
```

```sql
coalesce(a1, a2, ...) - Returns the first non-null argument
Example:
  > SELECT coalesce(NULL, 1, NULL) FROM src LIMIT 1;
  1
```

### 4、条件判断函数：CASE
语法: CASE a WHEN b THEN c [WHEN d THEN e]* [ELSE f] END
返回值: T
说明：如果a等于b，那么返回c；如果a等于d，那么返回e；否则返回f

```sql
hive> Select case 100 when 50 then 'tom' when 100 then 'mary' else 'tim' end;
mary
hive> Select case 200 when 50 then 'tom' when 100 then 'mary' else 'tim' end;
tim
```

```sql
CASE a WHEN b THEN c [WHEN d THEN e]* [ELSE f] END - When a = b, returns c; when a = d, return e; else return f
Example:
 SELECT
 CASE deptno
   WHEN 1 THEN Engineering
   WHEN 2 THEN Finance
   ELSE admin
 END,
 CASE zone
   WHEN 7 THEN Americas
   ELSE Asia-Pac
 END
 FROM emp_details
```

### 5、条件判断函数：CASE WHEN
语法: CASE WHEN a THEN b [WHEN c THEN d]* [ELSE e] END
返回值: T
说明：如果a为TRUE,则返回b；如果c为TRUE，则返回d；否则返回e

```sql
hive> select case when 1=2 then 'tom' when 2=2 then 'mary' else 'tim' end;
mary
hive> select case when 1=1 then 'tom' when 2=2 then 'mary' else 'tim' end;
tom
```

### 6、null值判断函数: isnull
语法: isnull( a )
返回值: boolean
说明: 判断是否为null

Returns true if a is NULL and false otherwise.
如果a为null就返回true，否则返回false

```sql
hive> select isnull(0);
false

hive> select isnull('');
false
```

### 7、非null值判断函数: isnotnull
语法: isnotnull( a )
返回值: boolean
说明: 判断是否为非null

Returns true if a is not NULL and false otherwise.
如果a为非null就返回true，否则返回false

## 七、聚合函数（UDAF） 
### 1、个数统计函数: count
语法: count(*), count(expr), count(DISTINCT expr[, expr_.])
返回值: bigint
说明: count(*)统计检索出的行的个数，包括NULL值的行；count(expr)返回指定字段的非空值的个数；count(DISTINCT expr[, expr_.])返回指定字段的不同的非空值的个数

```sql
hive> select count(*) from iteblog;
20
hive> select count(distinct t) from iteblog;
10
```

```
count(*) - Returns the total number of retrieved rows, including rows containing NULL values.

统计总行数，包括含有NULL值的行

count(expr) - Returns the number of rows for which the supplied expression is non-NULL.

统计提供非NULL的expr表达式值的行数

count(DISTINCT expr[, expr]) - Returns the number of rows for which the supplied expression(s) are unique and non-NULL. Execution of this can be optimized with hive.optimize.distinct.rewrite.

统计提供非NULL且去重后的expr表达式值的行数
```

### 2、总和统计函数: sum
语法: sum(col), sum(DISTINCT col)
返回值: double
说明: sum(col)统计结果集中col的相加的结果；sum(DISTINCT col)统计结果中col不同值相加的结果

Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.

sum(col),表示求指定列的和，sum(DISTINCT col)表示求去重后的列的和

```sql
hive> select sum(t) from iteblog;
100
hive> select sum(distinct t) from iteblog;
70
```

### 3、平均值统计函数: avg
语法: avg(col), avg(DISTINCT col)
返回值: double
说明: avg(col)统计结果集中col的平均值；avg(DISTINCT col)统计结果中col不同值相加的平均值

Returns the average of the elements in the group or the average of the distinct values of the column in the group.

avg(col),表示求指定列的平均值，avg(DISTINCT col)表示求去重后的列的平均值

```sql
hive> select avg(t) from iteblog;
50
hive> select avg (distinct t) from iteblog;
30
```

### 4、最小值统计函数: min
语法: min(col)
返回值: double
说明: 统计结果集中col字段的最小值

Returns the minimum of the column in the group.

求指定列的最小值

```sql
hive> select min(t) from iteblog;
20
```

### 5、最大值统计函数: max
语法: max(col)
返回值: double
说明: 统计结果集中col字段的最大值

Returns the maximum value of the column in the group.

求指定列的最大值

```sql
hive> select max(t) from iteblog;
120
```

### 6、集合不去重函数: collect_list
语法: collect_list(col)
返回值: array
说明: collect_list(x) - Returns a list of objects with duplicates


### 7、集合去重函数: collect_set
语法: collect_set(col)
返回值: array
说明: collect_set(x) - Returns a set of objects with duplicate elements eliminated

## 八、表生成函数Table-Generating Functions (UDTF)  
### 1、数组拆分成多行函数: explode
语法: explode(ARRAY<T> a)
返回值: T
说明: 每行对应数组中的一个元素

Returns one row for each element from the array..

每行对应数组中的一个元素

```sql
select explode(array('A','B','C'));
select explode(array('A','B','C')) as col;
select tf.* from (select 0) t lateral view explode(array('A','B','C')) tf;
select tf.* from (select 0) t lateral view explode(array('A','B','C')) tf as col;

A
B
C
```


### 2、MAP拆分成多行函数: explode
语法: explode(MAP<Tkey,Tvalue> m)
返回值: Tkey,Tvalue
说明: 每行对应每个map键-值，其中一个字段是map的键，另一个字段是map的值

Returns one row for each key-value pair from the input map with two columns in each row: one for the key and another for the value. (As of Hive 0.8.0.).

每行对应每个map键-值，其中一个字段是map的键，另一个字段是map的值

```sql
select explode(map('A',10,'B',20,'C',30));
select explode(map('A',10,'B',20,'C',30)) as (key,value);
select tf.* from (select 0) t lateral view explode(map('A',10,'B',20,'C',30)) tf;
select tf.* from (select 0) t lateral view explode(map('A',10,'B',20,'C',30)) tf as key,value;

A   10
B   20
C   30
```

### 3、数组拆分成多行带索引函数: posexplode
语法: posexplode(ARRAY<T> a)
返回值: int,T
说明: 与explode类似，不同的是还返回各元素在数组中的位置，从0开始。

```sql
select posexplode(array('A','B','C'));
select posexplode(array('A','B','C')) as (pos,val);
select tf.* from (select 0) t lateral view posexplode(array('A','B','C')) tf;
select tf.* from (select 0) t lateral view posexplode(array('A','B','C')) tf as pos,val;

0   A
1   B
2   C
```

### 4、URL解析函数：parse_url_tuple
语法: parse_url_tuple(url, partname1, partname2, ..., partnameN)
返回值: tuple
说明：返回从URL中抽取指定N部分的内容，参数url是URL字符串，而参数p1,p2,....是要抽取的部分，这个参数包含HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, USERINFO, QUERY:<KEY>。

```sql
parse_url_tuple(url, partname1, partname2, ..., partnameN) - extracts N (N>=1) parts from a URL.
It takes a URL and one or multiple partnames, and returns a tuple. All the input parameters and output column types are string.
Partname: HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, USERINFO, QUERY:<KEY_NAME>
Note: Partnames are case-sensitive, and should not contain unnecessary white spaces.
Example:
  > SELECT b.* FROM src LATERAL VIEW parse_url_tuple(fullurl, 'HOST', 'PATH', 'QUERY', 'QUERY:id') b as host, path, query, query_id LIMIT 1;
  > SELECT parse_url_tuple(a.fullurl, 'HOST', 'PATH', 'QUERY', 'REF', 'PROTOCOL', 'FILE',  'AUTHORITY', 'USERINFO', 'QUERY:k1') as (ho, pa, qu, re, pr, fi, au, us, qk1) from src a;sql
```

### 5、json解析函数：json_tuple
语法: json_tuple(jsonStr, k1, k2, ...)
返回值: tuple
说明: 从一个JSON字符串中获取多个键并作为一个元组返回，与get_json_object不同的是此函数能一次获取多个键值

当使用json_tuple对象时，可以显著提高效率，一次获取多个对象并且可以被组合使用，写法如下：
其中，需要使用lateral view 视图方法来写，不需要加$标示符读取对象

```sql
select a.timestamp,
 b.* 
from log a 
lateral view json_tuple(a.appevent, 'eventid', 'eventname') b as f1, f2;

-- 其中 b.* 代表的就是 f1,f2，也就是 appevent.eventid 、appevent.eventname
```

get_json_object与json_tuple在解析埋点数据时会经常用到，而且比较有效且很简单

## 九、类型转换函数
### 1、基础类型之间强制转换：cast
语法: cast(expr as <type>)
返回值: Expected "=" to follow "type"
说明: 返回转换后的数据类型

Converts the results of the expression expr to <type>. For example, cast('1' as BIGINT) will convert the string '1' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string.

将expr转换成type类型 如：cast("1" as BIGINT) 将字符串1转换成了BIGINT类型，如果转换失败将返回NULL

## 十、集合操作函数
### 1、array类型大小：size
语法: size(Array<T>)
返回值: int
说明: 返回数组的长度

### 2、map类型大小：size
语法: size(Map<K.V>)
返回值: int
说明: 返回map的长度

### 3、判断元素数组是否包含元素：array_contains
语法: array_contains(Array<T>, value)
返回值: boolean
说明: 如该数组Array<T>包含value返回true。，否则返回false

### 4、获取map中所有key集合：map_keys
语法: map_keys(Map<K.V>)
返回值: array<K>
说明: 返回转换后的数据类型

### 5、获取map中所有value集合：map_values
语法: map_values(Map<K.V>)
返回值: array<V>
说明: 返回转换后的数据类型

### 6、数组排序：sort_array
语法: sort_array(Array<T>)
返回值: Array<T>
说明: 返回转换后的数据类型

## 十一、集合访问
### 1、array类型访问: A[n]
语法: A[n]
操作类型: A为array类型，n为int类型
说明：返回数组A中的第n个变量值。数组的起始下标为0。比如，A是个值为['foo', 'bar']的数组类型，那么A[0]将返回'foo',而A[1]将返回'bar'

```sql
hive> create table iteblog as select array("tom","mary","tim") as t from iteblog;
hive> select t[0],t[1],t[2] from iteblog;
tom     mary    tim
```

### 2、map类型访问: M[key]
语法: M[key]
操作类型: M为map类型，key为map中的key值
说明：返回map类型M中，key值为指定值的value值。比如，M是值为{'f' -> 'foo', 'b' -> 'bar', 'all' -> 'foobar'}的map类型，那么M['all']将会返回'foobar'

```sql
hive> Create table iteblog as select map('100','tom','200','mary') as t from iteblog;
hive> select t['200'],t['100'] from iteblog;
mary    tom
```

### 3、struct类型访问: S.x
语法: S.x
操作类型: S为struct类型
说明：返回结构体S中的x字段。比如，对于结构体struct foobar {int foo, int bar}，foobar.foo返回结构体中的foo字段

```sql
hive> create table iteblog as select struct('tom','mary','tim') as t from iteblog;
hive> describe iteblog;
t       struct<col1:string ,col2:string,col3:string>
hive> select t.col1,t.col3 from iteblog;
tom     tim
```



https://www.iteblog.com/archives/2258.html

http://lxw1234.com/archives/2015/06/251.htm

https://www.cnblogs.com/MOBIN/p/5618747.html