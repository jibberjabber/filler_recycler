from dataclasses import dataclass

from Options import PerGameCommonOptions, OptionSet, OptionDict

class GamesToRecycle(OptionSet):
    """Which games' filler should be replaced?"""
    display_name = "Games to Recycle"

class SlotsToRecycle(OptionSet):
    """Which slots' filler should be replaced?"""
    display_name = "Slots to Recycle"

class ContributorGames(OptionSet):
    """Which games should contribute replacement filler?

    If both this and contributor_slots are empty, all slots not blacklisted or recycled will contribute."""
    display_name = "Contributor Games"

class ContributorSlots(OptionSet):
    """Which slots should contribute replacement filler?

    If both this and contributor_games are empty, all slots not blacklisted or recycled will contribute."""
    display_name = "Contributor Slots"

class ContributorGamesBlacklist(OptionSet):
    """These games will be excluded from contributing replacement filler."""
    display_name = "Contributor Games Blacklist"

class ContributorSlotsBlacklist(OptionSet):
    """These slots will be excluded from contributing replacement filler."""
    display_name = "Contributor Slots Blacklist"

class RecycleNonFillerItems(OptionDict):
    """Recycle the following items in addition to filler. Provide in the following format:

    recycle_non_filler_items:
      Yacht Dice:
      - Bad RNG
      - Bonus Point
      Another Game:
      - Treat Me Like Filler

    Items that are classified as filler do not need to be added to this setting.
    EXTREME CARE should be exercised if adding progression items to this!!!
    Doing so can break generation!!!"""
    display_name = "Recycle Non-Filler Items"

class DontRecycleFillerItems(OptionDict):
    """Don't recycle these items, even though they are classified as filler. Provide in the following format:

    dont_recycle_filler_items:
      Wordipelago:
      - Cooldown Reduction
      - Shop Points
      Another Game:
      - Important And Unavoidable"""
    display_name = "Don't Recycle Filler Items"

@dataclass
class FillerRecyclerOptions(PerGameCommonOptions):
    games_to_recycle: GamesToRecycle
    slots_to_recycle: SlotsToRecycle
    contributor_games: ContributorGames
    contributor_slots: ContributorSlots
    contributor_games_blacklist: ContributorGamesBlacklist
    contributor_slots_blacklist: ContributorSlotsBlacklist
    recycle_non_filler_items: RecycleNonFillerItems
    dont_recycle_filler_items: DontRecycleFillerItems
