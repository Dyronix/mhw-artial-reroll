# MH Wilds Gogmazios Tracker

Desktop tracker for planning Monster Hunter Wilds Artian weapon rerolls, focused on Gogmazios Tarred Device roll patterns.

The app helps you record crafted weapons, track the current roll index for each weapon, enter known future roll results, and decide when a roll is worth accepting.

## Features

- Track multiple Artian weapons by weapon type, element or ailment, and optional nickname.
- Record the current Set Bonus skill and Group Skill for each tracked weapon.
- Maintain a roll table per weapon with Set Bonus, Group Skill, and highlight markers.
- Advance all tracked weapons together when a new weapon is crafted or when global roll progress moves forward.
- Accept the next recorded roll for one weapon, updating that weapon's current skills and advancing global progress.
- Review current active rolls in a side panel.
- Define target rules per weapon for single Set Bonus skills, single Group Skills, or required Set Bonus + Group Skill pairs.
- See target summaries directly on weapon rows.
- Rename weapons inline from the dashboard.
- Delete individual weapons.
- Browse tracked weapons in a readonly Weapon Browser.
- Search Set Bonus skills, Group Skills, and encyclopedia entries in the Skill Encyclopedia.
- Autocomplete skill entry fields by skill name or source/armor name.
- Switch skill entry display mode from the Settings panel.
- Use Development Mode to enter prerecord roll data from notes without advancing live roll progress.
- Merge or replace prerecorded weapon roll data when matching weapons already exist.
- Reverse recent roll progress while the tracked weapon set still matches the latest history snapshot.
- Clear all tracked weapons and roll history from Development Mode.
- Store user state locally outside the repository.

## Data Storage

On Windows, user data is stored under:

```text
%APPDATA%\MHWildsRollTracker
```

On non-Windows systems, the fallback location is:

```text
~/.MHWildsRollTracker
```

The app creates these folders:

- `config` - copied default JSON configuration files.
- `saves` - the current tracked weapon state.
- `logs` - startup and runtime logs.
- `exported_data` - reserved for exported data.

Default configuration files live in [data/config](data/config). See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for the supported JSON shapes.

## Requirements

- Python 3.10 or newer.
- Python packages listed in [requirements.txt](requirements.txt).

Install dependencies manually with:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run Locally

From the repository root:

```bat
.venv\Scripts\python.exe src\main.py
```

If you are not using the virtual environment created above, run with any Python environment that has the requirements installed:

```bat
python src\main.py
```

## Build Locally

Release builds are handled by the GitHub release workflow when a version tag is pushed.

For a manual build, use the platform path separator expected by PyInstaller:

```sh
python -m pip install -r requirements.txt
python -m PyInstaller \
  --clean \
  --noconfirm \
  --windowed \
  --name MHWildsGogmaziosTracker \
  --paths src \
  --add-data "data:data" \
  --add-data "assets:assets" \
  src/main.py
```

On Windows, use semicolons for `--add-data`:

```bat
python -m pip install -r requirements.txt
python -m PyInstaller ^
  --clean ^
  --noconfirm ^
  --windowed ^
  --name MHWildsGogmaziosTracker ^
  --paths src ^
  --add-data "data;data" ^
  --add-data "assets;assets" ^
  src\main.py
```

## Repository Scripts

### `bump-version.bat`

Reads the current version from [version.txt](version.txt), applies a semantic version bump, writes the new version to all version-bearing files, commits those files, and creates a `vX.Y.Z` tag.

Supported commands:

```bat
bump-version.bat patch
bump-version.bat minor
bump-version.bat major
bump-version.bat major minor
bump-version.bat minor patch
```

Version bump behavior:

- `patch` increments patch only: `0.2.3` to `0.2.4`.
- `minor` increments minor and resets patch: `0.2.3` to `0.3.0`.
- `major` increments major and resets minor and patch: `0.2.3` to `1.0.0`.
- Combining arguments applies them in major, minor, patch order: `major minor` turns `0.2.3` into `1.1.0`.

The script updates:

- `version.txt`
- `pyproject.toml`
- `src/app/app_info.py`
- `packaging/version_info.txt`

It refuses to run if any of those files already have staged or unstaged changes, and it refuses to create a tag that already exists.

## When To Bump The Version

Bump the version when a change is intended to be released or packaged for users.

Use:

- `patch` for bug fixes, documentation-only release corrections, small UI fixes, data corrections, and packaging fixes.
- `minor` for new user-visible features, new dialogs, new workflows, or compatible data/config additions.
- `major` for breaking save-data changes, incompatible config changes, renamed app identity/storage locations, or major workflow changes that users must account for.

Recommended release flow:

```bat
bump-version.bat patch
git push
git push origin vX.Y.Z
```

Pushing a tag triggers the GitHub release workflow.

## GitHub Release Workflow

[.github/workflows/release.yml](.github/workflows/release.yml) runs on tag pushes.

It builds packages on:

- Ubuntu
- Windows
- macOS

The workflow installs dependencies, runs pytest when a `tests` directory exists, builds with PyInstaller, uploads build artifacts, creates a source archive, and publishes a GitHub Release.

## Version Files

[version.txt](version.txt) is the source of truth for the current version.

The bump script propagates that version to:

- `pyproject.toml` for Python package metadata.
- `src/app/app_info.py` for the application runtime version and window title.
- `packaging/version_info.txt` for Windows executable version metadata used by PyInstaller/spec based packaging.

Keep these files in sync. Prefer `bump-version.bat` instead of editing them manually.

## Configuration

The app reads JSON configuration from the user config folder after copying defaults from `data/config`.

Configuration controls:

- Weapon types.
- Elements.
- Ailments.
- Set Bonus skills.
- Group Skills.
- Skill Encyclopedia entries.

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

Monster Hunter Wilds and all related names, assets, trademarks, and intellectual property are owned by Capcom.

This tool is unofficial, based on observed behavior and personal tracking, and is provided as-is.
