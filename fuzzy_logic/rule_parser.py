"""
Luferov Victor <lyferov@yandex.ru>

Rule Parser
"""
from typing import List, Dict
from abc import ABC, abstractmethod
from collections import defaultdict
from copy import deepcopy
from .terms import Term
from .rules import FuzzyCondition, Conditions
from .types import HedgeType
from .variables import FuzzyVariable, SugenoVariable, SugenoFunction


class NameHelper:
    keywords: List[str] = [
        'if',
        'then',
        'is',
        'and',
        'or',
        'not',
        '(',
        ')',
        'slightly',
        'somewhat',
        'very',
        'extremely'
    ]

    @staticmethod
    def valid_name(name: str) -> bool:
        """
        Проверяем чтобы имя ключевого слоя не было равно нулю и не было в ключевых переменных
        :param name: имя токена
        :return: валидное имя или нет
        """
        if len(name) == 0:
            return False
        if name in NameHelper.keywords:
            return False
        return True


class RuleParser:
    """
    Парсим нечеткое правило на лексемы
    """

    class Expression(ABC):
        """
        Abstract class of expressions
        """

        @property
        @abstractmethod
        def text(self) -> str:
            ...

    class AlternativeLexem(ABC):
        """
        Alternative lexem
        """

        @property
        @abstractmethod
        def alternative(self) -> 'RuleParser.AlternativeLexem':
            ...

        @alternative.setter
        @abstractmethod
        def alternative(self, value: 'RuleParser.AlternativeLexem') -> 'RuleParser.AlternativeLexem':
            ...

    class Lexem(Expression):
        """
        Abstract class of Lexems
        """

        @property
        @abstractmethod
        def text(self) -> str:
            ...

        @abstractmethod
        def __str__(self):
            return self.text

    class KeywordLexem(Lexem):

        def __init__(self, name: str):
            self.name: str = name

        @property
        def text(self) -> str:
            return self.name

        def __str__(self):
            return self.text

    class VarLexem(Lexem):
        """
        Лексема нечеткой переменной
        """

        def __init__(self, variable: [FuzzyVariable, SugenoVariable], inp: bool):
            """
            Лексема нечеткой переменной
            :param variable: Нечеткая переменная
            :param inp: флаг входной переменной нечеткой базы правил
            """
            self.variable: [FuzzyVariable, SugenoVariable] = variable
            self.input: bool = inp

        @property
        def text(self) -> str:
            return self.variable.name

        def __str__(self):
            return self.text

    class TermLexem(Lexem, AlternativeLexem):
        """
        Лексема нечеткого терма
        """

        def __init__(self, term: [Term, SugenoFunction], inp: bool = True):
            self.term: [Term, SugenoFunction] = term
            self.input: bool = inp
            self.alternative_term: [RuleParser.AlternativeLexem, None] = None

        @property
        def alternative(self) -> ['RuleParser.AlternativeLexem', None]:
            return self.alternative_term

        @alternative.setter
        def alternative(self, value: ['RuleParser.AlternativeLexem', None]):
            self.alternative_term = value

        @property
        def text(self) -> str:
            return self.term.name

        def __str__(self):
            return self.text

    class ConditionExpression(Lexem):
        def __init__(self, expressions: List['RuleParser.Expression'], condition: FuzzyCondition):
            self.expressions: List['RuleParser.Expression'] = expressions
            self.condition: FuzzyCondition = condition

        @property
        def text(self) -> str:
            """
            Возвращаем текст состояния правила
            :return:
            """
            return ''.join([expression.text for expression in self.expressions])

        def __str__(self):
            return self.text

    @staticmethod
    def build_lexemes(inp: List[FuzzyVariable], out: List[FuzzyVariable, SugenoVariable]) -> Dict[str, Lexem]:
        lexemes: Dict[str, RuleParser.Lexem] = defaultdict(RuleParser.Lexem)
        # Построение ключевых лексем
        for keyword in NameHelper.keywords:
            lexemes[keyword] = RuleParser.KeywordLexem(keyword)
        # Построение лексем входных переменных
        for i in inp:
            lexemes.update(RuleParser.build_lexemes_list(i, True))
        # Построение лексем выходных переменных
        for o in out:
            lexemes.update(RuleParser.build_lexemes_list(o, False))
        return lexemes

    @staticmethod
    def build_lexemes_list(variable: [FuzzyVariable, SugenoVariable], inp: bool) -> Dict[str, Lexem]:
        lexemes: Dict[str, RuleParser.Lexem] = defaultdict(RuleParser.Lexem)
        lexemes[variable.name] = RuleParser.VarLexem(variable, inp)
        for term in variable.terms:
            term_lexem: RuleParser.TermLexem = RuleParser.TermLexem(term, inp)
            if term_lexem.text not in lexemes:
                # Если такой лексемы нет
                lexemes[term_lexem.text] = term_lexem
            else:
                # Если такая лексема есть
                found_term: RuleParser.TermLexem = lexemes[term_lexem.text]
                if isinstance(found_term, RuleParser.AlternativeLexem):
                    while found_term.alternative_term is not None:
                        found_term = found_term.alternative_term
                    found_term.alternative_term = term_lexem
                else:
                    raise Exception(f'Найдена более чем одна лексема с похожими именами: {term_lexem.text}')
        return lexemes

    @staticmethod
    def parse_lexems(rule: str, lexems: Dict[str, Lexem]) -> List[Lexem]:
        expressions: List[RuleParser.Lexem] = []
        words: List[str] = rule.split(' ')
        for word in words:
            if word in lexems:
                expressions.append(lexems[word])
            else:
                raise Exception(f'Найден неизвестный идентификатор: {word}')
        return expressions

    @staticmethod
    def extract_single_conditions(
            condition_expression: List[Expression],
            inp: List[FuzzyVariable],
            lexems: Dict[str, Lexem]) -> List[Expression]:
        copy_expression: List[RuleParser.Expression] = deepcopy(condition_expression)
        expressions: List[RuleParser.Expression] = []

        while len(copy_expression) > 0:
            if isinstance(copy_expression[0], RuleParser.VarLexem) and \
                    isinstance(copy_expression[0].variable, FuzzyVariable):
                # Разбор переменной лексемы
                vl: RuleParser.VarLexem = copy_expression[0]
                if len(copy_expression) < 3:
                    raise Exception(f'Состояние начинается с "{vl.text}" не корректно')
                if not vl.input:
                    raise Exception(f'Переменная в состоянии должна быть входной переменной')
                # Разбор "is" лексемы
                expression_is: RuleParser.Lexem = copy_expression[1]
                if expression_is != lexems['is']:
                    raise Exception(f'Ключевое слово "is" должно идти после идентификатора: {vl.text}')

                # Разбор 'not' лексемы, если существует
                current: int = 2
                _not: bool = False

                if copy_expression[current] == lexems['not']:
                    _not = True
                    current += 1
                    if len(copy_expression) <= current:
                        raise Exception(f'Ошибка рядом с "not" в состоянии части правила')

                # Разбор Hedge модификатора, если существует
                # slightly - немного
                # somewhat - в некотором роде
                # very - очень
                # extremely - чрезвычайно

                hedge: HedgeType = HedgeType.NULL
                if copy_expression[current] == lexems['slightly']:
                    hedge = HedgeType.SLIGHTLY
                if copy_expression[current] == lexems['somewhat']:
                    hedge = HedgeType.SOMEWHAT
                if copy_expression[current] == lexems['very']:
                    hedge = HedgeType.VERY
                if copy_expression[current] == lexems['extremely']:
                    hedge = HedgeType.EXTREMELY
                if hedge != HedgeType.NULL:
                    current += 1
                    if len(copy_expression) <= current:
                        raise Exception(f'Ошибка рядом с {str(hedge)} в состоянии части правила')

                # Разбор терма
                if not isinstance(copy_expression[current], RuleParser.AlternativeLexem):
                    raise Exception(f'Неверный идентификатор "{copy_expression[current].text}" в состоянии части правила')
                alternative_lexem: [RuleParser.AlternativeLexem, None] = copy_expression[current]
                term_lexem: [RuleParser.TermLexem, None] = None
                while True:
                    if isinstance(alternative_lexem, RuleParser.TermLexem):
                        term_lexem = alternative_lexem
                        if isinstance(vl.variable, FuzzyVariable) and term_lexem.term not in vl.variable.terms:
                            term_lexem = None

                    alternative_lexem = alternative_lexem.alternative_term
                    if alternative_lexem is None and term_lexem is not None:
                        break
                if term_lexem is None:
                    raise ValueError(f'Неверный идентификатор "{alternative_lexem.text}" в состоянии части правила')

                # Добавление нового выражения состояния
                condition: FuzzyCondition = FuzzyCondition(vl.variable, term_lexem, _not, hedge)
                expressions.append(RuleParser.ConditionExpression(copy_expression[:current + 1], condition))
            else:
                # Перебираем остальые лексемы
                expr: RuleParser.Expression = copy_expression[0]
                if expr in [lexems[op] for op in ['and', 'or', '(', ')']]:
                    expressions.append(expr)
                    copy_expression = copy_expression[1:]
                else:
                    raise Exception(f'Лексема {expr.text} найдена в неправильном месте в сотоянии части правила')
        return expressions

    @staticmethod
    def parse_conditions(
            ce: List[Expression],
            inp: List[FuzzyVariable],
            lexems: Dict[str, Lexem]) -> [Conditions, None]:
        """
        :param ce: Condition expression
        :param inp: input variable
        :param lexems: lexems
        :return: Condition
        """
        expressions: List[RuleParser.Expression] = RuleParser.extract_single_conditions(ce, inp, lexems)
        if len(expressions) == 0:
            raise Exception('Нет действительных условий в условиях части правила')
        # condition: Conditions = RuleParser.parse_conditions_recurse(expressions, lexems)
        condition = None
        return condition if isinstance(condition, Conditions) else Conditions()
