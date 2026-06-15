#!/usr/bin/env python3
# =============================================================================
#     File: bostonT.py
#  Created: 2022-06-22 12:20
#   Author: Bernie Roesler
# =============================================================================

"""Create data files for the Boston T transportation graph."""

import warnings
from collections import defaultdict
from pathlib import Path

import yaml
from yaml import Loader

from algs.graph.search import DepthFirstSearch
from algs.graph.undirected import SymbolGraph
from algs.search import ST

DATA_PATH = Path(__file__).parent.parent / 'data'

# TODO add Silver line branches


def _parse_bostonmetro(fname):
    """Parse the 'bostonmetro.txt' file."""
    names = {0: "END"}  # map: id -> name
    ids = {"END": 0}  # map: name -> id
    raw_edges = defaultdict(list)  # map: line -> list of (in, out) edges

    # Error corrections
    # NOTE len(names) == 125 because
    #   (38, 'St.PaulStreet') --> 'StPaulStreetB'
    #   (61, 'St.PaulStreet') --> 'StPaulStreetC'
    # both exist in names.
    # if station_id == 38:
    #     station_name += 'B'
    # elif station_id == 61:
    #     station_name += 'C'

    corrections = {
        'ChesnutHill': 'ChestnutHill',
        'BrightonAvenue': 'PackardsCorner',
        "St.Mary'sStreet": "St.MarysStreet",
    }

    with fname.open() as fp:
        for line in fp.readlines()[1:]:
            words = line.strip().split()
            if len(words) == 0:
                continue
            station_id = int(words[0])
            station_name = words[1]

            # Corrections
            station_name = corrections.get(station_name, station_name)

            names[station_id] = station_name
            ids[station_name] = station_id

            # Iterate over possibly multiple in/outbound lines, in groups of
            # (line_name, outbound, inbound)
            ws = iter(words[2:])

            for line_name, outbound, inbound in zip(ws, ws, ws):
                # Store raw integer connections for now
                raw_edges[line_name].append((int(inbound), station_id))
                raw_edges[line_name].append((station_id, int(outbound)))

    assert len(ids) == len(names), "Mismatch between station names and ids."

    # Construct the graphs for each line
    tlines = {}

    for line_name, edges in raw_edges.items():
        # Deduplicate edges, preserving order
        edge_tuples = [tuple(sorted((names[v], names[w]))) for v, w in edges]
        unique_edges = list(dict.fromkeys(edge_tuples))

        # Get unique station names, preserving order, and add "END" at the beginning
        flat_stations = (station for edge in unique_edges for station in edge)
        line_keys = list(dict.fromkeys(["END", *flat_stations]))

        # Create the graph
        tlines[line_name] = SymbolGraph(
            keys=line_keys,
            edges=unique_edges,
            parallel=False,
            self_loops=False,
        )

    return names, ids, tlines


def _path_from(G, s):
    """Perform DFS to find the entire path from source to end of line."""
    dfs = DepthFirstSearch(G, s)
    return dfs.path_to(dfs.leaf)


def _write_bostonT_ids(fname, station_ids):
    """Write re-formatted output file of station names and ids."""
    print(f"Writing to {fname}... ", end='')
    with fname.open('w') as fp:
        for k, v in station_ids.items():
            fp.write(f"{k} {v}\n")
    print('done.')


def _write_bostonT_paths(fname, tlines, ids=None):
    """Write formatted output file of the paths on each line."""
    print(f"Writing to {fname}... ", end='')
    with fname.open('w') as fp:
        for line, sg in tlines.items():
            local_path = _path_from(sg.graph, 0)
            if ids is None:
                # Use the station names
                path = [sg.name_of(v) for v in local_path]
            else:
                # Use the station ids
                path = [str(ids[sg.name_of(v)]) for v in local_path]
            fp.write(f"{line}: {'-'.join(path)}\n")
    print('done.')


