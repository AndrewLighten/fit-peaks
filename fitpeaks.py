import click

from zwift_loader import load_from_zwift
from power import power_report
from hr import hr_report
from detail import detail_report
from week import week_report

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
def do_power_report():
    """
    Report on peak power data.
    """
    power_report()


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


def main():
    cli.add_command(fetch)
    cli.add_command(do_power_report)
    cli.add_command(do_hr_report)
    cli.add_command(do_detail_report)
    cli(None)


# Run the CLI.
if __name__ == "__main__":
    main()
