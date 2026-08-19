from worlds.LSW3.LauncherComponents import LauncherComponent
from worlds.LSW3.LauncherComponents import LauncherComponents

from .client import run_client


def launch_lsw3_client(*args: str):
    LauncherComponent.launch(
        run_client,
        name="LEGO Star Wars III: The Clone Wars Client",
        args=args,
    )


LauncherComponents.components.append(
    LauncherComponent(
        display_name="LEGO Star Wars III: The Clone Wars",
        func=launch_lsw3_client,
        game_name="LEGO Star Wars III: The Clone Wars",
        description="Archipelago client for LEGO Star Wars III: The Clone Wars.",
    )
)