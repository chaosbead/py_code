# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import pymysql



class JobPipeline(object):
    def process_item(self, item, spider):
        return item


'''数据清洗'''
class DataCleanPipeline(object):

    def process_item(self, item, spider):
        print('+-'*100)

        #分割月薪，保存最大薪资，最小薪资
        salary = item['salary']
        if salary != '':
            salary_list = salary[:-3].split('-')
            unit = 0
            if salary[-1] == '月' and salary[-3] == '万':
                unit = 10000
            elif salary[-1] == '月' and salary[-3] == '千':
                unit = 1000
            elif salary[-1] == '年' and salary[-3] == '万':
                unit = 10000/12
            elif salary[-1] == '天' and salary[-3] == '元':
                unit = 1

            if len(salary_list)>1:
                item['min_salary'] = round(float(salary_list[0])*unit,2)
                item['max_salary'] = round(float(salary_list[1])*unit,2)
            else:
                item['min_salary'] = item['max_salary'] = round(float(salary_list[0])*unit,2)

        else:
            item['min_salary'] = item['max_salary'] = 0

        #切割地址，保存城市名
        item['city'] = item['city'].split('-')[0]
        #日期格式转换
        item['publish_date'] = '2018-'+item['publish_date']

        return item

'''数据去重'''
class DuplicatesPipeline(object):
    def __init__(self):
        self.name_seen = set()

    def process_item(self, item, spider):

        if item['post']+item['company'] in self.name_seen:
            # 职位+公司名重复 抛出异常
            raise DropItem('Duplicates item found %s' % item)
        else:
            print('-*'*100)
            self.name_seen.add(item['post']+item['company'])
        return item


'''数据存储'''
class MysqlPipeline(object):
    # 爬虫启动时连接数据库
    def open_spider(self,spider):
        self.conn = pymysql.connect(host='localhost',user='root',password='guava',db='bf_myschool',charset='utf8')

    def save(self, cursor, sql):
        cursor.execute(sql)
        self.conn.commit()

    def get_id(self,cursor,sql,save_sql):
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            self.save(cursor,save_sql)
            return self.get_id(cursor,sql,save_sql)


    def process_item(self, item, spider):
        print('+!' * 100)
        cursor = self.conn.cursor()

        #分表插值
        if item['post'] !='':
            #查询地点id
            city_id = self.get_id(cursor,'select * from t_city where city="%s"' % item['city'],
                                  'insert into t_city values(0,"%s")' % item['city'])

            #查询职位id
            post_id = self.get_id(cursor, 'select * from t_post where post="%s"' % item['post'],
                                  'insert into t_post values(0,"%s")' % item['post'])

            #查询公司id
            company_id = self.get_id(cursor, 'select * from t_company where company="%s"' % item['company'],
                                  'insert into t_company values(0,"%s")' % item['company'])

            #保存主表
            cursor.execute('select * from t_job where href=%s or (post_id=%s and company_id=%s)',(item['href'],post_id,company_id,))
            result = cursor.fetchone()
            if result:
                print('数据重复')
            else:
                cursor.execute('insert into t_job values(0,%s,%s,%s,%s,%s,%s,%s)',(post_id,company_id,city_id,item['min_salary'],
                                item['max_salary'],item['publish_date'],item['href']))
                self.conn.commit()
        cursor.close()
        return item

    # 爬虫结束后，断开数据库连接
    def close_spider(self,spider):
        self.conn.close()