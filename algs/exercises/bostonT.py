#!/usr/bin/env python3
# =============================================================================
#     File: bostonT.py
#  Created: 2022-06-22 12:20
#   Author: Bernie Roesler
#
"""
  Description:
"""
# =============================================================================

import yaml
from yaml import Loader

from pathlib import Path

from algs.search import ST
from algs.graph.undirected import STGraph, STDepthFirstPaths


# TODO
# * add Silver line branches
def _parse_bostonmetro(fname):
    """Parse the 'bostonmetro.txt' file."""
    names = dict()   # map: id -> name
    ids = dict()     # map: name -> id
    tlines = dict()  # Graph for each line
    with open(fname, 'r') as fp:
        for line in fp.readlines()[1:]:
            words = line.strip().split()
            station_id = int(words[0])
            station_name = words[1]
            names[station_id] = station_name
            ids[station_name] = station_id
            # Iterate over possibly multiple in/outbound lines
            ws = iter(words[2:])
            try:
                while True:
                    line_name = next(ws)
                    outbound = int(next(ws))
                    inbound = int(next(ws))
                    if line_name not in tlines:
                        tlines[line_name] = STGraph(self_loops=False)
                    tlines[line_name].add_edge(inbound, station_id)
                    tlines[line_name].add_edge(station_id, outbound)
            except StopIteration:
                continue
    # Special end-of-line marker
    names[0] = 'END'
    ids['END'] = 0
    assert len(ids) == len(names)
    return names, ids, tlines


def _path_from(G, s):
    """Perform DFS to find the entire path from source to end of line."""
    dfs = STDepthFirstPaths(G, s)
    return dfs.path_to(dfs.leaf)


def _write_bostonT_ids(fname, station_ids):
    """Write re-formatted output file of station names and ids."""
    print(f"Writing to {fname}... ", end='')
    with open(fname, 'w') as fp:
        for k, v in station_ids.items():
            fp.write(f"{k} {v}\n")
    print('done.')


def _write_bostonT_paths(fname, tlines, names=None):
    """Write formatted output file of the paths on each line."""
    print(f"Writing to {fname}... ", end='')
    with open(fname, 'w') as fp:
        for line, G in tlines.items():
            if names is None:
                path = [str(v) for v in _path_from(G, 0)]
            else:
                path = [str(names[v]) for v in _path_from(G, 0)]
            fp.write(f"{line}: {'-'.join(path)}\n")
    print('done.')


def _write_bostonT_locs(fname, stations):
    print(f"Writing to {fname}... ", end='')
    with open(Path(fname), 'w') as fp:
        fp.write('Station, Latitude, Longitude\n')
        for k, v in stations.items():
            fp.write(f"{k}, {v['lat']}, {v['lon']}\n")
    print('done.')


def _reformat_bostonT_files(fname=None, force_update=False):
    """Reformat the raw data file into a transportation graph format.

    Output files:
    'bostonT_stations.txt'
    1 OakGrove
    2 Malden
    ...

    'bostonT_lines.txt'
    Orange: 0-1-2-5-...
    Blue: 0-3-4-6-...
    ...
    """
    fname = fname or '../data/bostonmetro.txt'
    names, ids, tlines = _parse_bostonmetro(fname)
    station_locs = _parse_mbta_yaml()

    # Need mapping from station_locs.keys() to ids.keys()
    locs = dict()
    missing = list()
    for k in ids:
        for name, loc in station_locs.items():
            # if k.lower() in name.replace(' ', '').lower() and k not in locs:
            short_name = name.replace(' ', '').lower()
            if short_name.startswith(k.lower()) and k not in locs:
                locs[k] = loc
        if k not in locs:
            missing.append(k)

    manual_map = dict({
        'Airport': dict(lat=42.37273343268597, lon=-71.03519439697266),
        'Central': dict(lat=42.36516344770085, lon=-71.10332250595093),
        'Charles/MGH': dict(lat=42.36127108986245, lon=-71.07208013534546),
        'St.PaulStreetB': dict(lat=42.35117407125386, lon=-71.11476505448644),
        'St.PaulStreetC': dict(lat=42.34322515730961, lon=-71.11734509468079),
        'FordhamRoad': dict(lat=42.350564, lon=-71.128047),
        'Harvard': dict(lat=42.373939, lon=-71.119106),
        'SummitAvenue': dict(lat=42.3458745625443, lon=-71.14135804111079),
        'NewEnglandMedicalCenter': dict(lat=42.349873, lon=-71.063795),
        'GriggsStreet/LongwoodAvenue': dict(lat=42.34871243015163, lon=-71.13415718078613),
        'Hynes/ICA': dict(lat=42.348097, lon=-71.088396),
        'BackBay/SouthEnd': dict(lat=42.34727722151564, lon=-71.07603907585144),
        'MountHoodRoad': dict(lat=42.3423261226745, lon=-71.14418165157828),
        'SutherlandRoad': dict(lat=42.34149640856349, lon=-71.14662408828735),
        'WinchesterStreet/SummitAv.': dict(lat=42.34128229417212, lon=-71.12461924552917),
        'GreycliffRoad': dict(lat=42.34007160531, lon=-71.16135876826196),
        'FairbanksStreet': dict(lat=42.33960900474095, lon=-71.13134622573853),
        'ButlerStreet': dict(lat=42.27211695157111, lon=-71.06276750564575),
        })

    # assert sorted(missing) == sorted(manual_map.keys())
    locs.update(manual_map)

    # Bash one-liner:
    # echo "0 END" > bostonT_stations.txt \
    #   | tail -n +2 bostonmetro.txt \
    #   | awk '{print $1 " " $2}' \
    #   >> bostonT_stations.txt
    #
    # namefile = Path('../data/bostonT_stations.txt')
    # if force_update or not namefile.exists():
    #     print(f"Writing to {namefile}... ", end='')
    #     _write_bostonT_ids(namefile, names, ids)
    #     print('done.')

    locfile = Path('../data/bostonT_locs.txt')
    if force_update or not locfile.exists():
        _write_bostonT_locs(locfile, locs)

    pathfile = Path('../data/bostonT_lines.txt')
    if force_update or not pathfile.exists():
        _write_bostonT_paths(pathfile, tlines)

    pathfile = Path('../data/bostonT_symbol_lines.txt')
    if force_update or not pathfile.exists():
        _write_bostonT_paths(pathfile, tlines, names)


def _parse_mbta_yaml(fname=None):
    """Parse the [YAML file](https://erikdemaine.org/maps/mbta/mbta.yaml) to
    extract latitude and longitude."""

    fname = fname or '../data/mbta.yaml'
    with open(Path(fname), 'r') as fp:
        data = yaml.load(fp, Loader=Loader)
    stations = ST()
    for item in data:
        for s in item['stations']:
            try:
                name = s['title']
                if name not in stations:
                    stations[name] = dict.fromkeys(['lat', 'lon'])
                stations[name]['lat'] = s['latitude']
                stations[name]['lon'] = s['longitude']
            except KeyError:
                # Not all items have a title
                pass
    return stations


if __name__ == "__main__":
    _reformat_bostonT_files(force_update=True)


# =============================================================================
# =============================================================================
