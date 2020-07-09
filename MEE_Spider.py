# 不需要获取一共有几页...当返回结果为空，直接break就行
# url 一直有.. 暂时没办法解决。先不爬取 url吧。
# 循环到 url > 15 之后url格式就有问题了。用自己的格式循环url是不是有些蠢？自动抓取url康起来好一些(but how?)
import csv
import re
import cx_Oracle
import requests


class Scrabber:

    def __init__(self, urlstructure, datere, titlere, urlre, header):
        self.header = header  # the header used to extract the website
        self.urlstructure = urlstructure  # urlstructure example:'http://www.mee.gov.cn/govsearch/simp_gov_list_20180919.jsp?&SType=2&page={}&orderby=date'
        self.datere = datere  # The regular expression to extract the news date
        self.titlere = titlere  # The regular expression to extract the news title
        self.urlre = urlre  # The regular expression to extract the news url
        self.date = []  # initiate the place to storage the data
        self.url = []
        self.title = []

    def fetch(self):
        i = 0
        while True:
            if i == 0:
                url = self.urlstructure.format('')
            elif i > 10: # When it is higher than 10, the url gets problematic
                break
            else:
                url = self.urlstructure.format('_{}'.format(i))
            html = requests.get(url, headers=self.header)
            html.encoding = "utf-8"
            target = html.text
            dates = re.findall(self.datere, target)
            titles = re.findall(self.titlere, target)
            if len(dates) != len(titles):
                print('number of dates and titles does not match in the page: {}'.format(url))  # if not match, break directly
                break
            if len(dates) == 0:  # Stop at the last page
                break
            for j in dates:
                self.date.append(j)
            for k in titles:
                self.title.append(k)
            for l in re.findall(self.urlre, target):
                l = l # I am stuck here...the url is not complete
            i = i + 1

    def savetocsv(self): # works when open the file with text editor. Need more setting when using MS excel
        rows = zip(self.date, self.title) # zip is a python built-in function.
        with open('dateandtitle.csv', 'w', newline='') as f: # newline = '' is to avoid the unintended newline. Always a good practice
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

    def savetooracle(self):
        with cx_Oracle.connect("OT", "Orcl1234",
                               "localhost/pdborcl", encoding="UTF-8") as connection:  # Close the connection automatically. Specify the encoding is necessary
            cursor = connection.cursor()
            for i in range(len(self.date)):
                cursor.execute('''insert into GFS (title, issuedate) values (:title, :issuedate)''', [self.title[i],self.date[i]])
            connection.commit() #necessary when doing DML (Data Manipulation Language)

tryit = Scrabber('http://www.mee.gov.cn/xxgk2018/227/index_6700{}.html', '<span>(.+?)</span>','.html" title=(.+?)>', 'a target="_blank" href="(.+?)"', {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})

tryit.fetch()
tryit.savetooracle()
