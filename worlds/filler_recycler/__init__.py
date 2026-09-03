import logging

from BaseClasses import Item
from worlds.AutoWorld import World
from NetUtils import SlotType

from .options import FillerRecyclerOptions

class FillerRecyclerWorld(World):
    game = "Filler Recycler"
    options: FillerRecyclerOptions
    options_dataclass = FillerRecyclerOptions
    location_name_to_id = {"If you're sending this location, something has gone horribly wrong": 352000}
    item_name_to_id = {"If you're receiving this item, something has gone horribly wrong": 352000}
    topology_present = False

    global_contributor_blacklist: frozenset[str] = frozenset([
        # Blacklisted because they produce exclusively no-op filler
        "Filler Recycler", "Yacht Dice", "Yacht Dice Bliss", "Jigsaw", "Simon Tatham's Portable Puzzle Collection",
        # Blacklisted because they do not correctly implement create_filler/get_filler_item_name
        "Terraria", "Rogue Legacy 2"
    ])
    filler_item_name_blacklist: frozenset[str] = frozenset(["Nothing", "Filler"])

    def recycle_filler(self, contributors: list[World], filler_index: int) -> Item:
        if not contributors:
            return None
        contributor_index: int = filler_index % len(contributors)
        contributor: World = contributors[contributor_index]
        try:
            contributed_filler: Item = contributor.create_filler()
            if contributed_filler is not None:
                if contributed_filler.name in self.filler_item_name_blacklist:
                    logging.info(f"{contributor.player_name} ({contributor.game}).create_filler created blacklisted filler item {contributed_filler.name}, removing from contributors")
                elif contributed_filler.advancement:
                    logging.warning(f"{contributor.player_name}'s {contributor.game}.create_filler created progression item {contributed_filler.name}, removing from contributors")
                else:
                    return contributed_filler
        except Exception as e:
            logging.error(f"{contributor.player_name}'s {contributor.game}.create_filler raised an exception, removing from filler contributors: {e}")
        contributors.remove(contributor)
        return self.recycle_filler(contributors, contributor_index)

    def get_recyclers(self) -> set[str]:
        games_to_recycle: set[str] = self.options.games_to_recycle.value
        slots_to_recycle: set[str] = self.options.slots_to_recycle.value

        recycle_all_manuals = "_manual" in games_to_recycle

        return set([world.player_name for world in self.multiworld.worlds.values()
            if (world.game in games_to_recycle or world.player_name in slots_to_recycle
            or (recycle_all_manuals and world.game.startswith("manual_")))])

    def get_contributors(self, recyclers: set[str]) -> list[World]:
        contributor_games: set[str] = self.options.contributor_games.value
        contributor_slots: set[str] = self.options.contributor_slots.value
        contributor_games_blacklist: set[str] = self.options.contributor_games_blacklist.value
        contributor_slots_blacklist: set[str] = self.options.contributor_slots_blacklist.value

        manual_contributors: bool = "_manual" in contributor_games
        manual_contributors_allowed: bool = "_manual" not in contributor_games_blacklist

        return [world for world in self.multiworld.worlds.values()
             if (not (contributor_games or contributor_slots)
                 or world.game in contributor_games
                 or (manual_contributors and world.game.startswith("manual_"))
                 or world.player_name in contributor_slots)
             and world.game not in self.global_contributor_blacklist
             and world.game not in contributor_games_blacklist
             and world.player_name not in contributor_slots_blacklist
             and world.player_name not in recyclers
             and (manual_contributors_allowed or not world.game.startswith("manual_"))]

    def get_items_to_recycle(self, recyclers: set[str]) -> list[Item]:
        recycle_non_filler_items: dict[str, list[str]] = self.options.recycle_non_filler_items.value
        dont_recycle_filler_items: dict[str, list[str]] = self.options.dont_recycle_filler_items.value
        return [i for i in self.multiworld.itempool if
            self.multiworld.player_name[i.player] in recyclers
            and (
                 (i.filler or (i.game in recycle_non_filler_items and i.name in recycle_non_filler_items[i.game]))
                and not (i.game in dont_recycle_filler_items and i.name in dont_recycle_filler_items[i.game])
            )]

    def generate_early(self):
        self.multiworld.player_types[self.player] = SlotType.spectator

    def generate_basic(self) -> None:
        recyclers: set[str] = self.get_recyclers()
        contributors: list[World] = self.get_contributors(recyclers)
        if not recyclers:
            logging.warning("Filler Recycler found no valid slots to recycle")
            return
        if not contributors:
            logging.warning("Filler Recycler found no valid contributor slots")
            return

        for i, filler_to_recycle in enumerate(self.get_items_to_recycle(recyclers)):
            contributed_filler = self.recycle_filler(contributors, i)
            if contributed_filler is not None:
                self.multiworld.itempool.append(contributed_filler)
                self.multiworld.itempool.remove(filler_to_recycle)

    def fill_slot_data(self) -> dict:
        return {
            "world_version": self.world_version,
            "games_to_recycle": self.options.games_to_recycle.value,
            "slots_to_recycle": self.options.slots_to_recycle.value,
            "contributor_games": self.options.contributor_games.value,
            "contributor_slots": self.options.contributor_slots.value,
            "contributor_games_blacklist": self.options.contributor_games_blacklist.value,
            "contributor_slots_blacklist": self.options.contributor_slots_blacklist.value,
            "recycle_non_filler_items": self.options.recycle_non_filler_items.value,
            "dont_recycle_filler_items": self.options.dont_recycle_filler_items.value,
        }