def _write_bostonT_locs(fname, stations):
    print(f"Writing to {fname}... ", end='')
    with fname.open('w') as fp:
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
    fname = fname or DATA_PATH / 'bostonmetro.txt'
    names, ids, tlines = _parse_bostonmetro(fname)
    station_locs = _parse_mbta_yaml()

    # Need mapping from station_locs.keys() to ids.keys()
    locs = {}
    missing = set()
    for k in ids:
        for name, loc in station_locs.items():
            # if k.lower() in name.replace(' ', '').lower() and k not in locs:
            short_name = name.replace(' ', '').lower()
            if short_name.startswith(k.lower()) and k not in locs:
                locs[k] = loc
        if k not in locs:
            missing.add(k)

    manual_map = {
        'Airport': {'lat': 42.37273343268597, 'lon': -71.03519439697266},
        'Central': {'lat': 42.36516344770085, 'lon': -71.10332250595093},
        'Charles/MGH': {'lat': 42.36127108986245, 'lon': -71.07208013534546},
        'St.PaulStreetB': {'lat': 42.35117407125386, 'lon': -71.11476505448644},
        'St.PaulStreetC': {'lat': 42.34322515730961, 'lon': -71.11734509468079},
        'FordhamRoad': {'lat': 42.350564, 'lon': -71.128047},
        'Harvard': {'lat': 42.373939, 'lon': -71.119106},
        'SummitAvenue': {'lat': 42.3458745625443, 'lon': -71.14135804111079},
        'NewEnglandMedicalCenter': {'lat': 42.349873, 'lon': -71.063795},
        'GriggsStreet/LongwoodAvenue': {
            'lat': 42.34871243015163,
            'lon': -71.13415718078613,
        },
        'Hynes/ICA': {'lat': 42.348097, 'lon': -71.088396},
        'BackBay/SouthEnd': {'lat': 42.34727722151564, 'lon': -71.07603907585144},
        'MountHoodRoad': {'lat': 42.3423261226745, 'lon': -71.14418165157828},
        'SutherlandRoad': {'lat': 42.34149640856349, 'lon': -71.14662408828735},
        'WinchesterStreet/SummitAv.': {
            'lat': 42.34128229417212,
            'lon': -71.12461924552917,
        },
        'GreycliffRoad': {'lat': 42.34007160531, 'lon': -71.16135876826196},
        'FairbanksStreet': {'lat': 42.33960900474095, 'lon': -71.13134622573853},
        'ButlerStreet': {'lat': 42.27211695157111, 'lon': -71.06276750564575},
    }

    locs.update(manual_map)

    # assert sorted(missing) == sorted(manual_map.keys())
    missing -= set(manual_map.keys())
    if len(missing) != 0:
        pairs = "\n".join([f"{ids[m]} {m}\n" for m in missing])
        warnings.warn(f"Missing the following locations:\n{pairs}")

    # Bash one-liner to put "0 END" at top of file
    # echo "0 END" > bostonT_stations.txt \
    #   && tail -n +2 bostonmetro.txt \
    #   | awk '{print $1 " " $2}' \
    #   >> bostonT_stations.txt

    namefile = DATA_PATH / 'bostonT_stations.txt'
    if force_update or not namefile.exists():
        _write_bostonT_ids(namefile, names)

    locfile = DATA_PATH / 'bostonT_locs.txt'
    if force_update or not locfile.exists():
        _write_bostonT_locs(locfile, locs)

    pathfile = DATA_PATH / 'bostonT_lines.txt'
    if force_update or not pathfile.exists():
        _write_bostonT_paths(pathfile, tlines, ids)

    pathfile = DATA_PATH / 'bostonT_symbol_lines.txt'
    if force_update or not pathfile.exists():
        _write_bostonT_paths(pathfile, tlines)


def _parse_mbta_yaml(fname=None):
    """Parse the [YAML file](https://erikdemaine.org/maps/mbta/mbta.yaml) to
    extract latitude and longitude.
    """
    fname = fname or DATA_PATH / 'mbta.yaml'
    with fname.open() as fp:
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
