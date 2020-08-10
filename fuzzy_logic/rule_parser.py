"""
Luferov Victor <lyferov@yandex.ru>

Rule Parser
"""
import re
from typing import List, Dict
from abc import ABC, abstractmethod
from collections import defaultdict
from .terms import Term
from .types import OperatorType, HedgeType
from .rules import FuzzyCondition, Conditions, SingleCondition, FuzzyRule
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

    class AlternativeLexem(Expression):
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
    def build_lexemes(inp: List[FuzzyVariable], out: List[FuzzyVariable or SugenoVariable]) -> Dict[str, Lexem]:
        lexemes: Dict[str, RuleParser.Lexem] = defaultdict(RuleParser.Lexem)
        # Построение ключевых лексем
        for keyword in NameHelper.keywords:
            lexemes[keyword] = RuleParser.KeywordLexem(keyword)
        # Построение лексем входных переменных
        for i in inp:
            RuleParser.build_lexemes_list(i, True, lexemes)
        # Построение лексем выходных переменных
        for o in out:
            RuleParser.build_lexemes_list(o, False, lexemes)
        return lexemes

    @staticmethod
    def build_lexemes_list(
            variable: [FuzzyVariable, SugenoVariable],
            inp: bool,
            lexemes: Dict[str, Lexem]):
        """
        Парсим лексемы переменных
        :param variable: переменная
        :param inp: входная или выходная
        :param lexemes: лексемы
        :return:
        """
        lexemes[variable.name] = RuleParser.VarLexem(variable, inp)
        for term in variable.values:
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
        copy_expression: List[RuleParser.Expression] = condition_expression
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
                    if alternative_lexem is None:
                        break

                    if isinstance(alternative_lexem, RuleParser.TermLexem):
                        term_lexem = alternative_lexem
                        if isinstance(vl.variable, FuzzyVariable) and term_lexem.term not in vl.variable.terms:
                            term_lexem = None

                    alternative_lexem = alternative_lexem.alternative_term
                    if term_lexem is not None:
                        break
                if term_lexem is None:
                    raise ValueError(f'Неверный идентификатор "{alternative_lexem.text}" в состоянии части правила')

                # Добавление нового выражения состояния
                condition: FuzzyCondition = FuzzyCondition(vl.variable, term_lexem, _not, hedge)
                expressions.append(RuleParser.ConditionExpression(copy_expression[:current + 1], condition))
                copy_expression = copy_expression[current + 1:]
            else:
                # Перебираем остальые лексемы
                expr: RuleParser.Expression = copy_expression[0]
                if expr.text in ['and', 'or', '(', ')']:
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
        condition: Conditions = RuleParser.parse_conditions_recursive(expressions, lexems)
        return condition if isinstance(condition, Conditions) else Conditions()

    @staticmethod
    def find_pair_bracket(expressions: List[Expression], lexems: Dict[str, Lexem]) -> int:
        bracket_open: int = 1
        for i, e in enumerate(expressions[1:]):
            if e == lexems['(']:
                bracket_open += 1
            elif e == lexems[')']:
                bracket_open -= 1
                if bracket_open == 0:
                    return i + 1
        return -1

    @staticmethod
    def parse_conditions_recursive(
            expressions: List[Expression],
            lexems: Dict[str, Lexem]) -> [Conditions, SingleCondition]:
        """
        Рекурсивно парсим правила
        :param expressions: выражения
        :param lexems: лексемы
        :return:
        """
        if len(expressions) < 1:
            raise Exception('Условие пустое')
        if expressions[0] == lexems['('] and RuleParser.find_pair_bracket(expressions, lexems) == len(expressions):
            # Удаляем лишние собки
            return RuleParser.parse_conditions_recursive(expressions[1:-1], lexems)
        elif len(expressions) == 1 and isinstance(expressions[0], RuleParser.ConditionExpression):
            return expressions[0].condition
        else:
            conditions: Conditions = Conditions()
            copy_expression: List[RuleParser.Expression] = expressions
            set_or_and: bool = False
            while len(copy_expression) > 0:
                if copy_expression[0] == lexems['(']:
                    # ищем пару скобор
                    bracket_close: int = RuleParser.find_pair_bracket(copy_expression, lexems)
                    if bracket_close == -1:
                        raise Exception('Ошибка расстановки скобок')
                    condition: [Conditions, SingleCondition] = RuleParser.parse_conditions_recursive(
                        copy_expression[1: bracket_close], lexems
                    )
                    copy_expression = copy_expression[bracket_close + 1:]
                elif isinstance(copy_expression[0], RuleParser.ConditionExpression):
                    condition: [Conditions, SingleCondition] = copy_expression.condition
                    copy_expression = copy_expression[1:]
                else:
                    raise Exception(f'Неверное выражение в состоянии части правил {copy_expression[0].text}')

                # Добавляем состояние к списку
                conditions.conditions.append(condition)
                if len(copy_expression) > 0:
                    if copy_expression[0] in [lexems['and'], lexems['or']]:
                        if len(copy_expression) < 2:
                            raise Exception(f'Ошибка в части условия: {copy_expression[0].text}')
                        new_operator: OperatorType = OperatorType.AND \
                            if copy_expression[0] == lexems['and'] else OperatorType.OR

                        if set_or_and:
                            if conditions.op != new_operator:
                                raise Exception('На одном уровне вложенности не могут быть смешаны и/или операции')
                        else:
                            conditions.op = new_operator
                            set_or_and = True
                        copy_expression = copy_expression[1:]
                    else:
                        raise Exception(f'"{copy_expression[0].text}" не может идти за "{copy_expression[1].text}"')
            return conditions

    @staticmethod
    def parse_conclusion(
            expressions: List[Expression],
            out: Dict[str, Lexem],
            lexems: Dict[str, Lexem]) -> SingleCondition:
        copy_expression: List[RuleParser.Expression] = expressions
        # Удаляем лишние скобки
        while len(copy_expression) >= 2 and copy_expression[0] == lexems['('] and copy_expression[-1] == lexems[')']:
            copy_expression = copy_expression[1:-1]
        if len(copy_expression) != 3:
            raise Exception('Вывод части правила должны быть в форме: "переменная есть терм"')
        # Разбор нечеткой переменной
        if not isinstance(copy_expression[0], RuleParser.VarLexem):
            raise Exception(f'Неверный идентификатор {copy_expression[0].text} в состоянии части правила')
        vl: RuleParser.VarLexem = copy_expression[0]
        if vl.input:
            raise Exception('Нечеткая переменная в заключительной части должна быть выходной переменной')
        # Разбор лексемы is
        if copy_expression[1] != lexems['is']:
            raise Exception(f'После переменной {copy_expression[0].text} должен идти идентификатор "is"')
        term_lexem: [RuleParser.TermLexem, None] = None
        if not isinstance(copy_expression[2], RuleParser.AlternativeLexem):
            raise Exception(f'Неверный идентификатор {copy_expression[2].text} в заключительной части правила')
        # Разбор терма
        al: RuleParser.AlternativeLexem = copy_expression[2]
        while True:
            if al is None:
                break
            if isinstance(al, RuleParser.TermLexem):
                term_lexem: [RuleParser.TermLexem, None] = al
                if term_lexem.term not in vl.variable.values:
                    term_lexem = None
            al = al.alternative_term
            if term_lexem is not None:
                break

        if term_lexem is None:
            raise Exception(f'Неверный идентификатор {copy_expression[2].text} в заключительной части правила')
        # Возвращаем нечеткое заключение
        return SingleCondition(vl.variable, term_lexem.term)

    @staticmethod
    def parse(rule: str, inp: List[FuzzyVariable], out: [FuzzyVariable, SugenoVariable]) -> FuzzyRule:
        """
        Парсим правило из строки
        :param rule: строковое представление правила
        :param empty: пустое правило
        :param inp: входящие переменные
        :param out: выходные переменные
        :return: правило
        """
        if len(rule) == 0:
            raise Exception('Правило не может быть пустое')
        clean_rule: str = ''
        for ch in rule:
            if ch in ['(', ')']:
                if not (len(clean_rule) > 0 and clean_rule[-1] == ' '):
                    clean_rule = f'{clean_rule} '
                clean_rule = f'{clean_rule}{ch} '
            else:
                if not (ch == ' ' and len(clean_rule) > 0 and clean_rule[-1] == ''):
                    clean_rule = f'{clean_rule}{ch}'
        # убираем повторяющиеся пробелы
        clean_rule: str = re.sub(' +', ' ', clean_rule).strip()
        # построение словаря лексем
        lexems: Dict[str, RuleParser.Lexem] = RuleParser.build_lexemes(inp, out)
        expressions: List[RuleParser.Expression] = RuleParser.parse_lexems(clean_rule, lexems)
        if len(expressions) == 0:
            raise Exception('Не найдены допустимые идентификаторы')
        # Находим состояние и вывод частей нечеткого правила
        if expressions[0] != lexems['if']:
            raise Exception('"if" должно быть первым идентификаторов')
        try:
            then_index: int = expressions.index(lexems['then'])
        except ValueError:
            raise Exception('"then" идентификатор не найден')

        if then_index - 1 < 1:
            raise Exception('Состояние части нечеткого правила не найдено')
        conclusion_n: int = len(expressions) - then_index - 1
        if conclusion_n < 1:
            raise Exception('Заключение части нечеткого правила не найдено')
        # Забираем условие и следствие
        condition_expressions: List[RuleParser.Expression] = expressions[1: then_index]
        conclusion_expressions: List[RuleParser.Expression] = expressions[then_index + 1:]

        conditions: Conditions = RuleParser.parse_conditions(condition_expressions, inp, lexems)
        conclusion: SingleCondition = RuleParser.parse_conclusion(conclusion_expressions, out, lexems)
        return FuzzyRule(conditions, conclusion)
