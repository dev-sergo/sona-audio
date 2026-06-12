# Contributing to sona-audio

Thank you for your interest in contributing. This is a personal open-source project —
contributions that add new audio models, fix bugs, or improve documentation are welcome.

## Ground rules

- One concern per pull request. Keep PRs small and focused.
- Every new model or endpoint must come with a test in `tests/`.
- No breaking changes to existing API contracts without a version bump.
- English only — code, comments, docs, PR descriptions.

## Development setup

You do **not** need the GPU box to work on the server logic or bot.
The test suite mocks all model calls and runs in a plain Python container.

```bash
git clone https://github.com/dev-sergo/sona-audio-.git
cd sona-audio
cp .env.example .env
make test          # verify everything passes before you start
```

## How to add a new audio model

See the recipe in [README.md](README.md#how-to-add-a-new-audio-model).
The pattern is always the same: GPU endpoint → server service → server route → test.

## Submitting a pull request

1. Fork the repo and create a branch: `git checkout -b feature/my-feature`
2. Make your changes.
3. Run `make test` — all tests must pass.
4. Open a PR against `main` with a clear description of what and why.

## Reporting issues

Open a GitHub issue. Include:
- What you expected to happen
- What actually happened
- Relevant logs or error messages
- Hardware / OS if it is a model or performance issue

## Benchmarks

If you run the project on different hardware, consider sharing your numbers by
opening an issue or PR that adds a row to [docs/BENCHMARKS.md](docs/BENCHMARKS.md).

## License

By contributing you agree that your contributions will be licensed under the
project's [MIT License](LICENSE).
