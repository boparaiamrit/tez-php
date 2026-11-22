# tez-php

Static PHP builds for macOS on Apple silicon, made for tez, a local Laravel development
environment. Each build is one self-contained `php` (CLI) and
`php-fpm` binary with about 60 extensions compiled in, built with
[static-php-cli](https://github.com/crazywhalecc/static-php-cli) on GitHub Actions.

## Why not static-php-cli's own builds

static-php-cli's prebuilt "bulk" builds get PDO's PostgreSQL driver from Swoole
(`swoole-hook-pgsql`) instead of PHP's own `pdo_pgsql`. On macOS, Swoole's connect loop loses
libpq's first packet on TCP connections: PostgreSQL waits for a startup message that never
arrives, and the connection fails after 60 seconds. static-php-cli's documentation notes the
problem ("On macOS systems, `pdo_pgsql` may not be able to connect to the postgresql server
normally").

These builds use the same extensions as the bulk set, with two changes:

- `pdo_pgsql` and `pdo_sqlite` are PHP's own drivers, not Swoole's hooks.
- PHP 8.4 and 8.5 have no `imap`: PHP moved it out of core in 8.4.
- PHP 8.1 has no Swoole: Swoole 6.2 needs PHP 8.2 or newer.

Versions built: PHP 8.1 to 8.5. PHP 8.0 (end of life since 2023) does not compile against current
libxml2, so tez uses static-php-cli's 8.0 build for it.

A run compiles only PHP: the ~40 libraries (ICU, ImageMagick, OpenSSL and so on) are cached
between runs, per static-php-cli version and extension set.

Swoole is included from PHP 8.2, so Octane works there. The full list is in
[`extensions.txt`](extensions.txt).

## What is tested

Before a build is published, the workflow checks the PHP version, that the key extensions are
loaded, and that PDO connects to a real PostgreSQL over `127.0.0.1` and over its socket.

## Downloads

Everything is in the [`builds` release](../../releases/tag/builds):

- `php-<version>-cli-macos-aarch64.tar.gz` and `php-<version>-fpm-macos-aarch64.tar.gz`
- `index.json`, which lists every build with its extensions and SHA-256 checksums.

tez picks them up automatically. To use one by hand:

```sh
curl -fsSL https://github.com/boparaiamrit/tez-php/releases/download/builds/php-8.4.28-cli-macos-aarch64.tar.gz | tar xz
./php -v
```

## Building a version

New PHP patch releases are built every Monday. To build one now, run the **Build PHP for macOS**
workflow from the Actions tab. Enter a minor version (`8.4`) for its newest patch, or a full version
(`8.4.20`) for that exact release.

## Licenses

The build scripts are MIT licensed (see [LICENSE](LICENSE)). The binaries contain PHP (PHP License
3.01) and the libraries static-php-cli compiles in, each under its own license.
