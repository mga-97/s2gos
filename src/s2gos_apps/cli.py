from procodile.cli import new_cli


# The CLI with a basic set of commands.
# The `cli` is a Typer application of type `typer.Typer()`,
# so can use the instance to register your own commands.
cli = new_cli("s2gos_apps.processes:registry", "s2gos_apps", "0.0.1")