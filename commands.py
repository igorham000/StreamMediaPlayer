import argparse
from typing import Dict

import media_library
import json
import pathlib
from command import Command
from controller import Controller
from exceptions import UserException
from print_controller import print_msg


class IllegalArgument(UserException):
    pass


class SafeArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        print_msg(message)


class AddSong(Command):

    def __init__(self, controller: Controller):
        ap = SafeArgumentParser(description="Adds a new song to the library")
        ap.add_argument("song_alias", help="Alias by which the song shall forevermore be named")
        ap.add_argument("song_path", help="The URI where this song can be found")
        ap.add_argument("--description", type=str, required=False,
                        help="Describe the song to remember what it actually is tho")

        super().__init__("addsong", ap)
        self.controller = controller

    def do_function(self, song_alias="", song_path="", description=""):
        """Overrides parent "process" function."""
        if song_alias == "":
            raise IllegalArgument("Expected required argument song_alias, but got: \"\"")
        if song_path == "":
            raise IllegalArgument("Expected required argument song_path, but got: \"\"")

        self.controller.media_library.add_song(
            media_library.Song(alias=song_alias, uri=song_path, description=description))


class CreatePlaylist(Command):

    def __init__(self, controller: Controller):
        ap = SafeArgumentParser(description="Create a new playlist to start adding songs")
        ap.add_argument("playlist_name", help="The name of the playlist being created.")
        super().__init__("createplaylist", ap)
        self.controller = controller

    def do_function(self, playlist_name=""):
        self.controller.media_library.create_playlist(playlist_name=playlist_name)


class AddSongToPlaylist(Command):

    def __init__(self, controller: Controller):
        ap = SafeArgumentParser(description="Add a song to a playlist")
        ap.add_argument("playlist_name", help="The name of the playlist to add the song to")
        ap.add_argument("song_alias", help="The alias of the song to add to the playlist")
        super().__init__("addsongtoplaylist", ap)
        self.controller = controller

    def do_function(self, playlist_name="", song_alias=""):
        self.controller.media_library.add_song_to_playlist(song_alias, playlist_name)


class ListSongs(Command):

    def __init__(self, controller: Controller):
        ap = SafeArgumentParser(description="Lists all songs in the library")
        super().__init__("listsongs", ap)
        self.controller = controller

    def do_function(self):
        songs = self.controller.media_library.list_songs()
        for song in songs:
            if song.description is not None and song.description != "":
                print_msg("  %s: %s || %s" % (song.alias, song.uri, song.description))
            else:
                print_msg("  %s: %s" % (song.alias, song.uri))


class SaveLibrary(Command):
    """Save the current library to a file in the MediaLibrary sub-folder."""

    def __init__(self, controller: Controller):
        ap = SafeArgumentParser(description="Saves the current media library to disk.")
        ap.add_argument("library_name",
                        help="The name of the library. Used for the file name, with '.json' tacked on to the end.")
        super().__init__("save", ap)
        self.controller = controller

    def do_function(self, library_name=""):
        if library_name == "" or library_name is None:
            raise IllegalArgument("Expected a name for the library. Instead got '%s'" % (library_name,))

        json_str = json.dumps(self.controller.media_library.to_primitive())
        file = open("%s/Media Libraries/%s.json" % (pathlib.Path(__file__).parent.absolute(), library_name,), mode="w")
        file.write(json_str)
        file.close()


class LoadLibrary(Command):
    """Read the library written by SaveLibrary in a previous instance."""

    def __init__(self, controller: Controller):
        ap = SafeArgumentParser(description="Loads a library from disk.")
        ap.add_argument("library_name",
                        help="The name of the library. Used for the file name, with '.json' tacked on to the end.")
        super().__init__("load", ap)
        self.controller = controller

    def do_function(self, library_name=""):
        if library_name == "" or library_name is None:
            raise IllegalArgument("Expected a name for the library. Instead got '%s'" % (library_name,))

        file = open("%s/Media Libraries/%s.json" % (pathlib.Path(__file__).parent.absolute(), library_name), mode="r")
        json_str = file.read()
        ml_primitive = json.loads(json_str)
        self.controller.media_library = media_library.MediaLibrary.from_primitive(ml_primitive)


class DescribeSong(Command):
    def __init__(self, controller: Controller):
        ap = SafeArgumentParser(description="Adds a description to a song.")
        ap.add_argument("song_alias", help="The alias of the song to update.")
        ap.add_argument("description", help="The description to add to the song.")
        super().__init__("describesong", ap)
        self.controller = controller

    def do_function(self, song_alias="", description=""):
        if song_alias == "" or song_alias == None:
            raise IllegalArgument("Expected a name for the song. Instead got '%s'" % (song_alias,))
        if description == "" or description == None:
            raise IllegalArgument("Expected a description for the song. Instead got '%s'" % (description,))
        song = self.controller.media_library.get_song(song_alias)
        song.description = description
        self.controller.media_library.add_song(song, expect_overwrite=True)

class Help(Command):
    def __init__(self, command_dict: Dict[str, Command]):
        ap = SafeArgumentParser("Get help on any command")
        ap.add_argument("command", nargs='?', help="the command on which to receive help")
        super().__init__(name="help", arg_parser=ap)
        self.command_dict = command_dict

    def do_function(self, command=""):
        if command is None:
            print_msg(self.help_string())
            return
        if command not in self.command_dict:
            print_msg(
                "Cannot find command '%s'.\n\nAvailable commands: '%s'" % (command, self.command_dict.keys()))
            return
        print_msg(self.command_dict[command].help_string())
        return


class ListCommands(Command):
    def __init__(self, command_dict: Dict[str, Command]):
        ap = SafeArgumentParser("List commands")
        super().__init__(name="commands", arg_parser=ap)
        self.command_dict = command_dict

    def do_function(self):
        print_msg("Available commands: [\n  %s\n]" % ("\n  ".join(self.command_dict)))