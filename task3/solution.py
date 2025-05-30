import unittest

# Функция для поиска пересечений между двумя интервалами
def find_intersection(interval1: list[int], interval2: [int]) -> list[int] | None:

    start1, end1 = interval1
    start2, end2 = interval2

    start = max(start1, start2)
    end = min(end1, end2)

    if start > end:
        return None
    else:
        return [start, end]

# Функция для объединения интервалов, если они пересекаются
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:

    intervals.sort(key=lambda x: x[0])

    final_intervals = [intervals[0]]

    for interval in intervals[1:]:

        last_interval = final_intervals[-1]

        start1, end1 = last_interval
        start2, end2 = interval

        if start2 <= end1:
            final_intervals[-1] = [start1, max(end1, end2)]
        else:
            final_intervals.append(interval)

    return final_intervals

# Функция для подсчёта секунд в пересечении переданных интервалах
def count_intersection_seconds(interval1: list[int], interval2: list[int]) -> int:

    intersection = find_intersection(interval1, interval2)

    if intersection is None:
        return 0
    else:
        start, end = intersection
        return end - start

# Итоговая функция, которая объединяет всю логику
def appearance(intervals: dict[str, list[int]]) -> int:

    if not intervals or not all(key in intervals for key in ['pupil', 'tutor', 'lesson']):
        return 0

    if not all(len(intervals[key]) % 2 == 0 for key in ['lesson', 'pupil', 'tutor']):
        return 0

    lesson_interval = intervals['lesson']

    if not lesson_interval or lesson_interval[0] - lesson_interval[1] == 0:
        return 0

    pupil_lessons_intervals = []
    tutor_lessons_intervals = []

    for j in range(0, len(intervals['pupil']), 2):
        valid_intersection = find_intersection(lesson_interval, intervals['pupil'][j: j + 2])
        if valid_intersection is not None:
            pupil_lessons_intervals.append(valid_intersection)

    for j in range(0, len(intervals['tutor']), 2):
        valid_intersection = find_intersection(lesson_interval, intervals['tutor'][j: j + 2])
        if valid_intersection is not None:
            tutor_lessons_intervals.append(valid_intersection)

    if not pupil_lessons_intervals or not tutor_lessons_intervals:
        return 0

    merged_pupil_intervals = merge_intervals(pupil_lessons_intervals)
    merged_tutor_intervals = merge_intervals(tutor_lessons_intervals)

    common_seconds = 0
    for pupil_interval in merged_pupil_intervals:
        for tutor_interval in merged_tutor_intervals:
            common_seconds += count_intersection_seconds(pupil_interval, tutor_interval)

    return common_seconds

