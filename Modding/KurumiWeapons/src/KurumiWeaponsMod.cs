using System;
using UnityEngine;

namespace KurumiWeapons
{
    public sealed class KurumiWeaponsMod : IMod
    {
        internal const string ModId = "kurumi_weapons";
        private const string LongRifleId = "kurumi_clockwork_long_rifle";
        private const string PistolId = "kurumi_clockwork_pistol";

        private static ModLog _log;

        public void Init(ModManifest manifest)
        {
            _log = new ModLog(manifest);
            _log.Log("Kurumi's two custom firearms are ready to register.");
        }

        public void OnEnable()
        {
            ModHook.OnModItemDirectoryInit += RegisterItems;
        }

        public void OnDisable()
        {
            ModHook.OnModItemDirectoryInit -= RegisterItems;
        }

        private static string L(string key) => ModHelper.GetLocalized(ModId, key);

        private static void RegisterItems(ModItemDirectory directory)
        {
            bool rifleAdded = directory.Add(LongRifleId, CreateLongRifle);
            bool pistolAdded = directory.Add(PistolId, CreatePistol);

            if (!rifleAdded)
                _log?.Warning("Could not register Kurumi's long rifle (duplicate item ID?).");
            if (!pistolAdded)
                _log?.Warning("Could not register Kurumi's pistol (duplicate item ID?).");
            if (rifleAdded && pistolAdded)
                _log?.Log("Registered both Kurumi firearms.");
        }

        private static GameItem CreateLongRifle()
        {
            // Clone the native shotgun factory so the custom item keeps a working firearm
            // ability, ammunition handling and combat behaviour, then give it its own ID/art.
            return CreateFromNativeFirearm(
                templateId: "shotgun",
                customId: LongRifleId,
                spriteKey: "kurumi_long_rifle",
                nameKey: "item.long_rifle.name",
                descriptionKey: "item.long_rifle.description",
                flavorKey: "item.long_rifle.flavor",
                price: 1250L);
        }

        private static GameItem CreatePistol()
        {
            // Clone the native revolver factory to retain the game's real pistol behaviour.
            return CreateFromNativeFirearm(
                templateId: "revolver",
                customId: PistolId,
                spriteKey: "kurumi_pistol",
                nameKey: "item.pistol.name",
                descriptionKey: "item.pistol.description",
                flavorKey: "item.pistol.flavor",
                price: 950L);
        }

        private static GameItem CreateFromNativeFirearm(
            string templateId,
            string customId,
            string spriteKey,
            string nameKey,
            string descriptionKey,
            string flavorKey,
            long price)
        {
            GameItem item = ItemSpawner.Spawn(templateId);
            if (item == null || item.identifier != templateId)
                throw new InvalidOperationException(
                    "Could not create native firearm template '" + templateId + "'.");

            // The vanilla factory provides the complete weapon behaviour. Only its
            // identity, presentation and base value are changed for this custom variant.
            item.identifier = customId;
            item.SetName(L(nameKey));
            item.shortDescription = L(descriptionKey);
            item.flavorText = L(flavorKey);
            item.SetValue(price);
            item.unitValue = price;
            item.unitBaseValue = price;
            item.SetSpriteAndShapeFromMod(ModId, spriteKey);

            // Preserve its firearm classification explicitly for stock filters and buyers.
            item.SetGameItemType(TypeHelper.WEAPON);
            item.SetGameItemType(TypeHelper.FIREARM);

            return item;
        }
    }
}
