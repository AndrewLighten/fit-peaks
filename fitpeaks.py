import click

from zwift_loader import load_from_zwift
from file_loader import load_from_file
from power import power_report
from hr import hr_report
from detail import detail_report
from week import week_report
from detail_plot import detail_plot_report

# Setup a basic CLI application.
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if not ctx.invoked_subcommand:
        week_report()


# Add in a "fetch" command.
@click.command("fetch")
def fetch():
    """
    Load any new Zwift data.
    """
    load_from_zwift()


# Add in a "power" command.
@click.command("power")
@click.option("--all", is_flag=True)
def do_power_report(all: bool):
    """
    Report on peak power data.
    """
    power_report(all)


# Add in a "hr" command.
@click.command("hr")
def do_hr_report():
    """
    Report on peak heart rate data.
    """
    hr_report()


# Add in a "detail" command
@click.command("detail")
@click.argument("id", required=True, type=int)
def do_detail_report(id: int):
    """
    Provide an ID, and this command will show that activity's details.
    """
    detail_report(id)


# Add in a "plot" command
@click.command("plot")
@click.argument("id", required=True, type=int)
def do_detail_plot_report(id: int):
    """
    Provide an ID, and this command will plot that activity.
    """
    detail_plot_report(id)


# Add in a "load" command
@click.command("load")
@click.argument("filename", required=True, type=str)
@click.argument("elevation", required=True, type=int)
def do_load(filename: str, elevation: int):
    """
    Load a FIT file
    """
    load_from_file(filename=filename, elevation=elevation)


def main():
    cli.add_command(fetch)
    cli.add_command(do_power_report)
    cli.add_command(do_hr_report)
    cli.add_command(do_detail_report)
    cli.add_command(do_detail_plot_report)
    cli.add_command(do_load)
    cli(None)


# Run the CLI.
if __name__ == "__main__":
    main()
