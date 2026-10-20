
# LEGO Star Wars III: The Clone Wars

An [Archipelago](https://archipelago.gg/) implementation for **LEGO Star Wars III: The Clone Wars**, bringing the Clone Wars to the multi-game randomizer.

## Project Status

**Work in Progress** — several features are implemented, while others are still under development or planned.
Currently only tested with the 1.1 USA version of the game.

### Current Features

| Feature              | Status      | Notes                                                                                                                                                                   |
|----------------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Red Bricks           | Implemented | Acts as a [McGuffin](https://archipelago.gg/) item. Collecting all randomized Red Bricks is currently the goal. May have bugs; behavior hasn't been fully investigated. |
| Character Unlocks    | Implemented | Character randomization percentage is configurable, believed to range from 20–100%.                                                                                     |
| Character Categories | Implemented | Options to enable or disable Ground Battle, Brig, and Minikit characters. The category options may have bugs.                                                           |
| Level unlocks        | Implemented | Progressive levels only, due to how the game unlocks them.                                                                                                              |
| Ship Unlocks         | Implemented | May still have bugs.                                                                                                                                                    |
| Logic                | Implemented | Still in testing, should be working                                                                                                                                     |
| Gold Bricks          | Partial     | Backend groundwork exists, but they are not yet integrated into the randomizer.                                                                                         |

### Planned Features

| Feature | Status |
|---|---|
| Minikits | Not implemented; implementation plan TBD |
| Vehicle Locking | Planned; details TBD |
| Small Air Support Vehicles | Planned; details TBD |
| Large Air Support Vehicles | Planned; details TBD |

> **Known uncertainties:** Some character category options and Red Brick behavior may be buggy. These need further investigation before their behavior can be considered reliable.

This list may not cover every remaining task. Development is ongoing, and additional features or issues may be identified over time.

# How to Install

> Download the apworld, double click it to install to your archipelago installation.

# How to Use

1. Download [Dolphin's latest release](https://dolphin-emu.org/download/)
2. Install a legal copy of LSW3 (USA) rev 1.1
3. Launch the LSW3 Client from Archipelago
4. Follow the instructions exactly
	1. A note: You should see the "Do not close the game when you see this symbol" screen
	2. After the "Loading client" message is cleared, connect to the archipelago multiworld
	3. NOW load the new save by pressing "A".
5. report bugs and as much detail as possible to "@choryrth_" in the thread linked below.

## Contact

For questions, feedback, or discussion, [send a message on Discord](https://discord.com/channels/731205301247803413/1471781498524008480) or open an issue in this repository.

Bug reports and contributions are welcome!

I do work and go to college, so I may not reply immediately but I will get to the message as soon as I can.

## What Is LEGO Star Wars III: The Clone Wars?

[LEGO Star Wars III: The Clone Wars](https://en.wikipedia.org/wiki/Lego_Star_Wars_III:_The_Clone_Wars) is a LEGO action-adventure game developed by Traveller's Tales and released in 2011, based on the animated series *Star Wars: The Clone Wars*.

This project integrates the game with [Archipelago](https://archipelago.gg/), allowing its progression and items to be randomized alongside other supported games.

