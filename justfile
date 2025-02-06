
default:
  @just --list


run-aa-example:
  litestar  --app examples.advanced_alchemy:app run


run-basic-example:
  litestar  --app examples.basic:app run
