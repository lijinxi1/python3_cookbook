#### 这个项目是用来爬取python cookbook的中文译本的，这是我最喜欢的教程之一，https://python3-cookbook.readthedocs.io/zh-CN/latest/


#### 更新： 2019/12/18

版本： 0.2.0

优化抓取过程，可以保存CSS，JavaScript文件在本地，但在转换成pdf时发现本地渲染时会出现字体缺失问题，所以样式表采用url形式。



我爬取了以下书籍：

https://python3-cookbook.readthedocs.io/zh_CN/latest/    《python3 cookbook》中文译本

https://python-data-structures-and-algorithms.readthedocs.io/zh/latest/    《Python 算法与数据结构视频教程》

https://rl.qiwihui.com/zh_CN/latest/    《强化学习导论》

https://zj-linux-guide.readthedocs.io/zh_CN/latest/   《linux指南》

https://linux-c-learning-all-in-one.readthedocs.io/zh_CN/latest/  《Linux C编程一站式学习》

他们的代码是差不多的，你也可以试试。



#### 更新：2020/9/11

再次爬取这个教程，并删掉了一些冗余文件，代码中使用外部引用JS和CSS。

![image-20191219231345671](image-20191219231345671.png)