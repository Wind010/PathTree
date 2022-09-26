from src.path_tree import PathTree

from assertpy import assert_that

class TestPathTree:

    def test_add__one_path__added(self):
        # Arrange
        filepath = "A/B/C.txt"
        sut = PathTree()

        # Act
        sut.add(filepath.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({'A': {'B': {'C.txt'}}})


    def test_add__empty_path__no_add(self):
        # Arrange
        filepath = ""
        sut = PathTree()

        # Act
        sut.add(filepath.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({})


    def test_add__path_with_no_delim__no_add(self):
        # Arrange
        filepath = "X.txt"
        sut = PathTree()

        # Act
        sut.add(filepath.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({filepath})


    def test_add__two_same_paths_from_root__added(self):
        # Arrange
        filepath = "A/B/C.txt"
        sut = PathTree()

        # Act
        sut.add(filepath.split('/')).add(filepath.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({'A': {'B': {'C.txt'}}})


    def test_add__one_valid_and_one_empty_path_from_root__added(self):
        # Arrange
        filepath1 = "A/B/C.txt"
        filepath2 = ""

        sut = PathTree()

        # Act
        sut.add(filepath1.split('/')).add(filepath2.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({'A': {'B': {'C.txt'}}})


    def test_add__two_different_paths_from_root__added(self):
        # Arrange
        filepath1 = "A/B/C.txt"
        filepath2 = "1/2/3.txt"
        sut = PathTree()

        # Act
        sut.add(filepath1.split('/')).add(filepath2.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({'1': {'2': {'3.txt'}}, 'A': {'B': {'C.txt'}}})


    def test_add__two_different_paths_from_edge__added(self):
        # Arrange
        filepath1 = "A/B/C.txt"
        filepath2 = "A/X/Y.txt"
        sut = PathTree()

        # Act
        sut.add(filepath1.split('/')).add(filepath2.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({'A': {'B': {'C.txt'}, 'X': {'Y.txt'}}})


    def test_add__two_different_paths_from_leaf__added(self):
        # Arrange
        filepath1 = "A/B/C.txt"
        filepath2 = "A/B/D.txt"
        sut = PathTree()

        # Act
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({'A': {'B': {'C.txt', 'D.txt'}}})


    def test_add__two_different_paths_same_leaf_parent_name__added(self):
        # Arrange
        filepath1 = "A/B/C.txt"
        filepath2 = "B/D.txt"
        sut = PathTree()

        # Act
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))

        # Assert
        assert_that(sut.root).is_equal_to({'A': {'B': {'C.txt'}}, 'B': {'D.txt'}})


    def test_add__two_different_paths_with_same_subpath__added(self):
        # Arrange
        filepath1 = "A/B/C.txt"
        filepath2 = "A/A/B/C.txt"
        sut = PathTree()

        # Act
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))

        # Assert
        assert set([filepath1, filepath2]) == set(sut.get_flat_list(sut.root))

        assert_that(sut.root).is_equal_to({'A': {'B': {'C.txt'}, 'A': {'B': {'C.txt'}}}})


    def test_get_flat_list__one_existing_path__returns_list_of_one(self):
        # Arrange        
        sut = PathTree()
        sut.root = {'A': {'B': {'C.txt'}}}

        # Act
        result = sut.get_flat_list(None, '-')

        # Assert
        assert_that(result).is_equal_to(['A-B-C.txt'])


    def test_get_flat_list__one_existing_path_with_sep__returns_list_of_one(self):
        # Arrange        
        sut = PathTree()
        sut.root = {'A': {'B': {'C.txt'}}}

        # Act
        result = sut.get_flat_list()

        # Assert
        assert_that(result).is_equal_to(['A/B/C.txt'])


    def test_get_flat_list__two_different_paths_from_root__returns_list_of_two(self):
        # Arrange        
        sut = PathTree()
        sut.root = {'1': {'2': {'3.txt'}}, 'A': {'B': {'C.txt'}}}

        # Act
        result = sut.get_flat_list()

        # Assert
        assert_that(result).contains('1/2/3.txt').contains('A/B/C.txt')


    def test_get_flat_list__two_different_paths_from_edge__returns_list_of_two(self):
        # Arrange        
        sut = PathTree()
        sut.root = {'1': {'2': {'3.txt'}, 'B': {'C.txt'}}}

        # Act
        result = sut.get_flat_list()

        # Assert
        assert_that(result).contains('1/2/3.txt').contains('1/B/C.txt')


    def test_get_flat_list__two_different_paths_from_leaf__returns_list_of_two(self):
        # Arrange        
        sut = PathTree()
        sut.root = {'1': {'2': {'3.txt', '4.txt'}}}

        # Act
        result = sut.get_flat_list()

        # Assert
        assert_that(result).contains('1/2/3.txt').contains('1/2/4.txt')


    def test_contains__empty_tree__returns_false(self):
        # Arrange
        sut = PathTree()

        # Act
        result = sut.contains('anything')

        # Assert
        assert_that(result).is_false()


    def test_contains__path_does_not_exist__returns_false(self):
        # Arrange
        sut = PathTree()
        sut.root = {'A': {'B': {'C.txt'}}}

        # Act
        result = sut.contains("A/B/D.txt".split('/'))

        # Assert
        assert_that(result).is_false()


    def test_contains__path_exists__returns_true(self):
        # Arrange
        sut = PathTree()
        sut.root = {'A': {'B': {'C.txt'}}}

        # Act
        result = sut.contains("A/B/C.txt".split('/'))

        # Assert
        assert_that(result).is_true()


    def test_contains__path_has_no_file__returns_true(self):
        # Arrange
        sut = PathTree()
        sut.root = {'A': {'B': {'C.txt'}}}

        # Act
        result = sut.contains("A/B".split('/'))

        # Assert
        assert_that(result).is_true()


    def test_add__set_to_dict__cached(self):
        # Arrange
        sut = PathTree()
        filepath1 = 'write_year=2022/write_month=06/write_day=01/write_hour=23'
        filepath2 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/flat_partner'
      
        # Act
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))
 
        # Assert
        assert_that(sut.contains(filepath1)).is_true()
        assert_that(sut.contains(filepath2)).is_true()

        paths = sut.get_flat_list()
        assert filepath2 in paths


    def test_add__dict_to_set__cached(self):
        # Arrange
        sut = PathTree()
        filepath1 = 'write_year=2022'
        filepath2 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/flat_partner'
      
        # Act
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))
 
        # Assert
        assert_that(sut.contains(filepath1)).is_true()
        assert_that(sut.contains(filepath2)).is_true()

        paths = sut.get_flat_list()
        assert filepath2 in paths


    def test_add__sets__cached(self):
        # Arrange
        sut = PathTree()
        filepath1 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/flat_partner'
        filepath2 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/soa_basket'
      
        # Act
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))
 
        # Assert
        assert_that(sut.contains(filepath1)).is_true()
        assert_that(sut.contains(filepath2)).is_true()

        paths = sut.get_flat_list()
        assert filepath1 in paths
        assert filepath2 in paths


    def test_add__all_conditions__cached(self):
        # Arrange
        sut = PathTree()
        filepath1 = 'write_year=2022/write_month=06/write_day=01/write_hour=23'
        filepath2 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/flat_partner'
        filepath3 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/flat_partner/001'
        filepath4 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/soa_basket'
        filepath5 = 'write_year=2022/write_month=06/write_day=01/write_hour=23/soa_basket/002'

        # Act
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))
        sut.add(filepath3.split('/'))
        sut.add(filepath4.split('/'))
        sut.add(filepath5.split('/'))


        # Assert
        assert_that(sut.contains(filepath1)).is_true()
        assert_that(sut.contains(filepath2)).is_true()
        assert_that(sut.contains(filepath3)).is_true()
        assert_that(sut.contains(filepath4)).is_true()

        paths = sut.get_flat_list()
        assert filepath3 in paths
        assert filepath5 in paths


    def test_contains__long_path__returns__true(self):
        # Arrange
        sut = PathTree()
        filepath = 'write_year=2019/write_month=10/write_day=02/write_hour=23/item_alt_cat/2019100200_000_0000_000163_00001588792147.339/part-00000-tid-884024087271743393-049ce1fc-e50f-45ec-b85b-4952c7d203ae-111949-1-c000.txt'
        sut.add(filepath)

        # Act
        res = sut.contains(filepath)

        # Assert
        assert_that(res).is_true()


    def test_contains__multiple_paths__returns_true(self):
        # Arrange
        sut = PathTree()
        sut.root = {'1': {'2': {'3.txt', '4.txt'}, 'B': {'C.txt'}}}
        sut.root.update( {'A': {'B': {'C.txt'}, 'H': {'G.txt'}}} )
        sut.add("")

        # Act
        results = [ 
          sut.contains("1/2/3.txt"),
          sut.contains("1/2/4.txt"),
          sut.contains("1/B/C.txt"),
          sut.contains("A/B/C.txt"),
          sut.contains("A/H/G.txt")
        ]

        # Assert
        assert_that(all(res for res in results)).is_true()
        assert_that(sut.contains(""), False)


    def test_iter__multiple_paths__returns_iterator(self):
        # Arrange
        sut = PathTree()
        sut.root = {'1': {'2': {'3.txt', '4.txt'}, 'B': {'C.txt'}}}
        sut.root.update( {'A': {'B': {'C.txt'}, 'H': {'G.txt'}}} )

        # Act
        paths = [p for p in sut]

        # Assert
        assert_that(paths).contains("1/2/3.txt")
        assert_that(paths).contains("1/2/4.txt")
        assert_that(paths).contains("1/B/C.txt")
        assert_that(paths).contains("A/B/C.txt")
        assert_that(paths).contains("A/H/G.txt")

        

    def test_full(self):
        filepath1 = 'write_year=2019/write_month=10/write_day=02/write_hour=23/item_alt_cat/2019100200_000_0000_000163_00001588792147.339/part-00000-tid-884024087271743393-049ce1fc-e50f-45ec-b85b-4952c7d203ae-111949-1-c000.txt'
        filepath2 = 'A/B/C.txt'
        filepath3 = "1/2.txt"
        filepath4 = 'A/B/X.txt'
        filepath5 = '1/3.txt'
        sut = PathTree()

        #sut.root = {'A': {'B': {'C.txt', 'xx.xx'}}}
        sut.add(filepath1.split('/'))
        sut.add(filepath2.split('/'))
        sut.add(filepath3.split('/'))
        sut.add(filepath4.split('/'))
        sut.add(filepath5.split('/'))

        paths = sut.get_flat_list()
        
        assert_that(paths).contains(filepath1).contains(filepath2) \
            .contains(filepath3).contains(filepath4).contains(filepath5)
