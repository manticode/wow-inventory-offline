import argparse
from slpp import slpp as lua


def prerun():
    """ Check input args are valid. """
    argparser = argparse.ArgumentParser(description="Inventory database file.")
    argparser.add_argument("-i", help="the lua datafile", dest="infilename")
    argparser.print_help()
    args = argparser.parse_args()
    luafile = open(args.infilename, "r")
    return luafile


def parse_lua(luadb):
    """ Parse the lua data"""
    print("parsing...")
    inventorydata = luadb.read()
    inventorydataparsed = lua.decode(inventorydata)
    print(inventorydataparsed)
    iter_luadb(inventorydataparsed)


def iter_luadb(x):
    for key in x:
        print(key)
        if isinstance(x[key], dict):
            iter_luadb(x[key])


def main():
    """ Run main part of script. """
    print("main func")


if __name__ == "__main__":
    print("preparing")
    databaseobj = prerun()
    parse_lua(databaseobj)
    main()
