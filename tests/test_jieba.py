# encoding=utf-8
import unittest

import jieba


class TestJieba(unittest.TestCase):
    def test_text_split(self):
        sentence = "我爱北京天安门"
        seg_list = jieba.cut(sentence)