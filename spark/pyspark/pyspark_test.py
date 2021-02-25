from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
import json

def save(datas):
    import pymysql

    # 创建连接
    conn = pymysql.connect(host='hadoop101', port=3306, user='root', passwd='123456', db='gmall', charset='utf8')
    # 创建游标, 查询数据默认为元组类型
    cursor = conn.cursor()

    for data in datas:
        cursor.execute("insert ads_user_topic(dt,day_users,day_new_users) values('{dt}',{day_users},{day_new_users})".format(**data.asDict()))

    # 提交，不然无法保存新建或者修改的数据
    conn.commit()
    # 关闭游标
    cursor.close()
    # 关闭连接
    conn.close()

# spark-submit --master yarn --deploy-mode cluster --conf spark.yarn.dist.archives=hdfs:///python/py_367.zip#py_367_env --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=./py_367_env/py_367/bin/python --conf spark.pyspark.driver.python=./py_367_env/py_367/bin/python --conf spark.pyspark.python=./py_367_env/py_367/bin/python pyspark_test.py
if __name__ == '__main__':
    conf = SparkConf().setAppName("UserBehavior")
    sc = SparkContext(conf=conf)
    spark = SparkSession.builder.enableHiveSupport().getOrCreate()

    def func(iter):
        with open("/home/hadoop/pyspark.log", "a",encoding="utf-8") as f:
            for raw in iter:
                f.write(json.dumps({k:str(v) for k,v in raw.asDict().items()}) + "\n")

    spark.sql("use gmall")
    df = spark.sql("select * from ads_user_topic")
    df.cache()

    df.foreachPartition(func)
    df.foreachPartition(save)

    sc.stop()

