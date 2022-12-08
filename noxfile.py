import nox


@nox.session
def mypy(session: nox.Session) -> None:
    session.install("poetry")
    session.run("poetry", "install")

    session.run("mypy", ".")


@nox.session
def black(session: nox.Session) -> None:
    session.install("black")
    session.run("black", ".", "--check")


@nox.session
def ruff(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", ".")
