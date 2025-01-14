# -*- coding: utf-8 -*-

import collections
from hyper.parsing import knowledgebase

import unittest


class TestKnowledgeBaseParser(unittest.TestCase):
    def setUp(self):
        pass

    def test_kb_parser(self):
        lines = [
            's1 p1 s2',
            's2 p1 s2',
            's1 p2 s1'
        ]

        facts = []
        for line in lines:
            s, p, o = line.split()
            facts += [knowledgebase.Fact(predicate_name=p, argument_names=[s, o])]

        parser = knowledgebase.KnowledgeBaseParser(facts)

        self.assertTrue('s1' in parser.entity_index)
        self.assertTrue('s2' in parser.entity_index)
        self.assertTrue('p1' in parser.predicate_index)
        self.assertTrue('p2' in parser.predicate_index)
        self.assertTrue('p3' not in parser.predicate_index)

    def test_kb_parser_sorted(self):
        lines = [
            's1 p1 s2',
            's2 p1 s1',
            's3 p2 s4',
            's2 p3 s5'
        ]

        entity_lst, predicate_lst, facts = [], [], []
        for line in lines:
            s, p, o = line.split()
            entity_lst += [s, o]
            predicate_lst += [p]
            facts += [knowledgebase.Fact(predicate_name=p, argument_names=[s, o])]

        _entity_counts = {k: (v, k) for k, v in collections.Counter(entity_lst).items()}
        _predicate_counts = {k: (v, k) for k, v in collections.Counter(predicate_lst).items()}

        entity_ord = sorted(_entity_counts, key=_entity_counts.get)
        predicate_ord = sorted(_predicate_counts, key=_predicate_counts.get)

        parser = knowledgebase.KnowledgeBaseParser(facts, entity_ordering=entity_ord, predicate_ordering=predicate_ord)

        #print(parser.entity_index)

        self.assertTrue(parser.entity_index['s2'] == 5)
        self.assertTrue(parser.entity_index['s1'] == 4)
        self.assertTrue(parser.entity_index['s3'] == 1)
        self.assertTrue(parser.entity_index['s4'] == 2)
        self.assertTrue(parser.entity_index['s5'] == 3)

        self.assertTrue(parser.predicate_index['p1'] == 3)
        self.assertTrue(parser.predicate_index['p2'] == 1)
        self.assertTrue(parser.predicate_index['p3'] == 2)

if __name__ == '__main__':
    unittest.main()
