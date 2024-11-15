import click

from mlem.cli.main import cli
from mlem.cli.utils import with_model_meta
from mlem.core.objects import ModelMeta


@cli.command("serve")
@with_model_meta
@click.argument("server", default="fastapi")
def serve(model: ModelMeta, server: str):
    """Serve selected model."""
    from mlem.api.commands import serve

    click.echo("Serving")
    serve(model, server)
