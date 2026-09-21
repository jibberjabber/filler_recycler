from BaseClasses import MultiWorld, Item, ItemClassification
from collections import Counter
import random
import unittest
from unittest.mock import MagicMock
from worlds import filler_recycler
from worlds.AutoWorld import World

def mock_item(game: str, player: int, name: str, classification: ItemClassification):
    item = MagicMock()
    item.game = game
    item.name = name
    item.player = player
    item.classification = classification
    item.filler = classification == ItemClassification.filler
    item.advancement = classification == ItemClassification.progression
    return item

def mock_world(multiworld: MultiWorld, player: int, game: str, player_name: str) -> None:
    world = MagicMock()
    world.game = game
    world.player_name = player_name
    world.filler_item = mock_item(game, player, f"{game} Filler", ItemClassification.filler)
    world.useful_item = mock_item(game, player, f"{game} Useful", ItemClassification.useful)
    world.progression_item = mock_item(game, player, f"{game} Progression", ItemClassification.progression)
    world.create_filler = MagicMock(return_value=world.filler_item)

    multiworld.game[player] = game
    multiworld.worlds[player] = world
    multiworld.worlds_by_name[player_name] = world
    multiworld.player_name[player] = player_name
    multiworld.itempool.append(world.filler_item)
    multiworld.itempool.append(world.useful_item)
    multiworld.itempool.append(world.progression_item)

