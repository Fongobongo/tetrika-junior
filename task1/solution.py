from functools import wraps
import inspect
import unittest

def strict(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        # Сохраняем аннотации функции
        annotations = func.__annotations__.copy()

        # Удаляем аннотацию для 'return', если она есть
        if 'return' in annotations:
            del annotations['return']

        # Если есть аннотации, то проверяем соответствие типов
        if annotations:

            # Создаём словарь с переданными аргументами и их типами
            signature = inspect.signature(func)
            arguments = signature.bind(*args, **kwargs)
            arguments = {argument: type(value) for argument, value in arguments.arguments.items()}

            for annotation, annotation_type in annotations.items():
                if arguments.get(annotation) != annotation_type:
                    raise TypeError('Несоответствие типов переданных аргументов объявленным в прототипе функции')

        return func(*args, **kwargs)
    return wrapper

# --- Функции для тестирования ---
@strict
def sum_two(a: int, b: int) -> int:
    """Суммирует два целых числа."""
    return a + b

@strict
def concat_strings(s1: str, s2: str) -> str:
    """Конкатенирует две строки."""
    return s1 + s2

@strict
def describe_item(name: str, price: float, available: bool) -> str:
    """Формирует описание товара."""
    return f"{name} costs {price:.2f}, available: {available}" # Вывод остается на английском

@strict
def no_annotations_func(x, y):
    """Функция без аннотаций типов."""
    return x + y

@strict
def mixed_annotations_func(val1: int, val2, val3: str) -> str:
    """Функция с частично аннотированными параметрами."""
    return f"{val1}-{val2}-{val3}"

@strict
def only_return_annotated(a, b) -> int:
    """Функция с аннотацией только для возвращаемого значения."""
    return a + b


class TestStrictDecorator(unittest.TestCase):
    """Тесты для декоратора @strict"""

    error_message = "Несоответствие типов переданных аргументов объявленным в прототипе функции"

    def test_correct_types_fully_annotated(self):
        """Тест: корректная передача типов для полностью аннотированных функций."""
        self.assertEqual(sum_two(1, 2), 3, "Сумма 1 и 2 должна быть 3")
        self.assertEqual(sum_two(a=10, b=-5), 5, "Сумма 10 и -5 должна быть 5")
        self.assertEqual(concat_strings("a", "b"), "ab", "Конкатенация 'a' и 'b' должна быть 'ab'")
        self.assertEqual(concat_strings(s1="привет", s2=" мир"), "привет мир", "Конкатенация 'привет' и ' мир'")
        self.assertEqual(describe_item("яблоко", 1.50, True), "яблоко costs 1.50, available: True")
        self.assertEqual(describe_item(name="банан", price=0.75, available=False), "банан costs 0.75, available: False")

    def test_incorrect_type_for_int(self):
        """Тест: передача некорректного типа вместо int."""
        with self.assertRaisesRegex(TypeError, self.error_message):
            sum_two("1", 2)
        with self.assertRaisesRegex(TypeError, self.error_message):
            sum_two(1, 2.0)

    def test_incorrect_type_for_str(self):
        """Тест: передача некорректного типа вместо str."""
        with self.assertRaisesRegex(TypeError, self.error_message):
            concat_strings(123, "b")
        with self.assertRaisesRegex(TypeError, self.error_message):
            concat_strings("a", True)

    def test_incorrect_type_for_float(self):
        """Тест: передача некорректного типа вместо float."""
        with self.assertRaisesRegex(TypeError, self.error_message):
            describe_item("яблоко", 1, True) # 1 (int) вместо float

    def test_incorrect_type_for_bool(self):
        """Тест: передача некорректного типа вместо bool."""
        with self.assertRaisesRegex(TypeError, self.error_message):
            describe_item("яблоко", 1.5, "true") # "true" (str) вместо bool
        with self.assertRaisesRegex(TypeError, self.error_message):
            describe_item("яблоко", 1.5, 0) # 0 (int) вместо bool

    def test_bool_passed_for_int_annotation(self):
        """Тест: передача bool для параметра, аннотированного как int."""
        with self.assertRaisesRegex(TypeError, self.error_message):
            sum_two(True, 1)

    def test_function_with_no_annotations(self):
        """Тест: функция без аннотаций (не должно быть ошибок проверки типов)."""
        # Если func.__annotations__ пуст, `if annotations:` в декораторе будет False.
        self.assertEqual(no_annotations_func(1, 2), 3)
        self.assertEqual(no_annotations_func("x", "y"), "xy")
        self.assertEqual(no_annotations_func(True, 1.0), 2.0)

    def test_function_with_mixed_annotations_correct_annotated_types(self):
        """
        Тест: функция с частично аннотированными параметрами.
        Аннотированные параметры переданы с правильными типами, неаннотированный - с любым.
        Ошибки быть НЕ должно, так как проверяются только аннотированные.
        """
        self.assertEqual(mixed_annotations_func(10, "любой_тип", "текст"), "10-любой_тип-текст")
        self.assertEqual(mixed_annotations_func(val1=20, val2=True, val3="суффикс"), "20-True-суффикс")
        self.assertEqual(mixed_annotations_func(val1=5, val2=None, val3="окончание"), "5-None-окончание")

    def test_function_with_mixed_annotations_incorrect_annotated_types(self):
        """
        Тест: функция с частично аннотированными параметрами.
        Один из аннотированных параметров передан с неверным типом.
        Должна быть ошибка.
        """
        with self.assertRaisesRegex(TypeError, self.error_message):
            mixed_annotations_func("плохо", "любой", "текст") # val1: str вместо int

        with self.assertRaisesRegex(TypeError, self.error_message):
            mixed_annotations_func(10, "любой", 100) # val3: int вместо str

    def test_wrong_number_of_arguments(self):
        """
        Тест: вызов с неверным количеством аргументов.
        Ошибки генерируются `inspect.signature().bind()` и пробрасываются декоратором.
        Сообщения об ошибках от Python здесь будут на английском.
        """
        with self.assertRaisesRegex(TypeError, "missing a required argument: 'b'"):
            sum_two(1)
        with self.assertRaisesRegex(TypeError, "too many positional arguments"):
            sum_two(1, 2, 3)

    def test_wrong_keyword_argument(self):
        """
        Тест: вызов с неизвестным именованным аргументом.
        Ошибки генерируются `inspect.signature().bind()` и пробрасываются декоратором.
        Сообщения об ошибках от Python здесь будут на английском.
        """
        with self.assertRaisesRegex(TypeError, "got an unexpected keyword argument 'c'"):
             sum_two(a=1, b=2, c=3)

        with self.assertRaisesRegex(TypeError, "missing a required argument: 'b'"):
             sum_two(a=1, c=2) # 'b' отсутствует

    def test_metadata_preservation(self):
        """Тест: сохранение метаданных декорированной функции."""
        self.assertEqual(sum_two.__name__, 'sum_two', "Имя функции должно сохраниться")
        self.assertEqual(sum_two.__doc__, "Суммирует два целых числа.", "Докстринг функции должен сохраниться")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)