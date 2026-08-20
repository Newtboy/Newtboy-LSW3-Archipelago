from pathlib import Path
import shutil


DEV_FOLDER = Path(r"C:\Users\whirl\Desktop\LSW3-Archipelago-Git")
ARCHI_FOLDER = Path(
    r"C:\Users\whirl\Desktop\LSW3 Archi\Archipelago Source\Archipelago-0.6.7"
)


def sync_folder(source, destination):
    for source_file in source.rglob("*"):
        if not source_file.is_file():
            continue

        # Don't copy Git's files.
        if ".git" in source_file.parts:
            continue

        relative_path = source_file.relative_to(source)
        destination_file = destination / relative_path

        destination_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(source_file, destination_file)

        print(f"Copied: {relative_path}")


if __name__ == "__main__":
    print("Syncing development files to Archipelago...")
    print()

    sync_folder(DEV_FOLDER, ARCHI_FOLDER)

    print()
    print("Done.")