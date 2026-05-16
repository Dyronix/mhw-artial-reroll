# Configuration

The app ships default JSON configuration in `data/config`. On startup, missing config files are copied into the user's app data folder:

```text
%APPDATA%\MHWildsRollTracker\config
```

On systems without `%APPDATA%`, the fallback is:

```text
~/.MHWildsRollTracker/config
```

User config files are not overwritten after they already exist. To pick up new defaults from the repository, manually copy the relevant file from `data/config` into the user config folder.

## Files

### `weapon_types.json`

List of weapon types.

```json
[
  {
    "name": "Great Sword",
    "description": "Large blade weapon."
  }
]
```

Fields:

- `name` - Display name used by the app.
- `description` - Optional description.

### `elements.json`

List of elemental attributes.

```json
[
  {
    "name": "Fire"
  }
]
```

Fields:

- `name` - Display name used by the app.

### `ailments.json`

List of ailment attributes.

```json
[
  {
    "name": "Poison"
  }
]
```

Fields:

- `name` - Display name used by the app.

### `set_bonus_skills.json`

List of Set Bonus skills available in roll entry, target rules, and the Skill Encyclopedia.

```json
[
  {
    "name": "Gore Magala's Tyranny",
    "source": "Gore Magala",
    "description": "Set bonus description."
  }
]
```

Fields:

- `name` - Canonical skill name saved in tracked rolls.
- `source` - Armor, monster, or source label. Autocomplete can search this value.
- `description` - Optional reference text shown in lookup views.

### `group_skills.json`

List of Group Skills available in roll entry, target rules, and the Skill Encyclopedia.

```json
[
  {
    "name": "Lord's Soul",
    "source": "Gogmazios",
    "description": "Group skill description."
  }
]
```

Fields match `set_bonus_skills.json`.

### `skill_encyclopedia.json`

Additional readonly reference entries shown in the Skill Encyclopedia.

```json
[
  {
    "name": "Attack Boost",
    "source": "Armor Skill",
    "description": "Raises attack."
  }
]
```

These entries are not roll-entry skills unless they also appear in `set_bonus_skills.json` or `group_skills.json`.

## Skill Entry Behavior

Skill fields use autocomplete and validate against the configured Set Bonus and Group Skill lists.

- Empty skill cells are saved as `0`.
- Unknown skills are highlighted before saving.
- Some save flows ask for confirmation before unresolved skills or blank cells are accepted.
- Autocomplete searches both skill names and source labels.

## Icons And Assets

Default icons live under `assets/icons`.

The app first checks the user data asset folder, then falls back to bundled assets. This allows user-provided asset overrides without changing repository files:

```text
%APPDATA%\MHWildsRollTracker\assets
```

Use the same relative paths as the bundled `assets` folder when adding overrides.
