#!/usr/bin/env python3
"""
mediacleaner module:
The main media-cleaner script.
"""
from argparse import ArgumentParser, SUPPRESS
from time import strftime

from delugetools import has_active_torrents
from mediaargs import Flag, Option
from mediatools import log, TextType, clean_tv, log_err, clean_movie, \
    get_value_from_yaml

__version__ = "1.8"


def clean(flags, options):
    """ Cleans libraries . """
    # Check if safemode is enabled.
    if flags[Flag.SAFEMODE]:
        log(flags, "Safemode enabled, not changing any files",
            TextType.INFO)
    else:
        log(flags, "Safemode disabled, all changes will be applied",
            TextType.INFO)

    # Finish the log header.
    if options[Option.CRON]:
        log(flags, "-" * 30, TextType.INFO)

    # Clean what was specified.
    if options[Option.MOVIE]:
        # Find the library path.
        if options[Option.MOVIE_DIR] is not None:
            root_dir = options[Option.MOVIE_DIR]
        else:
            # Get path from yaml file.
            root_dir = get_value_from_yaml(options[Option.CONFIG],
                                           "path", "movie")
        log(flags, "\nRunning movie cleanup script on: {}".format(root_dir),
            TextType.INFO)
        clean_movie(flags, root_dir)

    if options[Option.TV_SERIES]:
        # Find the library path.
        if options[Option.TV_SERIES_DIR] is not None:
            root_dir = options[Option.TV_SERIES_DIR]
        else:
            # Get path from yaml file.
            root_dir = get_value_from_yaml(options[Option.CONFIG], "path", "tv")

        log(flags, "\nRunning tv-series cleanup script on: {}".format(root_dir),
            TextType.INFO)
        clean_tv(flags, root_dir)

    # Check if in cron-mode and write extra log info.
    if options[Option.CRON]:
        log(flags, "-" * 30, TextType.INFO)


########################## Argument Parsing #############################
#########################################################################

def parse_args_and_execute():
    """ Parses arguments and executes requested operations. """
    # Parse arguments.
    parser = ArgumentParser(description='Cleans and renames media files.')

    parser.add_argument('-V', '--{}'.format(Option.VERSION.value),
                        action='store_true', help='shows the version')

    group_vq = parser.add_mutually_exclusive_group()
    group_vq.add_argument('-v', '--{}'.format(Flag.VERBOSE.value),
                          action='store_true', help='enables verbose mode')
    group_vq.add_argument('-q', '--{}'.format(Flag.QUIET.value),
                          action="store_true", help='enables quiet mode')
    parser.add_argument('-c', '--{}'.format(Flag.COLOR.value),
                        action='store_true', help='enables colored log output')
    parser.add_argument('-s', '--{}'.format(Flag.SAFEMODE.value),
                        action='store_true', help='disables any file changes')
    parser.add_argument('-C', '--{}'.format(Option.CRON.value),
                        action='store_true',
                        help='enables cron mode with extra log output')

    parser.add_argument('-f', '--{}'.format(Option.FORCE.value),
                        action='store_true',
                        help='force clean and ignore torrent activity')

    parser.add_argument('-t', '--{}'.format(Option.TV_SERIES.value),
                        action='store_true', help='clean tv-series directory')
    parser.add_argument('-m', '--{}'.format(Option.MOVIE.value),
                        action='store_true', help='clean movie directory')
    parser.add_argument('--{}'.format(Option.MOVIE_DIR.value),
                        help='path to movie directory')
    parser.add_argument('--{}'.format(Option.TV_SERIES_DIR.value),
                        help='path to tv-series directory')

    parser.add_argument('--{}'.format(Option.CONFIG.value),
                        help='path to the yaml file containing media paths')

    # Hidden options.
    parser.add_argument('--{}'.format(Option.SHOW_FLAGS.value),
                        action='store_true', help=SUPPRESS)
    parser.add_argument('--{}'.format(Option.SHOW_OPTIONS.value),
                        action='store_true', help=SUPPRESS)

    args = parser.parse_args()
    flags = {Flag.SAFEMODE: args.safemode,
             Flag.VERBOSE: args.verbose,
             Flag.QUIET: args.quiet,
             Flag.COLOR: args.color}

    options = {Option.VERSION: args.version,
               Option.CRON: args.cron,
               Option.FORCE: args.force,
               Option.TV_SERIES: args.tv,
               Option.MOVIE: args.movie,
               Option.CONFIG: args.config,
               Option.MOVIE_DIR: args.movie_dir,
               Option.TV_SERIES_DIR: args.tv_dir,
               Option.SHOW_FLAGS: args.show_flags,
               Option.SHOW_OPTIONS: args.show_options}

    # Check if in cron-mode and write extra log info.
    if options[Option.VERSION]:
        log(flags, __version__, TextType.INFO)
        quit()

    # Show flags.
    if options[Option.SHOW_FLAGS]:
        print(" ".join(["--{}".format(f.value) for f in Flag]))
        # Always exit after listing flags.
        quit()

    # Show options.
    if options[Option.SHOW_OPTIONS]:
        print(" ".join(["--{}".format(o.value) for o in Option if
                        o is not Option.SHOW_FLAGS and
                        o is not Option.SHOW_OPTIONS]))
        # Always exit after listing options.
        quit()

    # Check path args.
    if options[Option.TV_SERIES] and options[Option.TV_SERIES_DIR] is None and \
            not options[Option.CONFIG]:
        log(flags, "No path set for tv library, see --{} or --{}".
            format(Option.TV_SERIES_DIR.value, Option.CONFIG.value),
            TextType.INFO)
        quit()
    if options[Option.MOVIE] and options[Option.MOVIE_DIR] is None and \
            not options[Option.CONFIG]:
        log(flags, "No path set for movie library, see --{} or --{}".
            format(Option.MOVIE_DIR.value, Option.CONFIG.value),
            TextType.INFO)
        quit()

    # Check if in cron-mode and write extra log header info.
    if options[Option.CRON]:
        log(flags, "-" * 30, TextType.INFO)

    log(flags, "Running cleanup: {}\n".format(strftime("%a %Y-%m-%d %H:%M:%S")),
        TextType.INFO)

    # Check if torrent activity should be ignored.
    if options[Option.FORCE]:
        log(flags, "Force enabled, skipping torrent activity check",
            TextType.INFO)
        # Start cleanup.
        clean(flags, options)
    else:
        # Do torrent activity check and start cleanup.
        try:
            if has_active_torrents():
                log_err(flags, "There are still live torrents, aborting")
            else:
                clean(flags, options)
        except RuntimeError as err:
            log_err(flags, err.args[0])


############################ Start script ###############################
#########################################################################
parse_args_and_execute()
