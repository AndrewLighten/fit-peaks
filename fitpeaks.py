import click

from zwift_loader import load_from_zwift
from power import power_report
from hr import hr_report
from detail import detail_report

# Setup a basic CLI application.
@click.group()
def cli():
    pass


# Add in a "zwift" command.
@click.command("zwift", short_help="Load Zwift data")
def zwift():
    load_from_zwift()


# Add in a "power" command.
@click.command("power", short_help="Report on peak power")
def do_power_report():
    power_report()


# Add in a "hr" command.
@click.command("hr", short_help="Report on peak heart rate")
def do_hr_report():
    hr_report()


# Add in a "detail" command
@click.command("detail", short_help="Show details for specific activity")
@click.argument("id", required=True, type=int)
def do_detail_report(id: int):
    detail_report(id)


def main():
    cli.add_command(zwift)
    cli.add_command(do_power_report)
    cli.add_command(do_hr_report)
    cli.add_command(do_detail_report)
    cli()


# Run the CLI.
if __name__ == "__main__":
    main()
