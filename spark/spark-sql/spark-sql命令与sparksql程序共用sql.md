# spark-sql命令与sparksql程序共用sql
py脚本执行sql语句使用format格式化sql语句，但是使用scala写spark sql程序时无法使用此语法，刚开始使用字符串差值语法，但是在两种形式切换时需要手动替换修改，有些麻烦，于是想要使用隐士转化为str添加format方法，由于scala默认实现了一个，于是方法名叫formatLikePy

## 测试
StringUtils:
```scala
package com.sparknotebook.string

import java.net.URL

import scala.io.Source
import scala.util.matching.Regex

object StringUtils {

  implicit class PyString(str: String){
    val pattern = "\\{(\\w+)\\}".r

    def formatLikePy(keyMap: Map[String, Any]): String ={
      pattern.replaceAllIn(str, m => keyMap.getOrElse(m.group(1), m.group(1)).toString)
    }

  }


  def main(args: Array[String]): Unit = {
    val datePattern = new Regex("""(\d\d\d\d)-(\d\d)-(\d\d)""", "year", "month", "day")
    val text = "From 2011-07-15 to 2011-07-17"
    val repl = datePattern replaceAllIn (text, m => s"${m group "month"}/${m group "day"}")

    println(repl)

    val map: Map[String, Any] = Map("name" -> "小明", "age" -> 30)
    val str = """
    name is {name},
    and age is {age}
    """
    val p = "\\{(\\w+)\\}".r
    val rst: String = p.replaceAllIn(str, m => {
      println(m.matched)
      println(m.group(1))
      map.getOrElse(m.group(1), m.group(1)).toString
    })
    println(rst)
    println("-------------")
    println(str.formatLikePy(map))

    val path: URL = getClass.getClassLoader.getResource("sql/test.sql")
    val fileStr: String = Source.fromURL(path, "utf-8").mkString.formatLikePy(Map("dt" -> "2020-01-01"))
    println(fileStr)
  }

}

```

test.sql:
```sql
insert overwrite table dev_jjsh.dws_paimai_wireless_event_click_di
partition(dt = '{dt}')
select
    browser_uniq_id,
    user_name,
    event_id,
    sum(click_cnt) click_cnt,
    collect_list( named_struct('event_param', event_param, 'click_cnt', click_cnt) ) event_param_click_cnts
from(
    select
        browser_uniq_id,
        user_name,
        event_id,
        event_param,
        count(1) click_cnt
    from(
        select
            browser_uniq_id,
            lower(trim(user_log_acct)) user_name,
            event_id,
            event_param
        from dev_jjsh.dwd_paimai_wireless_click_log_di
        where dt = '{dt}' and event_id is not null and event_id != ''
    ) a
    group by browser_uniq_id, user_name, event_id,event_param
) t
group by browser_uniq_id, user_name, event_id
;
```