class TestFillerRecycler(unittest.TestCase):
    def setUp(self):
        self.multiworld = MagicMock()
        self.multiworld.game = {}
        self.multiworld.worlds = {}
        self.multiworld.worlds_by_name = {}
        self.multiworld.player_name = {}
        self.multiworld.itempool = []
        self.multiworld.random = random.Random()

        self.world = filler_recycler.FillerRecyclerWorld(self.multiworld, 1)
        self.multiworld.game[1] = "Filler Recycler"
        self.multiworld.worlds[1] = self.world
        self.multiworld.player_name[1] = "Filler Recycler"
        self.world.options = MagicMock()

        mock_world(self.multiworld, 2, "A", "A1")
        mock_world(self.multiworld, 3, "A", "A2")
        mock_world(self.multiworld, 4, "B", "B1")
        mock_world(self.multiworld, 5, "B", "B2")
        mock_world(self.multiworld, 6, "manual_C", "manual_C")
        mock_world(self.multiworld, 7, "manual_D", "manual_D")

    def test_get_recyclers_nothing_to_recycle(self):
        self.world.options.games_to_recycle.value = set()
        self.world.options.slots_to_recycle.value = set()

        actual: set[str] = self.world.get_recyclers()
        self.assertEqual(0, len(actual))

    def test_get_recyclers_invalid_slot(self):
        self.world.options.games_to_recycle.value = set()
        self.world.options.slots_to_recycle.value = {"BAD"}

        actual: set[str] = self.world.get_recyclers()
        self.assertEqual(0, len(actual))

    def test_get_recyclers_slot(self):
        self.world.options.games_to_recycle.value = set()
        self.world.options.slots_to_recycle.value = {"A2"}

        actual: set[str] = self.world.get_recyclers()
        self.assertEqual(1, len(actual))
        self.assertIn("A2", actual)

    def test_get_recyclers_invalid_game(self):
        self.world.options.games_to_recycle.value = {"BAD"}
        self.world.options.slots_to_recycle.value = set()

        actual: set[str] = self.world.get_recyclers()
        self.assertEqual(0, len(actual))

    def test_get_recyclers_game(self):
        self.world.options.games_to_recycle.value = {"A"}
        self.world.options.slots_to_recycle.value = set()

        actual: set[str] = self.world.get_recyclers()
        self.assertEqual(2, len(actual))
        self.assertIn("A1", actual)
        self.assertIn("A2", actual)

    def test_get_recyclers_manuals(self):
        self.world.options.games_to_recycle.value = {"_manual"}
        self.world.options.slots_to_recycle.value = set()

        actual: set[str] = self.world.get_recyclers()
        self.assertEqual(2, len(actual))
        self.assertIn("manual_C", actual)
        self.assertIn("manual_D", actual)

    def test_get_recyclers_mixed(self):
        self.world.options.games_to_recycle.value = {"B", "_manual"}
        self.world.options.slots_to_recycle.value = {"A1"}

        actual: set[str] = self.world.get_recyclers()
        self.assertEqual(5, len(actual))
        self.assertIn("A1", actual)
        self.assertIn("B1", actual)
        self.assertIn("B2", actual)
        self.assertIn("manual_C", actual)
        self.assertIn("manual_D", actual)

    def test_get_contributors_all(self):
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = set()
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(6, len(actual))
        # Note that "Filler Recycler" itself isn't included, since it's on the global blacklist
        self.assertIn("A1", actual_player_names)
        self.assertIn("A2", actual_player_names)
        self.assertIn("B1", actual_player_names)
        self.assertIn("B2", actual_player_names)
        self.assertIn("manual_C", actual_player_names)
        self.assertIn("manual_D", actual_player_names)

    def test_get_contributors_slot(self):
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = {"A1"}
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = set()
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(1, len(actual))
        self.assertIn("A1", actual_player_names)

    def test_get_contributors_game(self):
        self.world.options.contributor_games.value = {"B"}
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = set()
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(2, len(actual))
        self.assertIn("B1", actual_player_names)
        self.assertIn("B2", actual_player_names)

    def test_get_contributors_manual(self):
        self.world.options.contributor_games.value = {"_manual"}
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = set()
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(2, len(actual))
        self.assertIn("manual_C", actual_player_names)
        self.assertIn("manual_D", actual_player_names)

    def test_get_contributors_blacklist_slot(self):
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = {"B1"}
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(5, len(actual))
        # Note that "Filler Recycler" itself isn't included, since it's on the global blacklist
        self.assertIn("A1", actual_player_names)
        self.assertIn("A2", actual_player_names)
        self.assertIn("B2", actual_player_names)
        self.assertIn("manual_C", actual_player_names)
        self.assertIn("manual_D", actual_player_names)

    def test_get_contributors_slot_in_recyclers(self):
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = set()
        recyclers: set[str] = {"B2"}

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(5, len(actual))
        # Note that "Filler Recycler" itself isn't included, since it's on the global blacklist
        self.assertIn("A1", actual_player_names)
        self.assertIn("A2", actual_player_names)
        self.assertIn("B1", actual_player_names)
        self.assertIn("manual_C", actual_player_names)
        self.assertIn("manual_D", actual_player_names)

    def test_get_contributors_blacklist_game(self):
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = {"B"}
        self.world.options.contributor_slots_blacklist.value = set()
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(4, len(actual))
        # Note that "Filler Recycler" itself isn't included, since it's on the global blacklist
        self.assertIn("A1", actual_player_names)
        self.assertIn("A2", actual_player_names)
        self.assertIn("manual_C", actual_player_names)
        self.assertIn("manual_D", actual_player_names)

    def test_get_contributors_blacklist_manual(self):
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = {"_manual"}
        self.world.options.contributor_slots_blacklist.value = set()
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(4, len(actual))
        self.assertIn("A1", actual_player_names)
        self.assertIn("A2", actual_player_names)
        self.assertIn("B1", actual_player_names)
        self.assertIn("B2", actual_player_names)

    def test_get_contributors_mixed(self):
        self.world.options.contributor_games.value = {"A", "_manual"}
        self.world.options.contributor_slots.value = {"B1"}
        self.world.options.contributor_games_blacklist.value = {"manual_C"}
        self.world.options.contributor_slots_blacklist.value = {"A1"}
        recyclers: set[str] = set()

        actual: list[World] = self.world.get_contributors(recyclers)
        actual_player_names = [world.player_name for world in actual]
        self.assertEqual(3, len(actual))
        self.assertIn("A2", actual_player_names)
        self.assertIn("B1", actual_player_names)
        self.assertIn("manual_D", actual_player_names)

    def test_get_items_to_recycle_no_recyclers(self):
        self.world.options.recycle_non_filler_items.value = {}
        self.world.options.dont_recycle_filler_items.value = {}
        recyclers: set[str] = set()

        actual: list[Item] = self.world.get_items_to_recycle(recyclers)
        self.assertEqual(0, len(actual))

    def test_get_items_to_recycle_recyclers(self):
        self.world.options.recycle_non_filler_items.value = {}
        self.world.options.dont_recycle_filler_items.value = {}
        recyclers: set[str] = {"A1", "A2"}

        actual: list[Item] = self.world.get_items_to_recycle(recyclers)
        actual_item_names = [item.name for item in actual]
        self.assertEqual(["A Filler", "A Filler"], actual_item_names)

    def test_get_items_to_recycle_dont_recycle(self):
        self.world.options.recycle_non_filler_items.value = {}
        self.world.options.dont_recycle_filler_items.value = {"A": ["A Filler"]}
        recyclers: set[str] = {"A1", "B1"}

        actual: list[Item] = self.world.get_items_to_recycle(recyclers)
        actual_item_names = [item.name for item in actual]
        self.assertEqual(["B Filler"], actual_item_names)

    def test_get_items_to_recycle_non_filler(self):
        self.world.options.recycle_non_filler_items.value = {"A": ["A Useful"]}
        self.world.options.dont_recycle_filler_items.value = {}
        recyclers: set[str] = {"A1", "B1"}

        actual: list[Item] = self.world.get_items_to_recycle(recyclers)
        actual_item_names = [item.name for item in actual]
        self.assertEqual(["A Filler", "A Useful", "B Filler"], actual_item_names)

    def test_recycle_filler_empty(self):
        contributors: list[World] = []

        actual: Item = self.world.recycle_filler(contributors, 0, {})
        self.assertIsNone(actual)

    def test_recycle_filler_first_good(self):
        a1 = self.multiworld.worlds_by_name["A1"]
        b1 = self.multiworld.worlds_by_name["B1"]
        contributors: list[World] = [a1, b1]

        actual: Item = self.world.recycle_filler(contributors, 0, {})
        self.assertEqual("A Filler", actual.name)
        self.assertEqual(2, len(contributors))
        self.assertIn(a1, contributors)
        self.assertIn(b1, contributors)

    def test_recycle_filler_global_dont_contribute(self):
        a1 = self.multiworld.worlds_by_name["A1"]
        b1 = self.multiworld.worlds_by_name["B1"]
        contributors: list[World] = [a1, b1]
        a1.create_filler = MagicMock(return_value=mock_item(a1.game, a1.player, "Nothing", ItemClassification.filler))

        actual: Item = self.world.recycle_filler(contributors, 0, {})
        self.assertEqual("B Filler", actual.name)
        self.assertEqual(1, len(contributors))
        self.assertIn(b1, contributors)

    def test_recycle_filler_dont_contribute_items(self):
        a1 = self.multiworld.worlds_by_name["A1"]
        b1 = self.multiworld.worlds_by_name["B1"]
        contributors: list[World] = [a1, b1]
        dont_contribute_items = {"A": ["A Filler"]}
        a1_first_filler = mock_item(a1.game, a1.player, "A Filler", ItemClassification.filler)
        a1_second_filler = mock_item(a1.game, a1.player, "Different A Filler", ItemClassification.filler)
        a1.create_filler = MagicMock(side_effect=[a1_first_filler, a1_second_filler])

        actual: Item = self.world.recycle_filler(contributors, 0, dont_contribute_items)
        self.assertEqual("Different A Filler", actual.name)
        self.assertEqual(2, len(contributors))
        self.assertIn(a1, contributors)
        self.assertIn(b1, contributors)

    def test_recycle_filler_dont_contribute_items_used_all_retries(self):
        a1 = self.multiworld.worlds_by_name["A1"]
        b1 = self.multiworld.worlds_by_name["B1"]
        contributors: list[World] = [a1, b1]
        dont_contribute_items = {"A": ["A Filler"]}

        actual: Item = self.world.recycle_filler(contributors, 0, dont_contribute_items)
        self.assertEqual("B Filler", actual.name)
        self.assertEqual(1, len(contributors))
        self.assertIn(b1, contributors)

    def test_recycle_filler_progression(self):
        a1 = self.multiworld.worlds_by_name["A1"]
        b1 = self.multiworld.worlds_by_name["B1"]
        contributors: list[World] = [a1, b1]
        a1.create_filler = MagicMock(return_value=a1.progression_item)

        actual: Item = self.world.recycle_filler(contributors, 0, {})
        self.assertEqual("B Filler", actual.name)
        self.assertEqual(1, len(contributors))
        self.assertIn(b1, contributors)

    def test_recycle_filler_exception(self):
        a1 = self.multiworld.worlds_by_name["A1"]
        b1 = self.multiworld.worlds_by_name["B1"]
        contributors: list[World] = [a1, b1]
        a1.create_filler = MagicMock(side_effect=Exception("Mistakes were made"))

        actual: Item = self.world.recycle_filler(contributors, 0, {})
        self.assertEqual("B Filler", actual.name)
        self.assertEqual(1, len(contributors))
        self.assertIn(b1, contributors)

    def test_recycle_filler_all_contributors_invalid(self):
        a1 = self.multiworld.worlds_by_name["A1"]
        b1 = self.multiworld.worlds_by_name["B1"]
        contributors: list[World] = [a1, b1]
        a1.create_filler = MagicMock(side_effect=Exception("Mistakes were made"))
        b1.create_filler = MagicMock(side_effect=Exception("Mistakes were made"))

        actual: Item = self.world.recycle_filler(contributors, 0, {})
        self.assertIsNone(actual)
        self.assertEqual(0, len(contributors))

    def test_generate_basic_no_recyclers(self):
        self.world.options.games_to_recycle.value = set()
        self.world.options.slots_to_recycle.value = set()
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = set()

        before_itempool = list(self.multiworld.itempool)
        self.world.generate_basic()
        self.assertEqual(before_itempool, self.multiworld.itempool)

    def test_generate_basic_no_contributors(self):
        self.world.options.games_to_recycle.value = {"A"}
        self.world.options.slots_to_recycle.value = {"B1"}
        self.world.options.contributor_games.value = set()
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = {"B", "_manual"}
        self.world.options.contributor_slots_blacklist.value = set()

        before_itempool = list(self.multiworld.itempool)
        self.world.generate_basic()
        self.assertEqual(before_itempool, self.multiworld.itempool)

    def test_generate_basic(self):
        self.world.options.games_to_recycle.value = {"A"}
        self.world.options.slots_to_recycle.value = set()
        self.world.options.contributor_games.value = {"B"}
        self.world.options.contributor_slots.value = set()
        self.world.options.contributor_games_blacklist.value = set()
        self.world.options.contributor_slots_blacklist.value = set()
        self.world.options.recycle_non_filler_items.value = {}
        self.world.options.dont_recycle_filler_items.value = {}
        self.world.options.dont_contribute_items.value = {}

        before_len = len(self.multiworld.itempool)
        before_counter = Counter([item.name for item in self.multiworld.itempool])
        self.world.generate_basic()
        after_len = len(self.multiworld.itempool)
        after_counter = Counter([item.name for item in self.multiworld.itempool])
        self.assertEqual(before_len, after_len)
        self.assertEqual(0, after_counter["A Filler"])
        self.assertEqual(before_counter["A Filler"] + before_counter["B Filler"], after_counter["B Filler"])
        for item, count in before_counter.items():
            if item != "A Filler" and item != "B Filler":
                self.assertEqual(count, after_counter[item])