class TestAppearanceFunction(unittest.TestCase):

    def test_provided_examples(self):
        """Тесты на основе предоставленных примеров."""
        provided_tests = [
            {'intervals': {'lesson': [1594663200, 1594666800],
                           'pupil': [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],
                           'tutor': [1594663290, 1594663430, 1594663443, 1594666473]},
             'answer': 3117},
            {'intervals': {'lesson': [1594702800, 1594706400],
                           'pupil': [1594702789, 1594704500, 1594702807, 1594704542, 1594704512, 1594704513, 1594704564, 1594705150, 1594704581, 1594704582, 1594704734, 1594705009, 1594705095, 1594705096, 1594705106, 1594706480, 1594705158, 1594705773, 1594705849, 1594706480, 1594706500, 1594706875, 1594706502, 1594706503, 1594706524, 1594706524, 1594706579, 1594706641],
                           'tutor': [1594700035, 1594700364, 1594702749, 1594705148, 1594705149, 1594706463]},
             'answer': 3577},
            {'intervals': {'lesson': [1594692000, 1594695600],
                           'pupil': [1594692033, 1594696347],
                           'tutor': [1594692017, 1594692066, 1594692068, 1594696341]},
             'answer': 3565},
        ]
        for i, test_case in enumerate(provided_tests):
            with self.subTest(f"Предоставленный тестовый случай {i}"):
                self.assertEqual(appearance(test_case['intervals']), test_case['answer'])

    def test_no_overlap_between_pupil_and_tutor(self):
        """Тест: нет пересечения между учеником и учителем."""
        intervals = {'lesson': [0, 1000],
                     'pupil': [100, 200],
                     'tutor': [300, 400]}
        self.assertEqual(appearance(intervals), 0)

    def test_full_overlap_pupil_tutor_lesson(self):
        """Тест: полное пересечение ученика, учителя и урока."""
        intervals = {'lesson': [0, 100],
                     'pupil': [0, 100],
                     'tutor': [0, 100]}
        self.assertEqual(appearance(intervals), 100)

    def test_partial_overlap(self):
        """Тест: частичное пересечение."""
        intervals = {'lesson': [0, 100],
                     'pupil': [10, 50],  # 40 секунд
                     'tutor': [30, 70]}  # 40 секунд
        # Пересечение: [30, 50] -> 20 секунд
        self.assertEqual(appearance(intervals), 20)

    def test_intervals_outside_lesson(self):
        """Тест: интервалы ученика и учителя полностью вне урока."""
        intervals = {'lesson': [100, 200], # Урок длится 100 секунд
                     'pupil': [0, 50, 250, 300], # Полностью вне урока
                     'tutor': [10, 60, 260, 310]} # Полностью вне урока
        self.assertEqual(appearance(intervals), 0)

    def test_intervals_clipping_by_lesson(self):
        """Тест: интервалы обрезаются границами урока."""
        intervals = {'lesson': [100, 200],
                     'pupil': [50, 150],   # Обрезается до [100, 150]
                     'tutor': [120, 250]}  # Обрезается до [120, 200]
        # Ученик (валидный): [100, 150]
        # Учитель (валидный): [120, 200]
        # Пересечение: [120, 150] -> 30 секунд
        self.assertEqual(appearance(intervals), 30)

    def test_empty_pupil_intervals(self):
        """Тест: пустой список интервалов у ученика."""
        intervals = {'lesson': [0, 1000],
                     'pupil': [],
                     'tutor': [100, 200]}
        self.assertEqual(appearance(intervals), 0)

    def test_empty_tutor_intervals(self):
        """Тест: пустой список интервалов у учителя."""
        intervals = {'lesson': [0, 1000],
                     'pupil': [100, 200],
                     'tutor': []}
        self.assertEqual(appearance(intervals), 0)

    def test_empty_or_invalid_lesson_interval(self):
        """Тест: пустой или некорректный интервал урока."""
        intervals1 = {'lesson': [100, 100], # Нулевая длительность
                     'pupil': [0, 200],
                     'tutor': [0, 200]}
        self.assertEqual(appearance(intervals1), 0)

        intervals2 = {'lesson': [], # Пустой список урока
                     'pupil': [0, 200],
                     'tutor': [0, 200]}
        self.assertEqual(appearance(intervals2), 0)

        intervals3 = {'lesson': [200, 100], # Некорректный интервал (конец раньше начала)
                     'pupil': [0, 200],
                     'tutor': [0, 200]}
        self.assertEqual(appearance(intervals3), 0)

        intervals4 = {'pupil': [0, 200], 'tutor': [0, 200]} # Ключ 'lesson' отсутствует
        self.assertEqual(appearance(intervals4), 0)


    def test_pupil_multiple_segments_tutor_one_segment(self):
        """Тест: несколько сегментов у ученика, один у учителя."""
        intervals = {'lesson': [0, 1000],
                     'pupil': [10, 20, 50, 60, 90, 110], # Объединенный ученик (в пределах урока): [[10,20], [50,60], [90,110]]
                     'tutor': [0, 100]}                  # Объединенный учитель (в пределах урока): [[0,100]]
        # Пересечения:
        # [10,20] с [0,100] -> [10,20] (10с)
        # [50,60] с [0,100] -> [50,60] (10с)
        # [90,110] с [0,100] -> [90,100] (10с) - здесь [90,110] обрезается уроком до [90,110], затем пересекается
        # Фактически, сначала интервалы ученика обрезаются уроком:
        # P1: [10,20] -> [10,20]
        # P2: [50,60] -> [50,60]
        # P3: [90,110] -> [90,110]
        # Учитель: [0,100] -> [0,100]
        # Пересечение P1 и Т: [10,20] (10с)
        # Пересечение P2 и Т: [50,60] (10с)
        # Пересечение P3 и Т: [90,100] (10с)
        # Итого: 30с
        self.assertEqual(appearance(intervals), 30)

    def test_tutor_multiple_segments_pupil_one_segment(self):
        """Тест: несколько сегментов у учителя, один у ученика."""
        intervals = {'lesson': [0, 1000],
                     'pupil': [0, 100],
                     'tutor': [10, 20, 50, 60, 90, 110]}
        # Аналогично предыдущему, результат 30с
        self.assertEqual(appearance(intervals), 30)

    def test_both_multiple_segments_complex_overlap(self):
        """Тест: несколько сегментов у обоих, сложное пересечение."""
        intervals = {'lesson': [0, 200],
                     'pupil': [0, 50, 70, 120, 150, 180],
                     # Ученик, обрезанный уроком и объединенный: [[0,50], [70,120], [150,180]]
                     'tutor': [30, 80, 100, 160]}
                     # Учитель, обрезанный уроком и объединенный: [[30,80], [100,160]]
        # Пересечения:
        # У:[0,50] и Т:[30,80] -> [30,50] (20с)
        # У:[0,50] и Т:[100,160] -> Нет
        # У:[70,120] и Т:[30,80] -> [70,80] (10с)
        # У:[70,120] и Т:[100,160] -> [100,120] (20с)
        # У:[150,180] и Т:[30,80] -> Нет
        # У:[150,180] и Т:[100,160] -> [150,160] (10с)
        # Итого: 20 + 10 + 20 + 10 = 60с
        self.assertEqual(appearance(intervals), 60)

    def test_adjacent_intervals_needing_merge(self):
        """Тест: смежные интервалы, требующие объединения."""
        intervals = {'lesson': [0, 100],
                     'pupil': [10, 20, 20, 30], # Должны объединиться в [10, 30]
                     'tutor': [15, 25]}
        # Ученик (валидный, объединенный): [[10, 30]]
        # Учитель (валидный, объединенный): [[15, 25]]
        # Пересечение: [15, 25] -> 10с
        self.assertEqual(appearance(intervals), 10)

    def test_one_party_absent_completely(self):
        """Тест: одна из сторон полностью отсутствует (пустой список интервалов)."""
        intervals = {'lesson': [0, 100],
                     'pupil': [10, 20],
                     'tutor': []} # Учитель отсутствует
        self.assertEqual(appearance(intervals), 0)

        intervals2 = {'lesson': [0, 100],
                      'pupil': [], # Ученик отсутствует
                      'tutor': [10,20]}
        self.assertEqual(appearance(intervals2), 0)

    def test_intervals_touching_no_overlap(self):
        """Тест: интервалы касаются, но не перекрываются."""
        intervals = {'lesson': [10, 50],
                     'pupil': [10, 30],
                     'tutor': [30, 50]}
        # У:[10,30] Т:[30,50] -> пересечение [30,30], длительность 0 (т.к. find_intersection вернет None при start >= end)
        self.assertEqual(appearance(intervals), 0)

    def test_intervals_touching_with_overlap(self):
        """Тест: интервалы касаются и один из них содержит точку касания."""
        intervals2 = {'lesson': [10, 50],
                     'pupil': [10, 40], # У:[10,40]
                     'tutor': [20, 50]} # Т:[20,50]
        # Пересечение: [20,40] -> 20с
        self.assertEqual(appearance(intervals2), 20)

    def test_invalid_segments_in_input(self):
        """Тест: некорректные сегменты во входных данных (начало >= конец)."""
        intervals = {'lesson': [1594663200, 1594666800],
                     'pupil': [1594663340, 1594663389,  # Валидный
                               1594663395, 1594663390,  # Невалидный (конец раньше начала)
                               1594663392, 1594663392,  # Невалидный (нулевая длина, будет отфильтрован `find_intersection`)
                               1594663396, 1594666472], # Валидный
                     'tutor': [1594663290, 1594663430, 1594663443, 1594666473]}

        # Ожидаемый результат, если невалидные сегменты ученика игнорируются:
        # Валидные сегменты ученика:
        # P1: [1594663340, 1594663389]
        # P2: [1594663396, 1594666472]
        # Они не объединяются, т.к. между ними промежуток.

        # Сегменты учителя:
        # T1: [1594663290, 1594663430]
        # T2: [1594663443, 1594666473]

        # Пересечения:
        # P1 и T1: [1594663340, 1594663389] (49с)
        # P1 и T2: нет
        # P2 и T1: [1594663396, 1594663430] (34с)
        # P2 и T2: [1594663443, 1594666472] (3029с)
        # Итого: 49 + 34 + 3029 = 3112
        self.assertEqual(appearance(intervals), 3112)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)