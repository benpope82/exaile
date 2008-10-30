from mutagen import id3
import traceback, time
from xl.cover import *
import os, os.path

def enable(exaile):
    if exaile.loading:
        event.add_callback(_enable, "exaile_loaded")
    else:
        _enable(None, exaile, None)

def _enable(eventname, exaile, nothing):
    exaile.covers.add_search_method(TagCoverSearch())

def disable(exaile):
    exaile.covers.remove_search_method_by_name('tagcover')

class TagCoverSearch(CoverSearchMethod):
    """
        Looks for album art in track tags
    """
    name = 'tagcover'
    type = 'local'

    def find_covers(self, track, limit=-1):
        """
            Searches track tags for album art
        """
        try:
            loc = track.get_loc()
        except AttributeError:
            raise NoCoverFoundException()

        (path, ext) = os.path.splitext(loc.lower())
        ext = ext[1:]

        if ext != 'mp3':
            # nothing but mp3 is supported at this time
            raise NoCoverFoundException()

        covers = []
        try:
            item = id3.ID3(loc)
            for value in item.values():
                if isinstance(value, id3.APIC):
                    covers.append(CoverData(value.data))
                    if limit != -1 and len(covers) >= limit:
                        return covers
        except:
            traceback.print_exc()

        if not covers:
            raise NoCoverFoundException()

        return covers

if __name__ == '__main__':
    from mutagen import id3
    from xl import cover, settings, xdg, settings
    
    settings = settings.SettingsManager(os.path.join(
        xdg.get_config_dir(), 'settings.ini'))

    from xl import collection
    print os.path.join(xdg.get_data_dirs()[0], 'music.db')
    collection = collection.Collection('Collection',    
        os.path.join(xdg.get_data_dirs()[0], 'music.db'))
    covers = cover.CoverManager(settings, cache_dir=os.path.join(
        xdg.get_data_dirs()[0], 'covers'))

    tracks = collection.search('')
    for track in tracks:
        if not track.get_loc().endswith('.mp3'):
            continue

        try:
            try:
                c = covers.get_cover(track)
                if not c: continue
            except cover.NoCoverFoundException:
                continue

            a = id3.ID3(track.get_loc())
            for v in a.values():
                if isinstance(v, id3.APIC):
                    if v.desc == '__exaile_cover__': continue
                    print "track %s already had an image!!!" % track.get_loc()

            print "Writing cover to %s..." % track.get_loc(),
            data = open(c).read()

            i = id3.APIC(type=3, desc='__exaile_cover__', data=data,
                encoding=3, mime='image/jpg')
            a.add(i)
            a.save()
            print "Done..."
        except:
            traceback.print_exc()

    print "Done!!!!"
    covers.save_cover_db()

