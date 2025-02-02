
default:
  @just --list


run-aa-example:
  litestar  --app examples.advanced_alchemy:app run
