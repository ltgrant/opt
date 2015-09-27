import unittest
from io import StringIO
from parser import *

class parseIngredientTest(unittest.TestCase):
    def test_normal(self):
        i = parseIngredient('25g butter')
        self.assertEqual(i, Ingredient('butter', '25', 'g'))

    def test_nospaces(self):
        i = parseIngredient('25g butter')
        self.assertEqual(i, Ingredient('butter', '25', 'g'))

    def test_fraction(self):
        i = parseIngredient('1/2g butter')
        self.assertEqual(i, Ingredient('butter', '1/2', 'g'))

    def test_mixed(self):
        i = parseIngredient('1 1/2g butter')
        self.assertEqual(i, Ingredient('butter', '1 1/2', 'g'))

    def test_real(self):
        i = parseIngredient('0.5g butter')
        self.assertEqual(i, Ingredient('butter', '0.5', 'g'))

    def test_nounit(self):
        i = parseIngredient('4 eggs')
        self.assertEqual(i, Ingredient('eggs', '4', None))

    def test_noamount(self):
        i = parseIngredient('diced onion')
        self.assertEqual(i, Ingredient('diced onion', None, None))

    def test_explicit(self):
        i = parseIngredient('about 25 [g] butter')
        self.assertEqual(i, Ingredient('butter', 'about 25', 'g'))

    def test_explicit_nospaces(self):
        i = parseIngredient('about 25[g]butter')
        self.assertEqual(i, Ingredient('butter', 'about 25', 'g'))

    def test_explicit_long_unit(self):
        i = parseIngredient('1 [ heaped tbsp. ] sugar')
        self.assertEqual(i, Ingredient('sugar', '1', 'heaped tbsp.'))

    def test_explicit_nounit(self):
        i = parseIngredient('as needed [] salt')
        self.assertEqual(i, Ingredient('salt', 'as needed', None))

class parseMetaTest(unittest.TestCase):
    def test_title(self):
        r = Recipe()
        key, value = splitCommand('title: my title')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe('my title'))

    def test_nospace_title(self):
        r = Recipe()
        key, value = splitCommand('title:my title')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe('my title'))

    def test_nobang_title(self):
        r = Recipe()
        key, value = splitCommand('title : foo')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe('foo'))
    
    def test_size(self):
        r = Recipe()
        key, value = splitCommand('size: for 4 people')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(None, 'for 4 people'))

    def test_lang(self):
        r = Recipe()
        key, value = splitCommand('lang: de')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(None, None, 'de'))

    def test_source(self):
        r = Recipe()
        key, value = splitCommand('source: internet')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(None, None, None, 'internet'))

    def test_author(self):
        r = Recipe()
        key, value = splitCommand('author: myself')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(None, None, None, None, 'myself'))

    def test_description(self):
        r = Recipe()
        key, value = splitCommand('desc: first block')
        m = parseMeta(key, value, r)
        key, value = splitCommand('desc: second block')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(None, None, None, None, None, 'first block second block'))

    def test_keyword(self):
        r = Recipe()
        key, value = splitCommand('keywords: austrian')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(None, None, None, None, None, None, None, ['austrian']))

    def test_multiple_keyword(self):
        r = Recipe()
        key, value = splitCommand('keywords: austrian, vegan, funny, own recipe ')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(keywords=['austrian', 'vegan', 'funny', 'own recipe']))

    def test_multiple_keyword_lines(self):
        r = Recipe()
        key, value = splitCommand('keywords: line 1')
        m = parseMeta(key, value, r)
        key, value = splitCommand('keywords: line 2')
        m = parseMeta(key, value, r)
        self.assertEqual(r, Recipe(keywords=['line 1', 'line 2']))

    def test_unkown(self):
        with self.assertRaises(Exception) as context:
            key, val = splitCommand('unknown: foo')
            parseMeta(key, val, None)
        self.assertEqual(context.exception.args[0], 'invalid metadata key')

class parseFileTest(unittest.TestCase):
    def test_simple(self):
        r = parseFile(StringIO(test_input['simple']))
        self.assertEqual(r, test_result['simple'])

    def test_images(self):
        r = parseFile(StringIO(test_input['images']))
        self.assertEqual(r, test_result['images'])

    def test_multiphase(self):
        r = parseFile(StringIO(test_input['multiphase']))
        self.assertEqual(r, test_result['multiphase'])

    def test_multi_recipe(self):
        r = parseFile(StringIO(test_input['multi_recipe']))
        self.assertEqual(r, test_result['multi_recipe'])

    def test_meta_error(self):
        with self.assertRaises(RecipeParseError) as context:
            parseFile(StringIO(test_input['meta_error']))

        self.assertEqual(context.exception.line, 'unknown: foo')
        self.assertEqual(context.exception.line_nr, 3)
        self.assertIsNotNone(context.exception.__cause__)
        self.assertEqual(context.exception.__cause__.args[0], 'invalid metadata key')

test_input = {
    'simple' : """
        ! title: the title
        # 25g butter
        * eat butter   """,
    'images' : """
        ! title: with images
        !img: image one.jpg
        !img: folder/image two.jpg
        # 25g butter
        * eat butter   """,
    'multiphase' : """
        ! title: the title
        # 25g butter
        * eat butter
        + lie down a bit
        # 100g meat
        * eat meat
        + never try this
        * this""",
    'multi_recipe' : """
        ! title: rec 1
        ! desc: simple description
        # something
        !title: rec 2

        a not so simple description
        that spans over two lines
        """,
    'meta_error' : """
        !title: error
        ! unknown: foo""",
    }

test_result = {
    'simple' : [
        Recipe(
            'the title',
            None,
            None,
            None,
            None,
            None,
            [
                Phase(
                    [
                        Ingredient('butter', '25', 'g'),
                        ],
                    [
                        Step('eat butter'),
                        ]
                    )
                ]
            )
        ],
    'images' : [
        Recipe(
            'with images',
            None,
            None,
            None,
            None,
            None,
            [
                Phase(
                    [
                        Ingredient('butter', '25', 'g'),
                        ],
                    [
                        Step('eat butter'),
                        ]
                    )
                ],
            None,
            [
                'image one.jpg',
                'folder/image two.jpg'
            ]
            )
        ],
    'multiphase' : [
        Recipe(
            'the title',
            None,
            None,
            None,
            None,
            None,
            [
                Phase(
                    [
                        Ingredient('butter', '25', 'g'),
                        ],
                    [
                        Step('eat butter')
                        ]
                    ),
                WaitPhase('lie down a bit'),
                Phase(
                    [
                        Ingredient('meat', '100', 'g')
                        ],
                    [
                        Step('eat meat')
                        ]
                    ),
                WaitPhase('never try this'),
                Phase(
                    None,
                    [
                        Step('this'),
                        ]
                    ),
                ],
            )
        ],
    'multi_recipe' : [
        Recipe(
            'rec 1',
            None,
            None,
            None,
            None,
            'simple description',
            [
                Phase(
                    [
                        Ingredient('something', None, None)
                        ],
                    )
                ]
            ),
        Recipe(
            'rec 2',
            None,
            None,
            None,
            None,
            'a not so simple description that spans over two lines'
            )
        ],
    }
