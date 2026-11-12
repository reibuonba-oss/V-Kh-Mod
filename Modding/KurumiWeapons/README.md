# Kurumi Exclusive Weapons

A standalone custom-item mod for Probably Stolen.

## Included firearms

| Item | Native behaviour base | Base value |
|---|---|---:|
| Kurumi's Antique Long Rifle | Native shotgun firearm behaviour | 1,250 |
| Kurumi's Antique Pistol | Native revolver firearm behaviour | 950 |

Both items are registered through `OnModItemDirectoryInit`. They are spawned from native firearm factories so they retain the game's real firearm ability and ammo/combat behaviour. The mod then assigns separate item IDs, names, Vietnamese descriptions, inventory sprites and higher base prices.

## Reze arms-dealer integration

Install the updated Reze NPC mod as well. On each Reze visit, there is a 50% chance that one Kurumi weapon is added to the random stock; when one appears, the long rifle and pistol have equal odds. Reze marks it as contraband like the rest of her catalogue.

The dependency is optional: if the item mod is absent or disabled, Reze continues working and simply skips the special weapon.

## Art

The two item sprites are cropped from the reference image in the repository during the build and processed into transparent PNG inventory assets.

## Install

Install the `KurumiWeapons` mod folder and the updated `Reze` mod folder into `Mods/`. Enable both and restart the game.
