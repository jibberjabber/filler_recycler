# Filler Recycler

Have you ever been annoyed by games chock-full of filler that does literally nothing? Enough to mess with generation in eldritch and morally questionable ways? Then do I have a solution for you! Filler Recycler is a spectactor apworld that allows you to set games and slots whose filthy filler will be summarily removed and replaced with fresh filler from other slots.

## Usage

Download the latest filler_recycler.apworld from the Releases page and place it in your custom_worlds folder. 

Create a yaml for your Filler Recycler either directly using your favorite text editor or using the Option Creator in the Archipelago launcher. 

Include your Filler Recycler yaml when generating locally to enable its functionality. 

## Caveats

- Only filler added to the multiworld's itempool will be recycled. Local filler, such as those created if Jigsaw's percentage_fillers_itempool is lower than 100, will not be recycled.
- Some apworlds do not properly implement the methods required to be contributors or themselves contribute nothing fillers. Filler Recycler includes a list of preemptively blacklisted games, but it is not guaranteed to be comprehensive. Exercise caution in the games you allow to be contributors, and if you encounter problems please report them here.
