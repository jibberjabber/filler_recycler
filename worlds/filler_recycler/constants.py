global_contributor_blacklist: frozenset[str] = frozenset([
    # Blacklisted because they produce exclusively no-op filler that isn't auotmatically caught
    "Clique",
    "Filler Recycler",
    "Jigsaw",
    "Yacht Dice",
    "Yacht Dice Bliss",

    # Blacklisted because their create_filler consistently raises errors
    "Cave Story",
    "Dome Keeper",

    # Blacklisted because their get_filler_item_name is old and spits out an item name the world no longer uses
    "Medievil",
    "Medievil 2",
])
global_dont_contribute_items: frozenset[str] = frozenset(["Nothing", "Filler"])
recycle_max_retries = 20