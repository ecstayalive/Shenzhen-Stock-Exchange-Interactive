'''
A gift for Qing Qing
'''

import requests
import ast


class Grab:
    '''
    收集某一个公司问答信息
    '''

    def __init__(self, company, startdate, enddate):
        '''

        :param company: 具体公司
        :param startdate: 开始时间，格式为：2019-12-14
        :param enddate: 结束时间，格式为：2019-12-14
        '''
        # 公司代号
        self.company = company
        # 问答信息收集开始时间
        self.startdate = startdate
        # 问答信息收集结束时间
        self.enddate = enddate

        # 一些网站
        self.url_ = "http://irm.cninfo.com.cn/ircs/index/queryKeyboardInfo"  # 获取公司的secid

    def run(self):
        '''
        调用接口，获取公司某一业的信息
        :param pagenum:
        :return:
        '''
        # url_part1 + pagenum + url_part2 即获取公司具体信息的url
        url_part1, url_part2, totalrecord, totalpage = self.access(self.url_)
        # print("totalrecord:", totalrecord)
        # print("totalpage:", totalpage)
        # 通过上一部的url获取公司所有具体信息
        # 常量定义
        Answers = 0  # 回答次数
        QWords = 0  # 提问字数
        AWords = 0  # 回答字数
        question_str = ''
        answers_str = ''
        # 保存文件
        # file = open("./temp_data/" + self.company + ".txt", "w")
        for pagenum in range(1, totalpage + 1):
            contents = self.information(url_part1, url_part2, pagenum)
            # 获取细节信息
            answers, qwords, awords = self.get_details(contents)
            Answers += answers
            QWords += qwords
            AWords += awords
            # 获取文本
            for i in range(len(contents)):
                question_str += contents[i]["mainContent"]
                if "attachedContent" in contents[i]:
                    answers_str += contents[i]["attachedContent"]

            # 保存文件
            # file.write(str(contents))
            # file.write("\n")
        # 打印问题和回答
        print('*' * 10 + "提问的文本" + "*"*10)
        print(question_str)
        print('*' * 10 + "回答的文本" + "*"*10)
        print(answers_str)
        print('*' * 20)
        # file.close()
        print("收集信息完毕")
        print("对于公司" + self.company + "来说，在" + self.startdate + "到" + self.enddate + "之间其总共有", totalrecord, "条提问")
        print("对于公司" + self.company + "来说，在" + self.startdate + "到" + self.enddate + "之间其总共有", Answers, "条回答")
        print("对于公司" + self.company + "来说，在" + self.startdate + "到" + self.enddate + "之间其总共有", QWords, "提问字数")
        print("对于公司" + self.company + "来说，在" + self.startdate + "到" + self.enddate + "之间其总共有", AWords, "回答字数")

    def access(self, url):
        '''
        获取公司的secid和下一步要访问的网站
        :param url: queryKeyboardInfo的网址
        :return:
        '''

        # 一些网站的组成部分
        url_part1 = "http://irm.cninfo.com.cn/ircs/search/searchResult?stockCodes="  # 后面跟conpany_code
        url_part2 = "&keywords=&infoTypes=1%2C11&startDate="  # 后面跟startdate
        url_part3 = "+00%3A00%3A00&endDate="  # 后面跟enddata
        url_part4 = "+23%3A59%3A59&onlyAttentionCompany=2&pageNum="  # 后面跟pagenum
        pagenum = 1
        url_part5 = "&pageSize=10"

        # 提交的访问信息
        payload = {"keyWord": self.company}
        # 返回结果
        html = requests.post(url, data=payload)
        # 获取需要的该公司的字典信息
        cindex = html.text.find("data")
        information = ast.literal_eval(html.text[cindex + 7:-2])
        # 生成company_code
        company_code = information["secid"] + "_" + self.company

        # 先访问一次，获取该公司问答情况，包括条数和总的页数
        next_url = url_part1 + company_code + url_part2 + self.startdate + url_part3 + self.enddate + url_part4 + \
                   str(pagenum) + url_part5
        # 访问
        content = requests.get(next_url).text
        # 获取totalrecord和toalpage
        index1 = content.find("totalRecord")
        index2 = content.find("totalPage")
        index3 = content.find("results")

        totalrecord = int(content[index1 + 13:index2 - 2])
        toalpage = int(content[index2 + 11:index3 - 2])

        # 生成返回信息
        url_part1 = url_part1 + company_code + url_part2 + self.startdate + url_part3 + self.enddate + url_part4
        url_part2 = url_part5

        return url_part1, url_part2, totalrecord, toalpage

    def information(self, url_part1, url_part2, pagenum):
        '''
        获取公司某一页的信息
        :param url_part1:
        :param url_part2:
        :param pagenum:
        :return:
        '''

        self.url = url_part1 + str(pagenum) + url_part2
        # 获取返回信息
        content = requests.get(self.url).text
        #
        index = content.find("results")
        content_list = ast.literal_eval(content[index + 9:-14])
        return content_list

    def get_details(self, contents):
        '''
        获取信息的细节
        :param content: 信息内容
        :return:
        '''

        import re

        # 常量定义
        answers = 0  # 回答次数
        qwords = 0  # 提问字数
        awords = 0  # 回答字数
        for i in range(len(contents)):
            # 将数字多个数字变成一个空格
            temp_content = contents[i]["mainContent"]
            # print(temp_content)
            # 去掉所有的符号
            parttern = re.compile('\%|\d|\.|\-|\s')  # | 表示或者的意思
            temp_content = re.sub(parttern, ' ', temp_content)
            temp_content = re.sub(' +', ' ', temp_content)
            # print(temp_content)
            qwords += len(temp_content)
            if "attachedContent" in contents[i]:
                temp_content = contents[i]["attachedContent"]
                temp_content = re.sub(parttern, ' ', temp_content)
                temp_content = re.sub(' +', ' ', temp_content)
                answers += 1
                awords += len(temp_content)

        return answers, qwords, awords


if __name__ == "__main__":
    print("Write for QingQing.")
    while True:
        print(">" * 20)
        print("Warning: 统计字数逻辑与word不同，是因为数字和符号处理方式不同")
        print("如果你想要获得word中统计的字数，请复制输出的文本到word中获取字数")
        print(">" * 20)
        try:
            company = input("输入公司代码（格式：000001）：")
            startdate = input("输入开始时间（格式 2019-07-01）：")
            enddate = input("输入开始时间（格式 2019-09-30）：")
            grab = Grab(company, startdate, enddate)
            # grab = Grab("002622", "2016-10-01", "2016-12-31")
            grab.run()
            # break
        except Exception:
            print("出现错误,可能是网络问题，请重新输入试试")
            print("<" * 20)
        finally:
            print("<" * 20)
