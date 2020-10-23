"""Defines utils used in unit tests.

This should ideally be tested at some point, likely once we have more than one
function (collect, at time of writing)
"""
from typing import List

from medialogic import oracles


def collect(oracle: oracles.Oracle) -> List[str]:
    """Get up to 100 songs from the oracle. If you need more there's something wrong with your test."""
    # Grab the starting song
    songs = [oracle.current_song()]
    for i in range(0, 99):
        # Get 99 "next" songs, for a total of 100.
        song = oracle.next_song()
        if song is None:
            return songs
        songs.append(song)
    return songs